import shutil
shutil.copy("test_file.txt", "parent/child/test_file_copy.txt")

shutil.move("test_file.txt", "parent/test_file_moved.txt")
print("File copied and moved successfully.")