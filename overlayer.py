"""Overlay two PDFs"""
import installer
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Overlay one PDF on top of another at a specific page index.')
    parser.add_argument('--base', '-b', required=True, help='Path to the base PDF file.')
    parser.add_argument('--upper', '-u', required=True, help='Path to the PDF file that will be overlayed on top of the base PDF.')
    parser.add_argument('--output', '-o', required=True, help='Path for the resulting output PDF file.')
    parser.add_argument('--index', '-i', type=int, required=True, help='Index of the page in the base PDF where the overlayed PDF is put on top of.')

    return parser.parse_args()


args = parse_arguments()
print("Parameters received:")
print(f"Base PDF: {args.base}")
print(f"Overlay PDF: {args.upper}")
print(f"Output PDF: {args.output}")
print(f"Page index for overlay: {args.index}")

installer.install_fitz()
import fitz


def overlay_pdfs(base_pdf_path, overlay_pdf_path, output_pdf_path, index):
    if index < 0:
        raise ValueError("Index must be a non-negative integer")

    base_pdf = fitz.open(base_pdf_path)
    overlay_pdf = fitz.open(overlay_pdf_path)
    start_index = index
    end_index = index + len(overlay_pdf)

    if end_index > len(base_pdf):
        raise ValueError("Overlay PDF does not have enough pages to cover the specified range in the base PDF.")

    print(f"Overlaying in base from {start_index} to {end_index}")

    for page_num in range(start_index, end_index):
        base_page = base_pdf[page_num]
        overlay_index = page_num - index
        print(f"Overlaying base page {page_num} with upper page {overlay_index}")

        if overlay_index >= len(overlay_pdf):
            raise RuntimeError("Unexpected end of overlay PDF.")

        overlay_page = overlay_pdf[overlay_index]
        try:
            base_page.show_pdf_page(base_page.rect, overlay_pdf, overlay_page.number)  # Overlay page
        except ValueError as e:
            print(f"Could not overlay empty page, {e}")

    base_pdf.save(output_pdf_path)

    print("Done... Saved output to " + output_pdf_path)


if __name__ == "__main__":
    overlay_pdfs(args.base, args.upper, args.output, args.index)
