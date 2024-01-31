"""
説明文

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy
from dataclasses import dataclass, field

@dataclass
class graphStyle:
    #以下は入力が必須
    name_list: list 

    #以下は入力が任意
    Col: int = 1
    Row: int = 1
    AxSize:tuple = (5,5)
    subplots_adjust:list = None
    figsize:tuple = None
    xlabel: str = "x label"
    ylabel: str = "y label"
    plot_list:list = None
    negcon:int = None
    legend:bool = True
    color_list:list = None
    marker:str = "."
    figsize: tuple = None

    #以下は入力が不要
    source_name_list = None
    datasize: int = 1
    
    def __post_init__(self):
        self.source_name_list = self.name_list
        self.dataSize = len(self.name_list)
        if(not self.plot_list):
            self.plot_list = [True] * (self.dataSize)
        if(not self.figsize):
            self.figsize = (self.Col*self.AxSize[0], self.Row*self.AxSize[1])
        if(not self.subplots_adjust):
            self.subplots_adjust = [plt.rcParams["figure.subplot.left"], plt.rcParams["figure.subplot.bottom"], plt.rcParams["figure.subplot.right"], plt.rcParams["figure.subplot.top"], plt.rcParams["figure.subplot.wspace"], plt.rcParams["figure.subplot.hspace"]]
    


class Experiment:
    """
    Experimentクラスは1つの計測データに対応し，大まかに以下の機能を持ちます．
    
    1.計測データをpandas.dataframe内に保管
    2.計測内容に関する文字列データを保管
    3.グラフスタイルをglaphStyleクラスとして保管
    4.保管されたgraphStyleに従ったグラフの作成

    具体的には，次のように設計されています
    self.sourve_data    :pandas.dataframe ->計測データの保管
    self.Info           :list ->計測内容に関する文字データ，自由に設定可能
    self.draw_graph()
        現在設定されているgraphStyleに従ってグラフを作成
        Figureのリサイズが発生した場合，FigureCanvasTkAggを改めて作成する必要があるため，これのチェックを返り値とする
        変更点を調べるために，self.rescent_gSにgraphStyleを設定する

        グラフの作成はgSの変更点に従って以下のように行われる
        (i)figsizeが変更されているか？
            y->generate_figureによってfigureオブジェクトを作成，check_FigureCanvasTkaggをTrue
            n->figureオブジェクトを使いまわす
        (ii)その他gSを設定する
    """
    UNICOLOR = ("#FF4B00", "#005AFF", "#03AF7A", "#4DC4FF", "#F6AA00", "#FFF100")
    BLANKUNI = ("#000000", "#FF4B00", "#005AFF", "#03AF7A", "#4DC4FF", "#F6AA00", "#FFF100")
    MUTEDCOLOR = ("#332288", "#88CCEE", "#44AA99", "#117733", "#999933", "#DDCC77", "#CC6677", "#882255", "#AA4499", "#DDDDDD")


    def __getcolor(self, color: str, n: int) -> str:#希望の色とデータ数からcolorを作成
        if(n <= 6 and color == "U"):
            color = self.UNICOLOR[:n]
        elif(n <= 10 and color in ["M","U"]):
            color = self.MUTEDCOLOR[:n]
        else:
            color = [None] * n
    
        return color
    
    def __init__(self, dataframe: pd.DataFrame, info: dict, **style):
        self.source_data = dataframe
        self.info = info
        column_list = self.source_data.columns.values.tolist()
        self.gS = graphStyle(column_list, **style)
        self._gS = self.fig = None


    #-----------------------------グラフの作成--------------------
    def draw_graph(self):
        check_FigureCanvasTkAgg = None
        if((not self._gS) or self.gS.figsize != self._gS.figsize):
            check_FigureCanvasTkAgg = True
            self.generate_Figure()
        self.set_graph_from_gS()
        self._gS = copy.deepcopy(self.gS)
        return check_FigureCanvasTkAgg
    
    def generate_Figure(self):
        if(self.fig):
            plt.close(self.fig)
        
        print(self.gS.figsize, type[self.gS.figsize[0]])
        self.fig = plt.figure(figsize=self.gS.figsize)
        pars = self.gS.subplots_adjust
        self.fig.subplots_adjust(left=pars[0], bottom=pars[1], right=pars[2], top=pars[3], wspace=pars[4], hspace=pars[5])
        self.ax:plt.Axes = self.fig.add_subplot(1,1,1)

    def set_graph_from_gS(self):
        self.ax.clear()
        #ラベル軸の設定
        self.ax.set_xlabel(self.gS.xlabel)
        self.ax.set_ylabel(self.gS.ylabel)
        plot_list = [i for i, value in enumerate(self.gS.plot_list) if value]
        df :pd.DataFrame = self.source_data.iloc[:, plot_list]
        if(self.gS.name_list):
            df.columns = [self.gS.name_list[i] for i in plot_list]
        if(self.gS.negcon):
            nc = np.array(self.source_data.iloc[:,self.gS.negcon])
            df = df.sub(nc,axis=0)
        df.plot.line(ax=self.ax, legend=self.gS.legend, color=self.gS.color_list, marker=self.gS.marker)
