from flask import flash
from .models import Patient, History, HistoryEvent, IndicatorValue, Diagnose, Operation, OperationLog,\
                    OperationComp
from ..main.models import Indicator, DiagnoseItem, Profile, OperationStep, Complication, Event, IndicatorNorm
from hashlib import md5
from webapp import db
from sqlalchemy import and_, or_, not_
from datetime import datetime, timedelta

def create_module(app, **kwargs):
    from .routes import history_blueprint
    app.register_blueprint(history_blueprint)


# Создание новой истории болезни
def CreateHistory(HistoryMainForm_, snils):
    if snils == '' or snils is None:
        flash('Необходимо заполнить СНИЛС', category='warning')
        return None

    digest = md5(snils.lower().encode('utf-8')).hexdigest()
    if Patient.get_patient_by_snils(digest) is None:
        # Новый пациент
        new_patient = Patient()
        new_patient.birthdate = HistoryMainForm_.birthdate.data
        new_patient.sex = HistoryMainForm_.sex.data
        new_patient.snils_hash = digest
        db.session.add(new_patient)
        db.session.flush()

        # Новая история болезни
        new_hist = History()
        new_hist.clinic_id = HistoryMainForm_.clinic.data
        new_hist.hist_number = HistoryMainForm_.hist_number.data
        new_hist.date_in = HistoryMainForm_.date_in.data
        new_hist.patient_id = new_patient.id
        new_hist.research_group_id = HistoryMainForm_.research_group.data
        new_hist.doctor_researcher_id = HistoryMainForm_.doctor_researcher.data
        new_hist.date_research_in = HistoryMainForm_.date_research_in.data
        new_hist.date_research_out = HistoryMainForm_.date_research_out.data
        new_hist.reason_id = HistoryMainForm_.reason.data
        db.session.add(new_hist)
        db.session.flush()

        # Пустое первичное обращение
        new_event = HistoryEvent()
        new_event.clinic_id = HistoryMainForm_.clinic.data
        new_event.history_id = new_hist.id
        new_event.patient_id = new_patient.id
        new_event.date_begin = new_hist.date_in
        new_event.event_id = 1
        db.session.add(new_event)
        db.session.flush()

        # Показатели: Физические параметры (самооценка при первичном опросе)
        indicators = Indicator.query.filter(Indicator.group_id==11).all()
        for i in indicators:
            new_i = IndicatorValue()
            new_i.clinic_id = HistoryMainForm_.clinic.data
            new_i.history_id = new_hist.id
            new_i.patient_id = new_patient.id
            new_i.history_event_id = new_event.id
            new_i.indicator_id = i.id
            new_i.date_value = new_hist.date_in
            db.session.add(new_i)
        try:
            db.session.commit()
        except Exception as e:
            flash('Ошибка при сохранении данных: %s' % str(e), 'error')
            db.session.rollback()
            return(None)
        else:
            return(new_hist)

    else:
        flash('Пациент с указанным СНИЛС уже есть в базе', category='warning')
        return(None)

# Обновление истории болезни
def UpdateHistory(HistoryMainForm_, h):
        history_obj = History.query.get(h)
        if history_obj is None:
            return(None)
        else:
            patient =  Patient.query.get(history_obj.patient_id)
            if patient is not None:
                patient.birthdate = HistoryMainForm_.birthdate.data
                patient.sex = HistoryMainForm_.sex.data
                db.session.add(patient)

            # Обновление истории
            history_obj.clinic_id = HistoryMainForm_.clinic.data
            history_obj.hist_number = HistoryMainForm_.hist_number.data
            history_obj.date_in = HistoryMainForm_.date_in.data
            history_obj.patient_id = patient.id
            history_obj.research_group_id = HistoryMainForm_.research_group.data
            history_obj.doctor_researcher_id = HistoryMainForm_.doctor_researcher.data
            history_obj.date_research_in = HistoryMainForm_.date_research_in.data
            history_obj.date_research_out = HistoryMainForm_.date_research_out.data
            history_obj.reason_id = HistoryMainForm_.reason.data
            db.session.add(history_obj)
            try:
                db.session.commit()
            except Exception as e:
                flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                db.session.rollback()
                return(None)
            else:
                return(history_obj)

# Добавление основного диагноза
def AddMainDiagnos(HistoryMainDiagnosForm_, history_obj):

    main_diagnose = None
    if history_obj is not None:
        # Создать или обновить основной диагноз
        # Основной диагноз может быть только один
        main_diagnose = history_obj.get_diagnoses()[1]
        if main_diagnose is not None:
            # Основной диагноз уже есть
            # Обновить атрибуты
            main_diagnose.diagnose_item_id = HistoryMainDiagnosForm_.diagnos.data
            main_diagnose.side_damage = HistoryMainDiagnosForm_.side_damage.data
            main_diagnose.date_created = HistoryMainDiagnosForm_.date_created.data
        else:
            # Создаем основной диагноз
            main_diagnose = Diagnose()
            main_diagnose.history_id = history_obj.id
            main_diagnose.clinic_id = history_obj.clinic_id
            main_diagnose.patient_id = history_obj.patient_id
            main_diagnose.diagnose_item_id = HistoryMainDiagnosForm_.diagnos.data
            main_diagnose.side_damage = HistoryMainDiagnosForm_.side_damage.data
            main_diagnose.date_created = HistoryMainDiagnosForm_.date_created.data
            print(main_diagnose)

        db.session.add(main_diagnose)

        try:
            db.session.commit()
        except Exception as e:
            flash('Ошибка при сохранении данных: %s' % str(e), 'error')
            db.session.rollback()
            return(None)
        else:
            return(main_diagnose)


# Добавление сопутствующего диагноза
def AddOtherDiagnos(HistoryOtherDiagnosForm_, history_obj):
    other_diagnose = None
    # Если диагноз уже добавлен - предупреждение
    other_diagnose = Diagnose.query.filter(Diagnose.history_id==history_obj.id, Diagnose.diagnose_item_id==HistoryOtherDiagnosForm_.diagnos.data).first()
    if other_diagnose is not None:
        flash('Такой диагноз уже есть', category='warning')
        return(None)
    # Создаем новый диагноз
    other_diagnose = Diagnose()
    other_diagnose.history_id = history_obj.id
    other_diagnose.clinic_id = history_obj.clinic_id
    other_diagnose.patient_id = history_obj.patient_id
    other_diagnose.diagnose_item_id = HistoryOtherDiagnosForm_.diagnos.data
    #other_diagnose.side_damage = MainDiagnosForm.side_damage.data
    other_diagnose.date_created = HistoryOtherDiagnosForm_.date_created.data
    db.session.add(other_diagnose)

    try:
        db.session.commit()
    except Exception as e:
        flash('Ошибка при сохранении данных: %s' % str(e), 'error')
        db.session.rollback()
        return(None)
    else:
        return(other_diagnose)


# Заполнение формы истории болезниin_([5,1,7,8])
def FillHistoryForm(HistoryMainForm_, IndicatorsForm_, HistoryMainDiagnosForm_, history_obj):
    #MainForm = HistoryMainForm()

    if history_obj != None:
        patient = Patient.query.get(history_obj.patient_id)
        HistoryMainForm_.clinic.data = history_obj.clinic_id
        HistoryMainForm_.hist_number.data = history_obj.hist_number
        HistoryMainForm_.snils.data = '111-111-111 11'#patient.snils_hash
        HistoryMainForm_.birthdate.data = patient.birthdate
        HistoryMainForm_.sex.data = patient.sex
        HistoryMainForm_.date_in.data = history_obj.date_in
        HistoryMainForm_.research_group.data = history_obj.research_group_id
        HistoryMainForm_.doctor_researcher.data = history_obj.doctor_researcher_id
        HistoryMainForm_.date_research_in.data = history_obj.date_research_in
        HistoryMainForm_.date_research_out.data = history_obj.date_research_out
        HistoryMainForm_.reason.data = history_obj.reason_id
        # Список показателей первичного обращения
        event = HistoryEvent.query.filter(HistoryEvent.history_id==history_obj.id, HistoryEvent.event_id==1 ).first()
        IndicatorsForm_.date_begin.data = event.date_begin
        # Добавление показателей первичного обращения
        items = event.get_indicators_values(11)
        # список диагнозов для отображения в форме
        diagnoses_items = history_obj.get_diagnoses()[0]
        main_diagnose = history_obj.get_diagnoses()[1]

        if main_diagnose is not None:
            HistoryMainDiagnosForm_.diagnos.data = main_diagnose.diagnose_item_id
            HistoryMainDiagnosForm_.side_damage.data = main_diagnose.side_damage
            HistoryMainDiagnosForm_.date_created.data = main_diagnose.date_created

        # Добавление амбулаторных приемов
        ambulance_events = history_obj.get_events(type='2')

        # Добавление госпитализаций
        hospital_events = history_obj.get_events(type='3')


        return([HistoryMainForm_, IndicatorsForm_, HistoryMainDiagnosForm_, event, items, diagnoses_items, ambulance_events, hospital_events])

    else:
        # История не найдена
        return(None)

# Создание нового амбулаторного приема
def CreateAmbulance(AmbulanceMainForm_, history_obj, event_obj):

    ambulance_event = HistoryEvent.query.filter(HistoryEvent.history_id==history_obj.id,HistoryEvent.event_id==event_obj.id).first()
    if ambulance_event is None:
        # Создаем амбулаторный прием
        ambulance_event = HistoryEvent()
        ambulance_event.clinic_id = history_obj.clinic_id
        ambulance_event.history_id = history_obj.id
        ambulance_event.patient_id = history_obj.patient_id
        ambulance_event.event_id = event_obj.id
        ambulance_event.date_begin = AmbulanceMainForm_.date_begin.data
        ambulance_event.doctor_id = AmbulanceMainForm_.doctor.data
        db.session.add(ambulance_event)
        db.session.flush()
        # Показатели:
        # Для амбулаторного приема перед госпитализацией (2):
        # 11 - Физические параметры (самооценка при первичном опросе)
        # 3 - Телерентгенография
        # 4 - Предоперационные обследования
        # Для амбулаторного приема через 3 и 6 месяцев (9, 10):
        # 1 - Данные объективного осмотра
        # 13 - Заключение
        # Для амбулаторного приема через год (11):
        # 1 - Данные объективного осмотра
        # 15 -Рентгенография коленного сустава в двух проекциях: Наличие зон просветления вокруг
        # 3 - Телерентгенография
        # 6 - КТ коленного сустава
        # 13 - Заключение

        if event_obj.id == 2:
            # Для амбулаторного приема перед госпитализацией (2):
            indicators = Indicator.query.filter(Indicator.group_id.in_([11,3,4])).\
                                    order_by(Indicator.group_id, Indicator.id).all()
            for i in indicators:
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.indicator_id = i.id
                new_i.date_value = ambulance_event.date_begin
                db.session.add(new_i)
            # Показатели: Рентгенография коленного сустава в двух проекциях
            indicators = Indicator.query.filter(Indicator.group_id==2).all()
            for i in indicators:
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.date_value = ambulance_event.date_begin
                new_i.indicator_id = i.id
                new_i.slice = 'Передне-задняя проекция'
                db.session.add(new_i)
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.date_value = ambulance_event.date_begin
                new_i.indicator_id = i.id
                new_i.slice = 'Боковая проекция'
                db.session.add(new_i)
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.date_value = ambulance_event.date_begin
                new_i.indicator_id = i.id
                new_i.slice = 'Результат'
                db.session.add(new_i)

        elif event_obj.id == 9 or event_obj.id == 10:
            # Для амбулаторного приема через 3 и 6 месяцев (9, 10):
            indicators = Indicator.query.filter(Indicator.group_id.in_([1,13])).\
                                    order_by(Indicator.group_id, Indicator.id).all()
            for i in indicators:
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.date_value = ambulance_event.date_begin
                new_i.indicator_id = i.id
                db.session.add(new_i)

        elif event_obj.id == 11:
            # Для амбулаторного приема через год (11):
            indicators = Indicator.query.filter(Indicator.group_id.in_([1,15,13])).\
                                    order_by(Indicator.group_id, Indicator.id).all()
            for i in indicators:
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.date_value = ambulance_event.date_begin
                new_i.indicator_id = i.id
                db.session.add(new_i)

            #КТ коленного сустава
            indicators_6 = Indicator.query.filter(Indicator.group_id==6).order_by(Indicator.group_id,Indicator.id).all()
            #Телерентгенография нижних конечностей
            indicators_3 = Indicator.query.filter(Indicator.group_id==3).order_by(Indicator.group_id,Indicator.id).all()

            # Показатели: Телерентгенография
            for i in indicators_3:
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.date_value = ambulance_event.date_begin
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.date_value = ambulance_event.date_begin
                new_i.indicator_id = i.id
                new_i.slice = 'Значение'
                new_i.num_value = 0
                db.session.add(new_i)
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.date_value = ambulance_event.date_begin
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.date_value = ambulance_event.date_begin
                new_i.indicator_id = i.id
                new_i.slice = 'Норма'
                indicator_norm =  IndicatorNorm.query.filter_by(indicator_id=i.id).first()
                if indicator_norm:
                    new_i.num_value = indicator_norm.nvalue_from
                db.session.add(new_i)
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.date_value = ambulance_event.date_begin
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.date_value = ambulance_event.date_begin
                new_i.indicator_id = i.id
                new_i.slice = 'Выход за пределы нормы'
                new_i.text_value = ''
                db.session.add(new_i)

            # Показатели: КТ коленного сустава
            for i in indicators_6:
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.date_value = ambulance_event.date_begin
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.date_value = ambulance_event.date_begin
                new_i.indicator_id = i.id
                new_i.slice = 'Значение'
                new_i.num_value = 0
                db.session.add(new_i)
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.date_value = ambulance_event.date_begin
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.date_value = ambulance_event.date_begin
                new_i.indicator_id = i.id
                new_i.slice = 'Норма'
                indicator_norm =  IndicatorNorm.query.filter_by(indicator_id=i.id).first()
                if indicator_norm:
                    new_i.num_value = indicator_norm.nvalue_to
                db.session.add(new_i)
                new_i = IndicatorValue()
                new_i.clinic_id = ambulance_event.clinic_id
                new_i.date_value = ambulance_event.date_begin
                new_i.history_id = ambulance_event.history_id
                new_i.patient_id = ambulance_event.patient_id
                new_i.history_event_id = ambulance_event.id
                new_i.date_value = ambulance_event.date_begin
                new_i.indicator_id = i.id
                new_i.slice = 'Выход за пределы нормы'
                new_i.text_value = ''
                db.session.add(new_i)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при сохранении данных: %s' % str(e), 'error')
            return(None)
        else:
            return(ambulance_event)

    else:
        flash('Амбулаторный прием такого типа уже существует', category='warning')
        return(None)

# Обновление амбулаторного приема
def UpdateAmbulance(AmbulanceMainForm_, ambulance_event):

        ambulance_event.doctor = AmbulanceMainForm_.doctor.data
        ambulance_event.date_begin = AmbulanceMainForm_.date_begin.data
        db.session.add(ambulance_event)
        db.session.commit()
        return(ambulance_event)


# Заполнение формы амбулаторного посещения
def FillAmbulanceForm(AmbulanceMainForm_, IndicatorsForm_, ProsthesisForm_, history_obj, ambulance_event):
    #MainForm = HistoryMainForm()
    if ambulance_event != None:
        AmbulanceMainForm_.doctor.data = ambulance_event.doctor_id
        AmbulanceMainForm_.date_begin.data = ambulance_event.date_begin
        IndicatorsForm_.date_begin.data = ambulance_event.date_begin
        #indicators = IndicatorValues.query.filter(IndicatorValues.history==history.id, IndicatorValues.history_event==ambulance_event.id).all()
        # Физические параметры
        items_11 = ambulance_event.get_indicators_values(11)
        # Телерентгенография нижних конечностей
        items_3 = ambulance_event.get_indicators_values(3)
        # Список предоперационных обследований
        items_4 = ambulance_event.get_indicators_values(4)
        # Рентгенография коленного сустава в двух проекциях
        indicators_sliced_values = ambulance_event.get_indicators_values(2, indicators_list=[11,12,13])

        # Рентгенография коленного сустава в двух проекциях: транспонирование списка
        item = {}
        items_2 = []
        current_indicator = 11
        for indicator_value in indicators_sliced_values:
            #item['id'] = indicator_value.get('id')
            if current_indicator != indicator_value.get('indicator'):
                items_2.append(item)
                current_indicator = indicator_value.get('indicator')
                item = {}
            item['indicator'] = indicator_value.get('indicator')
            item['description'] = indicator_value.get('description')
            slice = indicator_value.get('slice')
            if slice == 'Передне-задняя проекция':
                item['text_value_1'] = indicator_value.get('text_value')
            if slice == 'Боковая проекция':
                item['text_value_2'] = indicator_value.get('text_value')
            if slice == 'Результат':
                item['text_value_3'] = indicator_value.get('text_value')

        items_2.append(item)

        # Основной диагноз
        diagnosis = history_obj.get_diagnoses()[1]

        if diagnosis is not None:
            ProsthesisForm_.prosthesis.data = diagnosis.prosthesis_id

        return([AmbulanceMainForm_, items_11, items_2, items_3, items_4])

    else:
        # История не найдена
        return(None)

# Заполнение формы амбулаторного посещения
def FillAmbulance3Form(AmbulanceMainForm_, Ambulance3SubForm1_, Ambulance3SubForm2_, Ambulance3SubForm3_, history_obj, hospital_obj, operation_obj, ambulance_event):
    #MainForm = HistoryMainForm()
    if ambulance_event != None:
        AmbulanceMainForm_.doctor.data = ambulance_event.doctor_id
        AmbulanceMainForm_.date_begin.data = ambulance_event.date_begin
        Ambulance3SubForm1_.date_begin.data = ambulance_event.date_begin
        Ambulance3SubForm2_.date_created.data = ambulance_event.date_begin
        Ambulance3SubForm3_.date_begin.data = ambulance_event.date_begin
        #indicators = IndicatorValues.query.filter(IndicatorValues.history==history.id, IndicatorValues.history_event==ambulance_event.id).all()
        # Данные объективного осмотра
        items_1 = ambulance_event.get_indicators_values(1)
        # Заключение
        items_13 = ambulance_event.get_indicators_values(13)
        for item in items_13:
            indicator_id = item.get('indicator')
            if indicator_id == 97:
                Ambulance3SubForm3_.prostesis.data = item.get('def_value')
            if indicator_id == 104:
                Ambulance3SubForm3_.conclusions.data = item.get('def_value')
            if indicator_id == 105:
                Ambulance3SubForm3_.recomendations.data = item.get('def_value')

        # Результаты анкет
        items_profile = Profile.get_profiles_results(history_event=ambulance_event)
        # Осложнения
        complications = OperationComp.query.join(Complication, OperationComp.complication_id==Complication.id).\
                                            filter(and_(OperationComp.operation_id==operation_obj.id, Complication.type=='Поздние')).all()
        items_comp = []
        for comp in complications:
            item = {}
            item['id'] = comp.id
            comp_item = Complication.query.get(comp.complication_id)
            if comp_item:
                item['description'] = comp_item.description
            item['date_begin'] = comp.date_begin
            items_comp.append(item)

        return([AmbulanceMainForm_, Ambulance3SubForm1_, Ambulance3SubForm2_, Ambulance3SubForm3_, items_1, items_13, items_profile, items_comp])

    else:
        # История не найдена
        return(None)

# Заполнение формы амбулаторного посещения
def FillAmbulance12Form(AmbulanceMainForm_, Ambulance3SubForm1_, Ambulance3SubForm2_, Ambulance3SubForm4_,
                        Ambulance3SubForm5_, Ambulance3SubForm6_, Ambulance3SubForm7_,
                        history_obj, hospital_obj, operation_obj, ambulance_event):
    #MainForm = HistoryMainForm()
    if ambulance_event != None:
        AmbulanceMainForm_.doctor.data = ambulance_event.doctor_id
        AmbulanceMainForm_.date_begin.data = ambulance_event.date_begin
        Ambulance3SubForm1_.date_begin.data = ambulance_event.date_begin
        Ambulance3SubForm2_.date_created.data = ambulance_event.date_begin
        Ambulance3SubForm4_.date_begin.data = ambulance_event.date_begin
        #indicators = IndicatorValues.query.filter(IndicatorValues.history==history.id, IndicatorValues.history_event==ambulance_event.id).all()
        # Данные объективного осмотра
        items_1 = ambulance_event.get_indicators_values(1)
        # Рентгенография
        items_15 = ambulance_event.get_indicators_values(15)
        Ambulance3SubForm5_.indicators_date_begin.data = items_15[0].get("date_value")
        for item in items_15:
            indicator_id = item.get('indicator')
            if indicator_id == 103:
                Ambulance3SubForm5_.zone_light.data = item.get('def_value')
        # Заключение
        items_13 = ambulance_event.get_indicators_values(13)
        for item in items_13:
            indicator_id = item.get('indicator')
            if indicator_id == 97:
                Ambulance3SubForm4_.prostesis.data = item.get('def_value')
            if indicator_id == 98:
                Ambulance3SubForm4_.date_delete.data = item.get('date_value')
            if indicator_id == 99:
                Ambulance3SubForm4_.reason_delete.data = item.get('def_value')
            if indicator_id == 100:
                Ambulance3SubForm4_.patient_is_live.data = item.get('def_value')
            if indicator_id == 101:
                Ambulance3SubForm4_.date_died.data = item.get('date_value')
            if indicator_id == 102:
                Ambulance3SubForm4_.reason_died.data = item.get('def_value')
            if indicator_id == 104:
                Ambulance3SubForm4_.conclusions.data = item.get('def_value')
            if indicator_id == 105:
                Ambulance3SubForm4_.recomendations.data = item.get('def_value')

        # Результаты анкет
        items_profile = Profile.get_profiles_results(history_event=ambulance_event)
        # Осложнения
        complications = OperationComp.query.join(Complication, OperationComp.complication_id==Complication.id).\
                                            filter(and_(OperationComp.operation_id==operation_obj.id, Complication.type=='Поздние')).all()
        items_comp = []
        for comp in complications:
            item = {}
            item['id'] = comp.id
            comp_item = Complication.query.get(comp.complication_id)
            if comp_item:
                item['description'] = comp_item.description
            item['date_begin'] = comp.date_begin
            items_comp.append(item)

        # Телерентгенография
        indicators_sliced_values_3 = ambulance_event.get_indicators_values(3)
        Ambulance3SubForm6_.indicators_date_begin.data = indicators_sliced_values_3[0].get("date_value")
        # Телерентгенография: транспонирование списка
        item = {}
        items_3 = []
        current_indicator = 16
        for indicator_value in indicators_sliced_values_3:
            #item['id'] = indicator_value.get('id')
            if current_indicator != indicator_value.get('indicator'):
                items_3.append(item)
                current_indicator = indicator_value.get('indicator')
                item = {}
            item['indicator'] = indicator_value.get('indicator')
            item['description'] = indicator_value.get('description')
            item['unit'] = indicator_value.get('unit')
            slice = indicator_value.get('slice')
            if slice == 'Значение':
                item['num_value_1'] = indicator_value.get('num_value')
            if slice == 'Норма':
                item['num_value_2'] = indicator_value.get('num_value')
            if slice == 'Выход за пределы нормы':
                item['text_value_3'] = indicator_value.get('text_value')

        items_3.append(item)

        # КТ коленного сустава
        indicators_sliced_values_6 = ambulance_event.get_indicators_values(6)
        Ambulance3SubForm7_.indicators_date_begin.data = indicators_sliced_values_6[0].get("date_value")

        # КТ коленного сустава: транспонирование списка
        item = {}
        items_6 = []
        current_indicator = 57
        for indicator_value in indicators_sliced_values_6:
            #item['id'] = indicator_value.get('id')
            if current_indicator != indicator_value.get('indicator'):
                items_6.append(item)
                current_indicator = indicator_value.get('indicator')
                item = {}
            item['indicator'] = indicator_value.get('indicator')
            item['description'] = indicator_value.get('description')
            slice = indicator_value.get('slice')
            if slice == 'Значение':
                item['num_value_1'] = indicator_value.get('num_value')
            if slice == 'Норма':
                item['num_value_2'] = indicator_value.get('num_value')
            if slice == 'Выход за пределы нормы':
                item['text_value_3'] = indicator_value.get('text_value')

        items_6.append(item)

        return([AmbulanceMainForm_, Ambulance3SubForm1_, Ambulance3SubForm2_, Ambulance3SubForm4_, Ambulance3SubForm5_,
                Ambulance3SubForm6_, Ambulance3SubForm7_, items_1, items_13, items_profile, items_comp, items_3, items_6, items_15])

    else:
        # История не найдена
        return(None)

# Создание новой госпитализации
def CreateHospital(HospitalSubForm1_, history_obj):
    hospital_event = HistoryEvent()
    hospital_event.clinic_id = history_obj.clinic_id
    hospital_event.history_id = history_obj.id
    hospital_event.patient_id = history_obj.patient_id
    hospital_event.event_id = 3
    hospital_event.date_begin = HospitalSubForm1_.date_begin.data
    hospital_event.date_end = HospitalSubForm1_.date_end.data
    hospital_event.doctor_id = HospitalSubForm1_.doctor.data
    hospital_event.doctor_chief_id = HospitalSubForm1_.doctor_chief.data
    db.session.add(hospital_event)
    db.session.flush()
    # Показатели:
    indicators = Indicator.query.filter(Indicator.group_id.in_([5,1,7,8])).order_by(Indicator.group_id,Indicator.id).all()
    #Рентгенография коленного сустава в двух проекциях
    indicators_2 = Indicator.query.filter(Indicator.group_id==2).order_by(Indicator.group_id,Indicator.id).all()
    #Телерентгенография нижних конечностей
    indicators_3 = Indicator.query.filter(Indicator.group_id==3).order_by(Indicator.group_id,Indicator.id).all()

    for i in indicators:
        new_i = IndicatorValue()
        new_i.clinic_id = hospital_event.clinic_id
        new_i.history_id = hospital_event.history_id
        new_i.patient_id = hospital_event.patient_id
        new_i.history_event_id = hospital_event.id
        new_i.indicator_id = i.id
        new_i.date_value = hospital_event.date_begin
        db.session.add(new_i)

    # Показатели: Телерентгенография
    for i in indicators_3:
        new_i = IndicatorValue()
        new_i.clinic_id = hospital_event.clinic_id
        new_i.history_id = hospital_event.history_id
        new_i.patient_id = hospital_event.patient_id
        new_i.history_event_id = hospital_event.id
        new_i.indicator_id = i.id
        new_i.date_value = hospital_event.date_begin
        new_i.slice = 'Значение'
        db.session.add(new_i)
        new_i = IndicatorValue()
        new_i.clinic_id = hospital_event.clinic_id
        new_i.history_id = hospital_event.history_id
        new_i.patient_id = hospital_event.patient_id
        new_i.history_event_id = hospital_event.id
        new_i.indicator_id = i.id
        new_i.date_value = hospital_event.date_begin
        new_i.slice = 'План операции'
        db.session.add(new_i)

    # Показатели: Рентгенография коленного сустава в двух проекциях
    for i in indicators_2:
        new_i = IndicatorValue()
        new_i.clinic_id = hospital_event.clinic_id
        new_i.history_id = hospital_event.history_id
        new_i.patient_id = hospital_event.patient_id
        new_i.history_event_id = hospital_event.id
        new_i.indicator_id = i.id
        new_i.date_value = hospital_event.date_begin
        new_i.slice = 'Передне-задняя проекция'
        db.session.add(new_i)
        new_i = IndicatorValue()
        new_i.clinic_id = hospital_event.clinic_id
        new_i.history_id = hospital_event.history_id
        new_i.patient_id = hospital_event.patient_id
        new_i.history_event_id = hospital_event.id
        new_i.indicator_id = i.id
        new_i.date_value = hospital_event.date_begin
        new_i.slice = 'Боковая проекция'
        db.session.add(new_i)
        new_i = IndicatorValue()
        new_i.clinic_id = hospital_event.clinic_id
        new_i.history_id = hospital_event.history_id
        new_i.patient_id = hospital_event.patient_id
        new_i.history_event_id = hospital_event.id
        new_i.indicator_id = i.id
        new_i.date_value = hospital_event.date_begin
        new_i.slice = 'Планируемое значение'
        db.session.add(new_i)
        new_i = IndicatorValue()
        new_i.clinic_id = hospital_event.clinic_id
        new_i.history_id = hospital_event.history_id
        new_i.patient_id = hospital_event.patient_id
        new_i.history_event_id = hospital_event.id
        new_i.indicator_id = i.id
        new_i.date_value = hospital_event.date_begin
        new_i.slice = 'Фактическое значение'
        db.session.add(new_i)
        new_i = IndicatorValue()
        new_i.clinic_id = hospital_event.clinic_id
        new_i.history_id = hospital_event.history_id
        new_i.patient_id = hospital_event.patient_id
        new_i.history_event_id = hospital_event.id
        new_i.indicator_id = i.id
        new_i.date_value = hospital_event.date_begin
        new_i.slice = 'Совпадение'
        db.session.add(new_i)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при сохранении данных: %s' % str(e), 'error')
        return(None)
    else:
        return(hospital_event)

# Обновление госпитализации
def UpdateHospital(HospitalSubForm1_, hospital_event):
        hospital_event.date_begin = HospitalSubForm1_.date_begin.data
        hospital_event.date_end = HospitalSubForm1_.date_end.data
        hospital_event.doctor_id = HospitalSubForm1_.doctor.data
        hospital_event.doctor_chief_id = HospitalSubForm1_.doctor_chief.data
        # Расчет койко-дней

        if hospital_event.date_end is not None:
            delta = hospital_event.date_end - hospital_event.date_begin
            hospital_event.days1 = delta.days
        if hospital_event.date_end is None:
            hospital_event.days1 = 0
        # Если есть операция, то находим дату
        operation = Operation.query.filter(Operation.history_id==hospital_event.history_id).first()
        if operation is not None and hospital_event.date_end is not None and operation.time_begin is not None:
            # Послеоперационный койко-день
            delta = hospital_event.date_end - operation.time_begin.date()
            hospital_event.days3 = delta.days
        if operation is not None and operation.time_begin is not None:
            # Предоперационный койко-день
            delta = operation.time_begin.date() - hospital_event.date_begin
            hospital_event.days2 = delta.days
        if operation is None:
            hospital_event.days2 = 0
            hospital_event.days3 = 0

        db.session.add(hospital_event)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Ошибка при сохранении данных: %s' % str(e), 'error')
            return(None)
        else:
            return(hospital_event)

# Заполнение формы госпитализации
def FillHospitalForm(HospitalSubForm1_, HospitalSubForm2_, HospitalSubForm3_, HospitalSubForm4_,
                    HospitalSubForm5_, HospitalSubForm6_, HospitalSubForm7_,
                    HospitalSubForm8_, history_obj, hospital_event):
    HospitalSubForm1_.date_begin.data = hospital_event.date_begin
    HospitalSubForm1_.date_end.data = hospital_event.date_end
    HospitalSubForm1_.doctor.data = hospital_event.doctor_id
    HospitalSubForm1_.doctor_chief.data = hospital_event.doctor_chief_id
    HospitalSubForm1_.days1.data = hospital_event.days1
    HospitalSubForm1_.days2.data = hospital_event.days2
    HospitalSubForm1_.days3.data = hospital_event.days3

    # Общие данные о пациенте
    items_5 = hospital_event.get_indicators_values(5)
    # Заполнить форму
    for item in items_5:
        indicator_id = item.get('indicator')
        HospitalSubForm2_.date_begin.data = item.get('date_value')
        if indicator_id == 49:
            HospitalSubForm2_.claims.data = item.get('text_value')
        if indicator_id == 50:
            HospitalSubForm2_.claims_time.data = item.get('text_value')
        if indicator_id == 51:
            HospitalSubForm2_.diseases.data = item.get('text_value')
        if indicator_id == 52:
            HospitalSubForm2_.traumas.data = item.get('text_value')
        if indicator_id == 53:
            HospitalSubForm2_.smoking.data = item.get('text_value')
        if indicator_id == 54:
            HospitalSubForm2_.alcohol.data = item.get('text_value')
        if indicator_id == 55:
            HospitalSubForm2_.allergy.data = item.get('text_value')
        if indicator_id == 56:
            HospitalSubForm2_.genetic.data = item.get('text_value')

    # Данные объективного осмотра
    items_1 = hospital_event.get_indicators_values(1)
    HospitalSubForm3_.indicators_date_begin.data = items_1[0].get("date_value")
    # Оценка функции сустава и качества жизни по шкалам
    items_7 = hospital_event.get_indicators_values(7)
    # Результаты лабораторных исследований
    items_8 = hospital_event.get_indicators_values(8)
    HospitalSubForm7_.indicators_date_begin.data = items_8[0].get("date_value")
    # Рентгенография коленного сустава в двух проекциях
    indicators_sliced_values_2 = hospital_event.get_indicators_values(2, indicators_list=[11,12,13])
    HospitalSubForm4_.indicators_date_begin.data = indicators_sliced_values_2[0].get("date_value")
    # Телерентгенография
    indicators_sliced_values_3 = hospital_event.get_indicators_values(3)
    HospitalSubForm5_.indicators_date_begin.data = indicators_sliced_values_3[0].get("date_value")

    # Результаты анкет
    items_9 = Profile.get_profiles_results(history_event=hospital_event)

    # Операции
    items_10 = history_obj.get_operations()

    # Рентгенография коленного сустава в двух проекциях: транспонирование списка
    item = {}
    items_2 = []
    current_indicator = 11
    for indicator_value in indicators_sliced_values_2:
        #item['id'] = indicator_value.get('id')
        if current_indicator != indicator_value.get('indicator'):
            items_2.append(item)
            current_indicator = indicator_value.get('indicator')
            item = {}
        item['indicator'] = indicator_value.get('indicator')
        item['description'] = indicator_value.get('description')
        slice = indicator_value.get('slice')
        if slice == 'Передне-задняя проекция':
            item['text_value_1'] = indicator_value.get('text_value')
        if slice == 'Боковая проекция':
            item['text_value_2'] = indicator_value.get('text_value')
        if slice == 'Планируемое значение':
            item['text_value_3'] = indicator_value.get('text_value')
        if slice == 'Фактическое значение':
            item['text_value_4'] = indicator_value.get('text_value')
        if slice == 'Совпадение':
            item['text_value_5'] = indicator_value.get('text_value')

    items_2.append(item)

    # Телерентгенография: транспонирование списка
    item = {}
    items_3 = []
    current_indicator = 16
    for indicator_value in indicators_sliced_values_3:
        #item['id'] = indicator_value.get('id')
        if current_indicator != indicator_value.get('indicator'):
            items_3.append(item)
            current_indicator = indicator_value.get('indicator')
            item = {}
        item['indicator'] = indicator_value.get('indicator')
        item['description'] = indicator_value.get('description')
        item['unit'] = indicator_value.get('unit')
        slice = indicator_value.get('slice')
        if slice == 'Значение':
            item['num_value_1'] = indicator_value.get('num_value')
        if slice == 'План операции':
            item['num_value_2'] = indicator_value.get('num_value')

    items_3.append(item)

    # Протезы
    # Основной диагноз
    diagnosis = history_obj.get_diagnoses()[1]

    if diagnosis is not None:
        HospitalSubForm4_.prosthesis.data = diagnosis.prosthesis_id

    return(HospitalSubForm1_, HospitalSubForm2_, HospitalSubForm3_, HospitalSubForm4_, HospitalSubForm5_,
            HospitalSubForm6_, HospitalSubForm7_, HospitalSubForm8_, [items_1, items_2, items_3, items_5, items_7, items_8, items_9, items_10])

# Создание новой операции
def CreateOperation(OperationsSubForm1_, history_obj, hospital_obj):

    # Создание события для хранения показателей
    operation_event = HistoryEvent()
    operation_event.clinic_id = history_obj.clinic_id
    operation_event.history_id = history_obj.id
    operation_event.patient_id = history_obj.patient_id
    operation_event.event_id = 4
    db.session.add(operation_event)
    db.session.flush()

    # Создание операции
    operation_obj = Operation()
    operation_obj.clinic_id = history_obj.clinic_id
    operation_obj.history_id = history_obj.id
    operation_obj.hospital_id = hospital_obj.id
    operation_obj.patient_id = history_obj.patient_id
    operation_obj.history_event_id = operation_event.id
    operation_obj.doctor_surgeon_id = OperationsSubForm1_.doctor_surgeon.data
    operation_obj.doctor_assistant_id = OperationsSubForm1_.doctor_assistant.data
    operation_obj.operation_order = OperationsSubForm1_.operation_order.data
    db.session.add(operation_obj)
    db.session.flush()

    # Показатели: показатели операции и послеоперационные
    indicators = Indicator.query.filter(Indicator.group_id.in_([9,13])).order_by(Indicator.group_id,Indicator.id).all()

    for i in indicators:
        new_i = IndicatorValue()
        new_i.clinic_id = operation_event.clinic_id
        new_i.history_id = operation_event.history_id
        new_i.patient_id = operation_event.patient_id
        new_i.history_event_id = operation_event.id
        new_i.indicator_id = i.id
        db.session.add(new_i)

    # Показатели: Тестирование бригады
    indicators_10 = Indicator.query.filter(Indicator.group_id.in_([10])).order_by(Indicator.group_id,Indicator.id).all()
    for i in indicators_10:
        new_i = IndicatorValue()
        new_i.clinic_id = operation_event.clinic_id
        new_i.history_id = operation_event.history_id
        new_i.patient_id = operation_event.patient_id
        new_i.history_event_id = operation_event.id
        new_i.indicator_id = i.id
        new_i.slice = 'Реактивная тревожность'
        db.session.add(new_i)
        new_i = IndicatorValue()
        new_i.clinic_id = operation_event.clinic_id
        new_i.history_id = operation_event.history_id
        new_i.patient_id = operation_event.patient_id
        new_i.history_event_id = operation_event.id
        new_i.indicator_id = i.id
        new_i.slice = 'Личностная тревожность'
        db.session.add(new_i)

    # Этапы операции
    operation_steps = OperationStep.query.all()
    for operation_step_obj in operation_steps:
        operation_log_obj = OperationLog()
        operation_log_obj.clinic_id = operation_obj.clinic_id
        operation_log_obj.history_id = operation_obj.history_id
        operation_log_obj.patient_id = operation_obj.patient_id
        operation_log_obj.operation_id = operation_obj.id
        operation_log_obj.operation_step_id = operation_step_obj.id
        operation_log_obj.duration_min = 0
        db.session.add(operation_log_obj)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при сохранении данных: %s' % str(e), 'error')
        return(None)
    else:
        return([operation_obj, operation_event])

# Заполнение формы операции
def FillOperationForm(OperationsSubForm1_, OperationsSubForm2_, OperationsSubForm3_, OperationsSubForm4_,
                    OperationsSubForm5_, OperationsSubForm6_, OperationsSubForm7_,
                    history_obj, operation_obj, operation_event):
    OperationsSubForm1_.doctor_surgeon.data = operation_obj.doctor_surgeon_id
    OperationsSubForm1_.doctor_assistant.data = operation_obj.doctor_assistant_id
    OperationsSubForm1_.operation_order.data = operation_obj.operation_order
    # Показатели операции
    items_9 = operation_event.get_indicators_values(indicator_group=9)
    OperationsSubForm2_.operation_date_begin.data = items_9[0].get("operation_date_begin")
    for item in items_9:
        indicator_id = item.get('indicator')
        if indicator_id == 77:
            OperationsSubForm2_.anesthesia.data = item.get('def_value')
        if indicator_id == 78:
            OperationsSubForm2_.anesthesia_begin.data = item.get('date_time_value')
            OperationsSubForm2_.operation_date_begin.data = item.get('date_time_value')
        if indicator_id == 79:
            #date_time_value = item.get('date_time_value').strftime("%H:%M")
            OperationsSubForm2_.anesthesia_end.data = item.get('date_time_value')
        if indicator_id == 80:
            OperationsSubForm2_.anesthesia_duration.data = int(item.get('num_value'))
        if indicator_id == 81:
            OperationsSubForm2_.surgical_access.data = item.get('def_value')
        if indicator_id == 82:
            OperationsSubForm2_.operation_specificity.data = item.get('def_value')
        if indicator_id == 83:
            OperationsSubForm2_.technical_difficulty.data = item.get('def_value')
        if indicator_id == 84:
            OperationsSubForm2_.intraoperative_blood_loss.data = item.get('num_value')
        if indicator_id == 85:
            OperationsSubForm2_.wound_drainage.data = item.get('def_value')
        if indicator_id == 86:
            OperationsSubForm2_.amount_of_water.data = item.get('num_value')
        if indicator_id == 87:
            OperationsSubForm2_.duration_drainage.data = item.get('num_value')
        if indicator_id == 96:
            OperationsSubForm2_.intra_complications.data = item.get('def_value')

    # Тестирование операционной бригады
    indicators_sliced_values_10 = operation_event.get_indicators_values(indicator_group=10)
    OperationsSubForm3_.indicators_date.data = indicators_sliced_values_10[0].get("date_value")

    # Телерентгенография: транспонирование списка
    item = {}
    items_10 = []
    current_indicator = 88
    for indicator_value in indicators_sliced_values_10:
        #item['id'] = indicator_value.get('id')
        if current_indicator != indicator_value.get('indicator'):
            items_10.append(item)
            current_indicator = indicator_value.get('indicator')
            item = {}
        item['indicator'] = indicator_value.get('indicator')
        item['description'] = indicator_value.get('description')
        item['unit'] = indicator_value.get('unit')
        slice = indicator_value.get('slice')
        if slice == 'Реактивная тревожность':
            item['num_value_1'] = indicator_value.get('num_value')
        if slice == 'Личностная тревожность':
            item['num_value_2'] = indicator_value.get('num_value')

    items_10.append(item)

    # Журнал операции
    operation_logs = OperationLog.query.filter_by(history_id = history_obj.id, operation_id=operation_obj.id).order_by(OperationLog.operation_step_id).all()
    items_11 = []
    for operation_log in operation_logs:
        item = {}
        item['id'] = operation_log.id
        if operation_log.operation_step_id:
            step = OperationStep.query.get(operation_log.operation_step_id)
            item['step_item_id'] = operation_log.operation_step_id
            item['step_description'] = step.description
        if operation_log.time_begin:
            item['time_begin'] = operation_log.time_begin.strftime("%Y-%m-%dT%H:%M")
        else:
            item['time_begin'] = None
        if operation_log.time_end:
            item['time_end'] = operation_log.time_end.strftime("%Y-%m-%dT%H:%M")
        else:
            item['time_end'] = None
        item['duration_min'] = operation_log.duration_min
        items_11.append(item)

    # Послеоперационные наблюдения
    post_operations = HistoryEvent.query.filter_by(parent_event_id=operation_event.id).all()
    items_observations = []

    for po in post_operations:
        item = {}
        item['post_operation_id']=po.id
        item['date_begin']=po.date_begin
        event_obj = Event.query.get(po.event_id)
        item['e_type_id']=event_obj.id
        item['e_type_description']=event_obj.description
        items_observations.append(item)


    # Осложнения
    complications = OperationComp.query.join(Complication, OperationComp.complication_id==Complication.id).\
                    filter(and_(OperationComp.operation_id==operation_obj.id, Complication.type=='Послеоперационные')).all()
    items_comp = []
    for comp in complications:
        item = {}
        item['id'] = comp.id
        comp_item = Complication.query.get(comp.complication_id)
        if comp_item:
            item['description'] = comp_item.description
        item['date_begin'] = comp.date_begin
        items_comp.append(item)

    # Заключение
    items_13 = operation_event.get_indicators_values(13)
    if items_13:

        for item in items_13:
            indicator_id = item.get('indicator')
            if indicator_id == 104:
                OperationsSubForm7_.conclusions.data = item.get('def_value')
                OperationsSubForm7_.date_begin.data = item.get("date_value")
            if indicator_id == 105:
                OperationsSubForm7_.recomendations.data = item.get('def_value')

    return(OperationsSubForm1_, OperationsSubForm2_, OperationsSubForm3_, OperationsSubForm4_, OperationsSubForm5_,
            OperationsSubForm6_, OperationsSubForm7_, [items_9, items_10, items_11, items_13, items_observations, items_comp])


# Создание новой госпитализации
def CreatePostOperation(operation_obj,  e_type_id):
    operation_event_obj = HistoryEvent.query.get(operation_obj.history_event_id)

    post_operation_obj = HistoryEvent()
    post_operation_obj.parent_event_id = operation_event_obj.id
    post_operation_obj.clinic_id = operation_event_obj.clinic_id
    post_operation_obj.history_id = operation_event_obj.history_id
    post_operation_obj.patient_id = operation_event_obj.patient_id
    post_operation_obj.event_id = e_type_id
    if e_type_id == '5':
        # 1 сутки
        post_operation_obj.date_begin = operation_obj.time_end.date() + timedelta(days=1)
    elif e_type_id == '6':
        # 3 сутки
        post_operation_obj.date_begin = operation_obj.time_end.date() + timedelta(days=3)
    elif e_type_id == '7':
        # 5 сутки
        post_operation_obj.date_begin = operation_obj.time_end.date() + timedelta(days=5)
    elif e_type_id == '8':
        # 7 сутки
        post_operation_obj.date_begin = operation_obj.time_end.date() + timedelta(days=7)


    db.session.add(post_operation_obj)
    db.session.flush()
    # Показатели: Данные объективного осмотра и Результаты лабораторных исследований
    indicators = Indicator.query.filter(Indicator.group_id.in_([1,8])).order_by(Indicator.group_id,Indicator.id).all()
    #КТ коленного сустава
    indicators_6 = Indicator.query.filter(Indicator.group_id==6).order_by(Indicator.group_id,Indicator.id).all()
    #Телерентгенография нижних конечностей
    indicators_3 = Indicator.query.filter(Indicator.group_id==3).order_by(Indicator.group_id,Indicator.id).all()

    for i in indicators:
        new_i = IndicatorValue()
        new_i.clinic_id = post_operation_obj.clinic_id
        new_i.date_value = post_operation_obj.date_begin
        new_i.history_id = post_operation_obj.history_id
        new_i.patient_id = post_operation_obj.patient_id
        new_i.history_event_id = post_operation_obj.id
        new_i.indicator_id = i.id
        db.session.add(new_i)

    # Показатели: Телерентгенография
    for i in indicators_3:
        new_i = IndicatorValue()
        new_i.clinic_id = post_operation_obj.clinic_id
        new_i.date_value = post_operation_obj.date_begin
        new_i.history_id = post_operation_obj.history_id
        new_i.patient_id = post_operation_obj.patient_id
        new_i.history_event_id = post_operation_obj.id
        new_i.indicator_id = i.id
        new_i.slice = 'Значение'
        new_i.num_value = 0
        db.session.add(new_i)
        new_i = IndicatorValue()
        new_i.clinic_id = post_operation_obj.clinic_id
        new_i.date_value = post_operation_obj.date_begin
        new_i.history_id = post_operation_obj.history_id
        new_i.patient_id = post_operation_obj.patient_id
        new_i.history_event_id = post_operation_obj.id
        new_i.indicator_id = i.id
        new_i.slice = 'Норма'
        indicator_norm =  IndicatorNorm.query.filter_by(indicator_id=i.id).first()
        if indicator_norm:
            new_i.num_value = indicator_norm.nvalue_from
        db.session.add(new_i)
        new_i = IndicatorValue()
        new_i.clinic_id = post_operation_obj.clinic_id
        new_i.date_value = post_operation_obj.date_begin
        new_i.history_id = post_operation_obj.history_id
        new_i.patient_id = post_operation_obj.patient_id
        new_i.history_event_id = post_operation_obj.id
        new_i.indicator_id = i.id
        new_i.slice = 'Выход за пределы нормы'
        new_i.text_value = ''
        db.session.add(new_i)

    # Показатели: КТ коленного сустава
    for i in indicators_6:
        new_i = IndicatorValue()
        new_i.clinic_id = post_operation_obj.clinic_id
        new_i.date_value = post_operation_obj.date_begin
        new_i.history_id = post_operation_obj.history_id
        new_i.patient_id = post_operation_obj.patient_id
        new_i.history_event_id = post_operation_obj.id
        new_i.indicator_id = i.id
        new_i.slice = 'Значение'
        new_i.num_value = 0
        db.session.add(new_i)
        new_i = IndicatorValue()
        new_i.clinic_id = post_operation_obj.clinic_id
        new_i.date_value = post_operation_obj.date_begin
        new_i.history_id = post_operation_obj.history_id
        new_i.patient_id = post_operation_obj.patient_id
        new_i.history_event_id = post_operation_obj.id
        new_i.indicator_id = i.id
        new_i.slice = 'Норма'
        indicator_norm =  IndicatorNorm.query.filter_by(indicator_id=i.id).first()
        if indicator_norm:
            new_i.num_value = indicator_norm.nvalue_to
        db.session.add(new_i)
        new_i = IndicatorValue()
        new_i.clinic_id = post_operation_obj.clinic_id
        new_i.date_value = post_operation_obj.date_begin
        new_i.history_id = post_operation_obj.history_id
        new_i.patient_id = post_operation_obj.patient_id
        new_i.history_event_id = post_operation_obj.id
        new_i.indicator_id = i.id
        new_i.slice = 'Выход за пределы нормы'
        new_i.text_value = ''
        db.session.add(new_i)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Ошибка при сохранении данных: %s' % str(e), 'error')
        return(None)
    else:
        return(post_operation_obj)

# Заполнение формы госпитализации
def FillPostOperationForm(PostOperationsSubForm1_, PostOperationsSubForm2_, PostOperationsSubForm3_, PostOperationsSubForm4_,
                            PostOperationsSubForm5_, post_operation_obj):

    # Данные объективного осмотра
    items_1 = post_operation_obj.get_indicators_values(1)
    PostOperationsSubForm1_.indicators_date_begin.data = items_1[0].get("date_value")
    # Результаты лабораторных исследований
    items_8 = post_operation_obj.get_indicators_values(8)
    PostOperationsSubForm2_.indicators_date_begin.data = items_8[0].get("date_value")
    # Телерентгенография
    indicators_sliced_values_3 = post_operation_obj.get_indicators_values(3)
    PostOperationsSubForm3_.indicators_date_begin.data = indicators_sliced_values_3[0].get("date_value")
    # Телерентгенография: транспонирование списка
    item = {}
    items_3 = []
    current_indicator = 16
    for indicator_value in indicators_sliced_values_3:
        #item['id'] = indicator_value.get('id')
        if current_indicator != indicator_value.get('indicator'):
            items_3.append(item)
            current_indicator = indicator_value.get('indicator')
            item = {}
        item['indicator'] = indicator_value.get('indicator')
        item['description'] = indicator_value.get('description')
        item['unit'] = indicator_value.get('unit')
        slice = indicator_value.get('slice')
        if slice == 'Значение':
            item['num_value_1'] = indicator_value.get('num_value')
        if slice == 'Норма':
            item['num_value_2'] = indicator_value.get('num_value')
        if slice == 'Выход за пределы нормы':
            item['text_value_3'] = indicator_value.get('text_value')

    items_3.append(item)
    # КТ коленного сустава
    indicators_sliced_values_6 = post_operation_obj.get_indicators_values(6)
    PostOperationsSubForm4_.indicators_date_begin.data = indicators_sliced_values_6[0].get("date_value")

    # КТ коленного сустава: транспонирование списка
    item = {}
    items_6 = []
    current_indicator = 57
    for indicator_value in indicators_sliced_values_6:
        #item['id'] = indicator_value.get('id')
        if current_indicator != indicator_value.get('indicator'):
            items_6.append(item)
            current_indicator = indicator_value.get('indicator')
            item = {}
        item['indicator'] = indicator_value.get('indicator')
        item['description'] = indicator_value.get('description')
        slice = indicator_value.get('slice')
        if slice == 'Значение':
            item['num_value_1'] = indicator_value.get('num_value')
        if slice == 'Норма':
            item['num_value_2'] = indicator_value.get('num_value')
        if slice == 'Выход за пределы нормы':
            item['text_value_3'] = indicator_value.get('text_value')

    items_6.append(item)

    # Результаты анкет
    items_9 = Profile.get_profiles_results(history_event=post_operation_obj, profile_list=[1])

    return(PostOperationsSubForm1_, PostOperationsSubForm2_, PostOperationsSubForm3_, PostOperationsSubForm4_, PostOperationsSubForm5_,
            [items_1, items_3, items_6, items_8, items_9])
