import string
import json
import numpy as np
import pandas as pd
from urllib.request import urlopen
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html


def get_dashboard_header():
  return html.Div('County-level Response to COVID-19', id='dashboard-header')


with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
  counties_geojson = json.load(response)

  
def get_counties_display(data):
  """FIXME! briefly describe function

  :param data: 
  :returns: 
  :rtype: 

  """
  df = data.total_infections
  color_max = np.quantile(df['infections_per_capita'], 0.9)
  
  fig = px.choropleth(
    df,
    geojson=counties_geojson,
    locations='FIPS',
    color='infections_per_capita',
    color_continuous_scale='Reds',
    hover_name='county_name',
    hover_data=['infections'],
    custom_data=['FIPS'],
    scope='usa',
    height=800,
    range_color=(0, color_max),
    labels={'infections_per_capita': f'Infections per {data.per_what:,d}',
            'infections': 'Infections'},
    title='Infections per {:,d}, {}'.format(data.per_what, data.daily_infections_date.strftime('%B %d, %Y')))
  fig.update_layout(coloraxis_showscale=False)
  
  return dcc.Graph(id='counties-display', figure=fig, config={'scrollZoom': True})


def get_counties_dropdown(data):
  return dcc.Dropdown(
    id='counties-dropdown',
    options=[{'label': row['county_name'], 'value': row['FIPS']} for idx, row in data.county_names.iterrows()],
    value=[],
    multi=True,
    placeholder='Select a county.',
    style={# 'height': 384, 
           'maxHeight': 384,
           'overflow': 'scroll'})


def _get_timeseries_figure(data, timeseries_type):
  assert timeseries_type in ['infections', 'deaths']
  title = f'Confirmed {string.capwords(timeseries_type)}'
  timeseries = getattr(data, timeseries_type)

  data = [
    dict(
      x=list(range(len(row))),
      y=row[1:],
      mode='lines+markers',
      text=data.fips_to_county_name.get(row[0], 'NA'),
      # color=data.fips_to_cluster_labels.get(row[0], 'black'),
      hoverinfo='text+y')
    for i, row in timeseries.iterrows()]

  layout = dict(
    title=title,
    # margin={'l': 20, 'b': 30, 'r': 10, 't': 10},
    # annotations=[{
    #   'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
    #   'xref': 'paper', 'yref': 'paper', 'showarrow': False,
    #   'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)'}],
    showlegend=False,
    xaxis={},
    hovermode='closest')
    
  return dict(data=data, layout=layout)


def get_infections_display(data):
  fig = _get_timeseries_figure(data, 'infections')
  return dcc.Graph(id=f'infections-display',
                   figure=fig,
                   hoverData={'points': [{'customdata': '17031'}]})


def get_deaths_display(data):
  fig = _get_timeseries_figure(data, 'deaths')
  return dcc.Graph(id=f'deaths-display',
                   figure=fig,
                   hoverData={'points': [{'customdata': '17031'}]})

