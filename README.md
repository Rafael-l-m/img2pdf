# Batch Image to PDF Converter

A simple Python command-line tool that converts multiple images into a single PDF file.

## Requirements

- Python 3.10+
- Pillow
- ReportLab
- natsort

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage (Script / CLI)

Convert every supported image in a directory:

```bash
python main.py --input images_dir --output output.pdf
```
```bash
img2pdf --input images_dir --output output.pdf
```

Use a custom page size (millimeters):

```bash
python main.py --input images_dir --paper CUSTOM --width 210 --height 297
```
```bash
img2pdf --input images_dir --paper CUSTOM --width 210 --height 297
```

Use JSON to define image order:

```bash
python main.py --json images.json
```
```bash
img2pdf --json images.json
```

Example `images.json`:

```json
{
    "images": [
        {"id": 10, "path": "photo2.jpg", "order": 2},
        {"id": 11, "path": "photo1.jpg", "order": 1}
    ]
}
```

Relative image paths in JSON are resolved relative to the JSON file's directory.
The JSON input currently supports the `images` list only. PDF options such as paper,
orientation, output path and margins are supplied through command-line arguments.

## Options

- `--sort`: `natural`, `name`, `mtime`, `size` (directory input only)
- `--paper`: `A3`, `A4`, `A5`, `LETTER`, `LEGAL`, `ORIGINAL`, `CUSTOM`
- `--orientation`: `auto`, `portrait`, `landscape`
- `--fit`: `contain`, `cover`, `stretch`, `original`, `width`
- `--margin`: page margin in millimeters
- `--background`: background color name or hex value
- `--dpi`: DPI used by `ORIGINAL` paper and `original` fit
- `--align`: `center`, `top`, `bottom`, `left`, `right`
- `--width`, `--height`: custom paper dimensions in millimeters; both required with `--paper CUSTOM`
- `--title`, `--author`, `--subject`: PDF metadata
- `-v`, `--verbose`: debug logging

## CLI Options

| Option            | Type    | Default         | Choices / Accepted Values                                 | Description                                                                   |
|---                |---      |---              |---                                                        |---                                                                            |
| `--version`       | `Flag`  | —               | —                                                         | Display program version and exit.                                             |
| `-v`, `--verbose` | `Flag`  | `False`         | —                                                         | Enable verbose logging (DEBUG level).                                         |
| `--input`         | `Path`  | —               | Directory path                                            | Input image directory. Mutually exclusive with `--json`.                      |
| `--json`          | `Path`  | —               | JSON file path                                            | Input JSON configuration file. Mutually exclusive with `--input`.             |
| `--sort`          | `str`   | `natural`       | `natural`, `name`, `mtime`, `size`                        | Image sorting method. Only applies to directory input.                        |
| `--output`        | `Path`  | `output.pdf`    | PDF file path                                             | Output PDF file path.                                                         |
| `--paper`         | `str`   | `A4`            | `A3`, `A4`, `A5`, `LETTER`, `LEGAL`, `ORIGINAL`, `CUSTOM` | PDF page size.                                                                |
| `--orientation`   | `str`   | `auto`          | `auto`, `portrait`, `landscape`                           | Page orientation. `auto` determines orientation independently for each image. |
| `--fit`           | `str`   | `contain`       | `contain`, `cover`, `stretch`, `original`, `width`        | Image fitting mode.                                                           |
| `--margin`        | `float` | `0`             | Non-negative number                                       | Page margin in millimeters.                                                   |
| `--background`    | `str`   | `white`         | Color name or hex value                                   | Page background color. Supports color names and hexadecimal values.           |
| `--dpi`           | `int`   | `300`           | Positive integer                                          | DPI used to calculate physical image dimensions.                              |
| `--align`         | `str`   | `center`        | `center`, `top`, `bottom`, `left`, `right`                | Image alignment within the page.                                              |
| `--width`         | `float` | —               | Positive number                                           | Custom page width in millimeters. Requires `--paper CUSTOM`.                  |
| `--height`        | `float` | —               | Positive number                                           | Custom page height in millimeters. Requires `--paper CUSTOM`.                 |
| `--title`         | `str`   | `Generated PDF` | Any string                                                | PDF document title metadata.                                                  |
| `--author`        | `str`   | `""`            | Any string                                                | PDF document author metadata.                                                 |
| `--subject`       | `str`   | `""`            | Any string                                                | PDF document subject metadata.                                                |

## Fit behavior

- `contain`: scale the entire image to fit inside the available page area.
- `cover`: fill the available page area and crop overflow.
- `stretch`: stretch the image to the available page area; aspect ratio may change.
- `original`: use the image's physical dimensions based on the selected DPI. The image can extend beyond the page.
- `width`: fit the image width to the available page width while preserving aspect ratio. A very tall image can extend beyond the page.

`orientation=auto` chooses portrait or landscape separately for each page based on that image's dimensions. A single PDF can therefore contain pages with different orientations and, for `ORIGINAL`, different page sizes.

## Notes

The output parent directory must already exist. The generated PDF is written to a temporary
file in the same directory and replaces the target only after successful generation.
