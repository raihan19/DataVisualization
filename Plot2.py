import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.backends.backend_pdf import PdfPages

# create dataframe object
df = pd.read_csv("O_example.csv")
df_dict = df.to_dict()

countNA = 0
for key in df_dict['start_date']:
    if df_dict['start_date'][key] == "n.a.":
        countNA += 1

if countNA > 0:
    df = df.drop(df.query('start_date=="n.a."').sample(frac=1).index)
    df.to_csv('O_example.csv', index=False)

df = pd.read_csv("O_example.csv")
'''Group each entries by month'''
df['start_date'] = pd.to_datetime(df['start_date'])
groupedVal = df.groupby(df['start_date'].dt.strftime('%m/%Y'))['district'].apply(lambda z: "%s" % ', '.join(z))

# convert the grouped value to dictionary
newGroupedVal = groupedVal.to_dict()

'''Dates which are in string format cannot be sorted properly. That's string needs to be
converted in datetime object to be sorted properly'''
dates = []
lenDistrict = []
for key in newGroupedVal:
    date_object = datetime.strptime(key, '%m/%Y').date()
    dates.append(date_object)

sortedDates = sorted(dates)
newSortedDates = []

for i in range(len(sortedDates)):
    newSortedDates.append(sortedDates[i].strftime('%m/%Y'))

# get the value by passing the sorted date as key, count the number of entries
for i in range(len(newSortedDates)):
    lenDistrict.append(len(newGroupedVal[newSortedDates[i]].split(',')))

# create labels for years only like 2009, 2010...
labels = []
newSortedLabels = []
for val in newSortedDates:
    labels.append(val[3:7])
    newSortedLabels.append('')
sortedLabels = sorted(labels)
# eliminate copies
newLabels = list(dict.fromkeys(labels))

# for each corresponding y values create corresponding x values
labelsDict = {}
for i in range(len(newLabels)):
    count = 0
    for j in range(len(newSortedDates)):
        if newLabels[i] == sortedLabels[j]:
            count += 1
    labelsDict[newLabels[i]] = count

# format x axis value names
newVal = 0
for key in labelsDict:
    newSortedLabels[newVal] = "FY " + key
    newVal += labelsDict[key]

'''Create folders where reports will be saved'''
try:
    os.makedirs("{}/CityA/Reports".format(os.getcwd()))
except OSError as e:
    print(e)

# get all district
allDistrict = df.district.to_dict()
# get all district as a list of list
allDistrictList = []
for key in allDistrict.keys():
    allDistrictList.append(allDistrict[key].split(','))

# get all district in individual list
newAllDistrictList = []
for i in range(len(allDistrictList)):
    for j in range(len(allDistrictList[i])):
        newAllDistrictList.append(allDistrictList[i][j])

# get unique district
uniqueDistList = list(dict.fromkeys(newAllDistrictList))

'''get the index of unique district occurrence'''
newAllDistrictIndex = []
for i in range(len(uniqueDistList)):
    allDistrictIndex = []
    for j in range(len(allDistrictList)):
        if uniqueDistList[i] in allDistrictList[j]:
            allDistrictIndex.append(j)
    newAllDistrictIndex.append(allDistrictIndex)

# create a list of column names to be used in loop
listColumn = ['utilities_cost', 'miscellaneous_cost', 'rent', 'base_rent', 'price', 'size', 'price_per_qm']

df = pd.read_csv("O_example.csv")
df['start_date'] = pd.to_datetime(df['start_date'])
groupedVal = df.groupby(df['start_date'].dt.strftime('%m/%Y'))['furnished'].apply(lambda z: "%s" % ', '.join(z))
furnishedOrNot = groupedVal.to_dict()
furnished = 0
notFurnished = 0
furnishedOrNotList = []
for i in range(len(newSortedDates)):
    furnishedOrNotList.append(furnishedOrNot[newSortedDates[i]].split(', '))

furnishedOrNotDict = {}
j = 0
for val in furnishedOrNotList:
    for i in range(len(val)):
        if val[i] == 'Yes':
            furnished += 1
        else:
            notFurnished += 1
    furnishedOrNotDict[newSortedDates[j]] = str(furnished) + ',' + str(notFurnished)
    j += 1

furnishedBoth = []
for key in furnishedOrNotDict:
    furnishedBoth.append(furnishedOrNotDict[key].split(','))
furnishOne = []
furnishTwo = []
for val in furnishedBoth:
    for i in range(len(val)):
        if i % 2 == 0:
            furnishOne.append(int(val[i]))
        elif i % 2 == 1:
            furnishTwo.append(int(val[i]))

# uncomment if you want control the number of reports to be generated
# countTemp = 0
for iDist in range(len(uniqueDistList)):
    # uncomment if you want control the number of reports to be generated
    # if countTemp == 3:
    #     break

    '''generate pdf object'''
    try:
        pp = PdfPages('{}/CityA/Reports/O_report_CityA_Fig{}_{}.pdf'.format(os.getcwd(), iDist+1, uniqueDistList[iDist]))
    except:
        continue

    # bar plot
    x = np.arange(len(dates))  # the label locations
    width = 0.35  # the width of the bars

    fig_1, ax_1 = plt.subplots()
    fig_1.set_canvas(plt.gcf().canvas)
    N = len(sortedLabels)
    ind = np.arange(N)
    colors = []
    for key in labelsDict:
        for j in range(labelsDict[key]):
            if int(key) % 2 == 0:
                colors.append('y')
            else:
                colors.append('b')

    rects1 = ax_1.bar(x - width/2, lenDistrict, 0.05, label='Total Entries')
    rects2 = ax_1.bar(x, furnishOne, 0.05, label='Furnished Entries')
    rects3 = ax_1.bar(x + width/2, furnishTwo, 0.05, label='Non-Furnished Entries')


    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax_1.set_ylabel('Entries')
    ax_1.set_title('Entries per month')
    ax_1.set_xticks(x)
    ax_1.grid(which='both')
    ax_1.set_xticklabels(newSortedLabels)
    ax_1.legend()

    fig_1.tight_layout()
    plt.xticks(rotation=30)
    pp.savefig(bbox_inches='tight', dpi=300, orientation='portrait', pad_inches=0.5)

    # loop through each column to generate report
    for iterI in range(len(listColumn)):
        df = pd.read_csv("O_example.csv")
        # contains row value of the column
        val_list1 = []
        if listColumn[iterI] == 'utilities_cost':
            val_list1 = df.utilities_cost
        if listColumn[iterI] == 'miscellaneous_cost':
            val_list1 = df['miscellaneous_cost']
        if listColumn[iterI] == 'rent':
            val_list1 = df.rent
        if listColumn[iterI] == 'base_rent':
            val_list1 = df.base_rent
        if listColumn[iterI] == 'price':
            val_list1 = df.price
        if listColumn[iterI] == 'size':
            val_list1 = df['size']
        if listColumn[iterI] == 'price_per_qm':
            val_list1 = df.price_per_qm

        # contains raw values in dictionary format
        val_list2 = val_list1.to_dict()
        # contains raw values except faulty values
        val_list3 = []

        for p in val_list2:
            if listColumn[iterI] == 'utilities_cost':
                if val_list2[p] == 'n.a.' or val_list2[p] == 'n.a':
                    val_list3.append('Null')
                    continue
                val_list3.append(val_list2[p].split('€'))
            if listColumn[iterI] == 'miscellaneous_cost':
                if val_list2[p] == 'n.a.' or val_list2[p] == 'n.a':
                    val_list3.append('Null')
                    continue
                val_list3.append(val_list2[p].split('€'))
            if listColumn[iterI] == 'rent':
                if val_list2[p] == 'n.a.' or val_list2[p] == 'n.a':
                    val_list3.append('Null')
                    continue
                val_list3.append(val_list2[p].split('€'))
            if listColumn[iterI] == 'base_rent':
                if val_list2[p] == 'n.a.' or val_list2[p] == 'n.a':
                    val_list3.append('Null')
                    continue
                val_list3.append(val_list2[p].split('€'))
            if listColumn[iterI] == 'price':
                if val_list2[p] == 'n.a.' or val_list2[p] == 'n.a':
                    val_list3.append('Null')
                    continue
                val_list3.append(val_list2[p].split('€'))
            if listColumn[iterI] == 'size':
                if val_list2[p] == 'n.a.' or val_list2[p] == 'n.a':
                    val_list3.append('Null')
                    continue
                val_list3.append(val_list2[p].split(' m²'))
            if listColumn[iterI] == 'price_per_qm':
                if val_list2[p] == 'n.a.' or val_list2[p] == 'n.a':
                    val_list3.append('Null')
                    continue
                val_list3.append(val_list2[p])

        # contains values where null becomes none
        val_list4 = []
        for i in range(len(val_list3)):
            if val_list3[i] == "Null":
                val_list4.append(np.nan)
                continue
            if listColumn[iterI] == 'price_per_qm':
                val_list4.append(val_list3[i])
            else:
                val_list4.append(val_list3[i][0])

        '''Write a column to the csv file for calculation purpose'''
        df["new_val"] = val_list4
        df.to_csv("O_example.csv", index=False)

        df = pd.read_csv("O_example.csv")

        '''interpolate that column and override the new values'''
        interpolatedVal = df['new_val'].interpolate(method='linear', limit_direction='both').to_dict()
        interpolatedValList = []
        i = 0
        for key in interpolatedVal:
            interpolatedValList.append(interpolatedVal[key])
            i += 1

        df["new_val"] = interpolatedValList
        df.to_csv("O_example.csv", index=False)

        '''we want values for specific district. blankList will tract that.'''
        df = pd.read_csv("O_example.csv")
        blankList = []
        for i in range(len(interpolatedValList)):
            blankList.append(None)
        # only insert the value to the specific location where the corresponding district resides
        for i in range(len(newAllDistrictIndex[iDist])):
            blankList[newAllDistrictIndex[iDist][i]] = interpolatedValList[newAllDistrictIndex[iDist][i]]

        # create new column to insert the values
        df["new_new_val"] = blankList
        df.to_csv("O_example.csv", index=False)

        df = pd.read_csv("O_example.csv")
        '''interpolate that column and override the new values'''
        newInterpolatedVal = df['new_new_val'].interpolate(method='linear', limit_direction='both').to_dict()
        newInterpolatedValList = []
        i = 0
        for key in newInterpolatedVal:
            newInterpolatedValList.append(newInterpolatedVal[key])
            i += 1

        df["new_new_val"] = newInterpolatedValList
        df.to_csv("O_example.csv", index=False)

        '''group the values by months'''
        df = pd.read_csv("O_example.csv")
        df['start_date'] = pd.to_datetime(df['start_date'])
        groupedVal = df.groupby(df['start_date'].dt.strftime('%m/%Y'))['new_new_val'].sum().sort_values()
        newGroupedVal = groupedVal.to_dict()

        # append the new values in list format
        val_list5 = []
        for i in range(len(newSortedDates)):
            val_list5.append(newGroupedVal[newSortedDates[i]]/lenDistrict[i])

        # delete the newly generated columns
        first_column = df.columns[len(df.columns)-1]
        df = df.drop([first_column], axis=1)
        df.to_csv('O_example.csv', index=False)

        df = pd.read_csv("O_example.csv")
        second_column = df.columns[len(df.columns)-1]
        df = df.drop([second_column], axis=1)
        df.to_csv('O_example.csv', index=False)

        # plot
        # create data frame for plot
        duoPlot = pd.DataFrame({
         'entries': lenDistrict,
         'vals': val_list5})

        fig = plt.figure()
        fig.set_canvas(plt.gcf().canvas)
        ax = duoPlot['entries'].plot(kind="bar", width=width, color=colors);plt.xticks(rotation=30)
        ax2 = ax.twinx()
        ax2.plot(ax.get_xticks(),duoPlot['vals'], color='r')

        plt.ticklabel_format(style='plain', axis='y')
        ax.yaxis.set_label_position("right")
        ax.yaxis.tick_right()
        ax.set_ylabel('Entries')
        ax.set_title("Average {} for CityA-{}".format(listColumn[iterI], uniqueDistList[iDist]))
        ax.set_xticks(x)
        ax2.yaxis.set_label_position("left")
        ax2.yaxis.tick_left()
        ax2.set_ylabel("Average {}".format(listColumn[iterI]))
        ax.grid(which='both')
        ax.set_xticklabels(newSortedLabels)

        # save the figure
        pp.savefig(bbox_inches='tight', dpi=300, orientation='portrait', pad_inches=0.5)
    # uncomment if you want control the number of reports to be generated
    # countTemp += 1
    pp.close()