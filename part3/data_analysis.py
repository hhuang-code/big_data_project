import random
import pandas as pd
import numpy as np
from collections import namedtuple
import matplotlib.pyplot as plt
from matplotlib.dates import DAILY, DateFormatter, rrulewrapper, RRuleLocator, datestr2num

import pdb

# Define needed data structure
Measure = namedtuple('Measure', 'C1 C2, C3, C4, C5, C6, C7, C8, H1, stringency')
Tested = namedtuple('Tested', 'cumulative daily')
Confirmed = namedtuple('Confirmed', 'cumulative daily')
Combined = namedtuple('Combined', 'measure confirmed tested')

# Load the cleaned and integrated data
import pickle

filename = 'cleaned_integrated_data.pkl'

with open(filename, 'rb') as fp:
    loaded = pickle.load(fp)

print('Total number of samples: {}'.format(len(loaded)))

key = random.choice(list(loaded.keys()))
print('A random sample in the integrated dataset:')
print('key: ', key)
print('value: ', loaded[key])

def search_by_country(country):
    res_by_country = dict()
    for key, value in loaded.items():
        if country in key:
            res_by_country[key] = value

    return res_by_country

from collections import OrderedDict

def search_by_date(date, dataset):
    res_by_date = dict()
    for key, value in dataset.items():
        if date in key:
            res_by_date[key] = value

    return res_by_date

import io
import requests

# Oxford Covid-19 Government Response Tracker (OxCGRT)
oxcgrt_url = 'https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv'
oxcgrt_data = requests.get(oxcgrt_url).content
oxcgrt_data = pd.read_csv(io.StringIO(oxcgrt_data.decode('utf-8')))

a2m = {'C1': 'C1_School closing', 'C2': 'C2_Workplace closing', 'C3': 'C3_Cancel public events', 'C4': 'C4_Restrictions on gatherings',
       'C5': 'C5_Close public transport', 'C6': 'C6_Stay at home requirements', 'C7': 'C7_Restrictions on internal movement',
       'C8': 'C8_International travel controls', 'H1': 'H1_Public information campaigns'}
m2a = {v: k for k, v in a2m.items()}

# select C1 to C8, H1 and Stringency Index
dc_measure_data = dict()
Measure = namedtuple('Measure', 'C1 C2, C3, C4, C5, C6, C7, C8, H1, stringency')
for index, row in oxcgrt_data.iterrows():
    value = []
    for abbr, measure in a2m.items():
        if np.isnan(row[measure]):
            value.append(None)
        else:
            value.append(row[measure])
    if np.isnan(row['StringencyIndexForDisplay']):
        value.append(None)
    else:
        value.append(row['StringencyIndexForDisplay'])

    key = (row['Date'], row['CountryName'])
    value = Measure(*value)
    dc_measure_data[key] = value

date = '20200501'
res_by_date = search_by_date(int(date), dc_measure_data)
pdb.set_trace()
# extract stringency and country to form a compact dataset
country2stringency = dict()
for key, value in res_by_date.items():
    country2stringency[key[1]] = value.measure.stringency

def sort_by_date(samples):
    sorted_samples = OrderedDict(sorted(samples.items(), key=lambda t: t[0][0]))

    return sorted_samples

res_by_country = search_by_country('France')
sorted_samples = sort_by_date(res_by_country)

dates = [key[0].strftime('%Y-%m-%d') for key in sorted_samples.keys()]
dates = datestr2num(dates)

cum_confirmed = [value.confirmed.cumulative for value in sorted_samples.values()]
cum_tested = [value.tested.cumulative for value in sorted_samples.values()]
confirmed_over_tested = [c / t for c, t in zip(cum_confirmed, cum_tested)]

stringency = [value.measure.stringency for value in sorted_samples.values()]

rule = rrulewrapper(DAILY, interval=10)
loc = RRuleLocator(rule)
formatter = DateFormatter('%Y-%m-%d')

fig, ax1 = plt.subplots()
ax1.plot_date(dates, confirmed_over_tested, 'r-')
ax1.set_ylabel('ratio')

ax2 = ax1.twinx()
ax2.plot_date(dates, stringency, 'b-')
ax2.set_ylabel('stringency')

ax1.xaxis.set_major_locator(loc)
ax1.xaxis.set_major_formatter(formatter)
ax1.xaxis.set_tick_params(rotation=30, labelsize=10)

plt.show()

pdb.set_trace()
print('done')