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
from datetime import datetime
from scipy.stats import ttest_ind
from scipy.stats import chi2_contingency
from textwrap import dedent


def get_groups_stat():
  """
  Функция подготавливает статистику по группам исследования:
  """
  df_hist = get_short_hist_data()

  # Формирование таблицы 
  df_group_gr_count = df_hist.groupby(['research_group']).agg({'patient_id':'count'})
  df_group_gr_count['indicator_type'] = 'Абсолютное значение'
  df_group_gr_proc = round(df_hist.groupby(['research_group']).agg({'patient_id':'count'})/
                          df_group_gr_count['patient_id'].sum()*100,2)
  df_group_gr_proc['indicator_type'] = '%'
  df_group_gr = pd.concat([df_group_gr_count, df_group_gr_proc])
  df_group_gr['indicator'] = 'Общее количество пациентов'
  df_group_gr.reset_index(inplace=True)
  total_table = df_group_gr.pivot(index = ['research_group','indicator'], columns = ['indicator_type'], values = 'patient_id')
  #total_table = df_group_gr
  total_table.reset_index(inplace=True)
  total_table.columns = ['Группа исследования','Показатель','%','Абс. значение']
  total_table=total_table.round(2) 
  totals = pd.DataFrame([['Итого','',total_table['%'].sum(),total_table['Абс. значение'].sum()]], columns=list(total_table.columns))
  total_table = pd.concat([total_table, totals], ignore_index=True)
  return(dbc.Table.from_dataframe(total_table, striped=True, bordered=True, hover=True))

def register_callback(dashapp):
    @dashapp.callback(Output('html_output_table','children'),
                      [Input('html_hidden_div', 'style')])
    def get_total_table(div_style):          
        """"
        Формирование таблицы с основной статистикой
        """        
        return get_groups_stat()

