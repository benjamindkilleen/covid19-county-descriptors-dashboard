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
    title='Infections per {:,d}, {}'.format(data.per_what, data.daily_infections_date.strftime('%B %d, %Y')))
  fig.update_layout(coloraxis_showscale=False)
  
  return dcc.Graph(id='counties-display', figure=fig, config={'scrollZoom': False})


def get_counties_dropdown(data):
  return dcc.Dropdown(
    id='counties-dropdown',
    options=[{'label': row['county_name'], 'value': row['FIPS']} for idx, row in data.county_names.iterrows()],
    value=data.selected_county,
    multi=False,
    placeholder='Select a county...',
    style={})


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


def get_timeseries_figure(data, timeseries_type, mode='Date', threshold=50, intervention='stay at home', scale='Linear'):
  """FIXME! briefly describe function

  :param data: 
  :param timeseries_type: 
  :param mode: Either 'Analysis' or 'Raw'
  :returns: 
  :rtype: 

  """
  
  # get top 10 counties by default

  assert timeseries_type in ['infections', 'deaths']
  timeseries = getattr(data, timeseries_type)  
  timeseries = timeseries.loc[timeseries['FIPS'].isin(set(data.selected_counties))]

  color_palette = sns.color_palette('Set1', n_colors=len(data.selected_counties))
  color_palette = [f'#{int(255*t[0]):02x}{int(255*t[1]):02x}{int(255*t[2]):02x}' for t in color_palette]

  if mode == 'Date':
    start = data.timeseries_start_index
    dates = data.timeseries_dates[start:]
    fig_data = [
      dict(
        x=dates,
        y=row[start + 1:],
        mode='lines',
        text=data.fips_to_county_name.get(row[0], 'NA'),
        hoverinfo='text+x+y',
        line=dict(color=color_palette[i]))
      for i, (idx, row) in enumerate(timeseries.iterrows())]

    layout = dict(
      title=f'Confirmed {string.capwords(timeseries_type)}',
      showlegend=False,
      yaxis={'type': 'log' if scale == 'Log' else 'linear'},
      xaxis={'title': 'Date'},
      hovermode='closest',
      annotations=[])

    # add annotations
    annotations = getattr(data, f'raw_{timeseries_type}_annotations')
    for i, fips in enumerate(timeseries['FIPS']):
      if annotations.get((fips, intervention)) is not None:
        annotation = annotations[fips, intervention].copy()
        annotation['arrowcolor'] = color_palette[i]
        annotation['textfont'] = dict(size=8, color=color_palette[i])
        layout['annotations'].append(annotation)
        
  elif mode == 'Threshold':
    fig_data = [
      dict(
        x=list(range(len(row) - data.infections_start_indices[idx] - 1)),
        y=row[1:][data.infections_start_indices[idx]:] / data.fips_to_population[row[0]] * data.per_what,
        mode='lines',
        text=data.fips_to_county_name.get(row[0], 'NA'),
        hoverinfo='text+x+y',
        line=dict(color=color_palette[i]))
      for i, (idx, row) in enumerate(timeseries.iterrows())]
    
    layout = dict(
      title=f'Confirmed {string.capwords(timeseries_type)} per {data.per_what:,d}',
      showlegend=False,
      xaxis={'title': f'Days since {threshold} Confirmed {string.capwords(timeseries_type)}'},
      yaxis={'type': 'log' if scale == 'Log' else 'linear'},
      hovermode='closest',
      annotations=[])

    # add annotations
    annotations = getattr(data, f'analysis_{timeseries_type}_annotations')
    for i, fips in enumerate(timeseries['FIPS']):
      if annotations.get((fips, intervention)) is not None:
        annotation = annotations[fips, intervention].copy()
        annotation['arrowcolor'] = color_palette[i]
        annotation['textfont'] = dict(size=8, color=color_palette[i])
        layout['annotations'].append(annotation)
    
  return dict(data=fig_data, layout=layout)


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
    title=f'Counties Similar to: {data.fips_to_county_name[data.selected_county]}')
  fig.update_layout(coloraxis_showscale=False)
  return fig
  

def get_counties_clustering_display(data):
  fig = get_counties_clustering_figure(data)
  return dcc.Graph(id='counties-clustering-display', figure=fig, config={'scrollZoom': False})
