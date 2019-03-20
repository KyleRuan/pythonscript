#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import re
import hashlib

exclude_image_sets_dir = ['Pods']
file_suffix = ['m']
config = dict()
# 先不替换 先找图片吧
# storyBoard .m中 imageNamed:声明的图片
image_used = list()
# 用变量名保存的图片
image_string = list()
# project path
project_path = '/Users/kyleruan/Documents/kwai/Artemis/Artemis'
# project_path = './'
 
class ImageUsage:
    def __init__(self,config_path):
        self.config_path = config_path
        self.redConfig()
        self.image_used = list()

    def redConfig(self):
        with open(self.config_path, 'r') as f:
            data = f.read()
            self.config = json.loads(data)

usage = ImageUsage("./result.json")
print(usage.config)
replace_keys = list(usage.config.keys())
image_named_replaced = usage.config


def replace_code(walk_path):
    files = os.listdir(walk_path)
    files = list(set(files).difference(set(exclude_image_sets_dir)))
    pattern = re.compile('imageNamed:@"(.+?)?"', re.X | re.M)
    for file in files:
        file_path = walk_path+"/"+file
        if file.split('.')[-1] == 'm':
            changed_file = False
            data = ""
            with open(file_path,'r') as f:
                data = f.read()
                data = str(data)
                matched = pattern.search(data)
                while matched:
                    replace = matched.group(1)
                    if replace in replace_keys:
                        # replace + image
                        tt = '[UIImage imageNamed:@"{}"]'.format(replace)
                        if tt in data:
                            data = data.replace(tt,image_named_replaced[replace])
                            changed_file = True
                        else:
                            print(replace)
                    matched = pattern.search(data,matched.end())
            if changed_file:
                if data == "":
                    print("dswewewewew")
                with open(file_path,'w') as fs:
                    fs.write(data)
        else:
            if os.path.isdir(file_path):
                replace_code(file_path)

replace_code(project_path)
