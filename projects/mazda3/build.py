"""Scale a Mazda3 STL to 1:64 and join its floating wheels to the body with axles."""
import sys
import numpy as np
import trimesh

src, real_length_mm, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
AXLE_D = 2.4
FLAT = 0.3  # tire flat on the plate, so the car stands on four patches instead of four lines

m = trimesh.load(src, force="mesh")
m.apply_scale(real_length_mm / 64 / m.extents[1])
m.apply_translation(-m.bounds[0] * [0, 0, 1])
parts = m.split(only_watertight=True)
body = max(parts, key=lambda p: len(p.faces))
wheels = [p for p in parts if p is not body]

axles = []
for front in (True, False):
    pair = [w for w in wheels if (w.bounds.mean(0)[1] < 0) == front]
    a, b = (w.bounds.mean(0) for w in pair)
    axle = trimesh.creation.cylinder(radius=AXLE_D / 2, segment=[a, b], sections=48)
    axles.append(axle)

car = trimesh.boolean.union([body, *wheels, *axles], engine="manifold")
car = car.slice_plane([0, 0, FLAT], [0, 0, 1], cap=True)
car.apply_translation([0, 0, -FLAT])
assert car.is_watertight and len(car.split()) == 1
car.export(out)
print("extents", np.round(car.extents, 2), "volume", round(car.volume), "faces", len(car.faces))
