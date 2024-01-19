#!/usr/bin/with-contenv bashio

echo "Hello world!"

python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

if ! bashio::services.available "mqtt"; then
  bashio::log.error "No internal MQTT service found"
else
  bashio::log.info "MQTT service found, fetching credentials ..."
  export MQTT_HOST=$(bashio::services mqtt "host")
  export MQTT_USER=$(bashio::services mqtt "username")
  export MQTT_PASSWORD=$(bashio::services mqtt "password")
fi

echo "Run script"
python3 /udp.py