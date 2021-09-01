# -*- coding: utf-8 -*-
"""
@author: Chris
"""
import pandas as pd
import datetime

globalPredHorizon = 30
globalHistTimeFrame = 120
globalCurrentPump = "28"

#imports formatted data
def getData(pumpNum):
    baseDirectory = "C:\\Users\\Chris\\OneDrive\\Masters\\Project\\Code\\data\\"
    pumpNumbers = ["2", "7", "10", "14", "16", "21", "24", "28"]
    if pumpNum not in pumpNumbers:
        print("error, invalid pump number")
    return pd.read_excel(baseDirectory + pumpNum + "RoundedGlucose.xlsx"), pd.read_excel(baseDirectory + pumpNum + "FormattedCarbInsulin.xlsx")


#checks carbInsulinData goes back two hours from targetDateTime
def checkTargetIsValid(targetDT, varData, glucoseData, predHorizon = globalPredHorizon, histTimeFrame = globalHistTimeFrame):
    lastDT = targetDT - datetime.timedelta(minutes = predHorizon) - datetime.timedelta(minutes = histTimeFrame)
    strLastDT = lastDT.strftime("%Y-%m-%d %H:%M")
    strTarget = targetDT.strftime("%Y-%m-%d %H:%M")
    dt = targetDT - datetime.timedelta(minutes = predHorizon)
    strDT = dt.strftime("%Y-%m-%d %H:%M")
    if strLastDT in varData.values and strDT in varData.values and strDT in glucoseData.values and str(glucoseData["Glucose Value (mmol/L)"][glucoseData.index[glucoseData["Time"] == strDT][0]]).replace(".","",1).isdigit() and str(glucoseData["Glucose Value (mmol/L)"][glucoseData.index[glucoseData["Time"] == strTarget][0]]).replace(".","",1).isdigit():
        return True
    else:
        print("target is invalid: ", targetDT)
        return False

#assumes target date is valid
def getVariables(dt, varData, glucoseData, predHorizon = globalPredHorizon, histTimeFrame = globalHistTimeFrame):
    variables = {}
    variableCount = 0
    dt = dt - datetime.timedelta(minutes = predHorizon)
    lastDT = dt - datetime.timedelta(minutes = histTimeFrame)
    gluIndex = glucoseData.index[glucoseData["Time"] == dt.strftime("%Y-%m-%d %H:%M")][0]
    #combines time periods to reduce number of variables
    #varData is ordered by time so previous index is 5 minute previous
    while dt > lastDT:
        strDT = dt.strftime("%Y-%m-%d %H:%M")
        index = varData.index[varData["Time"] == strDT][0]
        variableCount += 1
        variables["x" + str(variableCount)] = round(varData["Basal Amount (U/h)"][index], 2)
        variableCount += 1
        variables["x" + str(variableCount)] = varData["Bolus Type"][index]
        variableCount += 1
        variables["x" + str(variableCount)] = round(varData["Bolus Volume (U)"][index], 2)
        variableCount += 1
        variables["x" + str(variableCount)] = varData["Duration (min)"][index]
        variableCount += 1
        variables["x" + str(variableCount)] = varData["Carbs(g)"][index]
        dt = dt - datetime.timedelta(minutes = 5)
    variableCount += 1
    variables["x" + str(variableCount)] = glucoseData["Glucose Value (mmol/L)"][gluIndex]
    return variables



#target data, variableData
glucoseData, carbInsulinData = getData(globalCurrentPump)


constructedVariableData = pd.DataFrame()
for i in range(len(glucoseData)):
    date = pd.to_datetime(glucoseData["Time"][i], format="%Y-%m-%d %H:%M")
    if (checkTargetIsValid(date, carbInsulinData, glucoseData)):
        variables = getVariables(date, carbInsulinData, glucoseData)
        variables["y1"] = float(glucoseData["Glucose Value (mmol/L)"][i])
        rowDF = pd.DataFrame([list(variables.values())], columns = [list(variables.keys())], index = [glucoseData["Time"][i]])
        constructedVariableData = constructedVariableData.append(rowDF)

print("\nConstructedVariableData")
print(constructedVariableData)

constructedVariableData.to_csv("C:\\Users\\Chris\\OneDrive\\Masters\\Project\\Code\\data\\" + str(globalCurrentPump) + "VariablesGlucoseAllVariables" + str(globalPredHorizon) + ".csv", index = False)