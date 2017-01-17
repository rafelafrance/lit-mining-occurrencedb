import re
import time
import random
import subprocess

ENGINE = 'google_scholar'
MAX_RESULTS = 500  # Maximum number of results to scrape from Google Scholar
DELAY_MIN = 20
DELAY_MAX = 40
PAGE_COUNT = 10
TERMS = {  # Hard coding the counts is not ideal
    '“species occurrence” database': 8690,
    '“natural history collection” database': 617,
    'herbarium database': 17400,
    '“biodiversity database”': 1320,
    '“primary biodiversity data”': 508,
    '“digital accessible information”': 542,
    '“digital accessible knowledge"': 54,
}


def build_command(term='', start=0):
    cmd = ('python scholar.py --after=2010 --no-patents --no-citations --csv '
           "--count={} --all='{}' --start={}").format(PAGE_COUNT, term, start)
    return cmd


def scholar():
    for term, count in TERMS.items():
        name = re.sub(r'\W', '_', term)
        file_name = '{}_{}.csv'.format(ENGINE, name)
        file_name = re.sub(r'__', '_', file_name)
        max_results = min(count, MAX_RESULTS)
        with open(file_name, 'wb') as csv_file:
            for start in range(0, max_results, PAGE_COUNT):
                cmd = build_command(term=term, start=start)
                output = subprocess.check_output(cmd, shell=True)
                print(cmd)
                csv_file.write(output)
                delay = random.randint(DELAY_MIN, DELAY_MAX)
                time.sleep(delay)


if __name__ == '__main__':
    scholar()
