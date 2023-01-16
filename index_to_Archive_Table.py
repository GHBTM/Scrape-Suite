# Index_to_Archive_Table will take the index_record.json map and
from PIL import Image, ExifTags
import pymage_size
import pandas as pd
import numpy as np
import json
import os


def main():
    tree = read_json()
    media_urls_dict = get_urls_map()
    df = build_dataframe(tree, media_urls_dict)
    write_csv(df, 'archive_table')
    return

def get_urls_map():
    media_urls = read_txt()
    media_urls_dict = {}
    for url in media_urls:
        prefix_url = url.replace('.jpg','').replace('.jpeg','').replace('.png','').replace('.webp','')
        media_name_1 = prefix_url.split("/")[-1]
        media_name_3 = prefix_url.split("/")[-3]+url.split("/")[-2]+url.split("/")[-1]
        media_urls_dict[media_name_1] = url
        media_urls_dict[media_name_3] = url
    return media_urls_dict

def build_dataframe(tree, media_urls_dict):
    all_imgs = []
    for i in range(len(tree['items'])):
        source = tree['items'][i]['folder']
        for j in range(len(tree['items'][i]['items'])):
            brand = tree['items'][i]['items'][j]['folder']
            for k in range(len(tree['items'][i]['items'][j]['items'])):
                genre = tree['items'][i]['items'][j]['items'][k]['folder']
                for l in range(len(tree['items'][i]['items'][j]['items'][k]['items'])):
                    category = tree['items'][i]['items'][j]['items'][k]['items'][l]['folder']
                    for m in range(len(tree['items'][i]['items'][j]['items'][k]['items'][l]['items'])):
                        img = tree['items'][i]['items'][j]['items'][k]['items'][l]['items'][m]
                        if (type(img) == type('a')) & (source == ('Company Site')):
                            all_imgs.append(img)

    all_imgs = sorted(list(set(all_imgs)))
    Columns = ['Source','Brand','Item Type','Width','Height','Size (kB)','Image URL', 'Path']
    #df = pd.DataFrame(pd.np.empty((len(all_imgs), len(Columns))), columns = Columns, index = all_imgs)
    df = pd.DataFrame(np.nan,columns = Columns, index = all_imgs)
    print(str(len(all_imgs)))
    count = 0
    for i in range(len(tree['items'])):
        source = tree['items'][i]['folder']
        for j in range(len(tree['items'][i]['items'])):
            brand = tree['items'][i]['items'][j]['folder']
            for k in range(len(tree['items'][i]['items'][j]['items'])):
                genre = tree['items'][i]['items'][j]['items'][k]['folder']
                for l in range(len(tree['items'][i]['items'][j]['items'][k]['items'])):
                    category = tree['items'][i]['items'][j]['items'][k]['items'][l]['folder']
                    for m in range(len(tree['items'][i]['items'][j]['items'][k]['items'][l]['items'])):
                        img = tree['items'][i]['items'][j]['items'][k]['items'][l]['items'][m]
                        if (type(img) == type('a')) & (source == ('Company Site')):
                            path = tree['items'][i]['items'][j]['items'][k]['items'][l]['path'] +'/' + img
                            try:
                                width, height = pymage_size.get_image_size(path).get_dimensions()
                            except:
                                print(source+", "+brand+", "+genre+", "+category+", "+img)
                            size = round(os.path.getsize(path)/1000,3)
                            url = ''
                            img_strip = img.replace('.jpg','').replace('.jpeg','').replace('.png','').replace('.webp','')
                            if img_strip in media_urls_dict.keys():
                                url = media_urls_dict[img_strip]

                            if pd.isnull(df.loc[img,'Source']):
                                df.loc[img,'Source'] = source
                            elif df.loc[img,'Source'] != source:
                                print('Dup Error: '+source +' for '+img)

                            if pd.isnull(df.loc[img,'Brand']):
                                df.loc[img,'Brand'] = brand
                            elif df.loc[img,'Brand'] != brand:
                                print('Dup Error: '+brand +' for '+img)

                            if pd.isnull(df.loc[img,'Item Type']):
                                df.loc[img,'Item Type'] = genre + " " + category
                            elif df.loc[img,'Item Type'] != genre + " " + category:
                                df.loc[img,'Item Type'] = df.loc[img,'Item Type']+"|"+ genre + " " + category

                            if pd.isnull(df.loc[img,'Width']):
                                df.loc[img,'Width'] = width
                            elif df.loc[img,'Width'] != width:
                                print('Width Dup Error: '+str(df.loc[img,'Width'])+", "+str(width) +' for '+img)

                            if pd.isnull(df.loc[img,'Height']):
                                df.loc[img,'Height'] = height
                            elif df.loc[img,'Height'] != height:
                                print('Height Dup Error: '+str(df.loc[img,'Height'])+", "+str(height) +' for '+img)

                            if pd.isnull(df.loc[img,'Size (kB)']):
                                df.loc[img,'Size (kB)'] = size
                            #elif df.loc[img,'Size (kB)'] != size:
                                #first_size = df.loc[img,'Size (kB)']
                                #first_path = df.loc[img,'Path']
                                #second_size = size
                                #second_path = path
                                #if first_size > second_size:
                                    #print('dif = '+str((first_size-second_size)/second_size))
                                    #try:
                                        #img_A = Image.open(first_path)
                                        #img_A.save(second_path, quality = 100, subsampling = 0)
                                        #print('overwrote')
                                    #except IOError:
                                        #print('failed to overwrite')
                                #if first_size < second_size:
                                    #print('dif = '+str((second_size-first_size)/first_size))
                                    #try:
                                        #img_B = Image.open(second_path)
                                        #img_B.save(first_path, quality = 100, subsampling = 0)
                                        #print('overwrote')
                                    #except IOError:
                                        #print('failed to overwrite')
                                #string_1 = 'Dup Error: '+str(size) +' & '+str(df.loc[img,'Size (kB)'])+' for '+img
                                #string_2 = df.loc[img,'Brand']+", "+df.loc[img,'Item Type']
                                #print(string_1)
                                #print(string_2)

                            if pd.isnull(df.loc[img,'Image URL']):
                                df.loc[img,'Image URL'] = url
                            elif df.loc[img,'Image URL'] != url:
                                print('Dup Error: '+url +' for '+img)

                            if pd.isnull(df.loc[img,'Path']):
                                df.loc[img,'Path'] = path
                            elif df.loc[img,'Image URL'] != url:
                                print('Dup Error: '+url +' for '+img)

                            count += 1
                            if count%5000 == 0:
                                print(count)
    #write_txt(ERROR_LOG)
    return df

def initialize_directory(output_folder):
    path = os.getcwd()
    home_dir = path
    IO = path + "/" +str(output_folder)
    if not os.path.exists(IO):
        os.mkdir(IO)
    return

def read_json(text_name='index_record'):
    path = os.getcwd()
    with open('./__index__/'+text_name + ".json", 'r') as f: #w or wt?
        data = json.load(f)
    print("Read "+str(text_name)+".json from path: "+str(path))
    return data

def read_txt(text_name='media_urls_aggregate'):
    with open('./__index__/'+text_name+'.txt', 'rt') as f:
        media_urls_aggregate = f.read().splitlines()
    f.close()
    return media_urls_aggregate

def write_csv(data, text_name):
    path = os.getcwd()
    data.to_csv('./__index__/'+text_name+'.csv', index=True)
    print("Wrote "+text_name+".csv to to path: "+str(path)+'/__index__/')
    return

def write_txt(data, text_name='ERROR_LOG'):
    with open('./__index__/'+text_name+'.txt', 'w') as f: #w or wt?
        for url in data:
            f.write(url+"\n")
    print("Wrote "+str(text_name)+".txt to to path: "+str(os.getcwd()+'/__index__/'))
    return

if __name__ == '__main__':
    main()
