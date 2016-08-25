from miflora.miflora_poller import MiFloraPoller, \
    MI_FERTILITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE

poller = MiFloraPoller("C4:7C:8D:60:8F:E6")
print("Getting data from Mi Flora")
print("Temperature: {}".format(poller.parameter_value("temperature")))
print("Moisture: {}".format(poller.parameter_value(MI_MOISTURE)))
print("Light: {}".format(poller.parameter_value(MI_LIGHT)))

