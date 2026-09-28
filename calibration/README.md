# Calibration log

Adventurer 5M, 0.4 nozzle, Polymaker Panchroma Neon PLA, `lego_minifig` profile.

| Date | Test | Model / script | Result | Applied |
|---|---|---|---|---|
| 2026-09-27 | First layer | `first_layer_ad5m.stl` | all nine squares complete and even, sheet peels in one piece, light through gaps between lines | `machine.z_offset=-0.02` in `profiles/figurine.json` |
| 2026-09-27 | Temperature 230 to 190 | `temp_tower_lego.stl`, `skill/scripts/temp_tower.py` | bridges and walls clean at every level, fine stringing everywhere, top levels unbreakable by hand | Panchroma preset `nozzle_temperature` 205 |
| 2026-09-27 | Flow rate pass 1 (printed at 220 C, generic PLA profile) | Orca GUI, Calibration > Flow rate; block map from `flowrate-test-pass1.3mf`: back row +20/+15/+10, middle +5/0/-5, front -20/-15/-10 | ring of under-extrusion from -5 down, 0 and above smooth | flow ratio stays 0.98; pass 2 skipped, the LEGO fits were tuned at 0.98 |
| 2026-09-27 | Pressure advance 0 to 0.08 step 0.005, at 205 C | Orca GUI pattern project, sliced by the 2.4.2 CLI; chevrons stack from 0 at the placeholder cube to 0.08 | thick tips below 0.02, dashed arms from 0.05 up in the photo; chevron 10 cleanest in hand | Panchroma preset `pressure_advance` 0.045 (was 0.025) |
| 2026-09-27 | Retraction 0 to 2 mm step 0.2, at 205 C | Orca GUI tower sliced by the 2.4.2 CLI, `retraction_steps.py` for the per-mm lengths | strings only in the 0 mm band, clean from 0.2 up | stays 0.8: the test cannot separate 0.2 from 2.0. The tower's fine hairs came from long travels and hotter levels; next suspect is moisture, not retraction |
| | LEGO fit coupon | to build | | |
