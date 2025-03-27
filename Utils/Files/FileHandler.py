# Auto CV Updater - automatize your CV modifications
# Copyright (C) 2025  Mariusz Matusiak <mariusz.m.matusiak@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# Utility script to handle file read/write operations.
#
# Version 1.0, 2025-03-27 - The initial version
#

import os, json

# Supports Windows, MacOS and OneDrive reserved chatecters
FILE_SYSTEM_CHARS_TO_ESCAPE = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*", ",", " ", "(", ")", "[", "]", "{", "}", "&", "#", "."]

def readFile(path: str):
    fileContent = ""
    if os.path.isfile(path):
        with open(path, "r") as file:
            fileContent = file.read()
    else:
        print(f"File {path} does not exists!")
    return fileContent

def readJsonFile(path: str):
    jsonFileContent = None
    if os.path.isfile(path):
        with open(path, "r") as file:
            jsonFileContent = json.load(file)
    else:
        print(f"File {path} does not exists!")
    return jsonFileContent

def writeFile(path: str, content: str):
    with open(path, "w") as file:
        file.write(content)

def escapeFileSystemCharacters(text: str):
    newText = text
    for ch in FILE_SYSTEM_CHARS_TO_ESCAPE:
        newText = newText.replace(ch, "_")
    return newText