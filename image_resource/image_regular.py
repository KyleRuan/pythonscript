import os
import json

print('gennerate image file start')
path_dir = "/Users/kyleruan/Documents/kwai/kwai_feature" # 文件夹目录
path_dir = './'
supportedExtensions = ["tiff", "tif", "jpg", "jpeg", "gif", "png", "bmp", "bmpf", "ico", "cur", "xbm"]
contents = 'Contents.json'
exclude_dir = "/Pods"
name_change = dict()
exclude_image_sets_dir = ['Animation', "Translate"]


def refactor_image_name(image_name):
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


def go_walk_xcassets(walk_path, namespace, cate=""):
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
                image_var_name = refactor_image_name(image_name)
                name_change[asset_name] = {"image_name": image_name, "category": cate, "image_var_name": image_var_name}
                continue
            go_walk_xcassets(file_path, next_prefix, cate)


def walk_project(path):
    files = os.listdir(path)
    for file in files:
        sets_path = path + "/" + file
        if '.xcassets' in file:
            if path_dir+exclude_dir not in sets_path:
                go_walk_xcassets(sets_path, "")
        else:
            if os.path.isdir(sets_path):
                walk_project(sets_path)
            else:
                if file.split('.')[-1] in supportedExtensions:
                    pass
                    #todo with the png in source
                    # print(file)

walk_project(path_dir)

#  这个只需要执行一次 去规范命名
for key in name_change:
    value = name_change[key]['image_name']
    values = value.split('/')
    if len(values) > 1:
        path = values[-1].lower()
        for cate in values[0:-1]:
            cate = cate.lower() + "_"
            if cate == path[0:len(cate)]:
                path = path[len(cate):]
        name_change[key]["image_var_name"] = refactor_image_name(path)

project_path = "./"
include_image_sets_dir = ['Business', "UIControl"]

# 产生文件
config = name_change
one_class = dict()
insert_order = list()
in_category = list()
def sort_by_value(d): 
    keys = list(d.keys())
    keys.sort() 
    new_D = dict()
    for key in keys:
        new_D[key] = d[key]
    return new_D

config = sort_by_value(config)
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

        def tuofeng(x):
            if len(x) > 1:
                return x[0].upper()+x[1:]
            else:
                return x
        
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
            new_item['image_var_name'] = refactor_image_name(levels[i])
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

# 代码模板
h_interface_temp = "@interface KSOImageIMAGE_CLASS_INSERT :NSObject\n"
m_imp_temp = "@implementation KSOImageIMAGE_CLASS_INSERT\n"
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

for key in insert_order:
    arr = one_class[key]
    h_interface = h_interface_temp.replace('IMAGE_CLASS_INSERT', key[0].upper()+key[1:])
    h_imp = m_imp_temp.replace('IMAGE_CLASS_INSERT', key[0].upper()+key[1:])
    h_var = ''
    m_var = ''
    for item in arr:
        class_name = "UIImage"
        if "class_name" in item:
            class_name = "KSOImage"+item["class_name"]
    
        if "image_name" in item:
            image_name =  item['image_name']
            m_temp = m_temp_str
        else:
            image_name = class_name
            m_temp = m_custom_temp_str  
        var_str = h_temp_str.replace('IMAGE_NAME_INSERT', item['image_var_name']).replace("IMAGE_ORIGIN_NAME_INSERT", image_name).replace('PROPERTY_NAME_INSERT', class_name)
        m_str = m_temp.replace('IMAGE_NAME_INSERT', item['image_var_name']).replace("IMAGE_ORIGIN_NAME_INSERT", image_name).replace('PROPERTY_NAME_INSERT', class_name)
        if var_str not in h_var:
            h_var += var_str
            num +=1

        if m_str not in m_var:
            m_var += m_str

    h_content += h_interface + h_var + "@end\n\n"
    m_content += h_imp + m_var + "@end\n\n"

# 插入对象

image_cate_var_temp = "@property (nonatomic, strong, class,readonly) KSOImageINSERT_CLASS *INSERT_VAR_STR;\n"
image_cate_var_key_temp = 'static NSString * const kKSOImageINSERT_CLASS = @"kKSOImageINSERT_CLASS";\n'
image_cate_imp_temp = "+ (KSOImageINSERT_CLASS *)INSERT_VAR_STR {\n\
    KSOImageINSERT_CLASS * INSERT_VAR_STR = objc_getAssociatedObject(self, &kKSOImageINSERT_CLASS);\n\
    if (!INSERT_VAR_STR) {\n\
        INSERT_VAR_STR = [KSOImageINSERT_CLASS new];\n\
        [self setINSERT_CLASS:INSERT_VAR_STR];\n\
    }\n\
    return INSERT_VAR_STR;\n\
}\n\
\
+(void)setINSERT_CLASS:(KSOImageINSERT_CLASS *)INSERT_VAR_STR {\n\
    objc_setAssociatedObject(self, &kKSOImageINSERT_CLASS, INSERT_VAR_STR, OBJC_ASSOCIATION_RETAIN_NONATOMIC);\n\
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

m_output = '#import "KSOImageResource.h"\n\
#import <objc/runtime.h>\n\n' + m_content + image_m_key_content + image_m_content


h_file_name = "./gif/UICommon/KSOImageResource.h"
with open(h_file_name, 'w', encoding='utf8') as f:
    # print('生成'+str(num)+"个图片对象")
    f.write(h_output)
h_file_name = "./gif/UICommon/KSOImageResource.m"
with open(h_file_name, 'w', encoding='utf8') as f:
    f.write(m_output)
print('gennerate image file done')
# with open('./result.json', 'w') as fs:
#     fs.write(json.dumps(one_class))
