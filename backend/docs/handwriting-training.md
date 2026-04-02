# Handwriting OCR Training

## Goal

Fine-tune a writer-independent handwriting OCR model on your own answer-sheet crops and let the backend load it automatically.

## Folder layout

See [README](/C:/Users/merfi/.codex/worktrees/e49d/Project/backend/training/handwriting/README.md) in `training/handwriting/`.

## Recommended dataset policy

- crop at line level first
- keep transcripts exact
- split by student
- keep hard handwriting in validation
- include noisy scans and skewed samples

## Training command

```bash
cd backend
python scripts/train_handwriting.py \
  --train-manifest training/handwriting/manifests/train.jsonl \
  --val-manifest training/handwriting/manifests/val.jsonl \
  --output-dir training/handwriting/models/trocr-finetuned
```

## Manifest example

```json
{"image":"raw/images/student_001/page_01_line_001.png","text":"Photosynthesis is the process by which plants make food.","student_id":"student_001","question_number":"1"}
```

## Metrics to watch

- CER below `0.10` is a strong early target
- WER below `0.20` is a practical starting point
- evaluate on writers not seen in training

## Backend integration

The backend looks for the trained model at the path from:

- [config.py](/C:/Users/merfi/.codex/worktrees/e49d/Project/backend/app/core/config.py)
- `OCR_HANDWRITING_MODEL_DIR` in `.env`

If the folder contains TrOCR model files such as `config.json` and `preprocessor_config.json`, [ocr.py](/C:/Users/merfi/.codex/worktrees/e49d/Project/backend/app/pipelines/ocr.py) will load it automatically.
