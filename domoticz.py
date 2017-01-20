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

# So id devices use: sudo hcitool lescan

# Sensor IDs

# Create 4 virtual sensors in dummy hardware
# type temperature
# type lux
# type percentage (moisture)
# type custom (fertility)

base64string = base64.encodestring(('%s:%s' % (domoticzusername, domoticzpassword)).encode()).decode().replace('\n', '')

def domoticzrequest (url):
  request = urllib.request.Request(url)
  request.add_header("Authorization", "Basic %s" % base64string)
  response = urllib.request.urlopen(request)
  return response.read()

def update(address,idx_moist,idx_temp,idx_lux,idx_cond):

    poller = MiFloraPoller(address)

    # reading error in poller (happens sometime, you go and bug the original author):
    #
    # 26231 fertility
    # 136% moisture
    # 4804.2 temperature
    # 61149 lux
    
    loop = 0
    while loop < 2 and poller.parameter_value("temperature") > 200:
        print("Patched: Error reading value retry after 5 seconds...\n")
        time.sleep(5)
        poller = MiFloraPoller(address)
        loop += 1
    
    if poller.parameter_value("temperature") > 200:
        print("Patched: Error reading value\n")
        return
    
    global domoticzserver

    print("Mi Flora: " + address)
    print("Firmware: {}".format(poller.firmware_version()))
    print("Name: {}".format(poller.name()))
    print("Temperature: {}°C".format(poller.parameter_value("temperature")))
    print("Moisture: {}%".format(poller.parameter_value(MI_MOISTURE)))
    print("Light: {} lux".format(poller.parameter_value(MI_LIGHT)))
    print("Fertility: {} uS/cm?".format(poller.parameter_value(MI_CONDUCTIVITY)))
    print("Battery: {}%".format(poller.parameter_value(MI_BATTERY)))

    val_bat  = "{}".format(poller.parameter_value(MI_BATTERY))
    
    # Update temp
    val_temp = "{}".format(poller.parameter_value("temperature"))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_temp + "&nvalue=0&svalue=" + val_temp + "&battery=" + val_bat)

    # Update lux
    val_lux = "{}".format(poller.parameter_value(MI_LIGHT))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_lux + "&svalue=" + val_lux + "&battery=" + val_bat)

    # Update moisture
    val_moist = "{}".format(poller.parameter_value(MI_MOISTURE))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_moist + "&svalue=" + val_moist + "&battery=" + val_bat)

    # Update fertility
    val_cond = "{}".format(poller.parameter_value(MI_CONDUCTIVITY))
    domoticzrequest("http://" + domoticzserver + "/json.htm?type=command&param=udevice&idx=" + idx_cond + "&svalue=" + val_cond + "&battery=" + val_bat)
    time.sleep(1)

# format address, moist (%), temp (°C), lux, fertility

print("\n1: Vrouwentong (sansevieria trifasciata)")
update("C4:7C:8D:62:42:88","470","138","140","141")

print("\n2: Gatenplant: (monstera deliciosa)")
update("C4:7C:8D:62:48:71","471","338","339","348")

print("\n3: Bananen boom (musa)")
update("C4:7C:8D:62:47:D0","472","337","340","347")

print("\n4: Graslelie (chlorophytum comosum)")
update("C4:7C:8D:62:48:4A","473","336","341","346")

print("\n5: Wonderstruik (codiaeum variegatum)")
update("C4:7C:8D:62:47:CB","474","335","342","345")

print("\n6: Manderijn (citrus reticulata)")
update("C4:7C:8D:62:47:B7","475","334","343","344")

print("\n7: Ficus (ficus elastica)")
update("C4:7C:8D:62:2F:F5","476","445","450","455")

print("\n8: Dracaena (dracaena marginata)")
update("C4:7C:8D:62:3B:2A","477","446","451","456")

print("\n9: Grapefruit (citrus paradisi)")
update("C4:7C:8D:62:2C:40","478","447","452","457")

print("\n10: Yucca (yucca  elephantipes)")
update("C4:7C:8D:62:3B:31","479","448","453","458")

print("\n11: Lepelplant (spathiphyllum)")
update("C4:7C:8D:62:3B:B7","480","449","454","459")





