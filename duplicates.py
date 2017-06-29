"""Find duplicate files and move them out of the way."""

import os
from os.path import join, basename
from glob import glob
from shutil import move


def file_names(root, cls):
    """Get a files for a particular class."""

    pattern = join('data', 'pdf', root, cls, '*.pdf')
    paths = glob(pattern)
    return [basename(p) for p in paths]


def move_duplicates(root):
    """Main function."""

    rel_yes = set(file_names(root, 'Rel-Yes'))
    rel_no = set(file_names(root, 'Rel-No'))
    duplicates = rel_yes & rel_no

    dup_root = join('data', 'pdf', 'duplicates')
    os.makedirs(dup_root, exist_ok=True)

    for duplicate in duplicates:
        print(duplicate)
        src = join('data', 'pdf', root, 'Rel-Yes', duplicate)
        dst = join(dup_root, duplicate)
        move(src, dst)
        src = join('data', 'pdf', root, 'Rel-No', duplicate)
        os.remove(src)


if __name__ == '__main__':
    move_duplicates('RSet_N1')
    move_duplicates('RSet_N2')
