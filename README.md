# packvium-native

Optional native backend selector for [Packvium](https://pypi.org/project/packvium/).
It uses the compiled Rust wheel when available and otherwise delegates to the pure
Python package.

Full documentation, the constraint reference and benchmarks live at
[packvium.com](https://packvium.com).

## Install

```bash
pip install 'packvium-native[native]' packvium
```

The `native` extra installs the platform wheel. To use only the fallback, install
`packvium-native` together with `packvium`.

`packvium-native` is not on PyPI yet. Until the native wheels ship, install it from source:

```bash
pip install git+https://github.com/toxakara/packvium-python-adapter packvium
```

## Quick start

```python
from packvium_native import backend, pack

result = pack({
    "items": [{
        "id": "book", "quantity": 4,
        "dimensions": {"length": "210", "width": "140", "height": "30"},
    }],
    "containers": [{
        "id": "carton",
        "inner_dimensions": {"length": "400", "width": "300", "height": "250"},
    }],
})

print(backend())          # "rust" or "python"
print(result["status"])  # "feasible"
```

The adapter does not replace the `packvium` import. It is useful when an application
wants one stable call site with a native fast path and a pure-Python fallback.

`pack_json` takes and returns the same JSON string every other Packvium binding speaks —
useful when the request is already serialized, or being forwarded as-is:

```python
from packvium_native import pack_json

response = pack_json('{"items":[...],"containers":[...]}')
```

## Examples

Runnable, in [`examples/`](examples). Each one is a single file you can read top to bottom
and execute without a project around it.

| File | What it shows |
| --- | --- |
| [`basic.py`](examples/basic.py) | Pack through the adapter and report which backend answered. |

```bash
python3 examples/basic.py
```

## Platforms

Native wheels support Linux x86_64/aarch64, macOS Apple Silicon/Intel and Windows. The
wheel uses Python's stable ABI, so one wheel supports Python 3.9 and later on its
platform.

## The Packvium family

One request and result contract, implemented independently in four engines (Rust,
Python, PHP, JavaScript) and held to identical placements on a shared fixture set.
Pick the package for your stack; mixing them in one system is safe.

Documentation, the constraint reference and the benchmarks are at
[packvium.com](https://packvium.com).

| Package | Install | Source |
| --- | --- | --- |
| Python — [`packvium`](https://pypi.org/project/packvium/) | `pip install packvium` | [packvium-python](https://github.com/toxakara/packvium-python) |
| PHP — [`packvium/packvium`](https://packagist.org/packages/packvium/packvium) | `composer require packvium/packvium` | [packvium-php](https://github.com/toxakara/packvium-php) |
| Rust — [`packvium`](https://crates.io/crates/packvium) | `packvium = "1.0"` | [packvium-rust](https://github.com/toxakara/packvium-rust) |
| Node.js — [`@packvium/engine`](https://www.npmjs.com/package/@packvium/engine) | `npm install @packvium/engine` | [packvium-node](https://github.com/toxakara/packvium-node) |
| Browser / WebAssembly — [`@packvium/browser`](https://www.npmjs.com/package/@packvium/browser) | `npm install @packvium/browser` | [packvium-wasm](https://github.com/toxakara/packvium-wasm) |
| PHP FFI bridge — [`packvium/native-bridge`](https://packagist.org/packages/packvium/native-bridge) | `composer require packvium/native-bridge` | [packvium-php-bridge](https://github.com/toxakara/packvium-php-bridge) |
| Python native selector — `packvium-native` | from source until the native wheels ship | [packvium-python-adapter](https://github.com/toxakara/packvium-python-adapter) |

## License

MIT. See [LICENSE](LICENSE).
