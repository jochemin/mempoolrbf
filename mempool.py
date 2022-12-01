# Mempool
import time
import subprocess
from sqlite3 import connect

substring1 = 'AcceptToMemoryPool:'
substring2 = 'replacing tx'
substring3 = 'mempoolrej'
logfile = open('./.bitcoin/debug.log','r')

while(True):
    time.sleep(0.2)
    lines = logfile.readlines()
    for line in lines:
        #print (line)
        if line.startswith('2022-12-01T09:4'):
            if substring1 in line:
                #print(line)
                line_list = line.split(' ')
                txid = line_list[5]
                hour = line_list[0]
                command = 'bitcoin-cli getrawtransaction {0} 1 | jq .vin[].sequence'.format (txid.rstrip())
                try:
                    sequence = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                    sequence_string = str(sequence, 'UTF-8')
                    if not "error" in sequence_string:
                        vin = sequence_string.split('\n')
                        int_vin = vin[:-1]
                        int_vin = list(map(int, int_vin))
                        for x in int_vin:
                            if x < 4294967295:
                                sequence = x
                except subprocess.CalledProcessError:
                    pass
                conn = connect('./mempool.db')
                curs = conn.cursor()
                curs.execute("INSERT INTO Accepted (time, txid, RBF) values(?,?,?)",(hour,txid,sequence))
                conn.commit()
            if substring2 in line:
                #print(line)
                line_list = line.split(' ')
                origin_txid = line_list[4]
                replaced_txid = line_list[6]
                hour = line_list[0]
                conn = connect('./mempool.db')
                curs = conn.cursor()
                curs.execute("INSERT INTO Replaced (time, Original_tx, New_tx) values(?,?,?)",(hour,origin_txid,replaced_txid   ))
                conn.commit()
            if substring3 in line:
                #print(line)
                line_list = line.split(' ')
                txid = line_list[2]
                reason = line_list[8]
                hour = line_list[0]
                conn = connect('./mempool.db')
                curs = conn.cursor()
                curs.execute("INSERT INTO Rejected (time, TXID, Reason) values(?,?,?)",(hour,txid,reason))
                conn.commit()
