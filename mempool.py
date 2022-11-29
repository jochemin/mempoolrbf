# Mempool
import time
import os
from sqlite3 import connect

substring1 = 'AcceptToMemoryPool:'
substring2 = 'replacing tx'
substring3 = 'mempoolrej'
logfile = open('./.bitcoin/debug.log','r')

while(True):
    lines = logfile.readlines()
    for line in lines:
        print (line)
        if line.startswith('2022-11-29T09:5'):
            if substring1 in line:
                print(line)
                line_list = line.split(' ')
                txid = line_list[5]
                hour = line_list[0]
                command = 'bitcoin-cli getrawtransaction {0} 1 | jq .vin[0].sequence'.format (txid.rstrip())
                sequence = os.popen(command)
                sequence = int(sequence.read().strip())
                conn = connect('./mempool.db')
                curs = conn.cursor()
                curs.execute("INSERT INTO Accepted (time, txid, RBF) values(?,?,?)",(hour,txid,sequence))
                conn.commit()
            if substring2 in line:
                print(line)
                line_list = line.split(' ')
                origin_txid = line_list[4]
                replaced_txid = line_list[6]
                hour = line_list[0]
                #command = 'bitcoin-cli getrawtransaction {0} 1 | jq .vin[0].sequence'.format (replaced_txid.rstrip())
                #sequence = os.popen(command)
                #sequence = int(sequence.read().strip())
                conn = connect('./mempool.db')
                curs = conn.cursor()
                curs.execute("INSERT INTO Replaced (time, Original_tx, New_tx) values(?,?,?)",(hour,origin_txid,replaced_txid   ))
                conn.commit()
            if substring3 in line:
                print(line)
                line_list = line.split(' ')
                txid = line_list[2]
                reason = line_list[8]
                hour = line_list[0]
                #command = 'bitcoin-cli getrawtransaction {0} 1 | jq .vin[0].sequence'.format (replaced_txid.rstrip())
                #sequence = os.popen(command)
                #sequence = int(sequence.read().strip())
                conn = connect('./mempool.db')
                curs = conn.cursor()
                curs.execute("INSERT INTO Rejected (time, TXID, Reason) values(?,?,?)",(hour,txid,reason))
                conn.commit()
            time.sleep(0.2)