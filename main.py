# HashGuard
# A lightweight file integrity tool in Python
# Copyright (C) 2025  Lucas Ramage

# IMPORTS
import csv
import datetime
import os
import sys
import hashlib

# cache.csv is always used to store the info
# Load the current directory and make an output folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cacheLocation = os.path.join(BASE_DIR, "Output")
os.makedirs(cacheLocation, exist_ok=True)

cacheName = os.path.join(cacheLocation, "cache.csv")


# Check for cache.csv
def Cache_Check():
    cacheFound = os.path.exists(cacheName)

    if cacheFound:  # If cache.csv exists, then we do not need to make it
        firstTime = False
    else:  # If it does not exist, then we make it and write the header row.
        firstTime = True
        with open(cacheName, "w") as cacheFile:
            cacheFile.write("Timestamp;File Path;MD5;SHA1;SHA256")
            cacheFile.write("\n")
    return firstTime


# Create first csv entries
def Create_CSV(inputDIR):
    with open(cacheName, "a+") as cacheFile:
        # Walk through all files in the directory, including subdirectories
        for path, dirs, files in os.walk(inputDIR, topdown=False):
            for name in files:
                timestamp = str(datetime.datetime.now().isoformat())
                fileName = os.path.join(path, name)
                # Generate hashes for the file
                with open(fileName, "rb") as refFile:
                    text = refFile.read()
                    fileMD5 = hashlib.md5(text).hexdigest()
                    fileSHA1 = hashlib.sha1(text).hexdigest()
                    fileSHA256 = hashlib.sha256(text).hexdigest()
                    # Store timestamp, filename, and the hashes to the cache file
                    string = f"{timestamp};{fileName};{fileMD5};{fileSHA1};{fileSHA256}"
                    cacheFile.write(string)
                    cacheFile.write("\n")


# Load cache.csv as a dict
def Load_Cache():
    cacheDict = {}
    # Read through the cache file and load the csv info into a dictionary.
    with open(cacheName, "r", newline="") as cache:
        reader = csv.DictReader(cache, delimiter=";")
        # The information is keyed by filename, and is stored as a dicitonary itself.
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
    # This does the same as Load_Cache(), but directly from a file.
    # It goes through each file in the directory, just like when creating the cache
    for path, dirs, files in os.walk(inputDIR, topdown=False):
        for name in files:
            timestamp = str(datetime.datetime.now().isoformat())
            fileName = os.path.join(path, name)
            with open(fileName, "rb") as refFile:
                # Calculate all of the hashes
                text = refFile.read()
                fileMD5 = hashlib.md5(text).hexdigest()
                fileSHA1 = hashlib.sha1(text).hexdigest()
                fileSHA256 = hashlib.sha256(text).hexdigest()
            # Store the hashes in a dictionary identically to the Load_Cache() function.
            inputDict[fileName] = {
                "md5": fileMD5,
                "sha1": fileSHA1,
                "sha256": fileSHA256,
            }

    return inputDict


# Compare cache with input
def Compare_Changes(baseline, current):
    # Creates lists based on logical operations on the cache dictionary and the input dictionary.
    # Any file that is not in the cache but is in the input is considered "added"
    added = [f for f in current if f not in baseline]
    # Any file that is in the cache but is not in the input is considered "removed"
    removed = [f for f in baseline if f not in current]
    # Any changes, which will result in changes to all of the file hashes, will be detected here, and any changed file is considered "modified"
    modified = [f for f in current if f in baseline and current[f] != baseline[f]]
    # As an aside, if a file name is changed, the old file name will be considered "removed" and the new file name will be considered "added", instead of the whole thing being considered "modified"
    # This is expected behavior, and is how most comemrcial file integrity monitors handle the situation.

    return added, removed, modified


# Func to save results
def Save_Results(filename, rows, header):
    # Save rows to a CSV file if rows is not empty.
    if not rows:
        return  # do nothing if list is empty

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)
        writer.writerows(rows)


# MAIN
def main():
    # Perform a check to see if the cache already exists
    firstTime = Cache_Check()
    # Check for proper command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python hashguard.py <directory>")
    # Load input folder from command-line argument, exiting if it is an invalid target.
    InputFolder = sys.argv[1]
    if not os.path.exists(InputFolder):
        sys.exit("Specified directory does not exist")
    # if there is no cache, it creates the cache and exits.
    if firstTime == True:
        Create_CSV(InputFolder)
        print(f"Created cache for files in {InputFolder}")
        sys.exit("Folder Cache Created")
    # If there is a cache, continue with execution.
    else:
        # Load the cache and input to a dictionary, then compare.
        cacheDict = Load_Cache()
        inputDict = Read_Input(InputFolder)
        added, removed, modified = Compare_Changes(cacheDict, inputDict)

        # PRINT RESULTS AND SAVE TO CSV FILES
        print("COMPARISON COMPLETE")
        print()

        # Display for if there are no changes, detected by checking if the length of added, removed, and modified are the same, and if the length of added is 0.
        if (
            len(added) == len(removed)
            and len(removed) == len(modified)
            and len(added) == 0
        ):
            print("No changes")
            sys.exit()

        # If there are any files added, display them to the console and save them to a CSV file.
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

        # If there are any files removed, display them to the console and save them to a CSV file.
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

        # If there are any modified files, display them to the console and save them to a csv file
        # POTENTIALLY MAKE IT SO THAT THE CSV STORES BASELINE AND CURRENT HASHES
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
