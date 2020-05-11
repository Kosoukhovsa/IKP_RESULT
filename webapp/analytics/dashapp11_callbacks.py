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
from ..history.models import HistoryEvent
from ..main.models import Event
from flask import current_app

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
        sql_query = '''select h.hist_number, case when p.sex = '1' then 'M' else 'F' end as sex , (current_date - p.birthdate) / 365 as age, h.date_in, h.date_research_in ,
                    h.date_research_out , rg.description as research_group, doc.fio as researcher, rsn.description reson_out,
                    diag.date_created as main_diagnose_date, diag.side_damage, diag_i.mkb10, diag_i.description as main_diagnose
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
                    left outer join "DiagnoseItem" as diag_i on
                    diag.diagnose_item_id = diag_i.id
                    where diag_i."type" = 'Основной' or diag_i."type" is null
                    order by h.date_in, h.hist_number  '''

        DF_Events = pd.read_sql_query(sql_query, db.engine) #, columns=['id','description','type'])
        df_selected = DF_Events
        print(df_selected.columns)

        return(dash_table.DataTable(
            id='datatable-interactivity',
            columns=[{"name": i, "id": i} for i in df_selected.columns],
            data=df_selected.to_dict('records'),
            #editable=True,
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            style_data={
            'whiteSpace': 'normal',
            'height': 'auto'},
            style_table={
            'maxHeight': '600px',
            'maxWeight': '500px',
            'overflowY': 'scroll',
            'overflowX': 'scroll'},
            style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'},
        ))
