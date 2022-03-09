import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re


# Consts:
DAYS = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday',
}
HOURS = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16',
         '17', '18', '19', '20', '21', '22', '23']


def getDataPoint(i_line):
    splitLine = i_line.split(' - ')
    dateTime = splitLine[0]
    date, time = dateTime.split(', ')
    return date, time


def startsWithDateAndTime(i_starting_line):
    # Checking if the line is compatible to one of the starting line patterns.
    pattern1 = '^([0-9]+)(/)([0-9]+)(/)([0-9][0-9]), ([0-9]+):([0-9][0-9]) -'
    pattern2 = '^([0-9]+)(.)([0-9]+)(.)([0-9][0-9][0-9][0-9]), ([0-9]+):([0-9][0-9]) -'
    return re.match(pattern1, i_starting_line) or re.match(pattern2, i_starting_line)


def addEmptyHoursRows(i_df, i_lstHours):
    # Adding new rows with zeros (represents the hours with no messages in all days)
    currDFHours = i_df.index.values.tolist()
    for hour in i_lstHours:
        if hour not in currDFHours:
            i_df.loc[hour] = [0, 0, 0, 0, 0, 0, 0]


def creatingDFFromFile(i_filePath):
    parsedData = []  # List to keep track of data so it can be used by a Pandas dataframe
    with open(i_filePath, encoding="utf-8") as fp:
        # Skipping first line of the file because contains information related to something about end-to-end encryption
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
    # changing datatype of "Date" column.
    df["Date"] = pd.to_datetime(df["Date"])

    # Dropping Nan values from dataset
    df = df.dropna()
    df = df.reset_index(drop=True)

    df['Day'] = df['Date'].dt.weekday.map(DAYS)  # matches date with corresponded day to a new column
    df = df[['Date', 'Day', 'Time']]  # rearranging df columns
    return df


def arrangeDFByHours(i_df):
    lst = []
    for i in i_df['Time']:  # e.g: '16:24'
        lst.append(i.split(':')[0])  # lst: 16,22,00,.... (Hours list)

    i_df['Hours'] = lst  # adding new hours column
    i_df = i_df.groupby(['Hours', 'Day'], as_index=False)['Time'].count()  # summarize num of messages in each hour
    # on each day.
    i_df = i_df.rename(columns={"Time": "#Messages"})
    return i_df


def createHeatmapData(i_df):
    # Create a matrix ( yAxis - Hours, xAxis - Days, values: #messages )
    heatmap_data = i_df.pivot(index='Hours', columns='Day', values='#Messages')
    heatmap_data = heatmap_data.fillna(0)  # replace nan values with 0.
    heatmap_data = heatmap_data[
        [DAYS[6], DAYS[0], DAYS[1], DAYS[2], DAYS[3], DAYS[4], DAYS[5]]]  # Reorder the days columns sequence

    addEmptyHoursRows(heatmap_data, HOURS)  # Adding rows with zero to hours with no messages.
    heatmap_data = heatmap_data.sort_values(by=['Hours'], ascending=False)
    heatmap_data = changeTo2HoursScale(heatmap_data)
    return heatmap_data


def changeTo2HoursScale(i_heatmap_data):
    for index in i_heatmap_data.index.values.tolist():
        if int(index) % 2 == 0:
            continue
        else:
            for day in DAYS.values():
                i_heatmap_data[day][int(index)] += i_heatmap_data[day][int(index) - 1]  # Adding the number of messages
                # from the next hour to the existing hour.

    # Staying with the even hours only ( 2 hours scale )
    for index in i_heatmap_data.index.values.tolist():
        if int(index) % 2 == 0:
            i_heatmap_data = i_heatmap_data.drop(i_heatmap_data.index[int(index)])
    return i_heatmap_data


def createHeatmap(i_heatmap_data):
    # Creating the heatmap window.
    plt.figure('WhatsApp Heatmap', figsize=(10, 6))
    plt.title("WhatsApp Heatmap", color='purple', size=16)
    sns.heatmap(
        data=i_heatmap_data,
        cmap='OrRd',
        annot=True,
        fmt='.0f',
        annot_kws={'fontsize': 6},
    )

    plt.show()


def main():
    # Uploading exported WhatsApp chat file
    whatsapp_filePath = 'WhatsApp.txt'
    df = creatingDFFromFile(whatsapp_filePath)
    df = arrangeDFByHours(df)
    heatmap_dataTable = createHeatmapData(df)
    createHeatmap(heatmap_dataTable)
    print(heatmap_dataTable)


if __name__ == "__main__":
    main()
