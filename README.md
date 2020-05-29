# storj_earnings
Earnings calculation script for Storj V3 storagenodes

Example:
```
May 2020 (Version: 9.2.1)                                               [snapshot: 2020-05-28 18:29:31Z]
                        TYPE            PRICE                   DISK       BANDWIDTH            PAYOUT
Upload                  Ingress         -not paid-                           3.60 TB
Upload Repair           Ingress         -not paid-                         104.31 GB
Download                Egress          20   USD / TB                      987.81 GB         19.76 USD
Download Repair         Egress          10   USD / TB                      276.76 GB          2.77 USD
Download Audit          Egress          10   USD / TB                       22.15 MB          0.00 USD
Disk Current            Storage         -not paid-          11.87 TB
Disk Average Month      Storage         1.50 USD / TBm       9.99 TBm                        14.99 USD
Disk Usage              Storage         -not paid-           7.29 PBh
_______________________________________________________________________________________________________+
Total                                                        9.99 TBm        4.97 TB         37.51 USD
Estimated total by end of month                             10.94 TBm        5.44 TB         41.09 USD

Payout and held amount by satellite:
SATELLITE       MONTH   JOINED       HELD TOTAL       EARNED    HELD%            HELD           PAID
us-central-1       16   2019-02-28     2.67 USD   1.7566 USD       0%      0.0000 USD     1.7566 USD
        Status: OK (Audit score: 1000)
europe-west-1      13   2019-05-31    41.63 USD   4.3264 USD       0%      0.0000 USD     4.3264 USD
        Status: OK (Audit score: 1000)
europe-north-1      2   2020-04-18     0.01 USD   4.7772 USD      75%      3.5829 USD     1.1943 USD
        Status: OK (Audit score: 1000)
asia-east-1        12   2019-06-10     0.69 USD   1.9635 USD       0%      0.0000 USD     1.9635 USD
        Status: OK (Audit score: 1000)
saltlake            4   2020-02-11    19.48 USD  12.8026 USD      50%      6.4013 USD     6.4013 USD
        Status: OK (Audit score: 1000)
stefan-benten      15   2019-03-03   187.51 USD  11.8863 USD       0%      0.0000 USD    11.8863 USD
        Status: OK (Audit score: 1000)
_____________________________________________________________________________________________________+
TOTAL                                251.98 USD  37.5126 USD               9.9842 USD    27.5284 USD
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
