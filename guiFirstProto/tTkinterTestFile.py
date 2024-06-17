import tkinter as tk
from tkinter import ttk
print(tk.TkVersion)

root = tk.Tk()
button = ttk.Button(root, text="Click Me")
button.pack()
root.mainloop()