# storj_earnings
Earnings calculation script for Storj V3 storagenodes

Example:
```
January 2021 (Version: 9.5.0)                                           [snapshot: 2021-01-26 13:55:08Z]
                        TYPE            PRICE                   DISK       BANDWIDTH             PAYOUT
Upload                  Ingress         -not paid-                         155.35 GB
Upload Repair           Ingress         -not paid-                         120.98 GB
Download                Egress          $ 20.00 / TB                         1.40 TB            $ 28.09
Download Repair         Egress          $ 10.00 / TB                       288.14 GB            $  2.88
Download Audit          Egress          $ 10.00 / TB                        13.30 MB            $  0.00
Disk Current            Storage         -not paid-          14.08 TB
Disk Average Month      Storage         $  1.50 / TBm       11.72 TBm                           $ 17.58
Disk Usage              Storage         -not paid-           8.44 PBh
________________________________________________________________________________________________________+
Total                                                       11.72 TBm        1.97 TB            $ 48.55
Estimated total by end of month                             14.21 TBm        2.39 TB            $ 58.84

Payout and held amount by satellite:
                        NODE AGE         HELD AMOUNT            REPUTATION                 PAYOUT THIS MONTH
SATELLITE          Joined     Month    Perc     Total       Disq   Susp   Down        Earned        Held        Paid
us-central-1    |  2019-02-28    24  |   0%  $   1.33  |   0.00%  0.00%  0.00%  |  $  3.0475   $  0.0000   $  3.0475
    Status: OK
us2             |  2021-01-07     1  |  75%  $   0.00  |   0.00%  0.00%  0.00%  |  $  0.0000   $  0.0000   $  0.0000
    Status: OK
europe-west-1   |  2019-05-31    21  |   0%  $  20.82  |   0.00%  0.00%  0.01%  |  $  3.9514   $  0.0000   $  3.9514
    Status: OK
europe-north-1  |  2020-04-18    10  |   0%  $  47.78  |   0.00%  0.00%  0.01%  |  $ 14.3507   $  0.0000   $ 14.3507
    Status: OK
asia-east-1     |  2019-06-10    20  |   0%  $   0.34  |   0.00%  0.00%  0.00%  |  $  3.0551   $  0.0000   $  3.0551
    Status: OK
saltlake        |  2020-02-11    12  |   0%  $  69.74  |   0.00%  0.00%  0.03%  |  $ 24.1496   $  0.0000   $ 24.1496
    Status: OK
_____________________________________________________________________________________________________________________+
TOTAL                                        $ 140.01                              $ 48.5544   $  0.0000   $ 48.5544
```

## Prerequisites
Python is required to run this script.

This script was tested on Windows 10 and Linux, with Python 3.7.
Other OS's and versions will likely also work.

### Warning
If you are running Docker on Windows or MacOS, stop the node, copy the bandwidth.db, storage_usage.db, piece_spaced_used.db, reputation.db and heldamount.db to a different location and run the script from there. Running the script on docker nodes on these OS's while the node is using it could lead to corruption of the database, which will kill the node.

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
