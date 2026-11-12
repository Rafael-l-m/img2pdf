# Batch Image to PDF Converter

A simple Python command-line tool that converts multiple images into a single PDF file.


## Features

- Convert multiple images into a single PDF.
- Support `JPG`, `JPEG`, `PNG`, `WEBP` and `BMP` formats.
- Natural sorting, filename sorting and regex-based sorting.
- Recursive image search in subdirectories.
- Support multiple paper sizes (`A3`, `A4`, `A5`, `Letter` and `Legal`).
- Custom page dimensions.
- Automatic, portrait and landscape orientations.
- Multiple image fitting modes.
- Configurable margins, background colors and alignment.
- Preserve image orientation using EXIF metadata.


## Usage (Command Line)

Basic usage:

```bash
img2pdf --input images_folder --output output.pdf
```

Display help:

```bash
img2pdf --help
```


## Usage (Script)

- Python 3.9+
- Pillow
- ReportLab

Install the required dependencies:

```bash
pip install pillow reportlab
```

Basic usage:

```bash
python img2pdf.py --input images_folder --output output.pdf
```

Display help:

```bash
python img2pdf.py --help
```

## Command-line Options

| Argument        | Default    | Description                |
|---              |---         |---                         |
| `--input`       | Required   | Input image folder         |
| `--output`      | output.pdf | Output PDF filename        |
| `--paper`       | A4         | Paper size                 |
| `--orientation` | auto       | Page orientation           |
| `--fit`         | cover      | Image fitting mode         |
| `--margin`      | 0          | Page margin (mm)           |
| `--background`  | white      | Page background color      |
| `--dpi`         | 300        | DPI for original page size |
| `--align`       | center     | Image alignment            |
| `--sort`        | natural    | Image sorting method       |
| `--pattern`     | `(\d+)`    | Regex sorting pattern      |
| `--recursive`   | False      | Search subdirectories      |
| `--width`       | None       | Custom page width (mm)     |
| `--height`      | None       | Custom page height (mm)    |


## Examples

### 1. Basic conversion

```bash
img2pdf --input images_folder
```

### 2. Use A3 landscape pages

```bash
img2pdf --input images_folder --paper A3 --orientation landscape --output output.pdf
```

### 3. Use contain fitting with margins

```bash
img2pdf --input images_folder --fit contain --margin 10 --output output.pdf
```

### 4. Recursive image search

```bash
img2pdf --input images_folder --recursive --output output.pdf
```

### 5. Custom page size

```bash
img2pdf --input images_folder --paper Custom --width 210 --height 297 --output output.pdf
```

### 6. Regex-based sorting

```bash
img2pdf --input images_folder --sort regex --pattern "(\d+)" --output output.pdf
```


## License

MIT License.
