# 1. Import Dash
import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np
import plotly.express as px

## --- DAHSBOARD ELEMENTS ---

### DATASET
df=pd.read_csv('uk_bank-customer.csv', parse_dates=['Date Joined'])
df['Name'] = df['Name'] + ' ' + df['Surname']
df['month'] = df['Date Joined'].dt.month_name()
cats = [ 'January', 'February', 'March', 'April', 'May', 'June', 'July','August','September','October','November','December']
cat_type = CategoricalDtype(categories=cats, ordered=True)
df['month'] = df['month'].astype(cat_type)

navbar = dbc.NavbarSimple(
	children=[
		dbc.NavItem(dbc.NavLink("Home", href="#")),
	],
	brand="Customer Identity",
	brand_href="#",
	color="#4B56D2",
	dark=True,
	sticky='top'
)

##### CARDS

txn_number = [
	dbc.CardHeader('Number of Transaction', style={'background-color': '#4B56D2', 'color':'white'}),
	dbc.CardBody(
		[
			html.H1(df.shape[0])
		]
	)
]

total_balance = [
	dbc.CardHeader('Total Balance (£)', style={'background-color': '#4B56D2', 'color':'white'}),
	dbc.CardBody(
		[
			html.H1('159.6 M')
		]
	)
]

median = [
	dbc.CardHeader('Median'),
	dbc.CardBody(
		[
			html.H1(df['Balance'].median())
		]
	)
]

max = [
	dbc.CardHeader('Max Balance'),
	dbc.CardBody(
		[
			html.H1(df['Balance'].max())
		]
	)
]

##### GRAPH

# 2. Create a Dash app instance
app = dash.Dash(
	name='Customer Identity',
	external_stylesheets=[dbc.themes.LUX]
)
app.title = 'Customer Identity 2015 Dashboard'

## --- DASHBOARD LAYOUT

app.layout = html.Div(children=[
	navbar,
	html.Br(),

	# Main page
	html.Div(
		[
			# ----- ROW 1
			dbc.Row(
				[
					# --- COLUMN 1
					dbc.Col(
						[
						html.Br(),
						dbc.Card(
							txn_number, color='white', 
						
						),
						html.Br(),
						dbc.Card(
							total_balance, color='white', 
						),
						html.Br(),
						dbc.Card(
								[
									dbc.CardHeader('Select Filter', style={'background-color': '#4B56D2', 'color':'white'}),
									dbc.CardBody(
										dcc.Dropdown(
											id='select_filter',
											options= np.array(['Gender','Job Classification']),
											value='Gender'
										),
									),
								]
							),
						],
						width=3,
					),

					# --- COLUMN 2
					dbc.Col(
						[
							dcc.Graph(
								id='bar_plot1'
							)
						],
						width=4
					),

					# --- COLUMN 3
					dbc.Col(
						[		dcc.Graph(
								id='box_plot1'
								     )
						],
						width=5
					),
					
				]
			),

			html.Hr(),

			# ----- ROW 2
			dbc.Row(
				[
					### --- COLUMN 1
					dbc.Col(
						[
							dcc.Graph(
								id='line_plot1'
							)
						],
						width=7
					),

					### --- COLUMN 2
					dbc.Col(
						[
							dcc.Graph(
								id='tree_plot1'
								#figure=treemap
							)
						],
						width=5
					),
				]
			),

		],
		style={
			'padding-right':'30px',
			'padding-left':'30px' 
		}
	)
	

],
style={
	'backgroundColor':'white',
	},
)

## ---- PLOT 1: Boxplot
@app.callback(
	Output(component_id='box_plot1', component_property='figure'),
	Input(component_id='select_filter', component_property='value'),
)

def update_plot1(filter):
	box_plot = px.box(df,
       	    		  x='Balance',
           	          y= filter,
					  title = f'{filter} Distribution',
					  labels = {'Gender':'', 'Balance':'Balance (£)'})
	
	return box_plot

@app.callback(
	Output(component_id='bar_plot1', component_property='figure'),
	Input(component_id='select_filter', component_property='value'),
)

def update_plot2(filter):
	df_temp = df.groupby(['Region',filter]).sum()['Balance'].reset_index()
	df_default = df.groupby('Region').sum()['Balance'].reset_index()

	if filter == 'Gender':
		barplot = px.bar(
					df.groupby(['Region','Gender']).sum()['Balance'].reset_index(),
					x = 'Region',
					y = 'Balance',
					color = 'Gender',
					title = 'Balance per Region',
					labels = {
						'index': '',
						'Customer ID': 'Total Balance (£)',
						'variable': '',
						'Region':'Region',
						'Balance':'Balance (£)'},
					#color_discrete_sequence=['teal'],
					template='plotly_white')
	elif filter == 'Job Classification':
		barplot = px.bar(
					df.groupby(['Region','Job Classification']).sum()['Balance'].reset_index(),
					x = 'Region',
					y = 'Balance',
					color = 'Job Classification',
					title = 'Balance per Region',
					labels = {
						'index': '',
						'Customer ID': 'Total Balance (£)',
						'variable': '',
						'Region':'Region',
						'Balance':'Balance (£)'},
					#color_discrete_sequence=['teal'],
					template='plotly_white')

	elif filter == 'None':
		barplot = px.bar(
					df_default,
					x = 'Region',
					y = 'Balance',
					title = 'Balance per Region',
					labels = {
						'index': '',
						'Customer ID': 'Total Balance (£)',
						'variable': '',
						'Region':'Region',
						'Balance':'Balance (£)'},
					#color_discrete_sequence=['teal'],
					template='plotly_white')
	else:
		barplot = px.bar(df.groupby('Region').sum()['Balance'].reset_index(), x = 'Region',
					y = 'Balance', title = 'Balance per Region', labels = {
						'index': '',
						'Customer ID': 'Total Balance',
						'variable': '',
						'Region':'Region',
						'Balance':'Balance (£)'},
					#color_discrete_sequence=['teal'],
					template='plotly_white')

	return barplot 

@app.callback(
	Output(component_id='line_plot1', component_property='figure'),
	Input(component_id='select_filter', component_property='value'),
)

def update_plot3(filter):
	#df['month'] = df['Date Joined'].dt.to_period('M')
	#df['month'] = df['month'].dt.to_timestamp()
	df_agg_balance = df.groupby('month').agg({'Balance':'sum'})
	df_temp1 = df.groupby(['month','Job Classification']).sum()['Balance'].reset_index()
	df_temp2 = df.groupby(['month','Gender']).sum()['Balance'].reset_index()
	
	if filter == 'Gender':
		lineplot = px.line(
                df_temp2,
                x = 'month',
                y = 'Balance',
                color = 'Gender',
                template='plotly_white',
                title = 'Balance Each Month',
                labels = {
                      'month': 'Month',
                      'value': 'Total Balance',
                      'variable': '',
					  'Balance':'Balance (£)'}
                   )
	elif filter == 'Job Classification':
		lineplot = px.line(
                df_temp1,
                x = 'month',
                y = 'Balance',
                color = 'Job Classification',
                template='plotly_white',
                title = 'Balance Each Month',
                labels = {
                      'month': 'Month',
                      'value': 'Total Balance',
                      'variable': '',
					  'Balance':'Balance (£)'}
                   )
	else:
		lineplot = px.line(
                df_agg_balance.reset_index(),
                x = 'month',
                y = 'Balance',
                template='plotly_white',
                title = 'Balance Each Month',
                labels = {
                      'month': 'Month',
                      'value': 'Total Balance',
                      'variable': '',
					  'Balance':'Balance (£)'}
                   )
	return lineplot

@app.callback(
	Output(component_id='tree_plot1', component_property='figure'),
	Input(component_id='select_filter', component_property='value'),
)

def update_plot4(filter):
	temp = df.groupby(['Gender','Name']).sum()['Balance'].reset_index().sort_values(['Gender','Balance'], ascending=[True,False])
	temp_result = temp.groupby('Gender').head()
	temp_2 = df.groupby(['Job Classification','Name']).sum()['Balance'].reset_index().sort_values(['Job Classification','Balance'], ascending=[True,False])
	temp_result_2 = temp_2.groupby('Job Classification').head()

	if filter == 'Job Classification':
		treeplot = px.treemap(temp_result_2, path=[px.Constant("Grand Total"),'Job Classification','Name'], 
           values='Balance', template='plotly_white', title = 'Top 5 Clients by Job Classification', color_continuous_scale= px.colors.sequential.Cividis_r)
	
	elif filter == 'Gender':
		treeplot = px.treemap(temp_result, path=[px.Constant("Grand Total"),'Gender','Name'], 
           values='Balance', template='plotly_white', title = 'Top 5 Clients by Gender', color_continuous_scale= px.colors.sequential.Cividis_r)
	
	else:
		treeplot = px.treemap(df.groupby('Name').sum().sort_values('Balance', ascending=False).reset_index().head(), path=[px.Constant("Grand Total"),'Name'], 
           values='Balance', template='plotly_white', title = 'Top 5 Clients', color_continuous_scale= px.colors.sequential.Cividis_r)
	
	return treeplot

# 3. Start the Dash server
if __name__ == "__main__":
	app.run_server()