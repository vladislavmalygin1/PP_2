import os
folder = r"C:\Users\Bull\Desktop\PP_2\Practice1\Practice_6\file_handling"

file = "document_1.txt"

full_path = os.path.join(folder, file)

with open(full_path, "w", encoding = "utf-8") as b:
    b.write("This is possible too")

with open("document_2.txt", "w") as a:
    a.write("Wooooow, that's cool")


#Appendig
lines_to_append = ["\nLine 1", "\nLine 2", "\nLine 3"]
with open("demofile.txt", "a") as f:
    f.writelines(lines_to_append)

