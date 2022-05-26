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
from .db_tools import get_short_hist_data, get_ind_values, get_observations, get_research_groups
from datetime import datetime
import statsmodels.api as sm
from statsmodels.formula.api import ols
#from loguru import logger


def get_age_stat(filter_group):
  """
  Функция подготавливает статистику по возрасту 
  """
  df_hist = get_short_hist_data()

  # Формирование таблицы
  df_group_age = df_hist[(df_hist['age'] > 10) & (df_hist['research_group'].isin(filter_group))]
  df_group_age['indicator'] = 'Возраст'
  total_table = pd.pivot_table(df_group_age, values = 'age', index = ['research_group','indicator'],
                                 aggfunc=['mean','min','max','std','median'])
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа','Показатель','Среднее','Min','Max','Ст откл','Медиана']
  total_table=total_table.round(2)

  # График
  fig = px.box(df_group_age, x = 'research_group', y= 'age',
              color = 'research_group',
              points = 'all',
              title='Распределение пациентов по возрасту в группах',
              labels = {'research_group':'Группа', 'age':'Возраст'}
              )
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                  plot_bgcolor='rgb(243, 243, 243)'
                 )
  fig.update_layout(legend=dict(
    orientation="h",
    yanchor="top",
    #y=1.02,
    xanchor="right",
    x=0.5
                ))
  fig.update_xaxes(showticklabels=False)
  #fig.show(config={'displaylogo':False})

  # Результат тестирования        
  my_mod = ols('age ~ research_group', data = df_group_age).fit()
  aov_table = sm.stats.anova_lm(my_mod)
  p = aov_table['PR(>F)'][0]         

  if p <= 0.05:
      p_result = 'Есть различия по возрасту между группами'
  else:
      p_result = 'Нет различий по возрасту между группами'

  result_text = [
    html.P("Показатель: Возраст", className="card-text"),
    html.P(f"Результаты сравнения возраста по группам: ", className="card-text"),
    dbc.Table.from_dataframe(aov_table, striped=True, bordered=True, hover=True),
    html.P(p_result, className="card-text"),
  ]

  return [dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), fig,
          html.P(result_text, className="card-text")]

def get_ind_stat(filter_group, ind_id):
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

  df_ind_b33 = df_ind_values[(df_ind_values['event_id']==3) 
                            & (df_ind_values['ind_id'].isin([ind_id]))
                            & (df_ind_values['research_group'].isin(filter_group))
                            ]
  total_table = pd.pivot_table(df_ind_b33, values = 'num_value', index = ['research_group','indicator'], 
                              aggfunc=['mean','min','max','std','median'])                   
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа исследования','Показатель','Среднее','Min','Max','Ст откл','Медиана']
  total_table=total_table.round(2)

  # График
  fig = px.box(df_ind_b33, x='research_group', y = 'num_value',
             color = 'research_group',
             facet_col = 'indicator',
             #points = 'all',
             title = 'Распределение веса, роста, ИМТ по группам',
             labels = {'num_value':'Значение','research_group':'Группа'}
  )
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                  plot_bgcolor='rgb(243, 243, 243)'
                 )
  fig.update_layout(legend=dict(
    orientation="h",
    yanchor="top",
    #y=1.02,
    xanchor="right",
    x= 0.5
  ))

  fig.update_xaxes(showticklabels=False)
  #fig.show(config={'displaylogo':False})

  # Результат тестирования        
  my_mod_h = ols('num_value ~ research_group', data = df_ind_b33).fit()
  aov_table = sm.stats.anova_lm(my_mod_h)
  p = aov_table['PR(>F)'][0]       

  if p <= 0.05:
      p_result = 'Есть различия между группами'
  else:
      p_result = 'Нет различий между группами'

  result_text = [
    html.P(f"Показатель: {ind_text}", className="card-text"),
    html.P("Результаты сравнения:"),
    dbc.Table.from_dataframe(aov_table, striped=True, bordered=True, hover=True),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")
          )

def get_observations_stat(filter_group):
  """
  Функция подготавливает статистику по сроку наблюдения в месяцах:
  """
  df_hevents = get_observations()

  # Формирование таблицы
  df_monthes_b39 = df_hevents[(df_hevents['research_group'].isin(filter_group))]
  df_monthes_b39['indicator'] = 'Cрок наблюдения в месяцах'
  total_table = pd.pivot_table(df_monthes_b39, values = 'monthes_observ', index = ['research_group','indicator'], 
                              aggfunc=['mean','min','max','std','median'])                  
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа исследования','Показатель','Среднее','Min','Max','Ст откл','Медиана']
  total_table=total_table.round(2)

  # График
  fig = px.box(df_monthes_b39, x='research_group', y = 'monthes_observ',
             color = 'research_group',
             #facet_col = 'indicator',
             points = 'all',
             title = 'Распределение показателя по группам',
             labels = {'monthes_observ':'Значение','research_group':'Группа исследования'}
)

  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                      plot_bgcolor='rgb(243, 243, 243)'
                    )
  fig.update_xaxes(showticklabels=False)
  #fig.show(config={'displaylogo':False})

  # Результат тестирования        
  model_monthes_observ = ols('monthes_observ ~ research_group', data = df_monthes_b39).fit()
  aov_table_monthes_observ = sm.stats.anova_lm(model_monthes_observ)
  p = aov_table_monthes_observ['PR(>F)'][0]        

  if p <= 0.05:
      p_result = 'Распределение отличается по группам'
  else:
      p_result = 'Нет различий между группами'

  result_text = [
    html.P(f"Показатель: Срок наблюдения в месяцах", className="card-text"),
    html.P("Результаты сравнения:", className="card-text"),
    dbc.Table.from_dataframe(aov_table_monthes_observ, striped=True, bordered=True, hover=True),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")
          )

def register_callback(dashapp):
    @dashapp.callback([Output('html_filter_group','options'),
                      Output('html_filter_group','value')],
                      [Input('html_hidden_div', 'style')]
                      )
    def get_filter_group(div_style):
      """
      Подготовка списка групп исследования
      """
      research_group_otions = [{'label':group, 'value':group} for group in get_research_groups()]
      research_group_values = get_research_groups()
      return research_group_otions, research_group_values

    @dashapp.callback([Output('html_output_table','children'),
                       Output('kf_output_graph','figure'),
                       Output('html_output_text','children')
                      ],                       
                    [ Input('html_filter_group', 'value' ), 
                      Input('html_filter_kf', 'value')
                     ])
    #@logger.catch
    def get_total_table(filter_group, filter_kf):          
        """"
        Формирование таблицы с основной статистикой
        """
        if filter_group is None:
          filter_group = get_research_groups()

        if filter_kf == 'Возраст':
          return get_age_stat(filter_group)

        elif filter_kf == 'Рост':#,'Вес','ИМТ']:
          return get_ind_stat(filter_group, 1)

        elif filter_kf == 'Вес':#,'ИМТ']:
          return get_ind_stat(filter_group, 2)

        elif filter_kf == 'ИМТ':
          return get_ind_stat(filter_group, 3)

        elif filter_kf in['Срок наблюдения']:
          return get_observations_stat(filter_group)
