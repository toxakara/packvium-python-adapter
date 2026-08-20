# packvium-native

Optional native backend selector for [Packvium](https://pypi.org/project/packvium/).
It uses the compiled Rust wheel when available and otherwise delegates to the pure
Python package.

## Install

```bash
pip install 'packvium-native[native]' packvium
```

The `native` extra installs the platform wheel. To use only the fallback, install
`packvium-native` together with `packvium`.

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

## License

MIT. See [LICENSE](LICENSE).
