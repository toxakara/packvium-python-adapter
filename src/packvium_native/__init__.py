from __future__ import annotations

import json
from types import ModuleType
from typing import Any, Optional

__version__ = "1.7.0"

#: Each untyped model error's code and the prefix the core's `PackError` writes before its
#: detail (`packvium-core` `error.rs`). `packvium` reports a model it cannot build as reason
#: `invalid_value` with no field and the bare detail, and so does this adapter.
_MODEL_ERROR_PREFIXES = {
    "invalid_input": "invalid input: ",
    "invalid_number": "invalid numeric value: ",
    "unsupported_unit": "unsupported unit: ",
}


def _native() -> Optional[ModuleType]:
    try:
        import packvium_native_rust  # type: ignore
    except ImportError:
        return None
    return packvium_native_rust


def backend() -> str:
    return "rust" if _native() is not None else "python"


def pack_json(payload: str) -> str:
    native = _native()
    if native is not None:
        return _pack_natively(native, payload)
    return _pack_in_python(payload)


def _pack_natively(native: ModuleType, payload: str) -> str:
    try:
        return native.pack_json(payload)
    except native.PackviumError as error:
        refusal = _refusal_for(error)
        if refusal is error:
            raise
        if refusal is not None:
            raise refusal from error
    # No refusal this adapter can name -- a panic caught at the boundary, a solution that
    # failed the core's own validation -- is the library's failure, not the caller's, so the
    # pure engine answers the same request (the PHP bridge's `refusalFor` rule).
    return _pack_in_python(payload)


def _pack_in_python(payload: str) -> str:
    try:
        from packvium.serialization import pack_from_dict
    except ImportError as exc:
        raise RuntimeError(
            f"Install packvium=={__version__} or the packvium-native-rust wheel"
        ) from exc
    # The canonical spelling the native engine writes (docs/SERIALIZATION.md): keys sorted,
    # compact separators, UTF-8 left unescaped -- so the text does not depend on the backend.
    return json.dumps(
        pack_from_dict(json.loads(payload)),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _refusal_for(error: Exception) -> Optional[Exception]:
    """The `packvium` exception the pure engine raises for the request the core refused;
    `error` itself when it carries a code but `packvium` is not installed to supply a class; or
    None when it names no refusal `packvium` has a class for -- a missing or unmapped code,
    which the caller treats as a native failure and answers from the pure engine."""
    code = getattr(error, "code", None)
    if not isinstance(code, str):
        return None
    try:
        from packvium import FixedPlacementError, InvalidRequestError, UnsupportedFeatureError
    except ImportError:
        return error
    message = str(error)
    if code == "unsupported_feature":
        return UnsupportedFeatureError(message)
    prefix = _MODEL_ERROR_PREFIXES.get(code)
    if prefix is not None:
        detail = message[len(prefix):] if message.startswith(prefix) else message
        return InvalidRequestError("invalid_value", "", detail)
    named = [getattr(error, name, None) for name in ("reason", "field", "detail")]
    if not all(isinstance(part, str) for part in named):
        return None
    reason, field, detail = named
    if code == "invalid_request":
        return InvalidRequestError(reason, field, detail)
    if code == "invalid_fixed_placement":
        return FixedPlacementError(detail, reason, field)
    return None


def pack(payload: dict[str, Any]) -> dict[str, Any]:
    return json.loads(pack_json(json.dumps(payload, separators=(",", ":"))))


__all__ = ["pack", "pack_json", "backend", "__version__"]
