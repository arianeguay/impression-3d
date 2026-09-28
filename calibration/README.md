# Calibration log

Adventurer 5M, 0.4 nozzle, Polymaker Panchroma Neon PLA, `lego_minifig` profile.

| Date | Test | Model / script | Result | Applied |
|---|---|---|---|---|
| 2026-09-27 | First layer | `first_layer_ad5m.stl` | all nine squares complete and even, sheet peels in one piece, light through gaps between lines | `machine.z_offset=-0.02` in `profiles/figurine.json` |
| 2026-09-27 | Temperature 230 to 190 | `temp_tower_lego.stl`, `skill/scripts/temp_tower.py` | bridges and walls clean at every level, fine stringing everywhere, top levels unbreakable by hand | Panchroma preset `nozzle_temperature` 205 |
| | Flow rate | Orca GUI, Calibration > Flow rate | | |
| | Pressure advance | Orca GUI, Calibration > Pressure advance | | |
| | Retraction | Orca GUI, Calibration > Retraction | stringing seen on the temperature tower | |
| | LEGO fit coupon | to build | | |
