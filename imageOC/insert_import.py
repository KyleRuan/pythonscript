import os
import re
import hashlib
import sys
exclude_image_sets_dir = ['Pods','gifTests']
project_path = '/Users/kyleruan/Documents/kwai/kwai_feature/Resources/images.xcassets'
project_path = '/Users/kyleruan/Documents/kwai/Artemis'

# 所有的配置文件
def insert_import(walk_path):
    files = os.listdir(walk_path)
    files = list(set(files).difference(set(exclude_image_sets_dir)))
    for file in files:
        file_path = walk_path+"/"+file
        if file.split('.')[-1] == 'm':
            with open(file_path,'r') as f:
                data = f.read()
                data = str(data)
                if '#import "ATImageResource.h"' in data:
                    continue
                pattern = re.compile('UIImage\.(.+?)?\.', re.X | re.M)
                matched = pattern.search(data)
                if matched :
                    string = matched.group(1)
                    print(string)
                    # 查找第一个 import
                    import_pattern = re.compile('\#import',re.X | re.M)
                    matched = import_pattern.search(data)
                    data = data[0:matched.start()]+ '\n#import "ATImageResource.h"\n' +data[matched.start():]
                    # print(data)
                    with open(file_path,'w') as fs:
                        fs.write(data)
        else:
            if os.path.isdir(file_path):
                insert_import(file_path)


insert_import(project_path)
