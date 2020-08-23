# storj_earnings
Earnings calculation script for Storj V3 storagenodes

Example:
```
August 2020 (Version: 9.3.1)                                            [snapshot: 2020-08-23 08:12:15Z]
                        TYPE            PRICE                   DISK       BANDWIDTH            PAYOUT
Upload                  Ingress         -not paid-                         134.51 GB
Upload Repair           Ingress         -not paid-                         164.83 GB
Download                Egress          20   USD / TB                        1.38 TB         27.60 USD
Download Repair         Egress          10   USD / TB                      885.27 GB          8.85 USD
Download Audit          Egress          10   USD / TB                       12.16 MB          0.00 USD
Disk Current            Storage         -not paid-          12.37 TB
Disk Average Month      Storage         1.50 USD / TBm       8.77 TBm                        13.15 USD
Disk Usage              Storage         -not paid-           6.31 PBh
_______________________________________________________________________________________________________+
Total                                                        8.77 TBm        2.56 TB         49.61 USD
Estimated total by end of month                             12.16 TBm        3.56 TB         68.83 USD

Payout and held amount by satellite:
SATELLITE       MONTH   JOINED       HELD TOTAL       EARNED    HELD%            HELD           PAID
us-central-1       19   2019-02-28     1.33 USD   2.4758 USD       0%      0.0000 USD     2.4758 USD
    Status: OK >> Audit[0.0% DQ|0.0% Susp]
europe-west-1      16   2019-05-31    41.63 USD   4.9130 USD       0%      0.0000 USD     4.9130 USD
    Status: OK >> Audit[0.0% DQ|0.0% Susp]
europe-north-1      5   2020-04-18    16.70 USD  13.6719 USD      50%      6.8359 USD     6.8359 USD
    Status: OK >> Audit[0.0% DQ|0.0% Susp]
asia-east-1        15   2019-06-10     0.69 USD   2.5012 USD       0%      0.0000 USD     2.5012 USD
    Status: OK >> Audit[0.0% DQ|0.0% Susp]
saltlake            7   2020-02-11    46.46 USD  25.9605 USD      25%      6.4901 USD    19.4704 USD
    Status: OK >> Audit[0.0% DQ|0.0% Susp]
stefan-benten      18   2019-03-03    93.75 USD   0.0857 USD       0%      0.0000 USD     0.0857 USD
    Status: OK >> Audit[0.0% DQ|0.0% Susp]
_____________________________________________________________________________________________________+
TOTAL                                200.56 USD  49.6080 USD              13.3261 USD    36.2820 USD
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
