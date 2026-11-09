# Landmark dataset workflow (offline)

Supply explicit JSONL samples: each line is an object with only `label` and `points`.
Points is an array of 21 [x,y] pairs; labels are fist, open_palm, thumbs_up,
thumbs_down, peace, pointing, other. No images, names or personal metadata.
With src/gesture_control on PYTHONPATH:

```text
python -B -m gesture_control.dataset_cli input.jsonl output.csv
python -B tools/evaluate_gestures.py output.csv
```

The recorder refuses overwrite, validates before creating the CSV, and buffers
the input dataset in memory: use small offline datasets. The evaluator returns
an explicit confusion matrix and null accuracy for an empty dataset. Split by
session/person for future real evaluations; synthetic fixtures do not establish
general accuracy. Nothing here captures camera frames or publishes commands.
Keep private datasets outside source changes. Never include secrets in any input.
