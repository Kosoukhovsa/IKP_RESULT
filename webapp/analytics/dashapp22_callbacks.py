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
from .db_tools import get_short_hist_data, get_ind_values, get_observations
from datetime import datetime
from scipy.stats import ttest_ind
from scipy.stats import chi2_contingency
from textwrap import dedent


def get_age_stat(filter_sex):
  """
  Функция подготавливает статистику по возрасту 
  """
  df_hist = get_short_hist_data()

  # Формирование таблицы
  df_sex_age = df_hist[(df_hist['age'] > 10) & (df_hist['sex'].isin(filter_sex))]
  df_sex_age['indicator'] = 'Возраст'
  total_table = pd.pivot_table(df_sex_age, values = 'age', index = ['sex','indicator'],
                                  aggfunc=['mean','min','max','std','median'])
  total_table.reset_index(inplace=True)
  total_table.columns = ['Пол','Показатель','Среднее','Min','Max','Ст откл','Медиана']
  total_table=total_table.round(2)

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

  # Результат тестирования        
  df_m_age = df_hist[(df_hist['age'] > 10) & (df_hist['sex'] == 'M')]
  df_f_age = df_hist[(df_hist['age'] > 10) & (df_hist['sex'] == 'F')]
  stat, p = ttest_ind(df_m_age['age'], df_f_age['age'])          

  if p <= 0.05:
      p_result = 'Распределение отличается по полу'
  else:
      p_result = 'Нет различия в распределении возраста между мужчинами и женщинами'

  result_text = [
    html.P("Показатель: Возраст", className="card-text"),
    html.P(f"Результаты сравнения возраста: p-value = {round(p, 7)}", className="card-text"),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")  )

def get_ind_stat(filter_sex, ind_id):
  """
  Функция подготавливает статистику по показателям:
  ind_id = 1: рост
  ind_id = 2: вес
  ind_id = 3: имт
  """
  df_ind_values = get_ind_values()

  # Формирование таблицы
  # Выборка показателей: рост, вес, ИМТ
  ind_text = ''
  if ind_id == 1:
    ind_text = 'Рост' 
  elif ind_id == 2:
    ind_text = 'Вес'
  elif ind_id == 3:
    ind_text = 'ИМТ'

  df_ind_b22 = df_ind_values[(df_ind_values['event_id']==3) 
                            & (df_ind_values['ind_id'].isin([ind_id]))
                            & (df_ind_values['sex'].isin(filter_sex))
                            ]
  total_table = pd.pivot_table(df_ind_b22, values = 'num_value', index = ['sex','indicator'], 
                              aggfunc=['mean','min','max','std','median'])                    
  total_table.reset_index(inplace=True)
  total_table.columns = ['Пол','Показатель','Среднее','Min','Max','Ст откл','Медиана']
  total_table=total_table.round(2)

  # График
  fig = px.box(df_ind_b22, x='sex', y = 'num_value',
             color = 'sex',
             facet_col = 'indicator',
             points = 'all',
             title = 'Распределение показателя по полу',
             labels = {'num_value':'Значение','sex':'Пол'}
)

  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                      plot_bgcolor='rgb(243, 243, 243)'
                    )
  #fig.show(config={'displaylogo':False})

  # Результат тестирования        
  df_m_height = df_ind_values[(df_ind_values['event_id']==3) & 
                            (df_ind_values['ind_id'].isin([ind_id])) & 
                            (df_ind_values['sex'] == 'M')]
  df_f_height = df_ind_values[(df_ind_values['event_id']==3) & 
                            (df_ind_values['ind_id'].isin([ind_id])) & 
                            (df_ind_values['sex'] == 'F')]

  stat, p = ttest_ind(df_m_height['num_value'], df_f_height['num_value'])         

  if p <= 0.05:
      p_result = 'Распределение отличается по полу'
  else:
      p_result = 'Нет различия в распределении между мужчинами и женщинами'

  result_text = [
    html.P(f"Показатель: {ind_text}", className="card-text"),
    html.P(f"Результаты сравнения: p-value = {round(p, 7)}", className="card-text"),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")
          )

def get_observations_stat(filter_sex):
  """
  Функция подготавливает статистику по сроку наблюдения в месяцах:
  """
  df_hevents = get_observations()

  # Формирование таблицы
  df_monthes_b22 = df_hevents[(df_hevents['sex'].isin(filter_sex))]
  df_monthes_b22['indicator'] = 'Cрок наблюдения в месяцах'
  total_table = pd.pivot_table(df_monthes_b22, values = 'monthes_observ', index = ['sex','indicator'], 
                              aggfunc=['mean','min','max','std','median'])                  
  total_table.reset_index(inplace=True)
  total_table.columns = ['Пол','Показатель','Среднее','Min','Max','Ст откл','Медиана']
  total_table=total_table.round(2)

  # График
  fig = px.box(df_monthes_b22, x='sex', y = 'monthes_observ',
             color = 'sex',
             facet_col = 'indicator',
             points = 'all',
             title = 'Распределение показателя по полу',
             labels = {'monthes_observ':'Значение','sex':'Пол'}
)

  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                      plot_bgcolor='rgb(243, 243, 243)'
                    )
  #fig.show(config={'displaylogo':False})

  # Результат тестирования        
  df_m_monthes = df_monthes_b22[(df_monthes_b22['sex'] == 'M')]
  df_f_monthes = df_monthes_b22[(df_monthes_b22['sex'] == 'F')]

  stat, p = ttest_ind(df_m_monthes['monthes_observ'], df_f_monthes['monthes_observ'])        

  if p <= 0.05:
      p_result = 'Распределение отличается по полу'
  else:
      p_result = 'Нет различия в распределении между мужчинами и женщинами'

  result_text = [
    html.P(f"Показатель: Срок наблюдения в месяцах", className="card-text"),
    html.P(f"Результаты сравнения: p-value = {round(p, 7)}", className="card-text"),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")
          )


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
        'ИМТ',
        'Срок наблюдения'
      ]
      kf_otions = [{'label':group, 'value':group} for group in kf_list]
      return kf_otions, 'Возраст'

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
        if filter_kf == 'Возраст':
          return get_age_stat(filter_sex)

        elif filter_kf == 'Рост':#,'Вес','ИМТ']:
          return get_ind_stat(filter_sex, 1)

        elif filter_kf == 'Вес':#,'ИМТ']:
          return get_ind_stat(filter_sex, 2)

        elif filter_kf == 'ИМТ':
          return get_ind_stat(filter_sex, 3)

        elif filter_kf in['Срок наблюдения']:
          return get_observations_stat(filter_sex)
