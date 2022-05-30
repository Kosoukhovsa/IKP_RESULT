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
from .db_tools import get_operations, get_short_hist_data, get_asa, get_research_groups, \
                      get_observations
from datetime import datetime
#from scipy.stats import ttest_ind
from scipy.stats import chi2_contingency
from scipy.stats import chi2
#import statsmodels.api as sm
#from statsmodels.formula.api import ols
#from loguru import logger


def get_side_stat(filter_group):
  """
  Функция подготавливает статистику по строне поражения 
  """
  df_hist = get_short_hist_data()
  df_hist = df_hist[df_hist['research_group'].isin(filter_group)]
  # Формирование таблицы
  df_side_count = df_hist.groupby(['research_group','side_damage']).agg({'patient_id':'count'})
  df_side_count['indicator_type'] = 'Абсолютное значение'
  df_side_proc = round(df_hist.groupby(['research_group','side_damage']).agg({'patient_id':'count'})/df_hist['patient_id'].nunique()*100)
  df_side_proc['indicator_type'] = '%'

  df_side = pd.concat([df_side_count, df_side_proc])
  df_side['indicator'] = 'Сторона поражения'

  df_side.reset_index(inplace=True)
  #df_sex_gr.columns
  total_table = df_side.pivot(index = ['research_group','indicator','side_damage'], columns = ['indicator_type'], values = 'patient_id')
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа','Показатель','Сторона поражения','%','Абсолютное значение']
  total_table=total_table.round(2)

  # График
  fig = px.bar(total_table, x='Сторона поражения', y = 'Абсолютное значение',
                        color = 'Сторона поражения',
                        facet_col= 'Группа'
                        )
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                      plot_bgcolor='rgb(243, 243, 243)'
                    )
  fig.update_xaxes(showticklabels=False)
  fig.for_each_annotation(lambda a: a.update(text=a.text.split(" ")[0]))
  #fig.show(config={'displaylogo':False})

  # Результат тестирования        
  df_side_count = df_hist.groupby(['side_damage','research_group']).agg({'patient_id':'count'})
  df_side_pivot = pd.pivot_table(df_side_count, index = ['side_damage'], columns = 'research_group', values = 'patient_id')

  contingency_table= [df_side_pivot] 
  stat, p, dof, expected = chi2_contingency(contingency_table)  
  critical = chi2.ppf(0.95, dof)
  
  if p > 0.05 and stat < critical:
        p_result = 'Вывод: Нет различий по группе, с вероятностью 95%'
  else:
        p_result = 'Вывод: Есть различия по группе, с вероятностью 95%'

  result_text = [
    html.P("Показатель: Сторона поражения", className="card-text"),
    html.P(f"Число степеней свободы: {dof}", className="card-text"),
    #dbc.Table.from_dataframe(df_side_pivot, striped=True, bordered=True, hover=True),
    html.P(f"Результаты сравнения: хи-квадрат = {round(stat,3)}, критическое = {round(critical,3)}, p-value: {round(p,5)}", className="card-text"),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text"))

def get_asa_stat(filter_group):
  """
  Функция подготавливает статистику по опроснику ASA 
  """
  df_asa = get_asa()
  df_asa = df_asa[df_asa['research_group'].isin(filter_group)]
  # Формирование таблицы
  df_asa_gr_count = df_asa.groupby(['research_group','ASA']).agg({'patient_id':'count'})
  df_asa_gr_count['indicator_type'] = 'Абсолютное значение'
  df_asa_gr_proc = round(df_asa.groupby(['research_group','ASA']).agg({'patient_id':'count'})/df_asa['patient_id'].nunique()*100)
  df_asa_gr_proc['indicator_type'] = '%'
  df_asa_gr = pd.concat([df_asa_gr_count,df_asa_gr_proc])
  df_asa_gr['indicator'] = 'ASA'
  df_asa_gr.reset_index(inplace=True)
  total_table = df_asa_gr.pivot(index = ['research_group','indicator','ASA'], columns = ['indicator_type'], values = 'patient_id')

  #df_sex_gr.columns
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа','Показатель','ASA','%','Абсолютное значение']
  total_table=total_table.round(2)

  # График
  fig = px.bar(total_table, x='ASA', y = 'Абсолютное значение',
                        color = 'ASA',
                        facet_col= 'Группа'
                        )
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                      plot_bgcolor='rgb(243, 243, 243)'
                    )
  fig.update_xaxes(showticklabels=False)
  fig.for_each_annotation(lambda a: a.update(text=a.text.split(" ")[0]))
  #fig.show(config={'displaylogo':False})

  # Результат тестирования        
  df_asa_count = df_asa.groupby(['ASA','research_group']).agg({'patient_id':'count'})
  df_asa_pivot = pd.pivot_table(df_asa_count, index = ['ASA'], columns = 'research_group', values = 'patient_id').fillna(0)

  contingency_table= [df_asa_pivot]
  stat, p, dof, expected = chi2_contingency(contingency_table)         

  critical = chi2.ppf(0.95, dof)
  
  if p > 0.05 and stat < critical:
        p_result = 'Нет различий по группе, с вероятностью 95%'
  else:
        p_result = 'Есть различия по группе, с вероятностью 95%'

  result_text = [
    html.P("Показатель: ASA", className="card-text"),
    html.P(f"Число степеней свободы: {dof}", className="card-text"),
    html.P(f"Результаты сравнения: хи-квадрат = {round(stat,3)}, критическое = {round(critical,3)}, p-value: {round(p,5)}", className="card-text"),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")  )


def get_operations_stat(filter_group):
  """
  Функция подготавливает статистику по количеству операций
  """
  df_operations = get_operations()
  df_operations = df_operations[df_operations['research_group'].isin(filter_group)]
  df_operations_gr34_proc = round(df_operations.groupby(['research_group','fio']).agg({'id':'count'}) / df_operations['id'].count()*100)
  df_operations_gr34_proc['indicator_type'] = 'Абсолютное значение'
  df_operations_gr34_count = df_operations.groupby(['research_group','fio']).agg({'id':'count'})
  df_operations_gr34_count['indicator_type'] = '%'
  df_operations_gr34 = pd.concat([df_operations_gr34_proc, df_operations_gr34_count])
  df_operations_gr34.reset_index(inplace=True)
  total_table = df_operations_gr34.pivot(index = ['research_group','fio'], columns = ['indicator_type'], values = 'id')
    
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа','Хирург','%','Абсолютное значение']
  total_table=total_table.round(2)

  # График
  fig = px.bar(total_table, x = 'Хирург', y = 'Абсолютное значение',
            color='Хирург',
            facet_col = 'Группа',
            labels = {'Хирург':'Хирург'})

  fig.update_xaxes(showticklabels=False)
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                    plot_bgcolor='rgb(243, 243, 243)'
                  )
  fig.for_each_annotation(lambda a: a.update(text=a.text.split(" ")[0]))
  #fig.show(config={'displaylogo':False})

  # Результат тестирования        
  df_operations_count = df_operations.groupby(['fio','research_group']).agg({'id':'count'})
  df_operations_pivot = pd.pivot_table(df_operations_count, index = ['fio'], columns = 'research_group', values = 'id').fillna(0)

  contingency_table= [df_operations_pivot]
  stat, p, dof, expected = chi2_contingency(contingency_table)         

  critical = chi2.ppf(0.95, dof)
  
  if p > 0.05 and stat < critical:
        p_result = 'Нет различий по группе, с вероятностью 95%'
  else:
        p_result = 'Есть различия по группе, с вероятностью 95%'

  result_text = [
    html.P("Показатель: Количество операций", className="card-text"),
    html.P(f"Число степеней свободы: {dof}", className="card-text"),
    html.P(f"Результаты сравнения: хи-квадрат = {round(stat,3)}, критическое = {round(critical,3)}, p-value: {round(p,5)}", className="card-text"),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")  )

def get_oper_steps_stat(filter_group):
  """
  Функция подготавливает статистику по количеству пациентов по этапам обследования
  """
  df_hevents = get_observations()  
  df_hist = get_short_hist_data()  
  df_hevents = df_hevents[df_hevents['research_group'].isin(filter_group)]
  df_hist = df_hist[df_hist['research_group'].isin(filter_group)]
  df_hevents_gr310_proc = round(df_hevents.groupby(['description','research_group']).agg({'patient_id':'count'})/df_hist['patient_id'].nunique()*100)
  df_hevents_gr310_count = df_hevents.groupby(['description','research_group']).agg({'patient_id':'count'})
  total_table = pd.merge( df_hevents_gr310_proc, df_hevents_gr310_count, on = ['description','research_group']).reset_index()
  total_table['description'] = total_table['description'].str.replace('\n',' ')
  total_table.columns = ['Наблюдение','Группа','Абсолютное значение', '%']   
  total_table=total_table.round(2)

  # График
  fig = px.bar(total_table, x = 'Наблюдение', y = 'Абсолютное значение',
            color='Наблюдение',
            facet_col = 'Группа',
            labels = {'Наблюдение':'Наблюдение'})

  fig.update_xaxes(showticklabels=False)
  fig.update_layout(paper_bgcolor='rgb(243, 243, 243)',
                    plot_bgcolor='rgb(243, 243, 243)'
                  )
  fig.for_each_annotation(lambda a: a.update(text=a.text.split(" ")[0]))
  #fig.show(config={'displaylogo':False})

  # Результат тестирования        
  df_obs_count = df_hevents.groupby(['description','research_group']).agg({'patient_id':'count'})
  df_obs_pivot = pd.pivot_table(df_obs_count, index = ['description'], columns = 'research_group', values = 'patient_id').fillna(0)

  contingency_table= [df_obs_pivot]
  stat, p, dof, expected = chi2_contingency(contingency_table)         

  critical = chi2.ppf(0.95, dof)
  
  if p > 0.05 and stat < critical:
        p_result = 'Нет различий по группе, с вероятностью 95%'
  else:
        p_result = 'Есть различия по группе, с вероятностью 95%'

  result_text = [
    html.P("Показатель: Количество пациентов по этапам обследования", className="card-text"),
    html.P(f"Число степеней свободы: {dof}", className="card-text"),
    html.P(f"Результаты сравнения: хи-квадрат = {round(stat,3)}, критическое = {round(critical,3)}, p-value: {round(p,5)}", className="card-text"),
    html.P(p_result, className="card-text"),
  ]

  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True), 
          fig, 
          html.P(result_text, className="card-text")  )



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

        if filter_kf == 'Сторона поражения':
          return get_side_stat(filter_group)

        elif filter_kf == 'ASA':#,'Вес','ИМТ']:
          return get_asa_stat(filter_group)

        elif filter_kf == 'Количество операций':#,'ИМТ']:
          return get_operations_stat(filter_group)

        elif filter_kf == 'Количество пациентов прошедших по этапам обследования':
          return get_oper_steps_stat(filter_group)


