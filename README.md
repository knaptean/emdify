# emdify

Prepare multiple Word files for migrating to the documentation website at once.

- Converts .docx to Markdown.
- Renames and saves images to a separate folder.
- Refactors image links in Markdown files to the wiki-ready.

## Requirements

- [Pandoc](https://pandoc.org/installing.html)
- [Python](https://www.python.org/downloads/)

## How to setup

- Download and install the requirements.
- Download the repository.
- You will need to create a folder where your files will be converted.
- In this folder, extract the `main.py` file in the downloaded zip.
- The setup is now complete. You can now delete the downloaded zip file.

## How to convert files

- Navigate to the folder.
- Place the `.docx` files you want to convert to Markdown in the folder.
- In the address bar of File Explorer type `cmd` and press the Enter key. The terminal window appears.
  You can also right-click in the folder and select **Open in Terminal**.
- Enter `python .\main.py` and press the Enter key.
- The converted files will be generated in the `md` folder and images will be saved to `md\images`.
- Drag and drop all the images from the images folder to the `.attachments` folder in VS Code.
- Drag and drop the Markdown files to the desired location in the VS Code Explorer.
- Delete the `md` folder and the `.docx` files that have been converted.
