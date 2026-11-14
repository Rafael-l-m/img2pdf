from __future__ import annotations

from pathlib import Path

from natsort import natsorted

from config.config_parser import get_args
from config.pdf_config import PDFConfig
from config.validators import (
    validate_args,
    validate_input_dir,
    validate_output_path,
    load_input_json,
)
from entry.image_entry import ImageEntry
from pdf_generator.pdf_generator import images_to_pdf

import logging, sys


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif", ".webp"}


def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )


def sort_images(image_paths: list[Path], sort_by: str = "natural") -> list[Path]:
    if sort_by == "natural":
        return natsorted(image_paths, key=lambda path: path.name)
    if sort_by == "name":
        return sorted(image_paths, key=lambda path: path.name.lower())
    if sort_by == "mtime":
        return sorted(image_paths, key=lambda path: path.stat().st_mtime)
    if sort_by == "size":
        return sorted(image_paths, key=lambda path: path.stat().st_size)
    raise ValueError(f"Unsupported sort method: {sort_by}")


def collect_directory_images(input_dir: Path, sort_by: str) -> list[ImageEntry]:
    input_dir = validate_input_dir(input_dir)
    image_paths = [
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    ]
    image_paths = sort_images(image_paths, sort_by)

    return [
        ImageEntry(id=index, path=path, order=index + 1)
        for index, path in enumerate(image_paths)
    ]


def main() -> int:
    args = get_args()
    setup_logging(args.verbose)

    try:
        validate_args(args)

        if args.json is not None:
            image_entries = load_input_json(args.json)

        else:
            input_dir = args.input if args.input is not None else Path.cwd()
            image_entries = collect_directory_images(input_dir, args.sort)

        if not image_entries:
            raise ValueError("No supported images found.")

        if args.verbose:
            logging.debug("Found %d images", len(image_entries))

            for entry in image_entries:
                logging.debug("%s", entry)

        output_path = validate_output_path(args.output)

        custom_size = (
            (args.width, args.height)
            if args.paper == "CUSTOM"
            else None
        )

        config = PDFConfig(
            paper=args.paper,
            orientation=args.orientation,
            fit=args.fit,
            margin=args.margin * 72 / 25.4,  # mm -> pt
            background=args.background,
            dpi=args.dpi,
            align=args.align,
            custom_size=custom_size,
            title=args.title,
            author=args.author,
            subject=args.subject,
            creator="img2pdf",
        )

        def on_progress(current: int, total: int) -> None:
            sys.stderr.write(f"\rGenerating PDF: {current}/{total}")
            sys.stderr.flush()
            if current == total:
                sys.stderr.write("\n")

        images_to_pdf(
            entries=image_entries,
            output=output_path,
            config=config,
            progress_callback=on_progress,
        )

        logging.info("PDF generated successfully: %s", output_path)
        return 0

    except (ValueError, OSError) as exc:
        logging.error("%s", exc)
        return 1

    except Exception:
        logging.exception("Unexpected error while generating PDF")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

    # pyinstaller --clean --noconfirm --onefile --console --name img2pdf main.py
