"""Get a concordance of words in the text documents."""

import re
import os
import glob
import argparse
import textwrap
import nltk
from nltk.corpus import stopwords
# from nltk.tokenize import RegexpTokenizer
# from nltk.stem.snowball import SnowballStemmer
from nltk.stem.snowball import PorterStemmer

STOP_WORDS = stopwords.words('english')
# STEMMER = SnowballStemmer('english')
STEMMER = PorterStemmer()


def preprocess_file(path):
    """Extract features from the document."""

    text = open(path).read().lower()
    tokens = nltk.word_tokenize(text)
    words = [STEMMER.stem(t) for t in tokens if t not in STOP_WORDS]
    words = [w for w in words
             if len(w) > 2 and re.match(r'[a-z]', w, re.IGNORECASE)]
    return words


def build_model(args):
    """Build the model with the training documents."""

    pattern = os.path.join(args.input_dir, '*.txt')
    paths = glob.glob(pattern)
    for path in paths:
        words = preprocess_file(path)
        all_words = nltk.FreqDist(words)
        print(all_words)
        print(len(all_words))
        break


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


if __name__ == '__main__':

    ARGS = parse_command_line()
    build_model(ARGS)
