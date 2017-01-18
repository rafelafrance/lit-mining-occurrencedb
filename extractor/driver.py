"""Drive the Tor browser to get search results."""

import sys
import argparse
from tbselenium.tbdriver import TorBrowserDriver
# from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = 'https://scholar.google.com'
TIMEOUT = 20


def open_browser(args, url):
    """Open the browser to the given web page."""
    driver = TorBrowserDriver(args['tbb_path'])
    driver.get(url)

    wait_for_page_load(driver)

    # Unclick the "include patents" checkbox
    # Unclick the "include citations" checkbox
    # Put 2010 into the custom range from box

    return driver


def wait_for_page_load(driver, title='Google Scholar'):
    """Wait for a page to load by waiting for the title change."""
    try:
        # Wait for the page to refresh, the last thing that seems to be updated is the title
        WebDriverWait(driver, TIMEOUT).until(EC.title_contains(title))
    except TimeoutException:
        print('Query term: {} -- Did not load in {}sec.'.format(title, TIMEOUT))
        sys.exit()


def query_google_scholar(driver, term):
    """Query Google Scholar with the given search term."""
    driver.get(URL)
    search = driver.find_element_by_name('q')
    search.send_keys(term)
    search.submit()
    wait_for_page_load(driver, term)


def search_terms():
    """Search for the terms and get the data."""
    with open('terms.txt') as term_file:
        terms = [line.strip() for line in term_file]
    print(terms)


def parse_command_line():
    """Get user input."""
    parser = argparse.ArgumentParser(description='''Use Selenium Drive the Tor browser.''')
    parser.add_argument('tbb_path', help='Path to the Tor Bowser Bundle.')
    return parser.parse_args()


if __name__ == "__main__":
    ARGS = parse_command_line()
    search_terms()
