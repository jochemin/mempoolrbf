from sqlite3 import connect
import json
from urllib.request import urlopen

conn = connect('./mempool_confirm.db')
curs = conn.cursor()
url_start = "https://blockchain.info/tx/"
url_end = "?format=json"
for row in curs.execute('SELECT TXID from Accepted'):
    print(row[0])
    response = urlopen(url_start + row[0]+url_end)
    data_json = json.loads(response.read())
    print(row[0], ' ',data_json["block_height"])
    mined = str(data_json["block_height"])
    print(mined)
    curs.execute("UPDATE Accepted SET MINED=? WHERE txid=?",(mined, row[0]))
    #conn.commit()


conn.close()