"""A simple utility to convert csv files to bibtex."""

import re
import os
import csv
import sys
import argparse
import textwrap
from urllib.parse import urlparse
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

    if 'pages' in entry:
        entry['pages'] = re.sub('-', '--', entry['pages'])
        entry['pages'] = re.sub(u'\u2013|\u2014', '--', entry['pages'])

    skips = list(optionals.values()) + ['File Attachments', 'Manual Tags',
                                        'Author', 'Title', 'Item Type']
    for old_key, value in row.items():
        if value and old_key not in skips:
            new_key = re.sub(r'\W', '', old_key).lower()
            if new_key not in entry and new_key not in ['xufeffkey']:
                entry[new_key] = row[old_key]

    file_field(row, entry)
    keywords(row, entry)


def add_requireds(row, entry_type):
    """Build an entry with the required fields"""
    entry = {
        'ID': key(row),
        'ENTRYTYPE': entry_type,
        'author': row['Author'],
        'title': row['Title']}

    entry['author'] = entry['author'].replace('; ', ' and ')

    return entry


def article(row):
    """Put dict into a bibtex article."""

    entry = add_requireds(row, 'article')

    optionals = {
        'url': 'Url',
        'note': 'Note',
        'date': 'Date',
        'year': 'Publication Year',
        'pages': 'Pages',
        'month': 'Month',
        'volume': 'Volume',
        'abstract': 'Abstract Note',
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
        'date': 'Date',
        'year': 'Publication Year',
        'pages': 'Pages',
        'volume': 'Volume',
        'abstract': 'Abstract Note',
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
        'date': 'Date',
        'year': 'Publication Year',
        'pages': 'Pages',
        'editor': 'Editor',
        'abstract': 'Abstract Note',
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
        'date': 'Date',
        'year': 'Publication Year',
        'pages': 'Pages',
        'editor': 'Editor',
        'abstract': 'Abstract Note',
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
        'date': 'Date',
        'year': 'Publication Year',
        'abstract': 'Abstract Note',
        'institution': 'Publisher'}
    add_optionals(row, optionals, entry)

    return entry


def phdthesis(row):
    """Put dict into a bibtex inproceedings."""

    entry = add_requireds(row, 'phdthesis')

    optionals = {
        'url': 'Url',
        'note': 'Note',
        'date': 'Date',
        'year': 'Publication Year',
        'school': 'Publisher',
        'abstract': 'Abstract Note'}
    add_optionals(row, optionals, entry)

    return entry


def keywords(row, entry):
    """Build the bibtex keywords field."""

    keywords = []

    for word in row['Manual Tags'].split(';'):
        word = word.strip()
        keywords.append(word)

    entry['keywords'] = ', '.join(keywords)


def file_field(row, entry):
    """Build the bibtex file field."""

    # entry['file'] = row['File Attachments']

    if not row['File Attachments']:
        return

    url = urlparse(row['Url'])

    attachments = []
    attachment_list = row['File Attachments'].split(';')
    for i, attachment in enumerate(attachment_list):
        attachment = attachment.strip()

        if attachment.startswith('dn='):
            continue
        elif attachment.startswith('res='):
            if attachment.endswith('.html'):
                attachment += ':text/html'
            continue

        file_name = re.split(r'[/\\]\s*', attachment)[-1]
        _, ext = os.path.splitext(attachment.lower())
        attachment = re.sub(r'\\', r'\\\\', attachment)
        attachment = re.sub(r':', r'\\:', attachment)

        if ext == '.pdf':
            attachment = '{}:{}:application/pdf'.format(file_name, attachment)
        elif ext == '.html':
            attachment = '{}:{}:text/html'.format(file_name, attachment)

        attachments.append(attachment)

    entry['file'] = ';'.join(attachments)


def key(row):
    """Build the bibtex key."""

    author = row['Author'].split()[0].lower()
    author = re.sub(r'\W+$', '', author)

    words = [w for w in row['Title'].lower().split() if w not in STOP_WORDS]
    title = words[0].lower() if words else 'anon'

    year = row['Publication Year'].split()
    year = year[0].lower() if year else '????'

    return '_'.join([author, title, year])


def fix_columns_headers(old_row):
    """R replace spaces in column headers with dots. We need to handle this."""

    new_row = {}

    for old_key, value in old_row.items():
        new_key = old_key.replace('.', ' ').strip()
        new_row[new_key] = old_row[old_key]

    return new_row


def parse_csv_file(args):
    """Parse a CSV file into bibtex format."""

    db = BibDatabase()
    entries = []

    with open(args.csv_file) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            row = fix_columns_headers(row)

            if row['Item Type'] in ['journalArticle', 'newspaperArticle']:
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
                print('ItemType not found: "{}"'.format(row['Item Type']))
                sys.exit()

            db.entries.append(entry)

    writer = BibTexWriter()
    with open(args.bibtex_file, 'w') as bibtex_file:
        bibtex_file.write(writer.write(db))


if __name__ == '__main__':

    args = parse_command_line()
    parse_csv_file(args)
