import dash
from dash import Dash, dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

#setting background colour & fonts
bg_col = '#faf1e0'
font_col = '#d96741'
title_font = '#ed724a'
text_col = '#9c179e'
title_style = 'verdana'

# Load the data and wrangle
weather = pd.read_csv("../data/weather.csv", 
                      usecols = ["month", "state", "city", "high_or_low", "temp_c", "temp_f", "date"])
weather = weather.dropna()
weather = weather[weather["high_or_low"]=="high"]
weather['date'] = pd.to_datetime(weather['date'])
weather = weather[(weather["date"] > '2021-02-01') & (weather["date"] < '2022-02-01')] 
weather["date_full"] = weather["date"].dt.strftime("%b %d, %Y")
months = ['January', 'February', 'March', 'April', 'May',
          'June', 'July', 'August', 'September', 'October',
          'November', 'December']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE])

# define layout of the app
app.layout = dbc.Container([
   # ROW 1
   dbc.Row([html.H2('TempeRATE: Helping you Chase the Sun!', 
                style = {'font-family': title_style, 
                        'color': title_font,
                        'textAlign':'center',
                        "font-weight": "bold",
                        'marginTop': 15}),                    
    # COLUMN 1
    dbc.Col([
        html.H5("When do you want to go?", 
                style = {'font-family': title_style, 
                          'textAlign':'left',
                          "font-weight": "bold",
                          'marginTop': 30}),
        html.Div([
        dcc.Slider(0, 12, 12, value=1, 
                   id="month_slider",
               marks=
          {(i):{'label':str(months[i]),
                'style':{'color':'black',
                         'writing-mode': 'vertical-rl',
                         'text-orientation': 'use-glyph-orientation'}} for i in range(0, 12)})
        ],
                style ={'color': 'black', 
                        'fontSize': 70,
                        'marginTop': 10,
                        'marginBottom': 20}),
        html.Br(),
        html.H5("Where do you want to go?", 
                style = {'font-family': title_style, 
                          'textAlign':'left',
                          "font-weight": "bold",
                          'marginTop': 10}),
        html.Label("(Check the heatmap for state with the highest average temperature)", 
                    style = {'font-family': title_style, 
                          'textAlign':'left',
                          'fontSize': 15,
                          'marginBottom': 20}), 
        dcc.Dropdown(
            id="state-dropdown",
            options=[{"label": state, "value": state} for state in weather["state"].unique()],
            value=weather["state"].iloc[0]),
            ]),
   # COLUMN TWO
    dbc.Col([
    html.Br(),
    html.Label("Heatmap of Monthly Average High Temperature", 
               style = {"font-weight": "bold"}),
    html.Div(dcc.Graph(id="heatmap"))
    ])
   ]),
    # ROW 2
    dbc.Row([dbc.Col([
    html.Label("Observed Temperatures by City", 
               style = {"font-weight": "bold"}),    
    dcc.Graph(id="violin", style={'display': 'inline-block'}, 
              )]),
     ]),
],
     className="container",
    style={'backgroundColor': bg_col})

# Define the callback to update the heatmap
@app.callback(Output('heatmap', 'figure'),
              Input('month_slider', 'value'))

def update_map(selected_month):
    heatmap_data = weather.groupby(['state', 'month'])[['temp_c', 'temp_f']].mean().reset_index()
    heatmap_data = heatmap_data[(heatmap_data.month == selected_month + 1)]

    fig = px.choropleth(
        heatmap_data,
        locations='state', 
        locationmode="USA-states", 
        color='temp_c',
        color_continuous_scale=px.colors.sequential.Plasma,
        scope="usa", 
        hover_data=['state','temp_c','temp_f'],
        width=600, height=300,
        )

    fig.update_layout(geo=dict(bgcolor='rgba(0,0,0,0)', 
                           lakecolor=bg_col,
                           landcolor='rgba(51,17,0,0.2)',
                           subunitcolor='grey'),
                    height=300, 
                    paper_bgcolor=bg_col,
                    margin={"r":0,"t":20,"l":0,"b":0}),
    
    fig.update_traces(
    hovertemplate="<br>".join([
    "State: %{customdata[0]}",
    "Mean Temperature: %{customdata[1]:.2f}°C or %{customdata[2]:.2f}°F<extra></extra>",
    ]))

    fig.layout.coloraxis.colorbar.title = 'Temperature (°C)'

    
    return fig

@app.callback(Output('violin', 'figure'), 
              [Input('month_slider', 'value'),
               Input("state-dropdown", "value")])

def update_figure(selected_month, selected_state):
  weather_filtered = weather[weather.month == selected_month + 1]
  weather_filtered = weather_filtered[weather_filtered.state == selected_state]

  fig = px.strip(weather_filtered, 
                 x='city', 
                 y='temp_c', 
                 custom_data=['date_full', 'temp_f', 'city'],
                 width=1000, height=400)
  
  fig.update_traces(hovertemplate="<br>".join([
    "Observed Date: %{customdata[0]}",
    "Observed Temperature: %{y}°C or %{customdata[1]}°F",
    "City: %{x}<extra></extra>",
    ]),
    marker=dict(color= title_font))

  fig.update_layout(showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin={"r":0,"t":0,"l":0,"b":0},
                    xaxis_title=None,
                    yaxis_title="Observed Temp. (°C)")
  
  fig.update_yaxes(showspikes=True)

  return fig

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)

server = app.server

