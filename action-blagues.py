import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io
import http

import requests
import logging

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logging.INFO, datefmt='%d-%m-%y %H:%M:%S')

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

INTENT_JOKE = "Buried:tellJoke"

class SnipsConfigParser(configparser.ConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.read_file(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    intent_name = intentMessage.intent.intent_name
    session_id = intentMessage.session_id
    
    logging.info(f"Opening session {session_id}")
    logging.info(f"Intent {intent_name}")
    
    resp = requests.get('https://blague.xyz/joke/random')
    if resp.status_code != 200 :
        logging.error(f"{session_id} Invalid response from API (Code: {resp.status_code})")
        result_sentence = "Désolé, je n'ai plus rien en stock"
    else :
        joke = resp.json()['joke']
        result_sentence = joke["question"] + "     " + joke["answer"]

    logging.info(f"Ending session {session_id}")
    hermes.publish_end_session(session_id, result_sentence)

if __name__ == "__main__":
    mqtt_opts = MqttOptions(broker_address="192.168.1.21:1883")
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent(INTENT_JOKE, subscribe_intent_callback)

        logging.info("Subscribed")
        h.loop_start()
        h.loop_forever()
