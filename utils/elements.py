import string
import json
import numpy as np
import pandas as pd
from urllib.request import urlopen
import plotly.express as px
import seaborn as sns

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
    title='United States COVID-19 Confirmed Cases, {}'.format(data.daily_infections_date.strftime('%x')))
  fig.update_layout(coloraxis_showscale=True, coloraxis_colorbar=dict(
    title=f'Infections per {data.per_what:,d}',
    thicknessmode="pixels",
    thickness=20,
    lenmode='pixels',
    len=200,
    ticks='outside',
    dtick=5,
    yanchor='middle'))
  
  return dcc.Graph(id='counties-display', figure=fig, config={'scrollZoom': False})


def get_counties_dropdown(data):
  return dcc.Dropdown(
    id='counties-dropdown',
    options=[{'label': row['county_name'], 'value': row['FIPS']} for idx, row in data.county_names.iterrows()],
    value=data.selected_county,
    multi=False,
    placeholder='Select a county...',
    style={})


def get_timeseries_type_dropdown():
  return dcc.Dropdown(
    id='timeseries-type-dropdown',
    options=[{'label': 'Confirmed Cases', 'value': 'infections'}, {'label': 'Deaths', 'value': 'deaths'}],
    value='infections',
    multi=False,
    placeholder='Choose timeseries...')


def get_interventions_dropdown(data):
  return dcc.Dropdown(
    id='interventions-dropdown',
    options=[{'label': intervention, 'value': intervention} for intervention in data.intervention_keys],
    value='stay at home',
    multi=False,
    placeholder='Intervention type.')


def get_timeseries_mode_radioitems():
  return dcc.RadioItems(
    id='timeseries-mode-radioitems',
    options=[{'label': i, 'value': i} for i in ['Date', 'Threshold']],
    value='Date',
    labelStyle={'display': 'inline-block'})


def get_timeseries_scale_radioitems():
  return dcc.RadioItems(
    id='timeseries-scale-radioitems',
    options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
    value='Linear',
    labelStyle={'display': 'inline-block'})


def get_timeseries_percapita_radioitems(data):
  return dcc.RadioItems(
    id='timeseries-percapita-radioitems',
    options=[{'label': 'Absolute', 'value': 'absolute'}, {'label': f'per {data.per_what:,d}', 'value': 'per_capita'}],
    value='absolute',
    labelStyle={'display': 'inline-block'})


def get_timeseries_figure(
    data,
    timeseries_type='infections',
    mode='Date',
    threshold=50,
    intervention='stay at home',
    scale='Linear',
    per_capita=False,
    gradient=False):
  """FIXME! briefly describe function

  :param data: 
  :param timeseries_type: 
  :param mode: Either 'Analysis' or 'Raw'
  :returns: 
  :rtype: 

  """
  
  # get top 10 counties by default
  assert timeseries_type in ['infections', 'deaths']
  timeseries = getattr(data, timeseries_type + ('_gradient' if gradient else ''))
  timeseries = timeseries.loc[timeseries['FIPS'].isin(set(data.selected_counties))]

  color_palette = sns.color_palette('Set1', n_colors=len(data.selected_counties))
  color_palette = [f'#{int(255*t[0]):02x}{int(255*t[1]):02x}{int(255*t[2]):02x}' for t in color_palette]

  if gradient:
    scale = 'Linear'

  if per_capita:
    value_func = lambda x, fips: x / data.fips_to_population[fips] * data.per_what
  else:
    value_func = lambda x, fips: x
    
  if mode == 'Date':
    xtitle = 'Date'
    start = data.timeseries_start_index
    xfunc = lambda row, idx: data.timeseries_dates[start:]
    yfunc = lambda row, idx: value_func(row[start + 1:], row[0])
  elif mode == 'Threshold':
    xtitle = f'Days since {threshold} Confirmed {string.capwords(timeseries_type)}'
    xfunc = lambda row, idx: list(range(len(row) - data.infections_start_indices[idx] - 1))
    yfunc = lambda row, idx: value_func(row[1:][data.infections_start_indices[idx]:], row[0])
    
  fig_data = [
    dict(
      x=xfunc(row, idx),
      y=yfunc(row, idx),
      mode='lines',
      name=data.fips_to_county_name.get(row[0], 'NA'),
      text=data.fips_to_county_name.get(row[0], 'NA'),
      hoverinfo='text+x+y',
      line=dict(color=color_palette[i]), shape='spline' if gradient else 'linear', smoothing=2)
    for i, (idx, row) in enumerate(timeseries.iterrows())]

  title = f'{string.capwords(timeseries_type)}'
  if gradient:
    title += ' per Day (smoothed)'
  if per_capita:
    title += f', per {data.per_what:,d}'
  
  layout = dict(
    title=title,
    # showlegend=False,
    yaxis={'type': 'log' if scale == 'Log' else 'linear'},
    xaxis={'title': xtitle},
    hovermode='closest',
    annotations=[])

  # add annotations
  annotations = getattr(data, ('threshold_' if mode == 'Threshold' else '') + f'{timeseries_type}_annotations')
  for i, (idx, row) in enumerate(timeseries.iterrows()):
    fips = row['FIPS']
    if annotations.get((fips, intervention)) is None:
      continue
    # if mode == 'Threshold' and annotations[fips, intervention]['x'] > len(fig_data[i]['x']):
    #   continue
    annotation = annotations[fips, intervention].copy()
    annotation['arrowcolor'] = color_palette[i]
    annotation['textfont'] = dict(size=8, color=color_palette[i])
    annotation['y'] = value_func(row[annotation['xidx']], fips)
    if scale == 'Log':
      annotation['y'] = np.log10(annotation['y'])
    layout['annotations'].append(annotation)
    
  return dict(data=fig_data, layout=layout)


def get_timeseries_display(data):
  fig = get_timeseries_figure(data, gradient=False)
  return dcc.Graph(id=f'timeseries-display', figure=fig)


def get_timeseries_gradient_display(data):
  fig = get_timeseries_figure(data, gradient=True)
  return dcc.Graph(id=f'timeseries-gradient-display', figure=fig)  


def get_infections_display(data):
  fig = get_timeseries_figure(data, 'infections')
  return dcc.Graph(id=f'infections-display',
                   figure=fig,
                   hoverData={'points': [{'customdata': '17031'}]})


def get_deaths_display(data):
  fig = get_timeseries_figure(data, 'deaths')
  return dcc.Graph(id=f'deaths-display',
                   figure=fig,
                   hoverData={'points': [{'customdata': '17031'}]})


def get_counties_embedding_figure(data):
  fig_data = [dict(
    x=data.embedding[:, 0],
    y=data.embedding[:, 1],
    text=data.counties_subset_names['county_name'],
    customdata=data.counties_subset_names['FIPS'],
    mode='markers',
    opacity=0.5,
    marker=dict(
      size=5,
      line={'width': 0.5, 'color': 'white'},
      color=data.cluster_colors,
      showscale=False),
    hoverinfo='text'
  )]

  idx = list(data.counties_subset_names['FIPS']).index(data.selected_county)
  fig_data += [dict(
    x=data.embedding[idx: idx + 1, 0],
    y=data.embedding[idx: idx + 1, 1],
    text=data.fips_to_county_name[data.selected_county],
    customdata=data.counties_subset_names['FIPS'],
    mode='markers',
    opacity=0.5,
    marker=dict(
      size=20,
      line={'width': 0.5, 'color': 'white'},
      color=data.cluster_colors[idx],
      showscale=False),
    hoverinfo='text')]

  layout = dict(
    title='United States Counties Embedding',
    height=700,
    hovermode='closest',
    showlegend=False,
    xaxis=dict(visible=False),
    yaxis=dict(visible=False)
  )

  return dict(data=fig_data, layout=layout)


def get_counties_embedding_display(data):
  return dcc.Graph(id='counties-embedding-display',
                   hoverData={'points': [{'text': 'Cook County, IL'}]},
                   figure=get_counties_embedding_figure(data))


def get_counties_clustering_figure(data):
  fig = px.choropleth(
    data.clustering_df[data.clustering_df['cluster'] == data.selected_cluster],
    geojson=counties_geojson,
    locations='FIPS',
    color='cluster',
    color_discrete_map=data.cluster_colors_map,
    hover_data=['county_name'],
    scope='usa',
    height=800,
    title=f'Cluster Neighbors for: {data.fips_to_county_name[data.selected_county]}')
  fig.update_layout(coloraxis_showscale=False)
  return fig
  

def get_counties_clustering_display(data):
  fig = get_counties_clustering_figure(data)
  return dcc.Graph(id='counties-clustering-display', figure=fig, config={'scrollZoom': False})
