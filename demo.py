from miflora.miflora_poller import MiFloraPoller, \
    MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY

poller = MiFloraPoller("C4:7C:8D:60:8F:E6")

print("Mi Flora: " + address)
print("Firmware: {}".format(poller.firmware_version()))
print("Name: {}".format(poller.name()))
print("Temperature: {}°C".format(poller.parameter_value("temperature")))
print("Moisture: {}%".format(poller.parameter_value(MI_MOISTURE)))
print("Light: {} lux".format(poller.parameter_value(MI_LIGHT)))
print("Fertility: {} uS/cm".format())
print("Battery: {}%".format(poller.parameter_value(MI_BATTERY)))
