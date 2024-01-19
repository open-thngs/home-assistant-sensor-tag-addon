import socket
import logging as log
import paho.mqtt.client as mqtt
import json
import os

UDP_IP = "::" # = 0.0.0.0 u IPv4
UDP_PORT = 4141

MQTT_HOST = os.getenv('MQTT_HOST')
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASSWORD =  os.getenv('MQTT_PASSWORD')

configured_devices = []

log.basicConfig(level=log.INFO)

def generate_config_payload(uid, device_class, valuetag, unit_of_measurement):
    #{"alive":8589,"voltage":3.245,"light":2266.726,"temperature":-0.56,"humidity":59.12,"pressure":1027.39}
    return {
        "name": device_class.capitalize(),
        "obj_id": "thread_sensor_tag_"+uid+"_"+valuetag,
        "~": "homeassistant/sensor/"+uid,
        "uniq_id": uid+"#"+valuetag,
        "state_topic": "~/state",
        "unit_of_measurement": unit_of_measurement,
        "device_class": device_class,
        "value_template": "{{ value_json."+valuetag+" }}",
        "force_update": True,
        "device": {
            "identifiers": [
                str(uid)
            ],
            "manufacturer": "open-things.de",
            "model": "Thread Sensor Tag",
            "name": "Thread Sensor Tag ["+uid+"]"
        }
    }

def send_config_message(clientMQTT, uid, device_class, valuetag, unit_of_measurement):
    if uid in configured_devices:
        return
    payload = generate_config_payload(uid, device_class, valuetag, unit_of_measurement)
    topic = "homeassistant/sensor/"+uid+"/"+device_class+"/config"
    log.debug(f"'{topic}' => '{payload}'")
    clientMQTT.publish(topic, json.dumps(payload), retain=True)

def send_all_config_messages(clientMQTT,uid):
    send_config_message(clientMQTT, uid, "duration",    "alive",        "ms")
    send_config_message(clientMQTT, uid, "voltage",     "voltage",      "V")
    send_config_message(clientMQTT, uid, "temperature", "temperature",  "°C")
    send_config_message(clientMQTT, uid, "humidity",    "humidity",     "%")
    send_config_message(clientMQTT, uid, "pressure",    "pressure",     "Pa")
    send_config_message(clientMQTT, uid, "illuminance", "light",        "lx")
    configured_devices.append(uid)

def run():
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    server_address = (UDP_IP, UDP_PORT)
    sock.bind(server_address)

    log.debug("Connect MQTT")
    clientMQTT = mqtt_start(True)

    log.info("Waiting for UDP messages...")
    while True:
        data, address = sock.recvfrom(4096)
        message = data.decode("utf-8")
        log.info("udp message: " + message)
        parts = message.split("{")
        uid = parts[0].split('/')[1]
        send_all_config_messages(clientMQTT, uid)

        topic = "homeassistant/sensor/"+uid+"/state"
        payload = '{'+parts[1].rstrip('\n')
        log.debug(f"'{topic}' => {payload}")
        clientMQTT.publish(topic, payload)

def on_connect(lclient, userdata, flags, rc):
    log.info("mqtt> connected with result code "+str(rc))        

def mqtt_start(start_looping):
    clientID = "thread_tags_" + socket.gethostname()
    clientMQTT = mqtt.Client(client_id=clientID)
    clientMQTT.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    clientMQTT.on_connect = on_connect
    clientMQTT.connect(MQTT_HOST, 1883, 60)
    if(start_looping):
        clientMQTT.loop_start()

    return clientMQTT

run()