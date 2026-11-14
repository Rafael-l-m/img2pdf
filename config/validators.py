from __future__ import annotations

from pathlib import Path
from argparse import Namespace

from entry.image_entry import ImageEntry

import json, os


def validate_args(args: Namespace) -> None:

    if args.dpi <= 0:
        raise ValueError("--dpi must be positive.")

    if args.margin < 0:
        raise ValueError("--margin cannot be negative.")

    if args.paper == "CUSTOM":

        if args.width is None or args.height is None:
            raise ValueError("--width and --height are required for CUSTOM paper.")

        if args.width <= 0 or args.height <= 0:
            raise ValueError("--width and --height must be positive.")

    elif args.width is not None or args.height is not None:
        raise ValueError("--width and --height can only be used with --paper CUSTOM.")


def validate_input_dir(input_dir: Path) -> Path:

    input_dir = Path(input_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_dir}")

    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    if not os.access(input_dir, os.R_OK):
        raise PermissionError(f"Input directory is not readable: {input_dir}")

    return input_dir


def validate_output_path(output_path: Path) -> Path:

    output_path = Path(output_path)

    if output_path.suffix.lower() != ".pdf":
        raise ValueError("Output filename must have a .pdf extension.")

    if output_path.exists() and not output_path.is_file():
        raise ValueError(f"Output path exists but is not a file: {output_path}")

    parent = output_path.parent

    if not parent.exists():
        raise FileNotFoundError(f"Output parent directory does not exist: {parent}")

    if not parent.is_dir():
        raise NotADirectoryError(f"Output parent path is not a directory: {parent}")

    if not os.access(parent, os.W_OK):
        raise PermissionError(f"Output parent directory is not writable: {parent}")

    return output_path


def validate_image_entries(images: list[dict]) -> None:

    ids: list[int] = []
    orders: list[int] = []

    for index, image in enumerate(images):
        if not isinstance(image, dict):
            raise ValueError(f"Image entry at index {index} must be an object.")

        required = {"id", "path", "order"}

        missing = required - image.keys()

        if missing:
            raise ValueError(
                f"Image entry at index {index} is missing fields: {', '.join(sorted(missing))}"
            )

        if type(image["id"]) is not int:
            raise ValueError(f"Image id at index {index} must be an integer.")

        if type(image["order"]) is not int or image["order"] <= 0:
            raise ValueError(
                f"Image order at index {index} must be a positive integer."
            )

        if not isinstance(image["path"], str) or not image["path"].strip():
            raise ValueError(
                f"Image path at index {index} must be a non-empty string."
            )

        ids.append(image["id"])
        orders.append(image["order"])

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate image id detected.")

    if len(orders) != len(set(orders)):
        raise ValueError("Duplicate image order detected.")


def load_input_json(json_file: Path) -> list[ImageEntry]:

    json_file = Path(json_file)

    if not json_file.exists():
        raise FileNotFoundError(f"JSON file does not exist: {json_file}")

    if not json_file.is_file():
        raise ValueError(f"JSON path is not a file: {json_file}")

    try:
        with json_file.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in {json_file} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object.")

    unsupported_config_keys = {"output", "orientation", "paperSize"} & data.keys()

    if unsupported_config_keys:
        keys = ", ".join(sorted(unsupported_config_keys))

        raise ValueError(
            f"JSON PDF settings are not supported ({keys}). "
            "Use command-line options for PDF settings."
        )

    images = data.get("images")

    if not isinstance(images, list):
        raise ValueError("JSON must contain an 'images' list.")

    if not images:
        raise ValueError("JSON 'images' list cannot be empty.")

    validate_image_entries(images)

    sorted_images = sorted(images, key=lambda item: item["order"])

    image_entries: list[ImageEntry] = []

    for image in sorted_images:
        path = Path(image["path"])

        if not path.is_absolute():
            path = json_file.parent / path

        path = path.resolve()

        if not path.is_file():
            raise FileNotFoundError(f"Image file does not exist: {path}")

        image_entries.append(
            ImageEntry(
                id=image["id"],
                path=path,
                order=image["order"],
            )
        )

    return image_entries
