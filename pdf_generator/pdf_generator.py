from __future__ import annotations

from pathlib import Path
from typing import Callable

from PIL import Image, ImageOps

from reportlab.lib.colors import toColor
from reportlab.lib.pagesizes import A3, A4, A5, LEGAL, LETTER
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from config.pdf_config import PDFConfig
from entry.image_entry import ImageEntry

import os, tempfile


ProgressCallback = Callable[[int, int], None]

PAPER_SIZES: dict[str, tuple[float, float]] = {
    "A3": A3,
    "A4": A4,
    "A5": A5,
    "LETTER": LETTER,
    "LEGAL": LEGAL,
}


def get_page_size(
    paper: str,
    orientation: str,
    image_size: tuple[int, int],
    dpi: int = 300,
    custom_size: tuple[float, float] | None = None,
) -> tuple[float, float]:

    image_width, image_height = image_size

    if image_width <= 0 or image_height <= 0:
        raise ValueError("Invalid image dimensions.")

    if dpi <= 0:
        raise ValueError("DPI must be positive.")

    paper = paper.upper()

    orientation = orientation.lower()

    if orientation not in {"auto", "portrait", "landscape"}:
        raise ValueError(f"Unsupported orientation: {orientation}")

    if paper == "ORIGINAL":
        width = image_width * 72 / dpi
        height = image_height * 72 / dpi

    elif paper == "CUSTOM":
        if custom_size is None:
            raise ValueError("Custom paper size is required.")

        width_mm, height_mm = custom_size
        if width_mm <= 0 or height_mm <= 0:
            raise ValueError("Custom dimensions must be positive.")

        width = width_mm * 72 / 25.4
        height = height_mm * 72 / 25.4

    else:
        if paper not in PAPER_SIZES:
            raise ValueError(f"Unsupported paper size: {paper}")
        width, height = PAPER_SIZES[paper]

    if orientation == "auto":
        image_is_landscape = image_width > image_height
        page_is_landscape = width > height

        if image_is_landscape != page_is_landscape:
            width, height = height, width

    elif orientation == "landscape" and width < height:
        width, height = height, width

    elif orientation == "portrait" and width > height:
        width, height = height, width

    return float(width), float(height)


def calculate_layout(
    image_size: tuple[int, int],
    page_size: tuple[float, float],
    fit: str,
    margin: float = 0,
    align: str = "center",
    dpi: int = 300,
) -> tuple[float, float, float, float]:

    image_width, image_height = image_size

    page_width, page_height = page_size

    if image_width <= 0 or image_height <= 0:
        raise ValueError("Invalid image dimensions.")

    if page_width <= 0 or page_height <= 0:
        raise ValueError("Invalid page dimensions.")

    if dpi <= 0:
        raise ValueError("DPI must be positive.")

    if margin < 0:
        raise ValueError("Margin cannot be negative.")

    if margin * 2 >= page_width or margin * 2 >= page_height:
        raise ValueError("Margin is too large for the page.")

    fit = fit.lower()

    align = align.lower()

    valid_fits = {"contain", "cover", "stretch", "original", "width"}

    valid_alignments = {"center", "top", "bottom", "left", "right"}

    if fit not in valid_fits:
        raise ValueError(f"Unsupported fit mode: {fit}")

    if align not in valid_alignments:
        raise ValueError(f"Unsupported alignment: {align}")

    available_width = page_width - margin * 2
    available_height = page_height - margin * 2
    image_ratio = image_width / image_height

    if fit == "stretch":
        width, height = available_width, available_height

    elif fit == "contain":
        scale = min(
            available_width / image_width,
            available_height / image_height,
        )
        width, height = image_width * scale, image_height * scale

    elif fit == "cover":
        scale = max(
            available_width / image_width,
            available_height / image_height,
        )
        width, height = image_width * scale, image_height * scale

    elif fit == "original":
        width = image_width * 72 / dpi
        height = image_height * 72 / dpi

    else:  # width
        width = available_width
        height = width / image_ratio

    if align in {"center", "top", "bottom"}:
        x = (page_width - width) / 2

    elif align == "left":
        x = margin

    else:
        x = page_width - margin - width

    if align in {"center", "left", "right"}:
        y = (page_height - height) / 2

    elif align == "top":
        y = page_height - margin - height

    else:
        y = margin

    return float(x), float(y), float(width), float(height)


def _background_rgb(color_text: str) -> tuple[int, int, int]:

    try:
        color = toColor(color_text)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid background color: {color_text}") from exc

    return tuple(
        round(channel * 255)
        for channel in (color.red, color.green, color.blue)
    )


def _load_normalized_image(path: Path) -> Image.Image:

    with Image.open(path) as source:
        transposed = ImageOps.exif_transpose(source)

        try:
            transposed.load()
            return transposed.convert("RGBA")

        finally:
            if transposed is not source:
                transposed.close()


def images_to_pdf(
    entries: list[ImageEntry],
    output: Path,
    config: PDFConfig,
    progress_callback: ProgressCallback | None = None,
) -> None:

    if not entries:
        raise ValueError("No images provided.")

    if config.dpi <= 0:
        raise ValueError("DPI must be positive.")

    if config.margin < 0:
        raise ValueError("Margin cannot be negative.")

    if config.paper.upper() == "CUSTOM" and config.custom_size is None:
        raise ValueError("Custom paper size is required.")

    ordered_entries = sorted(entries, key=lambda entry: entry.order)
    output = Path(output)

    if output.suffix.lower() != ".pdf":
        raise ValueError("Output filename must have a .pdf extension.")

    if output.exists() and not output.is_file():
        raise ValueError(f"Output path is not a file: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    background_color = toColor(config.background)
    background_rgb = _background_rgb(config.background)

    temp_fd, temp_name = tempfile.mkstemp(
        suffix=".pdf",
        prefix=f".{output.stem}_",
        dir=output.parent,
    )
    os.close(temp_fd)
    temp_output = Path(temp_name)

    try:
        pdf = canvas.Canvas(str(temp_output), pageCompression=1)
        pdf.setTitle(config.title)
        pdf.setAuthor(config.author)
        pdf.setSubject(config.subject)
        pdf.setCreator(config.creator)

        total = len(ordered_entries)

        for index, entry in enumerate(ordered_entries, start=1):
            normalized_image: Image.Image | None = None
            background: Image.Image | None = None
            rgb_image: Image.Image | None = None

            try:
                if not entry.path.is_file():
                    raise FileNotFoundError(f"Image file does not exist: {entry.path}")

                normalized_image = _load_normalized_image(entry.path)
                image_size = normalized_image.size

                page_size = get_page_size(
                    paper=config.paper,
                    orientation=config.orientation,
                    image_size=image_size,
                    dpi=config.dpi,
                    custom_size=config.custom_size,
                )
                page_width, page_height = page_size

                x, y, width, height = calculate_layout(
                    image_size=image_size,
                    page_size=page_size,
                    fit=config.fit,
                    margin=config.margin,
                    align=config.align,
                    dpi=config.dpi,
                )

                background = Image.new(
                    "RGBA",
                    normalized_image.size,
                    (*background_rgb, 255),
                )
                background.alpha_composite(normalized_image)
                rgb_image = background.convert("RGB")

                pdf.setPageSize(page_size)
                pdf.setFillColor(background_color)
                pdf.rect(
                    0,
                    0,
                    page_width,
                    page_height,
                    fill=1,
                    stroke=0,
                )

                if config.fit.lower() == "cover":
                    pdf.saveState()

                    try:
                        clip_path = pdf.beginPath()
                        clip_path.rect(
                            config.margin,
                            config.margin,
                            page_width - config.margin * 2,
                            page_height - config.margin * 2,
                        )
                        pdf.clipPath(clip_path, stroke=0, fill=0)
                        pdf.drawImage(
                            ImageReader(rgb_image),
                            x,
                            y,
                            width=width,
                            height=height,
                            preserveAspectRatio=False,
                        )

                    finally:
                        pdf.restoreState()

                else:
                    pdf.drawImage(
                        ImageReader(rgb_image),
                        x,
                        y,
                        width=width,
                        height=height,
                        preserveAspectRatio=False,
                    )

                pdf.showPage()

                if progress_callback is not None:
                    progress_callback(index, total)

            finally:
                if rgb_image is not None:
                    rgb_image.close()

                if background is not None:
                    background.close()

                if normalized_image is not None:
                    normalized_image.close()

        pdf.save()
        os.replace(temp_output, output)

    finally:
        if temp_output.exists():
            temp_output.unlink()
