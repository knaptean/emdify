import os
import random
import subprocess
import shutil
import re

def slugify(s):
    s = s.strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

if __name__ == "__main__":
   path = os.path.join(os.getcwd(), "md")
   #main()
   # Create a new dir, and an image dir inside it
   media_dir = os.path.join(path, "media")

   rand = ''.join(random.choice("abcdefghijklmnopqrstuvwxyz23456890") for i in range(5))

   ## TODO: ask to delete folder
   ##if os.path.exists(path):
   ##   confirm_delete = input("This folder already exists. Delete the folder (y/n):")
   ##   if confirm_delete == "y" or confirm_delete == "Y":
   ##      os.remove(path)
   ##   else:
   ##      exit("Cannot overwrite 'md' folder")

   if not os.path.exists(path):
      os.makedirs(os.path.join(path, "images"))

   img_num_pattern = re.compile("(\d+)\.\w{3,4}(?=\")")

   file_list = [f for f in os.listdir('.') if f.endswith('.docx')]
   # For each file:
   for f in file_list:
      name, ext = os.path.splitext(f)
      print(f"Converting {name}...")
      if "doc" in ext:
         # Slugify filename
         slug = slugify(name)
         target = os.path.join(path, f"{slug}.md")
         # Convert file to md and extract images
         subprocess.run(["pandoc", "-t", "gfm", "--extract-media", path, "--wrap=none", f, "-o", target])

         def img_to_md(str):
            img_num = img_num_pattern.search(str.group()).group()
            #img_num = re.search("(\d+)\.\w{3,4}(?=\")", str)
            return f"![image](/.attachments/{slug}{rand}{img_num})"

         md_text = ""
         with open(target, "r", encoding='utf-8') as md_file:
            md_text = md_file.read()

         with open(target, "w", encoding='utf-8') as md_file:
            # remove escape characters for backticks
            md_text = md_text.replace("\`", "`")
            # convert img to markdown syntax and update src
            md_text = re.sub("<img src.+\/>", img_to_md, md_text)
            md_file.write(md_text)

         # Rename images using slugified filename
         for img in os.listdir(media_dir):
            renamed = f"{slug}{rand}{img.replace('image','')}"
            shutil.move(os.path.join(media_dir, img), os.path.join(path, "images", renamed))

      #print(f"...Completed {name}")

   os.removedirs(media_dir)

print("===Converted all files===")
