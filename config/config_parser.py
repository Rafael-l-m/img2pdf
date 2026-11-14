from __future__ import annotations

from pathlib import Path

import argparse


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="img2pdf",
        description="Batch Image to PDF Converter",
        epilog="Example: img2pdf --input images_dir --output output.pdf",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    input_group = parser.add_mutually_exclusive_group(required=True)

    input_group.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input image directory",
    )

    input_group.add_argument(
        "--json",
        type=Path,
        default=None,
        help="JSON file containing an images list",
    )

    parser.add_argument(
        "--sort",
        choices=["natural", "name", "mtime", "size"],
        default="natural",
        help="Image sorting method (directory input only)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output.pdf"),
        help="Output PDF file path",
    )

    parser.add_argument(
        "--paper",
        type=str.upper,
        choices=["A3", "A4", "A5", "LETTER", "LEGAL", "ORIGINAL", "CUSTOM"],
        default="A4",
        help="PDF page size",
    )

    parser.add_argument(
        "--orientation",
        choices=["auto", "portrait", "landscape"],
        default="auto",
        help="Page orientation",
    )

    parser.add_argument(
        "--fit",
        choices=["contain", "cover", "stretch", "original", "width"],
        default="contain",
        help="Image fitting mode",
    )

    parser.add_argument(
        "--margin",
        type=float,
        default=0,
        help="Page margin in millimeters",
    )

    parser.add_argument(
        "--background",
        default="white",
        help="Page background color (color name or hex value)",
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI used for original image physical dimensions",
    )

    parser.add_argument(
        "--align",
        choices=["center", "top", "bottom", "left", "right"],
        default="center",
        help="Image alignment",
    )

    parser.add_argument(
        "--width",
        type=float,
        help="Custom page width in millimeters (requires --paper CUSTOM)",
    )

    parser.add_argument(
        "--height",
        type=float,
        help="Custom page height in millimeters (requires --paper CUSTOM)",
    )

    parser.add_argument("--title", default="Generated PDF", help="PDF document title")
    parser.add_argument("--author", default="", help="PDF document author")
    parser.add_argument("--subject", default="", help="PDF document subject")

    return parser


def get_args() -> argparse.Namespace:
    return get_parser().parse_args()
