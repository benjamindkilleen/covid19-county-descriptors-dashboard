import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html

from utils.data import DashboardData
from utils import elements

data = DashboardData()

# define core elements as global variables, with horizontally aligned divs on the same line.
# Objed id's are the variable name with '-' in place of '_'
dashboard_header = elements.get_dashboard_header()

counties_display = elements.get_counties_display(data)
counties_dropdown = elements.get_counties_dropdown(data)
selected_counties_div = html.Div(
  [
    html.Div([counties_display], style=dict(width='69%', float='left', display='inline-block')),
    html.Div([counties_dropdown], style=dict(width='19%', float='right', display='inline-block'))
  ])

selected_counties_infections_display = elements.get_infections_display(data)
selected_counties_deaths_display = elements.get_deaths_display(data)
selected_counties_timeseries_display = html.Div(
  [
    html.Div([selected_counties_infections_display], style=dict(width='49%', float='left', display='inline-block')),
    html.Div([selected_counties_deaths_display], style=dict(width='49%', float='right', display='inline-block'))
  ])

# selected_counties_scale = elements.get_selected_counties_scale()

# counties_embedding_display = elements.get_counties_embedding_display()

# define the app and its layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
  [
    dashboard_header,
    selected_counties_div,
    selected_counties_timeseries_display
  ]
)

if __name__ == '__main__':
  app.run_server(debug=True)
