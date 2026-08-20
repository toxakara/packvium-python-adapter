"""Pack through the adapter, whichever backend happens to be installed.

Run it:

    python3 examples/basic.py

This package is a thin selector, not an engine. It tries the compiled Rust wheel
(`packvium-native-rust`) first and uses the pure-Python `packvium` package when that
wheel is not installed for your platform. Both answer the same shared JSON contract, so
your code does not branch on which one is present -- that is the whole point of the
adapter.

`backend()` tells you which one answered, which is worth logging once at startup: it is
the difference between "we are running the compiled engine" and "we quietly fell back",
and you want to find that out from a log line rather than from a latency graph.
"""

from packvium_native import __version__, backend, pack

print(f"adapter {__version__} using the {backend()} backend\n")

request = {
    "items": [
        # Lengths and weights are strings on purpose. They are parsed into exact
        # integers, so "0.1" means a tenth of a millimetre and never
        # 0.09999999999999999. Plain integers and fractions like "3/16" work too.
        {
            "id": "mug",
            "quantity": 6,
            "dimensions": {"length": "120", "width": "120", "height": "100"},
            "weight": "400 g",
        },
        {
            "id": "plate",
            "quantity": 8,
            "dimensions": {"length": "260", "width": "260", "height": "20"},
            "weight": "600 g",
        },
        # Too long for the box in every orientation, so it cannot be placed.
        {
            "id": "ladder",
            "quantity": 1,
            "dimensions": {"length": "1800", "width": "300", "height": "100"},
            "weight": "6 kg",
        },
    ],
    "containers": [
        {
            "id": "box",
            "inner_dimensions": {"length": "400", "width": "400", "height": "400"},
            "max_payload": "15 kg",
            "cost_minor": 180,
        }
    ],
}

result = pack(request)

print(f"status: {result['status']}")
print(f"containers opened: {len(result['containers'])}")

for index, container in enumerate(result["containers"], start=1):
    placements = container["placements"]
    print(f"\nbox #{index}: {len(placements)} placement(s)")
    for placement in placements:
        # Every measurement arrives as {"ticks", "value", "unit"}: `ticks` is the exact
        # integer the engine reasoned about, `value` is that number written for a human.
        position = placement["position"]
        print(
            f"  {placement['item_type']:8s} at "
            f"({position['x']['value']}, {position['y']['value']}, {position['z']['value']}) "
            f"{position['x']['unit']}  orientation {placement['orientation']}"
        )

# A refusal is an answer, not an error.
if result["unpacked_items"]:
    print("\nnot packed:")
    for unpacked in result["unpacked_items"]:
        print(f"  {unpacked['item_id']:10s} {unpacked['reason']}")
