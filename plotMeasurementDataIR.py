import re                       #Regular Expression
import pandas as pd     
from pandas import DataFrame    #Pandas Dataframes

import seaborn as sns   #Seaborn Plots
import os               #File/Folder Operations
import numpy as np      #Linalg operations


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
rootDirectory = os.path.realpath(__file__)[:-24]

#Get all files in current directory
f = []
for (rootDirectory, subFolderList, currentFileList) in os.walk(rootDirectory):
    f.extend(currentFileList)
    break

#Exclude all files which are not dpt files
for currentItem in currentFileList:
    if currentItem.find('dpt') != -1:
        measurementFileList.append(currentItem)

currentFileRawData = []
wavenumber = []
measurementFilelabels = []
normalizedData = []
fileCounter = 0

for currentFile in measurementFileList:
    with open(currentFile) as dataFile:
        for currentLine in dataFile:
            currentValuePair = re.findall(singleValuePattern, currentLine)
            if(currentValuePair != []):
                
                if(len(wavenumber) < 1745): 
                    wavenumber.append(int(currentValuePair[0]))
                
                currentFileRawData.append(float(currentValuePair[1]))

    measurementFilelabels.append(currentFile)

    #Normalize raw data of current file
    maxValue = max(currentFileRawData)
    currentDataNumpy = np.array(currentFileRawData)/maxValue
    normalizedData.append(currentDataNumpy)

    currentFileRawData = []
    fileCounter += 1

#Convert back to numpy array and to correct form for dataframe
normalizedDataNumpy = np.transpose(np.asarray(normalizedData))
print(normalizedDataNumpy.shape)

measurementDataFrame = DataFrame(index=wavenumber, data=normalizedDataNumpy, columns=measurementFilelabels)

print('Raw Data: ')
print(measurementDataFrame)

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

#Whole Plot: Plot meaned and normed data for whole available data range    
dataPlot = sns.lineplot(data = measurementDataFrame)
dataPlot.set(xlabel = "Wavenumber [$cm^{-1}$]", ylabel = 'Transmittance', title = 'IR Measurements')
dataPlot.figure.savefig('IRPlot.jpg')

#Clear figure in order to save the zoomed version (just Seaborn stuff)
dataPlot.figure.clf()

#Zoomed Plot: Plot meaned and normed data for interesting range   
startingIndex = wavenumber.index(1700, 1000, 7000)
endingIndex = len(wavenumber)

zoomedData = measurementDataFrame.iloc[startingIndex:endingIndex, :]
zoomedPlot = sns.lineplot(data=zoomedData)
zoomedPlot.set(xlabel = "Wavenumber [$cm^{-1}$]", ylabel = 'Transmittance', title = 'Zoomed IR Measurement')
zoomedPlot.figure.savefig('ZoomedIRPlot.jpg')
