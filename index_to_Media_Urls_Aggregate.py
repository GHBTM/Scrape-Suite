# Script references index_record.json after index_IO maps for .txt filetypes, finds all media_urls.txt files, and aggregates them into one .txt file, index_media_urls, delimiting image source urls with new lines.

import json
import os

def main():
    tree = read_json()
    build_media_urls_aggregate(tree)
    return

def build_media_urls_aggregate(tree):
    media_urls_aggregate = []

    for i in range(len(tree['items'])):
        source = tree['items'][i]['folder']
        for j in range(len(tree['items'][i]['items'])):
            catalogue = tree['items'][i]['items'][j]['folder']
            for k in range(len(tree['items'][i]['items'][j]['items'])):
                genre = tree['items'][i]['items'][j]['items'][k]['folder']
                for l in range(len(tree['items'][i]['items'][j]['items'][k]['items'])):
                    trait = tree['items'][i]['items'][j]['items'][k]['items'][l]['folder']
                    for m in range(len(tree['items'][i]['items'][j]['items'][k]['items'][l]['items'])):
                        media_urls = tree['items'][i]['items'][j]['items'][k]['items'][l]['items'][m]
                        if media_urls == 'media_urls.txt':
                            local_path = tree['items'][i]['items'][j]['items'][k]['items'][l]['path']
                            media_urls = tree['items'][i]['items'][j]['items'][k]['items'][l]['items'][m]

                            media_urls_aggregate.append(read_media_urls_txt(local_path + '/' + media_urls))

    media_urls_aggregate = sorted(list(set(media_urls_aggregate)))
    write_txt(media_urls_aggregate)
    return

# reads index_media_urls
def read_json(text_name='index_record'):
    path = os.getcwd()
    with open('./__index__/'+text_name + ".json", 'r') as f: #w or wt?
        data = json.load(f)
    print("Read "+str(text_name)+".json from path: "+str(path))
    return data

# inputs path to media_urls.txt and outputs urls as list
def read_media_urls_txt(path):
    with open(path, 'rt') as f:
        media_urls = f.read().splitlines()
    f.close()
    return media_urls

# writes sorted list of unique img source urls, newline delimited, to
def write_txt(data, text_name='media_urls_aggregate'):
    with open('./__index__/'+text_name+'.txt', 'w') as f: #w or wt?
        for url in data:
            f.write(url+"\n")
    print("Wrote "+str(text_name)+".txt to to path: "+str(os.getcwd()+'/__index__/'))
    return

if __name__ == '__main__':
    main()
