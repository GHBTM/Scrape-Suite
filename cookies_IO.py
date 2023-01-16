# Script manages cookies through a JSON file that can be used with requests get calls.
# Cookies can be obtained with Cookie Editor Chrome plug-in export function, and pasted to JSON, or by getting cookies for a site with Selenium.
# Cookies format gets cleaned by convert_keys_to_requests_readable function, and either source must be cleaned.
# Cookies are written to a json file that is used with requests in either scrape scripts.
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import requests
import json
import time
import os

def main(url, cdpath):
    #  Run either read_cookies_json or get_cookies_with_selenium.  The former will take cookies manually exported by a webrowser plugin (i.e. Cookie Editor), while the latter will generate cookies after loading a page with selenium.
    cookies = read_cookies_json()
    #cookies = get_cookies_with_selenium(url, cdpath)

    #  cookies dict must be passed to convert_keys_to_requests_readable in order to make the output compatible with the requests module.
    #cookies = convert_keys_to_requests_readable(cookies)

    #  Finally, write_cookies_json will preserve the cookies in a json output for calls using requests libraray.
    write_cookies_json(cookies, text_name='cookies_config')
    print(cookies)
    return

# Set chromedriver path (cdpath) & url variables in if __name__ == '__main__':
# --headless options argument can pull without visibly loading browser, but fails on some domains.
def get_cookies_with_selenium(url, cdpath):
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=options,service=Service(ChromeDriverManager().install()))
    driver.get(url)
    time.sleep(3)
    cookies = driver.get_cookies()
    driver.close()
    return cookies

#  Variable cookies includes a list of dictionaries.  This function iterates through to produce dictionaries compatible with the requests library.
def convert_keys_to_requests_readable(cookies):
    unexpected = ['expirationDate','sameSite','storeId','hostOnly', 'session']
    cleaned_cookies = []
    #How to handle with 1 cookie... always listed?
    #if len(cookies) > 1:
    for cookie in cookies:
        new_cookie = {}
        for key in cookie.keys():
            if key == 'expiry':
                new_cookie['expires'] = cookie['expiry']
            elif key == 'httpOnly':
                new_cookie['rest'] = {'HttpOnly': cookie['httpOnly']}
            elif key not in unexpected:
                new_cookie[key] = cookie[key]
        cleaned_cookies.append(new_cookie)
    return cleaned_cookies

def write_cookies_json(data, text_name='cookies_config'):
    path = os.getcwd()
    with open('./__scrape_config__/'+text_name + ".json", 'w') as f: #w or wt?
        json.dump(data, f, indent = 4)
    print("Wrote "+str(text_name)+".json to to path: "+str(path))
    return

def read_cookies_json(text_name='cookies_config'):
    path = os.getcwd()
    with open('./__scrape_config__/'+text_name + ".json", 'r') as f: #w or wt?
        data = json.load(f)
    print("Read "+str(text_name)+".json from path: "+str(path))
    return data

if __name__ == '__main__':
    cdpath = '/Users/wyattgormley/Documents/WebDriver/chromedriver'
    url = 'https://www.balmain.com'
    main(url, cdpath)
