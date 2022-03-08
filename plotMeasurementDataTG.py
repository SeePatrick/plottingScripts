import re               #Regular Expression
import pandas as pd     #Pandas Dataframes
import seaborn as sns   #Seaborn Plots
import os               #File/Folder Operations
import numpy as np      #Linalg operations

from pandas import DataFrame

#List of folders contained in current directory
subFolderList = []

#List of all files in current folder
currentFileList = []

#List of only relevant data files in current folder
measurementFileList = []

#regular expression separating x and y value in one line of the dsc file
singleValuePattern = re.compile(r'\d+[^\t]\d+')

#Check whether two string differ in one character (if strings are the same, still return false)
def matchNames(firstName, secondName):
    match = False

    for firstCheck, secondCheck in zip(firstName, secondName):
        if firstCheck != secondCheck:
            if match:
                return False
            else:
                match = True

    return match

#Get path to this script (excluding 22 char name of script)
rootDirectory = os.path.realpath(__file__)[:-25]

#Get all files in current directory
f = []
for (rootDirectory, subFolderList, currentFileList) in os.walk(rootDirectory):
    f.extend(currentFileList)
    break

#Sort for data files only
for currentItem in currentFileList:
    if currentItem.find('txt') != -1:
        measurementFileList.append(currentItem)
print(measurementFileList)
#Get list of all subfolder names
subFolderList = [item for item in os.listdir(rootDirectory) if os.path.isdir(os.path.join(rootDirectory, item))]

currentFileData = []
allData = []
temperature = []
measurementFileLabels = []

lineCounter = 0

for currentFile in measurementFileList:
    with open(currentFile) as dataFile:
        for currentLine in dataFile:
            if (lineCounter > 33):
                currentValuePair = re.findall(singleValuePattern, currentLine)
                if(currentValuePair != []):

                    #Skip additional datapoints if measurements of same sample have different lengths
                    if(len(temperature) < 654):
                        temperature.append(float(currentValuePair[0]))
                    if(len(currentFileData) < 654):
                        currentFileData.append(float(currentValuePair[2]))

            lineCounter += 1

    measurementFileLabels.append(currentFile)
    lineCounter = 0

    allData.append(np.array(currentFileData))
    currentFileData = []

allDataNumpy = np.transpose(np.asarray(allData))

measurementDataFrame = DataFrame(index=temperature, data=allDataNumpy, columns=measurementFileLabels)
print('Read data:')
print(measurementDataFrame)

#Compute mean of multiple measurements of same sample (file names of these should differ in only one character/digit)

while True:
    #Work out data columns of the same sample
    columnsToComputeMeanOf = []
    lastLabel = ''
    for currentLabel in measurementDataFrame.columns:

        if lastLabel == '':
            lastLabel = currentLabel
        else:
            if matchNames(currentLabel, lastLabel):
                if(len(columnsToComputeMeanOf) == 0):
                    columnsToComputeMeanOf.append(lastLabel)
                columnsToComputeMeanOf.append(currentLabel)
                lastLabel = currentLabel

            else:
                break

    if len(columnsToComputeMeanOf) == 0:
        break 
    else:
        #Compute mean of selected columns
        dataToMean = measurementDataFrame[columnsToComputeMeanOf]
        dataToMean = dataToMean.mean(axis = 1)

        #Delete old columns from dataframe and add their mean instead
        measurementDataFrame = measurementDataFrame.drop(columns=columnsToComputeMeanOf)
        measurementDataFrame[columnsToComputeMeanOf[0][:-6] + '_Mean'] = dataToMean 

print('Worked Data: ')
print(measurementDataFrame)


dataPlot = sns.lineplot(data = measurementDataFrame)
dataPlot.set(xlabel = "Temperature [°C]", ylabel = 'Mass [%]', title = 'TG Analysis')
dataPlot.figure.savefig('TGPlot.jpg')
