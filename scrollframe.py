import tkinter as tk
import tkinter.ttk as ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, bar_x = True, bar_y = True, **key):
        super().__init__(container, **key)
        self.canvas = tk.Canvas(self)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.scrollable_frame.bind("MouseWheel", self.mouse_y_scroll)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        if bar_y:
            self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.scrollbar_y.pack(side=tk.RIGHT, fill="y")
            self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        if bar_x:
            self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            self.scrollbar_x.pack(side=tk.BOTTOM, fill="x")
            self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)

    def mouse_y_scroll(self, event):
        if(event.delta > 0):
            self.canvas.yview_scroll(-1, "units")
        elif(event.delta < 0):
            self.canvas.yview_scroll(1, "units")

    def bind_command(self):
        self._bind_to_children(self, "<MouseWheel>", self.mouse_y_scroll)

    def _bind_to_children(self, parent:tk.Widget, sequence, func, add=True):
        children = parent.winfo_children()
        for child in children:
            self._bind_to_children(child, sequence, func, add)
        parent.bind(sequence, func, add)



