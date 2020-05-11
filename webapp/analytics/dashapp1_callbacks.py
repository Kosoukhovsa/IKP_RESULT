import os
import pandas as pd
from dash.dependencies import Input
from dash.dependencies import Output
import plotly.graph_objs as go


basedir = os.path.abspath(os.path.dirname(__file__))
path_name1 = os.path.join(basedir, 'patients_m16.csv')
#path_name2 = os.path.join(basedir, 'patients_m17.csv')
patients_m16 = pd.read_csv(path_name1)
#patients_m17 = pd.read_csv(path_name2)

def register_callback(dashapp):
    @dashapp.callback(Output('Box1','figure'), [Input('dropdown-sex','value')])
    def update_graph(selected_value):

        df_selected = patients_m16[patients_m16['Пол']==selected_value]

        return {
            'data': [
                go.Box(y=df_selected['рост'],
                boxpoints = 'all',
                jitter = 0.3,
                pointpos = -1.8
                )
            ]
        }
