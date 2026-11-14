from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Paper = Literal["A3", "A4", "A5", "LETTER", "LEGAL", "ORIGINAL", "CUSTOM"]
Orientation = Literal["auto", "portrait", "landscape"]
FitMode = Literal["contain", "cover", "stretch", "original", "width"]
Alignment = Literal["center", "top", "bottom", "left", "right"]


@dataclass(frozen=True, slots=True)
class PDFConfig:
    paper: Paper = "A4"
    orientation: Orientation = "auto"
    fit: FitMode = "contain"

    # ReportLab points (1 pt = 1/72 inch)
    margin: float = 0.0

    background: str = "white"
    dpi: int = 300
    align: Alignment = "center"

    # Custom page size in millimeters: (width, height)
    custom_size: tuple[float, float] | None = None

    title: str = "Generated PDF"
    author: str = ""
    subject: str = ""
    creator: str = "img2pdf"
