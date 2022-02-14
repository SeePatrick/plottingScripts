import re               #Regular Expression
import pandas as pd     #Pandas Dataframes
import seaborn as sns   #Seaborn Plots
import os               #File/Folder Operations

from pandas import DataFrame

#List of folders contained in current directory
subFolderList = []

#List of all files in current folder
currentFileList = []

#List of only relevant data files in current folder
measurementFileList = []

#regular expression separating x and y value in one line of the dsc file
singleValuePattern = re.compile(r'\d+[^\t]\d+')

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

currentData = []
temperature = []
label = []

fileCounter = 0
lineCounter = 0

for currentFile in measurementFileList:
    with open(currentFile) as dataFile:
        for currentLine in dataFile:
            if (lineCounter > 33):
                currentValuePair = re.findall(singleValuePattern, currentLine)
                if(currentValuePair != []):
                    temperature.append(float(currentValuePair[0]))
                    currentData.append(float(currentValuePair[2]))               
                    label.append(currentFile)
            lineCounter += 1
    fileCounter += 1
    lineCounter = 0

data = {'Temperature' : temperature, 'Data': currentData, 'Measurement': label}

measurementDataFrame = DataFrame(data)
pd.pivot_table(measurementDataFrame, values='Data', index= 'Temperature', columns= 'Measurement')

print(measurementDataFrame)

dataPlot = sns.lineplot(data = measurementDataFrame, x = 'Temperature', y = 'Data', hue = 'Measurement')
dataPlot.set(xlabel = "Temperature [C]", ylabel = 'Mass [%]', title = 'TG Analysis')
dataPlot.figure.savefig('TGPlot.jpg')