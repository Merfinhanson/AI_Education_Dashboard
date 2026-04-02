from io import BytesIO
from pathlib import Path

from app.core.config import get_settings
from app.schemas.domain import OCRDocument
from app.utils.text import normalize_whitespace


class BaseOCRProvider:
    name = "base"

    def supports(self, path: Path) -> bool:
        return False

    def extract(self, path: Path) -> OCRDocument:
        raise NotImplementedError


class NativeTextOCRProvider(BaseOCRProvider):
    name = "native-text"
    supported_extensions = {".txt", ".md", ".json", ".csv"}

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self.supported_extensions

    def extract(self, path: Path) -> OCRDocument:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return OCRDocument(
            text=normalize_whitespace(text),
            provider=self.name,
            confidence=0.99,
            page_count=1,
        )


class PyMuPDFTextLayerProvider(BaseOCRProvider):
    name = "pymupdf-text-layer"

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf"

    def extract(self, path: Path) -> OCRDocument:
        import fitz  # type: ignore

        document = fitz.open(path)
        text_pages = [page.get_text("text") for page in document]
        text = normalize_whitespace("\n".join(text_pages))

        # Short or empty output usually means a scanned PDF with no usable text layer.
        if len(text) < 20:
            text = ""

        return OCRDocument(
            text=text,
            provider=self.name,
            confidence=0.9 if text else 0.0,
            page_count=len(document),
        )


class TrOCRHandwritingProvider(BaseOCRProvider):
    name = "trocr-handwriting"
    supported_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}

    def __init__(self, model_dir: str, device: str = "cpu", max_new_tokens: int = 256) -> None:
        self.model_dir = Path(model_dir)
        self.device_name = device
        self.max_new_tokens = max_new_tokens
        self._processor = None
        self._model = None
        self._device = None

    def supports(self, path: Path) -> bool:
        return (
            path.suffix.lower() in self.supported_extensions and self._has_model_assets()
        )

    def extract(self, path: Path) -> OCRDocument:
        if path.suffix.lower() == ".pdf":
            page_texts = self._extract_pdf(path)
            text = normalize_whitespace("\n".join(page_texts))
            return OCRDocument(
                text=text,
                provider=self.name,
                confidence=0.86 if text else 0.0,
                page_count=len(page_texts),
            )

        image = self._load_image(path)
        text = self._transcribe_image(image)
        return OCRDocument(
            text=text,
            provider=self.name,
            confidence=0.84 if text else 0.0,
            page_count=1,
        )

    def _has_model_assets(self) -> bool:
        return (
            self.model_dir.exists()
            and (self.model_dir / "config.json").exists()
            and (self.model_dir / "preprocessor_config.json").exists()
        )

    def _load(self) -> None:
        if self._processor is not None and self._model is not None:
            return

        import torch  # type: ignore
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel  # type: ignore

        resolved_device = self.device_name
        if resolved_device == "cuda" and not torch.cuda.is_available():
            resolved_device = "cpu"

        self._device = torch.device(resolved_device)
        self._processor = TrOCRProcessor.from_pretrained(self.model_dir)
        self._model = VisionEncoderDecoderModel.from_pretrained(self.model_dir)
        self._model.to(self._device)
        self._model.eval()

    def _load_image(self, path: Path):
        from PIL import Image  # type: ignore

        return Image.open(path).convert("RGB")

    def _extract_pdf(self, path: Path) -> list[str]:
        import fitz  # type: ignore
        from PIL import Image  # type: ignore

        document = fitz.open(path)
        page_texts: list[str] = []
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(BytesIO(pixmap.tobytes("png"))).convert("RGB")
            page_texts.append(self._transcribe_image(image))
        return page_texts

    def _transcribe_image(self, image) -> str:
        self._load()

        import torch  # type: ignore

        pixel_values = self._processor(images=image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(self._device)
        with torch.no_grad():
            generated_ids = self._model.generate(
                pixel_values,
                max_new_tokens=self.max_new_tokens,
                num_beams=4,
            )
        text = self._processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return normalize_whitespace(text)


class TesseractImageOCRProvider(BaseOCRProvider):
    name = "tesseract"
    supported_extensions = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self.supported_extensions

    def extract(self, path: Path) -> OCRDocument:
        from PIL import Image  # type: ignore
        import pytesseract  # type: ignore

        image = Image.open(path)
        text = normalize_whitespace(pytesseract.image_to_string(image))
        return OCRDocument(
            text=text,
            provider=self.name,
            confidence=0.72 if text else 0.0,
            page_count=1,
        )


class OCRPipeline:
    def __init__(self) -> None:
        settings = get_settings()
        self.providers = [
            NativeTextOCRProvider(),
            PyMuPDFTextLayerProvider(),
        ]

        if settings.ocr_enable_handwriting_model:
            self.providers.append(
                TrOCRHandwritingProvider(
                    model_dir=settings.ocr_handwriting_model_dir,
                    device=settings.ocr_device,
                    max_new_tokens=settings.ocr_max_new_tokens,
                )
            )

        self.providers.append(TesseractImageOCRProvider())

    def extract_text(self, file_path: str) -> OCRDocument:
        path = Path(file_path)
        errors: list[str] = []

        for provider in self.providers:
            if not provider.supports(path):
                continue
            try:
                result = provider.extract(path)
            except ModuleNotFoundError as exc:
                errors.append(f"{provider.name}: missing dependency ({exc})")
                continue
            except Exception as exc:
                errors.append(f"{provider.name}: {exc}")
                continue

            if result.text:
                return result

        error_text = "; ".join(errors) if errors else "no compatible OCR provider found"
        raise RuntimeError(
            "Unable to extract text from the supplied document. "
            "Install optional ML OCR dependencies or plug in a hosted VLM OCR provider. "
            f"Details: {error_text}"
        )
