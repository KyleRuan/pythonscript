import os

def scan_file(dir_path):
    files = os.listdir(dir_path)
    for file in files:
        file_path = dir_path+"/"+file
        if os.path.isdir(file_path):
            scan_file(file_path)
        else:
            print(file)