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
from .db_tools import get_short_hist_data, get_asa
#from ..history.models import HistoryEvent, Patient
#from ..main.models import Event
#from flask import current_app, session
from datetime import datetime
from scipy.stats import ttest_ind
from scipy.stats import chi2_contingency
from textwrap import dedent

def get_side_statistics(filter_sex):
  """
  Функция подготавливает статистику по стороне поражения 
  """
  df_hist = get_short_hist_data()

  # Формирование таблицы
  df_side_sex_count = df_hist[df_hist['sex'].isin(filter_sex)].groupby(['sex','side_damage']).agg({'patient_id':'count'})
  df_side_sex_count['indicator_type'] = 'Абсолютное значение'
  df_side_sex_proc = round(df_hist.groupby(['sex','side_damage']).agg({'patient_id':'count'})/df_hist['patient_id'].nunique()*100)
  df_side_sex_proc['indicator_type'] = '%'

  df_sex_side = pd.concat([df_side_sex_count,df_side_sex_proc])
  df_sex_side['indicator'] = 'Сторона поражения'

  df_sex_side.reset_index(inplace=True)
  #df_sex_gr.columns
  total_table = df_sex_side.pivot(index = ['sex','indicator','side_damage'], columns = ['indicator_type'], values = 'patient_id')
  total_table.reset_index(inplace=True)
  total_table.columns = ['Пол','Показатель','Сторона поражения','%','Абсолютное значение']
  total_table=total_table.round(2)

  # График
  fig = px.bar(total_table, x='Сторона поражения', y = 'Абсолютное значение',
                        color = 'Сторона поражения',
                        facet_col= 'Пол'
                        )
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                      plot_bgcolor='rgb(243, 243, 243)'
                    )
  #fig.show(config={'displaylogo':False})

  # Результат тестирования        
  df_side_count = df_hist.groupby(['side_damage','sex']).agg({'patient_id':'count'})
  df_side_pivot = pd.pivot_table(df_side_count, index = ['side_damage'], columns = 'sex', values = 'patient_id')

  contingency_table= [df_side_pivot] 
  stat, p, dof, expected = chi2_contingency(contingency_table)         

  if p > 0.05:
        p_result = 'Нет различий по полу'
  else:
        p_result = 'Есть различия по полу'

  result_text = [
    html.P("Показатель: Сторона поражения", className="card-text"),
    html.P(f"Результаты сравнения: хи-квадрат = {stat}, p-value: {round(p,5)}", className="card-text"),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")  )

def get_asa_statistics(filter_sex):
  """
  Функция подготавливает статистику по опроснику ASA 
  """
  df_asa = get_asa()

  # Формирование таблицы
  df_asa_gr_count = df_asa[df_asa['sex'].isin(filter_sex)].groupby(['sex','ASA']).agg({'patient_id':'count'})
  df_asa_gr_count['indicator_type'] = 'Абсолютное значение'
  df_asa_gr_proc = round(df_asa.groupby(['sex','ASA']).agg({'patient_id':'count'})/df_asa['patient_id'].nunique()*100)
  df_asa_gr_proc['indicator_type'] = '%'
  df_asa_gr = pd.concat([df_asa_gr_count,df_asa_gr_proc])
  df_asa_gr['indicator'] = 'ASA'
  df_asa_gr.reset_index(inplace=True)
  total_table = df_asa_gr.pivot(index = ['sex','indicator','ASA'], columns = ['indicator_type'], values = 'patient_id')

  #df_sex_gr.columns
  total_table.reset_index(inplace=True)
  total_table.columns = ['Пол','Показатель','ASA','%','Абсолютное значение']
  total_table=total_table.round(2)

  # График
  fig = px.bar(total_table, x='ASA', y = 'Абсолютное значение',
                        color = 'ASA',
                        facet_col= 'Пол'
                        )
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                      plot_bgcolor='rgb(243, 243, 243)'
                    )
  #fig.show(config={'displaylogo':False})

  # Результат тестирования        
  df_asa_count = df_asa.groupby(['ASA','sex']).agg({'patient_id':'count'})
  df_asa_pivot = pd.pivot_table(df_asa_count, index = ['ASA'], columns = 'sex', values = 'patient_id').fillna(0)

  contingency_table= [df_asa_pivot]
  stat, p, dof, expected = chi2_contingency(contingency_table)         

  if p > 0.05:
        p_result = 'Нет различий по полу'
  else:
        p_result = 'Есть различия по полу'

  result_text = [
    html.P("Показатель: ASA", className="card-text"),
    html.P(f"Результаты сравнения: хи-квадрат = {round(stat, 3)}, p-value: {round(p,5)}", className="card-text"),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")  )


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
        'Сторона поражения',
        'ASA',
      ]
      kf_otions = [{'label':group, 'value':group} for group in kf_list]
      return kf_otions, 'Сторона поражения'

    @dashapp.callback([Output('html_output_table','children'),
                       Output('kf_output_graph','figure'),
                       Output('html_output_text','children')],
                    [ Input('html_filter_sex', 'value' ), 
                      Input('html_filter_kf', 'value')
                     ])
    def get_total_table(filter_sex, filter_kf):          
        """"
        Формирование таблицы с основной статистикой
        """
        if filter_kf == 'Сторона поражения':
          return get_side_statistics(filter_sex)

        elif filter_kf == 'ASA':
          return get_asa_statistics(filter_sex)


