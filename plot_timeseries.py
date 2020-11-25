import argparse
import numpy as np
import string
import seaborn as sns
from plotly import graph_objects as go

from utils.data import DashboardData
from utils import elements


def main(*, counties):
  data = DashboardData()
  data.selected_counties = counties
  d = elements.get_timeseries_figure(
    data, mode='Date', threshold=1, daily=True, interventions=[
      'stay at home', 'restaurant dine-in',
      'stay at home rollback', 'restaurant dine-in rollback'])
  fig_data = d['data']
  layout = d['layout']

  fig = go.Figure(fig_data)
  fig.update_layout(layout)
  counties_string = '-'.join(counties)
  fig.write_image(f'infections_{counties_string}.pdf', height=500, width=800, scale=5)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('--counties', nargs='+', default=['36061'], type=str, help='counties to include, by fips code')
  args = parser.parse_args()
  
  main(**args.__dict__)

