import os
import pandas as pd
from dash.dependencies import Input
from dash.dependencies import Output
import plotly.graph_objs as go
from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from webapp import db
from ..history.models import HistoryEvent, Patient
from ..main.models import Event
from flask import current_app, session
from datetime import datetime

'''
basedir = os.path.abspath(os.path.dirname(__file__))
path_name1 = os.path.join(basedir, 'patients_m16.csv')
path_name2 = os.path.join(basedir, 'patients_m17.csv')
patients_m16 = pd.read_csv(path_name1)
patients_m17 = pd.read_csv(path_name2)
patients_m16.columns = ['Height', 'Weight', 'ID', 'FIO', 'Sex', 'Age', 'DateFrom', 'Diagnosis', 'DiagnosisOthers','BloodGroup','Resus', 'Age','IndexWeight','IndexGroup']
patients_m17.columns = ['Height', 'Weight', 'ID', 'FIO', 'Sex', 'Age', 'DateFrom', 'Diagnosis', 'DiagnosisOthers','BloodGroup','Resus', 'Height', 'Age','IndexWeight','IndexGroup']
patients_m16.DateFrom = pd.to_datetime(patients_m16.DateFrom)
#patients_m16['DateFrom'] = dt.strptime(str(patients_m16['DateFrom']),'%Y-%m-%d')


app = current_app._get_current_object()
with app.app_context():
    DB_Events = Event.query.all()
    DF_Events = pd.DataFrame(DB_Events, columns=['id','description','type'])
'''


def register_callback(dashapp):
    @dashapp.callback(Output('html_output_table','children'),
                    [Input('html_input_date_range','start_date'),
                     Input('html_input_date_range','end_date') ])

    def update_table(start_date, end_date):
        c_engine = db.get_engine()
        DB_Events = Event.query.all()
        sql_query = '''select
h.hist_number, -- Номер истории
p.id as patient_id,
'' as fio,
'' as snils,
case when p.sex = '1' then 'M' else 'F' end as sex , -- Пол
(current_date - p.birthdate) / 365 as age, -- Возраст
h.date_in, -- Дата открытия истории
h.date_research_in , -- Дата включения в исследование
h.date_research_out , -- Дата исключения из исследования
rg.description as research_group, -- Группа исследования
doc.fio as researcher, -- Врач-исследователь
rsn.description as reson_out, -- Причина исключения из исследования
diag.date_created as main_diagnose_date, -- Дата установления диагноза
diag.side_damage, -- Сторона поражения
diag_main.mkb10, -- Диагноз МКБ10
diag_main.description as main_diagnose,-- Диагноз
amb1.date_begin as amb1_date_from, -- Дата первичного приема
doc_amb1.fio as doc_amb1_fio, -- Врач на амб. приеме
hosp.date_begin as hospital_date_from, -- Дата госпитализации
oper.date_begin as operation_date, -- Дата операции
hosp.date_end as hospital_date_to, -- Дата выписки
amb3.date_begin as amb3_date_from, -- Дата визита через 3 месяца
amb6.date_begin as amb6_date_from, -- Дата визита через 6 месяцев
amb12.date_begin as amb12_date_from -- Дата визита через 12 месяцев
from "History" as h
left outer join "ResearchGroup" as rg on
h.clinic_id = rg.clinic_id  and
h.research_group_id = rg.id
left outer join "Doctor" as doc on
h.doctor_researcher_id = doc.id
left outer join "Reason" as rsn on
h.reason_id = rsn.id
left outer join "Patient" as p on
h.patient_id = p.id
left outer join "Diagnose" as diag on
h.clinic_id = diag.clinic_id and
h.id = diag.history_id
left outer join "DiagnoseItem" as diag_main on
diag.diagnose_item_id = diag_main.id
left outer join "HistoryEvent" as amb1 on
h.clinic_id = amb1.clinic_id and
h.id = amb1.history_id and
amb1.event_id = 2
left outer join "Doctor" as doc_amb1 on
amb1.doctor_id = doc_amb1.id
left outer join "HistoryEvent" as hosp on
h.clinic_id = hosp.clinic_id and
h.id = hosp.history_id and
hosp.event_id = 3
left outer join "HistoryEvent" as oper on
h.clinic_id = oper.clinic_id and
h.id = oper.history_id and
oper.event_id = 4
left outer join "HistoryEvent" as amb3 on
h.clinic_id = amb3.clinic_id and
h.id = amb3.history_id and
amb3.event_id = 9
left outer join "HistoryEvent" as amb6 on
h.clinic_id = amb6.clinic_id and
h.id = amb6.history_id and
amb6.event_id = 10
left outer join "HistoryEvent" as amb12 on
h.clinic_id = amb12.clinic_id and
h.id = amb12.history_id and
amb12.event_id = 11
where (diag_main."type" = 'Основной' or diag_main."type" is null)
order by h.date_in, h.hist_number   '''

        DF_Events = pd.read_sql_query(sql_query, db.engine) #, columns=['id','description','type'])
        #print(type(DF_Events['date_in']))
        #print(type(start_date))
        #print(type(datetime.strptime(start_date,'%Y-%m-%d').date()))
        DF_Events.rename(columns={'hist_number':'История болезни',
                                  'patient_id':'ID Пациента' ,
                                  'fio':'ФИО',
                                  'snils':'СНИЛС',
                                  'sex':'Пол',
                                  'age':'Возраст',
                                  'date_in':'Дата открытия истории',
                                  'date_research_in':'Дата включения в исследование' ,
                                  'date_research_out':'Дата исключения из исследования' ,
                                  'research_group':'Группа', 'researcher':'Исследователь',
                                  'reson_out':'Причина исключения',
                                  'main_diagnose_date':'Дата установления диагноза',
                                  'side_damage':'Сторона поражения',
                                  'mkb10':'Диагноз МКБ10',
                                  'main_diagnose':'Диагноз',
                                  'amb1_date_from':'Дата первичного приема',
                                  'doc_amb1_fio':'Врач на амб. приеме',
                                  'hospital_date_from':'Дата госпитализации',
                                  'operation_date':'Дата операции',
                                  'hospital_date_to':'Дата выписки',
                                  'amb3_date_from':'Дата визита через 3 месяца',
                                  'amb6_date_from':'Дата визита через 6 месяцев',
                                  'amb12_date_from':'Дата визита через 12 месяцев'}, inplace=True)
        df_selected = DF_Events[(DF_Events['Дата открытия истории'] >= datetime.strptime(start_date,'%Y-%m-%d').date()) & (DF_Events['Дата открытия истории'] <= datetime.strptime(end_date,'%Y-%m-%d').date())]

        df_selected_dict = df_selected.to_dict('records')
        #print(df_selected_dict)
        df_selected = DF_Events
        # Если загружены персональные данные, то добавляем их в реестр
        personal_data_list = session.get('personal_data_list')
        if personal_data_list:
            for i in df_selected_dict:
                current_patient = Patient.query.get(i['ID Пациента'])
                finded_snils = next((row for row in personal_data_list if row['digest']==current_patient.snils_hash), None)
                #print(finded_snils)
                if finded_snils:
                    i['ФИО'] = finded_snils['fio']
                    i['СНИЛС'] = finded_snils['snils']
        #print(df_selected.columns)

        return(dash_table.DataTable(
            id='datatable-interactivity',
            columns=[{"name": i, "id": i} for i in df_selected.columns],
            data=df_selected_dict,
            fixed_columns=1,
            #editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            #column_selectable="single",
            #row_selectable="multi",
            style_data={
            'whiteSpace': 'normal',
            'height': 'auto'},
            style_table={
            'maxHeight': '600px',
            'maxWeight': '500px',
            'overflowY': 'scroll',
            'overflowX': 'scroll'},
            style_cell = {"fontFamily": "Arial", "size": 10, 'textAlign': 'left','padding':15},
            style_header ={
            'backgroundColor': 'grey',
            'fontWeight': 'bold'}
        ))
