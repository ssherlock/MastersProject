# -*- coding: utf-8 -*-
"""
@author: Chris
"""
from math import fsum
import pandas as pd
import datetime

globalPredHorizon = 30
globalHistTimeFrame = 120
globalCurrentPump = "2"

#imports formatted data
def getData(pumpNum):
    baseDirectory = "C:\\Users\\Chris\\OneDrive\\Masters\\Project\\Code\\data\\"
    pumpNumbers = ["2", "7", "10", "16", "21", "24", "28"]
    if pumpNum not in pumpNumbers:
        print("error, invalid pump number")
    return pd.read_excel(baseDirectory + pumpNum + "RoundedGlucose.xlsx"), pd.read_excel(baseDirectory + pumpNum + "FormattedCarbInsulin.xlsx")


#checks carbInsulinData goes back two hours from targetDateTime
def checkTargetIsValid(targetDT, varData, predHorizon = globalPredHorizon, histTimeFrame = globalHistTimeFrame):
    lastDT = targetDT - datetime.timedelta(minutes = predHorizon) - datetime.timedelta(minutes = histTimeFrame)
    strLastDT = lastDT.strftime("%Y-%m-%d %H:%M")
    strDT = targetDT.strftime("%Y-%m-%d %H:%M")
    index = glucoseData.index[glucoseData["Time"] == strDT][0]
    if strLastDT in varData.values and strDT in varData.values and str(glucoseData["Glucose Value (mmol/L)"][index]).replace(".","",1).isdigit():
        return True
    else:
        print("target is invalid: ", targetDT)
        return False

#assumes target date is valid
def getVariables(dt, varData, predHorizon = globalPredHorizon, histTimeFrame = globalHistTimeFrame):
    variables = {}
    variableCount = 0
    dt = dt - datetime.timedelta(minutes = predHorizon)
    dtMinus1Hour = dt - datetime.timedelta(minutes = 60)
    lastDT = dt - datetime.timedelta(minutes = histTimeFrame)
    #combines time periods to reduce number of variables
    #varData is ordered by time so previous index is 5 minute previous
    while dt > lastDT:
        strDT = dt.strftime("%Y-%m-%d %H:%M")
        index = varData.index[varData["Time"] == strDT][0]
        #15 min intervals, 30 after an hour
        if dt > dtMinus1Hour:
            basalAmount = fsum([varData["Basal Amount (U/h)"][index], varData["Basal Amount (U/h)"][index - 1], varData["Basal Amount (U/h)"][index - 2]]) / 3.0
            bolusType = max([varData["Bolus Type"][index], varData["Bolus Type"][index - 1], varData["Bolus Type"][index - 2]])
            bolusVolume = fsum([varData["Bolus Volume (U)"][index], varData["Bolus Volume (U)"][index - 1], varData["Bolus Volume (U)"][index - 2]])
            duration = max([varData["Duration (min)"][index], varData["Duration (min)"][index - 1], varData["Duration (min)"][index - 2]])
            carbs = fsum([varData["Carbs(g)"][index], varData["Carbs(g)"][index - 1], varData["Carbs(g)"][index - 2]])
            dt = dt - datetime.timedelta(minutes = 15)
        else:
            basalAmount = fsum([varData["Basal Amount (U/h)"][index], varData["Basal Amount (U/h)"][index - 1], varData["Basal Amount (U/h)"][index - 2], varData["Basal Amount (U/h)"][index - 3], varData["Basal Amount (U/h)"][index - 4], varData["Basal Amount (U/h)"][index - 5]]) / 6.0
            bolusType = max([varData["Bolus Type"][index], varData["Bolus Type"][index - 1], varData["Bolus Type"][index - 2], varData["Bolus Type"][index - 3], varData["Bolus Type"][index - 4], varData["Bolus Type"][index - 5]])
            bolusVolume = fsum([varData["Bolus Volume (U)"][index], varData["Bolus Volume (U)"][index - 1], varData["Bolus Volume (U)"][index - 2], varData["Bolus Volume (U)"][index - 3], varData["Bolus Volume (U)"][index - 4], varData["Bolus Volume (U)"][index - 5]])
            duration = max([varData["Duration (min)"][index], varData["Duration (min)"][index - 1], varData["Duration (min)"][index - 2], varData["Duration (min)"][index - 3], varData["Duration (min)"][index - 4], varData["Duration (min)"][index - 5]])
            carbs = fsum([varData["Carbs(g)"][index], varData["Carbs(g)"][index - 1], varData["Carbs(g)"][index - 2], varData["Carbs(g)"][index - 3], varData["Carbs(g)"][index - 4], varData["Carbs(g)"][index - 5]])
            dt = dt - datetime.timedelta(minutes = 30)
        variableCount += 1
        variables["x" + str(variableCount)] = round(basalAmount, 2)
        variableCount += 1
        variables["x" + str(variableCount)] = bolusType
        variableCount += 1
        variables["x" + str(variableCount)] = round(bolusVolume, 2)
        variableCount += 1
        variables["x" + str(variableCount)] = duration
        variableCount += 1
        variables["x" + str(variableCount)] = carbs
    return variables



#target data, variableData
glucoseData, carbInsulinData = getData(globalCurrentPump)

print("Starting, pump =", globalCurrentPump, " globalPred = ", globalPredHorizon)
constructedVariableData = pd.DataFrame()
for i in range(len(glucoseData)):
    date = pd.to_datetime(glucoseData["Time"][i], format="%Y-%m-%d %H:%M")
    if (checkTargetIsValid(date, carbInsulinData)):
        variables = getVariables(date, carbInsulinData)
        variables["y1"] = float(glucoseData["Glucose Value (mmol/L)"][i])
        rowDF = pd.DataFrame([list(variables.values())], columns = [list(variables.keys())], index = [glucoseData["Time"][i]])
        constructedVariableData = constructedVariableData.append(rowDF)

print("\nConstructedVariableData")
print(constructedVariableData)

constructedVariableData.to_csv("C:\\Users\\Chris\\OneDrive\\Masters\\Project\\Code\\data\\" + str(globalCurrentPump) + "Variables" + str(globalPredHorizon) + ".csv", index = False)