# -*- coding: utf-8 -*-
"""
@author: Chris
"""

#formats variable data, rounds to 5 minute mark
import pandas as pd
import datetime

PUMP_NUMBER = "2"

print("Starting")

#imports data
def getData(pumpNum):
    baseDirectory = "C:\\Users\\Chris\\OneDrive\\Masters\\Project\\Code\\data\\"
    
    return pd.read_excel(baseDirectory + pumpNum + "CarbInsulin.xlsx")

carbInsulinData = getData(PUMP_NUMBER)

#Round time to 5 minutes then format
#reduces accuracy of data slightly but assuming slight inaccuracy in readings to begin with so shouldnt have too much effect
if PUMP_NUMBER != "7" and PUMP_NUMBER != "2":
    carbInsulinData["Time"] = pd.to_datetime(carbInsulinData["Time"], format="%d/%m/%Y %H:%M").dt.round("5min").dt.strftime("%Y-%m-%d %H:%M")
else:
    carbInsulinData["Time"] = pd.to_datetime(carbInsulinData["Time"], format="%m/%d/%Y %H:%M").dt.round("5min").dt.strftime("%Y-%m-%d %H:%M")

#Normal is classed as float in data for unknown reasons, converts everything to str
carbInsulinData["Bolus Type"] = carbInsulinData["Bolus Type"].astype(str)

#drops total daily dose rows from table
for i in range(len(carbInsulinData)):
    if carbInsulinData["Bolus Type"][i] == "nan":
        carbInsulinData["Bolus Type"][i] = 0
    elif carbInsulinData["Bolus Type"][i] == "Normal":
        carbInsulinData["Bolus Type"][i] = 1
    elif carbInsulinData["Bolus Type"][i] == "Combination":
        carbInsulinData["Bolus Type"][i] = 2
        
    if carbInsulinData["Total daily dose"][i] > 0:
        carbInsulinData = carbInsulinData.drop(i)

#drop total daily dose columns from table
carbInsulinData = carbInsulinData.drop(["Total daily dose", "Total daily basal"], axis = 1)

#resets index
carbInsulinData.reset_index(drop = True, inplace = True)

#Aggregating
aggregation_functions = {"Basal Amount (U/h)": "last", "Bolus Type": "max", "Bolus Volume (U)": "sum", "Duration (min)": "max", "Carbs(g)": "sum"}
aggregateCarbInsulinData = carbInsulinData.groupby(carbInsulinData["Time"]).aggregate(aggregation_functions)
aggregateCarbInsulinData = aggregateCarbInsulinData.sort_values(by = "Time")
carbInsulinData = aggregateCarbInsulinData.reset_index()

#loops through and adds 5 minute intervals in time if non currently exists
date = pd.to_datetime(carbInsulinData["Time"][0], format="%Y-%m-%d %H:%M")
endDate = pd.to_datetime(carbInsulinData["Time"][len(carbInsulinData) - 1], format="%Y-%m-%d %H:%M")
currentBasal = carbInsulinData["Basal Amount (U/h)"][0]

#assigns previous basal value if required
while date <= endDate:
    strDate = date.strftime("%Y-%m-%d %H:%M")
    if strDate in carbInsulinData.values:
        dateIndex = carbInsulinData.index[carbInsulinData["Time"] == strDate][0]
        if carbInsulinData["Basal Amount (U/h)"][dateIndex] >= 0:
            currentBasal = carbInsulinData["Basal Amount (U/h)"][dateIndex]
        else:
            carbInsulinData["Basal Amount (U/h)"][dateIndex] = currentBasal
    else:
        newRow = pd.DataFrame = {"Time": strDate, "Basal Amount (U/h)": currentBasal}
        carbInsulinData = carbInsulinData.append(newRow, ignore_index = True)
    date += datetime.timedelta(minutes = 5)

#change NaN values
carbInsulinData["Bolus Type"] = carbInsulinData["Bolus Type"].fillna(0)
carbInsulinData["Bolus Volume (U)"] = carbInsulinData["Bolus Volume (U)"].fillna(0)
carbInsulinData["Duration (min)"] = carbInsulinData["Duration (min)"].fillna(0)
carbInsulinData["Carbs(g)"] = carbInsulinData["Carbs(g)"].fillna(0)

#sorts values by time and reset index
formattedCarbInsulinData = carbInsulinData.sort_values(by = "Time")
formattedCarbInsulinData.reset_index(drop = True, inplace = True)

formattedCarbInsulinData.to_excel("C:\\Users\\Chris\\OneDrive\\Masters\\Project\\Code\\data\\" + PUMP_NUMBER + "FormattedCarbInsulin.xlsx")