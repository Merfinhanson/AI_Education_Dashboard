from pathlib import Path

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


class PyMuPDFOCRProvider(BaseOCRProvider):
    name = "pymupdf"

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf"

    def extract(self, path: Path) -> OCRDocument:
        import fitz  # type: ignore

        document = fitz.open(path)
        text_pages = [page.get_text("text") for page in document]
        text = normalize_whitespace("\n".join(text_pages))
        return OCRDocument(
            text=text,
            provider=self.name,
            confidence=0.88 if text else 0.0,
            page_count=len(document),
        )


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
        self.providers = [
            NativeTextOCRProvider(),
            PyMuPDFOCRProvider(),
            TesseractImageOCRProvider(),
        ]

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
