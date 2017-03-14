"""A simple utility to convert csv files to bibtex."""

import argparse
import textwrap


def parse_command_line():
    """Process command-line arguments."""

    description = """A utility to convert CSV files to Bibtex format."""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(description))

    group = parser.add_argument_group('required arguments')
    group.add_argument('-c', '--csv-file', required=True, metavar='CSV',
                       help='Input CSV file containing the bibliographic '
                            'entries.')

    group.add_argument('-b', '--bibtex-file', required=True, metavar='BIBTEX',
                       help='Output Bibtex file.')

    return parser.parse_args()


if __name__ == '__main__':

    args = parse_command_line()
    print(args)
