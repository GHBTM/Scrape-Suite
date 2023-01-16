######### Scrape Step 2 #########
### Inputs ###
# url -- full, prefixed and suffixed domain of current scrape
# input_method -- use 'sitemap' when crawling to product pages to search for img src, use 'media_urls' if img srcs already exist
# web_method -- use requests or selenium when searching sitemap
# regex_pattern -- img src regex pattern, preferable full suffix
# download_method -- wget is usually fastest, least stressful, requests with headers in cookies is failsafe.
# cdpath = chromedriver location
### Outputs ###
#   i) media_urls.txt includes all img srcs
#  ii) img file downloads for all imgs in media_urls.txt


from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from tqdm import tqdm
import unidecode
import requests
import backoff
import time
import json
import wget
import html
import re
import os

def main(url, input_method, web_method, regex_pattern, download_method):
    if input_method == 'sitemap':
        sitemap = read_sitemap(url)
        media_urls = sitemap_media(url,sitemap, web_method, regex_pattern)
    if input_method == 'media_urls':
        media_urls = read_media_urls(url)
    # modify set where necessary to access highest resolution images
    # cleaned_media = sorted(list(media_urls))
    #newDict = {i.replace(""):media_urls[i] for i in media_urls}

    write_media_output(url, media_urls, download_method)
    return

# loads sitemap.txt, a newline delimited text file of product pages, returns list of product pages
def read_sitemap(url):
    home_dir = os.getcwd()
    path = home_dir + "/IO/" +str(get_domain(url).replace('www.',''))
    os.chdir(path)
    with open('sitemap.json', 'rt') as f:
        sitemap  = json.load(f)
    f.close()
    os.chdir(home_dir)
    return sitemap
# iterates over product pages list, does regex search on page for media, returns list of all img media
def sitemap_media(url,sitemap, web_method, regex_pattern, loop=True):
    media = {}
    headers = get_headers()
    cookies = get_cookies()
    for page in tqdm(sitemap.keys(), position=0, leave=True):
        if web_method == 'requests':
            _html = html.unescape(run_requests(page, cookies, headers))
        if web_method == 'selenium':
            _html = html.unescape(run_selenium(page, cookies))
        with open("./__scrape_html__/last_pull.html", 'w') as f:
            f.write(_html)

        #try:
            #src = selectImg(re.compile(regex_pattern).findall(_html))#+'?sw=2400&sh=3000&q=100'
            #print(src)
            #media[src] = sitemap[page]
        #except IndexError:
            #pass
        #_html = _html.split('<ul class="product-options_list">')[1].split('<div class="size-info">')[0]
        #except Exception as e:
            #pass
        if loop:
            allImgs = list(set(re.compile(regex_pattern).findall(_html)))
            allImgs = [i for i in allImgs]
            print(len(allImgs))
            for i in range(len(allImgs)):
                if i != 0:
                    media[url + allImgs[i]] = sitemap[page] + "." + str(i+2)
                else:
                    media[url + allImgs[i]] = sitemap[page]
        else:
            try:
                regex_pattern = r'<div class="Product_top[\S\s]*?src="([\S]*\.[jpegn]{3,4})\?'
                src = selectImg(re.compile(regex_pattern).findall(_html))
                src = re.sub(r'_[0-9]{3,4}x[_0-9a-z]*\.',"_4000x.", src)
                print(src)
                media[src] = sitemap[page]
            except IndexError:
                pass
    if loop:
        loop = False
        media =  sitemap_media(url, {**sitemap, **media}, web_method, regex_pattern, loop)
        return media
        #return {**sitemap, **media}
    return media

def selectImg(list):
    pngs = [i for i in list if '.png' in i]
    if len(pngs) != 0:
        return pngs[0]
    else:
        return list[0]

@backoff.on_exception(backoff.expo, requests.exceptions.RequestException)
def run_requests(url, cookies, headers):
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(**cookie)
    return unidecode.unidecode(requests.get(url, headers=headers).text)

def get_cookies(json_file="./__scrape_config__/cookies_config.json"):
    with open(json_file) as f:
        data =json.load(f)
    return data

def get_headers(json_file="./__scrape_config__/headers_config.json"):
    with open(json_file) as f:
        data =json.load(f)
    return data

@backoff.on_exception(backoff.expo, requests.exceptions.RequestException)
def run_selenium(url, cookies):
    WINDOW_SIZE = "1920,1080"
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--remote-debugging-port=9230")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("user-agent=[Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36]")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=%s" % WINDOW_SIZE)
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options,service=Service(ChromeDriverManager().install()))
    driver.get(url)
    for cookie in cookies:
        driver.add_cookie(cookie)
    html = driver.page_source
    driver.quit()
    return unidecode.unidecode(html)

# writes to /media/ subdirectory, which should be renamed to match site catalogue
def write_media_output(url, media_urls, download_method):
    home_dir = initialize_media_directory(url)
    write_media(url, media_urls, download_method)
    os.chdir(home_dir)
    return

def initialize_media_directory(url):
    path = os.getcwd()
    home_dir = path
    subdir=str(home_dir)+"/IO/"+str(get_domain(url).replace('www.',''))
    if not os.path.exists(subdir):
        os.mkdir(subdir)
    subdir = subdir + "/media/"
    if not os.path.exists(subdir):
        os.mkdir(subdir)
    os.chdir(subdir)
    return home_dir

def get_domain(url):
    domain = url.split("//")[-1].split("/")[0].split('?')[0]
    return domain

# saves media_urls.txt and img files to /media/ subdirectory.  wget is quick and does not need headers or cookies, may fail.
def write_media(url, media_urls, download_method):

    print("found "+str(len(media_urls))+" to write.")
    with open("media_urls.json", 'wt') as f:
        json.dump(media_urls, f, indent = 4)

    cookies = get_cookies(json_file="../../../__scrape_config__/cookies_config.json")
    headers = get_headers(json_file="../../../__scrape_config__/headers_config.json")
    allImgs = [media_urls[i] for i in media_urls.keys()]
    writtenImgs = cleanListdr(intitialize_inputs(''), '')
    unwrittenImgs = list(set(allImgs).difference(set(writtenImgs)))

    newDict = {}
    ###Preserve###
    unwritten_Dict = {}
    for key in media_urls.keys():
        if media_urls[key] in unwrittenImgs:
            unwritten_Dict[key] = media_urls[key]
            #unwritten_Dict[re.sub(r'_ALT[0-9]{1}',"_ALT2", key)] = media_urls[key]
            #newDict[re.sub(r'_ALT[0-9]{1}',"_ALT2", key)] = media_urls[key]
        #else:
            #newDict[key] = media_urls[key]

    for img in tqdm(unwritten_Dict.keys(), position=0, leave=True):
        media_name = unwritten_Dict[img] +'.' + img.split('?')[0].split('.')[-1]
        if download_method == 'requests':
            s = requests.Session()
            for cookie in cookies:
                s.cookies.set(**cookie)
            try:
                #r = s.get(media_urls[img][0], headers=headers)
                r = s.get(img, headers=headers)
                print(img)
                print('Status_Code: '+str(r.status_code))
                with open(media_name,'wb') as f:
                    f.write(r.content)
                print("wrote media: "+str(media_name))
            except:
                print("passed media: "+str(media_name))
                pass
        if download_method == 'wget':
            try:
                wget.download(img, media_name)
                print("wrote media: "+str(media_name))
            except:
                print("passed media: "+str(media_name))
                pass

    #print("found "+str(len(newDict))+" to write.")
    #with open("media_urls.json", 'wt') as f:
        #json.dump(media_urls, f, indent = 4)

    path = os.getcwd()
    print("wrote media in path: "+str(path))
    return

def read_media_urls(url):
    home_dir = initialize_media_directory(url)
    print(str(os.getcwd()))
    with open('media_urls.json', 'rt') as f:
        data = json.load(f)
    media_urls = data
    f.close()
    print("length media_urls: "+str(len(media_urls)))
    os.chdir(home_dir)
    return media_urls

def cleanListdr(dr, path ,filetypes=['.png','.jpeg','.jpg','.webp']):
    clean_dr = []
    for item in dr:
        if (item[0]!='.') and (item[0:2]!='__') and (item[-2:]!='__'):
            name = re.sub(r'\.[jpegnwbp]{3,4}','', item)
            if '.' + item[-5:].split('.')[-1] in filetypes:

                clean_dr.append(name)
            if os.path.isdir(path+'/'+item):
                clean_dr.append(item)
    return sorted(list(set(clean_dr)))

def intitialize_inputs(inputFolder):
    path = os.getcwd()
    IO = path + "/" +str(inputFolder)
    os.chdir(IO)
    imgList = os.listdir()
    os.chdir(path)
    return imgList

def sessionArguments(regex_pattern):
    regex_config = {}
    #with open('./__scrape_config__/regex_config.json', 'r') as f:
        #regex_config = json.load(f)
    #if section_regex != name_regex != img_regex != None:
    regex_config[get_domain(url)] = {
        'img_regex_2': regex_config
    }
    with open('./__scrape_config__/regex_config.json', "wt") as f:
        json.dump(regex_config, f, indent = 4)
    f.close()
    return regex_config

if __name__ == '__main__':
    url = ''
    input_method = ['sitemap', 'media_urls'][0]
    web_method = ['requests', 'selenium'][0]
    regex_pattern = r''
    download_method = ['requests', 'wget'][0]
    ######sessionArguments(regex_pattern)######
    main(url, input_method, web_method, regex_pattern, download_method)
