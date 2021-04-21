from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit
import socketio
import requests
import time
from datetime import datetime, date
import random
import time
import threading
import logging
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

#lock para dar prioridad a botones sobre sensores
lockThings = threading.Semaphore(1)

url = 'https://api.thingspeak.com/channels/1282079/bulk_update.json'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*")

state = [0,0,0,0,0,0,0,0]

normalizarTemp=50
normalizarAir=100
normalizarSoil=2000


def on_message(client, userdata, message):  # The callback\n for when a PUBLISH message is received from the server.
	print("Message received", message.payload)  # Print a received msg

def on_subscribe(client, userdata, mid, granted_qos):
	print("Se ha suscrito uno")

def on_connect(client, userdata, flags, rc):
	print("Se ha conectado uno: ", client)
	print("Connected with result code "+str(rc))

def on_disconnect(client, userdata, rc):
	print("Se ha desconectado uno: ", client)
	print("Disconnected with result code "+str(rc))


def createData(state):
	s = "{\"temperature\":" + str(state[0]) +","
	s = s + "\"air\":" + str(state[1])+","
	s = s + "\"Pressure\":" + str(state[2])+","
	s = s + "\"CO2\":" + str(state[3])+","
	s = s + "\"airQuality\":" + str(state[4])+","
	s = s + "\"lightEnv\":" + str(state[5])+","
	s = s + "\"tempSoil\":" + str(state[6])+","
	s = s + "\"soil\":" + str(state[7])+"}"
	lockThings.release()
	return s

def uploadTB():

		client = paho.Client('TBTest', clean_session=True, userdata=None, protocol=paho.MQTTv311, transport="tcp")
		tb_host = "51.178.52.254"
		tb_port = 1883
		ACCESS_TOKEN= "RGfyC21EXK8rdmyMHnke"
		client.on_message = on_message
		client.on_subscribe = on_subscribe
		client.on_connect = on_connect
		client.on_disconnect = on_disconnect
		conectado = False
		while conectado!=True:
			i = 0
			while i!=10 and conectado!=True:
				try:
					client.loop_start()
					client.connect(tb_host, tb_port, keepalive=60, bind_address="")
					client.username_pw_set(ACCESS_TOKEN)
				except:
					print("No puedo conectarme")
					i=i+1


				else:
					conectado = True
					print("Me he conectado")
			if conectado == False:
				time.sleep(1000)

		while True:
			lockThings.acquire()
			data = createData(state)
			print(data)
			client.publish("v1/devices/me/telemetry", data, 1)
			print("Mensaje enviado")
			time.sleep(10)
		
x = threading.Thread(target=uploadTB, args=())
x.start()

def guardarEstado(state, cambio):
	lockThings.acquire()
	if "temperature" in cambio:
		state[0] = cambio["temperature"]
	if "air" in cambio:
		state[1] = cambio["air"]
	if "soil" in cambio:
		state[7] = cambio["soil"]
	if "airQuality" in cambio:
		state[4] = cambio["airQuality"]
	if "CO2" in cambio:
		state[3] = cambio["CO2"]
	if "lightEnv" in cambio:
		state[5] = cambio["lightEnv"]
	if "tempSoil" in cambio:
		state[6] = cambio["tempSoil"]
	if "Pressure" in cambio:
		state[2] = cambio["Pressure"]	
	lockThings.release()

@socketio.on('connect')
def test_connect():
	logging.info("Estoy conectado")
	json = { "temperature" : 0, "soil" : 0, "air" : 0}
	emit('message', {'data':json})

@socketio.on('message')
def handle_message(message):
	logging.info(message)

@socketio.on('cambio')
def handole_event(cambio):
	enviar = False
	cambio = cambio["data"]
	update={}
	if "temperature" in cambio:
		update["temperature"] = round(cambio["temperature"]/normalizarTemp, 1)
		enviar = True
	if "air" in cambio:
		update["air"] = round(cambio["air"]/normalizarAir, 1)
		enviar = True
	if "soil" in cambio:
		update["soil"] = round(cambio["soil"]/normalizarSoil, 1)
		enviar = True
	if "light" in cambio:
		update["light"] = cambio["light"]
		enviar = True
	if "water" in cambio:
		update["water"] = cambio["water"]
		enviar = True
	if "substrate" in cambio:
		update["substrate"] = cambio["substrate"]
		enviar = True
	if "audio" in cambio:
		update["audio"] = cambio["audio"]
		enviar = True

	x = threading.Thread(target=guardarEstado, args=(state,cambio,))
	x.start()
	if enviar == True:
		logging.info(update)
		json = {"data": update}
		logging.info(json)
		emit('recibido', json, broadcast=True)

@socketio.on('recibido')
def handle_event(recibido):
	logging.info(recibido)

@socketio.on('disconnect')
def test_disconnect():
    logging.info('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)
