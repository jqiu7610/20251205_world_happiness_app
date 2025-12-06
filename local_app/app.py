# app
from flask import Flask, render_template, request, Response
import json
import pandas as pd
import boto3
import os
import numpy as np
from io import StringIO
import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
	from passwords import *
	bool_debug = True
except:
	bool_debug = False
	AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
	AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# instantiate app
application = Flask(__name__)

# make a global variable
dict_contents = {}

# show home page
@application.route('/')
def show_home_page():
	# make global
	global dict_contents

	# get date info
	today = pd.Timestamp.now()
	date_file = today.strftime('%Y%m%d')
	date_format = today.strftime('%Y-%m-%d')

	# assign
	dict_contents['today'] = today
	dict_contents['date_file'] = date_file
	dict_contents['date_format'] = date_format

	# #################################################################################
	# # df_world_happiness_cleaned
	# #################################################################################
	# read in file
	str_key = f'static/shared/df_manual_combined_cleaned.csv'
	df = pd.read_csv(str_key)
	# assign
	print('Assigning to dict_contents...')
	dict_contents['df_happiness_cleaned'] = df


	# create plot of mean happiness
	#----------------------------------------------------------------------------------
	print('Making PlotlyJSONEncoder 1')
	# group and get mean
	df_grouped = df.groupby(by='year').agg({'happiness_score_new':'mean'}).sort_values(by='year', ascending=True).reset_index()

	# plot it
	fig = px.line(
	    df_grouped,
	    x='year',
	    y='happiness_score_new',
	    title='Mean Happiness Score Over Time',
	)

	# remove gridlines
	fig.update_xaxes(showgrid=False)
	fig.update_yaxes(showgrid=False)
	# make json
	graphJSON_mean_happiness = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	# create plot of median happiness
	#----------------------------------------------------------------------------------
	print('Making PlotlyJSONEncoder 2')
	# group and get mean
	df_grouped = df.groupby(by='year').agg({'happiness_score_new':'median'}).sort_values(by='year', ascending=True).reset_index()

	# plot it
	fig = px.line(
	    df_grouped,
	    x='year',
	    y='happiness_score_new',
	    title='Median Happiness Score Over Time',
	)

	# remove gridlines
	fig.update_xaxes(showgrid=False)
	fig.update_yaxes(showgrid=False)

	# make json
	graphJSON_median_happiness = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	# create plot of regional happiness
	#----------------------------------------------------------------------------------
	# mean
	df_grouped = df.groupby(by=['regional_indicator', 'year']).agg({'happiness_score_new':'mean'}).sort_values(by='year', ascending=True).reset_index()

	# plot
	fig = px.line(
	    df_grouped,
	    x='year',
	    y='happiness_score_new',
	    color='regional_indicator',
	    title='Mean Happiness Scores Over Time by Region',
	    width=1000,
	    height=500 
	)

	# remove grid
	fig.update_xaxes(showgrid=False)
	fig.update_yaxes(showgrid=False)

	# make json
	graphJSON_mean_region = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	#----------------------------------------------------------------------------------
	# median
	df_grouped = df.groupby(by=['regional_indicator', 'year']).agg({'happiness_score_new':'median'}).sort_values(by='year', ascending=True).reset_index()

	# plot
	fig = px.line(
	    df_grouped,
	    x='year',
	    y='happiness_score_new',
	    color='regional_indicator',
	    title='Median Happiness Scores Over Time by Region',
	    width=1000,
	    height=500 
	)

	# remove grid
	fig.update_xaxes(showgrid=False)
	fig.update_yaxes(showgrid=False)

	# make json
	graphJSON_median_region = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	#----------------------------------------------------------------------------------
	# correlation matrix
	# select numeric columns related to happiness
	numeric_cols = [
	    'happiness_score_new',
	    'gdp_per_capita',
	    'social_support',
	    'healthy_life_expectancy',
	    'freedom_to_make_life_choices',
	    'generosity',
	    'perceptions_of_corruption'
	]

	# compute correlation matrix
	corr = df[numeric_cols].corr()

	# plotly heatmap
	fig = px.imshow(
	    corr,
	    text_auto=True,
	    color_continuous_scale='RdBu_r',
	    zmin=-1,
	    zmax=1,
	    aspect='auto'
	)

	fig.update_layout(
	    title='Correlation Matrix of Happiness and Key Socioeconomic Variables',
	    width=900,
	    height=600
	)

	# make json
	graphJSON_corr = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	#----------------------------------------------------------------------------------
	# GDP vs happiness
	fig = px.scatter(
	    df,
	    x='gdp_per_capita',
	    y='happiness_score_new',
	    opacity=0.4,
	    title='GDP per capita vs Happiness (Global)',
	)

	fig.update_layout(
	    xaxis_title='GDP per capita',
	    yaxis_title='Happiness Score',
	)

	fig.update_xaxes(showgrid=True, gridwidth=0.5)
	fig.update_yaxes(showgrid=True, gridwidth=0.5)

	# make json
	graphJSON_gdp_v_target = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	#----------------------------------------------------------------------------------
	# social vs happiness	
	fig = px.scatter(
	    df,
	    x='social_support',
	    y='happiness_score_new',
	    opacity=0.4,
	    title='Social Support vs Happiness (Global)',
	)

	fig.update_layout(
	    xaxis_title='Social Support',
	    yaxis_title='Happiness Score',
	)

	fig.update_xaxes(showgrid=True, gridwidth=0.5)
	fig.update_yaxes(showgrid=True, gridwidth=0.5)

	# make json
	graphJSON_social_v_target = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	#----------------------------------------------------------------------------------
	# life vs happiness	
	fig = px.scatter(
	    df,
	    x='healthy_life_expectancy',
	    y='happiness_score_new',
	    opacity=0.4,
	    title='Healthy Life Expectancy vs Happiness (Global)'
	)

	fig.update_layout(
	    xaxis_title='Healthy Life Expectancy',
	    yaxis_title='Happiness Score'
	)

	fig.update_xaxes(showgrid=True, gridwidth=0.5)
	fig.update_yaxes(showgrid=True, gridwidth=0.5)


	# make json
	graphJSON_life_v_target = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	#----------------------------------------------------------------------------------
	# freedom vs happiness
	fig = px.scatter(
	    df,
	    x='freedom_to_make_life_choices',
	    y='happiness_score_new',
	    opacity=0.4,
	    title='Freedom vs Happiness (Global)',
	)

	fig.update_layout(
	    xaxis_title='Freedom',
	    yaxis_title='Happiness Score',
	    xaxis=dict(showgrid=True, gridwidth=0.5),
	    yaxis=dict(showgrid=True, gridwidth=0.5),
	)	

	# make json
	graphJSON_freedom_v_target = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

	#----------------------------------------------------------------------------------
	# lebanon
	# subset Lebanon sort by year
	lebanon_df = df[df['country'] == 'lebanon'].sort_values('year')

	# variables
	timeseries_variables = [
	    'happiness_score_new',
	    'gdp_per_capita',
	    'social_support',
	    'healthy_life_expectancy',
	    'freedom_to_make_life_choices',
	    'generosity',
	    'perceptions_of_corruption'
	]

	# 3 rows x 3 cols
	fig = make_subplots(
	    rows=3, cols=3,
	    subplot_titles=[f'{col} over Time' for col in timeseries_variables]
	)

	# loop through variables and add traces
	for i, col in enumerate(timeseries_variables):
	    row = i // 3 + 1
	    col_pos = i % 3 + 1
	    fig.add_trace(
	        go.Scatter(
	            x=lebanon_df['year'],
	            y=lebanon_df[col],
	            mode='lines+markers',
	            line=dict(color='purple'),
	            name=col
	        ),
	        row=row,
	        col=col_pos
	    )

	# remove empty subplot (bottom-right) if less than 9 variables
	fig.update_layout(height=900, width=1200, showlegend=False)

	# x and y axes labels
	for i in range(1, len(timeseries_variables)+1):
	    fig['layout'][f'xaxis{i}'].title.text = 'Year'
	    fig['layout'][f'yaxis{i}'].title.text = timeseries_variables[i-1]

	# make json
	graphJSON_lebanon = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)	  


	#----------------------------------------------------------------------------------
	# ivory coast
	# subset ivory sort by year
	ivory_df = df[df['country'] == 'ivory_coast'].sort_values('year')

	# Variables to plot
	timeseries_variables = [
	    'happiness_score_new',
	    'gdp_per_capita',
	    'social_support',
	    'healthy_life_expectancy',
	    'freedom_to_make_life_choices',
	    'generosity',
	    'perceptions_of_corruption'
	]

	# 3 rows x 3 cols
	fig = make_subplots(
	    rows=3, cols=3,
	    subplot_titles=[f'{col} over Time' for col in timeseries_variables]
	)

	# loop through variables and add traces
	for i, col in enumerate(timeseries_variables):
	    row = i // 3 + 1
	    col_pos = i % 3 + 1
	    fig.add_trace(
	        go.Scatter(
	            x=ivory_df['year'],
	            y=ivory_df[col],
	            mode='lines+markers',
	            line=dict(color='purple'),
	            name=col
	        ),
	        row=row,
	        col=col_pos
	    )

	# layout
	fig.update_layout(
	    height=900,
	    width=1200,
	    showlegend=False
	)

	# x and y axes labels
	for i in range(1, len(timeseries_variables)+1):
	    fig['layout'][f'xaxis{i}'].title.text = 'Year'
	    fig['layout'][f'yaxis{i}'].title.text = timeseries_variables[i-1] 

	# make json
	graphJSON_ivory = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)	 	    
	#################################################################################
	# SHOW HOME PAGE
	#################################################################################
	return render_template(
		'index.html',
		today=today,
		date_format=date_format,		
		# df_happiness_cleaned=df_happiness_cleaned,
		graphJSON_mean_happiness=graphJSON_mean_happiness,
		graphJSON_median_happiness=graphJSON_median_happiness,
		graphJSON_mean_region=graphJSON_mean_region,
		graphJSON_median_region=graphJSON_median_region,
		graphJSON_corr=graphJSON_corr,
		graphJSON_gdp_v_target=graphJSON_gdp_v_target,
		graphJSON_social_v_target=graphJSON_social_v_target,
		graphJSON_freedom_v_target=graphJSON_freedom_v_target,
		graphJSON_life_v_target=graphJSON_life_v_target,
		graphJSON_lebanon=graphJSON_lebanon,
		graphJSON_ivory=graphJSON_ivory,
	)

# run app		
if __name__ == '__main__':
	application.run(host="0.0.0.0", debug=True) # True for local testing