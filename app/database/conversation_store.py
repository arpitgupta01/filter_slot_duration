import logging
logger = logging.getLogger(__name__)

from app.database.dbpool import dbHdlr

def get_data_from_db(customer_id, center_id, bodypart, modality_name_in_db, protocol, purpose_of_study):
    qstr = """SELECT * FROM t_time_required where (customer_id, center_id, bodypart, modality, protocol, purpose_of_study) = ('{}', '{}', '{}', '{}', '{}', '{}')""".format(customer_id, center_id, bodypart, modality_name_in_db, protocol, purpose_of_study)
    print(qstr)
    stat, data = dbHdlr().select(qstr)
    print(data)
    return stat,data

