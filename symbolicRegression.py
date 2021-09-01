# -*- coding: utf-8 -*-
"""
@author: Chris
"""
import math
import pandas as pd
from random import randint, random
from copy import deepcopy
import numpy as np

#Function Hyperparamaters
POP_SIZE = 100
MAX_GENERATIONS = 20
NUMBER_OF_ELITES = 5
ELITISM = True
TOURNAMENT_SIZE = 5
CROSSOVER_PERCENTAGE = 0.7
SIZE_PENALTY = True
SIZE_PENALTY_STRENGTH = 0.05
VARIABLE_CONSTANT_RATIO = 60 #% out of 100

#variables to choose which file to use
#pumpNumbers = ["2", "7", "10", "14", "16", "21", "24", "28"]
FILE_NUMBER = "16"
PRED_HORIZON = 30
GLUCOSE = False
TRAINING_PERCENT = 0.6
ALL_VARIABLES = False


#imports data
def getVariables(pumpNum, glucose = False):
    baseDirectory = "C:\\Users\\Chris\\OneDrive\\Masters\\Project\\Code\\data\\"
    
    if ALL_VARIABLES:
        if GLUCOSE:
            return pd.read_csv(baseDirectory + str(pumpNum) + "VariablesAllVariablesGlucose" + str(PRED_HORIZON) + ".csv")
        else:
            return pd.read_csv(baseDirectory + str(pumpNum) + "VariablesAllVariables" + str(PRED_HORIZON) + ".csv")
    elif glucose:
        return pd.read_csv(baseDirectory + str(pumpNum) + "VariablesGlucose" + str(PRED_HORIZON) + ".csv")
    else:
        return pd.read_csv(baseDirectory + str(pumpNum) + "Variables" + str(PRED_HORIZON) + ".csv")

varData = getVariables(FILE_NUMBER, GLUCOSE)
print("varData:")
print(varData)

trainData = varData.sample(frac = TRAINING_PERCENT).reset_index(drop=True)
testData = varData.drop(trainData.index)
trainTarget = trainData.pop("y1")
testTarget= testData.pop("y1")


def getColumns(data):
    columns = []
    for col in data.columns:
        columns.append(col)
    return columns

columnNames = getColumns(trainData)

def convertColumnsNamesToNode(columnNames):
    variables = {}
    for i in range(1, len(columnNames) + 1):
        variables["x" + str(i)] = {"featureName": ("x" + str(i))}
    return variables

variables = convertColumnsNamesToNode(columnNames)

#function and operator functions
def add(x, y):
    try:
        ans = x + y
    except OverflowError:
        ans = float("inf")
    return ans

def sub(x, y):
    try:
        ans = x - y
    except OverflowError:
        ans = float("inf")
    return ans

def mul(x, y):
    try:
        ans = x * y
    except OverflowError:
        ans = float("inf")
    return ans

def div(x, y):
    return x / y if y else x

def neg(x):
    return -x

def cos(x):
    try:
        ans = math.cos(x)
    except math.error:
        ans = x
    return ans

def sin(x):
    try:
        ans = math.sin(x)
    except math.error:
        ans = x
    return ans

def exp(x):
    try:
        ans = math.exp(x)
    except OverflowError:
        ans = float("inf")
    return ans

operations = (
    {"func": add, "argCount": 2, "formatStr": "({} + {})"},
    {"func": sub, "argCount": 2, "formatStr": "({} - {})"},
    {"func": mul, "argCount": 2, "formatStr": "({} * {})"},
    {"func": div, "argCount": 2, "formatStr": "({} / {})"},
    {"func": neg, "argCount": 1, "formatStr": "-({})"},
    #{"func": cos, "argCount": 1, "formatStr": "Cos({})"},
    #{"func": sin, "argCount": 1, "formatStr": "Sin({})"},
    #{"func": exp, "argCount": 1, "formatStr": "Exp({})"}
)


def printModel(node):
    if "children" not in node:
        if "featureName" not in node:
            return node["value"]
        else:
            return node["featureName"]
    return node["formatStr"].format(*[printModel(c) for c in node["children"]])

def evaluate(node, row):
    if "children" not in node:
        if "featureName" not in node:
            return node["value"]
        else:
            return row[node["featureName"]]
    return node["func"](*[evaluate(c, row) for c in node["children"]])

def createRandomModel(depth, data = trainData):
    if randint(0, 10) >= depth * 0.5:
        op = operations[randint(0, len(operations) - 1)]
        return {
            "func": op["func"],
            "children": [createRandomModel(depth + 1) for _ in range(op["argCount"])],
            "formatStr": op["formatStr"]
        }
    elif randint(1, 100) <= VARIABLE_CONSTANT_RATIO:
        return {"featureName": data.columns[randint(0, data.shape[1] - 1)]}
    else:
        newConstant = round(random() * 2, 4) #random values between 0-2, opertions can adjust these values
        return {"value": newConstant}

def createPopulation(popSize, depth):
    population = [createRandomModel(0) for _ in range(popSize)]
    return population


#creating offspring (mutation + crossover)
def selectRandomNode(selected, parent, depth):
    if "children" not in selected:
        return parent
    #favour nodes near the root
    if randint(0, 10) < depth or depth >= 10:
        return selected
    childCount = len(selected["children"])
    return selectRandomNode(
        selected["children"][randint(0, childCount - 1)],
        selected,
        depth + 1
        )

def mutate(parent):
    offspring = deepcopy(parent)
    mutateNode = selectRandomNode(offspring, None, 0)
    childCount = len(mutateNode["children"])
    mutateNode["children"][randint(0, childCount - 1)] = createRandomModel(0)
    return offspring

def crossover(parent1, parent2):
    offspring = deepcopy(parent1)
    crossoverNode1 = selectRandomNode(offspring, None, 0)
    crossoverNode2 = selectRandomNode(parent2, None, 0)
    childCount = len(crossoverNode1["children"])
    crossoverNode1["children"][randint(0, childCount - 1)] = crossoverNode2
    return offspring


#selecting Parents
#uses tournament selection currently
def selectRandomParent(population, fitness):
    tournamentMembers = [
        randint(0, POP_SIZE - 1) for _ in range(TOURNAMENT_SIZE)
        ]
    memberFitness = [(fitness[i], population[i]) for i in tournamentMembers]
    return min(memberFitness, key = lambda x: x[0])[1]

#creates offspring
#either uses two parents for crossover or 1 for mutation, only one function used at a time atm
#researchers have found favoring crossover tends to produce better results
def createOffspring(population, fitness):
    parent1 = selectRandomParent(population, fitness)
    if random() > CROSSOVER_PERCENTAGE:
        parent2 = selectRandomParent(population, fitness)
        return crossover(parent1, parent2)
    else:
        return mutate(parent1)
    
def nodeCount(x):
    if "children" not in x:
        return 1
    return sum([nodeCount(c) for c in x["children"]])

#get model fitness
def calcFitness(program, prediction, target, method = "rmse", sizePenalty = SIZE_PENALTY):
    if method == "mse":
        error = ((prediction - target) ** 2).mean()
    elif method == "me":
        error = (prediction - target).mean()
    elif method == "mre":
        error = meanRelativeError(target, prediction)
    elif method == "rmse":
        error = math.sqrt(((prediction - target) ** 2).mean())
    if sizePenalty:
        error = error * (nodeCount(program) ** SIZE_PENALTY_STRENGTH)
    return error

def meanRelativeError(yTrue, yPred):
    return np.average(np.abs(yTrue - yPred) / yTrue, axis = 0)

#running generations
def runProgram(data = trainData, test = testData, target = trainTarget, testTarget = testTarget, eliteNum = NUMBER_OF_ELITES, elitism = ELITISM):
    topFitness = float("inf") #sets float to unbound max number
    population = createPopulation(POP_SIZE, 0)
    for gen in range(1, MAX_GENERATIONS + 1):
        fitnesses = []
        elites = [{"model": "", "fitness": float("inf")} for _ in range(eliteNum)]
        for model in population:
            prediction = [
                evaluate(model, row) for _, row in data.iterrows()
            ]
            score = calcFitness(model, prediction, target)
            fitnesses.append(score)
            if elitism:
                maxFitness = max(elites, key=lambda x:x["fitness"])
                if score <  maxFitness["fitness"]:
                    for i in range(len(elites)):
                        if elites[i]["fitness"] == maxFitness["fitness"]:
                            del elites[i]
                            break
                    elites.append({"model": model, "fitness": score})
            if score < topFitness:
                testPrediction = [
                    evaluate(model, row) for _, row in test.iterrows()
                ]
                topFitness = score
                bestTrainPred = prediction
                bestTestPred = testPrediction
                bestModel = model
                bestTrainRelError = meanRelativeError(target, prediction)
                bestTestRelError = meanRelativeError(testTarget, testPrediction)
                bestTrainMSE = ((prediction - target) ** 2).mean()
                bestTestMSE = ((testPrediction - testTarget) ** 2).mean()
                bestTrainRMSE = math.sqrt(((prediction - target) ** 2).mean())
                bestTestRMSE = math.sqrt(((testPrediction - testTarget) ** 2).mean())
        print(
            "Generation: %d\nBest Fitness: %.2f\nMedian Fitness: %.2f\nBest Model: %s\nBest Train RMSE: %.2f\nBest Train Relative Error: %.2f\nBest Test Relative Error: %.2f\n"
            % (
                gen,
                topFitness,
                pd.Series(fitnesses).median(),
                printModel(bestModel),
                bestTrainRMSE,
                bestTrainRelError,
                bestTestRelError
            )
        )
        if elitism:
            eliteModels = []
            for elite in elites:
                eliteModels.append(elite["model"])
            population = eliteModels + [
                createOffspring(population, fitnesses)
                for _ in range(POP_SIZE - eliteNum)
            ]
        else:
            population = [
                createOffspring(population, fitnesses)
                for _ in range(POP_SIZE)
            ]
    print("Best Fitness: %f" % topFitness)
    print("Best Train Relative Error: %f" % bestTrainRelError)
    print("Best Test Relative Error: %f" % bestTestRelError)
    print("Best Train Mean Square Error: %f" % bestTrainMSE)
    print("Best Test Mean Square Error: %f" % bestTestMSE)
    print("Best Train Root Mean Square Error: %f" % bestTrainRMSE)
    print("Best Test Root Mean Square Error: %f" % bestTestRMSE)
    print("Best Model: %s" % printModel(bestModel))
    trainOutput = {"TrainTarget": target, "TrainPred": bestTrainPred}
    testOutput = {"TestTarget": testTarget, "TestPred": bestTestPred}
    otherOutput = {"Model": printModel(bestModel), "Train Relative Error": bestTrainRelError, "Test Relative Error": bestTestRelError, "Train MSE": bestTrainMSE, "Test MSE": bestTestMSE, "Train RMSE": bestTrainRMSE, "Test RMSE": bestTestRMSE}
    settingsOutput = {"POP_SIZE": str(POP_SIZE), "Max_Generations": str(MAX_GENERATIONS), "NUMBER_OF_ELITES": str(NUMBER_OF_ELITES), "ELITISM": str(ELITISM), "TOURNAMENT_SIZE": str(TOURNAMENT_SIZE), "CROSSOVER_PERCENTAGE": str(CROSSOVER_PERCENTAGE),
                "SIZE_PENALTY": str(SIZE_PENALTY), "SIZE_PENALTY_STRENGTH": str(SIZE_PENALTY_STRENGTH), "VARIABLE_CONSTANT_RATIO": str(VARIABLE_CONSTANT_RATIO)}
    if ALL_VARIABLES:
        writer = pd.ExcelWriter(("C:\\Users\\Chris\\OneDrive\\Masters\\Project\\Code\\results\\" + FILE_NUMBER + "bestPredAllVariables+Glucose" + str(GLUCOSE) + str(PRED_HORIZON) + ".xlsx"), engine="xlsxwriter")
    else:
        writer = pd.ExcelWriter(("C:\\Users\\Chris\\OneDrive\\Masters\\Project\\Code\\results\\" + FILE_NUMBER + "bestPred+Glucose" + str(GLUCOSE) + str(PRED_HORIZON) + ".xlsx"), engine="xlsxwriter")
    pd.DataFrame(otherOutput, index=[0]).to_excel(writer, sheet_name = "modelInfo")
    pd.DataFrame(settingsOutput, index=[0]).to_excel(writer, sheet_name = "HyperparamterSettings")
    pd.DataFrame(trainOutput).to_excel(writer, sheet_name = "trainPredictions")
    pd.DataFrame(testOutput).to_excel(writer, sheet_name = "TestPredictions")
    writer.save()

runProgram()