import pandas as pd
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from utils.data import DashboardData
from utils import elements

data = DashboardData()

# define core elements as global variables, with horizontally aligned divs on the same line.
# Objed id's are the variable name with '-' in place of '_'
dashboard_header = elements.get_dashboard_header()

counties_display = html.Div([elements.get_counties_display(data)],
                            style=dict(width='89%', float='center', display='inline-block'))
counties_dropdown = html.Div([elements.get_counties_dropdown(data)],
                             style=dict(width='39%', float='center', display='inline-block'))

# selected_counties_scale = elements.get_selected_counties_scale()

counties_embedding_display = elements.get_counties_embedding_display(data)
counties_clustering_display = elements.get_counties_clustering_display(data)
counties_embedding_panel = html.Div(
  [
    html.Div([counties_embedding_display], style=dict(width='39%', float='left', display='inline-block')),
    html.Div([counties_clustering_display], style=dict(width='59%', float='right', display='inline-block'))
  ])

# infections_display = elements.get_infections_display(data)
# deaths_display = elements.get_deaths_display(data)
timeseries_display = elements.get_timeseries_display(data)
timeseries_gradient_display = elements.get_timeseries_gradient_display(data)
timeseries_type_dropdown = elements.get_timeseries_type_dropdown()
interventions_dropdown = elements.get_interventions_dropdown(data)
timeseries_mode_radioitems = elements.get_timeseries_mode_radioitems()
timeseries_scale_radioitems = elements.get_timeseries_scale_radioitems()
timeseries_percapita_radioitems = elements.get_timeseries_percapita_radioitems(data)
selected_counties_timeseries_panel = html.Div(
  [
    html.Div([timeseries_type_dropdown,
              interventions_dropdown,
              timeseries_mode_radioitems,
              timeseries_scale_radioitems,
              timeseries_percapita_radioitems],
             style=dict(width='19%', float='left', display='inline-block')),
    html.Div([timeseries_display, timeseries_gradient_display],
             style=dict(width='79%', float='right', display='inline-block'))
  ])

# define the app and its layout
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
  [
    # dashboard_header,
    counties_display,
    counties_dropdown,
    counties_embedding_panel,
    selected_counties_timeseries_panel,
  ])


@app.callback(
  Output('counties-dropdown', 'value'),
  [Input('counties-display', 'clickData'),
   Input('counties-embedding-display', 'clickData')])
def update_selected_county(display_click_data, embedding_click_data):
  if display_click_data is not None:
    fips = display_click_data['points'][0]['customdata'][0]
    data.set_selected_county(fips)
  elif embedding_click_data is not None:
    fips = embedding_click_data['points'][0]['customdata']
    data.set_selected_county(fips)
  return data.selected_county


@app.callback(
  Output('counties-embedding-display', 'figure'),
  [Input('counties-dropdown', 'value')])
def update_embedding(fips):
  data.set_selected_county(fips)
  return elements.get_counties_embedding_figure(data)


@app.callback(
  Output('counties-clustering-display', 'figure'),
  [Input('counties-dropdown', 'value')])
def update_clustering_display(fips):
  data.set_selected_county(fips)
  return elements.get_counties_clustering_figure(data)


@app.callback(
  Output('timeseries-display', 'figure'),
  [Input('counties-dropdown', 'value'),
   Input('timeseries-type-dropdown', 'value'),
   Input('interventions-dropdown', 'value'),
   Input('timeseries-mode-radioitems', 'value'),
   Input('timeseries-scale-radioitems', 'value'),
   Input('timeseries-percapita-radioitems', 'value')])
def update_timeseries_display(fips, timeseries_type, intervention, mode, scale, per_capita):
  data.set_selected_county(fips)
  return elements.get_timeseries_figure(data, timeseries_type, mode=mode, intervention=intervention,
                                        scale=scale, per_capita=per_capita == 'per_capita')


@app.callback(
  Output('timeseries-gradient-display', 'figure'),
  [Input('counties-dropdown', 'value'),
   Input('timeseries-type-dropdown', 'value'),
   Input('interventions-dropdown', 'value'),
   Input('timeseries-mode-radioitems', 'value'),
   Input('timeseries-scale-radioitems', 'value'),
   Input('timeseries-percapita-radioitems', 'value')])
def update_gradient_display(fips, timeseries_type, intervention, mode, scale, per_capita):
  data.set_selected_county(fips)
  return elements.get_timeseries_figure(data, timeseries_type, mode=mode, intervention=intervention,
                                        scale=scale, per_capita=per_capita == 'per_capita',
                                        gradient=True)


if __name__ == '__main__':
  app.run_server(debug=True)
