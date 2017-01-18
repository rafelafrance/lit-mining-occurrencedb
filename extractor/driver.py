from tbselenium.tbdriver import TorBrowserDriver


with TorBrowserDriver('/home/rlafrance/bin/tor-browser_en-US') as driver:
    driver.get('https://check.torproject.org')
