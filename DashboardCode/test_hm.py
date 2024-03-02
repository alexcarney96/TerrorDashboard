from dash import Dash, dcc, html, Input, Output
import dash
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css")
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG, dbc_css])
template = "cyborg"
load_figure_template(template)



df = px.data.medals_wide(indexed=True)
fig = px.imshow(df)
fig.show()
app = Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

app.run_server(debug=True, host='0.0.0.0', port=8050)
