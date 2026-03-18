import os
import shutil

path_to_create = os.path.join("data", "reports", "2026", "monthly")

try:
    os.makedirs(path_to_create, exist_ok=True)
    print(f"Directory ready: {path_to_create}")
except FileExistsError:
    print(f"Error: {path_to_create} is an existing file, not a directory.")
except OSError as e:
    print(f"An OS error occurred: {e}")



shutil.copy("test_file.txt", "parent/child/test_file_copy.txt")

shutil.move("test_file.txt", "parent/test_file_moved.txt")
print("File copied and moved successfully.")