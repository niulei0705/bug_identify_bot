import pandas as pd;
import re
import numpy as np


def isBugsInFile(oneFile, fileName, conditions, results):
    if(oneFile == None):
        return 0;
    i = 0;
    isBug = 0;
    index1 = -1;
    index2 = -1;
    all_lines = re.split('\n', oneFile);
    for linea in all_lines:
        i = i + 1;
        for indexCondition in range(len(conditions)):
            if linea.find(conditions[indexCondition]) != -1 :
                index1 = indexCondition;
        for indexRes in range(len(results)):
            if linea.find(results[indexRes]) != -1 :
                index2 = indexRes;
                if(index1 != -1 and index2 != -1 and index1 == index2):
#                    print 'find a mismatch bug in file:' + fileName + " on line", i;
                    isBug = 1;
    return isBug;
    
def get_from_mismatch(all_logs):    
    fpOb = open("features/nls/ObsMismatch.tsv", "r")
    conditionList = [];
    resultList = [];
    observationList = [];
    fileNameList = [];
    for lineOb in fpOb.readlines():
        if lineOb.split(",")[0] == 'Observation':
            observationList.append(lineOb.split(",")[1:]);
        if lineOb.split(",")[0] == 'condition':
            conditionList.append(lineOb.split(",")[1:]);
        if lineOb.split(",")[0] == 'result':
            resultList.append(lineOb.split(",")[1:]);
        if lineOb.split(",")[0] == 'log':
            fileNameList.append(lineOb.split(",")[1:]);
    fpOb.close()

    for j in range(len(observationList)):
        observationList[j][len(observationList[j]) - 1] = observationList[j][len(observationList[j]) - 1].replace("\n", "");
        conditionList[j][len(conditionList[j]) - 1] = conditionList[j][len(conditionList[j]) - 1].replace("\n", "");
        resultList[j][len(resultList[j]) - 1] = resultList[j][len(resultList[j]) - 1].replace("\n", "");
        fileNameList[j][len(fileNameList[j]) - 1] = fileNameList[j][len(fileNameList[j]) - 1].replace("\n", "");
    
#    print conditionList;
#    print resultList;
#    print observationList;
#    print fileNameList;
    output_list=[];
    bug_name_list=[];
    for numOfObs in range(len(observationList)):
#        print 
#        print "check " + observationList[numOfObs][0];
        conditions = conditionList[numOfObs];
        results = resultList[numOfObs];
        fileName = fileNameList[numOfObs][0];
        if fileName in np.array(all_logs.columns):
            isBug = isBugsInFile(all_logs[fileName][0], fileName, conditions, results);
        else:
            isBug = 0;
        observationList[numOfObs].append(isBug);
        bug_name_list.append(observationList[numOfObs][0]);
        output_list.append(isBug);
#        print "bug in " + observationList[numOfObs][0] + ":", isBug == 1;
#    print output_list;
    aa=np.array(output_list).reshape(1,len(bug_name_list));
    output_df = pd.DataFrame(aa,columns=bug_name_list);
#    print output_df;
    return output_df;
