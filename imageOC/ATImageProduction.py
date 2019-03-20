#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import hashlib
import sys
print('gennerate image file start')
path_dir = './'
supportedExtensions = ["tiff", "tif", "jpg", "jpeg", "gif", "png", "bmp", "bmpf", "ico", "cur", "xbm"]
contents = 'Contents.json'
exclude_dir = "/Pods"
exclude_image_sets_dir = ['Animation', "Translate","Launch Screen"]
md5_file_path = os.path.join(os.getcwd(),'..',".image_md5_sum")

class FileManager:
    def __init__(self,path_dir,name_change = dict()):
        self.path_dir = path_dir
        self.name_change = name_change
    
    def walk_project(self,path):
        """ 查找全工程的xcassets 文件夹 
        """
        files = os.listdir(path)
        for file in files:
            sets_path = path + "/" + file
            if '.xcassets' in file:
                if self.path_dir+exclude_dir not in sets_path:
                    self.go_walk_xcassets(sets_path, "")
            else:
                if os.path.isdir(sets_path):
                    self.walk_project(sets_path)
                else:
                    if file.split('.')[-1] in supportedExtensions:
                        pass
                    #todo with the png in source
                    # print(file)
    
    def refactor_image_name(self,image_name):
        """ 将图片名命名为驼峰的形式 
        例如 tab_me ==> tabMe
        """
        def tuofeng(x):
            if len(x) > 1:
                return x[0].upper()+x[1:]
            else:
                return x

        name_list = image_name.split('_')
        if len(name_list) > 1:
            names = map(tuofeng, image_name.split('_')[1:])
            return image_name.split('_')[0][0].lower()+image_name.split('_')[0][1:]+''.join(list(names))
        else:
            return image_name[0].lower() +image_name[1:]
        

    def go_walk_xcassets(self,walk_path, namespace, cate=""):
        """ 处理一个单独xcassets
        """
        files = os.listdir(walk_path)
        if cate == "":
            files = list(set(files).difference(set(exclude_image_sets_dir)))
        next_prefix = namespace
     
        if contents in files:
            with open(walk_path + '/Contents.json', 'r') as f:
                data = f.read()
                config = json.loads(data)
                if 'properties' in config:
                    prefix = walk_path.split('/')[-1]
                    next_prefix = namespace + prefix + '/'
        if '.xcassets' not in walk_path.split('/')[-1]:
            if cate == "":
                cate = walk_path.split('/')[-1]
            else:
                cate = cate + "/" + walk_path.split('/')[-1]
        for file in files:
            file_path = walk_path+"/"+file
            if os.path.isdir(file_path):
                is_asset = file.split('.')[-1] == 'imageset'
                if is_asset:
                    asset_name = file.split('.')[0]
                    image_name = next_prefix+asset_name
                    image_var_name = self.refactor_image_name(image_name)

                    value = image_name
                    values = value.split('/')
                    if len(values) > 1:
                        path = values[-1].lower()
                        for cate in values[0:-1]:
                            cate = cate.lower() + "_"
                            if cate == path[0:len(cate)]:
                                path = path[len(cate):]
                        image_var_name = self.refactor_image_name(path)
                    self.name_change[asset_name] = {"image_name": image_name, "category": cate, "image_var_name": image_var_name}
                    continue
                self.go_walk_xcassets(file_path, next_prefix, cate)
    
    def sort_name_list(self):
        """ 按key 排序 变量名（防止冲突）
        """
        keys = list(self.name_change.keys())
        keys.sort() 
        new_D = dict()
        for key in keys:
            new_D[key] = self.name_change[key]
        self.name_change = new_D
    
    def update_content_hash(self,running_hash, file, encoding=''):
        """Update running SHA1 hash, factoring in hash of given file.
        Side Effects:
            running_hash.update()
        """
        if encoding:
            lines = file.split("\n")
            for line in lines:
                hashed_line = hashlib.sha1(line)
                hex_digest = hashed_line.hexdigest().encode(encoding)
                running_hash.update(hex_digest)
        else:
            running_hash.update(hashlib.sha1(file).hexdigest())

    def check_need_update(self):
        """ check if need update file
        Returns:    
            bool: yes to update
        """
        current_md5 = self.dir_hash(self.path_dir)
        last_md5 = ""
        path = md5_file_path
        file_operation = 'r'
        if not os.path.exists(path):    
            file_operation = 'w+'

        with open(path,file_operation) as file:
            last_md5 = file.read()
            last_md5 = str(last_md5)
            is_equal = last_md5 == current_md5
            if not is_equal:
                with open(path,'w') as f:
                    f.write(current_md5)
                    return is_equal
            else:
                return is_equal

    def dir_hash(self, verbose=False):
        """Return SHA1 hash of a directory.

        Args:
            verbose (bool): If True, prints progress updates.

        Raises: 
            FileNotFoundError: If directory provided does not exist.

        Returns:    
            string: SHA1 hash hexdigest of a directory.
        """
        sha_hash = hashlib.sha1()

        if not os.path.exists(self.path_dir):
            raise FileNotFoundError
        content = ""
        for root, dirs, files in os.walk(self.path_dir):
            for dir_name in dirs:
                if '.imageset' in dir_name:
                    content += os.path.join(root,dir_name) + "\n"
                
        self.update_content_hash(sha_hash,content,encoding='utf-8')
        return sha_hash.hexdigest()
    


        
file_manager = FileManager(path_dir)
if file_manager.check_need_update():
    print("not change ")
    sys.exit()
else:
    print("change ")

file_manager.walk_project(file_manager.path_dir)
include_image_sets_dir = ['Business', "UIControl"]

file_manager.sort_name_list()
config = file_manager.name_change

one_class = dict()
insert_order = list()
in_category = list()



def tuofeng(x):
    if len(x) > 1:
        return x[0].upper()+x[1:]
    else:
        return x
        
for key in config:
    item = config[key]
    image_name = item['image_name']
    levels = image_name.split('/')
    if len(levels)== 1:
        # 采用文件夹的方式也就是目录的结构
        dir_levels = item['category'].split('/')
        if dir_levels[0] in include_image_sets_dir:
# 标准的命名方式, 从第二个开始取 其实可以去掉
            dir_levels = dir_levels[1:]
        dir_levels =list(map(tuofeng, dir_levels)) 
        levels = dir_levels +levels
    
    if len(levels) == 2:
        class_name = levels[0][0].upper()+levels[0][1:]
        if class_name not in one_class:
            one_class[class_name] = list()
            insert_order.append(class_name)
            in_category.append(class_name)
        one_class[class_name].append(item)
    elif len(levels) >= 3:
        class_name = levels[1]
        i = 1
        while i <= len(levels)-1:
            new_item = dict()
            new_class_name = ""
            for name in levels[:i]:
                new_class_name += name[0].upper()+name[1:].lower()
            new_item['image_var_name'] = file_manager.refactor_image_name(levels[i])
            if i != len(levels)-1:
                for name in levels[:i]:
                    class_name = ""
                    for name in levels[:i+1]:
                        class_name += name[0].upper()+name[1:].lower()
                    new_item['class_name'] = class_name
            else:
                new_item['image_name'] = image_name
            if new_class_name not in one_class:
                one_class[new_class_name] = list()
                insert_order.insert(0,new_class_name)
                if i == 1 :
                    in_category.append(new_class_name)
            one_class[new_class_name].append(new_item)
            i += 1

# gyb
# 代码模板
h_interface_temp = "@interface ATImageIMAGE_CLASS_INSERT :NSObject\n"
m_imp_temp = "@implementation ATImageIMAGE_CLASS_INSERT\n"
h_temp_str = "/** \n\
 IMAGE_ORIGIN_NAME_INSERT \n\
 */ \n\
@property (nonatomic, strong,readonly) PROPERTY_NAME_INSERT *IMAGE_NAME_INSERT;\n\n\
"
m_temp_str = '- (UIImage *)IMAGE_NAME_INSERT { \n\
    return [UIImage imageNamed:@"IMAGE_ORIGIN_NAME_INSERT"];\n\
}\n\n'
m_custom_temp_str = '- (PROPERTY_NAME_INSERT *)IMAGE_NAME_INSERT { \n\
    return [PROPERTY_NAME_INSERT new];\n\
}\n'

h_content = ""
m_content = ""
num = 0

var_config = dict()

for key in insert_order:
    arr = one_class[key]
    h_interface = h_interface_temp.replace('IMAGE_CLASS_INSERT', key[0].upper()+key[1:])
    h_imp = m_imp_temp.replace('IMAGE_CLASS_INSERT', key[0].upper()+key[1:])
    h_var = ''
    m_var = ''
    for item in arr:
        class_name = "UIImage"
        if "class_name" in item:
            class_name = "ATImage"+item["class_name"]
    
        if "image_name" in item:
            image_name =  item['image_name']
            m_temp = m_temp_str
        else:
            image_name = class_name
            m_temp = m_custom_temp_str  
        var_str = h_temp_str.replace('IMAGE_NAME_INSERT', item['image_var_name']).replace("IMAGE_ORIGIN_NAME_INSERT", image_name).replace('PROPERTY_NAME_INSERT', class_name)
        m_str = m_temp.replace('IMAGE_NAME_INSERT', item['image_var_name']).replace("IMAGE_ORIGIN_NAME_INSERT", image_name).replace('PROPERTY_NAME_INSERT', class_name)
        var_config[item["image_name"]] = "UIImage."+key[0].lower()+key[1:]+ "."+item['image_var_name']
        if var_str not in h_var:
            h_var += var_str
            num +=1

        if m_str not in m_var:
            m_var += m_str

    h_content += h_interface + h_var + "@end\n\n"
    m_content += h_imp + m_var + "@end\n\n"

# 插入对象

image_cate_var_temp = "@property (nonatomic, strong, class,readonly) ATImageINSERT_CLASS *INSERT_VAR_STR;\n"
image_cate_var_key_temp = 'static NSString * const kATImageINSERT_CLASS = @"kATImageINSERT_CLASS";\n'
image_cate_imp_temp = "+ (ATImageINSERT_CLASS *)INSERT_VAR_STR {\n\
    ATImageINSERT_CLASS * INSERT_VAR_STR = objc_getAssociatedObject(self, &kATImageINSERT_CLASS);\n\
    if (!INSERT_VAR_STR) {\n\
        INSERT_VAR_STR = [ATImageINSERT_CLASS new];\n\
        [self setINSERT_CLASS:INSERT_VAR_STR];\n\
    }\n\
    return INSERT_VAR_STR;\n\
}\n\
\
+(void)setINSERT_CLASS:(ATImageINSERT_CLASS *)INSERT_VAR_STR {\n\
    objc_setAssociatedObject(self, &kATImageINSERT_CLASS, INSERT_VAR_STR, OBJC_ASSOCIATION_RETAIN_NONATOMIC);\n\
}\n\n"

image_h_content = ""
image_m_content = ""
image_m_key_content = ""
for item in in_category:
    class_name = item[0].upper()+item[1:]
    var_name = item[0].lower()+item[1:]
    image_h_content += image_cate_var_temp.replace('INSERT_CLASS',class_name).replace('INSERT_VAR_STR',var_name)
    image_m_content += image_cate_imp_temp.replace('INSERT_CLASS',class_name).replace('INSERT_VAR_STR',var_name)
    image_m_key_content += image_cate_var_key_temp.replace('INSERT_CLASS',class_name).replace('INSERT_VAR_STR',var_name)

image_h_content = '@interface UIImage (Resource)\n\n' + image_h_content + '\n\n@end\
\
\nNS_ASSUME_NONNULL_END'

image_m_content = '@implementation UIImage (Resource)\n\n'+image_m_content+'\n\n@end'

h_output = '#import <UIKit/UIKit.h>\n\n\
\
NS_ASSUME_NONNULL_BEGIN\n' + h_content + image_h_content 

m_output = '#import "ATImageResource.h"\n\
#import <objc/runtime.h>\n\n' + m_content + image_m_key_content + image_m_content


h_file_name = "./ATImageResource.h"
with open(h_file_name, 'w') as f:
    f.write(h_output)
h_file_name = "./ATImageResource.m"
with open(h_file_name, 'w') as f:
    f.write(m_output)
print('gennerate image file done')


# config_path = './result.json'
# with open(config_path, 'w+') as f:
#     f.write(json.dumps(var_config))


