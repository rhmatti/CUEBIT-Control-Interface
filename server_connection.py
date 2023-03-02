#Import Server Tools
from data_client import BaseDataClient

DEBUG = True

import data_client
ADDR = data_client.ADDR
try:
    import socket
    on_network = str(socket.gethostbyname(socket.gethostname())).startswith('192.168.0.')
    if not on_network:
        DEBUG = True
except:
    pass

if DEBUG:
    ADDR = ("130.127.188.254", 20002)


class server_client():
    def __init__(self):
        #Establishes connection to Server
        try:
            self.client = BaseDataClient(ADDR)
            self.client.select()
        except:
            print('Error: Could not establish connection to server')

server = server_client()

values = server.client.get_all()

print(values)

U_cat = values['Cathode_Voltage_Read'][1]

#print(U_cat)