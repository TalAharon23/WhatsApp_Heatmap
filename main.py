import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
from datetime import *
import datetime as dt

from seaborn import heatmap


def getDataPoint(line):
    splitLine = line.split(' - ')
    dateTime = splitLine[0]
    date, time = dateTime.split(', ')

    return date, time


def startsWithDateAndTime(starting_line):
    pattern1 = '^([0-9]+)(/)([0-9]+)(/)([0-9][0-9]), ([0-9]+):([0-9][0-9]) -'
    pattern2 = '^([0-9]+)(.)([0-9]+)(.)([0-9][0-9][0-9][0-9]), ([0-9]+):([0-9][0-9]) -'
    result = re.match(pattern1, starting_line) or re.match(pattern2, starting_line)
    if result:
        return True
    return False


def addEmptyHoursRows(i_df, i_lstHours):
    currDFHours = i_df.index.values.tolist()
    print(currDFHours)
    for hour in i_lstHours:
        if hour not in currDFHours:
            i_df.loc[hour] = [0, 0, 0, 0, 0, 0, 0]


# def main():


parsedData = []  # List to keep track of data so it can be used by a Pandas dataframe
### Uploading exported chat file
whatsapp_filePath = 'WhatsApp.txt'
with open(whatsapp_filePath, encoding="utf-8") as fp:
    ### Skipping first line of the file because contains information related to something about end-to-end encryption
    fp.readline()
    date, time = None, None
    while True:
        line = fp.readline()
        if not line:
            break
        line = line.strip()
        if startsWithDateAndTime(line):
            date, time = getDataPoint(line)
            parsedData.append([date, time])

df = pd.DataFrame(parsedData, columns=['Date', 'Time'])  # Initialising a pandas Dataframe.
### changing datatype of "Date" column.
df["Date"] = pd.to_datetime(df["Date"])

# df.isnull().sum()  # Checking no. of null values in dataset
### Droping Nan values from dataset
df = df.dropna()
df = df.reset_index(drop=True)
print(df)

days = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}
df['Day'] = df['Date'].dt.weekday.map(days)  # matches date with corresponded day to a new column
df = df[['Date', 'Day', 'Time']]  # rearranging df

lst_hours = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16',
             '17', '18', '19', '20', '21', '22', '23']

lst = []
for i in df['Time']:  # '16:24'
    lst.append(i.split(':')[0])

df['Hours'] = lst
print(df)
df = df.groupby(['Hours', 'Day'], as_index=False)['Time'].count()
df = df.rename(columns={"Time": "#Messages"})

print(df)

### Analysing on which time group is mostly active based on hours and day.

day_of_week = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

heatmap_data = df.pivot(index='Hours', columns='Day', values='#Messages')

heatmap_data = heatmap_data.fillna(0)
heatmap_data = heatmap_data[
    [day_of_week[0], day_of_week[1], day_of_week[2], day_of_week[3], day_of_week[4], day_of_week[5], day_of_week[6]]]

yAxis = []
for i in range(00, 23, 2):
    yAxis.append(i)
# print(yAxis)

addEmptyHoursRows(heatmap_data, lst_hours)
heatmap_data = heatmap_data.sort_values(by=['Hours'], ascending=False)

print(heatmap_data)

# def changeTo2HoursScale
for index in heatmap_data.index.values.tolist():
    if int(index) % 2 == 0:
        continue
    else:
        for day in day_of_week:
            heatmap_data[day][int(index)] += heatmap_data[day][int(index) - 1]

for index in heatmap_data.index.values.tolist():
    if int(index) % 2 == 0:
        heatmap_data = heatmap_data.drop(heatmap_data.index[int(index)])

print(heatmap_data)


plt.figure('WhatsApp Heatmap', figsize=(10, 6))
sns.heatmap(
    data=heatmap_data,
    cmap='OrRd',
    annot=True,
    fmt='.0f',
    annot_kws={'fontsize': 6},
)

plt.show()

# if __name__ == "__main__":
#     main()
