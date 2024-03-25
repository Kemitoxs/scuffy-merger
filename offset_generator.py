"""Generate Asciidoctor documents with a given page numbering offset"""
import subprocess
import argparse
import tempfile
import installer
import os
import shutil
import uuid


installer.install_fitz()
import fitz


ASCIIDOCTOR_COMMAND_TEMPLATE = "asciidoctor-pdf \"{}\" -o {}"


def generate_asciidoctor_file(in_path, out_path):
    """Generate an Asciidoctor document and write the pdf to out_path"""
    command = ASCIIDOCTOR_COMMAND_TEMPLATE.format(in_path, out_path)

    try:
        subprocess.run(command, check=True, shell=True)
        print(f"Successfully generated PDF from {in_path} to {out_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate PDF from {in_path}. Error: {e}")
        exit()


def insert_page_breaks(file_path, repeats):
    """Insert a given amount of page breaks into an .adoc file"""
    print(f"Inserting {repeats} page breaks into {file_path}")
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
    page_num = 0  # Start from the first page

    # Loop until we've found and removed the desired amount of empty pages or reached the end of the document
    while empty_pages_found < max_amount and page_num < len(doc):
        page = doc.load_page(page_num)  # Load the current page
        if not page.get_text().strip():  # Check if the page is empty
            doc.delete_page(page_num)  # Delete the current page
            print(f"Deleted empty page at index {page_num}.")
            empty_pages_found += 1
            # Don't increment page_num since we removed the current page, and now the next page takes its place
        else:
            page_num += 1  # Move to the next page only if the current one wasn't deleted

    # Save the document with the empty pages removed
    doc.save(out_path)
    doc.close()
    print(f"Removed {empty_pages_found} empty pages from '{file_path}'.")


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
    print(f"Data directory copied to temporary directory {dest_dir}")
    return dest_dir


def generate_document(input_path, offset, output_path):
    print("(1/4) Preparing temporary workspace.")
    temp_dir = copy_data()
    temp_adoc_path = os.path.join(temp_dir, input_path)

    # Step 2: Insert page breaks into the temporary .adoc file
    print(f"(2/4) Inserting page breaks inserted into the .adoc file based on offset {offset}")
    insert_page_breaks(temp_adoc_path, offset)

    # Generate the PDF from the modified .adoc file
    temp_pdf_path = os.path.join(temp_dir, str(uuid.uuid4()) + ".pdf")
    print(f"(3/4) Generating PDF file from modified .adoc file. PDF Path: {temp_pdf_path}")
    generate_asciidoctor_file(temp_adoc_path, temp_pdf_path)

    # Step 4: Remove the first `x` empty pages from the generated PDF
    print(f"(4/4) Removing {offset} previously inserted empty pages")
    new_temp_pdf_path = os.path.join(temp_dir, str(uuid.uuid4()) + ".pdf")
    remove_empty_pages(temp_pdf_path, new_temp_pdf_path, offset)
    # Step 5: Save the final PDF to the specified output path
    shutil.move(new_temp_pdf_path, output_path)
    print(f"Generated document saved to {output_path}")


def main():
    args = parse_args()
    generate_document(args.input, args.offset, args.output)


if __name__ == "__main__":
    main()
