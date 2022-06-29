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
from .db_tools import get_short_hist_data, get_ind_values, get_observations, \
                      get_research_groups, get_b_days, get_oper_logs
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
    html.P(f"df: первая строка - кол-во групп, вторая - общее кол-во наблюдений минус колв-во групп ", className="card-text"),
    html.P(f"sum_sq: первая строка - межгрупповая дисперсия, вторая строка - внутригрупповая дисперсия", className="card-text"),
    html.P(f"mean_sq: отношение sum_sq/df по каждой строке", className="card-text"),
    html.P(f"F: отношение  межгрупповая дисперсия/внутригрупповая дисперсия", className="card-text"),
    html.P(f"PR(>F): p-value. Если значение < 0,05 то с вероятностью 95% есть различия между группами", className="card-text"),
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
    html.P(f"df: первая строка - кол-во групп, вторая - общее кол-во наблюдений минус колв-во групп ", className="card-text"),
    html.P(f"sum_sq: первая строка - межгрупповая дисперсия, вторая строка - внутригрупповая дисперсия", className="card-text"),
    html.P(f"mean_sq: отношение sum_sq/df по каждой строке", className="card-text"),
    html.P(f"F: отношение  межгрупповая дисперсия/внутригрупповая дисперсия", className="card-text"),
    html.P(f"PR(>F): p-value. Если значение < 0,05 то с вероятностью 95% есть различия между группами", className="card-text"),
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
    html.P(f"df: первая строка - кол-во групп, вторая - общее кол-во наблюдений минус колв-во групп ", className="card-text"),
    html.P(f"sum_sq: первая строка - межгрупповая дисперсия, вторая строка - внутригрупповая дисперсия", className="card-text"),
    html.P(f"mean_sq: отношение sum_sq/df по каждой строке", className="card-text"),
    html.P(f"F: отношение  межгрупповая дисперсия/внутригрупповая дисперсия", className="card-text"),
    html.P(f"PR(>F): p-value. Если значение < 0,05 то с вероятностью 95% есть различия между группами", className="card-text"),
    dbc.Table.from_dataframe(aov_table_monthes_observ, striped=True, bordered=True, hover=True),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")
          )

def get_b_days_stat(filter_group):
  """
  Общий койко-день
  """

  # Формирование таблицы
  df_b_days = get_b_days()
  df_b_days_b36 = df_b_days[(df_b_days['research_group'].isin(filter_group))]
  df_b_days_b36['indicator'] = 'Общий койко-день'
  df_b_days_b36.rename(columns={'c_days1':'value'}, inplace=True) 

  total_table = pd.pivot_table(df_b_days_b36, values = 'value', index = ['research_group','indicator'], 
                              aggfunc=['mean','min','max','std','median'])
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа исследования','Показатель','Среднее','Min','Max','Ст откл','Медиана']
  total_table=total_table.round(2)
  # График
  fig = px.box(df_b_days_b36, x= 'research_group', y = 'value',
             color = 'research_group',
             points = 'all',
            title = 'Общий койко-день' ,
             labels = {'research_group':'Группа','value':'Дней'} 
            )

  fig.update_xaxes(showticklabels=False)
  fig.update_layout(legend=dict(
      orientation="h",
      #yanchor="top",
      #y=1.02,
      xanchor="right",
      x= 1))
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                    plot_bgcolor='rgb(243, 243, 243)'
                  )
  # Результат тестирования 
  data = df_b_days[(df_b_days['c_days1']>0) & (df_b_days['research_group'].isin(filter_group))]
  my_mod_days_all = ols('c_days1 ~ research_group', data).fit()
  aov_table_days_all = sm.stats.anova_lm(my_mod_days_all)
  p = aov_table_days_all['PR(>F)'][0]

  if p <= 0.05:
      p_result = 'Распределение отличается по группам'
  else:
      p_result = 'Нет различий между группами'

  result_text = [
    html.P(f"Показатель:  Общий койко-день", className="card-text"),
    html.P("Результаты сравнения:", className="card-text"),
    html.P(f"df: первая строка - кол-во групп, вторая - общее кол-во наблюдений минус колв-во групп ", className="card-text"),
    html.P(f"sum_sq: первая строка - межгрупповая дисперсия, вторая строка - внутригрупповая дисперсия", className="card-text"),
    html.P(f"mean_sq: отношение sum_sq/df по каждой строке", className="card-text"),
    html.P(f"F: отношение  межгрупповая дисперсия/внутригрупповая дисперсия", className="card-text"),
    html.P(f"PR(>F): p-value. Если значение < 0,05 то с вероятностью 95% есть различия между группами", className="card-text"),
    dbc.Table.from_dataframe(aov_table_days_all, striped=True, bordered=True, hover=True),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")
          )

def get_b_days_before_stat(filter_group):
  """
  Предоперационный койко-день
  """

  # Формирование таблицы
  df_b_days = get_b_days()
  df_b_days_b36 = df_b_days[(df_b_days['research_group'].isin(filter_group))]
  df_b_days_b36['indicator'] = 'Предоперационный койко-день'
  df_b_days_b36.rename(columns={'c_days2':'value'}, inplace=True) 

  total_table = pd.pivot_table(df_b_days_b36, values = 'value', index = ['research_group','indicator'], 
                              aggfunc=['mean','min','max','std','median'])
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа исследования','Показатель','Среднее','Min','Max','Ст откл','Медиана']
  total_table=total_table.round(2)
  # График
  fig = px.box(df_b_days_b36, x= 'research_group', y = 'value',
             color = 'research_group',
             points = 'all',
            title = 'Предоперационный койко-день' ,
             labels = {'research_group':'Группа','value':'Дней'} 
            )

  fig.update_xaxes(showticklabels=False)
  fig.update_layout(legend=dict(
      orientation="h",
      #yanchor="top",
      #y=1.02,
      xanchor="right",
      x= 1))
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                    plot_bgcolor='rgb(243, 243, 243)'
                  )
  # Результат тестирования 
  data = df_b_days[(df_b_days['c_days2']>0) & (df_b_days['research_group'].isin(filter_group))]
  my_mod_days_all = ols('c_days2 ~ research_group', data).fit()
  aov_table_days_all = sm.stats.anova_lm(my_mod_days_all)
  p = aov_table_days_all['PR(>F)'][0]

  if p <= 0.05:
      p_result = 'Распределение отличается по группам'
  else:
      p_result = 'Нет различий между группами'

  result_text = [
    html.P(f"Показатель:  Предоперационный койко-день", className="card-text"),
    html.P("Результаты сравнения:", className="card-text"),
    html.P(f"df: первая строка - кол-во групп, вторая - общее кол-во наблюдений минус колв-во групп ", className="card-text"),
    html.P(f"sum_sq: первая строка - межгрупповая дисперсия, вторая строка - внутригрупповая дисперсия", className="card-text"),
    html.P(f"mean_sq: отношение sum_sq/df по каждой строке", className="card-text"),
    html.P(f"F: отношение  межгрупповая дисперсия/внутригрупповая дисперсия", className="card-text"),
    html.P(f"PR(>F): p-value. Если значение < 0,05 то с вероятностью 95% есть различия между группами", className="card-text"),
    dbc.Table.from_dataframe(aov_table_days_all, striped=True, bordered=True, hover=True),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")
          )
  
def get_b_days_after_stat(filter_group):
  """
  Послеоперационный койко-день
  """

  # Формирование таблицы
  df_b_days = get_b_days()
  df_b_days_b36 = df_b_days[(df_b_days['research_group'].isin(filter_group))]
  df_b_days_b36['indicator'] = 'Послеоперационный койко-день'
  df_b_days_b36.rename(columns={'c_days3':'value'}, inplace=True) 

  total_table = pd.pivot_table(df_b_days_b36, values = 'value', index = ['research_group','indicator'], 
                              aggfunc=['mean','min','max','std','median'])
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа исследования','Показатель','Среднее','Min','Max','Ст откл','Медиана']
  total_table=total_table.round(2)
  # График
  fig = px.box(df_b_days_b36, x= 'research_group', y = 'value',
             color = 'research_group',
             points = 'all',
            title = 'Послеоперационный койко-день' ,
             labels = {'research_group':'Группа','value':'Дней'} 
            )

  fig.update_xaxes(showticklabels=False)
  fig.update_layout(legend=dict(
      orientation="h",
      #yanchor="top",
      #y=1.02,
      xanchor="right",
      x= 1))
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                    plot_bgcolor='rgb(243, 243, 243)'
                  )
  # Результат тестирования 
  data = df_b_days[(df_b_days['c_days3']>0) & (df_b_days['research_group'].isin(filter_group))]
  my_mod_days_all = ols('c_days3 ~ research_group', data).fit()
  aov_table_days_all = sm.stats.anova_lm(my_mod_days_all)
  p = aov_table_days_all['PR(>F)'][0]

  if p <= 0.05:
      p_result = 'Распределение отличается по группам'
  else:
      p_result = 'Нет различий между группами'

  result_text = [
    html.P(f"Показатель:  Послеоперационный койко-день", className="card-text"),
    html.P("Результаты сравнения:", className="card-text"),
    html.P(f"df: первая строка - кол-во групп, вторая - общее кол-во наблюдений минус колв-во групп ", className="card-text"),
    html.P(f"sum_sq: первая строка - межгрупповая дисперсия, вторая строка - внутригрупповая дисперсия", className="card-text"),
    html.P(f"mean_sq: отношение sum_sq/df по каждой строке", className="card-text"),
    html.P(f"F: отношение  межгрупповая дисперсия/внутригрупповая дисперсия", className="card-text"),
    html.P(f"PR(>F): p-value. Если значение < 0,05 то с вероятностью 95% есть различия между группами", className="card-text"),
    dbc.Table.from_dataframe(aov_table_days_all, striped=True, bordered=True, hover=True),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")
          )

def get_operations_stat(filter_group):
  """
  Общая длительность операции
  """

  # Формирование таблицы
  df_op_time = get_oper_logs()
  df_op_time_b38 = df_op_time[(df_op_time['research_group'].isin(filter_group))]
  df_op_time_b38_gr = df_op_time_b38.groupby(['research_group','operation_id']).agg({'duration_min':'sum'}).reset_index()

  total_table = pd.pivot_table(df_op_time_b38_gr, values = 'duration_min', index = ['research_group'], 
                              aggfunc=['mean','min','max','std','median'])
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа исследования','Среднее','Min','Max','Ст откл','Медиана']
  total_table=total_table.round(2)
  # График
  fig = px.box(df_op_time_b38_gr, x= 'research_group', y = 'duration_min',
             color = 'research_group',
             points = 'all',
             
            title = 'Длительность операции по группам' ,
             labels = {'research_group':'Группа','duration_min':'Минуты'} 
            )

  fig.update_xaxes(showticklabels=False)
  fig.update_layout(legend=dict(
      orientation="h",
      #yanchor="top",
      #y=1.02,
      xanchor="right",
      x= 1))
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                    plot_bgcolor='rgb(243, 243, 243)'
                  )
  fig.for_each_annotation(lambda a: a.update(text=a.text.split(" ")[0]))

  # Результат тестирования  
  data = df_op_time_b38_gr[(df_op_time_b38_gr['research_group'].isin(filter_group))]
  my_mod = ols('duration_min ~ research_group', data).fit()
  aov_table = sm.stats.anova_lm(my_mod,  )
  p = aov_table['PR(>F)'][0]

  if p <= 0.05:
      p_result = 'Распределение отличается по группам'
  else:
      p_result = 'Нет различий между группами'

  result_text = [
    html.P(f"Показатель:  Общая длительность операции", className="card-text"),
    html.P("Результаты сравнения:", className="card-text"),
    html.P(f"df: первая строка - кол-во групп, вторая - общее кол-во наблюдений минус колв-во групп ", className="card-text"),
    html.P(f"sum_sq: первая строка - межгрупповая дисперсия, вторая строка - внутригрупповая дисперсия", className="card-text"),
    html.P(f"mean_sq: отношение sum_sq/df по каждой строке", className="card-text"),
    html.P(f"F: отношение  межгрупповая дисперсия/внутригрупповая дисперсия", className="card-text"),
    html.P(f"PR(>F): p-value. Если значение < 0,05 то с вероятностью 95% есть различия между группами", className="card-text"),
    dbc.Table.from_dataframe(aov_table, striped=True, bordered=True, hover=True),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")
          )

def get_operations_step_stat(filter_group):
  """
  Длительность каждого этапа операции
  """

  # Формирование таблицы
  df_op_time = get_oper_logs()
  df_op_time_b38 = df_op_time[(df_op_time['research_group'].isin(filter_group))
                             &(df_op_time['duration_min']>0)]
  total_table = pd.pivot_table(df_op_time_b38, values = 'duration_min', index = ['research_group','step_order','operation_step',], 
                              aggfunc=['mean','min','max','std','median'])
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа исследования','Номер этапа','Этап','Среднее','Min','Max','Ст откл','Медиана']
  total_table=total_table.round(2)
  # График
  fig = px.box(df_op_time_b38, x= 'operation_step', y = 'duration_min',
             color = 'operation_step',
             facet_col = 'research_group',
            title = 'Этапы операции по группам' ,
             labels = {'research_group':'Группа','duration_min':'Минуты', 'operation_step':'Этап операции'} 
            )

  fig.update_xaxes(showticklabels=False)
  fig.update_layout(legend=dict(
      orientation="h",
      #yanchor="top",
      #y=1.02,
      xanchor="right",
      x= 1))
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                    plot_bgcolor='rgb(243, 243, 243)'
                  )
  fig.for_each_annotation(lambda a: a.update(text=a.text.split(" ")[0]))

  # Результат тестирования  
  data = df_op_time_b38
  my_mod = ols('duration_min ~ research_group + operation_step', data).fit()
  aov_table = sm.stats.anova_lm(my_mod, type=2)
  p = aov_table['PR(>F)'][0]

  if p <= 0.05:
      p_result = 'Распределение отличается по группам'
  else:
      p_result = 'Нет различий между группами'

  result_text = [
    html.P(f"Показатель:  Длительность каждого этапа операции", className="card-text"),
    html.P("Результаты сравнения:", className="card-text"),
    html.P(f"df: первая строка - кол-во групп, вторая - общее кол-во наблюдений минус колв-во групп ", className="card-text"),
    html.P(f"sum_sq: первая строка - межгрупповая дисперсия, вторая строка - внутригрупповая дисперсия", className="card-text"),
    html.P(f"mean_sq: отношение sum_sq/df по каждой строке", className="card-text"),
    html.P(f"F: отношение  межгрупповая дисперсия/внутригрупповая дисперсия", className="card-text"),
    html.P(f"PR(>F): p-value. Если значение < 0,05 то с вероятностью 95% есть различия между группами", className="card-text"),
    dbc.Table.from_dataframe(aov_table, striped=True, bordered=True, hover=True),
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

        elif filter_kf in['Общий койко-день']:
          return get_b_days_stat(filter_group)

        elif filter_kf in['Предоперационный койко-день']:
          return get_b_days_before_stat(filter_group)

        elif filter_kf in['Послеоперационный койко-день']:
          return get_b_days_after_stat(filter_group)

        elif filter_kf in['Общая длительность операции']:
          return get_operations_stat(filter_group)

        elif filter_kf in['Длительность каждого этапа операции']:
          return get_operations_step_stat(filter_group)

