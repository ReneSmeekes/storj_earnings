#!/usr/bin/env python3
# -*- coding: utf-8 -*-
version = "10.2.1"

from calendar import monthrange
from datetime import datetime
from math import log

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
if not os.path.isfile(dbPathH):
	sys.exit('ERROR: heldamount.db not found at: "' + dbPath + '" or "' + configPath 
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
                           WHEN 'A28B4F04E10BAE85D67F4C6CB82BF8D4C0F0F47A8EA72627524DEB6EC0000000' THEN 'us1.storj.io'
                           WHEN '04489F5245DED48D2A8AC8FB5F5CD1C6A638F7C6E75EFD800EF2D72000000000' THEN 'us2.storj.io'
                           WHEN 'AF2C42003EFC826AB4361F73F9D890942146FE0EBE806786F8E7190800000000' THEN 'eu1.storj.io'
                           WHEN '84A74C2CD43C5BA76535E1F42F5DF7C287ED68D33522782F4AFABFDB40000000' THEN 'ap1.storj.io'
                           WHEN 'F474535A19DB00DB4F8071A1BE6C2551F4DED6A6E38F0818C68C68D000000000' THEN 'europe-north-1'
                           WHEN '7B2DE9D72C2E935F1918C058CAAF8ED00F0581639008707317FF1BD000000000' THEN 'saltlake'
                           WHEN '004AE89E970E703DF42BA4AB1416A3B30B7E1D8E14AA0E558F7EE26800000000' THEN 'stefan-benten'
                           ELSE '-UNKNOWN-'
                       END satellite_name,
                       CASE hex(satellite_id)
                           WHEN 'A28B4F04E10BAE85D67F4C6CB82BF8D4C0F0F47A8EA72627524DEB6EC0000000' THEN 1
                           WHEN '04489F5245DED48D2A8AC8FB5F5CD1C6A638F7C6E75EFD800EF2D72000000000' THEN 2
                           WHEN 'AF2C42003EFC826AB4361F73F9D890942146FE0EBE806786F8E7190800000000' THEN 3
                           WHEN '84A74C2CD43C5BA76535E1F42F5DF7C287ED68D33522782F4AFABFDB40000000' THEN 4
                           WHEN 'F474535A19DB00DB4F8071A1BE6C2551F4DED6A6E38F0818C68C68D000000000' THEN 5
                           WHEN '7B2DE9D72C2E935F1918C058CAAF8ED00F0581639008707317FF1BD000000000' THEN 6
                           WHEN '004AE89E970E703DF42BA4AB1416A3B30B7E1D8E14AA0E558F7EE26800000000' THEN 7
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
    ,COALESCE(d.audit_suspension_score,0) audit_suspension_score
    ,COALESCE(d.joined_at, '') sat_start_dt
    ,COALESCE(f.surge_percent, 100) surge_percent
    ,COALESCE(g.held_so_far, 0) held_so_far
    ,COALESCE(g.disp_so_far, 0) disp_so_far
    ,COALESCE(g.postponed_so_far, 0) postponed_so_far
    ,COALESCE(f.disposed, 0) disposed
    ,COALESCE(f.payout, 0) payout
    ,COALESCE(f.paid_out, 0) paid_out
    ,CASE WHEN f.payout > f.paid_out THEN f.payout - f.paid_out ELSE 0 END postponed
    ,CASE WHEN f.paid_out > f.payout THEN f.paid_out - f.payout ELSE 0 END paid_prev_month
    ,COALESCE(h.receipt, '') receipt
    ,COALESCE(h.receipt_amount, 0) receipt_amount
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
      ,CASE WHEN disqualified_at IS NOT NULL THEN 'Audit disqualification @ ' || datetime(disqualified_at)
            WHEN suspended_at IS NOT NULL THEN 'WARNING: Audit suspension @ ' || datetime(suspended_at)
            WHEN offline_suspended_at IS NOT NULL THEN 'WARNING: Downtime suspension @ ' || datetime(offline_suspended_at)
            WHEN offline_under_review_at IS NOT NULL THEN 'WARNING: Downtime under review @ ' || datetime(offline_under_review_at)
            WHEN audit_success_count < {audit_req} THEN 'Vetting '
            WHEN audit_reputation_score < 0.98 OR audit_unknown_reputation_score < 0.98 THEN 'WARNING: Audits failing'
            WHEN online_score < 0.98 THEN 'WARNING: Downtime high'
            ELSE 'OK' END AS rep_status
      ,date(joined_at) AS joined_at
      ,MIN(audit_success_count, {audit_req}) AS vet_count
      ,100.0*online_score AS uptime_score
      ,100.0-((audit_reputation_score-0.6)/0.004) AS audit_score
      ,100.0-((audit_unknown_reputation_score-0.6)/0.004) AS audit_suspension_score
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

held_perc = list()
paid_sum = list()
paid_sum_surge = list()
held_sum = list()
held_sum_surge = list()

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
    
    usd_get.append((20 / (1000.00**4)) * get[-1])
    usd_get_audit.append((10 / (1000.00**4)) * get_audit[-1])
    usd_get_repair.append((10 / (1000.00**4)) * get_repair[-1])
    usd_bh.append((1.5 / (1000.00**4)) * (bh[-1] / hours_month))
    
    surge_percent.append(data[14])

    usd_sum.append(usd_get[-1] + usd_get_audit[-1] + usd_get_repair[-1] + usd_bh[-1])
    usd_sum_surge.append(((usd_get[-1] + usd_get_audit[-1] + usd_get_repair[-1] + usd_bh[-1]) * surge_percent[-1]) / 100)
    
    if data[8] == 'Vetting ':
        rep_status.append('{:d}% Vetting progress ({:2d} / {:d} Audits)'.format(int((100*log(float(data[9])+1))//log(float(audit_req)+1)), int(data[9]), int(audit_req)) )
    else:
        rep_status.append(data[8])
    uptime_score.append(data[10])
    audit_score.append(data[11])
    audit_suspension_score.append(data[12])
    
    sat_start_dt.append(data[13])
    
    held_so_far.append(data[15])
    disp_so_far.append(data[16])
    postponed_so_far.append(data[17])
    
    disposed.append(data[18])
    payout.append(data[19])
    paid_out.append(data[20])
    postponed.append(data[21])
    paid_prev_month.append(data[22])

    receipt.append(data[23])
    receipt_amount.append(data[24])
    
    month_nr.append(data[25])

    pay_status.append(data[26])

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
    print("\033[4m{} (Version: {})\033[0m".format(mdate.strftime('%B %Y'), version))    
else:
    print("\033[4m{} (Version: {})\t\t\t\t\t\t[snapshot: {}]\033[0m".format(mdate.strftime('%B %Y'), version, mdate.strftime('%Y-%m-%d %H:%M:%SZ')))


print("\t\t\tTYPE\t\tPRICE\t\t\tDISK\t   BANDWIDTH\t\t PAYOUT")
print("Upload\t\t\tIngress\t\t-not paid-\t\t\t{}".format(formatSize(sum(put))))
print("Upload Repair\t\tIngress\t\t-not paid-\t\t\t{}".format(formatSize(sum(put_repair))))
print("Download\t\tEgress\t\t$ 20.00 / TB\t\t\t{}\t\t${:6.2f}".format(formatSize(sum(get)), sum(usd_get)))
print("Download Repair\t\tEgress\t\t$ 10.00 / TB\t\t\t{}\t\t${:6.2f}".format(formatSize(sum(get_repair)), sum(usd_get_repair)))
print("Download Audit\t\tEgress\t\t$ 10.00 / TB\t\t\t{}\t\t${:6.2f}".format(formatSize(sum(get_audit)), sum(usd_get_audit)))
if year_month < 201909:
    print("\n\t\t       ** Storage usage not available prior to September 2019 **")
    print("________________________________________________________________________________________________________+")
    print("Total\t\t\t\t\t\t\t\t\t{}\t   ${:6.2f}".format(formatSize(sum(bw_sum)), sum(usd_sum)))
else:
    if len(sys.argv) < 3:
        print("Disk Current\t\tStorage\t\t-not paid-\t{}".format(formatSize(sum(disk))))
    print("Disk Average Month\tStorage\t\t$  1.50 / TBm\t{}m\t\t\t\t${:6.2f}".format(formatSize(sum(bh) / hours_month), sum(usd_bh)))
    print("Disk Usage\t\tStorage\t\t-not paid-\t{}h".format(formatSize(sum(bh))))
    print("________________________________________________________________________________________________________+")
    print("Total\t\t\t\t\t\t\t{}m\t{}\t\t${:6.2f}".format(formatSize(sum(bh) / hours_month), formatSize(sum(bw_sum)), sum(usd_sum)))
if len(sys.argv) < 3:
    print("Estimated total by end of month\t\t\t\t{}m\t{}\t\t${:6.2f}".format(formatSize((sum(bh) / hours_month)/month_passed), formatSize(sum(bw_sum)/month_passed), sum(usd_sum)/month_passed))
elif len(surge_percent) > 0 and sum(surge_percent)/len(surge_percent) > 100.00001:
    print("Total Surge ({:.0f}%)\t\t\t\t\t\t\t\t\t\t${:6.2f}".format((sum(usd_sum_surge)*100) / sum(usd_sum), sum(usd_sum_surge)))

print("\033[4m\nPayout and held amount by satellite:\033[0m")

print("                        NODE AGE         HELD AMOUNT            REPUTATION                 PAYOUT THIS MONTH")
print("SATELLITE          Joined     Month    Perc     Total       Disq   Susp   Down        Earned        Held      Payout")

nl = ''

for i in range(len(usd_sum)):
    if len(sys.argv) < 3:
        rep = "{:6.2f}%{:6.2f}%{:6.2f}%".format(audit_score[i],audit_suspension_score[i],100-uptime_score[i])
    else:
        rep = "                     "
    print("{}{}\t|  {} {:5.0f}  |  {:2.0f}%  ${:7.2f}  | {}  |  ${:8.4f}   ${:8.4f}   ${:8.4f}".format(nl,sat_name[i],sat_start_dt[i],month_nr[i],held_perc[i]*100,held_so_far[i]-disp_so_far[i],rep,usd_sum[i],held_sum[i],paid_sum[i]))
    nl = '\n'
    if len(sys.argv) < 3:
        print("    Status: {}".format(rep_status[i]))
        nl = ''

    if len(pay_status[i]) > 0.00001:
        print("    PAYOUT NOTES: {}".format(pay_status[i]))

    if surge_percent[i] > 100.00001:
        print("    SURGE ({:3.0f}%)\t\t\t\t\t\t\t\t   ${:8.4f}   ${:8.4f}   ${:8.4f}".format(surge_percent[i],usd_sum_surge[i],held_sum_surge[i],paid_sum_surge[i]))
    
    if disposed[i] > 0.00001:
        print("    HELD AMOUNT RETURNED\t\t   - ${:7.2f}\t\t\t\t\t\t\t + ${:8.4f}".format(disposed[i],disposed[i]))
        print("    AFTER RETURN\t\t\t     ${:7.2f}\t\t\t\t\t\t\t   ${:8.4f}".format(held_so_far[i]-(disp_so_far[i]+disposed[i]),paid_sum_surge[i]+disposed[i]))

    if payout[i] > 0.00001:
        print("\t\t\t\t\t\t\t\t\t\t\t\tDIFFERENCE ${:8.4f}".format(payout[i]-(paid_sum_surge[i]+disposed[i])))

    if paid_out[i] > 0.00001:
        print("\t\t\t\t\t\t\t\t\t\t\t\t      PAID ${:8.4f}".format(paid_out[i]-paid_prev_month[i]))
    
    if paid_prev_month[i] > 0.00001:
        print("\t\t\t\t\t\t\t\t\t\t      PAID PREVIOUS MONTHS ${:8.4f}".format(paid_prev_month[i]))
        print("\t\t\t\t\t\t\t\t\t\t\t\tPAID TOTAL ${:8.4f}".format(paid_out[i]))

    if postponed[i] > 0.00001:
        print("\t\t\t\t\t\t\t\t\t\t\t  PAYOUT POSTPONED ${:8.4f}".format(postponed[i]))

    if receipt[i] != "":
        print("    Transaction(${:6.2f}): {}".format(receipt_amount[i], receipt[i]))

   
print("_____________________________________________________________________________________________________________________+")
print("TOTAL\t\t\t\t\t     ${:7.2f}                              ${:8.4f}   ${:8.4f}   ${:8.4f}".format(sum(held_so_far)-sum(disp_so_far),sum(usd_sum),sum(held_sum),sum(paid_sum)))
if len(surge_percent) > 0.00001 and sum(surge_percent)/len(surge_percent) > 100.00001:
    print("    SURGE ({:3.0f}%)\t\t\t\t\t\t\t\t   ${:8.4f}   ${:8.4f}   ${:8.4f}".format((sum(usd_sum_surge)*100)/sum(usd_sum),sum(usd_sum_surge),sum(held_sum_surge),sum(paid_sum_surge)))

if sum(disposed) > 0.00001:
    print("    HELD AMOUNT RETURNED\t\t   - ${:7.2f}\t\t\t\t\t\t\t + ${:8.4f}".format(sum(disposed),sum(disposed)))
    print("    AFTER RETURN\t\t\t     ${:7.2f}\t\t\t\t\t\t\t   ${:8.4f}".format(sum(held_so_far)-(sum(disp_so_far)+sum(disposed)),sum(paid_sum_surge)+sum(disposed)))

if sum(payout) > 0.00001:
    print("\n\t\t\t\t\t\t\t\t\t\t\t PAYOUT DIFFERENCE ${:8.4f}".format(sum(payout)-(sum(paid_sum_surge)+sum(disposed))))
if sum(paid_out) > 0.00001 and sum(postponed) > 0.00001:
    print("\t\t\t\t\t\t\t\t\t\t   TOTAL PAYOUT THIS MONTH ${:8.4f}".format(sum(payout)))
if sum(paid_out) > 0.00001:
    print("\t\t\t\t\t\t\t\t\t\t       PAID OUT THIS MONTH ${:8.4f}".format(sum(paid_out)-sum(paid_prev_month)))
if sum(postponed) > 0.00001:
    print("\t\t\t\t\t\t\t\t\t       POSTPONED PAYOUT THIS MONTH ${:8.4f}".format(sum(postponed)))

if sum(paid_prev_month) > 0.00001:
    print("\n\t\t\t\t\t\t\t\t\t\t      PAID PREVIOUS MONTHS ${:8.4f}".format(sum(paid_prev_month)))
    print("\t\t\t\t\t\t\t\t\t\t\t\tPAID TOTAL ${:8.4f}".format(sum(paid_out)))

if sum(postponed_so_far)-sum(paid_prev_month) > 0.00001:
    print("\n\t\t\t\t\t\t\t\t\t  POSTPONED PAYOUT PREVIOUS MONTHS ${:8.4f}".format(sum(postponed_so_far)-sum(paid_prev_month)))
    if sum(payout)-sum(paid_out) > 0.00001:
        print("\t\t\t\t\t\t\t\t\t            POSTPONED PAYOUT TOTAL ${:8.4f}".format(sum(postponed_so_far)+sum(postponed)-sum(paid_prev_month)))
