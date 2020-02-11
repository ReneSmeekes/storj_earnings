# -*- coding: utf-8 -*-
version = "8.1.1"

from calendar import monthrange
from datetime import datetime

import os
import sys
import sqlite3

audit_req = '100'

if len(sys.argv) > 3:
    sys.exit('ERROR: No more than two argument allowed. \nIf your path contains spaces use quotes. \nExample: python ' + sys.argv[0] + ' "' + os.getcwd() + '"')

if len(sys.argv) < 2:
    configPath = os.getcwd()
else:
    configPath = sys.argv[1]

if not os.path.exists(configPath):
    sys.exit('ERROR: Path does not exist: "' + configPath + '"')

if os.path.isfile(os.path.join(configPath,"bandwidth.db")):
    dbPath = configPath
else:
    dbPath = os.path.join(configPath,"storage")

dbPathBW = os.path.join(dbPath,"bandwidth.db")
dbPathSU = os.path.join(dbPath,"storage_usage.db")
dbPathPSU = os.path.join(dbPath,"piece_spaced_used.db")
dbPathR = os.path.join(dbPath,"reputation.db")

if not os.path.isfile(dbPathBW):
    sys.exit('ERROR: bandwidth.db not found at: "' + dbPath + '" or "' + configPath + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' + sys.argv[0] + ' "' + os.getcwd() + '"')

if not os.path.isfile(dbPathSU):
    sys.exit('ERROR: storage_usage.db not found at: "' + dbPath + '" or "' + configPath + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' + sys.argv[0] + ' "' + os.getcwd() + '"')

if not os.path.isfile(dbPathPSU):
    sys.exit('ERROR: piece_spaced_used.db not found at: "' + dbPath + '" or "' + configPath + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' + sys.argv[0] + ' "' + os.getcwd() + '"')

if not os.path.isfile(dbPathR):
	sys.exit('ERROR: reputation.db not found at: "' + dbPath + '" or "' + configPath + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' + sys.argv[0] + ' "' + os.getcwd() + '"')

if len(sys.argv) == 3:
    try:
        mdate = datetime.strptime(sys.argv[2], '%Y-%m')
    except ValueError:
        sys.exit('ERROR: Invalid month argument. \nUse YYYY-MM as format. \nExample: python ' + sys.argv[0] + ' "' + os.getcwd() + '" "' + datetime.now().strftime('%Y-%m') + '"')
else:
    mdate = datetime.utcnow()

def formatSize(size):
    "Formats size to be displayed in the most fitting unit"
    power = (len(str(abs(int(size))))-1)//3
    units = {
            0: " B",
            1: "KB",
            2: "MB",
            3: "GB",
            4: "TB",
            5: "PB",
            6: "EB",
            7: "ZB",
            8: "YB"
        }
    unit = units.get(power)
    sizeForm = size / (1000.00**power)
    return "{:9.2f} {}".format(sizeForm, unit)

date_from = datetime(mdate.year, mdate.month, 1)
date_to = datetime(mdate.year + int(mdate.month / 12), ((mdate.month % 12) + 1), 1)
year_month = (mdate.year * 100) + mdate.month

time_window = "interval_start >= '" + date_from.strftime("%Y-%m-%d") + "' AND interval_start < '" + date_to.strftime("%Y-%m-%d") + "'"

satellites = """
    SELECT DISTINCT satellite_id,
                       CASE hex(satellite_id)
                           WHEN 'A28B4F04E10BAE85D67F4C6CB82BF8D4C0F0F47A8EA72627524DEB6EC0000000' THEN 'us-central-1'
                           WHEN 'AF2C42003EFC826AB4361F73F9D890942146FE0EBE806786F8E7190800000000' THEN 'europe-west-1'
                           WHEN '84A74C2CD43C5BA76535E1F42F5DF7C287ED68D33522782F4AFABFDB40000000' THEN 'asia-east-1'
                           WHEN '7B2DE9D72C2E935F1918C058CAAF8ED00F0581639008707317FF1BD000000000' THEN 'saltlake'
                           WHEN '004AE89E970E703DF42BA4AB1416A3B30B7E1D8E14AA0E558F7EE26800000000' THEN 'stefan-benten'
                           ELSE '-UNKNOWN-'
                       END satellite_name,
                       CASE hex(satellite_id)
                           WHEN 'A28B4F04E10BAE85D67F4C6CB82BF8D4C0F0F47A8EA72627524DEB6EC0000000' THEN 1
                           WHEN 'AF2C42003EFC826AB4361F73F9D890942146FE0EBE806786F8E7190800000000' THEN 2
                           WHEN '84A74C2CD43C5BA76535E1F42F5DF7C287ED68D33522782F4AFABFDB40000000' THEN 3
                           WHEN '7B2DE9D72C2E935F1918C058CAAF8ED00F0581639008707317FF1BD000000000' THEN 4
                           WHEN '004AE89E970E703DF42BA4AB1416A3B30B7E1D8E14AA0E558F7EE26800000000' THEN 5
                           ELSE 999
                       END satellite_num
                FROM (
                   SELECT satellite_id, interval_start FROM bandwidth_usage_rollups
                   UNION
                   SELECT satellite_id, created_at interval_start FROM bandwidth_usage
                   UNION
                   SELECT satellite_id, interval_start FROM su.storage_usage)
                WHERE {time_window}
""".format(time_window=time_window)

query = """
    SELECT x.satellite_name satellite
    ,COALESCE(a.put_total,0) put_total
    ,COALESCE(a.get_total,0) get_total
    ,COALESCE(a.get_audit_total,0) get_audit_total
    ,COALESCE(a.get_repair_total,0) get_repair_total
    ,COALESCE(a.put_repair_total,0) put_repair_total
    ,COALESCE(c.bh_total,0) bh_total
    ,COALESCE(b.total,0) disk_total
    ,COALESCE(d.rep_status,'') rep_status
    ,COALESCE(d.vet_count,0) vet_count
    ,COALESCE(d.uptime_score,0) uptime_score
    ,COALESCE(d.audit_score,0) audit_score
    ,COALESCE(sat_start_dt, '') sat_start_dt
    FROM ({satellites}) x
    LEFT JOIN 
    psu.piece_space_used b
    ON x.satellite_id = b.satellite_id
    LEFT JOIN (
      SELECT
      satellite_id
      ,SUM(CASE WHEN action = 1 THEN amount ELSE 0 END) put_total
      ,SUM(CASE WHEN action = 2 THEN amount ELSE 0 END) get_total
      ,SUM(CASE WHEN action = 3 THEN amount ELSE 0 END) get_audit_total
      ,SUM(CASE WHEN action = 4 THEN amount ELSE 0 END) get_repair_total
      ,SUM(CASE WHEN action = 5 THEN amount ELSE 0 END) put_repair_total
      FROM (  SELECT satellite_id,action,amount,interval_start FROM bandwidth_usage_rollups
              UNION
              SELECT satellite_id,action,amount,created_at interval_start FROM bandwidth_usage) a
      WHERE {time_window}
      GROUP BY satellite_id
    ) a
    ON x.satellite_id = a.satellite_id
    LEFT JOIN (
      SELECT
      satellite_id
      ,SUM(at_rest_total) bh_total
      FROM su.storage_usage
      WHERE {time_window}
      GROUP BY satellite_id
    ) c
    ON x.satellite_id = c.satellite_id
    LEFT JOIN (
      SELECT
      satellite_id
      ,CASE WHEN disqualified IS NOT NULL THEN 'Status:DQ'
            WHEN audit_success_count < {audit_req} THEN 'Vetting:'
            ELSE 'Status:OK' END AS rep_status
      ,MIN(audit_success_count, {audit_req}) AS vet_count
      ,CAST(uptime_reputation_score * 1000 as INT) AS uptime_score
      ,CAST(audit_reputation_score * 1000 as INT) AS audit_score
      FROM r.reputation
    ) d
    ON x.satellite_id = d.satellite_id
    LEFT JOIN (
      SELECT
      satellite_id
      ,strftime('%Y-%m-%d',MIN(interval_start))||
      CASE WHEN MIN(interval_start) < '2019-05-01' THEN '*' ELSE '' END AS sat_start_dt
      FROM bandwidth_usage_rollups
      GROUP BY satellite_id
    ) e
    ON x.satellite_id = e.satellite_id
    ORDER BY x.satellite_num;
""".format(satellites=satellites, time_window=time_window, audit_req=audit_req)

con = sqlite3.connect(dbPathBW)

tSU = (dbPathSU,)
con.execute('ATTACH DATABASE ? AS su;',tSU)

tPSU = (dbPathPSU,)
con.execute('ATTACH DATABASE ? AS psu;',tPSU)

tR = (dbPathR,)
con.execute('ATTACH DATABASE ? AS r;',tR)

put_total = 0
get_total = 0
get_audit_total = 0
get_repair_total = 0
put_repair_total = 0
disk_total = 0
bh_total = 0

sat_name = list()
put = list()
get = list()
get_audit = list()
get_repair = list()
put_repair = list()
disk = list()
bh = list()
sums = list()

usd_get = list()
usd_get_audit = list()
usd_get_repair = list()
usd_bh = list()
usd_sum = list()

rep_status = list()
vet_count = list()
uptime_score = list()
audit_score = list()

sat_start_dt = list()

hours_month = monthrange(mdate.year, mdate.month)[1] * 24

for data in con.execute(query):
    if len(data) < 12:
        sys.exit('ERROR SQLite3: ' + data)
    put_total = put_total + int(data[1])
    get_total = get_total + int(data[2])
    get_audit_total = get_audit_total + int(data[3])
    get_repair_total = get_repair_total + int(data[4])
    put_repair_total = put_repair_total + int(data[5])
    bh_total = bh_total + int(data[6])
    if len(sys.argv) != 3:   
        disk_total = disk_total + int(data[7])

    #by satellite
    sat_name.append(data[0])
    put.append(int(data[1]))
    get.append(int(data[2]))
    get_audit.append(int(data[3]))
    get_repair.append(int(data[4]))
    put_repair.append(int(data[5]))
    if len(sys.argv) != 3:   
        disk.append(int(data[6]))
    else:
        disk.append(0)
    bh.append(int(data[6]))
    sums.append(put[-1] + get[-1] + get_audit[-1] + get_repair[-1] + put_repair[-1])
    
    usd_get.append((20 / (1000.00**4)) * get[-1])
    usd_get_audit.append((10 / (1000.00**4)) * get_audit[-1])
    usd_get_repair.append((10 / (1000.00**4)) * get_repair[-1])
    usd_bh.append((1.5 / (1000.00**4)) * (bh[-1] / hours_month))
    usd_sum.append(usd_get[-1] + usd_get_audit[-1] + usd_get_repair[-1] + usd_bh[-1])
    
    if data[8] == 'Vetting:':
        rep_status.append(data[8] + '{:d}%'.format((100*int(data[9]))//int(audit_req)) )
    else:
        rep_status.append(data[8])
    uptime_score.append(int(data[10]))
    audit_score.append(int(data[11]))
    
    sat_start_dt.append(data[12])

sum_total = put_total + get_total + get_audit_total + get_repair_total + put_repair_total

usd_get_total = (20 / (1000.00**4)) * get_total
usd_get_audit_total = (10 / (1000.00**4)) * get_audit_total
usd_get_repair_total = (10 / (1000.00**4)) * get_repair_total
usd_bh_total = (1.5 / (1000.00**4)) * (bh_total / hours_month)

usd_sum_total = usd_get_total + usd_get_audit_total + usd_get_repair_total + usd_bh_total


if len(sys.argv) == 3:
    print("\033[4m\n{} (Version: {})\033[0m".format(mdate.strftime('%B %Y'), version))    
else:
    print("\033[4m\n{} (Version: {})\t\t\t[snapshot: {}]\033[0m".format(mdate.strftime('%B %Y'), version, mdate.strftime('%Y-%m-%d %H:%M:%SZ')))


print("\t\t\tTYPE\t\tDISK\t   BANDWIDTH\t\tPAYOUT")
print("Upload\t\t\tIngress\t\t\t{}\t    -not paid-".format(formatSize(put_total)))
print("Upload Repair\t\tIngress\t\t\t{}\t    -not paid-".format(formatSize(put_repair_total)))
print("Download\t\tEgress\t\t\t{}\t{:10.2f} USD".format(formatSize(get_total), usd_get_total))
print("Download Repair\t\tEgress\t\t\t{}\t{:10.2f} USD".format(formatSize(get_repair_total), usd_get_repair_total))
print("Download Audit\t\tEgress\t\t\t{}\t{:10.2f} USD".format(formatSize(get_audit_total), usd_get_audit_total))
if year_month < 201909:
    print("\n\t   ** Storage usage not available prior to September 2019 **")
    print("_______________________________________________________________________________+")
    print("Total\t\t\t\t\t\t{}\t{:10.2f} USD".format(formatSize(sum_total), usd_sum_total))
else:
    if len(sys.argv) < 3:
        print("Disk Current\t\tStorage\t{}\t\t\t    -not paid-".format(formatSize(disk_total)))
    print("Disk Average Month\tStorage\t{}m\t\t\t{:10.2f} USD".format(formatSize(bh_total / hours_month), usd_bh_total))
    print("Disk Usage\t\tStorage\t{}h\t\t\t    -not paid-".format(formatSize(bh_total)))
    print("_______________________________________________________________________________+")
    print("Total\t\t\t\t{}m\t{}\t{:10.2f} USD".format(formatSize(bh_total  / hours_month), formatSize(sum_total), usd_sum_total))

print("\033[4m\nPayout and escrow by satellite:\033[0m")
print("SATELLITE\tFIRST CONTACT\tTYPE\t  MONTH 1-3\t  MONTH 4-6\t  MONTH 7-9\t  MONTH 10+")
for i in range(len(usd_sum)):
    print("{}\t{}\tPayout\t{:7.4f} USD\t{:7.4f} USD\t{:7.4f} USD\t{:7.4f} USD".format(sat_name[i],sat_start_dt[i],usd_sum[i]*.25,usd_sum[i]*.5,usd_sum[i]*.75,usd_sum[i]))
    if len(sys.argv) < 3:
        print("{} (Up.{}/Aud.{})\tEscrow\t{:7.4f} USD\t{:7.4f} USD\t{:7.4f} USD\t{:7.4f} USD\n".format(rep_status[i],uptime_score[i],audit_score[i],usd_sum[i]*.75,usd_sum[i]*.5,usd_sum[i]*.25,0))
    else:
        print("\t\t\t\tEscrow\t{:7.4f} USD\t{:7.4f} USD\t{:7.4f} USD\t{:7.4f} USD\n".format(usd_sum[i]*.75,usd_sum[i]*.5,usd_sum[i]*.25,0))
if any('*' in sdat for sdat in sat_start_dt):
    print("* First contact may be earlier, nodes didn't keep contact data before April 2019")
