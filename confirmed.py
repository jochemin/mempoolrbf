from sqlite3 import connect
import subprocess

conn = connect('./mempool_fullrbf.db')
# necesitamos 2 cursores a la bbdd para no salir del for
curs1 = conn.cursor()
curs2 = conn.cursor()

for row in curs1.execute('SELECT TXID from Accepted'):
    #print(row[0])
    command = 'bitcoin-cli getrawtransaction {0} 1 | jq .confirmations'.format (row[0])
    try:
        # Comprobamos la salida del comando
        confirmations = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        # Pasamos la variable de byte a string
        confirmations_string = str(confirmations, 'UTF-8')
        # Quitamos los espacios
        confirmations_string = confirmations_string.strip()
        # Si no hay ningún error en la salida del comando
        if not "error" in confirmations_string:
            # Cambiamos el tipo a int para tratarlo como un número
            #print(confirmations_string)
            int_confirmations = int(confirmations_string)
            if int_confirmations > 0:
                # Si encontramos un valor menor lo asignamos a la variable sequence
                confirmed = 1
                curs2.execute("UPDATE Accepted SET Mined=? WHERE txid=?",(confirmed, row[0]))
                conn.commit()
                print ("La transacción "+row[0]+" está confirmada")
        else:
            print ("La transacción "+row[0]+" no está confirmada")
    except subprocess.CalledProcessError:
        # Lo mismo me da que me da lo mismo
        pass
conn.close()