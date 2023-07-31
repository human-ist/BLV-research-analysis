from typing import List
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio

from .analysis.temporal_plot_data import TemporalPlotData

pio.templates.default = "simple_white" # plotly_white
#pio.kaleido.scope.default_format = "svg"


def multiple_line_plot(multiplot_title: str,
                       temp_plots: List[TemporalPlotData],
                       figname:str,
                       height:int=400,
                       width:int=700):
  """
  Create multiple lineplots in one plot.
  - https://plotly.com/python/subplots/
  - https://plotly.com/python-api-reference/generated/plotly.subplots.make_subplots.html; 
  - https://plotly.com/python/hover-text-and-formatting/
  - https://community.plotly.com/t/image-export-how-to-set-dpi-alternatively-how-to-scale-down-using-width-and-height/49536
  """
  subplot_titles = []
  for i in range(len(temp_plots)):
    subplot_titles.append(f"<b>{temp_plots[i].get_title()}</b>")

  fig = make_subplots(rows=len(temp_plots),
                      cols=1,
                      subplot_titles=subplot_titles,
                      x_title='Years')
  # shared_xaxes='all', shared_yaxes='all'

  row_index = 1
  for temp_plot in temp_plots:
    fig.add_trace(go.Scatter(x=temp_plot.get_x(), y=temp_plot.get_y(), showlegend=False),
                    row=row_index, col=1)
    row_index += 1

  fig.update_layout(height=height, width=width, title_text=multiplot_title, font=dict(size=16))

  #fig.write_image(f'{figname}.eps', engine="kaleido")
  fig.write_image(f'{figname}.png', engine="kaleido", scale=3)
