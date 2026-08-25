from __future__ import annotations

import json
from typing import Any

__version__ = "0.1.3"


def backend() -> str:
    try:
        import packvium_native_rust  # type: ignore
        return "rust"
    except ImportError:
        return "python"


def pack_json(payload: str) -> str:
    try:
        import packvium_native_rust  # type: ignore
        return packvium_native_rust.pack_json(payload)
    except ImportError:
        try:
            from packvium.serialization import pack_from_dict
        except ImportError as exc:
            raise RuntimeError(
                "Install packvium 0.1.0 or the packvium-native-rust wheel"
            ) from exc
        return json.dumps(
            pack_from_dict(json.loads(payload)),
            separators=(",", ":"),
        )


def pack(payload: dict[str, Any]) -> dict[str, Any]:
    return json.loads(pack_json(json.dumps(payload, separators=(",", ":"))))


__all__ = ["pack", "pack_json", "backend", "__version__"]
