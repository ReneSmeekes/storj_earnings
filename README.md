# storj_earnings
Earnings calculation script for Storj V3 storagenodes

Example:
```
February 2021 (Version: 10.0.0)                                         [snapshot: 2021-02-19 16:10:40Z]
                        TYPE            PRICE                   DISK       BANDWIDTH             PAYOUT
Upload                  Ingress         -not paid-                          93.23 GB
Upload Repair           Ingress         -not paid-                          90.81 GB
Download                Egress          $ 20.00 / TB                       977.52 GB            $ 19.55
Download Repair         Egress          $ 10.00 / TB                       175.74 GB            $  1.76
Download Audit          Egress          $ 10.00 / TB                         8.73 MB            $  0.00
Disk Current            Storage         -not paid-          14.18 TB
Disk Average Month      Storage         $  1.50 / TBm        8.72 TBm                           $ 13.08
Disk Usage              Storage         -not paid-           6.28 PBh
________________________________________________________________________________________________________+
Total                                                        8.72 TBm        1.34 TB            $ 34.38
Estimated total by end of month                             13.07 TBm        2.01 TB            $ 51.55

Payout and held amount by satellite:
                        NODE AGE         HELD AMOUNT            REPUTATION                 PAYOUT THIS MONTH
SATELLITE          Joined     Month    Perc     Total       Disq   Susp   Down        Earned        Held      Payout
us-central-1    |  2019-02-28    25  |   0%  $   1.33  |   0.00%  0.00%  0.06%  |  $  2.6229   $  0.0000   $  2.6229
    Status: OK
us2             |  2021-01-07     2  |  75%  $   0.00  |   0.00%  0.00%  0.00%  |  $  0.0000   $  0.0000   $  0.0000
    Status: OK
europe-west-1   |  2019-05-31    22  |   0%  $  20.82  |   0.00%  0.00%  0.05%  |  $  3.2402   $  0.0000   $  3.2402
    Status: OK
europe-north-1  |  2020-04-18    11  |   0%  $  47.78  |   0.00%  0.00%  0.07%  |  $ 11.9320   $  0.0000   $ 11.9320
    Status: OK
asia-east-1     |  2019-06-10    21  |   0%  $   0.34  |   0.00%  0.00%  0.03%  |  $  2.7076   $  0.0000   $  2.7076
    Status: OK
saltlake        |  2020-02-11    13  |   0%  $  69.74  |   0.00%  0.00%  0.06%  |  $ 13.8802   $  0.0000   $ 13.8802
    Status: OK
_____________________________________________________________________________________________________________________+
TOTAL                                        $ 140.01                              $ 34.3829   $  0.0000   $ 34.3829

                                                                          POSTPONED PAYOUT PREVIOUS MONTHS $ 54.8196
```

## Prerequisites
Python is required to run this script.

This script was tested on Windows 10 and Linux, with Python 3.7.
Other OS's and versions will likely also work.

### Warning
If you are running Docker on Windows or MacOS, stop the node, copy the bandwidth.db, storage_usage.db, piece_spaced_used.db, reputation.db and heldamount.db to a different location and run the script from there. Running the script on docker nodes on these OS's while the node is using it could lead to corruption of the database, which will kill the node.

## CLI Usage
Earnings for current month:
```
python earnings.py /path/to/storj/data
```
_Note: If you omit the path it will look in the current working directory._


Earnings for previous months:
```
python earnings.py /path/to/storj/data 2019-05
```

## Windows launcher
Create a folder.
Copy [earnings.py](https://github.com/ReneSmeekes/storj_earnings/blob/master/earnings.py) and [windows_launcher.bat](https://github.com/ReneSmeekes/storj_earnings/blob/master/windows_launcher.bat) files into it.
modify this line to add storj data path.
```
python "%~dp0\earnings.py" "\path\to\storj\data"
```
launch windows_launcher.bat
