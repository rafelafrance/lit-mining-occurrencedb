"""Split into training, validation, and test datasets."""

import os
from os.path import join, basename
from glob import glob
from shutil import copy
from random import shuffle, seed


SEED = 23578
TEST_SPLIT = 0.2
VAL_SPLIT = 0.2


def copy_files(paths, cls):
    """Move files into the correct dirctories."""

    shuffle(paths)

    val_split = int(len(paths) * VAL_SPLIT)
    test_split = val_split + int(len(paths) * TEST_SPLIT)

    for i, src in enumerate(paths):
        if i < val_split:
            root = 'val'
        elif i < test_split:
            root = 'test'
        else:
            root = 'train'

        dst = join('data', root, cls, basename(src))
        print(src)
        print(dst)
        print()
        copy(src, dst)


def split_files():
    """Split into training, validation, and test datasets."""

    os.makedirs('data/train/Rel-Yes', exist_ok=True)
    os.makedirs('data/train/Rel-No', exist_ok=True)
    os.makedirs('data/test/Rel-Yes', exist_ok=True)
    os.makedirs('data/test/Rel-No', exist_ok=True)
    os.makedirs('data/val/Rel-Yes', exist_ok=True)
    os.makedirs('data/val/Rel-No', exist_ok=True)

    rel_yes = glob('data/text/*/Rel-Yes/*')
    rel_no = glob('data/text/*/Rel-No/*')

    copy_files(rel_yes, 'Rel-Yes')
    copy_files(rel_no, 'Rel-No')


if __name__ == '__main__':
    seed(SEED)
    split_files()
