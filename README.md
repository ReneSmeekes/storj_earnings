# storj_earnings
Earnings calculation script for Storj V3 storagenodes

## Prerequisites
Python and SQLite3 are required to run this script.

This script was testen on Windows 10 and Linux, with Python 2.7 and 3.7. 
Other OS's and versions will likely also work.

## Usage
Earnings for current month:
```
python earnings.py /path/to/storj/data
```
_Note: If you omit the path it will look in the current working directory._


Earnings for previous months:
```
python earnings.py /path/to/storj/data 2019-05
```
