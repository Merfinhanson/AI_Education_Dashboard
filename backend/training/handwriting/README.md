# Handwriting Training Data

Use this folder to fine-tune a handwriting OCR model for your own students.

## Recommended structure

```text
training/
  handwriting/
    manifests/
      train.jsonl
      val.jsonl
      test.jsonl
    raw/
      images/
        student_001/
          page_01_line_001.png
          page_01_line_002.png
        student_002/
          page_01_line_001.png
    models/
      trocr-finetuned/
```

## Manifest format

Each line in `train.jsonl`, `val.jsonl`, and `test.jsonl` must be valid JSON:

```json
{"image":"raw/images/student_001/page_01_line_001.png","text":"Photosynthesis is the process by which plants make food.","student_id":"student_001","question_number":"1"}
```

Required fields:

- `image`: path to the crop, relative to `training/handwriting/`
- `text`: exact transcript for the crop

Recommended fields:

- `student_id`
- `question_number`
- `page_number`
- `split_source`

## Important data rule

Split by student, not by page. A single writer must not appear in both train and validation/test.

## Typical labeling pipeline

1. Convert PDFs to page images.
2. Crop lines or answer regions.
3. Transcribe each crop exactly.
4. Save one JSON object per crop.
5. Fine-tune using `scripts/train_handwriting.py`.
