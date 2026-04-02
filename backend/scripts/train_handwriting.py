import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
import torch
from torch.utils.data import Dataset
from transformers import (
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    TrOCRProcessor,
    VisionEncoderDecoderModel,
)


SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
TRAINING_DIR = BACKEND_DIR / "training" / "handwriting"


def normalize_text(text: str) -> str:
    return " ".join((text or "").strip().split())


def levenshtein_distance(source: list[str], target: list[str]) -> int:
    if source == target:
        return 0
    if not source:
        return len(target)
    if not target:
        return len(source)

    previous = list(range(len(target) + 1))
    for i, source_item in enumerate(source, start=1):
        current = [i]
        for j, target_item in enumerate(target, start=1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (source_item != target_item)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current
    return previous[-1]


def character_error_rate(predictions: list[str], references: list[str]) -> float:
    total_distance = 0
    total_length = 0
    for prediction, reference in zip(predictions, references, strict=False):
        reference_chars = list(reference)
        prediction_chars = list(prediction)
        total_distance += levenshtein_distance(prediction_chars, reference_chars)
        total_length += max(len(reference_chars), 1)
    return total_distance / max(total_length, 1)


def word_error_rate(predictions: list[str], references: list[str]) -> float:
    total_distance = 0
    total_length = 0
    for prediction, reference in zip(predictions, references, strict=False):
        reference_words = reference.split()
        prediction_words = prediction.split()
        total_distance += levenshtein_distance(prediction_words, reference_words)
        total_length += max(len(reference_words), 1)
    return total_distance / max(total_length, 1)


def load_manifest(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")

    records: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            record = json.loads(line)
            if "image" not in record or "text" not in record:
                raise ValueError(
                    f"Manifest line {line_number} in {path} must include 'image' and 'text'."
                )
            records.append(record)

    if not records:
        raise ValueError(f"Manifest {path} is empty. Add labeled handwriting samples first.")

    return records


class HandwritingDataset(Dataset):
    def __init__(
        self,
        records: list[dict],
        processor: TrOCRProcessor,
        data_root: Path,
        max_label_length: int,
    ) -> None:
        self.records = records
        self.processor = processor
        self.data_root = data_root
        self.max_label_length = max_label_length

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> dict:
        record = self.records[index]
        image_path = self.data_root / record["image"]
        image = Image.open(image_path).convert("RGB")
        pixel_values = self.processor(images=image, return_tensors="pt").pixel_values.squeeze(0)

        labels = self.processor.tokenizer(
            normalize_text(record["text"]),
            padding="max_length",
            max_length=self.max_label_length,
            truncation=True,
        ).input_ids
        labels = [
            token_id if token_id != self.processor.tokenizer.pad_token_id else -100
            for token_id in labels
        ]

        return {
            "pixel_values": pixel_values,
            "labels": labels,
        }


@dataclass
class OCRCollator:
    processor: TrOCRProcessor

    def __call__(self, features: list[dict]) -> dict:
        pixel_values = [feature["pixel_values"] for feature in features]
        labels = [feature["labels"] for feature in features]

        batch = {
            "pixel_values": torch.stack(pixel_values),
            "labels": torch.tensor(labels),
        }
        return batch


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fine-tune a TrOCR handwriting model on labeled student handwriting crops."
    )
    parser.add_argument(
        "--train-manifest",
        default=str(TRAINING_DIR / "manifests" / "train.jsonl"),
        help="Path to the train JSONL manifest.",
    )
    parser.add_argument(
        "--val-manifest",
        default=str(TRAINING_DIR / "manifests" / "val.jsonl"),
        help="Path to the validation JSONL manifest.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(TRAINING_DIR / "models" / "trocr-finetuned"),
        help="Directory to save the fine-tuned OCR model.",
    )
    parser.add_argument(
        "--base-model",
        default="microsoft/trocr-base-handwritten",
        help="Base pretrained handwriting OCR model.",
    )
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--train-batch-size", type=int, default=8)
    parser.add_argument("--eval-batch-size", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=5e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--warmup-ratio", type=float, default=0.1)
    parser.add_argument("--logging-steps", type=int, default=25)
    parser.add_argument("--save-steps", type=int, default=200)
    parser.add_argument("--eval-steps", type=int, default=200)
    parser.add_argument("--max-label-length", type=int, default=128)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=1)
    parser.add_argument(
        "--use-fp16",
        action="store_true",
        help="Enable mixed precision if your GPU supports it.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    train_manifest = Path(args.train_manifest).resolve()
    val_manifest = Path(args.val_manifest).resolve()
    data_root = train_manifest.parent.parent
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    train_records = load_manifest(train_manifest)
    val_records = load_manifest(val_manifest)

    processor = TrOCRProcessor.from_pretrained(args.base_model)
    model = VisionEncoderDecoderModel.from_pretrained(args.base_model)
    model.config.decoder_start_token_id = processor.tokenizer.cls_token_id
    model.config.pad_token_id = processor.tokenizer.pad_token_id
    model.config.eos_token_id = processor.tokenizer.sep_token_id
    model.config.max_length = args.max_label_length
    model.config.early_stopping = True
    model.config.no_repeat_ngram_size = 0
    model.config.length_penalty = 1.0
    model.config.num_beams = 4

    train_dataset = HandwritingDataset(
        records=train_records,
        processor=processor,
        data_root=data_root,
        max_label_length=args.max_label_length,
    )
    val_dataset = HandwritingDataset(
        records=val_records,
        processor=processor,
        data_root=data_root,
        max_label_length=args.max_label_length,
    )
    collator = OCRCollator(processor=processor)

    training_args = Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        overwrite_output_dir=True,
        predict_with_generate=True,
        evaluation_strategy="steps",
        save_strategy="steps",
        logging_strategy="steps",
        per_device_train_batch_size=args.train_batch_size,
        per_device_eval_batch_size=args.eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        warmup_ratio=args.warmup_ratio,
        weight_decay=args.weight_decay,
        num_train_epochs=args.epochs,
        fp16=args.use_fp16 and torch.cuda.is_available(),
        logging_steps=args.logging_steps,
        eval_steps=args.eval_steps,
        save_steps=args.save_steps,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="cer",
        greater_is_better=False,
        remove_unused_columns=False,
        seed=args.seed,
        report_to=[],
    )

    def compute_metrics(eval_prediction) -> dict:
        predictions = eval_prediction.predictions
        labels = eval_prediction.label_ids

        decoded_predictions = processor.batch_decode(predictions, skip_special_tokens=True)
        sanitized_labels = [
            [token if token != -100 else processor.tokenizer.pad_token_id for token in sequence]
            for sequence in labels
        ]
        decoded_labels = processor.batch_decode(sanitized_labels, skip_special_tokens=True)
        decoded_predictions = [normalize_text(item) for item in decoded_predictions]
        decoded_labels = [normalize_text(item) for item in decoded_labels]

        cer = character_error_rate(decoded_predictions, decoded_labels)
        wer = word_error_rate(decoded_predictions, decoded_labels)
        return {
            "cer": round(cer, 4),
            "wer": round(wer, 4),
        }

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=processor.tokenizer,
        data_collator=collator,
        compute_metrics=compute_metrics,
    )

    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")
    print(f"Base model: {args.base_model}")
    print(f"Output directory: {output_dir}")

    trainer.train()
    trainer.save_model(str(output_dir))
    processor.save_pretrained(str(output_dir))

    final_metrics = trainer.evaluate()
    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(final_metrics, indent=2), encoding="utf-8")
    print("Saved fine-tuned OCR model and metrics.")


if __name__ == "__main__":
    main()
