import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

#-----------------------------読み取り--------------------

class Experiment:
    UNICOLOR = ("#FF4B00", "#005AFF", "#03AF7A", "#4DC4FF", "#F6AA00", "#FFF100")
    BLANKUNI = ("#000000", "#FF4B00", "#005AFF", "#03AF7A", "#4DC4FF", "#F6AA00", "#FFF100")
    MUTEDCOLOR = ("#332288", "#88CCEE", "#44AA99", "#117733", "#999933", "#DDCC77", "#CC6677", "#882255", "#AA4499", "#DDDDDD")
    
    Axessize = [5,5] #Axes1つのサイズ
    Row = 1
    Column = 1
    S2M = 1/60#hh:ss:mm -> min
    def time2M(self, time) ->float :
        hms = str(time).split(":")
        M = int(hms[0]) * 60 + int(hms[1]) + int(hms[2]) * self.S2M
        return M

    def getcolor(self, color: str, n: int) -> str:#希望の色とデータ数からcolorを作成
        if(n <= 6 and color == "U"):
            color = self.UNICOLOR[:n]
        elif(n <= 10 and color in ["M","U"]):
            color = self.MUTEDCOLOR[:n]
        else:
            color = None
    
        return color


    def __init__(self, path:str):
        self.path = path
        self.Info = {}
        self.readInfoList = []
        self.readDfList = []
        self.columns  = None


        self.read_excel()

    def read_excel(self):
        wb = pd.read_excel(self.path, index_col=0)
        index = wb.index
        row = 0
        date = None
        time = None
        while(True):
            value = index[row]
            if(value =="Date"):
                date = wb.iloc[row,0]
            elif(value == "Time"):
                time = wb.iloc[row,0]
            elif(value in ["Plate Type", "    Shake"]):
                self.Info[value] = wb.iloc[row,0]
            elif(value == "Set Temperature"):
                self.Info[value] = re.findall(r"\d+", wb.iloc[row,0])
            elif(value == "Start Kinetic"):
                self.Info[value] = re.findall(r"(?=\d)[\d:]+", wb.iloc[row,0])[:2]
            elif(value == "    Read"):
                readInfo = {}
                if(wb.iloc[row,0] == "Fluorescence Endpoint"):
                    readInfo["type"] = "Fluorescence"

                elif(wb.iloc[row,0] == "Absorbance Endpoint"):
                    readInfo["type"] = "Absorbance"
                self.readInfoList.append(readInfo)
                print("found " + str(len(self.readInfoList)) + " measurement")
            elif(str(value).find("Read "+str(len(self.readDfList)+1)) >= 0):
                print("Reading detas " + str(len(self.readDfList)+1) + "/" + str(len(self.readInfoList)))
                i = row + 2
                if(type(self.columns) == type(None)):
                    j = 0
                    while(wb.iloc[i,j+1] is not np.nan):
                        j += 1
                    self.columns = wb.iloc[row+2,1:j]
                while(True):
                    if(wb.iloc[i,0] is np.nan):
                        df =  pd.DataFrame(wb.iloc[row+3:i,1:len(self.columns)+1])
                        df.columns = self.columns
                        df.columns.name = None
                        
                        time_value = wb.iloc[row+3:i,0]
                        min = [self.time2M(t) for t in time_value]
                        df.index = min
                        self.readDfList.append(df)
                        break
                    else:
                        i += 1
                if(len(self.readDfList) == len(self.readInfoList)):
                    break
            row += 1
        if(date != None and time != None):
            self.Info["date&time"] = datetime.datetime.combine(date.date(), time)

    #-----------------------------グラフの作成--------------------
    def make_graph(self, ax, read: int = 0, data: list = range(2), name :list = None, negcon :int = None, color :str = "U", marker : str = "."):
        ax.set_xlabel("Time / min")
        ax.set_ylabel(self.readInfoList[read]["type"] + " / A.U.")

        df :pd.DataFrame = self.readDfList[read].iloc[:,data]
        if(name):
            df.columns=name
        if(negcon):
            nc = np.array(self.readDfList[read].iloc[:,negcon])
            df = df.sub(nc,axis=0)
        df.plot.line(ax= ax, legend=True, color=self.getcolor(color, df.shape[1]), marker=marker)
        return 