# -*- coding: utf-8 -*-
version = "9.2.0"

from calendar import monthrange
from datetime import datetime

import os
import sys
import sqlite3

audit_req = '100'

if len(sys.argv) > 3:
    sys.exit('ERROR: No more than two argument allowed. \nIf your path contains spaces use quotes. \nExample: python ' 
             + sys.argv[0] + ' "' + os.getcwd() + '"')

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
if not os.path.isfile(dbPathBW):
    sys.exit('ERROR: bandwidth.db not found at: "' + dbPath + '" or "' + configPath 
             + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' 
             + sys.argv[0] + ' "' + os.getcwd() + '"')

dbPathSU = os.path.join(dbPath,"storage_usage.db")
if not os.path.isfile(dbPathSU):
    sys.exit('ERROR: storage_usage.db not found at: "' + dbPath + '" or "' + configPath 
             + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' 
             + sys.argv[0] + ' "' + os.getcwd() + '"')

dbPathPSU = os.path.join(dbPath,"piece_spaced_used.db")
if not os.path.isfile(dbPathPSU):
    sys.exit('ERROR: piece_spaced_used.db not found at: "' + dbPath + '" or "' + configPath 
             + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' 
             + sys.argv[0] + ' "' + os.getcwd() + '"')

dbPathR = os.path.join(dbPath,"reputation.db")
if not os.path.isfile(dbPathR):
	sys.exit('ERROR: reputation.db not found at: "' + dbPath + '" or "' + configPath 
             + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' 
             + sys.argv[0] + ' "' + os.getcwd() + '"')

dbPathH = os.path.join(dbPath,"heldamount.db")
if not os.path.isfile(dbPathR):
	sys.exit('ERROR: heldamount.db not found at: "' + dbPath + '" or "' + configPath 
             + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' 
             + sys.argv[0] + ' "' + os.getcwd() + '"')

if len(sys.argv) == 3:
    try:
        mdate = datetime.strptime(sys.argv[2], '%Y-%m')
    except ValueError:
        sys.exit('ERROR: Invalid month argument. \nUse YYYY-MM as format. \nExample: python ' 
                 + sys.argv[0] + ' "' + os.getcwd() + '" "' + datetime.now().strftime('%Y-%m') + '"')
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
year_month_char = '{:04n}-{:02n}'.format(mdate.year, mdate.month)

if mdate.month == 1:
    year_month_prev_char = '{:04n}-{:02n}'.format(mdate.year - 1, 12)
else:
    year_month_prev_char = '{:04n}-{:02n}'.format(mdate.year, mdate.month - 1)
    
time_window = "interval_start >= '" + date_from.strftime("%Y-%m-%d") + "' AND interval_start < '" + date_to.strftime("%Y-%m-%d") + "'"

satellites = """
    SELECT DISTINCT satellite_id,
                       CASE hex(satellite_id)
                           WHEN 'A28B4F04E10BAE85D67F4C6CB82BF8D4C0F0F47A8EA72627524DEB6EC0000000' THEN 'us-central-1'
                           WHEN 'AF2C42003EFC826AB4361F73F9D890942146FE0EBE806786F8E7190800000000' THEN 'europe-west-1'
                           WHEN 'F474535A19DB00DB4F8071A1BE6C2551F4DED6A6E38F0818C68C68D000000000' THEN 'europe-north-1'
                           WHEN '84A74C2CD43C5BA76535E1F42F5DF7C287ED68D33522782F4AFABFDB40000000' THEN 'asia-east-1'
                           WHEN '7B2DE9D72C2E935F1918C058CAAF8ED00F0581639008707317FF1BD000000000' THEN 'saltlake'
                           WHEN '004AE89E970E703DF42BA4AB1416A3B30B7E1D8E14AA0E558F7EE26800000000' THEN 'stefan-benten'
                           ELSE '-UNKNOWN-'
                       END satellite_name,
                       CASE hex(satellite_id)
                           WHEN 'A28B4F04E10BAE85D67F4C6CB82BF8D4C0F0F47A8EA72627524DEB6EC0000000' THEN 1
                           WHEN 'AF2C42003EFC826AB4361F73F9D890942146FE0EBE806786F8E7190800000000' THEN 2
                           WHEN 'F474535A19DB00DB4F8071A1BE6C2551F4DED6A6E38F0818C68C68D000000000' THEN 3
                           WHEN '84A74C2CD43C5BA76535E1F42F5DF7C287ED68D33522782F4AFABFDB40000000' THEN 4
                           WHEN '7B2DE9D72C2E935F1918C058CAAF8ED00F0581639008707317FF1BD000000000' THEN 5
                           WHEN '004AE89E970E703DF42BA4AB1416A3B30B7E1D8E14AA0E558F7EE26800000000' THEN 6
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
    ,COALESCE(d.joined_at, '') sat_start_dt
    ,COALESCE(f.surge_percent, 100) surge_percent
    ,COALESCE(g.held_so_far, 0) held_so_far
    ,COALESCE(g.disp_so_far, 0) disp_so_far
    ,COALESCE(f.disposed, 0) disposed
    ,1+strftime('%m', date('{date_from}')) - strftime('%m', date(d.joined_at)) +
     (strftime('%Y', date('{date_from}')) - strftime('%Y', date(d.joined_at))) * 12 AS month_nr
    ,COALESCE(SUBSTR(f.pay_stat, 1, LENGTH(f.pay_stat)-2), '') AS pay_status
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
      ,CASE WHEN disqualified IS NOT NULL THEN 'Disqualified @ ' || datetime(disqualified)
            WHEN suspended IS NOT NULL THEN 'Suspended @ ' || datetime(suspended)
            WHEN audit_success_count < {audit_req} THEN 'Vetting '
            ELSE 'OK' END AS rep_status
      ,date(joined_at) as joined_at
      ,MIN(audit_success_count, {audit_req}) AS vet_count
      ,CAST(uptime_reputation_score * 1000 as INT) AS uptime_score
      ,CAST(audit_reputation_score * 1000 as INT) AS audit_score
      FROM r.reputation
    ) d
    ON x.satellite_id = d.satellite_id
    LEFT JOIN (
      SELECT
      satellite_id
      , CASE WHEN INSTR(codes, 'D') > 0 THEN 'Disqualified, '          ELSE '' END
      ||CASE WHEN INSTR(codes, 'X') > 0 THEN 'Graceful Exit, '         ELSE '' END
      ||CASE WHEN INSTR(codes, 'S') > 0 THEN 'Sanctioned Country, '    ELSE '' END
      ||CASE WHEN INSTR(codes, 'T') > 0 THEN 'Tax form 1099 missing, ' ELSE '' END AS pay_stat
      ,CASE WHEN surge_percent = 0 THEN 100 ELSE surge_percent END AS surge_percent
      ,disposed/1000000.0 disposed
      FROM h.paystubs
      WHERE period = '{year_month_char}'
    ) f
    ON x.satellite_id = f.satellite_id
    LEFT JOIN (
      SELECT
      satellite_id
      ,COUNT(period) n_months_prec
      ,MAX(period) last_period
      ,SUM(held)/1000000.0 held_so_far
      ,SUM(disposed)/1000000.0 disp_so_far
      FROM h.paystubs
      WHERE period < '{year_month_char}'
      GROUP BY satellite_id
    ) g
    ON x.satellite_id = g.satellite_id
    ORDER BY x.satellite_num;
""".format(satellites=satellites, time_window=time_window, audit_req=audit_req, year_month_char=year_month_char, 
           year_month_prev_char=year_month_prev_char, date_from=date_from.strftime("%Y-%m-%d"))

con = sqlite3.connect(dbPathBW)

tSU = (dbPathSU,)
con.execute('ATTACH DATABASE ? AS su;',tSU)

tPSU = (dbPathPSU,)
con.execute('ATTACH DATABASE ? AS psu;',tPSU)

tR = (dbPathR,)
con.execute('ATTACH DATABASE ? AS r;',tR)

tH = (dbPathH,)
con.execute('ATTACH DATABASE ? AS h;',tH)

sat_name = list()
put = list()
get = list()
get_audit = list()
get_repair = list()
put_repair = list()
disk = list()
bh = list()
bw_sum = list()

usd_get = list()
usd_get_audit = list()
usd_get_repair = list()
usd_bh = list()

surge_percent = list()

usd_sum = list()
usd_sum_surge = list()

rep_status = list()
vet_count = list()
uptime_score = list()
audit_score = list()

sat_start_dt = list()
month_nr = list()

pay_status = list()

held_so_far = list()
disp_so_far = list()

disposed = list()

held_perc = list()
paid_sum = list()
paid_sum_surge = list()
held_sum = list()
held_sum_surge = list()

hours_month = monthrange(mdate.year, mdate.month)[1] * 24
month_passed = (datetime.utcnow() - date_from).total_seconds() / (hours_month*3600)

for data in con.execute(query):
    if len(data) < 12:
        sys.exit('ERROR SQLite3: ' + data)

    #by satellite
    sat_name.append(data[0])
    put.append(int(data[1]))
    get.append(int(data[2]))
    get_audit.append(int(data[3]))
    get_repair.append(int(data[4]))
    put_repair.append(int(data[5]))
    if len(sys.argv) != 3:   
        disk.append(int(data[7]))
    else:
        disk.append(0)
    bh.append(int(data[6]))
    bw_sum.append(put[-1] + get[-1] + get_audit[-1] + get_repair[-1] + put_repair[-1])
    
    usd_get.append((20 / (1000.00**4)) * get[-1])
    usd_get_audit.append((10 / (1000.00**4)) * get_audit[-1])
    usd_get_repair.append((10 / (1000.00**4)) * get_repair[-1])
    usd_bh.append((1.5 / (1000.00**4)) * (bh[-1] / hours_month))
    
    surge_percent.append(data[13])

    usd_sum.append(usd_get[-1] + usd_get_audit[-1] + usd_get_repair[-1] + usd_bh[-1])
    usd_sum_surge.append(((usd_get[-1] + usd_get_audit[-1] + usd_get_repair[-1] + usd_bh[-1]) * surge_percent[-1]) / 100)
    
    if data[8] == 'Vetting ':
        rep_status.append(data[8] + '{:d}%'.format((100*int(data[9]))//int(audit_req)) )
    else:
        rep_status.append(data[8])
    uptime_score.append(int(data[10]))
    audit_score.append(int(data[11]))
    
    sat_start_dt.append(data[12])
    
    held_so_far.append(data[14])
    disp_so_far.append(data[15])
    
    disposed.append(data[16])
    
    month_nr.append(data[17])

    pay_status.append(data[18])

    if month_nr[-1] >= 1 and month_nr[-1] <= 3:
        held_perc.append(.75)
    elif month_nr[-1] >= 4 and month_nr[-1] <= 6:
        held_perc.append(.50)
    elif month_nr[-1] >= 7 and month_nr[-1] <= 9:
        held_perc.append(.25)
    else:
        held_perc.append(0)
    
    paid_sum.append((1-held_perc[-1])*usd_sum[-1])
    paid_sum_surge.append((paid_sum[-1] * surge_percent[-1]) / 100)
    held_sum.append(held_perc[-1]*usd_sum[-1])
    held_sum_surge.append((held_sum[-1] * surge_percent[-1]) / 100)
    
con.close()

if len(sys.argv) == 3:
    print("\033[4m\n{} (Version: {})\033[0m".format(mdate.strftime('%B %Y'), version))    
else:
    print("\033[4m\n{} (Version: {})\t\t\t\t\t\t[snapshot: {}]\033[0m".format(mdate.strftime('%B %Y'), version, mdate.strftime('%Y-%m-%d %H:%M:%SZ')))


print("\t\t\tTYPE\t\tPRICE\t\t\tDISK\t   BANDWIDTH\t\tPAYOUT")
print("Upload\t\t\tIngress\t\t-not paid-\t\t\t{}".format(formatSize(sum(put))))
print("Upload Repair\t\tIngress\t\t-not paid-\t\t\t{}".format(formatSize(sum(put_repair))))
print("Download\t\tEgress\t\t20   USD / TB\t\t\t{}\t{:10.2f} USD".format(formatSize(sum(get)), sum(usd_get)))
print("Download Repair\t\tEgress\t\t10   USD / TB\t\t\t{}\t{:10.2f} USD".format(formatSize(sum(get_repair)), sum(usd_get_repair)))
print("Download Audit\t\tEgress\t\t10   USD / TB\t\t\t{}\t{:10.2f} USD".format(formatSize(sum(get_audit)), sum(usd_get_audit)))
if year_month < 201909:
    print("\n\t\t       ** Storage usage not available prior to September 2019 **")
    print("_______________________________________________________________________________________________________+")
    print("Total\t\t\t\t\t\t\t\t\t{}\t{:10.2f} USD".format(formatSize(sum(bw_sum)), sum(usd_sum)))
else:
    if len(sys.argv) < 3:
        print("Disk Current\t\tStorage\t\t-not paid-\t{}".format(formatSize(sum(disk))))
    print("Disk Average Month\tStorage\t\t1.50 USD / TBm\t{}m\t\t\t{:10.2f} USD".format(formatSize(sum(bh) / hours_month), sum(usd_bh)))
    print("Disk Usage\t\tStorage\t\t-not paid-\t{}h".format(formatSize(sum(bh))))
    print("_______________________________________________________________________________________________________+")
    print("Total\t\t\t\t\t\t\t{}m\t{}\t{:10.2f} USD".format(formatSize(sum(bh) / hours_month), formatSize(sum(bw_sum)), sum(usd_sum)))
if len(sys.argv) < 3:
    print("Estimated total by end of month\t\t\t\t{}m\t{}\t{:10.2f} USD".format(formatSize((sum(bh) / hours_month)/month_passed), formatSize(sum(bw_sum)/month_passed), sum(usd_sum)/month_passed))
elif len(surge_percent) > 0 and sum(surge_percent)/len(surge_percent) > 100:
    print("Total Surge ({:n}%)\t\t\t\t\t\t\t\t\t{:10.2f} USD".format((sum(usd_sum_surge)*100) / sum(usd_sum), sum(usd_sum_surge)))

print("\033[4m\nPayout and held amount by satellite:\033[0m")

print("SATELLITE\tMONTH\tJOINED\t     HELD TOTAL\t      EARNED\tHELD%\t\t HELD\t        PAID")

nl = ''
for i in range(len(usd_sum)):
    print("{}{}\t{:5n}\t{} {:8.2f} USD\t{:8.4f} USD\t{:4n}%\t {:8.4f} USD\t{:8.4f} USD".format(nl,sat_name[i],month_nr[i],sat_start_dt[i],held_so_far[i]-disp_so_far[i],usd_sum[i],held_perc[i]*100,held_sum[i],paid_sum[i]))
    nl = '\n'
    if len(sys.argv) < 3:
        print("\tStatus: {} (Audit score: {})".format(rep_status[i],audit_score[i]))
        nl = ''
    if surge_percent[i] > 100:
        print("\tSURGE ({:n}%)\t\t\t\t{:8.4f} USD\t{:4n}%\t {:8.4f} USD\t{:8.4f} USD".format(surge_percent[i],usd_sum_surge[i],held_perc[i]*100,held_sum_surge[i],paid_sum_surge[i]))
        nl = ''
    
    if disposed[i] > 0:
        print("\tHELD AMOUNT RETURNED\t   {:8.2f} USD\t\t\t\t\t\t{:8.4f} USD".format(-1*disposed[i],disposed[i]))
        print("\tAFTER RETURN\t\t   {:8.2f} USD\t{:8.4f} USD\t\t {:8.4f} USD\t{:8.4f} USD".format(held_so_far[i]-(disp_so_far[i]+disposed[i]),usd_sum_surge[i],held_sum_surge[i],paid_sum_surge[i]+disposed[i]))
        nl = ''

    if len(pay_status[i]) > 0:
        print("\tPAYOUT NOTES: {}".format(pay_status[i]))
        nl = ''
    
print("_____________________________________________________________________________________________________+")
print("TOTAL\t\t\t\t   {:8.2f} USD\t{:8.4f} USD\t\t {:8.4f} USD\t{:8.4f} USD".format(sum(held_so_far)-sum(disp_so_far),sum(usd_sum),sum(held_sum),sum(paid_sum)))
if len(surge_percent) > 0 and sum(surge_percent)/len(surge_percent) > 100:
    print("\tSURGE ({:n}%)\t\t\t\t{:8.4f} USD\t\t {:8.4f} USD\t{:8.4f} USD".format((sum(usd_sum_surge)*100)/sum(usd_sum),sum(usd_sum_surge),sum(held_sum_surge),sum(paid_sum_surge)))

if sum(disposed) > 0:
    print("\tHELD AMOUNT RETURNED\t   {:8.2f} USD\t\t\t\t\t\t{:8.4f} USD".format(-1*sum(disposed),sum(disposed)))
    print("\tAFTER RETURN\t\t   {:8.2f} USD\t{:8.4f} USD\t\t {:8.4f} USD\t{:8.4f} USD".format(sum(held_so_far)-(sum(disp_so_far)+sum(disposed)),sum(usd_sum_surge),sum(held_sum_surge),sum(paid_sum_surge)+sum(disposed)))
