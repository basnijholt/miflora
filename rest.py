#!/usr/bin/env python3
"""Rest API for the miflora library."""

from flask import Flask, request
from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY
from miflora import miflora_scanner, available_backends, BluepyBackend, GatttoolBackend, PygattBackend

app = Flask(__name__)

@app.route('/api/v1.0')
@app.route('/')
def index():
	return "Welcome to MiFlora rest API. The following methods are available:<br/>/api/v1.0/[moisture|conductivity|light|temperature|battery]?mac=[MAC]<br/>/api/v1.0/poll?mac=[MAC]"

@app.route('/api/v1.0/poll')
def poll():
	poller = getPoller(request.args)
	if poller is None:
		return "Provide a MAC address to poll, using ?mac="
	else:
		entitymapping = {'temperature': MI_TEMPERATURE, 'moisture': MI_MOISTURE, 'conductivity': MI_CONDUCTIVITY, 'light': MI_LIGHT, 'battery': MI_BATTERY}
		myoutput = {}
		for key,value in entitymapping.items():
			val = format(poller.parameter_value(value))
			myoutput[key]=val
		return str(myoutput)
				
@app.route('/api/v1.0/moisture')
def get_moisture():
	poller = getPoller(request.args)
	if poller is None:
		return "Provide a MAC address to poll, using ?mac="
	else:
		return format(poller.parameter_value(MI_MOISTURE))	

@app.route('/api/v1.0/conductivity')
def get_conductivity():
        args = request.args
        mac = args.get('mac')
        if mac is None:
                return "Provide a MAC address to poll, using ?mac="
        else:
                poller = MiFloraPoller(mac, backend)
                return format(poller.parameter_value(MI_CONDUCTIVITY))

@app.route('/api/v1.0/light')
def get_light():
        args = request.args
        mac = args.get('mac')
        if mac is None:
                return "Provide a MAC address to poll, using ?mac="
        else:
                poller = MiFloraPoller(mac, backend)
                return format(poller.parameter_value(MI_LIGHT))

@app.route('/api/v1.0/battery')
def get_battery():
        args = request.args
        mac = args.get('mac')
        if mac is None:
                return "Provide a MAC address to poll, using ?mac="
        else:
                poller = MiFloraPoller(mac, backend)
                return format(poller.parameter_value(MI_BATTERY))

@app.route('/api/v1.0/temperature')
def get_temperature():
	args = request.args
	mac = args.get('mac')
	if mac is None:
		return "Provide a MAC address to poll, using ?mac="
	else:
		poller = MiFloraPoller(mac, backend)
		return format(poller.parameter_value(MI_TEMPERATURE))		

def getPoller(args):
	mac = args.get('mac')
	if mac is None:
		return None
	else:
		poller = MiFloraPoller(mac, backend)
		return poller

if __name__ == '__main__':
	backend = BluepyBackend
	app.run(debug=True, host='0.0.0.0')
