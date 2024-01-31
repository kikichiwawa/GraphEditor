from experiment import *
import re
import pandas as pd
import datetime

S2M = 1/60#hh:ss:mm -> min
def time2M(time) ->float :
    hms = str(time).split(":")
    M = int(hms[0]) * 60 + int(hms[1]) + int(hms[2]) * S2M
    return M

def read_Excel(path):
    wb = pd.read_excel(path, index_col=0)
    index = wb.index
    row = 0
    date = None
    time = None
    common_info = {}
    columns = None
    info_list = []
    dataFrame_list = []

    while(True):
        value = index[row]
        if(value == "Date"):
            date = wb.iloc[row,0]
        elif(value == "Time"):
            time = wb.iloc[row,0]
        elif(value in ["Plate Type", "    Shake"]):
            common_info[value] = wb.iloc[row,0]
        elif(value == "Set Temperature"):
            common_info[value] = re.findall(r"\d+", wb.iloc[row,0])
        elif(value == "Start Kinetic"):
            common_info[value] = re.findall(r"(?=\d)[\d:]+", wb.iloc[row,0])[:2]
        elif(value == "    Read"):
            readinfo = {}
            if(wb.iloc[row,0] == "Fluorescence Endpoint"):
                readinfo["type"] = "Fluorescence"

            elif(wb.iloc[row,0] == "Absorbance Endpoint"):
                readinfo["type"] = "Absorbance"
            info_list.append(readinfo)
            print("found " + str(len(info_list)) + " measurement")
        elif(str(value).find("Read "+str(len(dataFrame_list)+1)) >= 0):
            print("Reading detas " + str(len(dataFrame_list)+1) + "/" + str(len(info_list)))
            i = row + 2
            if(type(columns) == type(None)):
                j = 0
                while(wb.iloc[i,j+1] is not np.nan):
                    j += 1
                columns = wb.iloc[row+2,1:j]
            while(True):
                if(wb.iloc[i,0] is np.nan):
                    df =  pd.DataFrame(wb.iloc[row+3:i,1:len(columns)+1])
                    df.columns = columns
                    df.columns.name = None
                    
                    time_value = wb.iloc[row+3:i,0]
                    min = [time2M(t) for t in time_value]
                    df.index = min
                    dataFrame_list.append(df)
                    break
                else:
                    i += 1
            if(len(dataFrame_list) == len(info_list)):
                break
        row += 1
    if(date != None and time != None):
        common_info["date&time"] = datetime.datetime.combine(date.date(), time)

    for info in info_list:
        info.update(common_info)

    return dataFrame_list, info_list

def getDataForGraphEditor(path:str) -> list[Experiment]:
    dataFrame_list, info_list = read_Excel(path)
    experiment_list = []
    for i in range(len(dataFrame_list)):
        dataFrame:pd.DataFrame = dataFrame_list[i]
        info = info_list[i]
        experiment = Experiment(dataFrame, info)

        #プレートリーダーに対応したグラフの各種設定
        experiment.gS.xlabel = "Time / min"
        experiment.gS.ylabel = info["type"]+" / A.U."
        experiment.gS.plot_list = [True]*len(dataFrame.columns)
        experiment.gS.plot_list[0] = False

        experiment_list.append(experiment)

    return experiment_list