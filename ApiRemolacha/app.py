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

def uploadThingSpeak():
	
	while True:
		#get the current timestamp
		#current date and time
		now = datetime.now()
		#date and time format: dd/mm/YYYY H:M:S
		format = "%d/%m/%Y %H:%M:%S %z%p"
		#format datetime using strftime() 
		time1 = now.strftime(format)
		 
		logging.info("Formatted DateTime:", time1)
		lockThings.acquire()
		bulk_update = {
			"write_api_key": "VMUFLH5MHCFIPJEF",
			"updates": [{
					"created_at": time1,
					"field1": state[0],
					"field2": state[1],
					"field3": state[2],
					"field4": state[3],
					"field5": state[4],
					"field6": state[5],
					"field7": state[6],
					"field8": state[7],
				}
			]
		}
		lockThings.release()
		logging.info("Envio json: " + str(bulk_update))
		x = requests.post(url, json = bulk_update)
		time.sleep(120)
		
x = threading.Thread(target=uploadThingSpeak, args=())
x.start()

def guardarEstado(state, cambio):
	lockThings.acquire()
	if "temperature" in cambio:
		state[0] = cambio["temperature"]
	if "air" in cambio:
		state[1] = cambio["air"]
	if "soil" in cambio:
		state[2] = cambio["soil"]
	if "airQuality" in cambio:
		state[3] = cambio["airQuality"]
	if "CO2" in cambio:
		state[4] = cambio["CO2"]
	if "lightEnv" in cambio:
		state[5] = cambio["lightEnv"]
	if "tempSoil" in cambio:
		state[6] = cambio["tempSoil"]
	if "Pressure" in cambio:
		state[7] = cambio["Pressure"]	
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
