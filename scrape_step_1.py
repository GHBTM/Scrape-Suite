######### Scrape Step 1 #########
### Inputs ###
# url -- domain name
# pages -- webpages to scrape, if multiple for item type
# regex_pattern -- can be any but best if only suffix to domain
# method -- use requests or selenium library
# sleep_time -- selenium sleep between scrolls
# scroll_count -- selenium scroll count
# output -- scrape step 1 output, see below
### Outputs ###
# sitemap.json including all product pages OR ./media/media_urls.json
# In write_directory(), use the latter if you can recover full img srcs from a page's html, use the former when you can only recover indidvidual product pages from a page's html.

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import unidecode
import requests
import backoff
import html
import json
import time
import re
import os

def main(url, pages, method, section_regex, name_regex, img_regex, sleep_time, scroll_count, output):
    sections = []
    cookies = get_cookies()
    headers = get_headers()
    for page in pages:
        if method == 'requests':
            text = run_requests(page, cookies, headers)
        if method == 'selenium':
            text = run_selenium(page, cookies, headers, sleep_time, scroll_count)
        with open("./__scrape_html__/last_pull.html", 'w') as f:
            f.write(text)
        #links = re.compile(regex_pattern).findall(text)
        links = re.split(section_regex, text)
        print(len(links))
        sections = sections + links


    # set() contents may need modification here:
    #prodName = sorted(list(set(re.compile(name_regex).findall(text))))
    #print('prodName: '+str(prodName))
    #print('prodName len: '+str(len(prodName)))
    #print('Found '+str(len(sections))+' product sections')
    sitemap = {}
    prodNamesDict = {}
    for section in sections:
        id = str(sections.index(section))
        prodName = sorted(list(set(re.compile(name_regex).findall(section))))
        prodName = [html.unescape(i).strip().replace("/","|") for i in prodName]
        prodImg = sorted(list(set(re.compile(img_regex).findall(section))))
        #prodImg = deDupe(prodImg)
        if (len(prodName) == 1) & (len(prodImg) != 0):
            prodImg = url + selectImg(prodImg) #+ '&width=60000&height=60000&quality=100'
            #prodImg = re.sub("_{width}x.", "_2048x.", prodImg)

            #prodName = html.unescape(prodName[0]).replace("'","")
            prodName = prodName[0]
            if (prodImg not in sitemap.keys()):
                if (prodName in prodNamesDict.keys()):
                    prodNamesDict[prodName] += 1
                    prodName = prodName+'.'+str(prodNamesDict[prodName])
                else:
                    prodNamesDict[prodName] = 1
            sitemap[prodImg] = prodName
        elif (len(prodImg) != 0) | (len(prodName) != 0):
            print('prodName: '+str(prodName))
            print('prodImg: '+str(prodImg))
        else:
            print('section index '+str(sections.index(section))+' of '+str(len(sections)))

    finishedKeys = []
    for key1 in sitemap.keys():
        if sitemap[key1] not in finishedKeys:
            count = 1
            for key2 in sitemap.keys():
                if key1 != key2:
                    if sitemap[key1] == sitemap[key2]:
                        count = count + 1
                        sitemap[key2] = sitemap[key2] + "." + str(count)
        finishedKeys.append(sitemap[key1])

    write_directory_output(url, sitemap, output)
    return

def selectImg(list):
    pngs = [i for i in list if '.png' in i]
    if len(pngs) != 0:
        return pngs[0]
    else:
        return list[0]

def deDupe(list):
    filetypes = set([i.split('.')[-1] for i in list])
    filenames = set([i.replace('.jpeg','').replace('.jpg','').replace('.png','').replace('.webp','') for i in list])
    deDuplist = []
    for file in filenames:
        if ('png' in filetypes) & (file + '.png' in list):
                deDuplist.append(file + '.png')
        else:
            for type in filetypes:
                if file + '.'+type in list:
                    deDuplist.append(file + '.' +type)
                    break
    return deDuplist

@backoff.on_exception(backoff.expo, requests.exceptions.RequestException)
def run_requests(page, cookies, headers):
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(**cookie)
    return unidecode.unidecode(requests.get(page, headers=headers).text).encode().decode('unicode-escape')

def get_cookies(json_file="./__scrape_config__/cookies_config.json"):
    with open(json_file) as f:
        data =json.load(f)
    return data

def get_headers(json_file="./__scrape_config__/headers_config.json"):
    with open(json_file) as f:
        data =json.load(f)
    return data

# headless option is faster but may fail on select pages
@backoff.on_exception(backoff.expo, requests.exceptions.RequestException)
def run_selenium(url, cookies, headers, sleep_time, scroll_count):
    WINDOW_SIZE = "1920,1080"
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("user-agent=[Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36]")

    options.add_argument("--start-maximized")
    options.add_argument("--window-size=%s" % WINDOW_SIZE)
    #options.add_argument("--headless")
    driver = webdriver.Chrome(options=options,service=Service(ChromeDriverManager().install()))
    driver.get(url)
    for cookie in cookies:
        driver.add_cookie(cookie)

    html = ''
    page = driver.find_element_by_tag_name('body')
    for i in range(scroll_count):
        html = html + driver.page_source
        page.send_keys(Keys.PAGE_DOWN)
        page.send_keys(Keys.PAGE_DOWN)
        time.sleep(sleep_time)
        print(str(len(html)))
    driver.quit()
    return unidecode.unidecode(html)

def write_directory_output(url, sitemap, output):
    print(str(len(sitemap)))
    home_dir = initialize_directory(url)
    write_directory(sitemap, output)
    os.chdir(home_dir)
    return

def initialize_directory(url):
    path = os.getcwd()
    home_dir = path
    IO = path + "/IO/"
    if not os.path.exists(IO):
        os.mkdir(IO)
    os.chdir(IO)
    subdir = IO + "/" + get_domain(url).replace('www.','') + "/"
    if not os.path.exists(subdir):
        os.mkdir(subdir)
    os.chdir(subdir)
    return home_dir

def get_domain(url):
    domain = url.split("//")[-1].split("/")[0].split('?')[0]
    return domain

def write_directory(sitemap, output):
    path = os.getcwd()
    IO_media = path + "/media/"
    if not os.path.exists(IO_media):
        os.mkdir(IO_media)
    #### CONFIG FOR JSON OUTPUT ####
    #with open(output + ".txt", "wt") as f:
        #for url in sitemap:
            #f.write(url+"\n")
    #### CONFIG FOR JSON OUTPUT ####
    with open(output + ".json", "wt") as f:
        json.dump(sitemap, f, indent = 4)
    f.close()
    print("wrote "+output+" to path: "+str(path))
    return

def sessionArguments(url, section_regex, name_regex, img_regex):
    with open('./__scrape_config__/regex_config.json', 'r') as f:
        regex_config = json.load(f)
    #if section_regex != name_regex != img_regex != None:
    regex_config[get_domain(url)] = {
            'section_regex': section_regex,
            'name_regex': name_regex,
            'img_regex_1': img_regex
        }
    with open('./__scrape_config__/regex_config.json', "wt") as f:
        json.dump(regex_config, f, indent = 4)
    f.close()
    return regex_config

if __name__ == '__main__':
    url = ''
    pages = [
                ''
            ]

    method = ['requests', 'selenium'][0]
    section_regex = r''
    name_regex = r''
    img_regex = r''
    sleep_time = 2
    scroll_count = 12
    output = ['sitemap', './media/media_urls'][0]
    sessionArguments(url, section_regex, name_regex, img_regex)
    main(url, pages, method, section_regex, name_regex, img_regex, sleep_time, scroll_count, output)
