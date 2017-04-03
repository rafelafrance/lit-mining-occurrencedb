"""A simple utility to convert csv files to bibtex."""

import re
import os
import csv
import sys
import argparse
import textwrap
from nltk.corpus import stopwords
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


STOP_WORDS = stopwords.words('english')

HEADERS = {
    'Abstract Note': 'abstract',
    'File Attachments': 'file',
    'Manual Tags': 'keywords',
    'Publication Title': 'journal',
    'Publication Year': 'year',
    'Publisher': 'publisher'}

TYPES = {
    'journalArticle': {
        'type': 'article',
        'remap': {}},
    'newspaperArticle': {
        'type': 'article',
        'remap': {}},
    'magazineArticle': {
        'type': 'article',
        'remap': {}},
    'conferencePaper': {
        'type': 'inproceedings',
        'remap': {'Publication Title': 'booktitle'}},
    'book': {
        'type': 'book',
        'remap': {'Publication Title': 'booktitle'}},
    'bookSection': {
        'type': 'incollection',
        'remap': {'Publication Title': 'booktitle'}},
    'report': {
        'type': 'techreport',
        'remap': {'Publisher': 'institution'}},
    'thesis': {
        'type': 'phdthesis',
        'remap': {'Publisher': 'school'}},
    'webpage': {
        'type': 'unpublished',
        'remap': {}}}


def add_entry(row, entry_type, remap):
    """Add an entry to the bibtex"""

    entry = {'ID': entry_key(row), 'ENTRYTYPE': entry_type}

    for header, value in row.items():
        if not value:
            continue
        elif header in ['Item Type', 'key', '']:
            continue
        elif header in remap:
            entry[remap[header]] = value
        elif header in HEADERS:
            entry[HEADERS[header]] = value
        else:
            bibtex = re.sub(r'\W', '', header).lower()
            entry[bibtex] = value

    entry['author'] = entry['author'].replace('; ', ' and ')

    if 'pages' in entry:
        entry['pages'] = re.sub('-', '--', entry['pages'])
        entry['pages'] = re.sub(u'\u2013|\u2014', '--', entry['pages'])

    if 'file' in entry:
        files = entry_file(entry['file'], entry['ID'])
        if files:
            entry['file'] = files
        else:
            del entry['file']

    if 'keywords' in entry:
        entry['keywords'] = entry_keywords(entry['keywords'])

    return entry


def entry_key(row):
    """Build the bibtex key."""

    author = row['Author'].split()[0].lower()
    author = re.sub(r'\W+$', '', author)

    words = [w for w in row['Title'].lower().split() if w not in STOP_WORDS]
    title = words[0].lower() if words else 'anon'

    year = row['Publication Year'].split()
    year = year[0].lower() if year else '????'

    return '_'.join([author, title, year])


def entry_keywords(value):
    """Build the bibtex keywords field."""

    keywords = []

    for word in value.split(';'):
        word = word.strip()
        keywords.append(word)

    return ', '.join(keywords)


def entry_file(value, key):
    """Build the bibtex file field."""

    attachments = []
    attachment_list = value.split(';')

    for attachment in attachment_list:
        attachment = attachment.strip()

        if attachment.startswith(('dn=', 'res=')):
            continue
        if 'documentSummary' in attachment:
            continue

        _, ext = os.path.splitext(attachment.lower())
        attachment = re.sub(r'\\', r'\\\\', attachment)
        attachment = re.sub(r':', r'\\:', attachment)

        if ext == '.pdf':
            attachment = '{}_pdf:{}:application/pdf'.format(key, attachment)
        else:
            attachment = '{}_html:{}:text/html'.format(key, attachment)

        attachments.append(attachment)

    return ';'.join(attachments)


def fix_columns_headers(old_row):
    """R replaces spaces in column headers with dots. We need to handle this.
    """

    new_row = {}

    for old_key, value in old_row.items():
        if re.match(r'(x.*)?key', old_key, re.IGNORECASE):
            old_key = 'key'

        new_key = old_key.replace('.', ' ').strip()
        new_row[new_key] = value

    return new_row


def parse_csv_file(args):
    """Parse a CSV file into bibtex format."""

    bibtex_db = BibDatabase()

    with open(args.csv_file) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            row = fix_columns_headers(row)

            if row['Item Type'] not in TYPES:
                print('ItemType not found: "{}"'.format(row['Item Type']))
                sys.exit()

            row_type = TYPES[row['Item Type']]

            entry = add_entry(row, row_type['type'], row_type['remap'])

            bibtex_db.entries.append(entry)

    writer = BibTexWriter()
    writer.order_entries_by = None
    with open(args.bibtex_file, 'w') as bibtex_file:
        bibtex_file.write(writer.write(bibtex_db))


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

    ARGS = parse_command_line()
    parse_csv_file(ARGS)
