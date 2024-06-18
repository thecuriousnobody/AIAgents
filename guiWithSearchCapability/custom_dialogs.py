import tkinter as tk
from tkinter import ttk

class LargeTextInputDialog(tk.Toplevel):
    def __init__(self, parent, title=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        
        if title:
            self.title(title)
        
        self.result = None
        
        self.label = ttk.Label(self, text="Enter your search query relevant to the subject matter:")
        self.label.pack(side="top", fill="x", pady=10)

        self.text_frame = ttk.Frame(self)
        self.text_frame.pack(fill="both", expand=True)

        self.text = tk.Text(self.text_frame, wrap="word", height=10, width=50)
        self.text.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.text_frame, command=self.text.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text.config(yscrollcommand=self.scrollbar.set)

        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(pady=10)

        self.ok_button = ttk.Button(self.button_frame, text="OK", command=self.on_ok)
        self.ok_button.pack(side="left", padx=5)

        self.cancel_button = ttk.Button(self.button_frame, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side="left", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.geometry("400x300")

    def on_ok(self):
        self.result = self.text.get("1.0", "end-1c")
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()
