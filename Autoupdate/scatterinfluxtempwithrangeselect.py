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
from dash.dependencies import Output, Input

def get_last_temp():
    """Return the last temperature measurement"""
    client = InfluxDBClient(host='localhost', port=8086)
    client.switch_database('indaba_session')
    query = 'select last("Temperature") from "Indaba Session" group by "wanyama01"'

    result = client.query(query)

    result_list = list(result.get_points())
    return result_list[0]['last']

def get_last_humidity():
    """Return the last humidity measurement"""
    client = InfluxDBClient(host='localhost', port=8086)
    client.switch_database('indaba_session')
    query = 'select last("Relative Humidity") from "Indaba Session" group by "wanyama01"'

    result = client.query(query)

    result_list = list(result.get_points())
    return result_list[0]['last']

def get_analysis(determinant):
    """Return the last humidity measurement"""
    client = InfluxDBClient(host='localhost', port=8086)
    client.switch_database('indaba_session')
    if determinant == "MAXHUM" :
        query = 'select max("Relative Humidity") from "Indaba Session" group by "wanyama01"'
        result = client.query(query)
        result_list = list(result.get_points())
        return result_list[0]['max']

    if determinant == "MINHUM" :
        query = 'select min("Relative Humidity") from "Indaba Session" group by "wanyama01"'
        result = client.query(query)
        result_list = list(result.get_points())
        return result_list[0]['min']

    if determinant == "MINTMP" :
        query = 'select Min("Temperature") from "Indaba Session" group by "wanyama01"'
        result = client.query(query)
        result_list = list(result.get_points())
        return result_list[0]['min']

    if determinant == "MAXTMP" :
        query = 'select Max("Temperature") from "Indaba Session" group by "wanyama01"'
        result = client.query(query)
        result_list = list(result.get_points())
        return result_list[0]['max']

def plotdatapoints(range) : 
	client = InfluxDBClient(host='localhost', port=8086)
	client.switch_database('indaba_session')
	result = client.query('select * from "Indaba Session" where time > now() - 100h group by "wanyama01"')#'select last("Temperature") from "Indaba Session"')
	df = list(result.get_points())
	# turn to pandas dataframe
	df = pd.DataFrame(df)
	# make time a datetime object
	df['time'] = df['time'].apply(pd.to_datetime)
	return df

#df = plottempdatapoints()

app = dash.Dash()

app.layout = html.Div([

	dcc.Graph(
		id = 'scatter1',
		figure=go.Figure(layout=go.Layout(
									)
                            ),),
	dcc.RadioItems(
        id='environproperty',
        options=[{'label': 'Temperature', 'value': 'TMP'},{'label' : 'Humidity' , 'value' : 'HUM'}],
        value='TMP'
    ),
	dcc.Interval(
            id = 'interval-component',
            interval = 1 * 1000,
            n_intervals = 0
            )
	])

@app.callback(Output('scatter1', 'figure'),
    [Input('interval-component', 'n_intervals'),
    Input('environproperty', 'value')])
def format_current_temp(interval,param):
	df = plotdatapoints('100h')
	if param == 'TMP' :
		
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
	if param == 'HUM' : 
		trace = go.Scatter(
					x = list(df['time']),
					y = list(df['Relative Humidity']),
					mode = "markers"

					),
		layout=go.Layout(
					title = 'Scatter Plot of Humidity points',
					xaxis = {'title' :"Time values"},
					yaxis = {'title' :"Humidity values"}
					)

		return go.Figure(data=trace, layout=layout)


if __name__ == '__main__' : 
	app.run_server(port = 8050)