#!/usr/bin/env python3
# -*- coding: utf-8 -*-
version = "13.0.1"

from calendar import monthrange
from datetime import datetime
from math import log, ceil

import os
import sys
import sqlite3

audit_req = '100'

zksync_bonus = 1.1
exponential_audit_perc = 40

dq_threshold = 0.96
suspension_threshold = 0.6

if len(sys.argv) > 3:
    sys.exit('ERROR: No more than two arguments allowed. \nIf your path contains spaces use quotes. \nExample: python ' 
             + sys.argv[0] + ' "' + os.getcwd() + '"')

if len(sys.argv) < 2:
    configPath = os.getcwd()
else:
    configPath = sys.argv[1]

if not os.path.exists(configPath):
    sys.exit('ERROR: Path does not exist: "' + configPath + '"')

if os.path.isfile(os.path.join(configPath,"satellites.db")):
    dbPath = configPath
else:
    dbPath = os.path.join(configPath,"storage")

dbPathS = os.path.join(dbPath,"satellites.db")
if not os.path.isfile(dbPathS):
    sys.exit('ERROR: satellites.db not found at: "' + dbPath + '" or "' + configPath 
             + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' 
             + sys.argv[0] + ' "' + os.getcwd() + '"')

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
if not os.path.isfile(dbPathH):
	sys.exit('ERROR: heldamount.db not found at: "' + dbPath + '" or "' + configPath 
             + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' 
             + sys.argv[0] + ' "' + os.getcwd() + '"')

dbPathP = os.path.join(dbPath,"pricing.db")
if not os.path.isfile(dbPathH):
	sys.exit('ERROR: pricing.db not found at: "' + dbPath + '" or "' + configPath 
             + '". \nEnter the correct path for your Storj config directory as a parameter. \nExample: python ' 
             + sys.argv[0] + ' "' + os.getcwd() + '"')

if len(sys.argv) == 3:
    try:
        mdate = datetime.strptime(sys.argv[2], '%Y-%m')
    except ValueError:
        sys.exit('ERROR: Invalid month argument. \nUse YYYY-MM as format. \nExample: python ' 
                 + sys.argv[0] + ' "' + os.getcwd() + '" "' + datetime.utcnow().strftime('%Y-%m') + '"')
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
    return "{:6.2f} {}".format(sizeForm, unit)

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
    SELECT DISTINCT active_sat.satellite_id,
                       CASE 
                    	   WHEN sat.address IS NOT NULL THEN sat.address
                           WHEN hex(satellite_id) = '84A74C2CD43C5BA76535E1F42F5DF7C287ED68D33522782F4AFABFDB40000000' THEN 'ap1.storj.io:7777*'
                           WHEN hex(satellite_id) = 'AF2C42003EFC826AB4361F73F9D890942146FE0EBE806786F8E7190800000000' THEN 'eu1.storj.io:7777*'
                           WHEN hex(satellite_id) = 'F474535A19DB00DB4F8071A1BE6C2551F4DED6A6E38F0818C68C68D000000000' THEN 'europe-north-1.tardigrade.io:7777*'
                           WHEN hex(satellite_id) = '7B2DE9D72C2E935F1918C058CAAF8ED00F0581639008707317FF1BD000000000' THEN 'saltlake.tardigrade.io:7777*'
                           WHEN hex(satellite_id) = 'A28B4F04E10BAE85D67F4C6CB82BF8D4C0F0F47A8EA72627524DEB6EC0000000' THEN 'us1.storj.io:7777*'
                           WHEN hex(satellite_id) = '04489F5245DED48D2A8AC8FB5F5CD1C6A638F7C6E75EFD800EF2D72000000000' THEN 'us2.storj.io:7777*'
                           WHEN hex(satellite_id) = '004AE89E970E703DF42BA4AB1416A3B30B7E1D8E14AA0E558F7EE26800000000' THEN 'satellite.stefan-benten.de:7777* (shut down)'
                           ELSE '-UNKNOWN-'
                       END satellite_name,
                       sat.added_at AS satellite_added_at
                FROM (
                   SELECT satellite_id, interval_start FROM bandwidth_usage_rollups WHERE {time_window}
                   UNION
                   SELECT satellite_id, created_at interval_start FROM bandwidth_usage WHERE {time_window}
                   UNION
                   SELECT satellite_id, timestamp interval_start FROM su.storage_usage WHERE {time_window}
                ) active_sat
                LEFT JOIN satellites sat
                ON active_sat.satellite_id = sat.node_id
                
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
    ,COALESCE(p.bh_payout,0) bh_payout
    ,COALESCE(p.get_payout,0) get_payout
    ,COALESCE(p.get_repair_payout,0) get_repair_payout
    ,COALESCE(p.get_audit_payout,0) get_audit_payout
    ,COALESCE(d.rep_status,'') rep_status
    ,COALESCE(d.vet_count,0) vet_count
    ,COALESCE(d.uptime_score,0) uptime_score
    ,COALESCE(d.audit_score,0) audit_score
    ,COALESCE(d.audit_suspension_score,0) audit_suspension_score
    ,COALESCE(d.joined_at, '') sat_start_dt
    ,COALESCE(f.surge_percent, 100) surge_percent
    ,COALESCE(g.held_so_far,0) held_so_far
    ,COALESCE(g.disp_so_far,0) disp_so_far
    ,COALESCE(g.postponed_so_far, 0) postponed_so_far
    ,COALESCE(f.disposed,0) disposed
    ,COALESCE(f.payout,0) payout
    ,COALESCE(f.paid_out,0) paid_out
    ,CASE WHEN f.payout > f.paid_out THEN f.payout - f.paid_out ELSE 0 END postponed
    ,CASE WHEN f.paid_out > f.payout THEN f.paid_out - f.payout ELSE 0 END paid_prev_month
    ,COALESCE(h.receipt, '') receipt
    ,COALESCE(h.receipt_amount,0) receipt_amount
    ,1+strftime('%m', date('{date_from}')) - strftime('%m', date(d.joined_at)) +
     (strftime('%Y', date('{date_from}')) - strftime('%Y', date(d.joined_at))) * 12 AS month_nr
    ,COALESCE(SUBSTR(f.pay_stat, 1, LENGTH(f.pay_stat)-2), '') AS pay_status
    ,COALESCE(c.seconds_bh_included,2592000) seconds_bh_included --Assume full month if NULL. This basically only happens when no storage has been reported by the satellite yet.
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
      FROM (  SELECT satellite_id,action,amount,interval_start FROM bw.bandwidth_usage_rollups
              UNION
              SELECT satellite_id,action,amount,created_at interval_start FROM bw.bandwidth_usage) a
      WHERE {time_window}
      GROUP BY satellite_id
    ) a
    ON x.satellite_id = a.satellite_id
    LEFT JOIN (
      SELECT
      satellite_id
      ,SUM(at_rest_total) bh_total
      ,strftime('%s', max(edt)) - strftime('%s', min(sdt)) seconds_bh_included
      FROM (SELECT timestamp interval_start, satellite_id, at_rest_total, interval_end_time edt,
            (SELECT interval_end_time 
             FROM su.storage_usage su2 
             WHERE su1.satellite_id = su2.satellite_id 
             AND su2.timestamp < su1.timestamp
             ORDER BY timestamp DESC
             LIMIT 1) sdt
            FROM su.storage_usage su1)
      WHERE {time_window}
      GROUP BY satellite_id
    ) c
    ON x.satellite_id = c.satellite_id
    LEFT JOIN (
      SELECT
      satellite_id
      ,CASE WHEN disqualified_at IS NOT NULL THEN 'Disqualified @ ' || datetime(disqualified_at)
            WHEN suspended_at IS NOT NULL THEN 'Suspended Audits @ ' || datetime(suspended_at)
            WHEN offline_suspended_at IS NOT NULL THEN 'Suspended Downt. @ ' || datetime(offline_suspended_at)
            WHEN offline_under_review_at IS NOT NULL THEN 'Downtime review @ ' || datetime(offline_under_review_at)
            WHEN audit_success_count < {audit_req} THEN 'Vetting '
            WHEN audit_reputation_score < 0.998 OR audit_unknown_reputation_score < 0.998 THEN 'WARN: Audits failing'
            WHEN online_score < 0.98 THEN 'WARN: Downtime high'
            ELSE 'OK' END AS rep_status
      ,date(joined_at) AS joined_at
      ,MIN(audit_success_count, {audit_req}) AS vet_count
      ,100.0*online_score AS uptime_score
      ,((1-audit_reputation_score)*100.0)/(1.0-{dq_threshold}) AS audit_score
      ,((1-audit_unknown_reputation_score)*100.0)/(1.0-{suspension_threshold}) AS audit_suspension_score
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
      ,paid/1000000.0 payout
      ,distributed/1000000.0 paid_out
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
      ,(SUM(paid)-SUM(distributed))/1000000.0 postponed_so_far
      FROM h.paystubs
      WHERE period < '{year_month_char}'
      GROUP BY satellite_id
    ) g
    ON x.satellite_id = g.satellite_id
    LEFT JOIN (
      SELECT
      satellite_id
      , CASE 
          WHEN SUBSTR(receipt, 1, 4) = 'eth:' THEN 'https://etherscan.io/tx/'||SUBSTR(receipt, 5)
          WHEN SUBSTR(receipt, 1, 7) = 'zksync:' THEN 'https://zkscan.io/explorer/transactions/'||SUBSTR(receipt, 8)
        END receipt
      , amount/1000000.0 AS receipt_amount
      FROM h.payments
      WHERE period = '{year_month_char}'
    ) h
    ON x.satellite_id = h.satellite_id
    LEFT JOIN (
      SELECT
      satellite_id
      ,disk_space_price/100.0 bh_payout
      ,egress_bandwidth_price/100.0 get_payout
      ,repair_bandwidth_price/100.0 get_repair_payout
      ,audit_bandwidth_price/100.0 get_audit_payout
      FROM p.pricing
    ) p
    ON x.satellite_id = p.satellite_id
    ORDER BY CAST(COALESCE(x.satellite_added_at, '9999-12-31') AS date), x.satellite_name;
""".format(satellites=satellites, time_window=time_window, audit_req=audit_req, year_month_char=year_month_char, 
           year_month_prev_char=year_month_prev_char, date_from=date_from.strftime("%Y-%m-%d"), 
           dq_threshold=dq_threshold, suspension_threshold=suspension_threshold)

con = sqlite3.connect(dbPathS)

tBW = (dbPathBW,)
con.execute('ATTACH DATABASE ? AS bw;',tBW)

tSU = (dbPathSU,)
con.execute('ATTACH DATABASE ? AS su;',tSU)

tPSU = (dbPathPSU,)
con.execute('ATTACH DATABASE ? AS psu;',tPSU)

tR = (dbPathR,)
con.execute('ATTACH DATABASE ? AS r;',tR)

tH = (dbPathH,)
con.execute('ATTACH DATABASE ? AS h;',tH)

tP = (dbPathP,)
con.execute('ATTACH DATABASE ? AS p;',tP)

sat_name = list()
put = list()
get = list()
get_audit = list()
get_repair = list()
put_repair = list()
disk = list()
bh = list()
bw_sum = list()

bh_payout = list()
get_payout = list()
get_repair_payout = list()
get_audit_payout = list()

usd_get = list()
usd_get_audit = list()
usd_get_repair = list()
usd_bh = list()

usd_get_surge = list()
usd_get_audit_surge = list()
usd_get_repair_surge = list()
usd_bh_surge = list()

surge_percent = list()

usd_sum = list()
usd_sum_surge = list()

rep_status = list()
vet_count = list()
uptime_score = list()
audit_score = list()
audit_suspension_score = list()

sat_start_dt = list()
month_nr = list()

pay_status = list()

held_so_far = list()
disp_so_far = list()
postponed_so_far = list()

disposed = list()
payout = list()
paid_out = list()
postponed = list()
paid_prev_month = list()

receipt = list()
receipt_amount = list()

paid_incl_bonus = list()

held_perc = list()
paid_sum = list()
paid_sum_surge = list()
held_sum = list()
held_sum_surge = list()

seconds_bh_included = list()
disk_average_so_far = list()

hours_month = 720 #Storj seems to use 720 instead of calculation
hours_this_month = monthrange(mdate.year, mdate.month)[1] * 24
month_passed = (datetime.utcnow() - date_from).total_seconds() / (hours_this_month*3600)

for data in con.execute(query):
    if len(data) < 25:
        print(data)
        sys.exit('ERROR SQLite3')

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

    bh_payout.append(data[8])
    get_payout.append(data[9])
    get_repair_payout.append(data[10])
    get_audit_payout.append(data[11])
    
    usd_get.append((get_payout[-1] / (1000.00**4)) * get[-1])
    usd_get_audit.append((get_audit_payout[-1] / (1000.00**4)) * get_audit[-1])
    usd_get_repair.append((get_repair_payout[-1] / (1000.00**4)) * get_repair[-1])
    usd_bh.append((bh_payout[-1] / (1000.00**4)) * (bh[-1] / hours_month))
    
    surge_percent.append(data[18])

    usd_get_surge.append((usd_get[-1] * surge_percent[-1]) / 100)
    usd_get_audit_surge.append((usd_get_audit[-1] * surge_percent[-1]) / 100)
    usd_get_repair_surge.append((usd_get_repair[-1] * surge_percent[-1]) / 100)
    usd_bh_surge.append((usd_bh[-1] * surge_percent[-1]) / 100)

    usd_sum.append(usd_get[-1] + usd_get_audit[-1] + usd_get_repair[-1] + usd_bh[-1])
    usd_sum_surge.append(((usd_get[-1] + usd_get_audit[-1] + usd_get_repair[-1] + usd_bh[-1]) * surge_percent[-1]) / 100)
    
    if data[12] == 'Vetting ':
        rep_status.append('{:d}% Vetted > {:d}/{:d} Audits'.format(
        	int(round(exponential_audit_perc*(log(float(data[13])+1))/log(float(audit_req)+1) + 
        	(100-exponential_audit_perc)*(float(data[13])/float(audit_req)))), int(data[13]), int(audit_req)) 
        )
    else:
        rep_status.append(data[12])
    uptime_score.append(data[14])
    audit_score.append(data[15])
    audit_suspension_score.append(data[16])
    
    sat_start_dt.append(data[17])
    
    held_so_far.append(data[19])
    disp_so_far.append(data[20])
    postponed_so_far.append(data[21])
    
    disposed.append(data[22])
    payout.append(data[23])
    paid_out.append(data[24])
    postponed.append(data[25])
    paid_prev_month.append(data[26])

    receipt.append(data[27])
    receipt_amount.append(data[28])
    
    if "https://zkscan.io/" in receipt[-1]:
    	paid_incl_bonus.append(paid_out[-1] * zksync_bonus)
    else:
    	paid_incl_bonus.append(paid_out[-1])
    
    month_nr.append(data[29])

    pay_status.append(data[30])

    seconds_bh_included.append(data[31])
    disk_average_so_far.append((bh[-1]*3600.0)/seconds_bh_included[-1])

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

if sum(get) > 0:
    avg_get_payout = sum(usd_get)/(sum(get)/1000.00**4)
else:
    avg_get_payout = sum(get_payout)/len(get_payout)
if sum(get_repair) > 0:
    avg_get_repair_payout = sum(usd_get_repair)/(sum(get_repair)/1000.00**4)
else:
    avg_get_repair_payout = sum(get_repair_payout)/len(get_repair_payout)
if sum(get_audit) > 0:
    avg_get_audit_payout = sum(usd_get_audit)/(sum(get_audit)/1000.00**4)
else:
    avg_get_audit_payout = sum(get_audit_payout)/len(get_audit_payout)
if sum(bh) > 0:
    avg_bh_payout = sum(usd_bh)/((sum(bh)/hours_month)/1000.00**4)
else:
    avg_bh_payout = sum(bh_payout)/len(bh_payout)

if len(sys.argv) == 3:
    print("\033[4m{} (Version: {})\033[0m".format(mdate.strftime('%B %Y'), version))    
else:
    print("\033[4m{} (Version: {})\t\t\t\t\t\t[snapshot: {}]\033[0m".format(mdate.strftime('%B %Y'), version, mdate.strftime('%Y-%m-%d %H:%M:%SZ')))

print("\t\t\tTYPE\t\tPRICE\t\t\t     DISK\tBANDWIDTH\t PAYOUT")
print("Upload\t\t\tIngress\t\t-not paid-\t\t\t\t{}".format(formatSize(sum(put))))
print("Upload Repair\t\tIngress\t\t-not paid-\t\t\t\t{}".format(formatSize(sum(put_repair))))
print("Download\t\tEgress\t\t${:6.2f} / TB (avg)\t\t\t{}\t${:6.2f}".format(avg_get_payout, formatSize(sum(get)), sum(usd_get)))
print("Download Repair\t\tEgress\t\t${:6.2f} / TB (avg)\t\t\t{}\t${:6.2f}".format(avg_get_repair_payout,formatSize(sum(get_repair)), sum(usd_get_repair)))
print("Download Audit\t\tEgress\t\t${:6.2f} / TB (avg)\t\t\t{}\t${:6.2f}".format(avg_get_audit_payout,formatSize(sum(get_audit)), sum(usd_get_audit)))
if year_month < 201909:
    print("\n\t\t       ** Storage usage not available prior to September 2019 **")
    print("_______________________________________________________________________________________________________+")
    print("Total\t\t\t\t\t\t\t\t\t\t{}\t${:6.2f}".format(formatSize(sum(bw_sum)), sum(usd_sum)))
else:
    if len(sys.argv) < 3:
        print("Disk Current\t\tStorage\t\t-not paid-\t\t{}".format(formatSize(sum(disk))))
        print("Disk Average So Far\tStorage\t\t-not paid-\t\t{}".format(formatSize(sum(disk_average_so_far))))
#Debug line for B*h testing
#        print("Disk Average So Far\t(debug)\t\t\t\t>> {:2.0f}% of expected {} <<".format(100*sum(disk_average_so_far)/((2*sum(disk)-(sum(put)*0.75+sum(put_repair)))/2), formatSize((2*sum(disk)-(sum(put)*0.75+sum(put_repair)))/2)))
    print("Disk Usage Month\tStorage\t\t${:6.2f} / TBm (avg)\t{}m\t\t\t${:6.2f}".format(avg_bh_payout, formatSize(sum(bh) / hours_month), sum(usd_bh)))
    print("________________________________________________________________________________________________________+")
    print("Total\t\t\t\t\t\t\t\t{}m\t{}\t${:6.2f}".format(formatSize(sum(bh) / hours_month), formatSize(sum(bw_sum)), sum(usd_sum)))
if len(sys.argv) < 3:
    print("Estimated total by end of month\t\t\t\t\t{}m\t{}\t${:6.2f}".format(formatSize(sum(disk_average_so_far)), formatSize(sum(bw_sum)/month_passed), ((sum(usd_sum)-sum(usd_bh))/month_passed) + ((1.5 / (1000.00**4)) * sum(disk_average_so_far)) ))
elif len(surge_percent) > 0 and sum(surge_percent)/len(surge_percent) > 100.000001:
    print("Total Surge ({:.0f}%)\t\t\t\t\t\t\t\t\t\t${:6.2f}".format((sum(usd_sum_surge)*100) / sum(usd_sum), sum(usd_sum_surge)))

print("\033[4m\nPayout and held amount by satellite:\033[0m")

print("┌────────────────────────────────┬─────────────┬──────────────────────────┬─────────────────────────────────────────────────────────────┐")
print("│ SATELLITE                      │ HELD AMOUNT │        REPUTATION        │                       PAYOUT THIS MONTH                     │")
print("│              Joined     Month  │      Total  │    Disq    Susp    Down  │    Storage      Egress  Repair/Aud        Held      Payout  │")
sep = "├────────────────────────────────┼─────────────┼──────────────────────────┼─────────────────────────────────────────────────────────────┤"
empty="│                                │             │                          │                                                             │"
lastl="└────────────────────────────────┴─────────────┴──────────────────────────┴─────────────────────────────────────────────────────────────┘"

def tableLine(leftstr, rightstr, indent=True, empty=empty):
    if indent:
        leftstr = "│    " + leftstr
    else:
        leftstr = "│ " + leftstr
    if len(rightstr) > 0:
        rightstr = rightstr + "  │"
    return "{}{}{}".format(leftstr, empty[len(leftstr):len(empty)-len(rightstr)],rightstr)

for i in range(len(usd_sum)):
    print(sep)
    if len(sys.argv) < 3:
        rep = "{:6.2f}% {:6.2f}% {:6.2f}%".format(audit_score[i],audit_suspension_score[i],100-uptime_score[i])
        sat = "{} ({})".format(sat_name[i],rep_status[i])
    else:
        rep = "                       "
        sat = sat_name[i]

    print(tableLine(sat,"${:6.2f}/TBm ${:6.2f}/TB  ${:6.2f}/TB      {:3.0f}%        {:3.0f}% ".format(bh_payout[i], get_payout[i], get_repair_payout[i], held_perc[i]*100, (1-held_perc[i])*100), False))
    print(tableLine("","{} {:5.0f}  │   ${:7.2f}  │ {}  │  ${:8.4f}   ${:8.4f}   ${:8.4f}  -${:8.4f}   ${:8.4f}".format(sat_start_dt[i],month_nr[i],held_so_far[i]-disp_so_far[i],rep,usd_bh[i],usd_get[i],usd_get_repair[i]+usd_get_audit[i],held_sum[i],paid_sum[i])))
#Optional line for display of data used
#    print(tableLine("","{}   {}   {}                        ".format(formatSize(bh[i] / hours_month), formatSize(get[i]), formatSize(get_repair[i]+get_audit[i]) )))
#Debug line for B*h testing
#    print("Disk Average So Far (debug): {}  >> {:2.0f}% of expected {} <<".format(formatSize(disk_average_so_far[i]), 100*disk_average_so_far[i]/((2*disk[i]-(put[i]*0.75+put_repair[i]))/2), formatSize((2*disk[i]-(put[i]*0.75+put_repair[i]))/2)))

    if surge_percent[i] > 100.000001:
        print(tableLine("SURGE ({:3.0f}%)".format(surge_percent[i]),"${:8.4f}   ${:8.4f}   ${:8.4f}  -${:8.4f}   ${:8.4f}".format(usd_bh_surge[i],usd_get_surge[i],usd_get_repair_surge[i]+usd_get_audit_surge[i],held_sum_surge[i],paid_sum_surge[i])))
    
    if disposed[i] > 0.000001:
        print(tableLine("HELD AMOUNT RETURNED        │  -${:7.2f}".format(disposed[i]), " +${:8.4f}".format(disposed[i])))
        print(tableLine("AFTER RETURN                │   ${:7.2f}".format(held_so_far[i]-(disp_so_far[i]+disposed[i])),"${:8.4f}".format(paid_sum_surge[i]+disposed[i])))

    if payout[i] > 0.000001:
        print(tableLine("","DIFFERENCE ${:8.4f}".format(payout[i]-(paid_sum_surge[i]+disposed[i]))))

    if paid_out[i] > 0.000001:
        print(tableLine("","PAID ${:8.4f}".format(paid_out[i]-paid_prev_month[i])))
    
    if paid_prev_month[i] > 0.000001:
        print(tableLine("","PAID PREVIOUS MONTHS ${:8.4f}".format(paid_prev_month[i])))
        print(tableLine("","PAID TOTAL ${:8.4f}".format(paid_out[i])))

    if (paid_incl_bonus[i] > paid_out[i] and year_month >= 202110):
	    print(tableLine("","PAID TOTAL +ZKSYNC BONUS ${:8.4f}".format(paid_incl_bonus[i])))

    if postponed[i] > 0.000001:
        print(tableLine("","PAYOUT POSTPONED ${:8.4f}".format(postponed[i])))

    if len(pay_status[i]) > 0:
        print(tableLine("PAYOUT NOTES: {}".format(pay_status[i]),""))

    if receipt[i] != "":
        print(tableLine("Transaction(${:6.2f}): {}".format(receipt_amount[i],receipt[i]), ""))


print(sep + " +")
print(tableLine("TOTAL                          │   ${:7.2f}".format(sum(held_so_far)-sum(disp_so_far)), "${:8.4f}   ${:8.4f}   ${:8.4f}  -${:8.4f}   ${:8.4f}".format(sum(usd_bh),sum(usd_get),sum(usd_get_repair)+sum(usd_get_audit),sum(held_sum),sum(paid_sum)), False ))
if len(sys.argv) < 3:
    print(tableLine("ESTIMATED END OF MONTH TOTAL   │   ${:7.2f}".format(sum(held_so_far)-sum(disp_so_far)+sum(held_sum)/month_passed), "${:8.4f}   ${:8.4f}   ${:8.4f}  -${:8.4f}   ${:8.4f}".format(sum(usd_bh)/month_passed,sum(usd_get)/month_passed,(sum(usd_get_repair)+sum(usd_get_audit))/month_passed,sum(held_sum)/month_passed,sum(paid_sum)/month_passed), False ))
if len(surge_percent) > 0.000001 and sum(surge_percent)/len(surge_percent) > 100.000001:
    print(tableLine("SURGE ({:3.0f}%)".format((sum(usd_sum_surge)*100)/sum(usd_sum)), "${:8.4f}   ${:8.4f}   ${:8.4f}  -${:8.4f}   ${:8.4f}".format(sum(usd_bh_surge),sum(usd_get_surge),sum(usd_get_repair_surge)+sum(usd_get_audit_surge),sum(held_sum_surge),sum(paid_sum_surge))))

if sum(disposed) > 0.000001:
    print(tableLine("HELD AMOUNT RETURNED        │  -${:7.2f}".format(sum(disposed)), " +${:8.4f}".format(sum(disposed))))
    print(tableLine("AFTER RETURN                │   ${:7.2f}".format(sum(held_so_far)-(sum(disp_so_far)+sum(disposed))), "${:8.4f}".format(sum(paid_sum_surge)+sum(disposed))))

if sum(payout) > 0.000001:
    print(empty + "\n" + tableLine("","PAYOUT DIFFERENCE ${:8.4f}".format(sum(payout)-(sum(paid_sum_surge)+sum(disposed)))))
if sum(paid_out) > 0.000001 and sum(postponed) > 0.000001:
    print(tableLine("","TOTAL PAYOUT THIS MONTH ${:8.4f}".format(sum(payout))))
if sum(paid_out) > 0.000001:
    print(tableLine("","PAID OUT THIS MONTH ${:8.4f}".format(sum(paid_out)-sum(paid_prev_month))))
if sum(postponed) > 0.000001:
    print(tableLine("","POSTPONED THIS MONTH ${:8.4f}".format(sum(postponed))))

if sum(paid_prev_month) > 0.000001:
    print(tableLine("","PAID PREVIOUS MONTHS ${:8.4f}".format(sum(paid_prev_month))))
    print(tableLine("","PAID TOTAL ${:8.4f}".format(sum(paid_out))))

if (sum(paid_incl_bonus) > sum(paid_out) and year_month >= 202110):
	print(tableLine("","PAID TOTAL +ZKSYNC BONUS ${:8.4f}".format(sum(paid_incl_bonus))))

if sum(postponed_so_far)-sum(paid_prev_month) > 0.000001:
    print(tableLine("","POSTPONED PAYOUT PREVIOUS MONTHS ${:8.4f}".format(sum(postponed_so_far)-sum(paid_prev_month))))
    if sum(payout)-sum(paid_out) > 0.000001:
        print(tableLine("","POSTPONED PAYOUT TOTAL ${:8.4f}".format(sum(postponed_so_far)+sum(postponed)-sum(paid_prev_month))))

print(lastl)
