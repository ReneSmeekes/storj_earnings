# storj_earnings
Earnings calculation script for Storj V3 storagenodes

## Example current month:
```
April 2024 (Version: 13.4.0)                                            [snapshot: 2024-04-14 13:50:38Z]
REPORTED BY     TYPE      METRIC                PRICE                     DISK  BANDWIDTH        PAYOUT
Node            Ingress   Upload                -not paid-                        0.00  B
Node            Ingress   Upload Repair         -not paid-                        0.00  B
Node            Egress    Download              $  2.00 / TB (avg)              126.58 GB       $  0.25
Node            Egress    Download Repair       $  2.00 / TB (avg)              110.45 GB       $  0.22
Node            Egress    Download Audit        $  2.00 / TB (avg)              116.43 MB       $  0.00
Node            Storage   Disk Current Total    -not paid-            17.23 TB
Node            Storage              ├ Blobs    -not paid-            16.56 TB
Node            Storage              └ Trash  ┐ -not paid-           671.65 GB
Node+Sat. Calc. Storage   Uncollected Garbage ┤ -not paid-           571.66 GB
Node+Sat. Calc. Storage   Total Unpaid Data <─┘ -not paid-             1.24 TB
Satellite       Storage   Disk Last Report      -not paid-            15.99 TB
Satellite       Storage   Disk Average So Far   -not paid-            16.01 TB
Satellite       Storage   Disk Usage Month      $  1.49 / TBm (avg)    7.06 TBm                 $ 10.53
________________________________________________________________________________________________________+
Total                                                                  7.06 TBm 237.15 GB       $ 11.00
Estimated total by end of month                                       16.01 TBm 524.01 GB       $ 24.91

Payout and held amount by satellite:
┌────────────────────────────────┬─────────────┬──────────────────────────┬─────────────────────────────────────────────────────────────┐
│ SATELLITE                      │ HELD AMOUNT │        REPUTATION        │                       PAYOUT THIS MONTH                     │
│              Joined     Month  │      Total  │    Disq    Susp    Down  │    Storage      Egress  Repair/Aud        Held      Payout  │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ ap1.storj.io:7777 (OK)         │             │                          │  $  1.49/TBm $  2.00/TB  $  2.00/TB        0%        100%   │
│              2019-06-10    59  │   $   0.34  │   0.00%   0.00%   0.00%  │  $  1.0431   $  0.0038   $  0.0310  -$  0.0000   $  1.0779  │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ eu1.storj.io:7777 (OK)         │             │                          │  $  1.49/TBm $  2.00/TB  $  2.00/TB        0%        100%   │
│              2019-05-31    60  │   $  20.82  │   0.00%   0.00%   0.02%  │  $  2.9840   $  0.0074   $  0.0558  -$  0.0000   $  3.0473  │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ saltlake.tardigrade.io:7777 (OK)             │                          │  $  1.49/TBm $  2.00/TB  $  2.00/TB        0%        100%   │
│              2020-02-11    51  │   $  34.87  │   0.00%   0.00%   0.01%  │  $  4.8148   $  0.0000   $  0.1142  -$  0.0000   $  4.9290  │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ us1.storj.io:7777 (OK)         │             │                          │  $  1.49/TBm $  2.00/TB  $  2.00/TB        0%        100%   │
│              2019-02-28    63  │   $   1.33  │   1.52%   0.00%   0.01%  │  $  1.6840   $  0.2419   $  0.0201  -$  0.0000   $  1.9460  │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤ +
│ TOTAL                          │   $  57.36  │                          │  $ 10.5258   $  0.2532   $  0.2211  -$  0.0000   $ 11.0001  │
│ ESTIMATED END OF MONTH TOTAL   │   $  57.36  │                          │  $ 23.8619   $  0.5594   $  0.4886  -$  0.0000   $ 24.9099  │
└────────────────────────────────┴─────────────┴──────────────────────────┴─────────────────────────────────────────────────────────────┘
```

## Prerequisites
Python 3.2 or newer is required to run this script.

This script was tested on Windows 10 and Linux, with Python 3.7.
Other OS's and versions will likely also work.

Some NAS systems may have versions of python 2 and 3 installed on the same system, try running the script with python3 instead of python. On QNAP systems you may need to install Python 3 from the store and run `/etc/profile.d/python3.bash` before running the script. For Synology it should default to python 3 if you run DSM 7 or higher.

### Warning
Never access node databases over a network connection like SMB, NFS etc. SQLite uses file locking to prevent database corruption and isn't reliable over these types of connections. So run this script locally or over iSCSI. If you want to run it on a different system anyway, stop the node and copy the satellites.db, bandwidth.db, storage_usage.db, piece_spaced_used.db, reputation.db, heldamount.db and pricing.db to your local system, and run the script from there.
If you are running Docker on Windows or MacOS, this implementation uses network storage in the backend. To use the script with such a setup, stop the node, copy the satellites.db, bandwidth.db, storage_usage.db, piece_spaced_used.db, reputation.db, heldamount.db and pricing.db to a different location and run the script from there. Running the script on docker nodes on these OS's while the node is using it could lead to corruption of the database, which will kill the node.

## Usage
Earnings for current month:
```
python earnings.py /path/to/storj/data
```
_Note: If you omit the path it will look in the current working directory._


Earnings for previous months:
```
python earnings.py /path/to/storj/data 2023-03
```

## Example previous months:
```
February 2021 (Version: 13.4.0)
REPORTED BY     TYPE      METRIC                PRICE                     DISK  BANDWIDTH        PAYOUT
Node            Ingress   Upload                -not paid-                      269.83 GB
Node            Ingress   Upload Repair         -not paid-                      130.37 GB
Node            Egress    Download              $  3.00 / TB (avg)                1.45 TB       $  4.34
Node            Egress    Download Repair       $  3.56 / TB (avg)              296.18 GB       $  1.05
Node            Egress    Download Audit        $  2.60 / TB (avg)               12.25 MB       $  0.00
Satellite       Storage   Disk Usage Month      $  1.49 / TBm (avg)   13.18 TBm                 $ 19.63
________________________________________________________________________________________________________+
Total                                                                 13.18 TBm   2.14 TB       $ 25.02

Payout and held amount by satellite:
┌────────────────────────────────┬─────────────┬──────────────────────────┬─────────────────────────────────────────────────────────────┐
│ SATELLITE                      │ HELD AMOUNT │        REPUTATION        │                       PAYOUT THIS MONTH                     │
│              Joined     Month  │      Total  │    Disq    Susp    Down  │    Storage      Egress  Repair/Aud        Held      Payout  │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ ap1.storj.io:7777              │             │                          │  $  1.49/TBm $  2.00/TB  $  2.00/TB        0%        100%   │
│              2019-06-10    21  │   $   0.34  │                          │  $  1.4123   $  0.2099   $  0.0277  -$  0.0000   $  1.6499  │
│                                │             │                          │                                       DIFFERENCE $  1.9862  │
│                                │             │                          │                                             PAID $  3.6361  │
│                                │             │                          │                             PAID PREVIOUS MONTHS $  4.0464  │
│                                │             │                          │                                       PAID TOTAL $  7.6825  │
│    Transaction($  7.68): https://etherscan.io/tx/0x################################################################                   │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ eu1.storj.io:7777              │             │                          │  $  1.49/TBm $  2.00/TB  $  2.00/TB        0%        100%   │
│              2019-05-31    22  │   $  20.82  │                          │  $  1.9266   $  0.3738   $  0.0361  -$  0.0000   $  2.3365  │
│                                │             │                          │                                       DIFFERENCE $  3.4903  │
│                                │             │                          │                                             PAID $  5.8268  │
│                                │             │                          │                             PAID PREVIOUS MONTHS $  4.3825  │
│                                │             │                          │                                       PAID TOTAL $ 10.2093  │
│    Transaction($ 10.21): https://etherscan.io/tx/0x################################################################                   │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ saltlake.tardigrade.io:7777    │             │                          │  $  1.49/TBm $  2.00/TB  $  2.00/TB        0%        100%   │
│              2020-02-11    13  │   $  69.74  │                          │  $  8.1967   $  1.1808   $  0.1963  -$  0.0000   $  9.5738  │
│                                │             │                          │                                       DIFFERENCE $ 11.3353  │
│                                │             │                          │                                             PAID $ 20.9091  │
│                                │             │                          │                             PAID PREVIOUS MONTHS $ 25.7830  │
│                                │             │                          │                                       PAID TOTAL $ 46.6921  │
│    Transaction($ 46.69): https://etherscan.io/tx/0x################################################################                   │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ us1.storj.io:7777              │             │                          │  $  1.49/TBm $  2.00/TB  $  2.00/TB        0%        100%   │
│              2019-02-28    25  │   $   1.33  │                          │  $  1.3938   $  0.1624   $  0.0247  -$  0.0000   $  1.5810  │
│                                │             │                          │                                       DIFFERENCE $  1.5478  │
│                                │             │                          │                                             PAID $  3.1287  │
│                                │             │                          │                             PAID PREVIOUS MONTHS $  4.0642  │
│                                │             │                          │                                       PAID TOTAL $  7.1929  │
│    Transaction($  7.19): https://etherscan.io/tx/0x################################################################                   │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ europe-north-1.tardigrade.io:7777*           │                          │  $  1.49/TBm $  5.00/TB  $  5.00/TB        0%        100%   │
│                             0  │   $  47.78  │                          │  $  6.7010   $  2.4110   $  0.7691  -$  0.0000   $  9.8812  │
│                                │             │                          │                                       DIFFERENCE $  7.9394  │
│                                │             │                          │                                             PAID $ 17.8205  │
│                                │             │                          │                             PAID PREVIOUS MONTHS $ 16.5435  │
│                                │             │                          │                                       PAID TOTAL $ 34.3641  │
│    Transaction($ 34.36): https://etherscan.io/tx/0x################################################################                   │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤
│ us2.storj.io:7777*             │             │                          │  $  1.49/TBm $ 10.00/TB  $ 10.00/TB        0%        100%   │
│                             0  │   $   0.00  │                          │  $  0.0003   $  0.0006   $  0.0000  -$  0.0000   $  0.0009  │
│                                │             │                          │                                       DIFFERENCE $ -0.0005  │
│                                │             │                          │                                             PAID $  0.0004  │
│                                │             │                          │                             PAID PREVIOUS MONTHS $  0.0000  │
│                                │             │                          │                                       PAID TOTAL $  0.0004  │
│    Transaction($  0.00): https://etherscan.io/tx/0x################################################################                   │
├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤ +
│ TOTAL                          │   $ 140.01  │                          │  $ 19.6308   $  4.3385   $  1.0539  -$  0.0000   $ 25.0232  │
│                                │             │                          │                                                             │
│                                │             │                          │                                PAYOUT DIFFERENCE $ 26.2984  │
│                                │             │                          │                              PAID OUT THIS MONTH $ 51.3216  │
│                                │             │                          │                             PAID PREVIOUS MONTHS $ 54.8196  │
│                                │             │                          │                                       PAID TOTAL $106.1412  │
└────────────────────────────────┴─────────────┴──────────────────────────┴─────────────────────────────────────────────────────────────┘
```
