# Mempool
import time # Para el sleep
import subprocess # Para lanzar el comando
from sqlite3 import connect # Para interactuar con la BBDD

# El texto que queremos buscar 
substring1 = 'AcceptToMemoryPool:'
substring2 = 'replacing tx'
substring3 = 'mempoolrej'

# El fichero de log donde vamos a buscar. Acordarse de activar las opciones de debug de mempool en el fichero bitcoin.conf
logfile = open('./.bitcoin/debug.log','r')

# Con el while(true) iniciamos un loop sin salida
while(True):
    # Sin este sleep el procesador se pone al 100% todo el rato
    time.sleep(0.2)
    # Leemos linea por linea el fichero debug.log
    lines = logfile.readlines()
    for line in lines:
        # Aquí es donde debemos cambiar la fecha que queremos monitorizar, si queremos monitorizar 1 hora pondríamos '2022-12-02T09' esto monitorizaría desde las 9 de la mañana
        # del día 2 de diciembre hasta las 10 del mismo día
        if line.startswith('2022-12-02T'):
            # Comprobamos si la linea contiene 'AcceptToMemoryPool:'
            if substring1 in line:
                # Dividimos la linea en campos utilizando el espacio como separador
                line_list = line.split(' ')
                # El quinto campo es el id de la transacción
                txid = line_list[5]
                # El primer campo es la fecha/hora
                hour = line_list[0]
                # Creamos el comando a lanzar utilizando el id de la transacción
                command = 'bitcoin-cli getrawtransaction {0} 1 | jq .vin[].sequence'.format (txid.rstrip())
                # Vamos a sacar lo que nos importa de la salida del comando que no es más que el parámetro sequence para determinar si la tx está marcada como reemplazable
                try:
                    # Comprobamos la salida del comando
                    sequence = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
                    # Pasamos la variable de byte a string
                    sequence_string = str(sequence, 'UTF-8')
                    # Si no hay ningún error en la salida del comando
                    if not "error" in sequence_string:
                        # Separamos los input de la transacción (cualquier input que tenga un sequence inferior a 0xffffffff - 1 --> 4294967295 marca como reemplazable a la tx)
                        vin = sequence_string.split('\n')
                        # El comando devuelve un campo vacio al final de los input, así que lo quitamos.
                        int_vin = vin[:-1]
                        # Cambiamos el tipo a int para tratarlo como un número
                        int_vin = list(map(int, int_vin))
                        # Comprobamos si alguno de los input es menor a 4294967295
                        for x in int_vin:
                            if x < 4294967295:
                                # Si encontramos un valor menor lo asignamos a la variable sequence
                                sequence = x
                                # Salimos del for porque si un input es menor que 4294967295 la transacción ya es reemplazable
                                break
                            else:
                                # Si no guardamos el sequence que tiene que ser 4294967295 o mayor.
                                sequence = x
                # Si da error 
                except subprocess.CalledProcessError:
                    # Lo mismo me da que me da lo mismo
                    pass
                
                # Nos conectamos a la BBDD
                conn = connect('./mempool.db')
                curs = conn.cursor()
                # Agregamos los datos que hemos sacado, la hora, el id de la transacción y la secuencia.
                curs.execute("INSERT INTO Accepted (time, txid, RBF) values(?,?,?)",(hour,txid,sequence))
                conn.commit()

            # Comprobamos si la linea contiene 'replacing tx'    
            if substring2 in line:
                # Dividimos la linea en campos utilizando el espacio como separador
                line_list = line.split(' ')
                # El id de la transacción reemplazada es el cuarto campo
                origin_txid = line_list[4]
                # El ide de la transacción de reemplazo es el sexto campo
                replaced_txid = line_list[6]
                # El primer campo es la fecha/hora
                hour = line_list[0]
                # Nos conectamos a la BBDD
                conn = connect('./mempool.db')
                curs = conn.cursor()
                # Agregamos los datos que hemos sacado, la hora, el id de la transacción original y la de reemplazo.
                curs.execute("INSERT INTO Replaced (time, Original_tx, New_tx) values(?,?,?)",(hour,origin_txid,replaced_txid   ))
                conn.commit()
            
            # Comprobamos si la linea contiene 'mempoolrej'
            if substring3 in line:
                # Dividimos la linea en campos utilizando el espacio como separador
                line_list = line.split(' ')
                # El id de la transacción reemplazada es el segundo campo
                txid = line_list[2]
                # La causa es el octavo campo (esto hay que afinar)
                reason = line_list[8]
                # El primer campo es la fecha/hora
                hour = line_list[0]
                # Nos conectamos a la BBDD
                conn = connect('./mempool.db')
                curs = conn.cursor()
                # Agregamos los datos que hemos sacado, la hora, el id de la transacción rechazada y la causa
                curs.execute("INSERT INTO Rejected (time, TXID, Reason) values(?,?,?)",(hour,txid,reason))
                conn.commit()
