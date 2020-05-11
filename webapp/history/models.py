from webapp import db
from time import time
from datetime import datetime, date
from sqlalchemy import and_, or_, not_
from hashlib import md5
from ..main.models import Indicator, Complication, Clinic, DiagnoseItem, Doctor, Event, OperationStep, Profile, \
                    Prosthesis, ProfileItem, ProfileAnswer, ProsthesisComponent, Reason, ResearchGroup, \
                    IndicatorDef, IndicatorNorm, IndicatorGroup

# Пациенты
class Patient(db.Model):
    __tablename__ = 'Patient'
    id = db.Column(db.Integer(), primary_key=True)
    snils_hash =db.Column(db.String(128), unique=False)
    birthdate = db.Column(db.Date())
    sex = db.Column(db.String(1), index=True)
    histories = db.relationship('History', backref='patient')

#  Создание хэш-значения для СНИЛС
    @staticmethod
    def get_snils_hash(snils):
        digest = md5(snils.lower().encode('utf-8')).hexdigest()
        return digest

#  Проверка наличия пациента в базе
    @staticmethod
    def get_patient_by_snils(digest):
        f_patient = Patient.query.filter(Patient.snils_hash==digest).first()
        if f_patient is None:
            return(None)
        else:
            return(f_patient)

# Истории болезни
class History(db.Model):
    __tablename__='History'
    id = db.Column(db.Integer(), primary_key=True)
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinic.id'), index = True)
    hist_number = db.Column(db.String(100), unique=False)
    time_created = db.Column(db.DateTime(), default=datetime.utcnow())
    date_in = db.Column(db.Date())
    patient_id = db.Column(db.Integer(), db.ForeignKey('Patient.id'))
    research_group_id = db.Column(db.Integer(), db.ForeignKey('ResearchGroup.id'), index = True)
    doctor_researcher_id = db.Column(db.Integer(), db.ForeignKey('Doctor.id'), index = True)
    date_research_in = db.Column(db.Date())
    date_research_out = db.Column(db.Date())
    reason_id = db.Column(db.Integer(), db.ForeignKey('Reason.id'))
    diagnoses = db.relationship('Diagnose', backref='history', lazy='dynamic')
    events = db.relationship('HistoryEvent', backref='history', lazy = 'dynamic')
    operations = db.relationship('Operation', backref='history', lazy = 'dynamic')

    def get_diagnoses(self, **kwargs):
        """
        Выбор диагнозов
        Возвращает все диагнозы
        и отдельно - основной
        Параметры:
        """
        # Выбор диагнозов
        diagnoses = self.diagnoses
        diagnoses_items = []
        main_diagnose=None
        for d in diagnoses:
            diagnose_item = DiagnoseItem.query.get(d.diagnose_item_id)
            item = {}
            item['id'] = d.id
            item['description'] = diagnose_item.description
            item['type'] = diagnose_item.type
            item['mkb10'] = diagnose_item.mkb10
            item['date_created'] = d.date_created
            if diagnose_item.type=='Основной':
                main_diagnose = d
            diagnoses_items.append(item)

        return([diagnoses_items, main_diagnose])

    def get_events(self, **kwargs):
        """
        Выбор событий
        Возвращает все события истории болезни
        Параметры:
        Тип события - опционально
        """
        # Выбор событий
        event_type = kwargs.get('type',None)
        if event_type:
            # Задано событие определенного типа
            events = HistoryEvent.query.join(Event, Event.id==HistoryEvent.event_id).\
                            filter(and_(HistoryEvent.history_id==self.id,  Event.type==event_type)).all()
        else:
            events = self.events

        items = []
        for a in events:
            # Пытаемся найти и передать номер госпитализации и операции
            operation_obj = Operation.query.filter_by(history_id=self.id).first()

            event_item = Event.query.get(a.event_id)
            item = {}
            item['event'] = a
            item['event_id'] = a.id
            item['event_date'] = a.date_begin
            item['event_date_begin'] = a.date_begin
            item['event_date_end'] = a.date_end
            doctor = Doctor.query.get(a.doctor_id)
            item['doctor'] = doctor.fio
            item['event_name'] = event_item.description
            item['event_type'] = event_item.id
            if operation_obj:
                item['operation_id'] = operation_obj.id
                item['hospital_id'] = operation_obj.hospital_id
            else:
                item['operation_id'] = 0
                item['hospital_id'] = 0

            items.append(item)
        return items

    def get_operations(self):

        items = []
        operations = self.operations

        for o in operations:
            doctor_surgeon = Doctor.query.get(o.doctor_surgeon_id)
            item = {}
            item["id"] = o.id
            item["date"] =  date(2012,1,1)
            if doctor_surgeon:
                item["doctor_surgeon"] =  doctor_surgeon.fio
            else:
                item["doctor_surgeon"] = ''

            items.append(item)

        return items


# Диагнозы
class Diagnose(db.Model):
    __tablename__='Diagnose'
    id = db.Column(db.Integer(), primary_key=True)
    clinic_id =  db.Column(db.Integer(), db.ForeignKey('Clinic.id'), index = True)
    history_id = db.Column(db.Integer(), db.ForeignKey('History.id'), index = True)
    patient_id = db.Column(db.Integer(), db.ForeignKey('Patient.id'))
    diagnose_item_id = db.Column(db.Integer(), db.ForeignKey('DiagnoseItem.id'))
    prosthesis_id = db.Column(db.Integer(), db.ForeignKey('Prosthesis.id'))
    side_damage = db.Column(db.String(100))
    date_created = db.Column(db.Date())

# События в рамках истории болезни
class HistoryEvent(db.Model):
    __tablename__='HistoryEvent'
    id = db.Column(db.Integer(), primary_key=True)
    parent_event_id = db.Column(db.Integer(), db.ForeignKey('HistoryEvent.id'))
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinic.id'))
    history_id = db.Column(db.Integer(), db.ForeignKey('History.id'))
    patient_id = db.Column(db.Integer(), db.ForeignKey('Patient.id'))
    event_id = db.Column(db.Integer(), db.ForeignKey('Event.id'), index = True)
    date_begin = db.Column(db.Date())
    date_end = db.Column(db.Date())
    doctor_id = db.Column(db.Integer(), db.ForeignKey('Doctor.id'), index = True)
    doctor_researcher_id = db.Column(db.Integer(), db.ForeignKey('Doctor.id'), index = True)
    doctor_chief_id = db.Column(db.Integer(), db.ForeignKey('Doctor.id'), index = True)
    days1 = db.Column(db.Integer()) #койко-день
    days2 = db.Column(db.Integer()) #предоперационный койко-день
    days3 = db.Column(db.Integer()) #послеоперационный койко-день


    def get_indicators_values(self, indicator_group, **kwargs):
        """
        Выбор показателей события
        Параметры:
        indicators_group - код группы
        indicators_list - список показателей (опционально)

        """
        indicators_list = kwargs.get('indicators_list',None)

        # Выбор всех показателей из группы
        indicators_values = IndicatorValue.query.join(Indicator, IndicatorValue.indicator_id==Indicator.id).\
                    filter(IndicatorValue.history_event_id==self.id, Indicator.group_id==indicator_group).\
                    order_by(IndicatorValue.id).all()

        items = []
        for i in indicators_values:
            indicator = Indicator.query.get(i.indicator_id)
            if indicators_list and indicator.id not in indicators_list:
                continue
            indicator_norms = IndicatorNorm.query.filter(IndicatorNorm.indicator_id==indicator.id).first()
            item = {}
            item['id'] = i.id
            item['indicator'] = i.indicator_id
            item['slice'] = i.slice
            item['description'] = indicator.description
            item['is_calculated'] = indicator.is_calculated
            item['date_value'] = i.date_value
            item['date_time_value'] = i.date_time_value
            item['def_value'] = i.def_value
            if i.num_value == None:
                item['num_value'] = 0
            else:
                if indicator.type == 'integer':
                    item['num_value'] = int(i.num_value)
                else:
                    item['num_value'] = i.num_value
            if i.comment == None:
                item['comment'] = ''
            else:
                item['comment'] = i.comment
            if i.text_value == None:
                item['text_value'] = ''
            else:
                item['text_value'] = i.text_value
            if indicator.unit == None:
                item['unit'] = ''
            else:
                item['unit'] = indicator.unit
            if indicator_norms:
                item['nvalue_from'] = indicator_norms.nvalue_from
                item['nvalue_to'] = indicator_norms.nvalue_from

            items.append(item)

        return(items)

# Фактические значения показателей пациентов
class IndicatorValue(db.Model):
    __tablename__='IndicatorValue'
    id = db.Column(db.Integer(), primary_key=True)
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinic.id'), index = True)
    history_id = db.Column(db.Integer(), db.ForeignKey('History.id'), index = True)
    patient_id = db.Column(db.Integer(), db.ForeignKey('Patient.id'))
    history_event_id = db.Column(db.Integer(), db.ForeignKey('HistoryEvent.id'))
    indicator_id = db.Column(db.Integer(), db.ForeignKey('Indicator.id'))
    slice = db.Column(db.String(100))
    time_created = db.Column(db.DateTime(), default=datetime.utcnow())
    date_value = db.Column(db.Date())
    date_time_value = db.Column(db.DateTime())
    text_value = db.Column(db.String(100))
    num_value = db.Column(db.Numeric())
    num_deviation = db.Column(db.Numeric())
    def_value = db.Column(db.Integer())
    comment = db.Column(db.String(500))

# Операции
class Operation(db.Model):
    __tablename__='Operation'
    id = db.Column(db.Integer(), primary_key=True)
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinic.id'), index = True)
    history_id = db.Column(db.Integer(), db.ForeignKey('History.id'))
    hospital_id = db.Column(db.Integer(), db.ForeignKey('HistoryEvent.id'))
    history_event_id = db.Column(db.Integer(), db.ForeignKey('HistoryEvent.id'))
    patient_id = db.Column(db.Integer(), db.ForeignKey('Patient.id'))
    doctor_surgeon_id = db.Column(db.Integer(), db.ForeignKey('Doctor.id'))
    doctor_assistant_id = db.Column(db.Integer(), db.ForeignKey('Doctor.id'))
    #operation_order_id = db.Column(db.Integer())
    operation_order = db.Column(db.Integer())
    time_begin = db.Column(db.DateTime())
    time_end = db.Column(db.DateTime())
    duration_min = db.Column(db.Integer()) # Длительность в минутах

    # Получить список операций для истории болезни
    @staticmethod
    def get_operations(history):

        operations = history.operations
        if operations:
            items = []
            for operation in operations:
                doctor = Doctor.get(operation.doctor_surgeon_id)
                item = {}
                item["date"] = operation.time_begin
                item["doctor_surgeon"] = doctor.fio
                items.append(item)

            return items

# Журнал операции
class OperationLog(db.Model):
    __tablename__='OperationLog'
    id = db.Column(db.Integer(), primary_key=True)
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinic.id'), index = True)
    history_id = db.Column(db.Integer(), db.ForeignKey('History.id'))
    patient_id = db.Column(db.Integer(), db.ForeignKey('Patient.id'))
    operation_id = db.Column(db.Integer(), db.ForeignKey('Operation.id'))
    operation_step_id = db.Column(db.Integer(), db.ForeignKey('OperationStep.id'))
    time_begin = db.Column(db.DateTime())
    time_end = db.Column(db.DateTime())
    duration_min = db.Column(db.Integer()) # Длительность в минутах

# Осложнения после операции
class OperationComp(db.Model):
    __tablename__='OperationComp'
    id = db.Column(db.Integer(), primary_key=True)
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinic.id'), index = True)
    history_id = db.Column(db.Integer(), db.ForeignKey('History.id'))
    patient_id = db.Column(db.Integer(), db.ForeignKey('Patient.id'))
    operation_id = db.Column(db.Integer(), db.ForeignKey('Operation.id'))
    complication_id = db.Column(db.Integer(), db.ForeignKey('Complication.id'))
    date_begin = db.Column(db.Date())


# Фактические ответы анкет
class ProfileResponse(db.Model):
    __tablename__='ProfileResponse'
    id = db.Column(db.Integer(), primary_key=True)
    date_value = db.Column(db.Date())
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinic.id'), index = True)
    history_id = db.Column(db.Integer(), db.ForeignKey('History.id'))
    patient_id = db.Column(db.Integer(), db.ForeignKey('Patient.id'))
    history_event_id = db.Column(db.Integer(), db.ForeignKey('HistoryEvent.id'))
    profile_id = db.Column(db.Integer(), db.ForeignKey('Profile.id'), index = True)
    profile_item_id= db.Column(db.Integer(), db.ForeignKey('ProfileItem.id'))
    response = db.Column(db.String(100), unique=False)
    response_value = db.Column(db.Numeric())
