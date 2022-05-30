import os
import pandas as pd
from dash.dependencies import Input
from dash.dependencies import Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from webapp import db
from .db_tools import get_short_hist_data, get_research_groups
#from ..history.models import HistoryEvent, Patient
#from ..main.models import Event
#from flask import current_app, session
from datetime import datetime

def register_callback(dashapp):
    @dashapp.callback([Output('html_filter_group','options'),
                      Output('html_filter_group','value')],
                      [Input('html_hidden_div', 'style')]
                      )
    def get_filter_group(div_style):
      """
      Подготовка списка групп исследования
      """
      research_group_options = [{'label':group, 'value':group} for group in get_research_groups()]
      research_group_values = get_research_groups()
      #print(research_group_otions)
      #print(research_group_values)
       #research_group_otions, 
      return research_group_options, research_group_values

    @dashapp.callback(Output('html_output_table','children'),
                    [ Input('html_filter_sex', 'value' ), 
                      Input('html_filter_group', 'value')
                     ])
    def get_total_table(filter_sex, filter_group):          
        """"
        Формирование таблицы с основной статистикой
        """
        if filter_group is None:
          filter_group = get_research_groups()
          
        df_history = get_short_hist_data()
        df_history_selected = df_history[(df_history['research_group'].isin(filter_group)) & 
                                         (df_history['sex'].isin(filter_sex))]
        df_table = df_history_selected.groupby( ['research_group','sex']).agg({'patient_id':'count'}).reset_index()
        totals = pd.DataFrame([['Итого','',df_table['patient_id'].sum()]], columns=list(df_table.columns))
        total_table = pd.concat([df_table, totals], ignore_index=True)
        total_table.rename(columns={'research_group':'Группа', 'sex':'Пол', 'patient_id':'Количество'}, 
                          inplace=True)

        return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True))