# AI Answer Evaluation Backend

Production-oriented FastAPI backend for evaluating student answer sheets against a question paper and optional marking scheme.

## What is implemented

- FastAPI API with upload and reporting endpoints
- Modular OCR, question parsing, answer mapping, scoring, and plagiarism pipeline
- SQLite-backed persistence via SQLModel
- Local storage for uploaded assets
- Architecture and training notes in `docs/architecture.md`

## Important note

The codebase is designed as a deployable foundation, but a true `>95%` evaluation target requires:

- a domain-specific labeled answer-sheet dataset
- calibrated OCR for the document styles you receive
- rubric-specific evaluator tuning
- human moderation loops for edge cases

This backend includes a strong orchestration layer and a rule-based fallback evaluator. For production AI accuracy, swap the OCR and evaluation providers with fine-tuned models or hosted VLM/LLM services.

## Run locally

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Optional ML providers:

```bash
pip install -r requirements-ml.txt
```

## Train a handwriting OCR model

1. Put labeled line crops under `training/handwriting/raw/images/`.
2. Fill `training/handwriting/manifests/train.jsonl` and `val.jsonl`.
3. Install ML dependencies:

```bash
pip install -r requirements-ml.txt
```

4. Start training:

```bash
python scripts/train_handwriting.py
```

Or with npm:

```bash
npm run install:ml
npm run train:handwriting
```

5. The fine-tuned model will be saved to:

```text
training/handwriting/models/trocr-finetuned/
```

Once that folder contains a saved Hugging Face TrOCR model, the backend OCR pipeline will automatically load it.

## Main endpoints

- `GET /api/v1/health`
- `POST /api/v1/evaluations/run`
- `GET /api/v1/evaluations/submissions/{submission_id}`
- `POST /api/v1/plagiarism/submissions/{submission_id}`

## Suggested production upgrades

- PostgreSQL instead of SQLite
- Redis + Celery/RQ for background OCR/evaluation
- hosted VLM for hard handwriting OCR
- sentence embedding store for large-scale plagiarism search
- human review queue for low-confidence answers
