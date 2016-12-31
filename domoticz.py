import urllib.request
import base64
import time
from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY

# Settings for the domoticz server

# Forum see: http://domoticz.com/forum/viewtopic.php?f=56&t=13306&hilit=mi+flora&start=20#p105255

domoticzserver   = "127.0.0.1:8080"
domoticzusername = ""
domoticzpassword = ""

# sudo hcitool lescan

# Sensor IDs

# Create 4 virtual sensors in dummy hardware
# type temperature
# type lux
# type moisture
# type custom

base64string = base64.encodestring(('%s:%s' % (domoticzusername, domoticzpassword)).encode()).decode().replace('\n', '')

def domoticzrequest (url):
  request = urllib.request.Request(url)
  request.add_header("Authorization", "Basic %s" % base64string)
  response = urllib.request.urlopen(request)
  return response.read()

def go(address,idx_moist,idx_temp,idx_lux,idx_cond):

    poller = MiFloraPoller(address)
    
    global domoticzserver

    print("Getting data from Mi Flora: " + address)
    print("FW: {}".format(poller.firmware_version()))
    print("Name: {}".format(poller.name()))
    print("Moisture: {}".format(poller.parameter_value(MI_MOISTURE)))
    print("Light: {}".format(poller.parameter_value(MI_LIGHT)))
    print("Conductivity: {}".format(poller.parameter_value(MI_CONDUCTIVITY)))
    print("Battery: {}".format(poller.parameter_value(MI_BATTERY)))
    print("Temperature: {}".format(poller.parameter_value("temperature")))

    val_bat  = "{}".format(poller.parameter_value(MI_BATTERY))

    # Update temp
    val_temp = "{}".format(poller.parameter_value("temperature"))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_temp + "&nvalue=0&svalue=" + val_temp + "&battery=" + val_bat)

    # Update lux
    val_lux = "{}".format(poller.parameter_value(MI_LIGHT))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_lux + "&svalue=" + val_lux + "&battery=" + val_bat)

    # Update moisture
    val_moist = "{}".format(poller.parameter_value(MI_MOISTURE))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_moist + "&nvalue=" + val_moist + "&battery=" + val_bat)

    # Update conductivity
    val_cond = "{}".format(poller.parameter_value(MI_CONDUCTIVITY))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_cond + "&svalue=" + val_cond + "&battery=" + val_bat)


# format address moist temp lux cond
go("C4:7C:8D:62:42:88","139","138","140","141")
time.sleep(1)
go("C4:7C:8D:62:48:71","329","338","339","348")
time.sleep(1)
go("C4:7C:8D:62:47:D0","330","337","340","347")
time.sleep(1)
go("C4:7C:8D:62:48:4A","331","336","341","346")
time.sleep(1)
go("C4:7C:8D:62:47:CB","332","335","342","345")
time.sleep(1)
go("C4:7C:8D:62:47:B7","333","334","343","344")





