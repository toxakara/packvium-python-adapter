import json
import sys
import types
from pathlib import Path

import pytest

import packvium_native
from packvium_native import pack

# A cross-language fixture kept several levels above this package; a published copy
# does not carry it.
ROOT = Path(__file__).parents[2] / "conformance" / "shared" / "fixtures"


def test_fixtures() -> None:
    if not ROOT.is_dir():
        pytest.skip("the shared cross-language fixture corpus is not part of this package")
    # A blanket `result["complete"]` assertion would be wrong — the group-atomicity
    # regression fixture is deliberately unsatisfiable.
    for path in ROOT.glob("*.json"):
        result = pack(json.loads(path.read_text()))
        expected_complete = len(result["unpacked_items"]) == 0
        assert result["complete"] == expected_complete, (path.name, result)


# The native path raises what the pure engine raises, and both write one spelling.
# A stand-in module raises what the compiled wheel raises -- `PackviumError(ValueError)` with
# the core's refusal as attributes -- so this runs without a Rust build.
SIDE = {"length": "100", "width": "100", "height": "100"}
FIXED = {"item_type": "cube", "container_type": "box", "container_instance": 1,
         "position": {"x": "0", "y": "0", "z": "0"}, "orientation": "LWH"}
REFUSED = {
    "collision": {
        "items": [{"id": "cube", "quantity": 2, "dimensions": SIDE}],
        "containers": [{"id": "box", "inner_dimensions": {"length": "200", "width": "100", "height": "100"}}],
        "fixed_placements": [FIXED, FIXED],
    },
    "unsupported": {
        "items": [{"id": "cube", "quantity": 1, "dimensions": SIDE}],
        "containers": [{"id": "box", "inner_dimensions": SIDE, "pallet_overhang_limit": "1"}],
    },
    "policy": {
        "items": [{"id": "cube", "quantity": 1, "dimensions": SIDE}],
        "containers": [{"id": "box", "inner_dimensions": SIDE}],
        "policy": "x",
    },
    "quantity": {
        "items": [{"id": "cube", "quantity": 0, "dimensions": SIDE}],
        "containers": [{"id": "box", "inner_dimensions": SIDE}],
    },
}


class StandInError(ValueError):
    def __init__(self, message: str, **attributes: object) -> None:
        super().__init__(message)
        for name in ("code", "reason", "field", "detail"):
            setattr(self, name, attributes.get(name))


def stand_in(raised: Exception) -> types.ModuleType:
    module = types.ModuleType("packvium_native_rust")
    module.PackviumError = StandInError  # type: ignore[attr-defined]

    def pack_json(payload: str) -> str:
        raise raised

    module.pack_json = pack_json  # type: ignore[attr-defined]
    return module


def describe(error: BaseException) -> tuple:
    return (type(error), getattr(error, "code", None), getattr(error, "reason", None),
            getattr(error, "field", None), getattr(error, "detail", None))


def clock_free(value: object) -> object:
    # Two solves of one request differ only in what the clock read: a loaded host reads 1 ms.
    if isinstance(value, dict):
        return {key: clock_free(item) for key, item in value.items() if "duration" not in key}
    if isinstance(value, list):
        return [clock_free(item) for item in value]
    return value


def python_refusal(request: dict) -> BaseException:
    # The pure engine is a test extra only on Python 3.10+, where it is supported.
    packvium = pytest.importorskip("packvium")
    with pytest.raises(ValueError) as caught:
        packvium.pack_from_dict(request)
    return caught.value


NATIVE_ERRORS = {
    "collision": StandInError("invalid_fixed_placement: collision: cube#1 with cube#2", code="invalid_fixed_placement",
                              reason="cannot_hold", field="/fixed_placements", detail="collision: cube#1 with cube#2"),
    "unsupported": StandInError("unsupported_feature: the Rust core does not yet implement container.pallet_overhang_limit; "
                                "the request was rejected instead of silently ignoring public fields",
                                code="unsupported_feature"),
    "policy": StandInError("invalid input: policy must be an object", code="invalid_input"),
    "quantity": StandInError("invalid_request: /items/0/quantity: must be at least 1", code="invalid_request",
                             reason="below_minimum", field="/items/0/quantity", detail="must be at least 1"),
}


@pytest.mark.parametrize("name", sorted(REFUSED))
def test_a_native_refusal_is_raised_as_the_pure_engines_class(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    expected = python_refusal(REFUSED[name])
    monkeypatch.setitem(sys.modules, "packvium_native_rust", stand_in(NATIVE_ERRORS[name]))
    assert packvium_native.backend() == "rust"
    with pytest.raises(ValueError) as caught:
        packvium_native.pack(REFUSED[name])
    assert describe(caught.value) == describe(expected)
    if name != "unsupported":  # that sentence names the engine that refused
        assert str(caught.value) == str(expected)


@pytest.mark.parametrize("unnamed", [
    StandInError("caught native panic"),
    StandInError("solver result failed independent validation: overlap", code="solution_failed_validation"),
], ids=["missing code", "unmapped code"])
def test_a_native_error_with_no_refusal_to_name_falls_back_to_the_pure_engine(
        monkeypatch: pytest.MonkeyPatch, unnamed: StandInError) -> None:
    pytest.importorskip("packvium")
    request = {"items": [{"id": "cube", "quantity": 1, "dimensions": SIDE}],
               "containers": [{"id": "box", "inner_dimensions": SIDE}]}
    monkeypatch.setitem(sys.modules, "packvium_native_rust", None)
    expected = packvium_native.pack_json(json.dumps(request))
    monkeypatch.setitem(sys.modules, "packvium_native_rust", stand_in(unnamed))
    assert packvium_native.backend() == "rust"
    assert clock_free(json.loads(packvium_native.pack_json(json.dumps(request)))) == clock_free(json.loads(expected))
    assert json.loads(expected)["complete"] is True


def test_a_native_error_with_a_code_is_raised_as_it_came_when_packvium_is_absent(
        monkeypatch: pytest.MonkeyPatch) -> None:
    coded = NATIVE_ERRORS["quantity"]
    monkeypatch.setitem(sys.modules, "packvium", None)  # import fails: no class to raise
    monkeypatch.setitem(sys.modules, "packvium_native_rust", stand_in(coded))
    with pytest.raises(StandInError) as caught:
        packvium_native.pack(REFUSED["quantity"])
    assert caught.value is coded


def test_the_fallback_writes_the_canonical_spelling(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("packvium")
    monkeypatch.setitem(sys.modules, "packvium_native_rust", None)  # import fails: fallback
    assert packvium_native.backend() == "python"
    request = {"items": [{"id": "é", "quantity": 1, "dimensions": SIDE}],
               "containers": [{"id": "box", "inner_dimensions": SIDE}]}
    text = packvium_native.pack_json(json.dumps(request))
    assert text == json.dumps(json.loads(text), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    assert '"é' in text, "non-ASCII stays UTF-8, as the native engine writes it"


def test_the_native_extra_is_pinned_to_this_release() -> None:
    pyproject = (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    assert f'"packvium-native-rust=={packvium_native.__version__}"' in pyproject
