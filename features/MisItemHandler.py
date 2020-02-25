import pandas as pd;
import re
import numpy as np

def isBugsInFile(oneFile, fileName, condition, result, lastContext, nextContext):
    if(oneFile == None):
        return 0;
    i = 0;
    isBug = 1;
    lineNumResult = -1;
    lineNumLastContext = -1;
    lineNumNextContext = -1;
    isConditionFound = False;
    all_lines = re.split('\n', oneFile);
    for linea in all_lines:
        i = i + 1;
        if linea.find(condition) != -1 :
            isConditionFound = True;
        else:
#            print 'not a bug, cannot find condition!';
            return 0;
        if linea.find(result) != -1 and isConditionFound:
            if(lastContext == 'none' and nextContext == 'none'):
#                print 'not a bug, find a item in file:' + fileName + " on line", i;
                return 0;
            else:lineNumResult = i;
        if lastContext != 'none' and linea.find(lastContext) != -1 and isConditionFound:
            lineNumLastContext = i;
        if nextContext != 'none' and linea.find(nextContext) != -1 and isConditionFound:
            lineNumNextContext = i;
        if(lastContext != 'none' and nextContext != 'none' and lineNumLastContext + 1 == lineNumResult and lineNumResult + 1 == lineNumNextContext and lineNumResult != -1 and lineNumLastContext != -1 and lineNumNextContext != -1):
#            print 'not a bug, find a item in file:' + fileName + " on line", i - 1;
            return 0;
        if(lastContext != 'none' and nextContext == 'none' and lineNumLastContext + 1 == lineNumResult and lineNumResult != -1 and lineNumLastContext != -1):
#            print 'not a bug, find a item in file:' + fileName + " on line", i;
            return 0;
        if(lastContext == 'none' and nextContext != 'none' and lineNumResult + 1 == lineNumNextContext and lineNumResult != -1 and lineNumNextContext != -1):
#            print 'not a bug, find a item in file:' + fileName + " on line", i - 1;
            return 0;
    return isBug;

def getfrommisitem(all_logs):    
    fpOb = open("features/nls/ObsMissItem.tsv", "r");
    conditionList = [];
    resultList = [];
    observationList = [];
    fileNameList = [];
    lastContextList = [];
    nextContextList = [];    
    for lineOb in fpOb.readlines():
        if lineOb.split(",")[0] == 'Observation':
            observationList.append(lineOb.split(",")[1:]);
        if lineOb.split(",")[0] == 'condition':
            conditionList.append(lineOb.split(",")[1:]);
        if lineOb.split(",")[0] == 'result':
            resultList.append(lineOb.split(",")[1:]);
        if lineOb.split(",")[0] == 'log':
            fileNameList.append(lineOb.split(",")[1:]);
        if lineOb.split(",")[0] == 'lastContext':
            lastContextList.append(lineOb.split(",")[1:]);
        if lineOb.split(",")[0] == 'nextContext':
            nextContextList.append(lineOb.split(",")[1:]);
    fpOb.close()

    for j in range(len(observationList)):
        observationList[j][len(observationList[j]) - 1] = observationList[j][len(observationList[j]) - 1].replace("\n", "");
        conditionList[j][len(conditionList[j]) - 1] = conditionList[j][len(conditionList[j]) - 1].replace("\n", "");
        resultList[j][len(resultList[j]) - 1] = resultList[j][len(resultList[j]) - 1].replace("\n", "");
        fileNameList[j][len(fileNameList[j]) - 1] = fileNameList[j][len(fileNameList[j]) - 1].replace("\n", "");
        lastContextList[j][len(lastContextList[j]) - 1] = lastContextList[j][len(lastContextList[j]) - 1].replace("\n", "");
        nextContextList[j][len(nextContextList[j]) - 1] = nextContextList[j][len(nextContextList[j]) - 1].replace("\n", "");

#    print conditionList;
#    print resultList;
#    print observationList;
#    print fileNameList;
#    print lastContextList;
#    print nextContextList;
    output_list=[];
    bug_name_list=[];
    for numOfObs in range(len(observationList)):
#        print 
#        print "check " + observationList[numOfObs][0];
        conditions = conditionList[numOfObs][0];
        results = resultList[numOfObs][0];
        fileName = fileNameList[numOfObs][0];
        lastContext = lastContextList[numOfObs][0];
        nextNeighbor = nextContextList[numOfObs][0];
#        print conditions;
#        print results;
#        print fileName;
#        print lastContext;
#        print nextNeighbor;
#        print if fileName in np.array(all_logs.columns)
        if fileName in np.array(all_logs.columns):
            isBug = isBugsInFile(all_logs[fileName][0], fileName, conditions, results, lastContext, nextNeighbor);
        else:
            isBug = 0;
        #observationList[numOfObs].append(isBug);
        output_list.append(isBug);
        bug_name_list.append(observationList[numOfObs][0]);
        print "bug in " + observationList[numOfObs][0] + ":", isBug == 1;
#    print output_list;
    aa=np.array(output_list).reshape(1,len(bug_name_list));
    output_df = pd.DataFrame(aa,columns=bug_name_list);
#    print output_df;
    return output_df;


