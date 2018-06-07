#
# Created 7th June 2018
# Current Version: 1.00
#
# Purpose: Framework for creating custom widgets used for battleships
# - Grid (8 x 8, 10 x 10)
# - Buttons
# - Progress Bars (vertical / horizontal)
# -
#

import tkinter as tk


### Main window object ###
class WindowObj(tk.Frame):
    def __init__(self, root):
        super().__init__(root)

        self.pack()
        self["width"] = 600
        self["height"] = 400

### Battleship grids ###
class CustomGrid(tk.Canvas):
    def __init__(self, parent):
        super().__init__(parent)


### Button blueprint (different types incl.) ###
class CustomButton(tk.Frame):
    def __init__(self, parent, text):
        super().__init__(parent)


if __name__ == "__main__":
    root = tk.Tk()

    root.wm_title("Battleships V1.00")
    root.wm_resizable(0, 0)

    window = WindowObj(root)

    #button = CustomButton(window, text="Good morning America!")
    #button.pack()

    root.mainloop()
