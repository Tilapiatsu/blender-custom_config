# Copyright (C) 2023 Elias V.
# SPDX-License-Identifier: GPL-3.0-only

import urllib.request
import json
import os
import re
import zipfile
import shutil
import re

def getLatestReleaseURL(owner, repo):
    req = urllib.request.Request("https://api.github.com/repos/{}/{}/releases"
                                 .format(owner, repo))

    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read())

        try:
            for a in data[0]["assets"]:
                if(re.search("UnwrapMe_Win_(\d|\.)+zip", a["browser_download_url"])):
                    return a["browser_download_url"]
        except:
            return None

def downloadUrl(url, targetDir):
    filename = url.split("/")[-1]

    if(not os.path.exists(targetDir)):
        os.makedirs(targetDir)

    filePath = os.path.abspath(os.path.join(targetDir, filename))

    try:
        urllib.request.urlretrieve(url, filePath)
    except:
        return None

    if(os.path.exists(filePath)):
        return filePath

    return None

def getTupleFromString(s):
    intTuple = tuple(map(int, re.findall(r'\d+', s)))

    return intTuple

def extractAndRemoveZip(filePath, targetFolder):
    with zipfile.ZipFile(filePath, 'r') as zip:
        zip.extractall(targetFolder)

    os.remove(filePath)

def moveAllFiles(fromPath, toPath):
    failCount = 0

    for f in (os.listdir(fromPath)):
        fFrom = os.path.join(fromPath, f)
        fTo = os.path.join(toPath, f)

        try:
            os.replace(fFrom, fTo)
        except:
            failCount += 1

    return failCount

def getFileCount(targetPath):
    try:
        return len(os.listdir(targetPath))
    except:
        return 0
