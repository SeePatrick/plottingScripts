import re               #Regular Expression
import pandas as pd     #Pandas Dataframes
import seaborn as sns   #Seaborn Plots
import os               #File/Folder Operations
import numpy as np      #Linalg operations

from pandas import DataFrame

subFolderList = []          #List of folders contained in current directory

currentFileList = []        #List of files

measurementFileList = []    #List of all dpt files

singleValuePattern = re.compile(r'\d+.\d+') #regular expression separating x and y value in one line of the dsc file

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
rootDirectory = os.path.realpath(__file__)[:-22]

#Get all files in current directory
f = []
for (rootDirectory, subFolderList, currentFileList) in os.walk(rootDirectory):
    f.extend(currentFileList)
    break

#Exclude all files which are not dpt files
for currentItem in currentFileList:
    if currentItem.find('dpt') != -1:
        measurementFileList.append(currentItem)

currentData = []
allData = []
ramanShift = []
measurementLabels = []

fileCounter = 0

for currentFile in measurementFileList:
    with open(currentFile) as dataFile:
        for currentLine in dataFile:
            currentValuePair = re.findall(singleValuePattern, currentLine)
            if(currentValuePair != []):
                currentData.append(float(currentValuePair[1]))  

                if(len(ramanShift) < 8881):
                    ramanShift.append(float(currentValuePair[0]))
    
    measurementLabels.append(currentFile)

    #Compute norm
    maxValue = max(currentData)
    currentDataNumpy = np.array(currentData)/maxValue 
    #allData.extend(currentDataNumpy)
    allData.append(currentDataNumpy)

    currentData = []
    fileCounter += 1

allDataNumpy = np.asarray(allData)

measurementDataFrame = DataFrame(index=ramanShift, data=np.transpose(allDataNumpy), columns=measurementLabels)
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
dataPlot.set(xlabel = "Raman Shift [$cm^{-1}$]", ylabel = 'Intensity', title = 'Raman Measurement')
dataPlot.figure.savefig('RamanPlot.jpg')

#Clear figure in order to save the zoomed version (just Seaborn stuff)
dataPlot.figure.clf()

#Zoomed Plot: Plot meaned and normed data for interesting range   
startingIndex = ramanShift.index(900, 1600, 1700)
endingIndex = ramanShift.index(1700, 3000, 4000)

zommedData = measurementDataFrame.iloc[startingIndex:endingIndex, :]
zoomedPlot = sns.lineplot(data=zommedData)
zoomedPlot.set(xlabel = "Raman Shift [$cm^{-1}$]", ylabel = 'Intensity', title = 'Zoomed Raman Measurement')
zoomedPlot.figure.savefig('ZoomedRamanPlot.jpg')