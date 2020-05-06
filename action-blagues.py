import io
import http

import requests
import logging

from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%d-%m-%y %H:%M:%S",
)

INTENT_JOKE = "tellJoke"


def subscribe_intent_callback(hermes, intentMessage):
    action_wrapper(hermes, intentMessage)


def action_wrapper(hermes, intentMessage):
    intent_name = intentMessage.intent.intent_name
    session_id = "esnjfske"  # intentMessage.session_id

    logging.info(f"Opening session {session_id}")
    logging.info(f"Intent {intent_name}")

    resp = requests.get("https://api.icndb.com/jokes/random")
    if resp.status_code != 200:
        logging.error(
            f"{session_id} Invalid response from API (Code: {resp.status_code})"
        )
        result_sentence = "Désolé, je n'ai plus rien en stock"
    else:
        print(resp.json()["value"]["joke"])
        result_sentence = "Noemy tu pues des fesses"  # resp.json()["value"]["joke"]

    logging.info(f"Ending session {session_id}")
    requests.post(
        "http://192.168.1.21:12101/api/text-to-speech", data=result_sentence,
    )
    hermes.publish_end_session(session_id, result_sentence)


if __name__ == "__main__":
    mqtt_opts = MqttOptions(broker_address="192.168.1.21:1883")
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent(INTENT_JOKE, subscribe_intent_callback)

        logging.info("Subscribed")
        h.loop_start()
        h.loop_forever()
