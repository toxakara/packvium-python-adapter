import json
from pathlib import Path

import pytest

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
