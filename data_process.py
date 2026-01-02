#%%
import pandas as pd
import matplotlib.pyplot as plt
import os 
import plotly.express as px

#Put 

cwd = os.getcwd()
data_wd = os.path.join(cwd, 'Timedata', 'Raw_Life_Data.csv')

renaming_dictionary = {
    'YouTube + computer' : 'Internet',
    'Petting cat' : 'Pets',
    'Art ' : 'Art',
    'Music playing' : 'Piano',
    'Work' : 'PhD',
    'Side job' : 'Career',
    'Romantic partner' : 'Romantic Partner'
    }

begin_date = '2023-02-01'
end_date = '2023-12-31'

def read_and_clean(file_path, cleaning_dictionary, begin_date = None, end_date= None): 
    life_dataframe = pd.read_csv(file_path)
    life_dataframe = life_dataframe.replace({'Activity type': cleaning_dictionary})
    life_dataframe['From_dt'] = pd.to_datetime(life_dataframe['From'], format='%Y-%m-%d %H:%M:%S')
    life_dataframe['To_dt'] = pd.to_datetime(life_dataframe['To'], format='%Y-%m-%d %H:%M:%S')
    if end_date is None:
        end_date = life_dataframe['From_dt'].max()
    if begin_date is None:
        begin_date = life_dataframe['From_dt'].min()
    life_dataframe = life_dataframe[(life_dataframe['From_dt'] >= begin_date) & (life_dataframe['From_dt'] <= end_date)]
    return life_dataframe

life_dataframe = read_and_clean(data_wd,renaming_dictionary, begin_date, end_date)
colors = {
    'Piano': '#ff6c4a',
    'Phone': '#000000',
    'Internet': '#bdbdbd',
    'Yoga': '#78ffff',
    'Pets': '#3e2720',
    'Walk': '#59c6df',
    'Transport': '#c54167',
    'Friends': '#d0030c',
    'Read': '#8c7148',
    'Write': '#a903fd',
    'PhD': '#a58978',
    'Chinese': '#06e872',
    'Housework': '#8eb07a',
    'Art': '#c91262',
    'Career': '#5a5b60',
    'Exercise': '#02bda4',
    'Dnd': '#9467bd',
    'Sleep': '#bcbd22',
    'Chosing music': '#bcbd22',
    'Job search': '#526e7b',
    'Romantic Partner': '#fe01ff',
    'Zone': '#ffaa06',
}

#%%
#find some way to display totals for the year
life_dataframe['Time_Amount'] = life_dataframe['To_dt'] - life_dataframe['From_dt']
life_dataframe['Time_Amount'] = (life_dataframe['Time_Amount'].dt.total_seconds()/3600).round(2)
year_total_series = life_dataframe.groupby(['Activity type'])['Time_Amount'].sum()
fig_total, ax_total = plt.subplots()
year_total_series.plot.bar(ax = ax_total,figsize = (10,6), grid=True, xticks=[], legend=False, ylabel="Percentage of Day", xlabel ="",  width=1.0, color = list(colors.values()))


#%%
#graph to get stacked bar chart by day for a year
life_dataframe['Date'] = life_dataframe['From_dt'].dt.date
life_dataframe['Time_Amount'] = life_dataframe['To_dt'] - life_dataframe['From_dt']
week_dataframe = life_dataframe.groupby(['Date','Activity type'])['Time_Amount'].sum().unstack()

pivot_df_percentage = week_dataframe.div(week_dataframe.sum(axis=1), axis=0) * 100
fig_percentage, ax_percentage = plt.subplots()
pivot_df_percentage.plot.bar(ax = ax_percentage,figsize = (10,6), stacked=True,
                  grid=True, xticks=[], color =colors, legend=False, ylabel="Percentage of Day", xlabel ="",  width=1.0)

fig_percentage.legend(loc='upper center', ncol = 6, bbox_to_anchor=(0.5, 1.10))

#%% Graph to get percentage average time per week day
life_dataframe['Weekday'] = life_dataframe['From_dt'].dt.dayofweek
life_dataframe['Time_Amount'] = life_dataframe['To_dt'] - life_dataframe['From_dt']

life_dataframe['Time_Amount'] = (life_dataframe['Time_Amount'].dt.total_seconds()/3600).round(2)
week_dataframe = life_dataframe.groupby(['Weekday','Activity type'])['Time_Amount'].mean().unstack()

fig_week, ax_week = plt.subplots()
week_dataframe.plot.bar(ax = ax_week,figsize = (10,6), stacked=True, grid=True, legend=False,color =colors, ylabel="Average Time Spent per day", xlabel ="",  width=1.0)

fig_week.legend(loc='upper center', ncol = 6, bbox_to_anchor=(0.5, 1.10))
#might need to fix bc timestamp not datetime
# Graph by hour of the day
#%%
duplicate = life_dataframe[life_dataframe['From_dt'].dt.date != life_dataframe['To_dt'].dt.date].copy()
duplicate_midnight = life_dataframe[life_dataframe['From_dt'].dt.date != life_dataframe['To_dt'].dt.date].copy()
duplicate_morning = life_dataframe[life_dataframe['From_dt'].dt.date != life_dataframe['To_dt'].dt.date].copy()

duplicate_midnight['To_dt'] = duplicate_midnight.apply(lambda x: pd.Timestamp(x['To_dt']).replace(
    year = x['From_dt'].date().year,
    month = x['From_dt'].date().month, 
    day = x['From_dt'].date().day, 
    hour= 23, 
    minute= 59, 
    second = 59),
    axis = 1)
duplicate_morning['From_dt'] = duplicate_morning.apply(lambda x: pd.Timestamp(x['From_dt']).replace(
    year = x['To_dt'].date().year,
    month = x['To_dt'].date().month, 
    day = x['To_dt'].date().day, 
    hour= 0, 
    minute= 0, 
    second = 1),
    axis = 1)

lifedataframe =life_dataframe.drop(duplicate.index)
cleandataframe = pd.concat([lifedataframe, duplicate_midnight, duplicate_morning])

assert len(cleandataframe[cleandataframe['From_dt'].dt.date != cleandataframe['To_dt'].dt.date]) == 0, "BAD DAYS"

# add hour columns
for i in range(24):
    a = cleandataframe['From_dt'].apply(lambda x: x.replace(hour=i, minute=0, second=0))
    b = cleandataframe['From_dt'].apply(lambda x: x.replace(hour=i, minute=59, second=59))
    c = cleandataframe['From_dt']
    d = cleandataframe['To_dt']
    minbd = pd.concat([b, d], axis=1).apply(min, axis=1)
    maxac = pd.concat([a, c], axis=1).apply(max, axis=1)
    diff = (minbd - maxac).apply(lambda x: max(x, pd.Timedelta(0)))
    cleandataframe[f"hour{i}"] = diff

hour_columns = cleandataframe.columns

clean_dataframe_bar = cleandataframe.groupby('Activity type')[hour_columns[-24:]].sum()
clean_dataframe_bar= clean_dataframe_bar.apply(lambda x: x.apply(lambda y: y.total_seconds()/3600))
clean_dataframe_bar=clean_dataframe_bar.transpose()
fig_stacked, a_stacked = plt.subplots()
clean_dataframe_bar.plot(ax = a_stacked, kind='bar', stacked = True, figsize = (10,6), legend=False, color =colors, ylabel="Hours")
fig_stacked.legend(loc='upper center', ncol = 6, bbox_to_anchor=(0.5, 1.10))

# percent stacked bar by day

# Graph by day of the week
# by month

