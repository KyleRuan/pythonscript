# PythonScript

这个库专门放一下，平时工作写的python脚本


## gyb
 修改了apple 原有的gyb脚本，通过一个配置文件和一个.gyb文件生成多个模板代码文件。
 
## ScanFile
递归查找文件

## rename_tuofeng
将下划线的命名方式改完驼峰命名方式例如tips_new_view 改为 tipsNewView
 
## refactor_image_name
运用了ScanFile，rename_tuofeng。来查找iOS项目的文件然后生成oc版的图片代码。将图片资源化。oc版本的图片资源化
## imageOC
三个脚本实现整套OC 版图片的RSwift版本
1. ATImageProduction.py 加到build phrase 加个脚本
2. 用ATImageProduction.py 替换现有工程中所有的实现
3. 最后使用insert_import.py 插入替换工程的头文件