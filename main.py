# Coding Project
# Lucas Ramage
# Sept 2025

# IMPORTS
import csv
import datetime
import os
import sys
import hashlib

# cache.csv is always used to store the info
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cacheLocation = os.path.join(BASE_DIR, "Output")
os.makedirs(cacheLocation, exist_ok=True)

cacheName = os.path.join(cacheLocation, "cache.csv")


# Check for cache.csv
def Cache_Check():
    cacheFound = os.path.exists(cacheName)

    if cacheFound:  # If cache.csv exists
        firstTime = False
    else:  # If it does not exist
        firstTime = True
        with open(cacheName, "w") as cacheFile:
            cacheFile.write("Timestamp;File Path;MD5;SHA1;SHA256")
            cacheFile.write("\n")
    return firstTime


# Create first csv entries
def Create_CSV(inputDIR):
    with open(cacheName, "a+") as cacheFile:
        for path, dirs, files in os.walk(inputDIR, topdown=False):
            for name in files:
                timestamp = str(datetime.date.today())
                fileName = os.path.join(path, name)
                with open(fileName, "rb") as refFile:
                    text = refFile.read()
                    fileMD5 = hashlib.md5(text).hexdigest()
                    fileSHA1 = hashlib.sha1(text).hexdigest()
                    fileSHA256 = hashlib.sha256(text).hexdigest()

                    string = f"{timestamp};{fileName};{fileMD5};{fileSHA1};{fileSHA256}"
                    cacheFile.write(string)
                    cacheFile.write("\n")


# Load cache.csv as a dict
def Load_Cache():
    cacheDict = {}

    with open(cacheName, "r", newline="") as cache:
        reader = csv.DictReader(cache, delimiter=";")
        for row in reader:
            cacheDict[row["File Path"]] = {
                "md5": row["MD5"],
                "sha1": row["SHA1"],
                "sha256": row["SHA256"],
            }

    return cacheDict


# Read file to dict
def Read_Input(inputDIR):
    inputDict = {}

    for path, dirs, files in os.walk(inputDIR, topdown=False):
        for name in files:
            timestamp = str(datetime.date.today())
            fileName = os.path.join(path, name)
            with open(fileName, "rb") as refFile:
                text = refFile.read()
                fileMD5 = hashlib.md5(text).hexdigest()
                fileSHA1 = hashlib.sha1(text).hexdigest()
                fileSHA256 = hashlib.sha256(text).hexdigest()

            inputDict[fileName] = {
                "md5": fileMD5,
                "sha1": fileSHA1,
                "sha256": fileSHA256,
            }

    return inputDict


# Compare cache with input
def Compare_Changes(baseline, current):
    added = [f for f in current if f not in baseline]
    removed = [f for f in baseline if f not in current]
    modified = [f for f in current if f in baseline and current[f] != baseline[f]]

    return added, removed, modified


# Func to save results
def Save_Results(filename, rows, header):
    """Save rows to a CSV file if rows is not empty."""
    if not rows:
        return  # do nothing if list is empty

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        writer.writerows(rows)


# MAIN
def main():
    firstTime = Cache_Check()
    InputFolder = sys.argv[1]
    if not os.path.exists(InputFolder):
        sys.exit("Specified directory does not exist")
    if firstTime == True:
        Create_CSV(InputFolder)
        print(f"Created cache for files in {InputFolder}")
        sys.exit("Folder Cache Created")
    else:
        cacheDict = Load_Cache()
        inputDict = Read_Input(InputFolder)
        added, removed, modified = Compare_Changes(cacheDict, inputDict)

        # PRINT RESULTS - POSSIBLY ADD OUTPUT IN A DIFFERENT WAY AS WELL
        print("COMPARISON COMPLETE")
        print()

        if (
            len(added) == len(removed)
            and len(removed) == len(modified)
            and len(added) == 0
        ):
            print("No changes")
            sys.exit()

        if added:
            print("Added Files")
            for item in added:
                print(f"\t{item}")
            Save_Results(
                os.path.join(cacheLocation, "added.csv"),
                [
                    [str(datetime.date.today()), item] + list(inputDict[item].values())
                    for item in added
                ],
                ["Timestamp", "File Path", "MD5", "SHA1", "SHA256"],
            )
            print()

        if removed:
            print("Removed Files")
            for item in removed:
                print(f"\t{item}")
            Save_Results(
                os.path.join(cacheLocation, "removed.csv"),
                [
                    [str(datetime.date.today()), item] + list(cacheDict[item].values())
                    for item in removed
                ],
                ["Timestamp", "File Path", "MD5", "SHA1", "SHA256"],
            )
            print()

        if modified:
            print("Modified Files")
            for item in modified:
                print(f"\t{item}")
            Save_Results(
                os.path.join(cacheLocation, "modified.csv"),
                [
                    [str(datetime.date.today()), item] + list(inputDict[item].values())
                    for item in modified
                ],
                ["Timestamp", "File Path", "MD5", "SHA1", "SHA256"],
            )


# RUN
if __name__ == "__main__":
    main()
