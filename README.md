# storj_earnings
Earnings calculation script for Storj V3 storagenodes

## Example current month:
```
April 2022 (Version: 11.1.0)                                            [snapshot: 2022-04-14 18:11:09Z]
                        TYPE            PRICE                   DISK       BANDWIDTH             PAYOUT
Upload                  Ingress         -not paid-                         169.34 GB
Upload Repair           Ingress         -not paid-                         144.78 GB
Download                Egress          $ 20.00 / TB                       618.10 GB            $ 12.36
Download Repair         Egress          $ 10.00 / TB                       456.13 GB            $  4.56
Download Audit          Egress          $ 10.00 / TB                         4.71 MB            $  0.00
Disk Current            Storage         -not paid-          16.76 TB
Disk Average Month      Storage         $  1.50 / TBm        7.30 TBm                           $ 10.94
Disk Usage              Storage         -not paid-           5.25 PBh
________________________________________________________________________________________________________+
Total                                                        7.30 TBm        1.39 TB            $ 27.87
Estimated total by end of month                             15.91 TBm        3.03 TB            $ 60.77

Payout and held amount by satellite:
┌────────────────────────────────┬───────────────────┬─────────────────┬────────────────────────┬─────────────────────────────────────┐
│ SATELLITE                      │      NODE AGE     │   HELD AMOUNT   │        REPUTATION      │          PAYOUT THIS MONTH          │
│                                │ Joined     Month  │ Perc     Total  │    Disq   Susp   Down  │     Earned        Held      Payout  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ ap1.storj.io:7777 (OK)         │                   │                 │                        │                                     │
│                                │ 2019-06-10    35  │   0%  $   0.34  │   0.00%  0.00%  0.00%  │  $  1.8141   $  0.0000   $  1.8141  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ eu1.storj.io:7777 (OK)         │                   │                 │                        │                                     │
│                                │ 2019-05-31    36  │   0%  $  20.82  │   0.00%  0.00%  0.00%  │  $  2.4173   $  0.0000   $  2.4173  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ europe-north-1.tardigrade.io:7777 (OK)             │                 │                        │                                     │
│                                │ 2020-04-18    25  │   0%  $  23.89  │   0.00%  0.00%  0.01%  │  $  5.1215   $  0.0000   $  5.1215  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ saltlake.tardigrade.io:7777 (OK)                   │                 │                        │                                     │
│                                │ 2020-02-11    27  │   0%  $  34.87  │   0.00%  0.00%  0.00%  │  $ 15.4047   $  0.0000   $ 15.4047  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ us1.storj.io:7777 (OK)         │                   │                 │                        │                                     │
│                                │ 2019-02-28    39  │   0%  $   1.33  │   0.00%  0.00%  0.01%  │  $  3.0943   $  0.0000   $  3.0943  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ us2.storj.io:7777 (OK)         │                   │                 │                        │                                     │
│                                │ 2021-01-07    16  │   0%  $   0.09  │   0.00%  0.00%  0.00%  │  $  0.0157   $  0.0000   $  0.0157  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤ +
│ TOTAL                          │                   │       $  81.34  │                        │  $ 27.8677   $  0.0000   $ 27.8677  │
└────────────────────────────────┴───────────────────┴─────────────────┴────────────────────────┴─────────────────────────────────────┘
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

## Example previous months:
```
February 2021 (Version: 11.1.0)
                        TYPE            PRICE                   DISK       BANDWIDTH             PAYOUT
Upload                  Ingress         -not paid-                         269.83 GB
Upload Repair           Ingress         -not paid-                         130.37 GB
Download                Egress          $ 20.00 / TB                         1.45 TB            $ 28.91
Download Repair         Egress          $ 10.00 / TB                       296.18 GB            $  2.96
Download Audit          Egress          $ 10.00 / TB                        12.25 MB            $  0.00
Disk Average Month      Storage         $  1.50 / TBm       13.18 TBm                           $ 19.76
Disk Usage              Storage         -not paid-           9.49 PBh
________________________________________________________________________________________________________+
Total                                                       13.18 TBm        2.14 TB            $ 51.64

Payout and held amount by satellite:
┌────────────────────────────────┬───────────────────┬─────────────────┬────────────────────────┬─────────────────────────────────────┐
│ SATELLITE                      │      NODE AGE     │   HELD AMOUNT   │        REPUTATION      │          PAYOUT THIS MONTH          │
│                                │ Joined     Month  │ Perc     Total  │    Disq   Susp   Down  │     Earned        Held      Payout  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ ap1.storj.io:7777              │                   │                 │                        │                                     │
│                                │ 2019-06-10    21  │   0%  $   0.34  │                        │  $  3.6588   $  0.0000   $  3.6588  │
│                                │                   │                 │                        │               DIFFERENCE $ -0.0227  │
│                                │                   │                 │                        │                     PAID $  3.6361  │
│                                │                   │                 │                        │     PAID PREVIOUS MONTHS $  4.0464  │
│                                │                   │                 │                        │               PAID TOTAL $  7.6825  │
│     Transaction($  7.68):      │        https://etherscan.io/tx/******************************************************************  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ eu1.storj.io:7777              │                   │                 │                        │                                     │
│                                │ 2019-05-31    22  │   0%  $  20.82  │                        │  $  5.8577   $  0.0000   $  5.8577  │
│                                │                   │                 │                        │               DIFFERENCE $ -0.0309  │
│                                │                   │                 │                        │                     PAID $  5.8268  │
│                                │                   │                 │                        │     PAID PREVIOUS MONTHS $  4.3825  │
│                                │                   │                 │                        │               PAID TOTAL $ 10.2093  │
│     Transaction($ 10.21):      │        https://etherscan.io/tx/******************************************************************  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ europe-north-1.tardigrade.io:7777                  │                 │                        │                                     │
│                                │ 2020-04-18    11  │   0%  $  47.78  │                        │  $ 17.9284   $  0.0000   $ 17.9284  │
│                                │                   │                 │                        │               DIFFERENCE $ -0.1078  │
│                                │                   │                 │                        │                     PAID $ 17.8205  │
│                                │                   │                 │                        │     PAID PREVIOUS MONTHS $ 16.5435  │
│                                │                   │                 │                        │               PAID TOTAL $ 34.3641  │
│     Transaction($ 34.36):      │        https://etherscan.io/tx/******************************************************************  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ saltlake.tardigrade.io:7777    │                   │                 │                        │                                     │
│                                │ 2020-02-11    13  │   0%  $  69.74  │                        │  $ 21.0411   $  0.0000   $ 21.0411  │
│                                │                   │                 │                        │               DIFFERENCE $ -0.1320  │
│                                │                   │                 │                        │                     PAID $ 20.9091  │
│                                │                   │                 │                        │     PAID PREVIOUS MONTHS $ 25.7830  │
│                                │                   │                 │                        │               PAID TOTAL $ 46.6921  │
│     Transaction($ 46.69):      │        https://etherscan.io/tx/******************************************************************  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ us1.storj.io:7777              │                   │                 │                        │                                     │
│                                │ 2019-02-28    25  │   0%  $   1.33  │                        │  $  3.1512   $  0.0000   $  3.1512  │
│                                │                   │                 │                        │               DIFFERENCE $ -0.0225  │
│                                │                   │                 │                        │                     PAID $  3.1287  │
│                                │                   │                 │                        │     PAID PREVIOUS MONTHS $  4.0642  │
│                                │                   │                 │                        │               PAID TOTAL $  7.1929  │
│     Transaction($  7.19):      │        https://etherscan.io/tx/******************************************************************  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤
│ us2.storj.io:7777              │                   │                 │                        │                                     │
│                                │ 2021-01-07     2  │  75%  $   0.00  │                        │  $  0.0015   $  0.0011   $  0.0004  │
│                                │                   │                 │                        │               DIFFERENCE $ -0.0000  │
│                                │                   │                 │                        │                     PAID $  0.0004  │
│                                │                   │                 │                        │     PAID PREVIOUS MONTHS $  0.0000  │
│                                │                   │                 │                        │               PAID TOTAL $  0.0004  │
│     Transaction($  0.00):      │        https://etherscan.io/tx/******************************************************************  │
├────────────────────────────────┼───────────────────┼─────────────────┼────────────────────────┼─────────────────────────────────────┤ +
│ TOTAL                          │                   │       $ 140.01  │                        │  $ 51.6387   $  0.0011   $ 51.6375  │
│                                │                   │                 │                        │                                     │
│                                │                   │                 │                        │        PAYOUT DIFFERENCE $ -0.3159  │
│                                │                   │                 │                        │      PAID OUT THIS MONTH $ 51.3216  │
│                                │                   │                 │                        │     PAID PREVIOUS MONTHS $ 54.8196  │
│                                │                   │                 │                        │               PAID TOTAL $106.1412  │
└────────────────────────────────┴───────────────────┴─────────────────┴────────────────────────┴─────────────────────────────────────┘
```
