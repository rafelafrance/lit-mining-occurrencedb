"""Pull the documents in from the Zotero API and put them into the labeled
directories.
"""

import os
import argparse
import textwrap
from pyzotero import zotero
from dot_dict import DotDict


def get_collections(zot):
    """Get all collections keyed by collection name."""

    return {c['data']['name']: DotDict(c) for c in zot.collections()}


def items_with_tag(zot, key, tag):
    """Get all document records in the collection with the given tag."""

    return [DotDict(d) for d
            in zot.everything(zot.collection_items(key, tag=tag))]
    # in zot.collection_items(key, tag=tag, limit=5)]


def get_item_documents(zot, key):
    """Get document records for the item."""

    return [DotDict(c) for c in zot.children(key)]


def get_pdfs(args):
    """Pull the PDFs from the Zotero cache."""

    path = os.path.join(args.output_dir, args.tag)
    os.makedirs(path, exist_ok=True)

    zot = zotero.Zotero(args.group_id, 'group', args.user_key)

    collections = get_collections(zot)
    collection = collections[args.collection]

    items = items_with_tag(zot, collection.key, args.tag)

    for item in items:
        children = get_item_documents(zot, item.key)

        pdfs = [c for c in children
                if c.data.get('contentType') == 'application/pdf']

        if not children:
            print('\nMISSING DOCUMENTS {}\n'.format(item.key))
        elif not pdfs:
            print('\nNO PDFs {}\n'.format(item.key))
        elif len(pdfs) != 1:
            print('\nTOO MANY PDFs {}\n'.format(item.key))
        else:
            doc = pdfs[0]
            print(doc.data.filename)
            zot.dump(doc.key, '{}.pdf'.format(doc.key), path)


def parse_command_line():
    """Process command-line arguments."""

    description = """Write all documents in a collection with the tag to the
    given directory.
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(description))

    parser.add_argument('-g', '--group-id', metavar='GROUP-ID',
                        help='The ID of the Zotero group you want to access.')

    # parser.add_argument('-u', '--user-id', metavar='USER-ID',
    #                     help='Your Zotero user ID.')

    parser.add_argument('-k', '--user-key', help='Your Zotero user key.')

    parser.add_argument('-c', '--collection',
                        help='The name of the collection to extract.')

    parser.add_argument('-t', '--tag', help='Get files with this tag.')

    parser.add_argument('-o', '--output-dir', metavar='DIR',
                        help='Write files into this directory.')

    return parser.parse_args()


if __name__ == '__main__':

    ARGS = parse_command_line()
    get_pdfs(ARGS)
