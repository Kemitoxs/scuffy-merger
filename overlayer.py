"""Overlay two PDFs"""
import argparse
import fitz
from log_helper import *


def parse_arguments():
    parser = argparse.ArgumentParser(description='Overlay one PDF on top of another at a specific page index.')
    parser.add_argument('--base', '-b', required=True, help='Path to the base PDF file.')
    parser.add_argument('--upper', '-u', required=True, help='Path to the PDF file that will be overlayed on top of the base PDF.')
    parser.add_argument('--output', '-o', required=True, help='Path for the resulting output PDF file.')
    parser.add_argument('--index', '-i', type=int, required=True, help='Index of the page in the base PDF where the overlayed PDF is put on top of.')

    return parser.parse_args()


def overlay_pdfs(base_pdf_path, overlay_pdf_path, output_pdf_path, index):
    if index < 0:
        log.critical("Index must be greater than or equal to 0")
        exit()

    base_pdf = fitz.open(base_pdf_path)
    overlay_pdf = fitz.open(overlay_pdf_path)
    start_index = index
    end_index = index + len(overlay_pdf)

    if end_index > len(base_pdf):
        log.critical("The base PDF stops before the upper PDF... Make sure to enter a correct index")
        exit()

    log.info(f"Overlaying in base from {start_index} to {end_index}")

    for page_num in range(start_index, end_index):
        base_page = base_pdf[page_num]
        overlay_index = page_num - index
        log.debug(f"Overlaying base page {page_num} with upper page {overlay_index}")

        overlay_page = overlay_pdf[overlay_index]
        try:
            base_page.show_pdf_page(base_page.rect, overlay_pdf, overlay_page.number)  # Overlay page
        except ValueError:
            log.debug(f"Skipping empty upper page {overlay_index}")

    base_pdf.save(output_pdf_path)

    log.info(f"---- Saved output to {output_pdf_path} ----")


def main():
    args = parse_arguments()
    overlay_pdfs(args.base, args.upper, args.output, args.index)


if __name__ == "__main__":
    configure_logger()
    main()
