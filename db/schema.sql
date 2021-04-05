CREATE DATABASE IF NOT EXISTS slot_time;
USE slot_time;

CREATE TABLE IF NOT EXISTS t_time_required(
    id INT PRIMARY KEY AUTO_INCREMENT,
    procedure_name VARCHAR(64),
    customer_id INT,
    center_id INT,
    bodypart VARCHAR(64),
    modality VARCHAR(64),
    protocol VARCHAR(64),
    purpose_of_study VARCHAR(64),
    time_needed_for_procedure INT
);

INSERT INTO t_time_required (procedure_name, customer_id, center_id, bodypart,modality,protocol,purpose_of_study,time_needed_for_procedure) VALUES ("Pelvis Ultrasound-Male", 1,1,'pelvis','US','*','*',20);
INSERT INTO t_time_required (procedure_name, customer_id, center_id, bodypart,modality,protocol,purpose_of_study,time_needed_for_procedure) VALUES ("Pelvis Ultrasound-Female", 1,1,'pelvis','US','*','*',30);
INSERT INTO t_time_required (procedure_name, customer_id, center_id, bodypart,modality,protocol,purpose_of_study,time_needed_for_procedure) VALUES ("Pregnancy Scan", 1,1,'pelvis','US','pregnancy','*',45);
INSERT INTO t_time_required (procedure_name, customer_id, center_id, bodypart,modality,protocol,purpose_of_study,time_needed_for_procedure) VALUES ("CR", 1,1,'*','CR','*','*',15);
INSERT INTO t_time_required (procedure_name, customer_id, center_id, bodypart,modality,protocol,purpose_of_study,time_needed_for_procedure) VALUES ("MR", 1,1,'*','MR','*','*',45);
INSERT INTO t_time_required (procedure_name, customer_id, center_id, bodypart,modality,protocol,purpose_of_study,time_needed_for_procedure) VALUES ("US", 1,1,'*','US','*','*',30);
INSERT INTO t_time_required (procedure_name, customer_id, center_id, bodypart,modality,protocol,purpose_of_study,time_needed_for_procedure) VALUES ("CT", 1,1,'*','CT','*','*',25);
INSERT INTO t_time_required (procedure_name, customer_id, center_id, bodypart,modality,protocol,purpose_of_study,time_needed_for_procedure) VALUES ("DEXA", 1,1,'*','DEXA','*','*',60);
INSERT INTO t_time_required (procedure_name, customer_id, center_id, bodypart,modality,protocol,purpose_of_study,time_needed_for_procedure) VALUES ("BMD", 1,1,'*','BMD','*','*',40);
