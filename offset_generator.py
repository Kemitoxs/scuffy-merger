"""Generate Asciidoctor documents with a given page numbering offset"""
import logging
import subprocess
import argparse
import tempfile
import os
import shutil
import fitz
import uuid
from log_helper import *

ASCIIDOCTOR_COMMAND_TEMPLATE = "asciidoctor-pdf \"{}\" -o {}"


def log_subprocess_output(string, log_method):
    if not string:
        return

    for line in string.splitlines():
        log_method("\t" + str(line.strip()))


def generate_asciidoctor_file(in_path, out_path):
    """Generate an Asciidoctor document and write the pdf to out_path"""
    command = ASCIIDOCTOR_COMMAND_TEMPLATE.format(in_path, out_path)

    log.debug(f"Generating PDF with command: {command}")
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)

    log_subprocess_output(process.stdout, log.debug)
    log_subprocess_output(process.stderr, log.warn)
    if process.returncode != 0:
        log.critical("Generating AsciiDoctor document failed... "
                     "You might have to adapt the command template in the offset_generator.py file")
        exit()


def insert_page_breaks(file_path, repeats):
    """Insert a given amount of page breaks into an .adoc file"""
    logging.debug(f"Inserting {repeats} page breaks into {file_path}")
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        try:
            index = lines.index('\n')
        except ValueError:
            index = len(lines)

        insert_lines = ['\n'] + ['[%always]\n<<<\n'] * repeats
        lines[index:index] = insert_lines

        file.seek(0)
        file.writelines(lines)
        file.truncate()


def remove_empty_pages(file_path, out_path, max_amount):
    """Removes the first max_amount of empty pages in a pdf document"""
    doc = fitz.open(file_path)
    empty_pages_found = 0
    page_num = 0

    while empty_pages_found < max_amount and page_num < len(doc):
        page = doc.load_page(page_num)
        if not page.get_text().strip():
            doc.delete_page(page_num)
            empty_pages_found += 1
        else:
            page_num += 1

    doc.save(out_path)
    doc.close()

    if empty_pages_found != max_amount:
        log.critical(f"Failed to remove all inserted empty pages {empty_pages_found}/{max_amount}... "
                     "Make sure the PDF contains no footer, such that page breaks create completely empty pages")
        exit()
    else:
        log.debug(f"Removed all {empty_pages_found} empty pages from {file_path}")


def parse_args():
    parser = argparse.ArgumentParser(description='Process .adoc files to insert page breaks and generate PDFs.')

    parser.add_argument('--input', '-i', required=True, help='Input .adoc file path')
    parser.add_argument('--offset', '-O', type=int, default=1, help='Number of page breaks to offset the TOC')
    parser.add_argument('--output', '-o', required=True, help='Output PDF file path')

    args = parser.parse_args()
    return args


def copy_data():
    """Copy the entire ./data directory into a temporary directory and return the path."""
    source_dir = './data'
    temp_dir = tempfile.mkdtemp()  # Create a temporary directory
    dest_dir = os.path.join(temp_dir, 'data')
    shutil.copytree(source_dir, dest_dir)  # Copy the entire content of ./data to the temporary directory
    log.debug(f"Copied ./data directory to {dest_dir}")
    return dest_dir


def generate_document(input_path, offset, output_path):
    log.info(f"Generating document for {input_path} with offset {offset} to {output_path}")

    log.debug("(1/4) Preparing temporary workspace")
    temp_dir = copy_data()
    temp_adoc_path = os.path.join(temp_dir, input_path)

    log.debug(f"(2/4) Inserting page breaks")
    insert_page_breaks(temp_adoc_path, offset)

    temp_pdf_path = os.path.join(temp_dir, str(uuid.uuid4()) + ".pdf")
    log.debug(f"(3/4) Generating modified PDF")
    generate_asciidoctor_file(temp_adoc_path, temp_pdf_path)

    log.debug(f"(4/4) Removing {offset} previously inserted empty pages")
    new_temp_pdf_path = os.path.join(temp_dir, str(uuid.uuid4()) + ".pdf")
    remove_empty_pages(temp_pdf_path, new_temp_pdf_path, offset)
    # Step 5: Save the final PDF to the specified output path
    shutil.move(new_temp_pdf_path, output_path)
    log.info(f"Generated document saved to {output_path}")


def main():
    args = parse_args()
    generate_document(args.input, args.offset, args.output)


if __name__ == "__main__":
    configure_logger()
    main()
