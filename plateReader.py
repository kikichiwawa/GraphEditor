"""
参考文献
全体のデザイン：https://imagingsolution.net/program/python/tkinter/widget_layout_pack/ (最終アクセス:2023/11/21)
スクロールボックス：https://qiita.com/shinno1993/items/3ea14ffd7f17d8214961 (最終アクセス:2023/11/12)
"""
import tkinter as Tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os

from scrollframe import ScrollableFrame
from experiment import *

import get_plateReader_data #このインポートは動的にする予定

GEO_MAIN = "+50+50"

class SidePanel(ScrollableFrame):#pandasデータを受け取るたびに作成
    def __init__(self, master, experiment: Experiment, cf, **key):
        ScrollableFrame.__init__(self, master, **key)
        self.master = master
        self.key = key
        self.experiment = experiment
        self.gS = experiment.gS
        self.cf = cf

        #figsizeについての設定項目
        self.create_figsize_option()
        #data_selectionについての設定項目
        self.create_data_selection()
        #subplots_adjustについての設定項目
        self.create_subplots_adjust()
        #グラフ上に表示されるテキストに関する設定項目
        self.create_text_option()

    def create_figsize_option(self):
        KEY = "FIGSIZE"
        #figsizeについての設定項目
        #フレームの設定
        parent = ttk.Labelframe(self.scrollable_frame, text = "figsize(変更すると重くなります)")
        parent.pack(anchor=Tk.W)

        frame1 = Tk.Frame(parent)
        frame1.pack(anchor=Tk.W, padx=10, pady=2)
        #列タイトルの設定
        col_namelist = [None, "value"]
        for col in range(len(col_namelist)):
            if(col_namelist[col]):
                l = Tk.Label(frame1, text=col_namelist[col])
                l.grid(row=0, column=col)
        
        #詳細の設定
        row_namelist = ["width", "height"]
        value_list = []
        rescent_value_list = self.gS.figsize
        for row in range(len(row_namelist)):
            name = Tk.Label(frame1, text = row_namelist[row])
            name.grid(row=row+1, column=0)
            value = Tk.StringVar(value=rescent_value_list[row])
            #value.trace_add("write", lambda: self.value_check(KEY, value))
            value_list.append(value)
            e_value = ttk.Entry(frame1, state=Tk.NORMAL, textvariable=value)
            e_value.grid(row=row+1, column=1)
        self.figsize = value_list
        
        frame2 = Tk.Frame(parent)
        frame2.pack()

        button_reset = ttk.Button(frame2, text="Reset", command=lambda: self.reset_click(KEY))
        button_reset.pack(padx=5, pady=5, side=Tk.LEFT)
        button_init = ttk.Button(frame2, text="Initialize", command=lambda: self.init_click(KEY))
        button_init.pack(padx=5, pady=5, side=Tk.LEFT)    

    def get_figsize(self):
        figsize = [float(var.get()) for var in self.figsize]
        print(1,figsize, self.figsize)
        return figsize

    def create_data_selection(self):
        KEY = "DATA"
        #figsizeについての設定項目
        #フレームの設定
        parent = ttk.Labelframe(self.scrollable_frame, text = "Data selection")
        parent.pack(anchor=Tk.W)

        frame1 = Tk.Frame(parent)
        frame1.pack(anchor=Tk.W, padx=10, pady=2)
        #列タイトルの設定
        col_namelist = [None, "Source", "Name"]
        for col in range(len(col_namelist)):
            if(col_namelist[col]):
                l = Tk.Label(frame1, text=col_namelist[col])
                l.grid(row=0, column=col)
        
        #詳細の設定
        row_namelist = self.gS.source_name_list
        plot_list = []
        rescent_plot = self.gS.plot_list
        name_list = []
        rescent_name = self.gS.name_list
        for row in range(len(row_namelist)):
            plot = Tk.BooleanVar(value=rescent_plot[row])
            plot_list.append(plot)
            c_plot = ttk.Checkbutton(frame1, variable=plot)
            c_plot.grid(row=row+1, column=0)

            source = Tk.Label(frame1, text = row_namelist[row]) 
            source.grid(row=row+1, column=1)

            name = Tk.StringVar(value=rescent_name[row])
            name_list.append(name)
            e_name = ttk.Entry(frame1, state=Tk.NORMAL, textvariable=name)
            e_name.grid(row=row+1, column=2)

        self.plot_list = plot_list
        self.name_list = name_list

        frame2 = Tk.Frame(parent)
        frame2.pack()

        button_reset = ttk.Button(frame2, text="Reset", command=lambda: self.reset_click(KEY))
        button_reset.pack(padx=5, pady=5, side=Tk.LEFT)
        button_init = ttk.Button(frame2, text="Initialize", command=lambda: self.init_click(KEY))
        button_init.pack(padx=5, pady=5, side=Tk.LEFT)  

    def get_data_selection(self):
        name_list = [var.get() for var in self.name_list]
        plot_list = [var.get() for var in self.plot_list]

        if (not any(plot_list)):
            plot_list[0] = True
            self.plot_list[0].set(True)
            messagebox.showwarning("警告", "プロットするデータは必ず1つは選択してください．")
        return name_list, plot_list
    
    def create_subplots_adjust(self):
        KEY = "SUBPLOTS"
        #subplots_adjustについての設定項目
        #フレームの設定
        parent = ttk.Labelframe(self.scrollable_frame, text = "Subplots adjust")
        parent.pack(anchor=Tk.W)

        frame1 = Tk.Frame(parent)
        frame1.pack(anchor=Tk.W, padx=10, pady=2)
        #列タイトルの設定
        col_namelist = [None, "Value"]
        for col in range(len(col_namelist)):
            if(col_namelist[col]):
                l = Tk.Label(frame1, text=col_namelist[col])
                l.grid(row=0, column=col)
        
        #詳細の設定
        row_namelist = ["left", "bottom", "right", "top", "wspace", "hspace"]
        subplots_list = []
        rescent_subplots_list = self.gS.subplots_adjust

        for row in range(len(row_namelist)):
            name = Tk.Label(frame1, text = row_namelist[row]) 
            name.grid(row=row+1, column=1)

            value = Tk.StringVar(value=rescent_subplots_list[row])
            subplots_list.append(value)
            e_subplots = ttk.Entry(frame1, textvariable=value)
            e_subplots.grid(row=row+1, column=0)

        self.subplots_adjust_list = subplots_list

        frame2 = Tk.Frame(parent)
        frame2.pack()

        button_reset = ttk.Button(frame2, text="Reset", command=lambda: self.reset_click(KEY))
        button_reset.pack(padx=5, pady=5, side=Tk.LEFT)
        button_init = ttk.Button(frame2, text="Initialize", command=lambda: self.init_click(KEY))
        button_init.pack(padx=5, pady=5, side=Tk.LEFT)  

    def get_subplots_adjust(self):
        subplots_adjust = [float(var.get()) for var in self.subplots_adjust_list]
        left, bottom, right, top, *_ = subplots_adjust
        if(not (all(0 <= value <= 1 for value in subplots_adjust) and left < right and top > bottom)):
            messagebox.showwarning("警告", "subplots_adjustの条件が誤っています．")
            self.reset_click("SUBPLOTS")
            subplots_adjust = self.get_subplots_adjust()
        return subplots_adjust

    def create_text_option(self):
        KEY = "TEXT"
        #textについての設定項目
        #フレームの設定
        parent = ttk.Labelframe(self.scrollable_frame, text = "Text Option")
        parent.pack(anchor=Tk.W)

        frame1 = Tk.Frame(parent)
        frame1.pack(anchor=Tk.W, padx=10, pady=2)
        #列タイトルの設定
        col_namelist = [None, "Value"]
        for col in range(len(col_namelist)):
            if(col_namelist[col]):
                l = Tk.Label(frame1, text=col_namelist[col])
                l.grid(row=0, column=col)
        
        #詳細の設定
        row_namelist = ["xlabel", "ylabel"]
        text_list = []
        rescent_text_list = [self.gS.xlabel, self.gS.ylabel]

        for row in range(len(row_namelist)):
            name = Tk.Label(frame1, text = row_namelist[row]) 
            name.grid(row=row+1, column=1)

            value = Tk.StringVar(value=rescent_text_list[row])
            text_list.append(value)
            e_text = ttk.Entry(frame1, textvariable=value)
            e_text.grid(row=row+1, column=0)

        self.xlabel, self.ylabel = text_list

        frame2 = Tk.Frame(parent)
        frame2.pack()

        button_reset = ttk.Button(frame2, text="Reset", command=lambda: self.reset_click(KEY))
        button_reset.pack(padx=5, pady=5, side=Tk.LEFT)
        button_init = ttk.Button(frame2, text="Initialize", command=lambda: self.init_click(KEY))
        button_init.pack(padx=5, pady=5, side=Tk.LEFT)  

    def get_text_option(self):
        xlabel = self.xlabel.get()
        ylabel = self.ylabel.get()
        return xlabel, ylabel

    def reset_click(self, KEY):
        if(KEY == "FIGSIZE"):
            new_value = self.gS.figsize
            for i in range(len(self.figsize)):
                self.figsize[i].set(new_value[i])

        elif(KEY == "DATA"):
            new_plot_list = self.gS.plot_list
            for i in range(len(self.plot_list)):
                self.plot_list[i].set(new_plot_list[i])
            new_name_list = self.gS.name_list
            for i in range(len(self.name_list)):
                self.name_list[i].set(new_name_list[i])

        elif(KEY == "SUBPLOTS"):
            new_subplots_list = self.gS.subplots_adjust
            for i in range(len(self.subplots_adjust_list)):
                self.subplots_adjust_list[i].set(new_subplots_list[i])
        
        elif(KEY == "TEXT"):
            self.xlabel.set(self.gS.xlabel)
            self.ylabel.set(self.gS.ylabel)

    def init_click(self, KEY):
        if(KEY == "FIGSIZE"):
            new_value = (5,5)
            for i in range(len(self.figsize)):
                self.figsize[i].set(new_value[i])

        elif(KEY == "DATA"):
            new_plot_list = [True]*len(self.plot_list)
            for i in range(len(self.plot_list)):
                self.plot_list[i].set(new_plot_list[i])
            new_name_list = self.gS.source_name_list
            for i in range(len(self.name_list)):
                self.name_list[i].set(new_name_list[i])

        elif(KEY == "SUBPLOTS"):
            new_subplots_list = plt.rcParams["figure.subplot.left"], plt.rcParams["figure.subplot.bottom"], plt.rcParams["figure.subplot.right"], plt.rcParams["figure.subplot.top"], plt.rcParams["figure.subplot.wspace"], plt.rcParams["figure.subplot.hspace"]
            for i in range(len(self.subplots_adjust_list)):
                self.subplots_adjust_list[i].set(new_subplots_list[i])
               
        elif(KEY == "TEXT"):
            self.xlabel.set("x label")
            self.ylabel.set("y label")
    
    def export_gS(self):
        figsize = self.get_figsize()   
        name_list, plot_list = self.get_data_selection()
        subplots_adjust = self.get_subplots_adjust()
        xlabel, ylabel = self.get_text_option()
        negcon=None
        legend=True
        color_list=None
        marker="."
        new_gS = graphStyle(
            figsize=figsize,
            name_list=name_list,
            plot_list=plot_list,
            subplots_adjust=subplots_adjust,
            xlabel=xlabel,
            ylabel=ylabel,
            negcon=negcon,
            legend=legend,
            color_list=color_list,
            marker=marker
        )
        return new_gS

    def import_gS(self, gS):
        self.gS = gS   
        for KEY in ["FIGSIZE","DATA","SUBPLOTS","TEXT"]:
            self.reset_click(KEY)

class ExperimentSelect(Tk.Toplevel):
    def __init__(self, master, **key):
        Tk.Toplevel.__init__(master, **key)
        self.master = master
        self.index = self.master.experiment_index
        self.experiment_list = self.master.experiment_list

        self.title("データ選択") # ウィンドウタイトル
        self.geometry("300x200+100+100")   # ウィンドウサイズ(幅x高さ)
        # モーダルにする設定
        self.grab_set()        # モーダルにする
        self.focus_set()       # フォーカスを新しいウィンドウをへ移す
        self.transient(self.master)   # タスクバーに表示しない

        self.create_select_label() 
        self.create_table()

        self.protocol(self.on_closing)
 

    def create_select_label(self):
        parent = Tk.Label(self)
        parent.pack(side=Tk.TOP)

        l = Tk.Label(parent, text="データ選択")
        value_list = list(range(len(self.experiment_list)))
        self.cbox = ttk.Combobox(parent, values=value_list)
        print(self.index, value_list)
        self.cbox.set(self.index)
        self.cbox.bind('<<ComboboxSelected>>',self.table_update)

        l.pack(side=Tk.LEFT)
        self.cbox.pack(side=Tk.LEFT)

    def create_table(self):
        self.tree = ttk.Treeview(self, columns=(0,1))
        self.tree.heading(0,text="要素名")
        self.tree.heading(1,text="内容")
        info:dict = self.experiment_list[self.index].info
        for values in info.items():
            self.tree.insert("", index="end", values=values)

    def table_update(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.index = int(self.cbox.get())
        info:dict = self.experiment_list[self.index].info
        for values in info.items():
            self.tree.insert("", index="end", values=values)

    def on_closing(self):
        self.master.experiment_index =  self.index


class GraphFrame(Tk.Frame):
    def __init__(self, master, **key):
        Tk.Frame.__init__(self, master, **key)
        self.master = master
        self.key = key
        self.once = False
        self.saved = True
        self.sf:SidePanel = None

        #ツールバーの作成
        self.create_tool_bar()
        #サイドパネルの作成
        self.create_side_panel()
        #グラフ描画範囲の作成
        self.create_graph_area()

    def create_tool_bar(self):
        frame_tool_bar = Tk.Frame(self.master, borderwidth = 2, relief = Tk.SUNKEN)

        button1 = Tk.Button(frame_tool_bar, text = "更新", width = 5, command = self.update)
        button2 = Tk.Button(frame_tool_bar, text = "保存", width = 5, command = self.save)
        button3 = Tk.Button(frame_tool_bar, text = "リセット", width = 5, command=self.reset)
        button4 = Tk.Button(frame_tool_bar, text = "データ選択", width = 5, command=self.select_experiment)

        button1.pack(side = Tk.LEFT)
        button2.pack(side = Tk.LEFT)
        button3.pack(side = Tk.LEFT)
        button4.pack(side = Tk.LEFT)

        frame_tool_bar.pack(fill = Tk.X)

    def update(self):
        if(not self.once):
            return
        self.experiment.gS = self.sf.export_gS()
        if(self.experiment.draw_graph()):
            self.fig_canvas.get_tk_widget().pack_forget()
            self.fig_canvas = FigureCanvasTkAgg(self.experiment.fig, self.frame_graph_area)        
            self.fig_canvas.get_tk_widget().pack(anchor=Tk.NW)
        self.fig_canvas.draw()
        self.saved = False
        self.sf.import_gS(self.experiment.gS)
        return

    def save(self):
        if(not self.once):
            return
        # ファイルを保存するダイアログ
        filename = filedialog.asksaveasfilename(
            title="名前を付けて保存",
            filetypes=[("PNG", ".png"), ("JPEG", ".jpg"), ("Tiff", ".tif")],
            initialdir=os.getcwd(),  # カレントディレクトリ
            defaultextension="png"
        )
        # 同名のファイルが存在する場合に警告ウィンドウを表示
        if os.path.exists(filename):
            result = messagebox.askquestion("上書きの警告", "同名のファイルが存在します。上書きしますか？", icon='warning')
            if result != 'yes':
                return
            
        self.experiment.fig.savefig(filename)
        self.saved = True
        return
    
    def reset(self):
        if(not self.once):
            return
        return      

    def select_experiment(self):
        if(not self.once):
            return
        #現在のグラフがセーブされていない場合，警告を表示
        if(not self.saved):
            result = messagebox.askquestion("グラフ破棄の警告", "現在表示されているグラフがまだ保存されていません．\n新たなファイルをロードすると現在のグラフは削除されます．\n新たなファイルをロードしますか？", icon='warning')
            if result != 'yes':
                return
        gS = self.experiment.gS
        index = self.experiment_index
        window = ExperimentSelect(master=self)
        self.wait_window(window)
        if(index==self.experiment_index):
            return
        self.experiment = self.experiment_list[self.experiment_index]
        self.experiment.gS = gS
        self.experiment.draw_graph()

        #一度フレームの内部をリセットする．
        for parent in [self.frame_graph_area, self.frame_side_panel]:
            for widget in parent.winfo_children():
                widget.destroy()

        #グラフは伸縮させずにフレームの左上から配置
        self.fig_canvas = FigureCanvasTkAgg(self.experiment.fig, master=self.frame_graph_area)
        self.fig_canvas.draw()
        self.fig_canvas.get_tk_widget().pack(anchor=Tk.NW)

        #サイドパネルは事前に配置したフレームに敷き詰めて配置
        self.sf = SidePanel(self.frame_side_panel, self.experiment, self.fig_canvas)
        self.sf.pack(fill=Tk.BOTH, expand=True)

        #SidePanel内の全てのウィジェットに対して関数を埋め込む
        self.sf.bind_command()
        self.saved = False
        


    def create_side_panel(self):
        percentage = 30
        width = int(self.master.winfo_screenwidth() * percentage / 100)
        self.frame_side_panel = Tk.Frame(self.master,width=width, borderwidth=2, relief=Tk.SUNKEN)
        self.frame_side_panel.pack(side = Tk.RIGHT, fill = Tk.Y)
    
    def create_graph_area(self):
        '''グラフエリア'''
        #枠組みになるフレームのみ作成する
        self.frame_graph_area = Tk.Frame(self.master, bg="#ADD8E6")

        label = Tk.Label(self.frame_graph_area, text = "ツールバーの ファイル -> 開く から\nファイルを選択してください", font=("Arial", 16))
        label.pack(fill=Tk.BOTH, expand=True)

        self.frame_graph_area.pack(fill=Tk.BOTH, expand=True)

    def load(self, path):
        #現在のグラフがセーブされていない場合，警告を表示
        self.once=True
        if(not self.saved):
            result = messagebox.askquestion("グラフ破棄の警告", "現在表示されているグラフがまだ保存されていません．\n新たなファイルをロードすると現在のグラフは削除されます．\n新たなファイルをロードしますか？", icon='warning')
            if result != 'yes':
                return

        #実験データの読み取り
        try:
            experiment_list = get_plateReader_data.getDataForGraphEditor(path)
        except:
            messagebox.showwarning("警告", "データが正常に読み取れませんでした．\nファイルの読み取り形式を確認してください．")
            return
        self.experiment_list:list[Experiment] = experiment_list
        self.experiment_index = 0
        self.experiment = self.experiment_list[self.experiment_index]
        self.experiment.draw_graph()

        #一度フレームの内部をリセットする．
        for parent in [self.frame_graph_area, self.frame_side_panel]:
            for widget in parent.winfo_children():
                widget.destroy()

        #グラフは伸縮させずにフレームの左上から配置
        self.fig_canvas = FigureCanvasTkAgg(self.experiment.fig, master=self.frame_graph_area)
        self.fig_canvas.draw()
        self.fig_canvas.get_tk_widget().pack(anchor=Tk.NW)

        #サイドパネルは事前に配置したフレームに敷き詰めて配置
        self.sf = SidePanel(self.frame_side_panel, self.experiment, self.fig_canvas)
        self.sf.pack(fill=Tk.BOTH, expand=True)

        #SidePanel内の全てのウィジェットに対して関数を埋め込む
        self.sf.bind_command()
        self.saved = False



class Frame(Tk.Frame):
    def __init__(self, master = None):
        Tk.Frame.__init__(self, master)
        self.master.title("plate reader analyzer")
        
        self.master.state("zoomed")
        self.master.resizable(False, False)

        # メニューの作成
        self.create_menu()
        # ステータスバーの作成
        self.create_status_bar()
        # サイドパネルとグラフ描画エリア
        self.create_graph_frame()

    def create_menu(self):
        menu_bar = Tk.Menu(self)
 
        file_menu = Tk.Menu(menu_bar, tearoff = Tk.OFF)
        menu_bar.add_cascade(label="ファイル", menu = file_menu) 

        file_menu.add_command(label = "開く", command = self.menu_open_click, accelerator = "Ctrl+O")
        file_menu.add_separator() # セパレータ
        file_menu.add_command(label = "終了", command = self.master.destroy)
        # ショートカットの設定
        menu_bar.bind_all("Ctrl+M", self.menu_open_click)

        # 親のメニューに設定
        self.master.config(menu = menu_bar)

    def menu_open_click(self):
        path = filedialog.askopenfilename(title="ファイル選択", filetypes=[("Excel File","*.xlsx")])
        if(path):
            self.graph_frame.load(path)

    def create_status_bar(self):
        '''ステータスバー'''
        frame_status_bar = Tk.Frame(self.master, borderwidth = 2, relief = Tk.SUNKEN)

        self.label1 = Tk.Label(frame_status_bar, text = "ステータスラベル１")
        self.label2 = Tk.Label(frame_status_bar, text = "ステータスラベル２")

        self.label1.pack(side = Tk.LEFT)
        self.label2.pack(side = Tk.RIGHT)

        frame_status_bar.pack(side = Tk.BOTTOM, fill = Tk.X)

    def create_graph_frame(self):
        self.graph_frame = GraphFrame(self.master)

if(__name__ == "__main__"):
    f = Frame()
    f.pack()
    f.mainloop()