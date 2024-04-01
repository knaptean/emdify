import os
import random
import subprocess
import shutil
import re
from datetime import date

product = ""
author = ""
techwriter = ""

def slugify(s):
    s = s.strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

def convert_files(file_list):
   path = os.path.join(os.getcwd(), "md")
   media_dir = os.path.join(path, "media")

   rand = ''.join(random.choice("abcdefghijklmnopqrstuvwxyz23456890") for i in range(5))

   ## TODO: Add metadata

   ## TODO: ask to delete folder
   ##if os.path.exists(path):
   ##   confirm_delete = input("This folder already exists. Delete the folder (y/n):")
   ##   if confirm_delete == "y" or confirm_delete == "Y":
   ##      os.remove(path)
   ##   else:
   ##      exit("Cannot overwrite 'md' folder")

   # Create a new dir, and an image dir inside it
   if not os.path.exists(path):
      os.makedirs(os.path.join(path, ".attachments"))
   # Create a media dir, if it doesnt exist
   if not os.path.exists(media_dir):
      os.makedirs(media_dir)

   img_num_pattern = re.compile("(\d+)\.\w{3,4}(?=\")")

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

         partial_metadata = f"product: {product}\n" \
                    "author:\n" \
                    f"  - {author}\n" \
                    "tech-writer:\n" \
                    f"  - {techwriter}\n" \
                    "reviewer: \n" \
                    f"  - {author}\n" \
                    f"reviewed: {date.today()}\n" \
                    "tags:\n" \
                    f"  - {product}\n" \
                    "---\n\n"
         md_text = ""
         with open(target, "r", encoding='utf-8') as md_file:
            md_text = md_file.read()
            # if h1 exsists, use as title
            title, md_text = md_text.split("\n", 1)
            if title[0] == "#":
               title = title[2:]
            else:
               md_text = title + "\n" + md_text
               title = ""

            md_text = f"---\ntitle: {title}\n" + partial_metadata + md_text
            # remove escape characters for backticks
            md_text = md_text.replace('\`', '`')
            md_text = md_text.replace('“|”', '"')
            # add kbd tags
            md_text = md_text.replace('\[\[', '<kbd>')
            md_text = md_text.replace('\]\]', '</kbd>')
            # convert img to markdown syntax and update src
            md_text = re.sub("<img src.+\/>", img_to_md, md_text)

         with open(target, "w", encoding='utf-8') as md_file:
            md_file.write(md_text)

         # Rename images using slugified filename
         for img in os.listdir(media_dir):
            renamed = f"{slug}{rand}{img.replace('image','')}"
            shutil.move(os.path.join(media_dir, img), os.path.join(path, ".attachments", renamed))

      #print(f"...Completed {name}")
   if os.path.exists(media_dir):
      os.removedirs(media_dir)

if __name__ == "__main__":
   file_list = [f for f in os.listdir('.') if f.endswith('.docx')]
   if len(file_list) > 0:
      product = input("Product name: ")
      author = input("Author: ")
      techwriter = input("Tech Writer: ")
      reviewer = input("Reviewer: ")
      
      convert_files(file_list)

      print("===Converted all files===")
   else:
      print("No files to convert!")
