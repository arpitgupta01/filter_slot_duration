import json

from app.database.dbpool import dbHdlr
from fastapi import APIRouter, Request

from app.database.conversation_store import get_data_from_db
from app.core.nlp.pipeline import PipelineV1
from app.model.schemas import Data

import logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/calculate_score")
def calculate_matching_score(request:Request, data:Data):
    entity_list = __entity_found_in_user_utterance(data.utterance)
    logger.info("Entity values : {}".format(entity_list))
    if entity_list is not None:
        bodypart, modality, protocol, purpose_of_study = __extract_each_entity(entity_list)
        print("Bodypart : {}\nModality : {}\nProtocol : {}\nPurpose of study : {}".format(bodypart, modality, protocol, purpose_of_study))
        if modality != "*":
            modality_name_in_db = __map_modality_in_user_utterance(modality)
        db_enty_list = __filter_db_for_entity_found(data.customer_id, data.center_id, bodypart, modality_name_in_db, protocol, purpose_of_study)
        logger.info("db_entry_list : {}".format(db_enty_list))
        if db_enty_list != None:
            logger.info(db_enty_list.__len__())
            match_count_list = __compare_user_utterance_with_db_data(data.utterance, db_enty_list)
            return match_count_list
        else:
            logger.info("No data found in database")
    else:
        return "No entities found in utterance"


def __entity_found_in_user_utterance(utterance):
    entity_list = None
    pv1 = PipelineV1()
    if utterance != "":
        asr_corrected_utterance = pv1.do_asr_correction(utterance)
        if asr_corrected_utterance is None:
            asr_corrected_utterance = 'No data found'
        else:
            intent, confidence = pv1.get_intent(asr_corrected_utterance)

        if intent == "service_request":
            entity_list = pv1.get_entity(asr_corrected_utterance)
    else:
        return None
    return entity_list


def __extract_each_entity(entity_list):
    bodypart = modality = protocol = purpose_of_study = "*"

    for each_entity in entity_list:
        if each_entity["entity"] in ["bodypart", "modality", "protocol", "purpose_of_study"]:
            if each_entity["entity"] == "bodypart":
                bodypart = each_entity["value"]
            if each_entity["entity"] == "modality":
                modality = each_entity["value"]
            if each_entity["entity"] == "protocol":
                protocol = each_entity["value"]
            if each_entity["entity"] == "purpose_of_study":
                purpose_of_study = each_entity["value"]

    return bodypart, modality, protocol, purpose_of_study


def __filter_db_for_entity_found(customer_id, center_id, bodypart, modality_name_in_db, protocol, purpose_of_study):
    stat, db_enty_list = get_data_from_db(customer_id, center_id, bodypart, modality_name_in_db, protocol, purpose_of_study)
    if type(db_enty_list) != list:
        db_enty_list = [db_enty_list]
    if db_enty_list != [()]:
        return db_enty_list
    else:
        return None


def __compare_user_utterance_with_db_data(utterance, db_enty_list):
    utterance_word_list = utterance.split(" ")
    logger.info(utterance_word_list)
    match_count_list = []
    found_entites = []
    for each_entry in db_enty_list:
        id = each_entry["id"]
        time_needed_for_procedure = each_entry["time_needed_for_procedure"]
        if "bodypart" in each_entry and each_entry["bodypart"] is not "*":
            bodypart = each_entry["bodypart"]
            found_entites.append(bodypart)
        if "modality" in each_entry and each_entry["modality"] is not "*":
            modality = each_entry["modality"]
            found_entites.append(modality)
        if "protocol" in each_entry and each_entry["protocol"] is not "*":
            protocol = each_entry["protocol"]
            found_entites.append(protocol)
        if "purpose_of_study" in each_entry and each_entry["purpose_of_study"] is not "*":
            purpose_of_study = each_entry["purpose_of_study"]
            found_entites.append(purpose_of_study)

        match_count = 0
        for each_word in utterance_word_list:
            if each_word in found_entites:
                match_count += 1

        each_entry_data = {"id":id, "match_count":match_count, "time_needed_for_procedure":time_needed_for_procedure}
        match_count_list.append(each_entry_data)
        # logger.info("ID : {}\nMatch Count : {}".format(id, match_count))

    return match_count_list


def __map_modality_in_user_utterance(modality):
    modality_map = {'xray':'CR','x-ray':'CR','x ray':'CR','mri':'MR','ultrasound':"US",'usg':"US",'sonography':"US",'cat':'CT','dexa':'DEXA','bmd':'BMD'}
    if modality in modality_map:
        modality_name_in_db = modality_map[modality]
    else:
        modality_name_in_db = "DEFAULT"

    return modality_name_in_db

# CR
# MR
# US
# CT
# DEXA
# BMD
