import os
import subprocess
from slugify import slugify
import shutil
import re

if __name__ == "__main__":
   path = os.path.join(os.getcwd(), "md")
   #main()
   # Create a new dir, and an image dir inside it
   media_dir = os.path.join(path, "media")

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

   ## TODO: Show progress bar

   ## TODO: Exit if no files
   # For each file:
   for f in os.listdir():
      name, ext = os.path.splitext(f)
      if "doc" in ext:
         # Convert file to md and extract images
         # Slugify filename
         slug = slugify(name)
         target = os.path.join(path, f"{slug}.md")
         #temp_img_dir = os.path.join(path, "temp")
         subprocess.run(["pandoc", "-t", "gfm", "--extract-media", path, "--wrap=none", f, "-o", target])

         # Check for img tags and convert to markdown syntax
         # Change image addresses in file
         def img_to_md(str):
            img_num = img_num_pattern.search(str.group()).group()
            #img_num = re.search("(\d+)\.\w{3,4}(?=\")", str)
            return f"![image](/.attachments/{slug}{img_num})"

         md_text = ""
         with open(target, "r", encoding='utf-8') as md_file:
            md_text = md_file.read()

         with open(target, "w", encoding='utf-8') as md_file:
            #md_text = md_file.read()
            md_text = re.sub("<img src.+\/>", img_to_md, md_text)
            md_file.write(md_text)

         # Rename images using slugified filename
         for img in os.listdir(media_dir):
            renamed = f"{slug}{img.replace('image','')}"
            shutil.move(os.path.join(media_dir, img), os.path.join(path, "images", renamed))

   os.removedirs(media_dir)
