"""DEPRECATED: Too simplistic to work."""

import re
import time
import random
import subprocess

ENGINE = 'google_scholar'
MAX_RESULTS = 500  # Maximum number of results to scrape from Google Scholar
DELAY_MIN = 20
DELAY_MAX = 40
PAGE_COUNT = 10
TERMS = [  # Hard coding the counts is not ideal
    {'phrase': 'digital accessible knowledge', 'all': '', 'count': 54},
    {'phrase': 'species occurrence', 'all': 'database', 'count': 8690},
    {'phrase': 'natural history collection', 'all': 'database', 'count': 617},
    {'phrase': '', 'all': 'herbarium database', 'count': 17400},
    {'phrase': 'biodiversity database', 'all': '', 'count': 1320},
    {'phrase': 'primary biodiversity data', 'all': '', 'count': 508},
    {'phrase': 'digital accessible information', 'all': '', 'count': 542},
]


def build_command(term=None, start=0):
    """Build the command line."""
    cmd = ['python scholar.py']
    cmd.append('--after=2010')
    cmd.append('--no-citations')
    cmd.append('--csv')
    cmd.append('--start={}'.format(start))
    if term['phrase']:
        cmd.append('--phrase="{}"'.format(term['phrase']))
    if term['all']:
        cmd.append('--all="{}"'.format(term['phrase']))
    return ' '.join(cmd)


def scholar():
    """Loop thru the terms and hit the pages."""
    for term in TERMS:
        name = term['phrase'] + ' ' + term['all']
        name = '_'.join(name.split())
        file_name = '{}_{}.csv'.format(ENGINE, name)
        file_name = re.sub(r'__', '_', file_name)
        max_results = min(term['count'], MAX_RESULTS)
        with open(file_name, 'wb') as csv_file:
            for start in range(0, max_results, PAGE_COUNT):
                cmd = build_command(term=term, start=start)
                print(cmd)
                output = subprocess.check_output(cmd, shell=True)
                csv_file.write(output)
                delay = random.randint(DELAY_MIN, DELAY_MAX)
                time.sleep(delay)


if __name__ == '__main__':
    scholar()
