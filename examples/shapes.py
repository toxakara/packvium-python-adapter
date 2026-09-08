"""Shapes through the adapter: the same answer from whichever backend is installed.

Run it:

    python3 examples/shapes.py

`basic.py` shows that the adapter picks a backend for you. This example answers the
question that follows: does the accelerated path support everything the pure one does?

It does, and the point is worth making with the newest capability rather than the oldest.
`shape_type` says an item is not simply its declared box -- `convex_hull` narrows it in
space, `compressible` in height under load -- and both belong to the shared JSON contract
rather than to any one engine. The adapter forwards the request untouched, so the numbers
below are the same whether the compiled Rust wheel answered or the pure-Python package
did. `backend()` says which one it was; the answer does not depend on it.

If you ever see these numbers change when the backend changes, that is a bug worth
reporting rather than a difference to work around.
"""

from packvium_native import backend, pack

print(f"answered by the {backend()} backend\n")

MM = {"units": {"length": "mm"}}


def crate(length: str, width: str, height: str) -> list:
    return [{"id": "crate",
             "inner_dimensions": {"length": length, "width": width, "height": height}}]


def summarise(label: str, request: dict) -> None:
    """Print only what the shape changed: containers, placements and unused volume."""
    result = pack(request)
    placed = sum(len(container["placements"]) for container in result["containers"])
    print(f"  {label:22s} {len(result['containers'])} container(s), {placed} placed, "
          f"unused volume {result['score'][3]} ppm")


# ------------------------------------------------------------------ convex_hull
#
# Two triangular prisms cut from the same cube along its diagonal. Their bounding boxes
# are identical and each fills the crate alone, so as cuboids the second has nowhere to
# go. As hulls they are complementary halves and share the crate exactly: collisions are
# decided by an exact integer separating-axis test on the vertices, not a box overlap.

LOWER_WEDGE = [{"x": "0", "y": "0", "z": "0"}, {"x": "100", "y": "0", "z": "0"},
               {"x": "0", "y": "100", "z": "0"}, {"x": "0", "y": "0", "z": "100"},
               {"x": "100", "y": "0", "z": "100"}, {"x": "0", "y": "100", "z": "100"}]
UPPER_WEDGE = [{"x": "100", "y": "100", "z": "0"}, {"x": "100", "y": "0", "z": "0"},
               {"x": "0", "y": "100", "z": "0"}, {"x": "100", "y": "100", "z": "100"},
               {"x": "100", "y": "0", "z": "100"}, {"x": "0", "y": "100", "z": "100"}]


def wedge(item_id: str, vertices: "list | None") -> dict:
    item = {"id": item_id, "quantity": 1,
            "dimensions": {"length": "100", "width": "100", "height": "100"},
            "weight": {"value": "1", "unit": "kg"}}
    if vertices is not None:
        item["shape_type"] = "convex_hull"
        item["hull_vertices"] = vertices
    return item


print("convex_hull -- two complementary wedges cut from one cube")
summarise("as cuboids", {**MM,
                         "items": [wedge("wedge-lower", None), wedge("wedge-upper", None)],
                         "containers": crate("100", "100", "100")})
summarise("as hulls", {**MM,
                       "items": [wedge("wedge-lower", LOWER_WEDGE),
                                 wedge("wedge-upper", UPPER_WEDGE)],
                       "containers": crate("100", "100", "100")})

# ----------------------------------------------------------------- compressible
#
# `compression_ratio` is the fraction of its own height an item may lose under load;
# `max_compression_pressure_kpa` is where yielding becomes crushing and the load is
# refused instead. `must_be_on_floor` is not decoration -- without it the solver may put
# the brick underneath, nothing bears on the cushion, and the feature never engages.

CUSHION = {"id": "cushion", "quantity": 1,
           "dimensions": {"length": "100", "width": "100", "height": "100"},
           "weight": {"value": "2", "unit": "kg"},
           "must_be_on_floor": True,
           "shape_type": "compressible",
           "compression_ratio": 0.25,
           "max_compression_pressure_kpa": 100}


def brick(kilograms: int) -> dict:
    return {"id": "brick", "quantity": 1,
            "dimensions": {"length": "100", "width": "100", "height": "100"},
            "weight": {"value": str(kilograms), "unit": "kg"}}


# The crate is 100x100x200 and both items are 100 mm cubes, so rigidly they fill it and
# nothing is unused. Under 101 kg the cushion gives up part of its quarter. One more
# kilogram crosses 100 kPa over its 0.01 m^2 face and the stack is refused instead.
print("\ncompressible -- a cushion that yields to the load above it")
for kilograms in (101, 102):
    summarise(f"brick {kilograms} kg", {**MM, "items": [CUSHION, brick(kilograms)],
                                        "containers": crate("100", "100", "200")})
