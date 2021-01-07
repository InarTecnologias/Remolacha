from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def test_connect():
	print("Estoy conectado")
	json = { "temperature" : 0.5, "soil" : 0.5, "air" : 0.5}
	emit('message', {'data':json})
	
@socketio.on('message')
def handle_message(message):
	print(message)

@socketio.on('preparado')
def handle_message(preparado):
	print(preparado)
	emit('recibido', {'data':'dame los datos'})


@socketio.on('cambio')
def handole_event(cambio):
	print(cambio)
	emit('recibido', cambio, broadcast=True)

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app)
