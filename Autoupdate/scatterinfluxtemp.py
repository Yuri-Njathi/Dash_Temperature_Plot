import dash
import dash_core_components as dcc 
import dash_html_components as html 
import pandas as pd
from influxdb import InfluxDBClient
from pandas import DataFrame, Series
from pandas.io.json import json_normalize
from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import plotly.graph_objs as go 


def plotdatapoints() : 
	client = InfluxDBClient(host='localhost', port=8086)
	client.switch_database('indaba_session')
	result = client.query('select * from "Indaba Session" where time > now() - 100h group by "wanyama01"')#'select last("Temperature") from "Indaba Session"')
	df = list(result.get_points())
	# turn to pandas dataframe
	df = pd.DataFrame(df)
	# make time a datetime object
	df['time'] = df['time'].apply(pd.to_datetime)
	return df


#df = plotdatapoints()

app = dash.Dash()

app.layout = html.Div([

	dcc.Graph(
		id = 'scatter1',
		figure=go.Figure(layout=go.Layout(
									)
                            ),),
	dcc.Interval(
            id = 'interval-component',
            interval = 1 * 1000,
            n_intervals = 0
            )
	])

@app.callback(dash.dependencies.Output('scatter1', 'figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals')])
def format_current_temp(interval):
	df = plotdatapoints()
	trace = go.Scatter(
					x = list(df['time']),
					y = list(df['Temperature']),
					mode = "markers"

					),
	layout=go.Layout(
					title = 'Scatter Plot of Temperature points',
					xaxis = {'title' :"Time values"},
					yaxis = {'title' :"Temperature values"}
					)

	return go.Figure(data=trace, layout=layout)



if __name__ == '__main__' : 
	app.run_server(port = 8050)