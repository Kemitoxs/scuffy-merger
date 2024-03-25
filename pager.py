import argparse
import tempfile

import installer
import offset_generator
import os
import uuid


installer.install_fitz()
from pypdf import PdfWriter, PdfReader, PageObject
import fitz


def parse_args():
    parser = argparse.ArgumentParser(description='Combine .adoc files into a PDF with custom page offset.')
    parser.add_argument('files', nargs='+', help='Paths to .adoc files')
    parser.add_argument('--offset', '-O', type=int, default=1, help='Total page offset')
    parser.add_argument("--output", "-o", help="Path to the output file")
    parser.add_argument("-c", "--count", action="store_true", default=False, help="Count the number of pages")
    parser.add_argument("--always-on", choices=['odd', 'even'],
                        help="Ensure separation starts on either an odd or even page.")

    args = parser.parse_args()
    return args


def get_pages(file_path):
    doc = fitz.open(file_path)
    page_count = len(doc)
    doc.close()
    return page_count


def generate_every_pdf(temp_dir, files, always_on=None):
    """Generates every PDF and returns how long they are"""
    pdf_info = {}

    for adoc_file in files:
        # Generate a unique filename for the PDF
        pdf_filename = str(uuid.uuid4()) + ".pdf"
        pdf_path = os.path.join(temp_dir, pdf_filename)

        input_path = os.path.join(temp_dir, adoc_file)
        offset_generator.generate_asciidoctor_file(input_path, pdf_path)

        # Count the pages of the generated PDF
        page_count = get_pages(pdf_path)

        # Store the info in the dictionary
        pdf_info[adoc_file] = page_count

    format_str = "{:<30} | {:>5}"
    print(format_str.format("Path", "Page Numbers"))
    print("-" * 35)
    for key, value in pdf_info.items():
        print(format_str.format(key, value))

    return pdf_info


def generate_with_offset(pdf_info, temp_dir, initial_offset, always_on=None):
    """Generates every PDF with the given offset"""
    cumulative_offset = initial_offset
    regenerated_pdf_paths = []

    for adoc_file in pdf_info:
        page_count = pdf_info[adoc_file]

        # Generate the output path for the regenerated PDF
        pdf_path = os.path.join(temp_dir, str(uuid.uuid4()) + ".pdf")

        # Use the offset_generator to regenerate the document with the current cumulative offset
        if always_on:
            is_even = cumulative_offset % 2 == 0
            needs_empty_page = (always_on == "odd" and is_even) or (always_on == "even" and not is_even)
            if needs_empty_page:
                cumulative_offset += 1

        offset_generator.generate_document(adoc_file, cumulative_offset, pdf_path)
        print(f"Regenerated {adoc_file} with offset {cumulative_offset} to {pdf_path}")

        # Update the cumulative offset with the page count of the current document
        cumulative_offset += page_count

        # Store the path to the regenerated PDF
        regenerated_pdf_paths.append(pdf_path)

    return regenerated_pdf_paths


def combine_pdfs(files, output_path, offset, always_on=None):
    """Combines all the given PDFs into one by appending them"""
    merger = PdfWriter()

    for file in files:
        if not always_on:
            merger.append(file)
            continue

        current_num_pages = len(merger.pages) + offset
        is_even = current_num_pages % 2 == 0

        # Determine if an empty page needs to be added
        needs_empty_page = (always_on == "odd" and is_even) or (always_on == "even" and not is_even)

        if needs_empty_page:
            # Create an empty page and add it
            empty_page = PageObject.create_blank_page(width=595, height=842)
            merger.add_page(empty_page)

        # Append the current file
        merger.append(file)

    merger.write(output_path)
    merger.close()

    print(f"Combined PDF saved to {output_path}")


def main():
    args = parse_args()

    temp_dir = offset_generator.copy_data()
    pdf_info = generate_every_pdf(temp_dir, args.files)
    if args.count:
        return

    files = generate_with_offset(pdf_info, temp_dir, args.offset, args.always_on)
    combine_pdfs(files, args.output, args.offset, args.always_on)

    print(f"---- Combined all PDFs with offset {args.offset} and saved to {args.output} ----")


if __name__ == '__main__':
    main()
