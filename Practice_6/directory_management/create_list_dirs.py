import os
import shutil
from pathlib import Path


Path("parent/child/grandchild").mkdir(parents=True, exist_ok=True)
print("Directories created.")


print("Contents of current directory:", os.listdir('.'))


Path("test_file.txt").touch()
txt_files = [f for f in os.listdir('.') if f.endswith('.txt')]
print(f"Found text files: {txt_files}")


shutil.copy("test_file.txt", "parent/child/test_file_copy.txt")

shutil.move("test_file.txt", "parent/test_file_moved.txt")
print("File copied and moved successfully.")