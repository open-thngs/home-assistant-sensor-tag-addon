import socket
import json
import paho.mqtt.client as mqtt
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import CONF_NAME
from homeassistant.helpers.entity import Entity

DOMAIN = 'my_plugin'
UDP_IP = "::"
UDP_PORT = 4141
MQTT_BROKER = "mqtt_broker_ip"
MQTT_PORT = 1883

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_NAME): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

def setup_platform(hass, config, add_entities, discovery_info=None):
    add_entities([MyPluginEntity(config[CONF_NAME])])

class MyPluginEntity(Entity):
    def __init__(self, name):
        self._name = name
        self._state = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))
        self.client = mqtt.Client()
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    def update(self):
      data, addr = self.sock.recvfrom(1024)
      data = data.decode("utf-8")
      data = json.loads(data[data.index('{'):])
      self._state = data

      # Configuration message
      config_topic = f"homeassistant/sensor/{self._name}/config"
      config_message = {
        "name": self._name,
        "state_topic": f"homeassistant/sensor/{self._name}/state",
        "unit_of_measurement": "°C",
        "value_template": "{{ value_json.temperature }}",
        "json_attributes_topic": f"homeassistant/sensor/{self._name}/attributes",
        "json_attributes_template": "{{ value_json | tojson }}"
      }
      self.client.publish(config_topic, json.dumps(config_message))

      # State message
      state_topic = f"homeassistant/sensor/{self._name}/state"
      self.client.publish(state_topic, data["temperature"])

      # Attributes message
      attributes_topic = f"homeassistant/sensor/{self._name}/attributes"
      self.client.publish(attributes_topic, json.dumps(data))