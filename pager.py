import argparse
import tempfile

import installer
import offset_generator
import os
import uuid

installer.install_fitz()
import fitz


def parse_args():
    parser = argparse.ArgumentParser(description='Combine .adoc files into a PDF with custom page offset.')
    parser.add_argument('files', nargs='+', help='Paths to .adoc files')
    parser.add_argument('--offset', '-O', type=int, default=1, help='Total page offset')
    parser.add_argument("--output", "-o", help="Path to the output file")

    args = parser.parse_args()
    return args


def get_pages(file_path):
    doc = fitz.open(file_path)
    page_count = len(doc)
    doc.close()
    return page_count


def generate_every_pdf(temp_dir, files):
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

    return pdf_info


def generate_with_offset(pdf_info, temp_dir, initial_offset):
    """Generates every PDF with the given offset"""
    cumulative_offset = initial_offset
    regenerated_pdf_paths = []

    for adoc_file in pdf_info:
        page_count = pdf_info[adoc_file]

        # Generate the output path for the regenerated PDF
        pdf_path = os.path.join(temp_dir, str(uuid.uuid4()) + ".pdf")

        # Use the offset_generator to regenerate the document with the current cumulative offset
        offset_generator.generate_document(adoc_file, cumulative_offset, pdf_path)
        print(f"Regenerated {adoc_file} with offset {cumulative_offset} to {pdf_path}")

        # Update the cumulative offset with the page count of the current document
        cumulative_offset += page_count

        # Store the path to the regenerated PDF
        regenerated_pdf_paths.append(pdf_path)

    return regenerated_pdf_paths


def combine_pdfs(files, output_path):
    """Combines all the given PDFs into one by appending them"""
    merged_doc = fitz.open()

    for pdf_path in files:
        # Open the current PDF
        current_doc = fitz.open(pdf_path)

        # Iterate through each page of the current PDF and append it to the merged document
        for page_num in range(len(current_doc)):
            merged_doc.insert_pdf(current_doc, from_page=page_num, to_page=page_num)

        # Close the current document now that its pages have been appended
        current_doc.close()

    # Save the merged document to the specified output path
    merged_doc.save(output_path)
    merged_doc.close()

    print(f"Combined PDF saved to {output_path}")


def main():
    args = parse_args()

    temp_dir = offset_generator.copy_data()
    pdf_info = generate_every_pdf(temp_dir, args.files)
    files = generate_with_offset(pdf_info, temp_dir, args.offset)
    combine_pdfs(files, args.output)

    print(f"---- Combined all PDFs with offset {args.offset} and saved to {args.output} ----")


if __name__ == '__main__':
    main()
