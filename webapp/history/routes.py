import os
import tempfile
from datetime import datetime, timedelta
from hashlib import md5

import subprocess
import shlex
import pandas as pd
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, session, url_for, send_file)
from flask_login import login_required
from werkzeug.utils import secure_filename

from .. import db
from ..main.models import (Clinic, DiagnoseItem, Event, Indicator,
                           OperationStep, Profile, ProfileSection,
                           ProfileSectionResponse, Prosthesis)
from . import (AddMainDiagnos, AddOtherDiagnos, CreateAmbulance, CreateHistory,
               CreateHospital, CreateOperation, CreatePostOperation,
               FillAmbulance3Form, FillAmbulance12Form, FillAmbulanceForm,
               FillHistoryForm, FillHospitalForm, FillOperationForm,
               FillPostOperationForm, UpdateAmbulance, UpdateHistory,
               UpdateHospital)
from .forms import (Ambulance3SubForm1, Ambulance3SubForm2, Ambulance3SubForm3,
                    Ambulance3SubForm4, Ambulance3SubForm5, Ambulance3SubForm6,
                    Ambulance3SubForm7, AmbulanceMainForm,
                    HistioryNewAmbulanceForm, HistoryFilterForm,
                    HistoryMainDiagnosForm, HistoryMainForm,
                    HistoryOtherDiagnosForm, HospitalSubForm1,
                    HospitalSubForm2, HospitalSubForm3, HospitalSubForm4,
                    HospitalSubForm5, HospitalSubForm6, HospitalSubForm7,
                    HospitalSubForm8, IndicatorsForm, NewHospitalForm,
                    OperationsSubForm1, OperationsSubForm2, OperationsSubForm3,
                    OperationsSubForm4, OperationsSubForm5, OperationsSubForm6,
                    OperationsSubForm7, PostOperationsSubForm1,
                    PostOperationsSubForm2, PostOperationsSubForm3,
                    PostOperationsSubForm4, PostOperationsSubForm5,
                    PreoperativeForm, ProfileSubForm1, ProfileSubForm2,
                    ProfileSubForm3, ProfileSubForm4, ProfileSubForm5,
                    ProfileSubForm6, ProfileSubForm7, ProfileSubForm8,
                    ProfileSubForm9, ProsthesisForm, TelerentgenographyForm)
from .models import (Diagnose, History, HistoryEvent, IndicatorValue,
                     Operation, OperationComp, OperationLog, Patient)

from ..analytics import db_tools

history_blueprint = Blueprint('history',
                            __name__,
                            template_folder='..templates/history')

tempdirectory = tempfile.gettempdir()

@history_blueprint.route('/download_data', methods = ['GET','POST'])
@login_required
def download_data():
    flash('Выгрузка формируется. Подождите.', category="info")

    hist_data = db_tools.get_short_hist_data()
    file_path = os.path.join(os.path.dirname(__file__),'Histories.xlsx')
    print(os.path.dirname(__file__))
    print(file_path) 
    try:
        hist_data.to_excel(file_path, engine='openpyxl')
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f'Произошла ошибка: {e}', category="danger")
        return redirect(url_for('main.index'))  


@history_blueprint.route('/download_report', methods = ['GET','POST'])
@login_required
def download_report():
    flash('Отчет формируется. Подождите.', category="info")
    env = os.environ.get("APP_CONFIG")
    if env.capitalize() == 'Production':
        command = './venv/bin/jupyter nbconvert --to html --no-input ikp.ipynb --output ikp_report.html'
    else:
        command = 'jupyter nbconvert --to html --no-input ikp.ipynb --output ikp_report.html'
    args = shlex.split(command)
    try:
        subprocess.Popen(args) 
        return send_file('../ikp_report.html', as_attachment=True)
    except Exception as e:
        flash(f'Произошла ошибка: {e}', category="danger")
<<<<<<< HEAD
        return redirect(url_for('main.index'))

=======
        return redirect(url_for('main.index'))  


        
>>>>>>> 42290f026dd11bd2cfd22caaab844b97e64cc7f7
# Загрузка персональной информации из файла
@history_blueprint.route('/load_personal_data', methods = ['GET','POST'])
@login_required
def load_personal_data():

    if request.method == 'POST':
        if request.files:
            personal_data_file = request.files['personal_data']
            personal_data_filename = secure_filename(personal_data_file.filename)
            if personal_data_filename == '':
                flash('Выберите файл', category="warning")
                return redirect(url_for('history.history_select'))

            path_name = os.path.join(tempdirectory,personal_data_filename)
            personal_data_file.save(path_name)
            session['file_name'] = path_name
            try:
                pd_frame = pd.read_excel(path_name, 'fio')
            except:
                flash('Выбранный файл имеет некорректный формат. Необходим excel файл с персональными данными!', category="danger")
            else:
                personal_data_list = pd_frame.to_dict(orient='records')

                for row in personal_data_list:
                    digest = md5(row['snils'].lower().encode('utf-8')).hexdigest()
                    row['digest'] = digest

                #print(personal_data_list)
                session['personal_data_list'] = personal_data_list
                flash('Файл с персональными данными загружен', category='info')


    return redirect(url_for('history.history_select'))

# Замена персональных данных (СНИЛС)
@history_blueprint.route('/replace_personal_data', methods = ['GET','POST'])
@login_required
def replace_personal_data():
    # Список персональных данных
    personal_data_list = session.get('personal_data_list')
    # Ищем пациентов по старому СНИЛС
    for p_data in personal_data_list:        
        new_snils = str(p_data['new_snils'])
        print(f'Новый СНИЛС:{new_snils}')
        if new_snils.strip() != 'nan':        
            # Получим пациента по СНИЛС
            old_snils_hash = Patient.get_snils_hash(p_data['snils'])
            patient = Patient.get_patient_by_snils(old_snils_hash)
            i = 0 # Индикатор произведенной замены
            if patient:
                # Замена СНИЛС
                new_snils_hash = Patient.get_snils_hash(p_data['new_snils'])
                patient.snils_hash = new_snils_hash
                db.session.add(patient)
                db.session.commit()
                i += 1
                flash(f"СНИЛС {p_data['snils']} был скорректирован на {p_data['new_snils']}", category='info')
                #p_data['snils'] = p_data['new_snils']
                #session['personal_data_list'] = personal_data_list      
            if i > 0:
                flash('Была произведена корректировка СНИЛС! Не забудьте поменять СНИЛС в файле с персональными данными!', category='warning')
            else:
                flash('Изменений в системе не выпонено', category='info')

    return redirect(url_for('history.history_select'))


# Список историй болезни
@history_blueprint.route('/history_select', methods = ['GET','POST'])
@login_required
def history_select():

    FilterForm = HistoryFilterForm()
    page = request.args.get('page',1,type=int)

    clinic_filter_id = session.get('clinic_filter_id')
    hist_number_filter = session.get('hist_number_filter')
    group_filter_id = session.get('group_filter_id')
    snils_filter_hash = session.get('snils_filter_hash')
    personal_data_list = session.get('personal_data_list')
    history_list = History.query.join(Patient, History.patient_id==Patient.id).order_by(History.date_in)
    if clinic_filter_id is not None:
        history_list = history_list.filter(History.clinic_id==clinic_filter_id)
    if group_filter_id is not None:
        history_list = history_list.filter(History.research_group_id==group_filter_id)
    if hist_number_filter is not None and hist_number_filter != '':
        history_list = history_list.filter(History.hist_number==hist_number_filter)

    if snils_filter_hash is not None:
        patient = Patient.query.filter(Patient.snils_hash==snils_filter_hash).first()
        if patient is not None:
            history_list = history_list.filter(History.patient_id==patient.id)


    pagination =  history_list.paginate(page,5,error_out=False)
    histories = pagination.items

    if FilterForm.submit_filter.data and FilterForm.validate_on_submit():
# Фильтрация списка
        history_list = History.query.order_by(History.date_in)
        if FilterForm.clinic_filter.data != 0:
# Выбрано значение ( не All)
            history_list = history_list.filter(History.clinic_id==FilterForm.clinic_filter.data)
            session['clinic_filter_id']= FilterForm.clinic_filter.data
# Выбрано значение ALL - снять фильтр
        if FilterForm.clinic_filter.data == 0:
            session['clinic_filter_id'] = None

        if FilterForm.group_filter.data != 0:
# Выбрано значение ( не All)
            history_list = history_list.filter(History.research_group_id==FilterForm.group_filter.data)
            session['group_filter_id']= FilterForm.group_filter.data
# Выбрано значение ALL - снять фильтр
        if FilterForm.group_filter.data == 0:
            session['group_filter_id'] = None

        if FilterForm.hist_number_filter.data != '' and FilterForm.hist_number_filter.data is not None:
# Выбрано значение ( не All)
            history_list = history_list.filter(History.hist_number==FilterForm.hist_number_filter.data)
            session['hist_number_filter']= FilterForm.hist_number_filter.data
# Выбрано значение ALL - снять фильтр
        if FilterForm.hist_number_filter.data == '' or FilterForm.hist_number_filter.data is None:
            session['hist_number_filter'] = None


        if FilterForm.snils_filter.data != '':
# Выбрано значение ( не All)
            digest = md5(FilterForm.snils_filter.data.lower().encode('utf-8')).hexdigest()
            patient = Patient.query.filter(Patient.snils_hash==digest).first()
            if patient != None:
                history_list = history_list.filter(History.patient_id==patient.id)
                session['snils_filter_hash']= digest
            else:
                flash('Пациента с указанным СНИЛС не существует', category='warning')
                session['snils_filter_hash'] = None
                FilterForm.snils_filter.data = ''


# Выбрано значение ALL - снять фильтр
        if FilterForm.snils_filter.data == '':
            session['snils_filter_hash'] = None


        pagination =  history_list.paginate(page,5,error_out=False)
        histories = pagination.items


    if personal_data_list:
        # Если загружены персональные данные, то попытаемся определить ФИО по хэш снилса
        for i in histories:
            current_patient = Patient.query.get(i.patient_id)
            finded_snils = next((row for row in personal_data_list if row['digest']==current_patient.snils_hash), None)
            print(finded_snils)
            if finded_snils:
                i.__dict__['fio'] = finded_snils['fio']
                i.__dict__['snils'] = finded_snils['snils']
  
    file_name = ''
    if session.get('path_name'):
        file_name = session.get('path_name')


    return render_template('history/history_select.html', HistoryFilterForm=FilterForm,
                            title='Поиск истории болезни', histories=histories, pagination=pagination, 
                            personal_data_list=personal_data_list, file_name=file_name)


# Редактирование истории болезни
@history_blueprint.route('/history_edit/<h>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - History.id
# pill - номер закладки в форме
@login_required
def history_edit(h, pill):
    history_obj = History.query.get(h)

    HistoryMainForm_ = HistoryMainForm()
    IndicatorsForm_ = IndicatorsForm()
    HistoryMainDiagnosForm_ = HistoryMainDiagnosForm()
    HistoryOtherDiagnosForm_ = HistoryOtherDiagnosForm()
    HistioryNewAmbulanceForm_ = HistioryNewAmbulanceForm()
    NewHospitalForm_ = NewHospitalForm()

        # сохранение истории болезни
    if HistoryMainForm_.submit.data and HistoryMainForm_.validate_on_submit():
        pill = 1
        if history_obj is None:
            # Это ввод новой истории
            snils = request.form.get('snils')
            history_obj = CreateHistory(HistoryMainForm_, snils)
        else:
            # Обновление истории
            history_obj = UpdateHistory(HistoryMainForm_, h)

        if  history_obj is not None:
            flash('Данные сохранены', category='info')
            h = history_obj.id

        return redirect(url_for('history.history_edit', h=h, pill=pill))


    if HistoryMainDiagnosForm_.submit.data and HistoryMainDiagnosForm_.validate_on_submit():
        pill = 3
        main_diagnose = AddMainDiagnos(HistoryMainDiagnosForm_, history_obj)
        if main_diagnose is not None:
            flash('Данные сохранены', category='info')

        return redirect(url_for('history.history_edit', h=history_obj.id, pill=pill))

    if HistoryOtherDiagnosForm_.submit.data and HistoryOtherDiagnosForm_.validate_on_submit():
        pill = 3
        other_diagnose = AddOtherDiagnos(HistoryOtherDiagnosForm_, history_obj)
        if other_diagnose is not None:
            flash('Данные сохранены', category='info')

        return redirect(url_for('history.history_edit', h=history_obj.id, pill=pill))

    if HistioryNewAmbulanceForm_.submit.data: # and HistioryNewAmbulanceForm_.validate_on_submit():
        pill = 4
        # Проверка существования такого типа приема
        hisory_event = HistoryEvent.query.filter(HistoryEvent.history_id==h, HistoryEvent.event_id==HistioryNewAmbulanceForm_.event.data).first()
        if hisory_event is not None and hisory_event.event_id != 11:
            # Амбулаторные приемы одинаковых типов заводить нельзя - кроме ежегодных после операции
            flash('Амбулаторный прием такого типа уже существует', category='warning')
            return redirect(url_for('history.history_edit', h=history_obj.id, pill=pill))
        else:
            # Переход в форму амбулаторного приема
            if HistioryNewAmbulanceForm_.event.data == 2:
                # Прием перед госпитализацией
                return redirect(url_for('history.ambulance_edit', h=history_obj.id, h_e='0', e_type=HistioryNewAmbulanceForm_.event.data, pill=1))
            elif HistioryNewAmbulanceForm_.event.data == 9 or HistioryNewAmbulanceForm_.event.data == 10 or HistioryNewAmbulanceForm_.event.data == 11:
                # Прием через 3,6 и 12 месяцев после
                # Можно заводить только при наличии госпитализации и операции
                operation_obj = Operation.query.filter_by(history_id=history_obj.id).first()
                if operation_obj:
                    hospital_obj = HistoryEvent.query.filter_by(history_id=history_obj.id, event_id=3).first()
                else:
                    hospital_obj = None

                if operation_obj and hospital_obj:
                    if HistioryNewAmbulanceForm_.event.data == 9 or HistioryNewAmbulanceForm_.event.data == 10:
                        return redirect(url_for('history.ambulance3_edit', h=history_obj.id, hospital_id = history_obj.id,
                                        operation_id = operation_obj.id, h_e='0', e_type=HistioryNewAmbulanceForm_.event.data, pill=1))
                    else:
                        return redirect(url_for('history.ambulance12_edit', h=history_obj.id, hospital_id = history_obj.id,
                                        operation_id = operation_obj.id, h_e='0', e_type=HistioryNewAmbulanceForm_.event.data, pill=1))
                else:
                    flash('Амбулаторный прием такого типа можно заводить только при наличии данных об операции и госпитализации', category='warning')
                    return redirect(url_for('history.history_edit', h=history_obj.id, pill=pill))

            #elif HistioryNewAmbulanceForm_.event.data == 11:
                # Прием через год после
            #    return redirect(url_for('history.ambulance12_edit', h=history_obj.id, h_e='0', e_type=HistioryNewAmbulanceForm_.event.data, pill=1))

    if NewHospitalForm_.submit.data and NewHospitalForm_.validate_on_submit():
        # Переход в форму госпитализации
        # Проверка существования такого типа приема
        hospital_event = HistoryEvent.query.filter(HistoryEvent.history_id==h, HistoryEvent.event_id==3).first()
        if hospital_event is not None:
            flash('Госпитализация уже существует', category='warning')
            return redirect(url_for('history.hospital_edit', h=history_obj.id, h_e=hospital_event.id, pill=1))
        else:
            return redirect(url_for('history.hospital_edit', h=history_obj.id, h_e='0', pill=1))

    if history_obj is not None:
        # Заполнение формы данными из базы
        form_list = FillHistoryForm(HistoryMainForm_, IndicatorsForm_, HistoryMainDiagnosForm_, history_obj)
        HistoryMainForm_ = form_list[0]
        IndicatorsForm_ = form_list[1]
        HistoryMainDiagnosForm_ = form_list[2]
        history_event_id = form_list[3].id
        items = form_list[4]
        diagnoses_items = form_list[5]
        ambulance_events = form_list[6]
        hospital_events = form_list[7]
        # Определим ФИО и СНИЛС если они загружены в сессию
        personal_data_list = session.get('personal_data_list')
        if personal_data_list:
            current_patient = Patient.query.get(history_obj.patient_id)
            personal_data = next((row for row in personal_data_list if row['digest']==current_patient.snils_hash ), None)
        else:
            personal_data = None


    else:
        items = []
        history_event_id = 0
        diagnoses_items = []
        ambulance_events = []
        hospital_events = []
        personal_data = None

    return render_template('history/history_edit.html', history = history_obj, HistoryMainForm=HistoryMainForm_,
                            h=h, items = items, IndicatorsForm=IndicatorsForm_,
                            HistoryMainDiagnosForm = HistoryMainDiagnosForm_,
                            HistoryOtherDiagnosForm = HistoryOtherDiagnosForm_,
                            HistioryNewAmbulanceForm = HistioryNewAmbulanceForm_,
                            NewHospitalForm = NewHospitalForm_,
                            history_event_id = history_event_id,
                            diagnoses_items = diagnoses_items,
                            ambulance_events = ambulance_events,
                            hospital_events = hospital_events,
                            personal_data = personal_data,
                            pill=pill)

# Сохранение показателей первичного обращения
@history_blueprint.route('/save_indicators/<h>/<h_e>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# h_e - HistoryEvents.id
# pill - номер закладки в форме
def save_indicators(h, h_e, pill):
    history_obj = History.query.get(h)
    history_event = HistoryEvent.query.get(h_e)
    event_obj = Event.query.get(history_event.event_id)
    event_type = event_obj.type
    print(history_event)

    if 'save_indicators' in request.form:

        # Группа показателей
        indicator_group = request.form.get('indicator_group')
        print(indicator_group)

        if indicator_group == '2':
            # Это данные инструментальных исследований
            # Сначала сохраняем протез
            # Сохраняем протез с привязкой к основному диагнозу
            diagnosis = history_obj.get_diagnoses()[1]
            if diagnosis:
                diagnosis.prosthesis_id = request.form.get("prosthesis")
                db.session.add(diagnosis)
            else:
                flash('Отсутствует основной диагноз. Протез не сохранен!', category='danger')
                return redirect(url_for('history.hospital_edit', h=h, h_e=h_e, pill=pill))

            indicators_date_begin = None
            if request.form.get('indicators_date_begin'):
                indicators_date_begin = datetime.strptime(request.form.get('indicators_date_begin'), '%Y-%m-%d').date()
            text_values_1 = request.form.getlist('text_value_1')
            text_values_2 = request.form.getlist('text_value_2')
            text_values_3 = request.form.getlist('text_value_3')
            text_values_4 = request.form.getlist('text_value_4')
            text_values_5 = request.form.getlist('select_value')
            ids = request.form.getlist('indicator')
            for i, id in enumerate(ids):

                indicator_pzp = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Передне-задняя проекция',
                                                            IndicatorValue.indicator_id==id).first()
                if indicator_pzp:
                    indicator_pzp.text_value = text_values_1[i]
                    indicator_pzp.date_value = indicators_date_begin
                    db.session.add(indicator_pzp)

                indicator_bp = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Боковая проекция',
                                                            IndicatorValue.indicator_id==id).first()
                if indicator_bp:
                    indicator_bp.text_value = text_values_2[i]
                    indicator_bp.date_value = indicators_date_begin
                    db.session.add(indicator_bp)

                indicator_pz = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Планируемое значение',
                                                            IndicatorValue.indicator_id==id).first()
                if indicator_pz:
                    indicator_pz.text_value = text_values_3[i]
                    indicator_pz.date_value = indicators_date_begin
                    db.session.add(indicator_pz)

                indicator_fz = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Фактическое значение',
                                                            IndicatorValue.indicator_id==id).first()
                if indicator_fz:
                    indicator_fz.text_value = text_values_4[i]
                    indicator_fz.date_value = indicators_date_begin
                    db.session.add(indicator_fz)

                indicator_s = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Совпадение',
                                                            IndicatorValue.indicator_id==id).first()
                if indicator_s:
                    indicator_s.text_value = text_values_5[i]
                    indicator_s.date_value = indicators_date_begin
                    db.session.add(indicator_s)

            try:
                db.session.commit()
            except Exception as e:
                flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                db.session.rollback()
            else:
                flash('Данные сохранены', category='info')

        elif indicator_group == '3':
            # Это Телерентгенография
            # Может сохраняться из госпитализации или амбулаторного приема
            # Сохраняется по разному
            if event_type == '3':
                # Госпитализация - сохраняется на срезах
                indicators_date_begin = None
                if request.form.get('indicators_date_begin'):
                    indicators_date_begin = datetime.strptime(request.form.get('indicators_date_begin'), '%Y-%m-%d').date()
                num_values_1 = request.form.getlist('num_value_1')
                num_values_2 = request.form.getlist('num_value_2')
                ids = request.form.getlist('indicator')
                for i, id in enumerate(ids):

                    indicator_zn = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Значение',
                                                                IndicatorValue.indicator_id==id).first()
                    if indicator_zn:
                        if num_values_1[i] == '':
                            num_values_1[i] = 0
                        indicator_zn.num_value = int(num_values_1[i])
                        indicator_zn.date_value = indicators_date_begin
                        db.session.add(indicator_zn)

                    indicator_po = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='План операции',
                                                                IndicatorValue.indicator_id==id).first()
                    if indicator_po:
                        if num_values_2[i] == '':
                            num_values_2[i] = 0
                        indicator_po.num_value = int(num_values_2[i])
                        indicator_po.date_value = indicators_date_begin
                        db.session.add(indicator_po)

                try:
                    db.session.commit()
                except Exception as e:
                    flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                    db.session.rollback()
                else:
                    flash('Данные сохранены', category='info')

            elif event_type in ['5']:
                # Послеоперационное наблюдение  - сохраняется на срезах
                indicators_date_begin = None
                if request.form.get('indicators_date_begin'):
                    indicators_date_begin = datetime.strptime(request.form.get('indicators_date_begin'), '%Y-%m-%d').date()
                num_values_1 = request.form.getlist('num_value_1')
                num_values_2 = request.form.getlist('num_value_2')
                ids = request.form.getlist('indicator')
                for i, id in enumerate(ids):

                    indicator_zn = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Значение',
                                                                IndicatorValue.indicator_id==id).first()
                    if indicator_zn:
                        if num_values_1[i] == '':
                            num_values_1[i] = 0
                        indicator_zn.num_value = int(num_values_1[i])
                        #indicator_zn.date_value = indicators_date_begin
                        db.session.add(indicator_zn)

                    indicator_norm = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Норма',
                                                                IndicatorValue.indicator_id==id).first()
                    if indicator_norm:
                        if num_values_2[i] == '':
                            num_values_2[i] = 0
                        indicator_norm.num_value = int(num_values_2[i])
                        #indicator_norm.date_value = indicators_date_begin
                        db.session.add(indicator_norm)

                    indicator_out = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Выход за пределы нормы',
                                                                IndicatorValue.indicator_id==id).first()
                    if indicator_out and indicator_norm and indicator_zn:
                        if ( indicator_zn.num_value - indicator_norm.num_value ) > 3:
                            indicator_out.text_value = '+'
                        elif ( indicator_norm.num_value - indicator_zn.num_value ) > 3:
                            indicator_out.text_value = '-'
                        else:
                            indicator_out.text_value = '0'
                        #indicator_out.date_value = indicators_date_begin
                        db.session.add(indicator_out)
                try:
                    db.session.commit()
                except Exception as e:
                    flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                    db.session.rollback()
                else:
                    flash('Данные сохранены', category='info')
            elif event_type == '2' and event_obj.id == 11:
                # Амбулаторный прием - через год  - сохраняется на срезах
                indicators_date_begin = None
                if request.form.get('indicators_date_begin'):
                    indicators_date_begin = datetime.strptime(request.form.get('indicators_date_begin'), '%Y-%m-%d').date()
                num_values_1 = request.form.getlist('num_value_1')
                num_values_2 = request.form.getlist('num_value_2')
                ids = request.form.getlist('indicator')
                for i, id in enumerate(ids):

                    indicator_zn = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Значение',
                                                                IndicatorValue.indicator_id==id).first()
                    if indicator_zn:
                        if num_values_1[i] == '':
                            num_values_1[i] = 0
                        indicator_zn.num_value = int(num_values_1[i])
                        #indicator_zn.date_value = indicators_date_begin
                        db.session.add(indicator_zn)

                    indicator_norm = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Норма',
                                                                IndicatorValue.indicator_id==id).first()
                    if indicator_norm:
                        if num_values_2[i] == '':
                            num_values_2[i] = 0
                        indicator_norm.num_value = int(num_values_2[i])
                        #indicator_norm.date_value = indicators_date_begin
                        db.session.add(indicator_norm)

                    indicator_out = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Выход за пределы нормы',
                                                                IndicatorValue.indicator_id==id).first()
                    if indicator_out and indicator_norm and indicator_zn:
                        if ( indicator_zn.num_value - indicator_norm.num_value ) > 3:
                            indicator_out.text_value = '+'
                        elif ( indicator_norm.num_value - indicator_zn.num_value ) > 3:
                            indicator_out.text_value = '-'
                        else:
                            indicator_out.text_value = '0'
                        #indicator_out.date_value = indicators_date_begin
                        db.session.add(indicator_out)
                try:
                    db.session.commit()
                except Exception as e:
                    flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                    db.session.rollback()
                else:
                    flash('Данные сохранены', category='info')

            else:
                # Это амбулаторный прием - сохраняем без срезов
                indicators_date_begin = None
                if request.form.get('indicators_date_begin'):
                    indicators_date_begin = datetime.strptime(request.form.get('indicators_date_begin'), '%Y-%m-%d').date()
                num_values = request.form.getlist('num_value')
                ids = request.form.getlist('indicator_id')
                for i, id in enumerate(ids):
                    indicator = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.id==id).first()
                    if indicator:
                        if num_values[i] == '':
                            num_values[i] = 0
                        indicator.num_value = int(num_values[i])
                        indicator.date_value = indicators_date_begin
                        db.session.add(indicator)

                try:
                    db.session.commit()
                except Exception as e:
                    flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                    db.session.rollback()
                else:
                    flash('Данные сохранены', category='info')

        elif indicator_group == '6':
            # Это КТ коленного сустава

            if event_type in ['5','2']:
                # Послеоперационное наблюдение  - сохраняется на срезах
                indicators_date_begin = None
                num_values_1 = request.form.getlist('num_value_1')
                num_values_2 = request.form.getlist('num_value_2')
                ids = request.form.getlist('indicator')
                for i, id in enumerate(ids):

                    indicator_zn = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Значение',
                                                                IndicatorValue.indicator_id==id).first()
                    if indicator_zn:
                        if num_values_1[i] == '':
                            num_values_1[i] = 0
                        indicator_zn.num_value = int(num_values_1[i])
                        #indicator_zn.date_value = indicators_date_begin
                        db.session.add(indicator_zn)

                    indicator_norm = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Норма',
                                                                IndicatorValue.indicator_id==id).first()
                    if indicator_norm:
                        if num_values_2[i] == '':
                            num_values_2[i] = 0
                        indicator_norm.num_value = int(num_values_2[i])
                        #indicator_norm.date_value = indicators_date_begin
                        db.session.add(indicator_norm)

                    indicator_out = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Выход за пределы нормы',
                                                                IndicatorValue.indicator_id==id).first()
                    if indicator_out and indicator_norm and indicator_zn:
                        if ( indicator_zn.num_value - indicator_norm.num_value ) > 3:
                            indicator_out.text_value = '+'
                        elif ( indicator_norm.num_value - indicator_zn.num_value ) > 3:
                            indicator_out.text_value = '-'
                        else:
                            indicator_out.text_value = '0'
                        #indicator_out.date_value = indicators_date_begin
                        db.session.add(indicator_out)
                try:
                    db.session.commit()
                except Exception as e:
                    flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                    db.session.rollback()
                else:
                    flash('Данные сохранены', category='info')


        elif indicator_group == '4':
            # Это предоперационные обследования
            select_values = request.form.getlist('select_value')
            ids = request.form.getlist('indicator_id')
            # Получим список всех показателей
            for i, id in enumerate(ids):
                indicator_value = IndicatorValue.query.get(id)
                if indicator_value:
                    if len(select_values) > i:
                        indicator_value.text_value = select_values[i]
                    db.session.add(indicator_value)
            try:
                db.session.commit()
            except Exception as e:
                flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                db.session.rollback()
            else:
                flash('Данные сохранены', category='info')

        elif indicator_group == '10':
            # Это тестирование бригады
            # Сохраняется из операции - на срезах

            indicators_date = None
            if request.form.get('indicators_date'):
                indicators_date = datetime.strptime(request.form.get('indicators_date'), '%Y-%m-%d').date()
            num_values_1 = request.form.getlist('num_value_1')
            num_values_2 = request.form.getlist('num_value_2')
            ids = request.form.getlist('indicator')
            for i, id in enumerate(ids):

                indicator_1 = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Реактивная тревожность',
                                                            IndicatorValue.indicator_id==id).first()
                if indicator_1:
                    if num_values_1[i] == '':
                        num_values_1[i] = 0
                    indicator_1.num_value = int(num_values_1[i])
                    indicator_1.date_value = indicators_date
                    db.session.add(indicator_1)

                indicator_2 = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e, IndicatorValue.slice=='Личностная тревожность',
                                                            IndicatorValue.indicator_id==id).first()
                if indicator_2:
                    if num_values_2[i] == '':
                        num_values_2[i] = 0
                    indicator_2.num_value = int(num_values_2[i])
                    indicator_2.date_value = indicators_date
                    db.session.add(indicator_2)

            try:
                db.session.commit()
            except Exception as e:
                flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                db.session.rollback()
            else:
                flash('Данные сохранены', category='info')



        elif indicator_group in ['11','1','8']:
            # Дата ввода показателей
            print(history_event)

            if request.form.get('date_begin'):
                history_event.date_begin = datetime.strptime(request.form.get('date_begin'), '%Y-%m-%d').date()
                db.session.add(history_event)
                try:
                    db.session.commit()
                except Exception as e:
                    flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                    db.session.rollback()
                else:
                    flash('Данные сохранены', category='info')
            # Это физические параметры
            num_values = request.form.getlist('num_value')
            comments = request.form.getlist('comment')
            ids = request.form.getlist('indicator_id')

            # Получим список всех показателей физ параметров истории болезни
            for i, id in enumerate(ids):
                indicator_value = IndicatorValue.query.get(id)

                if indicator_value:
                    # Сохранить дату показаний
                    if request.form.get('date_begin'):
                        indicator_value.date_value = datetime.strptime(request.form.get('date_begin'), '%Y-%m-%d').date()
                    if request.form.get('indicators_date_begin'):
                        indicator_value.date_value = datetime.strptime(request.form.get('indicators_date_begin'), '%Y-%m-%d').date()

                    if len(num_values) > i:
                        if num_values[i] == '':
                            num_values[i] = 0
                        indicator_value.num_value = num_values[i]
                    #print(len(comments))
                    if len(comments) > i:
                        indicator_value.comment = comments[i]

                    if indicator_group == '11' or indicator_group == '1':
                        # Расчет ИМТ
                        if i == 2 and int(num_values[0]) != 0:
                            indicator_value.num_value = int(num_values[1])/(int(num_values[0])/100)**2
                        elif i == 2 and int(num_values[0]) == 0:
                            indicator_value.num_value = 0
                        # Расчет объема движений
                        if i == 9 :
                            indicator_value.num_value  = int(num_values[7]) - int(num_values[8])

                    db.session.add(indicator_value)
            try:
                db.session.commit()
            except Exception as e:
                flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                db.session.rollback()
            else:
                flash('Данные сохранены', category='info')

        elif indicator_group == '5':
            # Это госпитализация - общие данные
            comments = request.form.getlist('comment')
            ids = request.form.getlist('indicator_id')
            # Получим список всех показателей
            for i, id in enumerate(ids):
                indicator_value = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e,\
                                                    IndicatorValue.indicator_id==id).first()
                if indicator_value:
                    # Сохранить дату показаний
                    if request.form.get('date_begin'):
                        indicator_value.date_value = datetime.strptime(request.form.get('date_begin'), '%Y-%m-%d').date()
                    if len(comments) > i:
                        indicator_value.comment = comments[i]
                    if id == '49':
                        indicator_value.text_value = request.form.get('claims')
                    if id == '50':
                        indicator_value.text_value = request.form.get('claims_time')
                    if id == '51':
                        indicator_value.text_value = request.form.get('diseases')
                    if id == '52':
                        indicator_value.text_value = request.form.get('traumas')
                    if id == '53':
                        indicator_value.text_value = request.form.get('smoking')
                    if id == '54':
                        indicator_value.text_value = request.form.get('alcohol')
                    if id == '55':
                        indicator_value.text_value = request.form.get('allergy')
                    if id == '56':
                        indicator_value.text_value = request.form.get('genetic')
                    db.session.add(indicator_value)
            try:
                db.session.commit()
            except Exception as e:
                flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                db.session.rollback()
            else:
                flash('Данные сохранены', category='info')
        elif indicator_group == '9':
            # Это операция - показатели
            comments = request.form.getlist('comment')
            ids = request.form.getlist('indicator_id')
            # Получим список всех показателей
            for i, id in enumerate(ids):
                # Сохранение даты начала операции в дату события
                history_event_obj = HistoryEvent.query.get(h_e)
                if request.form.get('operation_date_begin'):
                    history_event_obj.date_begin = datetime.strptime(request.form.get('operation_date_begin'), '%Y-%m-%d').date()

                indicator_value = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e,\
                                                    IndicatorValue.indicator_id==id).first()
                if indicator_value:
                    # Сохранить дату показаний
                    if request.form.get('operation_date_begin'):
                        indicator_value.date_value = datetime.strptime(request.form.get('operation_date_begin'), '%Y-%m-%d').date()
                    if len(comments) > i:
                        indicator_value.comment = comments[i]
                    if id == '77':
                        indicator_value.def_value = request.form.get('anesthesia')
                    if id == '78':
                        anesthesia_begin = datetime.strptime(str(request.form.get('operation_date_begin')) + str(request.form.get('anesthesia_begin')+':00'), '%Y-%m-%d%H:%M:%S')
                        #print(str(request.form.get('operation_date_begin')) + str(request.form.get('anesthesia_begin')+'00'))
                        indicator_value.date_time_value = anesthesia_begin
                    if id == '79':
                        anesthesia_end = datetime.strptime(str(request.form.get('operation_date_begin')) + str(request.form.get('anesthesia_end')+':00'), '%Y-%m-%d%H:%M:%S')
                        if anesthesia_end < anesthesia_begin:
                            anesthesia_end = anesthesia_end + timedelta(days=1)
                        indicator_value.date_time_value = anesthesia_end
                    if id == '80':
                        if anesthesia_begin and anesthesia_end:
                            delta = anesthesia_end - anesthesia_begin
                            anesthesia_duration = delta.total_seconds() // 60
                            indicator_value.num_value = anesthesia_duration
                    if id == '81':
                        indicator_value.def_value = request.form.get('surgical_access')
                    if id == '82':
                        indicator_value.def_value = request.form.get('operation_specificity')
                    if id == '83':
                        indicator_value.def_value = request.form.get('technical_difficulty')
                    if id == '84':
                        indicator_value.num_value = request.form.get('intraoperative_blood_loss')
                    if id == '85':
                        indicator_value.def_value = request.form.get('wound_drainage')
                    if id == '86':
                        indicator_value.num_value = request.form.get('amount_of_water')
                    if id == '87':
                        indicator_value.num_value = request.form.get('duration_drainage')
                    if id == '96':
                        indicator_value.def_value = request.form.get('intra_complications')
                    db.session.add(indicator_value)
            try:
                db.session.commit()
            except Exception as e:
                flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                db.session.rollback()
            else:
                flash('Данные сохранены', category='info')

        elif indicator_group == '13':
            # Это заключение
            comments = request.form.getlist('comment')
            ids = request.form.getlist('indicator_id')
            # Получим список всех показателей
            for i, id in enumerate(ids):
                indicator_value = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e,\
                                                    IndicatorValue.indicator_id==id).first()
                if indicator_value:
                    # Сохранить дату показаний
                    if request.form.get('date_begin'):
                        indicator_value.date_value = datetime.strptime(request.form.get('date_begin'), '%Y-%m-%d').date()
                    if len(comments) > i:
                        indicator_value.comment = comments[i]
                    if id == '97':
                        indicator_value.def_value = request.form.get('prostesis')
                    if id == '98':
                        indicator_value.date_value = request.form.get('date_delete')
                    if id == '99':
                        indicator_value.def_value = request.form.get('reason_delete')
                    if id == '100':
                        indicator_value.def_value = request.form.get('patient_is_live')
                    if id == '101':
                        indicator_value.date_value = request.form.get('date_died')
                    if id == '102':
                        indicator_value.def_value = request.form.get('reason_died')
                    if id == '104':
                        indicator_value.def_value = request.form.get('conclusions')
                    if id == '105':
                        indicator_value.def_value = request.form.get('recomendations')

                    db.session.add(indicator_value)
            try:
                db.session.commit()
            except Exception as e:
                flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                db.session.rollback()
            else:
                flash('Данные сохранены', category='info')

        elif indicator_group == '15':
            # Это рентгенография (описание)
            comments = request.form.getlist('comment')
            ids = request.form.getlist('indicator_id')
            # Получим список всех показателей
            for i, id in enumerate(ids):
                indicator_value = IndicatorValue.query.filter(IndicatorValue.history_event_id==h_e,\
                                                    IndicatorValue.indicator_id==id).first()
                if indicator_value:
                    # Сохранить дату показаний
                    if request.form.get('indicators_date_begin'):
                        indicator_value.date_value = datetime.strptime(request.form.get('indicators_date_begin'), '%Y-%m-%d').date()
                    if len(comments) > i:
                        indicator_value.comment = comments[i]
                    if id == '113':
                        indicator_value.def_value = request.form.get('zone_light1')
                    if id == '114':
                        indicator_value.def_value = request.form.get('zone_light2')

                    db.session.add(indicator_value)
            try:
                db.session.commit()
            except Exception as e:
                flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                db.session.rollback()
            else:
                flash('Данные сохранены', category='info')

    if event_type == '1':
        # Сохранение выполнено из первичного приема
        return redirect(url_for('history.history_edit', h=h, pill=pill))
    elif event_type == '2':
        # Сохранение выполнено из амбулаторного  приема
        if event_obj.id == 2:
            # Амбулаторный прием до госпитализации
            return redirect(url_for('history.ambulance_edit', h=h, h_e=h_e, e_type = event_obj.id, pill=pill))
        elif event_obj.id == 9 or event_obj.id == 10:
            # Сохранение выполнено из амбулаторного приема 3 или 6 месяцев
            operation_obj = Operation.query.filter_by(history_id=h).first()
            hospital_obj = HistoryEvent.query.get(operation_obj.hospital_id)
            return redirect(url_for('history.ambulance3_edit', h=h, hospital_id=hospital_obj.id, operation_id=operation_obj.id, h_e=h_e, e_type = event_obj.id, pill=pill))
        elif event_obj.id == 11:
            # Сохранение выполнено из амбулаторного приема 12 месяцев
            operation_obj = Operation.query.filter_by(history_id=h).first()
            hospital_obj = HistoryEvent.query.get(operation_obj.hospital_id)
            return redirect(url_for('history.ambulance12_edit', h=h, hospital_id=hospital_obj.id, operation_id=operation_obj.id, h_e=h_e, e_type = event_obj.id, pill=pill))
    elif event_type == '3':
        # Сохранение выполнено из госпитализации
        return redirect(url_for('history.hospital_edit', h=h, h_e=h_e, pill=pill))
    elif event_type == '4':
        # Сохранение выполнено из операции
        operation_obj = Operation.query.filter_by(history_event_id=h_e).first()
        return redirect(url_for('history.operation_edit', h=h, hospital_id=operation_obj.hospital_id, operation_id=operation_obj.id, pill=pill))
    elif event_type == '5' or event_type == '6' or event_type == '7' or event_type == '8':
        # Сохранение выполнено из послеоперационного наблюдения
        post_operation_obj = HistoryEvent.query.get(h_e)
        operation_obj = Operation.query.filter_by(history_event_id=post_operation_obj.parent_event_id).first()
        hospital_obj = HistoryEvent.query.get(operation_obj.hospital_id)
        return redirect(url_for('history.post_operation_edit', h=h, hospital_id=hospital_obj.id, operation_id=operation_obj.id, post_operation_id=h_e,
                                    e_type_id=post_operation_obj.event_id, pill=pill))


# История болезни / Диагнозы
@history_blueprint.route('/diagnose_delete/<h>/<d>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# d - Diagnoses.id
# pill - номер закладки в форме
def diagnose_delete(h,d,pill):
    diagnose = Diagnose.query.get(d)
    db.session.delete(diagnose)

    try:
        db.session.commit()
    except Exception as e:
        flash('Ошибка при сохранении данных: %s' % str(e), 'error')
        db.session.rollback()
    else:
        return redirect(url_for('history.history_edit', h=h, pill=pill))


# Редактирование амбулаторного приема
@history_blueprint.route('/ambulance_edit/<h>/<h_e>/<e_type>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# h_e - HistoryEvents.id
# e_type - Тип события
# pill - номер закладки в форме
@login_required
def ambulance_edit(h, h_e, e_type, pill):
    history_obj = History.query.get(h)
    if history_obj:
        # Определим ФИО и СНИЛС если они загружены в сессию
        personal_data_list = session.get('personal_data_list')
        if personal_data_list:
            current_patient = Patient.query.get(history_obj.patient_id)
            personal_data = next((row for row in personal_data_list if row['digest']==current_patient.snils_hash ), None)
        else:
            personal_data = None
    else:
        personal_data = None

    AmbulanceMainForm_ = AmbulanceMainForm()
    IndicatorsForm_ = IndicatorsForm()
    ProsthesisForm_ = ProsthesisForm()
    PreoperativeForm_ = PreoperativeForm()
    TelerentgenographyForm_ = TelerentgenographyForm()
    event_obj = Event.query.get(e_type)
    AmbulanceMainForm_.event.data = event_obj.id
    ambulance_event = HistoryEvent.query.get(h_e)

    if AmbulanceMainForm_.submit.data and AmbulanceMainForm_.validate_on_submit():
        pill = 1

        if ambulance_event is None:
            # Это ввод нового амбулаторного приема
            ambulance_event = CreateAmbulance(AmbulanceMainForm_, history_obj, event_obj)

        else:
            # Обновление амбулаторного приема
            ambulance_event = HistoryEvent.query.get(h_e)
            UpdateAmbulance(AmbulanceMainForm_, ambulance_event)

        if ambulance_event is not None:
            flash('Данные сохранены', category='info')
            return redirect(url_for('history.ambulance_edit', h=h, h_e=ambulance_event.id, e_type=e_type, pill=pill))

        else:
            # Ввод не выполнен. Сохранение новой формы не завершено.
            return redirect(url_for('history.ambulance_edit', h=h, h_e='0', e_type=e_type, pill=pill))

    if ProsthesisForm_.submit.data and ProsthesisForm_.validate_on_submit():
        pill = 3
        # Сохраняем протез с привязкой к основному диагнозу
        diagnosis = history_obj.get_diagnoses()[1]
        prothesis = Prosthesis.query.get(ProsthesisForm_.prosthesis.data)

        if diagnosis:
            diagnosis.prosthesis_id = ProsthesisForm_.prosthesis.data
            db.session.add(diagnosis)
            try:
                db.session.commit()
            except Exception as e:
                flash('Ошибка при сохранении данных: %s' % str(e), 'error')
                db.session.rollback()
            else:
                flash('Данные сохранены', category='info')
        else:
            flash('Отсутствует основной диагноз', category='danger')

        return redirect(url_for('history.ambulance_edit', h=h, h_e=ambulance_event.id, e_type=e_type, pill=pill))


    if ambulance_event is not None:
        # Открываем уже сущестующее посещение
        # Заполнение формы данными из базы
        form_list = FillAmbulanceForm(AmbulanceMainForm_, IndicatorsForm_, ProsthesisForm_, history_obj, ambulance_event)
        AmbulanceMainForm_ = form_list[0]
        items = form_list[1]
        items_2 = form_list[2]
        items_3 = form_list[3]
        items_4 = form_list[4]

    else:
        items = []
        items_2 = []
        items_3 = []
        items_4 = []

    return render_template('history/ambulance.html', AmbulanceMainForm = AmbulanceMainForm_,
                            IndicatorsForm=IndicatorsForm_, ProsthesisForm = ProsthesisForm_,
                            TelerentgenographyForm=TelerentgenographyForm_,
                            PreoperativeForm = PreoperativeForm_,
                            h=h, history_event_id = h_e,
                            event=event_obj, history=history_obj, items = items,
                            items_2=items_2, items_3 = items_3,
                            items_4 = items_4, personal_data = personal_data, pill=pill)

# Редактирование амбулаторного приема через 3 и 6 месяцев
@history_blueprint.route('/ambulance3_edit/<h>/<hospital_id>/<operation_id>/<h_e>/<e_type>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# hospital_id
# oparation_id
# h_e - HistoryEvents.id
# e_type - Тип события
# pill - номер закладки в форме
@login_required
def ambulance3_edit(h, hospital_id, operation_id, h_e, e_type, pill):
    history_obj = History.query.get(h)
    if history_obj:
        # Определим ФИО и СНИЛС если они загружены в сессию
        personal_data_list = session.get('personal_data_list')
        if personal_data_list:
            current_patient = Patient.query.get(history_obj.patient_id)
            personal_data = next((row for row in personal_data_list if row['digest']==current_patient.snils_hash ), None)
        else:
            personal_data = None
    else:
        personal_data = None

    AmbulanceMainForm_ = AmbulanceMainForm()
    # Оценка функции сустава и качества жизни по шкалам
    Ambulance3SubForm1_ = Ambulance3SubForm1()
    # Осложнения
    Ambulance3SubForm2_ = Ambulance3SubForm2()
    # Заключение
    Ambulance3SubForm3_ = Ambulance3SubForm3()
    ProfileSubForm1_  = ProfileSubForm1()
    ProfileSubForm2_  = ProfileSubForm2()
    ProfileSubForm3_  = ProfileSubForm3()
    ProfileSubForm4_  = ProfileSubForm4()
    ProfileSubForm5_  = ProfileSubForm5()
    ProfileSubForm6_  = ProfileSubForm6()
    ProfileSubForm7_  = ProfileSubForm7()
    ProfileSubForm8_  = ProfileSubForm8()
    ProfileSubForm9_  = ProfileSubForm9()
    event_obj = Event.query.get(e_type)
    AmbulanceMainForm_.event.data = event_obj.id
    ambulance_event = HistoryEvent.query.get(h_e)
    operation_obj = Operation.query.get(operation_id)
    hospital_obj = HistoryEvent.query.get(hospital_id)


    if AmbulanceMainForm_.submit.data and AmbulanceMainForm_.validate_on_submit():
        pill = 1

        if ambulance_event is None:
            # Это ввод нового амбулаторного приема
            ambulance_event = CreateAmbulance(AmbulanceMainForm_, history_obj, event_obj)

        else:
            # Обновление амбулаторного приема
            ambulance_event = HistoryEvent.query.get(h_e)
            UpdateAmbulance(AmbulanceMainForm_, ambulance_event)

        if ambulance_event is not None:
            flash('Данные сохранены', category='info')
            return redirect(url_for('history.ambulance3_edit', h=h, hospital_id = hospital_id, operation_id=operation_id, h_e=ambulance_event.id, e_type=e_type, pill=pill))

        else:
            # Ввод не выполнен. Сохранение новой формы не завершено.
            return redirect(url_for('history.ambulance3_edit', h=h, hospital_id = hospital_id, operation_id=operation_id, h_e='0', e_type=e_type, pill=pill))

    if Ambulance3SubForm2_.submit.data and Ambulance3SubForm2_.validate_on_submit():
        # Осложнения
        pill = 3
        date_begin = Ambulance3SubForm2_.date_created.data
        complication_id = Ambulance3SubForm2_.complication.data
        operation_complication_obj = OperationComp.query.filter_by(complication_id=complication_id, operation_id=operation_obj.id).first()
        if operation_complication_obj:
            # Такое осложнение уже заведено
            flash('Такое осложнение уже заведено', category='warning')
            return redirect(url_for('history.ambulance3_edit', h=h, hospital_id = hospital_id, operation_id=operation_id, h_e=h_e, e_type=e_type, pill=pill))
        else:
            # Добавить осложнение
            operation_complication_obj = OperationComp()
            operation_complication_obj.clinic_id = operation_obj.clinic_id
            operation_complication_obj.history_id = operation_obj.history_id
            operation_complication_obj.operation_id = operation_obj.id
            operation_complication_obj.patient_id = operation_obj.patient_id
            operation_complication_obj.date_begin = date_begin
            operation_complication_obj.complication_id = complication_id

            db.session.add(operation_complication_obj)
            db.session.commit()

        flash('Данные сохранены', category='info')
        return redirect(url_for('history.ambulance3_edit', h=h, hospital_id = hospital_id, operation_id=operation_id, h_e=h_e, e_type=e_type, pill=pill))

    if ambulance_event is not None:
        # Открываем уже сущестующее посещение
        # Заполнение формы данными из базы
        form_list = FillAmbulance3Form(AmbulanceMainForm_, Ambulance3SubForm1_, Ambulance3SubForm2_, Ambulance3SubForm3_, history_obj, hospital_obj, operation_obj, ambulance_event)
        AmbulanceMainForm_ = form_list[0]
        Ambulance3SubForm1_ = form_list[1]
        Ambulance3SubForm2_ = form_list[2]
        Ambulance3SubForm3_ = form_list[3]

        items_1 = form_list[4]
        items_13 = form_list[5]
        items_profile = form_list[6]
        items_comp = form_list[7]

    else:
        items_1 = []
        items_13 = []
        items_profile = []
        items_comp = []


    return render_template('history/ambulance3.html', AmbulanceMainForm = AmbulanceMainForm_,
                            Ambulance3SubForm1=Ambulance3SubForm1_, Ambulance3SubForm2 = Ambulance3SubForm2_,
                            Ambulance3SubForm3=Ambulance3SubForm3_, ProfileSubForm1 = ProfileSubForm1_,
                            ProfileSubForm2  = ProfileSubForm2_, ProfileSubForm3  = ProfileSubForm3_,
                            ProfileSubForm4  = ProfileSubForm4_, ProfileSubForm5  = ProfileSubForm5_,
                            ProfileSubForm6  = ProfileSubForm6_, ProfileSubForm7  = ProfileSubForm7_,
                            ProfileSubForm8  = ProfileSubForm8_, ProfileSubForm9 = ProfileSubForm9_,
                            h=h, hospital=hospital_obj, operation=operation_obj, history_event_id = h_e,
                            event=event_obj, history=history_obj,
                            items_1=items_1, items_13 = items_13, items_profile = items_profile, items_comp = items_comp,
                            personal_data = personal_data, pill=pill)


# Редактирование амбулаторного приема через 12 месяцев
@history_blueprint.route('/ambulance12_edit/<h>/<hospital_id>/<operation_id>/<h_e>/<e_type>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# hospital_id
# oparation_id
# h_e - HistoryEvents.id
# e_type - Тип события
# pill - номер закладки в форме
@login_required
def ambulance12_edit(h, hospital_id, operation_id, h_e, e_type, pill):
    history_obj = History.query.get(h)
    if history_obj:
        # Определим ФИО и СНИЛС если они загружены в сессию
        personal_data_list = session.get('personal_data_list')
        if personal_data_list:
            current_patient = Patient.query.get(history_obj.patient_id)
            personal_data = next((row for row in personal_data_list if row['digest']==current_patient.snils_hash ), None)
        else:
            personal_data = None
    else:
        personal_data = None

    AmbulanceMainForm_ = AmbulanceMainForm()
    # Оценка функции сустава и качества жизни по шкалам
    Ambulance3SubForm1_ = Ambulance3SubForm1()
    # Осложнения
    Ambulance3SubForm2_ = Ambulance3SubForm2()
    # Заключение
    Ambulance3SubForm4_ = Ambulance3SubForm4()
    # Рентгенография
    Ambulance3SubForm5_ = Ambulance3SubForm5()
    # Телерентгенография
    Ambulance3SubForm6_ = Ambulance3SubForm6()
    # КТ
    Ambulance3SubForm7_ = Ambulance3SubForm7()
    # Формы для анкет
    ProfileSubForm1_  = ProfileSubForm1()
    ProfileSubForm2_  = ProfileSubForm2()
    ProfileSubForm3_  = ProfileSubForm3()
    ProfileSubForm4_  = ProfileSubForm4()
    ProfileSubForm5_  = ProfileSubForm5()
    ProfileSubForm6_  = ProfileSubForm6()
    ProfileSubForm7_  = ProfileSubForm7()
    ProfileSubForm8_  = ProfileSubForm8()
    ProfileSubForm9_  = ProfileSubForm9()


    event_obj = Event.query.get(e_type)
    AmbulanceMainForm_.event.data = event_obj.id
    ambulance_event = HistoryEvent.query.get(h_e)
    operation_obj = Operation.query.get(operation_id)
    hospital_obj = HistoryEvent.query.get(hospital_id)


    if AmbulanceMainForm_.submit.data and AmbulanceMainForm_.validate_on_submit():
        pill = 1

        if ambulance_event is None:
            # Это ввод нового амбулаторного приема
            ambulance_event = CreateAmbulance(AmbulanceMainForm_, history_obj, event_obj)

        else:
            # Обновление амбулаторного приема
            ambulance_event = HistoryEvent.query.get(h_e)
            UpdateAmbulance(AmbulanceMainForm_, ambulance_event)

        if ambulance_event is not None:
            flash('Данные сохранены', category='info')
            return redirect(url_for('history.ambulance12_edit', h=h, hospital_id = hospital_id, operation_id=operation_id, h_e=ambulance_event.id, e_type=e_type, pill=pill))

        else:
            # Ввод не выполнен. Сохранение новой формы не завершено.
            return redirect(url_for('history.ambulance12_edit', h=h, hospital_id = hospital_id, operation_id=operation_id, h_e='0', e_type=e_type, pill=pill))

    if Ambulance3SubForm2_.submit.data and Ambulance3SubForm2_.validate_on_submit():
        # Осложнения
        pill = 3
        date_begin = Ambulance3SubForm2_.date_created.data
        complication_id = Ambulance3SubForm2_.complication.data
        operation_complication_obj = OperationComp.query.filter_by(complication_id=complication_id, operation_id=operation_obj.id).first()
        if operation_complication_obj:
            # Такое осложнение уже заведено
            flash('Такое осложнение уже заведено', category='warning')
            return redirect(url_for('history.ambulance12_edit', h=h, hospital_id = hospital_id, operation_id=operation_id, h_e=h_e, e_type=e_type, pill=pill))
        else:
            # Добавить осложнение
            operation_complication_obj = OperationComp()
            operation_complication_obj.clinic_id = operation_obj.clinic_id
            operation_complication_obj.history_id = operation_obj.history_id
            operation_complication_obj.operation_id = operation_obj.id
            operation_complication_obj.patient_id = operation_obj.patient_id
            operation_complication_obj.date_begin = date_begin
            operation_complication_obj.complication_id = complication_id

            db.session.add(operation_complication_obj)
            db.session.commit()

        flash('Данные сохранены', category='info')
        return redirect(url_for('history.ambulance12_edit', h=h, hospital_id = hospital_id, operation_id=operation_id, h_e=h_e, e_type=e_type, pill=pill))

    if ambulance_event is not None:
        # Открываем уже сущестующее посещение
        # Заполнение формы данными из базы
        form_list = FillAmbulance12Form(AmbulanceMainForm_, Ambulance3SubForm1_, Ambulance3SubForm2_, Ambulance3SubForm4_,
                                            Ambulance3SubForm5_, Ambulance3SubForm6_, Ambulance3SubForm7_,
                                            history_obj, hospital_obj, operation_obj, ambulance_event)

        AmbulanceMainForm_ = form_list[0]
        Ambulance3SubForm1_ = form_list[1]
        Ambulance3SubForm2_ = form_list[2]
        Ambulance3SubForm4_ = form_list[3]
        Ambulance3SubForm5_ = form_list[4]
        Ambulance3SubForm6_ = form_list[5]
        Ambulance3SubForm7_ = form_list[6]

        items_1 = form_list[7]
        items_13 = form_list[8]
        items_profile = form_list[9]
        items_comp = form_list[10]
        items_3 = form_list[11]
        items_6 = form_list[12]
        items_15 = form_list[13]



    else:
        items_1 = []
        items_13 = []
        items_profile = []
        items_comp = []
        items_3 = []
        items_6 = []
        items_15 = []


    return render_template('history/ambulance12.html', AmbulanceMainForm = AmbulanceMainForm_,
                            Ambulance3SubForm1=Ambulance3SubForm1_, Ambulance3SubForm2 = Ambulance3SubForm2_,
                            Ambulance3SubForm4=Ambulance3SubForm4_, Ambulance3SubForm5=Ambulance3SubForm5_,
                            Ambulance3SubForm6=Ambulance3SubForm6_, Ambulance3SubForm7=Ambulance3SubForm7_,
                            ProfileSubForm1 = ProfileSubForm1_,
                            ProfileSubForm2  = ProfileSubForm2_, ProfileSubForm3  = ProfileSubForm3_,
                            ProfileSubForm4  = ProfileSubForm4_, ProfileSubForm5  = ProfileSubForm5_,
                            ProfileSubForm6  = ProfileSubForm6_, ProfileSubForm7  = ProfileSubForm7_,
                            ProfileSubForm8  = ProfileSubForm8_, ProfileSubForm9 = ProfileSubForm9_,
                            h=h, hospital=hospital_obj, operation=operation_obj, history_event_id = h_e,
                            event=event_obj, history=history_obj,
                            items_1=items_1, items_13 = items_13, items_profile = items_profile, items_comp = items_comp,
                            items_3 = items_3, items_6 = items_6, items_15 = items_15,
                            personal_data = personal_data, pill=pill)

# Редактирование госпитализации
@history_blueprint.route('/hospital_edit/<h>/<h_e>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# h_e - HistoryEvents.id
# pill - номер закладки в форме
@login_required
def hospital_edit(h, h_e, pill):
    history_obj = History.query.get(h)
    if history_obj:
        # Определим ФИО и СНИЛС если они загружены в сессию
        personal_data_list = session.get('personal_data_list')
        if personal_data_list:
            current_patient = Patient.query.get(history_obj.patient_id)
            personal_data = next((row for row in personal_data_list if row['digest']==current_patient.snils_hash ), None)
        else:
            personal_data = None
    else:
        personal_data = None

    hospital_event = HistoryEvent.query.get(h_e)
    HospitalSubForm1_ = HospitalSubForm1()
    HospitalSubForm2_ = HospitalSubForm2()
    HospitalSubForm3_ = HospitalSubForm3()
    HospitalSubForm4_ = HospitalSubForm4()
    HospitalSubForm5_ = HospitalSubForm5()
    HospitalSubForm6_ = HospitalSubForm6()
    HospitalSubForm7_ = HospitalSubForm7()
    HospitalSubForm8_ = HospitalSubForm8()
    ProfileSubForm1_  = ProfileSubForm1()
    ProfileSubForm2_  = ProfileSubForm2()
    ProfileSubForm3_  = ProfileSubForm3()
    ProfileSubForm4_  = ProfileSubForm4()
    ProfileSubForm5_  = ProfileSubForm5()
    ProfileSubForm6_  = ProfileSubForm6()
    ProfileSubForm7_  = ProfileSubForm7()
    ProfileSubForm8_  = ProfileSubForm8()
    ProfileSubForm9_  = ProfileSubForm9()

    if HospitalSubForm1_.submit.data: #and HospitalSubForm1_.validate_on_submit():

        pill = 1
        if hospital_event is None:
            # Это ввод новой госпитализации
            hospital_event = CreateHospital(HospitalSubForm1_, history_obj)
        else:
            # Обновление амбулаторного приема
            UpdateHospital(HospitalSubForm1_, hospital_event)

        flash('Данные сохранены', category='info')
        return redirect(url_for('history.hospital_edit', h=h, h_e=hospital_event.id, pill=pill))

    if HospitalSubForm8_.create.data:
        pill = 1
        operation_obj = Operation.query.filter_by(hospital_id=hospital_event.id).first()
        if operation_obj:
            flash('Данные об операции уже созданы', category='warning')
            return redirect(url_for('history.operation_edit', h=h, hospital_id=hospital_event.id, operation_id=operation_obj.id, pill=pill))
        else:
            return redirect(url_for('history.operation_edit', h=h, hospital_id=hospital_event.id, operation_id='0', pill=pill))


    items = []

    if hospital_event is not None:
        # Открываем уже сущестующую госпитализацию
        # Заполнение формы данными из базы
        form_list = FillHospitalForm(HospitalSubForm1_, HospitalSubForm2_, HospitalSubForm3_, HospitalSubForm4_, \
                                        HospitalSubForm5_, HospitalSubForm6_, HospitalSubForm7_, HospitalSubForm8_, \
                                        history_obj, hospital_event)

        HospitalSubForm1_ = form_list[0]
        HospitalSubForm2_ = form_list[1]
        HospitalSubForm3_ = form_list[2]
        HospitalSubForm4_ = form_list[3]
        HospitalSubForm5_ = form_list[4]
        HospitalSubForm6_ = form_list[5]
        HospitalSubForm7_ = form_list[6]
        HospitalSubForm8_ = form_list[7]
        items = form_list[8]


    return render_template('history/hospital.html', HospitalSubForm1 = HospitalSubForm1_,
                            HospitalSubForm2 = HospitalSubForm2_, HospitalSubForm3 = HospitalSubForm3_,
                            HospitalSubForm4 = HospitalSubForm4_, HospitalSubForm5 = HospitalSubForm5_,
                            HospitalSubForm6 = HospitalSubForm6_, HospitalSubForm7 = HospitalSubForm7_,
                            HospitalSubForm8 = HospitalSubForm8_, ProfileSubForm1 = ProfileSubForm1_,
                            ProfileSubForm2 = ProfileSubForm2_,ProfileSubForm3 = ProfileSubForm3_,
                            ProfileSubForm4 = ProfileSubForm4_,ProfileSubForm5 = ProfileSubForm5_,
                            ProfileSubForm6 = ProfileSubForm6_,ProfileSubForm7 = ProfileSubForm7_,
                            ProfileSubForm8 = ProfileSubForm8_, ProfileSubForm9 = ProfileSubForm9_,
                            hospital_event = hospital_event,
                            h = h, history = history_obj, h_e = h_e, items = items,
                            personal_data = personal_data, pill = pill)

# Редактирование операции
@history_blueprint.route('/operation_edit/<h>/<hospital_id>/<operation_id>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# operation - Operations.id
# pill - номер закладки в форме
@login_required
def operation_edit(h, hospital_id, operation_id, pill):
    history_obj = History.query.get(h)
    if history_obj:
        # Определим ФИО и СНИЛС если они загружены в сессию
        personal_data_list = session.get('personal_data_list')
        if personal_data_list:
            current_patient = Patient.query.get(history_obj.patient_id)
            personal_data = next((row for row in personal_data_list if row['digest']==current_patient.snils_hash ), None)
        else:
            personal_data = None
    else:
        personal_data = None

    hospital_obj = HistoryEvent.query.get(hospital_id)
    operation_obj = Operation.query.get(operation_id)
    if operation_obj:
        operation_event = HistoryEvent.query.get(operation_obj.history_event_id)
    else:
        operation_event = None
    OperationsSubForm1_ = OperationsSubForm1()
    OperationsSubForm2_ = OperationsSubForm2()
    OperationsSubForm3_ = OperationsSubForm3()
    OperationsSubForm4_ = OperationsSubForm4()
    OperationsSubForm5_ = OperationsSubForm5()
    OperationsSubForm6_ = OperationsSubForm6()
    OperationsSubForm7_ = OperationsSubForm7()


    if OperationsSubForm1_.submit.data and OperationsSubForm1_.validate_on_submit():
        pill = 1
        if operation_obj is None:
            # Это ввод новой операции
            operation_list = CreateOperation(OperationsSubForm1_, history_obj, hospital_obj )
            operation_obj = operation_list[0]
            operation_event = operation_list[1]
        else:
            # Обновление операци
            operation_obj.clinic_id = history_obj.clinic_id
            operation_obj.history_id = history_obj.id
            operation_obj.hospital_id = hospital_obj.id
            operation_obj.patient_id = history_obj.patient_id
            operation_obj.doctor_surgeon_id = OperationsSubForm1_.doctor_surgeon.data
            operation_obj.doctor_assistant_id = OperationsSubForm1_.doctor_assistant.data
            operation_obj.operation_order = OperationsSubForm1_.operation_order.data
            db.session.add(operation_obj)
            db.session.commit()

        flash('Данные сохранены', category='info')
        return redirect(url_for('history.operation_edit', h=h, hospital_id=hospital_obj.id, operation_id=operation_obj.id, pill=pill))

    if OperationsSubForm5_.submit.data and OperationsSubForm5_.validate_on_submit():
        # Наблюдения после операции
        pill = 5
        # Проверка существования такого типа наблюдения
        hisory_event = HistoryEvent.query.filter_by(history_id=h, event_id=OperationsSubForm5_.event.data, parent_event_id=operation_event.id).first()
        if hisory_event is not None:
            flash('Послеоперационное наблюдение такого типа уже существует', category='warning')
            return redirect(url_for('history.operation_edit', h=h, hospital_id=hospital_obj.id, operation_id=operation_obj.id, pill=pill))
        else:
            # Переход в форму послеоперационного наблюдения
            return redirect(url_for('history.post_operation_edit', h=h, hospital_id=hospital_obj.id, operation_id=operation_obj.id,
                                                                    post_operation_id = 0, e_type_id = OperationsSubForm5_.event.data, pill=1))


    if OperationsSubForm6_.submit.data and OperationsSubForm6_.validate_on_submit():
        # Осложнения
        pill = 6
        date_begin = OperationsSubForm6_.date_created.data
        complication_id = OperationsSubForm6_.complication.data
        operation_complication_obj = OperationComp.query.filter_by(complication_id=complication_id, operation_id=operation_obj.id).first()
        if operation_complication_obj:
            # Такое осложнение уже заведено
            flash('Такое осложнение уже заведено', category='warning')
            return redirect(url_for('history.operation_edit', h=h, hospital_id=hospital_obj.id, operation_id=operation_obj.id, pill=pill))
        else:
            # Добавить осложнение
            operation_complication_obj = OperationComp()
            operation_complication_obj.clinic_id = operation_obj.clinic_id
            operation_complication_obj.history_id = operation_obj.history_id
            operation_complication_obj.operation_id = operation_obj.id
            operation_complication_obj.patient_id = operation_obj.patient_id
            operation_complication_obj.date_begin = date_begin
            operation_complication_obj.complication_id = complication_id

            db.session.add(operation_complication_obj)
            db.session.commit()

        flash('Данные сохранены', category='info')
        return redirect(url_for('history.operation_edit', h=h, hospital_id=hospital_obj.id, operation_id=operation_obj.id, pill=pill))

    if OperationsSubForm4_.save.data and OperationsSubForm4_.validate_on_submit():
        pill = 4
        # Расчет длительности этапов и сохранение в базу
        dates_from = request.form.getlist('time_begin')
        dates_to = request.form.getlist('time_end')
        ids = request.form.getlist('id')
        # Получим список всех шагов операции
        for i, id in enumerate(ids):

            operation_obj_log = OperationLog.query.get(id)
            if operation_obj_log:
                # Сохранить даты и посчитать продолжительность
                if dates_from[i] != '':
                    operation_obj_log.time_begin = datetime.strptime(dates_from[i], "%Y-%m-%dT%H:%M")
                    if i == 0:
                        # Начало операции
                        operation_obj.time_begin = operation_obj_log.time_begin

                if dates_to[i] != '':
                    operation_obj_log.time_end = datetime.strptime(dates_to[i], "%Y-%m-%dT%H:%M")
                    if i == 8:
                        # окончание операции
                        operation_obj.time_end = operation_obj_log.time_end
                        if operation_obj.time_begin and operation_obj.time_end:
                            # Длительность операции
                            delta = (operation_obj.time_end - operation_obj.time_begin)
                            operation_obj.duration_min = delta.total_seconds() // 60

                if dates_from[i] != '' and dates_to[i] != '':
                    delta = (operation_obj_log.time_end - operation_obj_log.time_begin)
                    operation_obj_log.duration_min = delta.total_seconds() // 60
                db.session.add(operation_obj_log)

        db.session.add(operation_obj)
        try:
            db.session.commit()
        except Exception as e:
            flash('Ошибка при сохранении данных: %s' % str(e), 'error')
            db.session.rollback()
        else:
            flash('Данные сохранены', category='info')
            return redirect(url_for('history.operation_edit', h=h, hospital_id=hospital_obj.id, operation_id=operation_obj.id, pill=pill))


    items = []

    if operation_obj is not None:
        # Открываем уже сущестующую операцию
        # Заполнение формы данными из базы
        form_list = FillOperationForm(OperationsSubForm1_, OperationsSubForm2_, OperationsSubForm3_, OperationsSubForm4_, \
                                        OperationsSubForm5_, OperationsSubForm6_, OperationsSubForm7_, \
                                        history_obj, operation_obj, operation_event)

        OperationsSubForm1_ = form_list[0]
        OperationsSubForm2_ = form_list[1]
        OperationsSubForm3_ = form_list[2]
        OperationsSubForm4_ = form_list[3]
        OperationsSubForm5_ = form_list[4]
        OperationsSubForm6_ = form_list[5]
        OperationsSubForm7_ = form_list[6]

        items = form_list[7]



    if operation_event:
        operation_event_id = operation_event.id
    else:
        operation_event_id = 0
    return render_template('history/operations.html', OperationsSubForm1 = OperationsSubForm1_,
                            OperationsSubForm2 = OperationsSubForm2_, OperationsSubForm3 = OperationsSubForm3_,
                            OperationsSubForm4 = OperationsSubForm4_, OperationsSubForm5 = OperationsSubForm5_,
                            OperationsSubForm6 = OperationsSubForm6_, OperationsSubForm7 = OperationsSubForm7_,
                            h = h, history = history_obj, hospital = hospital_obj, h_e = operation_event_id,
                            operation_event = operation_event, operation = operation_obj, items = items,
                            personal_data = personal_data, pill = pill)

# История болезни / Диагнозы
@history_blueprint.route('/operation_comp_delete/<h>/<h_e>/<operation_id>/<operation_comp_id>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# d - Diagnoses.id
# pill - номер закладки в форме
def operation_comp_delete(h, h_e, operation_id, operation_comp_id, pill):
    operation_obj = Operation.query.get(operation_id)
    history_event_obj = HistoryEvent.query.get(h_e)
    if operation_obj:
        operation_comp_obj = OperationComp.query.get(operation_comp_id)
        db.session.delete(operation_comp_obj)
        try:
            db.session.commit()
        except Exception as e:
            flash('Ошибка при сохранении данных: %s' % str(e), 'error')
            db.session.rollback()
        else:
            if history_event_obj.event_id == 4:
                # Операция
                return redirect(url_for('history.operation_edit', h=h, hospital_id=operation_obj.hospital_id, operation_id=operation_id, pill=pill))
            elif history_event_obj.event_id == 9 or history_event_obj.event_id == 10:
                # Амбулаторные наблюдения через 3 и 6 месяцев паосле операции
                return redirect(url_for('history.ambulance3_edit', h=h, hospital_id=operation_obj.hospital_id, operation_id=operation_id, h_e=h_e, e_type=history_event_obj.event_id, pill=3))
            elif history_event_obj.event_id == 11:
                # Амбулаторные наблюдения через 12 месяцев паосле операции
                return redirect(url_for('history.ambulance12_edit', h=h, hospital_id=operation_obj.hospital_id, operation_id=operation_id, h_e=h_e, e_type=history_event_obj.event_id, pill=3))

# Модальные формы для заполнения показателей анкет
@history_blueprint.route('/profile_save/<profile_id>/<history_id>/<history_event_id>',methods = ['POST'])
# Параметры:
# profile_id - id анкеты
# history_id - id истории
# history_event_id - id госпитализации
def profile_save(profile_id, history_id, history_event_id):
    # Сохранить данные анкеты
    ProfileSubForm1_ = ProfileSubForm1()
    ProfileSubForm2_ = ProfileSubForm2()
    ProfileSubForm3_ = ProfileSubForm3()
    ProfileSubForm4_ = ProfileSubForm4()
    ProfileSubForm5_ = ProfileSubForm5()
    ProfileSubForm6_ = ProfileSubForm6()
    ProfileSubForm7_ = ProfileSubForm7()
    ProfileSubForm8_ = ProfileSubForm8()
    ProfileSubForm9_ = ProfileSubForm9()

    history_event_obj = HistoryEvent.query.get(history_event_id)

    
#and ProfileSubForm1_.validate_on_submit() 
    if ProfileSubForm1_.submit.data and profile_id == '1':
        # Сохранение результатов анкеты 1
        profile_section = ProfileSection.query.filter_by(profile_section='VAS').first()
        if profile_section is None:
            # В справочнике нет такого раздела
            flash('Ошибка при сохранении данных: в справочнике ProfileSection нет раздела VAS')
            return redirect(url_for('history.hospital_edit', h=history_id, h_e=history_event_id, pill=6))

        section_response = ProfileSectionResponse.query.filter_by(history_event_id=history_event_id, profile_id=profile_id, profile_section_id=profile_section.id).first()
        if section_response is None:
            section_response = ProfileSectionResponse()
            section_response.clinic_id = history_event_obj.clinic_id
            section_response.history_id = history_event_obj.history_id
            section_response.patient_id = history_event_obj.patient_id
            section_response.history_event_id = history_event_id
            section_response.profile_id = profile_id
            section_response.profile_section_id = profile_section.id
        
        section_response.date_value = ProfileSubForm1_.date_created.data
        section_response.response_value = ProfileSubForm1_.num_value.data
        section_response.response_str = ''
        db.session.add(section_response)
        db.session.commit()

    if ProfileSubForm2_.submit.data and ProfileSubForm2_.validate_on_submit() and profile_id == '2':
        # Сохранение результатов анкеты 1
        profile_section = ProfileSection.query.filter_by(profile_section='ASA').first()
        if profile_section is None:
            # В справочнике нет такого раздела
            flash('Ошибка при сохранении данных: в справочнике ProfileSection нет раздела ASA')
            return redirect(url_for('history.hospital_edit', h=history_id, h_e=history_event_id, pill=6))

        section_response = ProfileSectionResponse.query.filter_by(history_event_id=history_event_id, profile_id=profile_id, profile_section_id=profile_section.id).first()
        if section_response is None:
            section_response = ProfileSectionResponse()
            section_response.clinic_id = history_event_obj.clinic_id
            section_response.history_id = history_event_obj.history_id
            section_response.patient_id = history_event_obj.patient_id
            section_response.history_event_id = history_event_id
            section_response.profile_id = profile_id
            section_response.profile_section_id = profile_section.id

        section_response.date_value = ProfileSubForm2_.date_created.data
        section_response.response_value = 0
        section_response.response_str = ProfileSubForm2_.value.data
        db.session.add(section_response)
        db.session.commit()

    if ProfileSubForm3_.submit.data and ProfileSubForm3_.validate_on_submit() and profile_id == '3':
        # Сохранение результатов анкеты 1
        profile_sections = ProfileSection.query.filter_by(profile_id=3).all()
        if len(profile_sections) == 0:
            # В справочнике нет такого раздела
            flash('Ошибка при сохранении данных: в справочнике ProfileSection нет раздела для KSK')
            return redirect(url_for('history.hospital_edit', h=history_id, h_e=history_event_id, pill=6))

        for section in profile_sections:

            section_response = ProfileSectionResponse.query.filter_by(history_event_id=history_event_id, profile_id=profile_id, profile_section_id=section.id).first()
            if section_response is None:
                section_response = ProfileSectionResponse()
                section_response.clinic_id = history_event_obj.clinic_id
                section_response.history_id = history_event_obj.history_id
                section_response.patient_id = history_event_obj.patient_id
                section_response.history_event_id = history_event_id
                section_response.profile_id = profile_id
                section_response.profile_section_id = section.id

            section_response.date_value = ProfileSubForm3_.date_created.data
            if section.profile_section == 'KSS-K':
                section_response.response_value = ProfileSubForm3_.value_kss_k.data
            if section.profile_section == 'KSS-F':
                section_response.response_value = ProfileSubForm3_.value_kss_f.data
            section_response.response_str = ''
            db.session.add(section_response)

        db.session.commit()

    if ProfileSubForm4_.submit.data and ProfileSubForm4_.validate_on_submit() and profile_id == '4':
        # Сохранение результатов анкеты 1
        profile_section = ProfileSection.query.filter_by(profile_section='OKS').first()
        if profile_section is None:
            # В справочнике нет такого раздела
            flash('Ошибка при сохранении данных: в справочнике ProfileSection нет раздела OKS')
            return redirect(url_for('history.hospital_edit', h=history_id, h_e=history_event_id, pill=6))

        section_response = ProfileSectionResponse.query.filter_by(history_event_id=history_event_id, profile_id=profile_id, profile_section_id=profile_section.id).first()
        if section_response is None:
            section_response = ProfileSectionResponse()
            section_response.clinic_id = history_event_obj.clinic_id
            section_response.history_id = history_event_obj.history_id
            section_response.patient_id = history_event_obj.patient_id
            section_response.history_event_id = history_event_id
            section_response.profile_id = profile_id
            section_response.profile_section_id = profile_section.id

        section_response.date_value = ProfileSubForm4_.date_created.data
        section_response.response_value = ProfileSubForm4_.value_oks.data
        section_response.response_str = ''
        db.session.add(section_response)
        db.session.commit()

    if ProfileSubForm5_.submit.data and ProfileSubForm5_.validate_on_submit() and profile_id == '5':
        # Сохранение результатов анкеты 5
        profile_sections = ProfileSection.query.filter_by(profile_id=5).order_by(ProfileSection.id.desc()).all()
        if len(profile_sections) == 0:
            # В справочнике нет такого раздела
            flash('Ошибка при сохранении данных: в справочнике ProfileSection нет раздела для WOMAC')
            return redirect(url_for('history.hospital_edit', h=history_id, h_e=history_event_id, pill=6))

        value_a = 0
        value_b = 0
        value_c = 0

        for section in profile_sections:

            section_response = ProfileSectionResponse.query.filter_by(history_event_id=history_event_id, profile_id=profile_id, profile_section_id=section.id).first()
            if section_response is None:
                section_response = ProfileSectionResponse()
                section_response.clinic_id = history_event_obj.clinic_id
                section_response.history_id = history_event_obj.history_id
                section_response.patient_id = history_event_obj.patient_id
                section_response.history_event_id = history_event_id
                section_response.profile_id = profile_id
                section_response.profile_section_id = section.id

            section_response.date_value = ProfileSubForm5_.date_created.data
            if section.profile_section == 'A':
                section_response.response_value = ProfileSubForm5_.value_a.data
                value_a = ProfileSubForm5_.value_a.data
            if section.profile_section == 'B':
                section_response.response_value = ProfileSubForm5_.value_b.data
                value_b = ProfileSubForm5_.value_b.data
            if section.profile_section == 'C':
                section_response.response_value = ProfileSubForm5_.value_c.data
                value_c = ProfileSubForm5_.value_c.data
            if section.profile_section == 'WOMAC':
                section_response.response_value = value_a + value_b + value_c
            section_response.response_str = ''
            db.session.add(section_response)

        db.session.commit()

    if ProfileSubForm6_.submit.data and ProfileSubForm6_.validate_on_submit() and profile_id == '6':
        # Сохранение результатов анкеты 5
        profile_sections = ProfileSection.query.filter_by(profile_id=6).all()
        if len(profile_sections) == 0:
            # В справочнике нет такого раздела
            flash('Ошибка при сохранении данных: в справочнике ProfileSection нет раздела для SF-36')
            return redirect(url_for('history.hospital_edit', h=history_id, h_e=history_event_id, pill=6))

        for section in profile_sections:

            section_response = ProfileSectionResponse.query.filter_by(history_event_id=history_event_id, profile_id=profile_id, profile_section_id=section.id).first()
            if section_response is None:
                section_response = ProfileSectionResponse()
                section_response.clinic_id = history_event_obj.clinic_id
                section_response.history_id = history_event_obj.history_id
                section_response.patient_id = history_event_obj.patient_id
                section_response.history_event_id = history_event_id
                section_response.profile_id = profile_id
                section_response.profile_section_id = section.id

            section_response.date_value = ProfileSubForm6_.date_created.data
            if section.profile_section == 'PF':
                section_response.response_value = ProfileSubForm6_.value_pf.data
            if section.profile_section == 'RP':
                section_response.response_value = ProfileSubForm6_.value_rp.data
            if section.profile_section == 'P':
                section_response.response_value = ProfileSubForm6_.value_p.data
            if section.profile_section == 'GH':
                section_response.response_value = ProfileSubForm6_.value_gh.data
            if section.profile_section == 'VT':
                section_response.response_value = ProfileSubForm6_.value_vt.data
            if section.profile_section == 'SF':
                section_response.response_value = ProfileSubForm6_.value_sf.data
            if section.profile_section == 'RE':
                section_response.response_value = ProfileSubForm6_.value_re.data
            if section.profile_section == 'MH':
                section_response.response_value = ProfileSubForm6_.value_mh.data

            section_response.response_str = ''
            db.session.add(section_response)

        db.session.commit()

    if ProfileSubForm7_.submit.data and ProfileSubForm7_.validate_on_submit() and profile_id == '7':
        # Сохранение результатов анкеты 5
        profile_sections = ProfileSection.query.filter_by(profile_id=7).all()
        if len(profile_sections) == 0:
            # В справочнике нет такого раздела
            flash('Ошибка при сохранении данных: в справочнике ProfileSection нет раздела для STAI')
            return redirect(url_for('history.hospital_edit', h=history_id, h_e=history_event_id, pill=6))

        for section in profile_sections:

            section_response = ProfileSectionResponse.query.filter_by(history_event_id=history_event_id, profile_id=profile_id, profile_section_id=section.id).first()
            if section_response is None:
                section_response = ProfileSectionResponse()
                section_response.clinic_id = history_event_obj.clinic_id
                section_response.history_id = history_event_obj.history_id
                section_response.patient_id = history_event_obj.patient_id
                section_response.history_event_id = history_event_id
                section_response.profile_id = profile_id
                section_response.profile_section_id = section.id

            section_response.date_value = ProfileSubForm7_.date_created.data
            if section.profile_section == 'STAI-RA':
                section_response.response_value = ProfileSubForm7_.value_ra.data
            if section.profile_section == 'STAI-PA':
                section_response.response_value = ProfileSubForm7_.value_pa.data

            section_response.response_str = ''
            db.session.add(section_response)

        db.session.commit()

    if ProfileSubForm8_.submit.data and ProfileSubForm8_.validate_on_submit() and profile_id == '8':
        # Сохранение результатов анкеты 1
        profile_section = ProfileSection.query.filter_by(profile_section='FJS-12').first()
        if profile_section is None:
            # В справочнике нет такого раздела
            flash('Ошибка при сохранении данных: в справочнике ProfileSection нет раздела FJS-12')
            return redirect(url_for('history.hospital_edit', h=history_id, h_e=history_event_id, pill=6))

        section_response = ProfileSectionResponse.query.filter_by(history_event_id=history_event_id, profile_id=profile_id, profile_section_id=profile_section.id).first()
        if section_response is None:
            section_response = ProfileSectionResponse()
            section_response.clinic_id = history_event_obj.clinic_id
            section_response.history_id = history_event_obj.history_id
            section_response.patient_id = history_event_obj.patient_id
            section_response.history_event_id = history_event_id
            section_response.profile_id = profile_id
            section_response.profile_section_id = profile_section.id

        section_response.date_value = ProfileSubForm8_.date_created.data
        section_response.response_value = ProfileSubForm8_.value_fjs.data
        section_response.response_str = ''
        db.session.add(section_response)
        db.session.commit()

    if ProfileSubForm9_.submit.data and ProfileSubForm9_.validate_on_submit() and profile_id == '9':
        # Сохранение результатов анкеты 1
        profile_section = ProfileSection.query.filter_by(profile_section='SLR').first()
        if profile_section is None:
            # В справочнике нет такого раздела
            flash('Ошибка при сохранении данных: в справочнике ProfileSection нет раздела SLR')
            return redirect(url_for('history.hospital_edit', h=history_id, h_e=history_event_id, pill=6))

        section_response = ProfileSectionResponse.query.filter_by(history_event_id=history_event_id, profile_id=profile_id, profile_section_id=profile_section.id).first()
        if section_response is None:
            section_response = ProfileSectionResponse()
            section_response.clinic_id = history_event_obj.clinic_id
            section_response.history_id = history_event_obj.history_id
            section_response.patient_id = history_event_obj.patient_id
            section_response.history_event_id = history_event_id
            section_response.profile_id = profile_id
            section_response.profile_section_id = profile_section.id

        section_response.date_value = ProfileSubForm9_.date_created.data
        section_response.response_value = ProfileSubForm9_.value_slr.data
        section_response.response_str = ''
        db.session.add(section_response)
        db.session.commit()

    if history_event_obj.event_id == 3:
        # Сохранение из госпитализации
        return redirect(url_for('history.hospital_edit', h=history_id, h_e=history_event_id, pill=6))
    elif history_event_obj.event_id == 9 or history_event_obj.event_id == 10:
        # Сохранение из приема через 3 и 6 месяцев после операции
        operation_obj = Operation.query.filter_by(history_id=history_id).first()
        hospital_obj  = HistoryEvent.query.get(operation_obj.hospital_id)
        return redirect(url_for('history.ambulance3_edit', h=history_id, hospital_id=hospital_obj.id, operation_id=operation_obj.id, h_e=history_event_id, e_type = history_event_obj.event_id, pill=2))
    elif history_event_obj.event_id == 11:
        # Сохранение из приема через 12 месяцев после операции
        operation_obj = Operation.query.filter_by(history_id=history_id).first()
        hospital_obj  = HistoryEvent.query.get(operation_obj.hospital_id)
        return redirect(url_for('history.ambulance12_edit', h=history_id, hospital_id=hospital_obj.id, operation_id=operation_obj.id, h_e=history_event_id, e_type = history_event_obj.event_id, pill=2))
    elif history_event_obj.event_id in [5,6,7,8]:
        # Сохранение из послеоперационных наблюдений
        operation_obj = Operation.query.filter_by(history_id=history_id).first()
        hospital_obj  = HistoryEvent.query.get(operation_obj.hospital_id)
        return redirect(url_for('history.post_operation_edit', h=history_id, hospital_id=hospital_obj.id, operation_id=operation_obj.id, post_operation_id=history_event_id,
                                    e_type_id=history_event_obj.event_id, pill=5))

# Редактирование послеоперационных наблюдений
@history_blueprint.route('/post_operation_edit/<h>/<hospital_id>/<operation_id>/<post_operation_id>/<e_type_id>/<pill>', methods = ['GET','POST'])
# Параметры:
# h - Histories.id
# hospital_id - Госпитализация
# operation_id - Операция
# post_operation_id - послеоперационное наблюдение
# e_type_id - тип события послеоперационного наблюдения
# pill - номер закладки в форме
@login_required
def post_operation_edit(h, hospital_id, operation_id, post_operation_id, e_type_id, pill):
    history_obj = History.query.get(h)
    if history_obj:
        # Определим ФИО и СНИЛС если они загружены в сессию
        personal_data_list = session.get('personal_data_list')
        if personal_data_list:
            current_patient = Patient.query.get(history_obj.patient_id)
            personal_data = next((row for row in personal_data_list if row['digest']==current_patient.snils_hash ), None)
        else:
            personal_data = None
    else:
        personal_data = None

    hospital_obj = HistoryEvent.query.get(hospital_id)
    operation_obj = Operation.query.get(operation_id)
    post_operation_obj = HistoryEvent.query.get(post_operation_id)

    PostOperationsSubForm1_ = PostOperationsSubForm1()
    PostOperationsSubForm2_ = PostOperationsSubForm2()
    PostOperationsSubForm3_ = PostOperationsSubForm3()
    PostOperationsSubForm4_ = PostOperationsSubForm4()
    PostOperationsSubForm5_ = PostOperationsSubForm4()
    ProfileSubForm1_ = ProfileSubForm1()

    if post_operation_obj is None:
        # Это ввод нового события
        # Предварительная проверка события такого типа
        operation_event_obj = HistoryEvent.query.get(operation_obj.history_event_id)
        post_operation_obj = HistoryEvent.query.filter_by(history_id=h, parent_event_id=operation_event_obj.id, event_id=e_type_id).first()
        if post_operation_obj is None:
            post_operation_obj = CreatePostOperation(operation_obj,  e_type_id)
        else:
            post_operation_id =  post_operation_obj.id

    items = []



    if post_operation_obj is not None:
        #Открываем уже сущестующее событие
        # Заполнение формы данными из базы
        form_list = FillPostOperationForm(PostOperationsSubForm1_, PostOperationsSubForm2_, PostOperationsSubForm3_, PostOperationsSubForm4_, PostOperationsSubForm5_, post_operation_obj)

        PostOperationsSubForm1_ = form_list[0]
        PostOperationsSubForm2_ = form_list[1]
        PostOperationsSubForm3_ = form_list[2]
        PostOperationsSubForm4_ = form_list[3]
        PostOperationsSubForm5_ = form_list[4]

        items = form_list[5]

    return render_template('history/post_operation.html', PostOperationsSubForm1 = PostOperationsSubForm1_,
                            PostOperationsSubForm2 = PostOperationsSubForm2_, PostOperationsSubForm3 = PostOperationsSubForm3_,
                            PostOperationsSubForm4 = PostOperationsSubForm4_, PostOperationsSubForm5 = PostOperationsSubForm5_,
                            ProfileSubForm1 = ProfileSubForm1_,
                            h = h, history = history_obj, hospital = hospital_obj, h_e = post_operation_obj.id, operation = operation_obj, \
                            post_operation = post_operation_obj, items = items,
                            personal_data = personal_data, pill = pill)
