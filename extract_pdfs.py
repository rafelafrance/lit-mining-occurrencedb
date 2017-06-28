"""Extract the PDFs, convert the PDF files into text, and then
place them into the given output directory.
"""

import os
import zipfile
import fnmatch
import tempfile
import argparse
import textwrap
import subprocess


def get_pdf_paths(pdf_dir):
    """Walk the dir to get all of the PDFs."""

    pdfs = []
    for root, _, files in os.walk(pdf_dir):
        for base_name in files:
            if fnmatch.fnmatch(base_name, '*.pdf'):
                file_name = os.path.join(root, base_name)
                pdfs.append(file_name)

    return pdfs


def extract_zip(args, temp_dir):
    """Extract the zip file into a temporary directory."""

    with zipfile.ZipFile(args.zip_file) as z_file:
        z_file.extractall(path=temp_dir)


def pdf_to_text(args, pdf_path, tie_breaker):
    """Extract the text from the PDF ad write it to a file."""

    txt_name = os.path.basename(pdf_path) + '_{:04d}.txt'.format(tie_breaker)
    txt_path = os.path.join(args.output_dir, txt_name)
    quiet = '-q' if args.quiet else ''
    cmd = "pdftotext {} '{}' '{}'".format(quiet, pdf_path, txt_path)
    try:
        subprocess.check_call(cmd, shell=True)
    except:
        pass


def parse_command_line():
    """Process command-line arguments."""

    description = """Extract the PDF files and convert them into text. They
    will be placed into the given output directory. This utility depends on
    the external program "xpdf" specifically "pdftotext".
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(description))

    cwd = os.getcwd()
    parser.add_argument('-o', '--output-dir', default=cwd,
                        help=('Where to store the extracted documents. '
                              'Defaults to the current '
                              'directory "{}".'.format(cwd)))

    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Don't print any messages or errors.")

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-i', '--input-dir',
                       help='The PDF files are in this directory.')

    group.add_argument('-z', '--zip-file',
                       help='The PDF files are in this zip file.')

    return parser.parse_args()


if __name__ == '__main__':

    ARGS = parse_command_line()

    with tempfile.TemporaryDirectory() as TEMP_DIR:

        if ARGS.zip_file:
            extract_zip(ARGS, TEMP_DIR)
            PDF_DIR = TEMP_DIR
        else:
            PDF_DIR = ARGS.input_dir

        os.makedirs(ARGS.output_dir, exist_ok=True)

        PDF_PATHS = get_pdf_paths(PDF_DIR)

        for i, PDF_PATH in enumerate(PDF_PATHS, 1):
            if not ARGS.quiet:
                print('Extracting:', PDF_PATH)
            pdf_to_text(ARGS, PDF_PATH, i)

    print('Extracted: {} PDFs'.format(len(PDF_PATHS)))
