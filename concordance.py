"""Get a concordance of words in the text documents."""

import re
import os
import glob
import argparse
import textwrap
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.snowball import SnowballStemmer, PorterStemmer

STOP_WORDS = stopwords.words('english')
STEMMER = SnowballStemmer('english')
# STEMMER = PorterStemmer()


def parse_command_line():
    """Process command-line arguments."""

    description = """A utility to get the concordance of text files."""

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(description))

    group = parser.add_argument_group('required arguments')

    group.add_argument('-i', '--input-dir', required=True,
                       help='The text documents are in this directory.')

    return parser.parse_args()


def pre_process_file(path):
    text = open(path).read().lower()
    tokens = nltk.word_tokenize(text)
    words = [STEMMER.stem(t) for t in tokens if t not in STOP_WORDS]
    return words


if __name__ == '__main__':

    args = parse_command_line()

    pattern = os.path.join(args.input_dir, '*.txt')
    paths = glob.glob(pattern)
    for path in paths:
        words = pre_process_file(path)
        print(words)
        break
