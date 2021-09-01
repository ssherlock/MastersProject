# -*- coding: utf-8 -*-
"""
@author: Chris
"""

#File to floor minute into 5 minutes, ignoring seconds

import pandas as pd

REMOVE_STRING_ALERTS = True

baseDirectory = "C:\\Users\\Chris\\OneDrive\\Masters\\Project\\Code\\data\\"

pumpNumbers = ["2", "7", "10", "14", "16", "21", "24", "28"]

for number in pumpNumbers:

    directory = baseDirectory + number + "Glucose.xls"
    
    glucoseData = pd.read_excel(baseDirectory + number + "Glucose.xls")    
    
    for i in range(len(glucoseData["Timestamp (YYYY-MM-DDThh:mm:ss)"])):
        glucoseData["Timestamp (YYYY-MM-DDThh:mm:ss)"][i] = pd.Timestamp(glucoseData["Timestamp (YYYY-MM-DDThh:mm:ss)"][i]).floor(freq='5T')
    
    glucoseData["Timestamp (YYYY-MM-DDThh:mm:ss)"] = pd.to_datetime(glucoseData["Timestamp (YYYY-MM-DDThh:mm:ss)"]).dt.strftime("%Y-%m-%d %H:%M")
    
    #Renames Column
    glucoseData.rename(columns = {"Timestamp (YYYY-MM-DDThh:mm:ss)": "Time"}, inplace = True)
    
    glucoseData["Glucose Value (mmol/L)"] = glucoseData["Glucose Value (mmol/L)"].apply(pd.to_numeric, errors = "coerce")
    glucoseData = glucoseData.groupby(glucoseData["Time"]).aggregate({"Glucose Value (mmol/L)": "mean"})
    
    glucoseData.dropna(inplace = True)
    glucoseData.reset_index(inplace = True)
    
    print("\nfinal " + number + " Values:")
    print(glucoseData)
    
    glucoseData.to_excel(baseDirectory + number + "RoundedGlucose.xlsx", index = False)