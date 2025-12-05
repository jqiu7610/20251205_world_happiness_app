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

	# show
	fig.show()
	# make json
	graphJSON_median_happiness = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

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

	)

# run app		
if __name__ == '__main__':
	application.run(host="0.0.0.0", debug=True) # True for local testing