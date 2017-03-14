"""A simple utility to convert csv files to bibtex."""

import re
import csv
import sys
import argparse
import textwrap
from nltk.corpus import stopwords
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


STOP_WORDS = stopwords.words('english')


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


def add_optionals(row, optionals, entry):
    """Put optional fields into the entry."""

    for bib, csv in optionals.items():
        if row.get(csv):
            entry[bib] = row[csv]


def add_requireds(row, entry_type):
    """Build an entry with the required fields"""
    entry = {
        'ID': key(row),
        'ENTRYTYPE': entry_type,
        'author': row['Author'],
        'title': row['Title']}
    return entry


def article(row):
    """Put dict into a bibtex article."""

    entry = add_requireds(row, 'article')

    optionals = {
        'url': 'Url',
        'note': 'Note',
        'file': 'File Attachments',
        'year': 'Publication Year',
        'pages': 'Pages',
        'month': 'Month',
        'volume': 'Volume',
        'journal': 'Publication Title',
        'shorttitle': 'Short Title'}
    add_optionals(row, optionals, entry)

    return entry


def inproceedings(row):
    """Put dict into a bibtex inproceedings."""

    entry = add_requireds(row, 'inproceedings')

    optionals = {
        'url': 'Url',
        'note': 'Note',
        'file': 'File Attachments',
        'year': 'Publication Year',
        'pages': 'Pages',
        'volume': 'Volume',
        'publisher': 'Publisher',
        'booktitle': 'Publication Title',
        'shorttitle': 'Short Title'}
    add_optionals(row, optionals, entry)

    return entry


def book(row):
    """Put dict into a bibtex inproceedings."""

    entry = add_requireds(row, 'book')

    optionals = {
        'url': 'Url',
        'note': 'Note',
        'file': 'File Attachments',
        'year': 'Publication Year',
        'pages': 'Pages',
        'publisher': 'Publisher',
        'shorttitle': 'Short Title'}
    add_optionals(row, optionals, entry)

    return entry


def incollection(row):
    """Put dict into a bibtex inproceedings."""

    entry = add_requireds(row, 'incollection')

    optionals = {
        'url': 'Url',
        'note': 'Note',
        'file': 'File Attachments',
        'year': 'Publication Year',
        'pages': 'Pages',
        'publisher': 'Publisher',
        'booktitle': 'Publication Title',
        'shorttitle': 'Short Title'}
    add_optionals(row, optionals, entry)

    return entry


def techreport(row):
    """Put dict into a bibtex inproceedings."""

    entry = add_requireds(row, 'techreport')

    optionals = {
        'url': 'Url',
        'note': 'Note',
        'year': 'Publication Year',
        'file': 'File Attachments',
        'institution': 'Publisher'}
    add_optionals(row, optionals, entry)

    return entry


def phdthesis(row):
    """Put dict into a bibtex inproceedings."""

    entry = add_requireds(row, 'phdthesis')

    optionals = {
        'url': 'Url',
        'note': 'Note',
        'year': 'Publication Year',
        'file': 'File Attachments',
        'school': 'Publisher'}
    add_optionals(row, optionals, entry)

    return entry


def key(row):
    """Build the bibtex key."""

    author = row['Author'].split()[0].lower()
    author = re.sub(r'\W+$', '', author)

    words = [w for w in row['Title'].lower().split() if w not in STOP_WORDS]
    title = words[0].lower() if words else 'anon'

    year = row['Publication Year'].split()
    year = year[0].lower() if year else '????'

    return '_'.join([author, title, year])


def parse_csv_file(args):
    """Parse a CSV file into bibtex format."""

    db = BibDatabase()
    entries = []

    with open(args.csv_file) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            row['Key'] = row['\ufeff"Key"']
            if row['Item Type'] == 'journalArticle':
                entry = article(row)
            elif row['Item Type'] == 'conferencePaper':
                entry = inproceedings(row)
            elif row['Item Type'] == 'book':
                entry = book(row)
            elif row['Item Type'] == 'bookSection':
                entry = incollection(row)
            elif row['Item Type'] == 'report':
                entry = techreport(row)
            elif row['Item Type'] == 'thesis':
                entry = phdthesis(row)
            else:
                print('ItemType not found')
                sys.exit()

            db.entries.append(entry)

    writer = BibTexWriter()
    with open(args.bibtex_file, 'w') as bibtex_file:
        bibtex_file.write(writer.write(db))


if __name__ == '__main__':

    args = parse_command_line()
    parse_csv_file(args)
