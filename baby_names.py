import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import seaborn as sns
import csv
from zipfile import ZipFile

# url = "https://www.ssa.gov/oact/babynames/names.zip"
#
# with requests.get(url) as response:
#
#     with open("names.zip", "wb") as temp_file:
#         temp_file.write(response.content)
#
# file_name = "names.zip"
#
# # opening the zip file in READ mode
# with ZipFile(file_name, 'r') as zip:
#     # printing all the contents of the zip file
#     zip.printdir()
#
#     # extracting all the files
#     print('Extracting all the files now...')
#     zip.extractall()

#     print('Done!')
#
# # for i in file_name.namelist():
# #     print(i)
#
# names1880 = pd.read_csv('yob1880.txt', names=['name', 'sex', 'births'])
# print(names1880)
# ZipFile.
import os

path = 'C:\\Users\\Aravind\\Desktop\\aws\\baby'
temp=[]
files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.txt' in file:
            files.append(os.path.join(r, file))

for f in files:
    temp.append(f)
print(temp)


years = range(1880, 2010)
pieces = []
columns = ['name', 'sex', 'births']
i = 0
for year in years:
  file = temp[i]
  frame = pd.read_csv(file, names=columns)
  frame['year'] = year
  pieces.append(frame)
  i = i + 1



names = pd.concat(pieces, ignore_index=True)
print(names)

total_births = names.pivot_table('births', index='year', columns='sex', aggfunc=sum)
print(total_births.head())
total_births.plot(title='Total births by sex and year')
plt.show()
#### Creating ratio coloum
def add_prop(group):
	# Integer division floors
	births = group.births.astype(float)
	group['prop'] = births / births.sum()
	return group

names = names.groupby(['year', 'sex']).apply(add_prop)
print(names)

### analysing on top1000
def get_top1000(group):
	return group.sort_values(by='births', ascending=False)[:1000]

grouped = names.groupby(['year', 'sex'])
top1000 = grouped.apply(get_top1000)

pieces = []
for year, group in names.groupby(['year', 'sex']):
	pieces.append(group.sort_values(by='births', ascending=False)[:1000])
top1000 = pd.concat(pieces, ignore_index=True)

print(top1000)

 ####Analyzing Naming Trends
#

boys = top1000[top1000.sex == 'M']
girls = top1000[top1000.sex == 'F']

total_births = top1000.pivot_table('births', index='year', columns='name', aggfunc=sum)
print(total_births)

subset = total_births[['John', 'Harry', 'Mary', 'Marilyn']]
subset.plot(subplots=True, figsize=(12, 10), grid=False, title="Number of births per year")
plt.show()

#
# Measuring the increase in naming diversity
#

table = top1000.pivot_table('prop', index='year', columns='sex', aggfunc=sum)
table.plot(title='Sum of table1000.prop by year and sex', yticks=np.linspace(0, 1.2, 13), xticks=range(1880, 2020, 10))
plt.show()

#
# How many of the most popular names it takes to reach 50%
#
df = boys[boys.year == 2010]
prop_cumsum = df.sort_values(by='prop', ascending=False).prop.cumsum()
print(prop_cumsum[:10])
print(prop_cumsum.searchsorted(0.5))

df = boys[boys.year == 1900]
in1900 = df.sort_values(by='prop', ascending=False).prop.cumsum()
in1900.searchsorted(0.5) + 1

def get_quantile_count(group, q=0.5): 
	group = group.sort_values(by='prop', ascending=False)
	return group.prop.cumsum().searchsorted(q) + 1

diversity = top1000.groupby(['year', 'sex']).apply(get_quantile_count)
diversity = diversity.unstack('sex')
diversity.plot(title="Number of popular names in top 50%")
plt.show()

#
# The “Last letter” Revolution: In 2007, a baby name researcher Laura Wattenberg pointed out on her website 
# (http://www.babynamewizard.com) that the distribution of boy names by final letter has
# changed significantly over the last 100 years.
# extract last letter from name column
# As you will see, boy names ending in “n” have experienced significant growth since the
# 1960s.
get_last_letter = lambda x: x[-1]
last_letters = names.name.map(get_last_letter)
last_letters.name = 'last_letter'
table = names.pivot_table('births', index=last_letters, columns=['sex', 'year'], aggfunc=sum)
subtable = table.reindex(columns=[1910, 1960, 2010], level='year')
subtable.head()
subtable.sum()
letter_prop = subtable / subtable.sum().astype(float)

fig, axes = plt.subplots(2, 1, figsize=(10, 8))
letter_prop['M'].plot(kind='bar', rot=0, ax=axes[0], title='Male')
letter_prop['F'].plot(kind='bar', rot=0, ax=axes[1], title='Female', legend=False)
plt.show()

letter_prop = table / table.sum().astype(float)
dny_ts = letter_prop.loc[['d', 'n', 'y'], 'M'].T
dny_ts.head()
dny_ts.plot()
plt.show()

#
# Boy names that became girl names (and vice versa)
# Another fun trend is looking at boy names that were more popular with one sex earlier
# in the sample but have “changed sexes” in the present. One example is the name Lesley
# or Leslie.
#
all_names = top1000.name.unique()
mask = np.array(['lesl' in x.lower() for x in all_names])
lesley_like = all_names[mask]
print(lesley_like)
#array([Leslie, Lesley, Leslee, Lesli, Lesly], dtype=object)
filtered = top1000[top1000.name.isin(lesley_like)]
filtered.groupby('name').births.sum()
table = filtered.pivot_table('births', index='year', columns='sex', aggfunc='sum')
table = table.div(table.sum(1), axis=0)
table.tail()
table.plot(style={'M': 'k-', 'F': 'k--'})
plt.show()