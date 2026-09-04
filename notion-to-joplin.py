#!/usr/bin/env python3
# This script is used to convert a Notion export to a Joplin import (MD - Markdown directory).
# Step 1: Get the notion export zip file
# Step 2: Unzip the notion export zip file
# Step 3: Rename every file with a .md extension with the heading of the file and fix all the links
# Step 4: Rename all folder. Remove the "hash" from the ending of the folder name and fix all the links

from argparse import ArgumentParser
import sys
import zipfile
import glob
import shutil
from os import path
import ntpath
import urllib.parse

# VARIABLES
FOLDER_EXTRACTION = "import to joplin"
MARKDOWN_EXTENSION = "md"
filename_backup = ""

## Step 1: Get the notion export zip file
# Delete the folder if it exists
if path.exists(FOLDER_EXTRACTION):
    shutil.rmtree(FOLDER_EXTRACTION)
# Get parameter
parser = ArgumentParser(
    prog="ProgramName",
    description="What the program does",
    epilog="Text at the bottom of help",
)
parser.add_argument("-f", "--file", help="File to be processed", required=True)
try:
    args = parser.parse_args()
    filename_backup = args.file
except:
    parser.print_help()
    sys.exit(0)

## Step 2: Unzip the file
print("Unzipping backup file...")
with zipfile.ZipFile(filename_backup, "r") as zip_ref:
    zip_ref.extractall(FOLDER_EXTRACTION)
print("Unzipping done.")

## Step 3: Rename every file with a .md extension with the heading of the file and fix all the links
print("Renaming files and fixing links...")
# Get all markdown files
path_to_files = path.join(FOLDER_EXTRACTION, "**/*." + MARKDOWN_EXTENSION)
for filename in glob.iglob(path_to_files, recursive=True):
    # Get the heading of the file
    with open(filename, "r", encoding="utf-8") as file:
        # Get the heading
        first_line = file.readline()
        heading = first_line.replace("# ", "").replace("\n", "").replace("/", "-")
        # Delete two first lines
        lines = file.readlines()
        lines_without_heading = lines[1:]
    # Write the file without the heading
    with open(filename, "w", encoding="utf-8") as file:
        file.write("".join(lines_without_heading))
    # Rename the file
    new_filename = path.join(path.dirname(filename), heading + "." + MARKDOWN_EXTENSION)
    shutil.move(filename, new_filename)
    # Fix all the links
    old_filename_encoded = urllib.parse.quote(ntpath.basename(filename))
    heading_encoded = urllib.parse.quote(heading) + "." + MARKDOWN_EXTENSION
    for filename_to_fix in glob.iglob(path_to_files, recursive=True):
        with open(filename_to_fix, "r", encoding="utf-8") as file:
            lines_to_fix = file.readlines()
        with open(filename_to_fix, "w", encoding="utf-8") as file:
            text_to_write = "".join(lines_to_fix).replace(
                old_filename_encoded, heading_encoded
            )
            file.write(text_to_write)
print("Renaming files and fixing links done.")

## Step 4: Rename all folders. Remove the "hash" from the ending of the folder name
print("Renaming folders...")

path_of_folders = path.join(FOLDER_EXTRACTION, '**/*')

# Get all folders first, deepest folders first
folders = [folder for folder in glob.iglob(path_of_folders, recursive=True) if path.isdir(folder)]
folders.sort(key=lambda folder: folder.count(path.sep), reverse=True)

for folder in folders:
    # The folder may have already been moved or removed
    if not path.isdir(folder):
        continue

    current_folder_name = path.basename(folder)
    new_folder_name = " ".join(current_folder_name.split(" ")[:-1])

    # If there is nothing to remove from the name, skip it
    if not new_folder_name:
        continue

    destination = path.join(path.dirname(folder), new_folder_name)

    if path.exists(destination):
        # Merge this folder into the existing folder
        for item in glob.glob(path.join(folder, "*")):
            item_name = path.basename(item)
            destination_item = path.join(destination, item_name)

            if path.exists(destination_item):
                if path.isdir(item) and path.isdir(destination_item):
                    # Merge nested folders recursively
                    for nested_item in glob.glob(path.join(item, "*")):
                        shutil.move(nested_item, destination_item)
                    shutil.rmtree(item)
                else:
                    # Keep both files if they have the same name
                    base, extension = path.splitext(item_name)
                    counter = 1
                    new_item = path.join(
                        destination,
                        f"{base}_{counter}{extension}"
                    )

                    while path.exists(new_item):
                        counter += 1
                        new_item = path.join(
                            destination,
                            f"{base}_{counter}{extension}"
                        )

                    shutil.move(item, new_item)
            else:
                shutil.move(item, destination)

        shutil.rmtree(folder)

    else:
        shutil.move(folder, destination)

    # Fix all the links
    old_folder_name_encoded = urllib.parse.quote(current_folder_name)
    new_folder_name_encoded = urllib.parse.quote(new_folder_name)

    for filename_to_fix in glob.iglob(path_to_files, recursive=True):
        with open(filename_to_fix, "r", encoding="utf-8") as file:
            lines_to_fix = file.readlines()

        with open(filename_to_fix, "w", encoding="utf-8") as file:
            text_to_write = "".join(lines_to_fix).replace(
                old_folder_name_encoded, new_folder_name_encoded
            )

            file.write(text_to_write)

print("Renaming folders done.")
print("All done. You can now import the folder \"" + FOLDER_EXTRACTION + "\" to Joplin (File > Import > MD - Markdown directory)")
