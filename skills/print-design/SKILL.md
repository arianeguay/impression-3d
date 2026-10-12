---
name: print-design
description: Turn a 3D model into printable parts for Ariane's Flashforge Adventurer 5M - inspect it, scale it, fix joints and fits, choose each part's orientation and whether it needs supports. Use when the user shares a model (.3mf, .stl, MakerWorld/Printables link), wants it at a given size or LEGO scale, reports a joint too tight or too loose, or a part that broke or toppled because of its shape. Triggers - "imprime ce modèle", "prépare le fichier", "taille lego", "c'est trop serré", "c'est trop lousse", "ça a cassé". Hands off to print-prepare.
---

# Designing printable parts

Read `~/dev/src/impression-3d/reference.md` first: setup, filaments, where files go.
This skill ends with oriented STL parts and, per part, whether it needs supports or a raft. Then
use **print-prepare** to slice them.

## Steps

1. **Inspect the model before touching settings.** Unzip the 3MF with Python `zipfile`, read the
   designer description (`3D/3dmodel.model` metadata), `Metadata/project_settings.config` and
   `model_settings.config`. Measure parts with trimesh: bounding boxes, and `mesh.section()` slices
   to find studs, holes and pins.
2. **Export each object to STL** with its build transform applied (flip triangle winding when the
   transform's determinant is negative). MakerWorld / Bambu Studio 3MFs cannot be sliced as-is.
3. **Fix geometry by editing vertices**, not by scaling a part up or down to cheat a fit (see Fits).
4. **Choose each part's orientation and support need** (see Orientation), and state them.
5. **Record the project** in `projects/<name>/`: final parts and what changed, with the measurement
   that justified it, then commit.

## Fits

- **Every part of an assembly at one scale.** Different scales per part broke every joint.
- **Designers often model press fits at zero clearance.** Head socket = neck stud diameter, leg hole
  0.07 mm bigger than the pin. Scaling down shrinks the gap to nothing. Fix it by moving the hole's
  vertices radially, keeping the part itself at scale. **Target ~0.15 mm on the diameter for a joint
  that must turn and stay on** (leg on hip pin: 0.07 seized, 0.30 slid off, 0.15 clips); the head
  socket sits at 0.16 over its stud. `standards/lego_minifig.json` holds the tested value per joint.
- **Hollow studs with sub-mm walls snap off.** Real LEGO studs flex, printed ones shear at the base.
  Fill the hollow and slim the stud 0.1 mm.
- **Printed studs come out thinner than modeled, and the material moves the number.** A neck stud
  modeled at 4.9 gripped a real LEGO head in PETG and was loose in PLA. The PLA value is in
  `standards/lego_minifig.json`.
- A fit that is unsure: print `calibration/lego_fit_coupon.stl` (three sizes per joint) before a
  whole part.

- **Scaling up grows clearances too.** A minifig skeleton at 500% had 0.85 mm of play at the neck
  (0.17 at 1x): refit every joint at the target scale, the same as when scaling down.
- **A printed snap must flex within a layer.** Both 500% skeleton arms cracked at the shoulder clip,
  whose two halves parted across the layers; turned so they part sideways, the same clip flexed
  without cracking. Scaling keeps a molded snap's strain, not a printed one's: layer bonds are the
  weak direction.
- **Look for floating shells in the source.** The skeleton's shoulder clip had two side walls
  floating 0.08 mm off it (0.4 mm at 500%); fusing one closed the clip and it cracked. The real
  LEGO arm has an open C clip: drop such shells rather than fuse them, after checking the real part.
- **Make every mesh manifold before slicing, without changing its shape.** Non-manifold edges make
  Orca drop layers silently (see print-prepare). pymeshfix closed the skeleton head but filled in
  its nose and an eye; giving each sheet its own copy of the shared edge's vertices fixed it, with
  each copy nudged 0.002 mm into its sheet, since an STL merges vertices left on the same point
  (`projects/skeleton500/build.py`, `split_nonmanifold`).

## Orientation and supports

- **Start from the designer's orientation and the user's, not a clever one.** Flipping Oogie's hip
  studs-up put it on a raft and supports, and it split in two coming off them. Studs on the plate,
  as designed and as the user had said, needs no support at all: the block bridges between the studs.
  When the user names an orientation, restate it in geometric terms (which face touches the plate)
  before slicing.
- **Pegs and studs break across layers.** A vertical stud is a stack of discs and snaps at its root.
  Lay the part so its studs are horizontal: Oogie's hip studs fit a real torso but one snapped when
  printed vertical; lying on its front face they print along their length (33 mm2 contact, 7.7 mm
  tall). Never print stud tips on the plate, where the first layer's squish makes them oversize.
- **Check the weakest layer before choosing an orientation.** Section the part every ~0.4 mm and take
  the smallest cross-section: Oogie's arm standing on its tip had a 2.3 mm2 layer and snapped there,
  on its edge the weakest is 17.7 mm2. Score candidates on weakest layer, supported area inside
  cavities (faces >0.4 mm inside the convex hull) and supported area on the visible outside, then pick.
- **A pocket whose ceiling overhangs gets filled with support, and its inside comes out rough.**
  Minimizing supported overhang alone is not enough: Oogie's flipper arm standing on its thin tip
  had the least support (19 mm2) and the cleanest pocket, and snapped at its 2.3 mm2 weakest layer.
  On its edge (weakest layer 17.7 mm2, supports split between pocket and outside) it printed whole.
- **A designer's file orientation is not a print orientation for a raft part.** The 500% Oogie
  arm as placed in the MakerWorld file touched its raft on 15 mm2 and failed at 1.2 mm; laid on
  its edge (`trimesh.poses.compute_stable_poses`, then the pose with the most contact) it sits on
  126 mm2. Run the contact check below on every part before slicing, at every scale.
- **Measure every part's bed contact before deciding supports.** Section the mesh 0.1 mm above its
  lowest point and compare the area to the height. A part whose height over the square root of its
  contact area is above ~5 topples at small scale, even when its overhangs would print unsupported
  at full size: give it a 3-layer raft and normal supports. Measured: a 16.4 mm head on 2.4 mm2 and a
  12.8 mm hip on 2.3 mm2 both went to spaghetti without them, while a torso on 42 mm2 and legs on
  29 mm2 printed clean with none.

## LEGO minifigure reference

The machine-readable version, with what to **model** for each joint on this printer and the test
behind it, is `standards/lego_minifig.json`. Update that file (and its evidence) whenever a fit is
tested. A figure advertised "500%" is 5x a minifig: 20% brings it back, and the torso width confirms it.

Official LDraw geometry (1 LDU = 0.4 mm; parts at `library.ldraw.org/library/official/parts/`, the
real shapes live in the `s/` subfiles, the patterned `.dat` only carry decals):

| Feature | mm |
|---|---|
| Torso bottom width x height x depth | 15.2 x 12.8 x 8.0 |
| Neck stud | 4.8 diameter, 4.8 tall above the torso |
| Hips width | 14.4 |
| Leg width | 7.2 |
| Hip top to sole | 16.0 |
| Shoulder hole | 4.0 diameter through a 0.8 mm wall (hollow torso) |
| Arm pin (`knob1.dat`) | 4.0 x 0.8 neck, then a 4.4 snap lip, split and hollow |
| Leg bottom hole (grips a plate stud) | 4.8 x 4.8 square, 1.6 deep |
| Plate stud | 4.8 diameter, 1.7 tall |

Printed holes come out about 0.15 mm small plus first-layer squish: model a stud-receiving hole at
5.1 x 5.1 and 1.9 deep (5.0 fit a baseplate only just, 5.1 fits). Keep at least 0.78 mm of wall;
widen toward the thick side if the hole is off-center.

A snap lip cannot work on a solid printed torso and a split 4 mm pin breaks when printed: use a
plain friction cylinder instead. If friction is not enough, the next step is an acorn peg, which
needs a deeper shoulder hole with a groove, so a new torso. A ball resting on a hole's rim holds
nothing at minifig scale.
