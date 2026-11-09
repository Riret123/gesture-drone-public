# R01 V03 - calibration evidence checklist
Blocked: no camera, target imagery, surveyed marker or board session is present.

Required artifact: camera serial/revision, lens/focus setting, image resolution and crop, intrinsic matrix, distortion convention, calibration images, reprojection summary by image, held-out reconstruction errors, units, marker physical measurements and calibration timestamp. Give calibration IDs to immutable bundles, not mutable filenames.

Extrinsics require a physically measured camera-to-body rotation/translation and a stated right-handed frame convention. Validate a known displacement along each axis and a known rotation independently. A downward-looking mounting description alone cannot establish signs. Recalibrate after focus, resolution, crop or mounting changes. Do not infer acceptable error from training-image reprojection alone.
