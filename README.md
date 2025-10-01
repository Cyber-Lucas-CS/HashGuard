# HashGuard

HashGuard is a lightweight Python-based file integrity monitoring tool. It scans a specified directory (and all subdirectories) and generates cryptographic hashes (MD5, SHA1, and SHA256) for each file. On subsequent runs, it compares the current state against a cached baseline and reports:

Added files

Removed files

Modified files

This makes HashGuard useful for detecting unauthorized changes, tampering, or suspicious activity in critical directories.

## Features

Full directory and subdirectory scanning

Baseline cache file (cache.csv) with MD5, SHA1, and SHA256 for each file

Change detection for added, removed, and modified files

Separate output reports (added.csv, removed.csv, modified.csv) generated only if changes are found

Results and cache stored in an output/ folder alongside the project

Simple command-line interface

## Usage
1. Clone the repository

`git clone https://github.com/Cyber-Lucas-CS/HashGuard.git`

`cd HashGuard`

2. Run the program

`python hashguard.py <folder_to_watch>`

Example

`python hashguard.py C:\Users\Default\Documents`


On the first run, HashGuard will create a baseline (cache.csv) in the output/ folder.

On subsequent runs, it will compare the current directory state against the baseline.

## Output

cache.csv – the baseline file integrity database

added.csv – list of new files since last scan

removed.csv – list of missing files since last scan

modified.csv – list of files that were altered since last scan

Files are only created if changes exist.

## Requirements

Python 3.7 or higher

No external libraries required

## Security Notes

HashGuard is not intended to replace enterprise-grade FIM tools like Tripwire or OSSEC.

It is designed as a lightweight, educational, and portable integrity checker.

The use of MD5 and SHA1 is for comparison and demonstration purposes. For production-grade monitoring, SHA256 or stronger algorithms should be preferred.
