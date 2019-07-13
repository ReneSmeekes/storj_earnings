# storj_earnings
Earnings calculation script for Storj V3 storagenodes

## Prerequisites
Python and SQLite3 are required to run this script.

This script was tested on Windows 10 and Linux, with Python 2.7 and 3.7. 
Other OS's and versions will likely also work.

### Warning
Especially if you are running on Windows or MacOS, stop the node, copy the info.db to a different location and run the script from there. Running the script on these OS's while the node is using it could lead to corruption of the database, which will kill the node. This approach is best practice on Linux as well.

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
