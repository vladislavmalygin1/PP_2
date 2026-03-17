import os
import shutil
file_path_1 = r"C:\Users\Bull\Desktop\PP_2\Practice1\Practice_6\file_handling\document_1.txt"

if os.path.exists(file_path_1):
    os.remove(file_path_1)
else:
    print(f"File '{file_path_1}' does not exist.")

source_dir = r"C:\Users\Bull\Desktop\67"
backup_dir = r"C:\Users\Bull\Desktop\68"
try:
    shutil.copytree(source_dir, backup_dir)
    print(f"Directory '{source_dir}' backed up to '{backup_dir}'")
except FileExistsError:
    print(f"Error: The destination directory '{backup_dir}' already exists.")
except Exception as e:
    print(f"Error occurred: {e}")
if os.path.exists(backup_dir):
    os.rmdir(backup_dir)
    print("success")