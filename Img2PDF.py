import argparse, os, re

from PIL import Image, ImageOps
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A3, A5, LETTER, LEGAL
from reportlab.lib.utils import ImageReader


PAPER_SIZES = {
    "A3": A3,
    "A4": A4,
    "A5": A5,
    "LETTER": LETTER,
    "LEGAL": LEGAL,
}


def natural_key(filename):
    return [
        int(x) if x.isdigit() else x.lower()
        for x in re.split(r"(\d+)", filename)
    ]


def get_images(
    folder: str,
    sort: str = "natural",
    pattern: str = r"(\d+)",
    recursive: bool = False
):

    extensions: tuple[str, ...] = (
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp"
    )

    files: list[str] = []

    if recursive:
        for root, _, filenames in os.walk(folder):
            for name in filenames:
                if name.lower().endswith(extensions):
                    files.append(os.path.join(root, name))
    else:
        files = [
            os.path.join(folder, name)
            for name in os.listdir(folder)
            if name.lower().endswith(extensions)
        ]

    if sort == "natural":
        files.sort(key=lambda x: natural_key(os.path.basename(x)))

    elif sort == "name":
        files.sort(key=lambda x: os.path.basename(x).lower())

    elif sort == "regex":
        def key(path: str) -> tuple:
            match = re.search(pattern, os.path.basename(path))

            if not match:
                return 1, 0, os.path.basename(path).lower()

            value: str = match.group(1)

            try:
                parsed_value: int = int(value)

            except ValueError:
                parsed_value: str = value.lower()

            return 0, parsed_value, os.path.basename(path).lower()

        files.sort(key=key)

    return files


def get_page_size(paper, orientation, img_size, dpi=300, custom__size=None):

    if paper.upper() == "ORIGINAL":
        width = img_size[0] * 72 / dpi
        height = img_size[1] * 72 / dpi

    elif paper.upper() == "CUSTOM":
        if not custom__size:
            raise ValueError("Width and height must be specified for the custom option.")

        width = custom__size[0] * 72 / 25.4
        height = custom__size[1] * 72 / 25.4

    else:
        width, height = PAPER_SIZES[paper.upper()]

    if orientation == "auto":
        landscape = img_size[0] > img_size[1]
    else:
        landscape = orientation == "landscape"

    if landscape and height > width:
        width, height = height, width

    elif not landscape and width > height:
        width, height = height, width

    return width, height


def calculate_layout(
    img_width,
    img_height,
    page_width,
    page_height,
    fit,
    margin,
    align
):

    available_width = page_width - 2 * margin
    available_height = page_height - 2 * margin

    if available_width <= 0 or available_height <= 0:
        raise ValueError("Printable area is too small because of the current margin settings")

    if fit == "contain":
        scale = min(
            available_width / img_width,
            available_height / img_height
        )
        width = img_width * scale
        height = img_height * scale

    elif fit == "cover":
        scale = max(
            available_width / img_width,
            available_height / img_height
        )
        width = img_width * scale
        height = img_height * scale

    elif fit == "stretch":
        width = available_width
        height = available_height

    elif fit == "original":
        width = img_width
        height = img_height

    elif fit == "width":
        scale = available_width / img_width
        width = available_width
        height = img_height * scale

    else:
        raise ValueError(f"Unknown layout mode: {fit}")

    if align == "center":
        x = (page_width - width) / 2
        y = (page_height - height) / 2
    elif align == "top":
        x = (page_width - width) / 2
        y = page_height - margin - height
    elif align == "bottom":
        x = (page_width - width) / 2
        y = margin
    elif align == "left":
        x = margin
        y = (page_height - height) / 2
    elif align == "right":
        x = page_width - margin - width
        y = (page_height - height) / 2
    else:
        raise ValueError(f"Unknown alignment mode: {align}")

    return x, y, width, height


def images_to_pdf(
    image_files,
    output_pdf,
    paper="A4",
    orientation="auto",
    fit="cover",
    margin=0,
    align="center",
    background="white",
    dpi=300,
    custom__size=None
):

    if not image_files:
        raise ValueError("No images to process.")

    pdf = canvas.Canvas(output_pdf)

    for image_path in image_files:

        with Image.open(image_path) as source:

            img = ImageOps.exif_transpose(source).convert("RGB")

            page_width, page_height = get_page_size(
                paper,
                orientation,
                img.size,
                dpi,
                custom__size
            )

            pdf.setPageSize((page_width, page_height))

            pdf.setFillColor(background)
            pdf.rect(
                0, 0,
                page_width, page_height,
                fill=1,
                stroke=0
            )

            x, y, width, height = calculate_layout(
                img.width,
                img.height,
                page_width,
                page_height,
                fit,
                margin,
                align
            )

            if fit == "cover":
                pdf.saveState()
                clip = pdf.beginPath()
                clip.rect(
                    margin,
                    margin,
                    page_width - 2 * margin,
                    page_height - 2 * margin
                )
                pdf.clipPath(clip, stroke=0, fill=0)

            pdf.drawImage(
                ImageReader(img),
                x, y,
                width=width,
                height=height
            )

            if fit == "cover":
                pdf.restoreState()

            pdf.showPage()

    pdf.save()

    print(f"Merge completed successfully: {output_pdf}")
    print(f"Total pages: {len(image_files)}")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="img2pdf",
        description="Batch Image to PDF Converter",
        epilog="Example: python img2pdf.py --input ./images --output result.pdf",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0-alpha"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input folder containing images."
    )

    parser.add_argument(
        "--output",
        default="output.pdf",
        help="Output PDF filename."
    )

    parser.add_argument(
        "--paper",
        default="A4",
        choices=["A3", "A4", "A5", "Letter",
                 "Legal", "Original", "Custom"],
        help="PDF page size."
    )

    parser.add_argument(
        "--orientation",
        default="auto",
        choices=["auto", "portrait", "landscape"],
        help="Page orientation."
    )

    parser.add_argument(
        "--fit",
        default="cover",
        choices=["contain", "cover", "stretch",
                 "original", "width"],
        help="Image fitting mode."
    )

    parser.add_argument(
        "--margin",
        type=float,
        default=0,
        help="Page margin in millimeters."
    )

    parser.add_argument(
        "--background",
        default="white",
        help="PDF page background color."
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI used for original image page size."
    )

    parser.add_argument(
        "--align",
        default="center",
        choices=["center", "top", "bottom", "left", "right"],
        help="Image alignment on the page."
    )

    parser.add_argument(
        "--sort",
        default="natural",
        choices=["natural", "name", "regex"],
        help="Image sorting method."
    )

    parser.add_argument(
        "--pattern",
        default=r"(\d+)",
        help="Regex pattern for extracting sorting keys."
    )

    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively search for images in subdirectories."
    )

    parser.add_argument(
        "--width",
        type=float,
        help="Custom page width in millimeters."
    )

    parser.add_argument(
        "--height",
        type=float,
        help="Custom page height in millimeters."
    )

    args = parser.parse_args()

    if args.paper == "Custom":
        if args.width is None or args.height is None:
            parser.error("--width and --height must be specified for the custom option.")

        custom_size = (args.width, args.height)
    else:
        custom_size = None

    if args.dpi <= 0:
        parser.error("--dpi must be positive integer.")

    images = get_images(
        args.input,
        args.sort,
        args.pattern,
        args.recursive
    )

    images_to_pdf(
        images,
        args.output,
        paper=args.paper,
        orientation=args.orientation,
        fit=args.fit,
        margin=args.margin * 72 / 25.4,
        align=args.align,
        background=args.background,
        dpi=args.dpi,
        custom__size=custom_size
    )
