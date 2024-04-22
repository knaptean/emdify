import os
import random
import subprocess
import shutil
import re
from datetime import date

product = ""
author = ""
reviewer = ""
techwriter = ""

src_filename_pattern = re.compile("\/(\w+?\.[A-z]{3,4})(?=\")")

header_pattern = re.compile("^\#+\s")
ol_pattern = re.compile("^\s*\d+\.\s")
text_pattern = re.compile("^<?\w+")
ul_pattern = re.compile("^-\s")

# Create three directories
# One base dir with all converted files
base_dir = os.path.join(os.getcwd(), "md")
if not os.path.exists(base_dir):
   os.makedirs(base_dir)
# One temporary dir for images that need to be renamed
media_dir = os.path.join(base_dir, "media")
if not os.path.exists(media_dir):
   os.makedirs(media_dir)
# One directory which will contain all final images
attch_dir = os.path.join(base_dir, ".attachments")
if not os.path.exists(attch_dir):
   os.makedirs(attch_dir)

def slugify(s):
    s = s.strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_-]+', '-', s)
    s = re.sub(r'^-+|-+$', '', s)
    return s

def get_img_replacer_callback(slug, rand):
   def inner(str):
      img_tag = str.group()
      img_filename = src_filename_pattern.search(img_tag).group()

      # Change name of images in MD files using slug and random string
      if (img_filename.startswith("/image")):
         img_filename = img_filename.replace("image", f"{slug}{rand}")

      return f"![image](/.attachments{img_filename})"

   return inner

def insert_metadata(md_text):
   partial_metadata = f"product: {product}\n" \
           "author:\n" \
           f"  - {author}\n" \
           "tech-writer:\n" \
           f"  - {techwriter}\n" \
           "reviewer: \n" \
           f"  - {reviewer}\n" \
           f"published: {date.today()}\n" \
           f"reviewed: {date.today()}\n" \
           "tags:\n" \
           f"  - {product}\n" \
           "---\n\n"
   # if h1 exsists, use as title
   title, md_text = md_text.split("\n", 1)
   if title.startswith("# "):
      title = title[2:]
   else:
      md_text = title + "\n" + md_text
      title = ""
   md_text = f"---\ntitle: {title}\n" + partial_metadata + md_text

   return md_text


def convert_files(file_list):
   # For each file:
   for f in file_list:
      name, ext = os.path.splitext(f)
      print(f"Converting {name}...")
      if "doc" in ext:
         # generate a random string to use in the filename to prevent conflicts/overwriting
         rand = ''.join(random.choice("abcdefghijklmnopqrstuvwxyz23456890") for i in range(5))
         slug = slugify(name)
         target = os.path.join(base_dir, f"{slug}.md")

         # Use Pandoc to convert file to md and extract images
         subprocess.run(["pandoc", "-t", "gfm", f"--extract-media={base_dir}", "--wrap=none", f, "-o", target])
         # NOTE:
         # Pandoc may disregard the extract-media flag and save images to the md folder.
         # In this case, the filenames of the images extracted are hashes instead of the
         # usual convention of "image1.png", "image2.png", ...
         # Move these images directly into the .attachments folder

         for filename in os.listdir(base_dir):
            file = os.path.join(base_dir, filename) 
            if (os.path.isfile(file)) and (not filename.endswith('.md')):
               shutil.move(file, os.path.join(attch_dir, filename))

            md_text = ""
            with open(target, "r", encoding='utf-8') as md_file:
               lines = md_file.readlines()
               # a stack to store the indentation points
               landmarks = []
               indent = "    "

               # iterate over lines to fix spacing issues
               for i, line in enumerate(lines):
                  if len(line.strip()) > 0:
                     if header_pattern.match(line):
                        landmarks.clear()
                        md_text += "\n" + line

                     elif ol_pattern.match(line): # numbered list item
                        num = int(line.split(".")[0]) # get the number
                        if num == 1: # start of a new list
                           landmarks.append(num) # set a new indentation level
                        elif (len(landmarks) > 0) and (num - 1) != landmarks[-1]:
                           # break in the numbering
                           landmarks.pop() # go back one indent
                           landmarks[-1] = num # replace the last landmark
                        else:
                           landmarks[-1] = num # replace the last landmark
                        #md_text += "\n" + ( indent * (len(landmarks) - 1) ) + line # add new line and indent
                        md_text += "\n" + line # add new line and indent

                     else: # text/ul/image
                        md_text += "\n" + (indent * len(landmarks)) + line ## add indents

            md_text = insert_metadata(md_text)
            # remove escape characters for backticks
            md_text = md_text.replace('\`', '`')
            md_text = md_text.replace('“|”', '"')
            # add kbd tags
            md_text = md_text.replace('\[\[', '<kbd>')
            md_text = md_text.replace('\]\]', '</kbd>')

            # Replace HTML img tags with markdown syntax and update src
            img_replacer = get_img_replacer_callback(slug, rand)
            md_text = re.sub("<img src.+\/>", img_replacer, md_text)

         with open(target, "w", encoding='utf-8') as md_file:
            md_file.write(md_text)

         # Rename images using slugified filename
         for img in os.listdir(media_dir):
            renamed = f"{slug}{rand}{img.replace('image','')}"
            shutil.move(os.path.join(media_dir, img), os.path.join(attch_dir, renamed))

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
      if (reviewer == ""):
         reviewer = author
      
      convert_files(file_list)

      print("===Converted all files===")
   else:
      print("No files to convert!")
