import os
import requests

import logging
logger = logging.getLogger(__name__)

class PipelineV1:
    def __init__(self):
        pass

    def do_asr_correction(self, utterance:str):
        link = os.getenv("ASR_CORRECTION_ENDPOINT")
        req = requests.post(link,json={'text':utterance.lower()})
        json_response = req.json()
        if utterance!=json_response['text']:
            logger.info("ASR correction occured. \n\tInput=> {}\n\tCorrect=> {}\n".format(utterance, json_response['text']))
        return json_response['text']

    def get_intent(self, utterance:str):
        req = requests.post(os.getenv("INTENT_CLASSIFICATION_SERVICE_ENDPOINT"),json={'text':utterance.lower()})
        json_response = req.json()
        logger.debug(json_response)
        intent = json_response['intent']['name']
        confidence = json_response['intent']['confidence']
        return intent,confidence

    def get_entity(self, utterance:str):
        req = requests.post(os.getenv("NER_SERVICE_ENDPOINT"),json={'text':utterance.lower()})
        json_response = req.json()
        if  json_response.__contains__("entities"):
            return json_response['entities']
        return []
