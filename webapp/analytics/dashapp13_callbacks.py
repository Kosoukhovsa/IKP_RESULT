import os
import pandas as pd
from dash.dependencies import Input
from dash.dependencies import Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime as dt
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from webapp import db
from .db_tools import get_short_hist_data
#from ..history.models import HistoryEvent, Patient
#from ..main.models import Event
#from flask import current_app, session
from datetime import datetime

def register_callback(dashapp):
    @dashapp.callback([Output('html_filter_kf','options'),
                      Output('html_filter_kf','value')],
                      [Input('html_hidden_div', 'style')]
                      )
    def get_filter_kf(div_style):
      """
      Подготовка списка показателей
      """
      kf_list = [
        'Возраст',
        'Рост',
        'Вес',
        'ИМТ'
        'Срок наблюдения'
      ]
      kf_otions = [{'label':group, 'value':group} for group in kf_list]
      return kf_otions, 'Возраст'

    @dashapp.callback([Output('html_output_table','children'),
                       Output('kf_output_graph','figure')],
                    [ Input('html_filter_sex', 'value' ), 
                      Input('html_filter_kf', 'value')
                     ])
    def get_total_table(filter_sex, filter_kf):          
        """"
        Формирование таблицы с основной статистикой
        """
        if filter_kf == 'Возраст':
          df_hist = get_short_hist_data()

          # Формирование таблицы
          df_sex_age = df_hist[(df_hist['age'] > 10) & (df_hist['sex'].isin(filter_sex))]
          df_sex_age['indicator'] = 'Возраст'
          total_table = pd.pivot_table(df_sex_age, values = 'age', index = ['sex','indicator'],
                                          aggfunc=['mean','min','max','std','median'])
          total_table.reset_index(inplace=True)
          #total_table.rename(columns={'sex':'Пол', 'indicator':'Показатель', 
          #                            'patient_id':'Количество'}, 
          #                  inplace=True)
          total_table.columns = ['Пол','Показатель','Среднее','Min','Max','Ст откл','Медиана']
          total_table['Ст откл']=total_table['Ст откл'].round(2)

          # График
          fig = px.box(df_sex_age, x = 'sex', y= 'age',
             color = 'sex',
             points = 'all',
            title='Распределение пациентов по полу и возрасту',
            labels = {'sex':'Пол', 'age':'возраст'}
            )
          fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                              plot_bgcolor='rgb(243, 243, 243)'
                            )
          #fig.show(config={'displaylogo':False})


          return dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), fig

        elif filter_kf in['Рост','Вес','ИМТ']:
          pass

        elif filter_kf in['Срок наблюдения']:
          pass
