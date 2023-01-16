# index_IO crawls through the current directory to build a dictionary map of the folder substructure.  Each nested dictionary contains a path, folder (name), and items/contents list.  Items lists will contain folders or files that match the filetypes specified in if __name__ == '__main__':
# Outputs a map, index_record.json, of the working path's directory and all subdirectory's contents.

import json
import os

def main(filetypes, input_folder, output_folder):
    folder, home_dir = initialize_directory(output_folder)
    tree = {'folder': folder, 'path': home_dir, 'items':[]}
    tree = build_layers_tree(filetypes, input_folder, tree, home_dir)
    write_json(tree)
    return
# Needs editing, function should call itself rather than iterate conditionals.
# Each for conditional builds a key value pair of the folder's name, path, and lists directory contents.
def build_layers_tree(filetypes, input_folder, tree, home_dir):
    os.chdir(home_dir)
    dr = clean_listdr(filetypes, os.listdir(), home_dir)
    sub_tree = build_sub_tree(dr, home_dir)

    tree['items'] = sub_tree

    for item in tree['items']:
        if type(item) is dict:
            path = item['path']
            os.chdir(path)
            dr = clean_listdr(filetypes, os.listdir(), path)
            sub_tree = build_sub_tree(dr, path)
            item['items'] = sub_tree
            for i in item['items']:
                #item = tree[0]['items'][i]
                if type(i) is dict:
                    path = i['path']
                    os.chdir(path)
                    dr = clean_listdr(filetypes, os.listdir(), path)
                    sub_tree = build_sub_tree(dr, path)
                    i['items'] = sub_tree
                    for j in i['items']:
                        #item = tree[0]['items'][i]
                        if type(j) is dict:
                            path = j['path']
                            os.chdir(path)
                            dr = clean_listdr(filetypes, os.listdir(), path)
                            sub_tree = build_sub_tree(dr, path)
                            j['items'] = sub_tree
                            for k in j['items']:
                                #item = tree[0]['items'][i]
                                if type(k) is dict:
                                    path = k['path']
                                    os.chdir(path)
                                    dr = clean_listdr(filetypes, os.listdir(), path)
                                    sub_tree = build_sub_tree(dr, path)
                                    k['items'] = sub_tree

    return tree
# rebuilds listdr contents, excluding __folders__ and including files that match the provided filetypes
def clean_listdr(filetypes, dr, path):
    clean_dr = []
    for item in dr:
        if (item[0:2]!='._') and (item[0:2]!='__') and (item[-2:]!='__'):
            if '.' + item.split('.')[-1] in filetypes:
                clean_dr.append(item)
            if os.path.isdir(path+'/'+item):
                clean_dr.append(item)
    return sorted(clean_dr)

def build_sub_tree(dr, path):
    sub_tree = []
    for item in dr:
        if os.path.isfile(path+'/'+item):
            sub_tree.append(item)
        if os.path.isdir(path+'/'+item):
            item = {'folder': str(item), 'path': path+'/'+item, 'items': []}
            sub_tree.append(item)
    return sub_tree

# Checks for and creates output folder
def initialize_directory(output_folder):
    home_dir = os.getcwd()
    IO = home_dir + "/" +str(output_folder)
    if not os.path.exists(IO):
        os.mkdir(IO)
    parent_folder = os.path.basename(os.getcwd())
    return parent_folder, home_dir

# Writes new map to json file
def write_json(data, text_name='index_record'):
    os.chdir(data['path'])
    path = os.getcwd()
    with open('./__index__/'+text_name + ".json", 'w') as f: #w or wt?
        json.dump(data, f, indent = 4)
    print("Wrote "+str(text_name)+".json to to path: "+str(path))
    return

if __name__ == '__main__':
    filetypes = ['.jpg','.jpeg','.png','.webp','.txt']
    input_folder = ''
    output_folder = '__index__'
    main(filetypes, input_folder, output_folder)
