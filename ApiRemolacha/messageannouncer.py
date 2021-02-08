
import socketio
from flask import Flask
import random


app = Flask(__name__)

# standard Python
sio = socketio.Client()

connected = False
while not connected:
    try:
        sio.connect("http://192.168.0.171:8080")
    except socketio.exceptions.ConnectionError as err:
        print("ConnectionError: %s", err)
    else:
        connected = True

@sio.on('recibido')
def handole_event(recibido):
    print(recibido)
    print('Mensaje de cambio ha sido recibido por el servidor')
    sio.sleep(3)
    a = 0
    b = 1
    air=random.randint(a*10,b*10)/10
    soil=random.randint(a*10,b*10)/10
    temp=random.randint(a*10,b*10)/10
    json = { "temperature" : temp, "soil" : soil, "air" : air, "water" : 1, "light" : 1}
    sio.emit('cambio',  {'data': json})

@sio.on('connect')
def test_connect():
    print("Estoy conectado")
    sio.emit('preparado',  {'data':'envio'})
