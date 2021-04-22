"""A simple utility to convert csv files to bibtex."""

import re
import os
import csv
import sys
import argparse
import textwrap
import numpy as np
from nltk.corpus import stopwords
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


STOP_WORDS = stopwords.words('english')
MAX_ENTRIES = 9999999999

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
        entry['pages'] = re.sub(u'[\u2013\u2014]', '--', entry['pages'])

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
        if re.match(r'(.*)?key$', old_key, re.IGNORECASE):
            old_key = 'key'

        new_key = old_key.replace('.', ' ').strip()
        new_row[new_key] = value

    return new_row


def get_filter_rows(args):
    """Set up a dict with all of the rows that will be filtered out."""

    filter_rows = {}

    if not args.filter_csv:
        return filter_rows

    with open(args.filter_csv) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            row = fix_columns_headers(row)
            key = entry_key(row)
            filter_rows[key] = 1

    return filter_rows


def parse_csv_file(args):
    """Parse a CSV file into bibtex format."""

    entries = []

    filter_rows = get_filter_rows(args)

    with open(args.csv_file) as csv_file:
        reader = csv.DictReader(csv_file)

        for i, row in enumerate(reader, 1):

            if i < args.starting_row:
                continue

            row = fix_columns_headers(row)

            key = entry_key(row)
            if filter_rows.get(key):
                continue

            if row['Item Type'] not in TYPES:
                print('ItemType not found: "{}"'.format(row['Item Type']))
                sys.exit()

            row_type = TYPES[row['Item Type']]

            entry = add_entry(row, row_type['type'], row_type['remap'])

            entries.append(entry)

    if args.randomize:
        entries = np.random.permutation(entries)  # pylint: disable=no-member

    for i, beg in enumerate(range(0, len(entries), args.max_entries), 1):
        file_name = args.bibtex_file
        if args.max_entries != MAX_ENTRIES:
            root, ext = os.path.splitext(file_name)
            file_name = '{}{}{}'.format(root, i, ext)

        print(i, len(entries[beg:beg + args.max_entries]))

        bibtex_db = BibDatabase()
        bibtex_db.entries = entries[beg:beg + args.max_entries]
        writer = BibTexWriter()
        writer.order_entries_by = None
        with open(file_name, 'w') as bibtex_file:
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

    group.add_argument('-f', '--filter-csv', metavar='FILTER',
                       help='Filter CSV rows by rows in this file.')

    group.add_argument('-m', '--max-entries', default=MAX_ENTRIES, type=int,
                       help='Maximum entries per bibtex output file.')

    group.add_argument('-r', '--randomize', action='store_true',
                       help='Shuffle the bibtext output entries?')

    group.add_argument('-s', '--starting-row', metavar='ROW', default=0,
                       type=int,
                       help='Output Bibtex file.')

    return parser.parse_args()


if __name__ == '__main__':

    ARGS = parse_command_line()
    parse_csv_file(ARGS)
