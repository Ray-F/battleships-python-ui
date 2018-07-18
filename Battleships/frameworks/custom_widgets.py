# # # # # # # # # # # # # # # # # # # #
#
# Created 11th June 2018, Raymond Feng
#
# Current Version: 1.00
# Updated: 14th June 2018
#
# Purpose: Framework for creating custom widgets used for battleships
# - Grid (10 x 10)
# - Buttons
# - Progress Bars (vertical / horizontal)
#
# # # # # # # # # # # # # # # # # # # #


import tkinter as tk
import copy


### Multi-function coordinate controller ###


class CoordUtils(object):

    # Coordinate given in (x, y) or alpha-num form, returned in (x, y) form
    @classmethod
    def get_surrounding_coords(cls, coord):
        surrounding_coords = []

        sides = ['left', 'right', 'top', 'bottom']

        for side in sides:
            side_coord = CoordUtils.get_side_coord(coord, side)

            if side_coord: surrounding_coords.append(side_coord)

        return surrounding_coords

    # Get the coordinate in each position, returned in (x, y) form
    @classmethod
    def get_side_coord(cls, coord, side):
        if type(coord) is not tuple:
            coord = CoordUtils.convert_type(coord)

        x, y = coord[0], coord[1]

        if side == 'left' and x != 1:
            return (x - 1, y)

        elif side == 'right' and x != 10:
            return (x + 1, y)

        elif side == 'top' and y != 1:
            return (x, y - 1)

        elif side == 'bottom' and y != 10:
            return (x, y + 1)

        # Conditions for else... either side is not defined, OR no coordinate
        else:
            return None



    # Converts input coordinate into a different form.
    # A -> 1    1 -> A      A1 -> (1, 1)    (1, 1) –> A1
    @classmethod
    def convert_type(cls, letter):
        CHAR = list("ABCDEFGHIJ")

        NUM = list("123456789") + ["10"]


        # If coord in alpha-num form (i.e D1)
        if str(letter)[0].isalpha() and letter[-1].isdigit():
            coord_x = CoordUtils.convert_type(letter[0])
            coord_y = "".join(letter[1:])

            return (int(coord_x), int(coord_y))

        # If coord in (x, y) form
        elif type(letter) is tuple:
            return (CoordUtils.convert_type(letter[0]) + str(letter[1]))

        # If given single letter (i.e A)
        elif str(letter).isalpha():
            return NUM[CHAR.index(letter.upper())]

        # If letter is number
        else:
            return CHAR[letter - 1]

### Creates a rounded rectangle, with corner dimensions format ###
#
# – canvas defines parent body
# – x1, y1 (first corner), x2, y2 (second corner), r defines corner radius
# – colour is for the shape's colour
# – tag is for any special tags
# – bottom_hidden=True makes no rounding on bottom border
#
def rounded_rect(canvas, x1, y1, x2, y2, r, colour, tag=None, bottom_hidden=False):

    # All the elements of
    elements = []

    if str(r).isdigit():
        rad = (r, r, r, r)
    elif len(r) == 2:
        rad = (r[0], r[0], r[1], r[1])
    elif len(r) == 4:
        rad = (r[0], r[1], r[2], r[3])

    # Top Left
    elements.append(canvas.create_arc(x1, y1, x1+r, y1+r,
                                      start=90, extent=90, style=tk.PIESLICE,
                                      fill=colour, outline=colour))

    # Top Right
    elements.append(canvas.create_arc(x2-r, y1, x2, y1+r,
                                      start=0, extent=90, style=tk.PIESLICE,
                                      fill=colour, outline=colour))

    # Bottom Left
    elements.append(canvas.create_arc(x1, y2-r, x1+r, y2,
                                      start=180, extent=90, style=tk.PIESLICE,
                                      fill=colour, outline=colour))

    # Bottom Right
    elements.append(canvas.create_arc(x2-r, y2-r, x2, y2,
                                      start=270, extent=90, style=tk.PIESLICE,
                                      fill=colour, outline=colour))

    elements.append(canvas.create_rectangle(x1+r/2, y1, x2-r/2+1, y2+1, fill=colour, width=0))
    elements.append(canvas.create_rectangle(x1, y1+r/2, x2+1, y2-r/2+1, fill=colour, width=0))

    if bottom_hidden:
        bottom_edge = canvas.create_rectangle(x1, y2 - r/2,
                                              x2, y2 + r/2,
                                              fill=colour, width=0)
        elements.append(bottom_edge)

    return elements


### Class of all the colours used with colour themes ###
#
# – default colour scheme can be accessed theme = Colour("default"), theme.GRAY... etc
#
class Colours(object):
    def __init__(self, theme):

        if theme == "default":
            self.WHITE = "#FFFFFF"

            self.GRAY_BRIGHT = "#eee"
            self.GRAY_LIGHT = "#D0D0D0"
            self.GRAY = "#9E9E9E"
            self.GRAY_DARK = "#707070"
            self.GRAY_BLACK = "#505050"

            self.RED = "#FF4F4F"
            self.RED_DARK = "#A42F2F"

            self.GOLD = "orange"
            self.GOLD_DARK = "orange3"

            self.ORANGE = "#FCB659"
            self.ORANGE_DIM = "#DCA649"
            self.ORANGE_DARK = "#AA5629"

            self.YELLOW = "#FFF874"

            self.GREEN = "#5ED88F"
            self.GREEN_DIM = "#4EB878"
            self.GREEN_DARK = "#3E7054"

            self.CYAN = "#00A1BB"
            self.CYAN_DARK = "#00819B"

            self.TURQUOISE = "#94C7C0"
            self.TURQUOISE_DARK = "#74A7A0"

            self.BLUE = "#20B8CC"

            self.GRADIENT = [self.RED, self.ORANGE,
                             self.YELLOW, self.GREEN]


### A progress bar ###
class ProgressBar(tk.Canvas):
    def __init__(self, parent, direction="up", colours=("#FF4F4F", "#A42F2F"),
                 bg_canvas="white", multiplier=2, gradient=False):
        super().__init__(parent)

        self.theme = Colours("default")

        self.direction = direction
        self.multiplier = multiplier
        self.gradient = gradient

        self.background = colours[0]
        self.foreground = colours[1]

        self.percentage = 0

        self.bar_height = round(self.multiplier * 205)

        self.previous = None

        self["highlightthickness"] = 0
        self["bg"] = bg_canvas
        self["width"] = self.multiplier * 60
        self["height"] = self.bar_height + 50

        self.update_canvas()

    def update_canvas(self):

        if self.previous:
            self.delete('all')

        colour = self.theme.GRADIENT[round(self.percentage/25)] if self.gradient else self.background

        if self.direction == "down":
            self.bar = rounded_rect(self, 0, self.bar_height - (self.bar_height/100 * (100 - self.percentage)),
                                    int(self["width"]) - 2,
                                    int(self["height"]), 40,
                                    colour)
        else:
            self.bar = rounded_rect(self, 0, self.bar_height - (self.bar_height/100 * self.percentage),
                                    int(self["width"]) - 2,
                                    int(self["height"]), 40,
                                    colour)

        self.create_text(int(self["width"])/2, int(self["height"]) - 10,
                         text="{}%".format((self.percentage if self.direction == "up" else (100 - self.percentage))),
                         fill=self.foreground, font=("TW Cen MT", 20, "bold"), anchor="s")

        self.previous = True

    def set_percentage(self, new_percentage):
        self.percentage = new_percentage

        self.update_canvas()


### A popup that disappears in time ###
class Popup(tk.Canvas):
    def __init__(self, parent, text, bg, fg, fill=False, subtext=None):
        theme = Colours("default")
        super().__init__(parent)

        self.place(x=parent.winfo_width()/2, y=parent.winfo_height()/2, anchor='center')

        self["width"] = parent.winfo_width()

        self["height"] = parent.winfo_height() if fill else 100
        self["bg"] = bg

        main_font = ("Tw Cen MT", 28, "bold") if subtext else ("Tw Cen MT", 24)

        self.create_text(int(self["width"]) / 2, int(self["height"]) / 2 - (12 if subtext else 0),
                         text=text, fill=fg, font=main_font, anchor='center')

        self.create_text(int(self["width"]) / 2, int(self["height"]) / 2 + 12,
                         text=subtext if subtext else "", fill=fg, font=("Tw Cen MT", 16), anchor='center')


        parent.after(5000 if fill else 2000, self.destroy)


### A ship to be placed on a canvas ###
class Ship(object):
    def get_name(ship_length):
         return {2: 'Destroyer',
                 3: 'Cruiser',
                 4: 'Battleship',
                 5: 'Carrier'}.get(ship_length, "Yellow Submarine")

    def __init__(self, parent_canvas, x1, y1, length=4, colour=Colours("default").WHITE, dir='h'):

        self.parent = parent_canvas
        self.theme = Colours("default")
        self.colour = colour

        self.name = Ship.get_name(length)

        self.dir = dir

        # Length is in square length units, width is in pixels wide
        self.length = length
        self.width = 35

        self.binded_func = None
        self.selected = False

        # 2 Boat: 60px    3 Boat: 100px     4 Boat: 140px       5 Boat: 180px
        x_dimension = (60 + 40 * (length - 2)) if self.dir == 'h' else self.width
        y_dimension = (60 + 40 * (length - 2)) if self.dir == 'v' else self.width

        self.elements = rounded_rect(parent_canvas, x1, y1,
                                     x1 + x_dimension,
                                     y1 + y_dimension,
                                     55, colour=colour)

        self.text = parent_canvas.create_text(x1 + int(x_dimension/2), y1 + int(y_dimension/2), anchor='center',
                                              text=self.length, fill=self.colour, font=('Tw Cen MT', 12))

        for canvas_obj in self.elements + [self.text]:
            self.parent.tag_bind(canvas_obj, "<Button-1>", lambda event: self.click(event))
            self.parent.tag_bind(canvas_obj, "<Enter>", lambda event: self.hover(event))
            self.parent.tag_bind(canvas_obj, "<Leave>", lambda event: self.unhover(event))

    def bind_to_click(self, function):
        self.binded_func = function

    def click(self, event):
        if self.selected == True:
            return

        for canvas_obj in self.elements:
            self.parent.itemconfigure(canvas_obj, fill=self.theme.GRAY)
            self.parent.itemconfigure(canvas_obj, outline=self.theme.GRAY)

        self.selected = True
        self.binded_func(self)

    def hover(self, event):
        if self.selected == True:
            return

        self.parent.itemconfigure(self.text, fill=self.theme.GRAY_BLACK)

        for canvas_obj in self.elements:
            self.parent.itemconfigure(canvas_obj, fill=self.theme.GRAY_LIGHT)
            self.parent.itemconfigure(canvas_obj, outline=self.theme.GRAY_LIGHT)

    def unhover(self, event):
        if self.selected == True:
            return

        self.parent.itemconfigure(self.text, fill=self.colour)

        for canvas_obj in self.elements:
            self.parent.itemconfigure(canvas_obj, fill=self.colour)
            self.parent.itemconfigure(canvas_obj, outline=self.colour)


### Battleship grids for setup and game ###
class CustomGrid(tk.Canvas):
    def __init__(self, parent, progress_bar=None, multiplier=3, disabled=False,
                 colours="grey", bg_canvas="white", bottom_hidden=False,
                 is_game_board=True, game=None, owner=None):
        super().__init__(parent)

        # Multiplier for scaling grid
        self.multiplier = multiplier
        self.theme = Colours("default")

        self.background = self.theme.GRAY
        self.foreground = self.theme.GRAY_LIGHT
        self["highlightthickness"] = 0

        self["bg"] = bg_canvas

        # Defines the dimensions of the grid
        self["width"], self["height"] = 110 * self.multiplier, 110 * self.multiplier

        # Grey rounded container, aesthetic purposes
        self.container = rounded_rect(self, 0, 0, int(self["width"]), int(self["height"]),
                                      10 * self.multiplier, colour=self.background, bottom_hidden=bottom_hidden)


        # Defining a linked progress bar, setting original position to full
        self.linked_progress_bar = progress_bar
        if self.linked_progress_bar: self.linked_progress_bar.set_percentage(0)

        self.linked_percentage = None
        if self.linked_percentage: self.linked_percentage["text"] = "0.00%"

        # Determines whether or not the board is used for setup or game
        self.is_game_board = is_game_board

        # Determines whether user interaction is enabled
        self.disabled = disabled

        # List of all squares (with coordinates) on grid, appended to in update_canvas()
        self.squares = []

        # For setting up the board
        if is_game_board:
            self.game = game
            self.owner = owner

            if self.owner == 'player':
                self.ships = self.game.player_ships
                self.remaining_ships = self.game.player_remaining_ships
                self.hit_spaces = self.game.player_board_hit

            else:
                self.ships = self.game.computer_ships
                self.remaining_ships = self.game.computer_remaining_ships
                self.hit_spaces = self.game.computer_board_hit

        else:
            self.selection_length = 0
            self.selection_dir = 'h'

            # Structured as [ship1 ... shipn], for each ship [coord1 ... coordn], like self.ships
            self.selection = []

        self.update_canvas()


    def update_canvas(self, show_hidden_ships=False):

        # Deletes existing squares
        self.delete("square")
        self.squares = []

        for y in range(0, 10):
            for x in range(0, 10):

                # shifts every square in grid to center grid
                shift = 10 if self.multiplier == 2 else 20

                # determines spacing of grid squares
                spacing = 1

                # Each object will contain the canvas obj and the coordinate (x, y)
                square_colour = self.foreground
                tag = "square"

                if self.is_game_board:
                    # For every ship on the board, make that square have an "occupied" tag
                    # for identification for mouse click event.
                    for ship in self.ships:
                        if (x + 1, y + 1) in [CoordUtils.convert_type(alpha_coord) for alpha_coord in ship]:
                            tag = ("square", "occupied")

                rect = (self.create_rectangle(self.multiplier * 10 * x + spacing + shift,
                                              self.multiplier * 10 * y + spacing + shift,
                                              self.multiplier * 10 * (x + 1) + shift,
                                              self.multiplier * 10 * (y + 1) + shift,
                                              fill=square_colour, width=0, tags=tag), (x + 1, y + 1))

                if show_hidden_ships and len(tag) == 2 and tag[1] == "occupied":
                    self.itemconfigure(rect[0], fill=self.theme.GREEN)


                # Adds the letter coord on the first row
                textrow = (self.create_text(self.multiplier * 10 * x + self.multiplier * 13,
                                           shift + (7 if self.multiplier == 2 else 12),
                                           text=CoordUtils.convert_type(x + 1), font=("Tw Cen Mt", self.multiplier * 3 + 1),
                                           fill=self.theme.GRAY_DARK)) if (rect[1][1] == 1) else None

                # Adds the integer coord on the first column
                textcol = (self.create_text(self.multiplier * 7 + 2,
                                           self.multiplier * 10 * y + self.multiplier * 13,
                                           text=str(y + 1), font=("Tw Cen Mt", self.multiplier * 3 + 1),
                                           fill=self.theme.GRAY_DARK)) if (rect[1][0] == 1) else None

                # Adds each object (canvas object w/ coord) to self.squares
                self.squares.append(rect)

                if self.is_game_board:
                    # Binds click, hover, unhover events
                    element_arr = [rect[0]]

                    if textrow: element_arr.append(textrow)
                    if textcol: element_arr.append(textcol)

                    for element in element_arr:
                        self.tag_bind(element, "<Button-1>", lambda event, arg=rect: self.hit(event, arg))
                        self.tag_bind(element, "<Enter>", lambda event, arg=rect: self.hover(event, arg))
                        self.tag_bind(element, "<Leave>", lambda event, arg=rect: self.unhover(event, arg))

                else:
                    element_arr = [rect[0]]

                    if textrow: element_arr.append(textrow)
                    if textcol: element_arr.append(textcol)

                    for element in element_arr:
                        self.tag_bind(element, "<Button-1>", lambda event, rect=rect: self.place_ship(event, rect))
                        self.tag_bind(element, "<Button-2>", lambda event, rect=rect: self.rotate_selection(event, rect))
                        self.tag_bind(element, "<Enter>", lambda event, rect=rect: self.hover_selection(event, rect))
                        self.tag_bind(element, "<Leave>", lambda event, rect=rect: self.unhover_selection(event, rect))

    # Find the "rect" object (Canvas elements, (x, y)) based on a given (x, y) coord
    def coord_to_rect(self, coord):
        for rect in self.squares:
            if rect[1] == coord:
                return rect

    # Colour each coordinate, coordinate given in (x, y) – frontend
    def colour_square(self, coord, fill):
        self.itemconfigure(self.coord_to_rect(coord)[0], fill=fill)

    ## FOLLOWING 4 DEFINITIONS ARE EVENT HANDLERS FOR SETUP ##

    # Places a ship based on the selection length
    def place_ship(self, event, rect):
        if self.selection_length == 0:
            return

        selection_coords = []

        for i in range(self.selection_length):
            if self.selection_dir == 'h':
                selection_coords.append((rect[1][0] + i, rect[1][1]))
            else:
                selection_coords.append((rect[1][0], rect[1][1] + i))

        selection_rect = [self.coord_to_rect(coord) for coord in selection_coords]

        for rect in selection_rect:
            if rect == None:
                break

            if self.itemcget(rect[0], "fill") != self.theme.GRAY_BRIGHT:
                break

        else:
            for coord in selection_coords:
                self.colour_square(coord, self.theme.GREEN)

            selection = []
            for x, y in selection_coords:
                selection.append("{}{}".format(CoordUtils.convert_type(x), y))

            self.selection.append(selection)

            self.selection_length = 0
            self.selection_dir = 'h'

    # Changes ship placement to be horizontal/vertical
    def rotate_selection(self, event, rect):
        self.unhover_selection(None, rect)
        self.selection_dir = ('v' if self.selection_dir == 'h' else 'h')
        self.hover_selection(None, rect)

    # Lightens squares where ship will be placed
    def hover_selection(self, event, rect):

        selection_coords = []

        for i in range(self.selection_length):
            if self.selection_dir == 'h':
                selection_coords.append((rect[1][0] + i, rect[1][1]))
            else:
                selection_coords.append((rect[1][0], rect[1][1] + i))

        selection_rect = [self.coord_to_rect(coord) for coord in selection_coords]

        for rect in selection_rect:
            if rect == None:
                break
            if self.itemcget(rect[0], "fill") != self.foreground:
                break
        else:
            for coord in selection_coords:
                self.colour_square(coord, self.theme.GRAY_BRIGHT)

    # Opposite of hover_selection
    def unhover_selection(self, event, rect):
        selection_coords = []

        for i in range(self.selection_length):
            if self.selection_dir == 'h':
                selection_coords.append((rect[1][0] + i, rect[1][1]))
            else:
                selection_coords.append((rect[1][0], rect[1][1] + i))

        selection_rect = [self.coord_to_rect(coord) for coord in selection_coords]

        for rect in selection_rect:
            if rect == None:
                continue

            if self.itemcget(rect[0], "fill") == self.theme.GRAY_BRIGHT:
                self.colour_square(rect[1], self.foreground)

    # Event handler when square is clicked
    def hit(self, event, rect, override=False):
        if self.itemcget(rect[0], "fill") == self.theme.GRAY_BRIGHT or override:

            game_control = self.game.game_control(CoordUtils.convert_type(rect[1]), self.owner)

            # Nothing was hit
            if len(game_control) == 1:
                self.colour_square(rect[1], self.theme.BLUE)
                self.disabled = True

            # A ship square was hit
            elif len(game_control) == 3:

                name = Ship.get_name(len(game_control[2]))

                # Ship was sunk
                if game_control[1]:
                    [self.colour_square(CoordUtils.convert_type(coord), self.theme.RED) for coord in game_control[2]]

                # Ship wasn't sunk
                else:
                    self.colour_square(rect[1], self.theme.GOLD)

                # Total number of ship squares
                total_spaces = sum([len(ship) for ship in self.ships])

                # Number of ship squares remaining (unhit)
                remaining_spaces = sum([len(ship) for ship in self.remaining_ships])

                # Increments the progress bar, note: percentage is the percentage of ships sunk
                if self.linked_progress_bar:
                    new_percent = round((1 - remaining_spaces/total_spaces) * 100)
                    self.linked_progress_bar.set_percentage(new_percent)

                if self.linked_percentage:
                    new_percent = (1 - remaining_spaces/total_spaces) * 100

                    roundings = ["{:.2f}%".format(round(new_percent)), "{:.1f}%".format(round(new_percent)), "100%"]

                    self.linked_percentage["text"] = roundings[0] if new_percent < 10 else roundings[1]

                    if round(new_percent) == 100:
                        self.linked_percentage["text"] = roundings[2]

    # When a square is hovered – frontend
    def hover(self, event, rect):
        if self.disabled == False and self.itemcget(rect[0], "fill") == self.theme.GRAY_LIGHT:
            self.colour_square(rect[1], self.theme.GRAY_BRIGHT)

    # When a square is unhovered – frontend
    def unhover(self, event, rect):
        if self.itemcget(rect[0], "fill") == self.theme.GRAY_BRIGHT:
            self.colour_square(rect[1], self.theme.GRAY_LIGHT)

    # Show all hidden ships on board
    def show_hidden_ships(self):
        self.update_canvas(show_hidden_ships=True)


### Blueprint for rounded buttons with built in event handlers ###
class CustomButton(tk.Frame):
    def __init__(self, parent, text, fg=None, colour=None, active=None,
                       width=200, height=60, bg_canvas='white', font=("Tw Cen MT", 20), align="center"):
        super().__init__(parent)

        if None in [fg, colour, active]:
            self.fg = "red4"
            self.colour = "yellow"
            self.active_colour = "orange"

        self.fg = fg
        self.colour = colour
        self.active_colour = active
        self.text = text
        self.click_func = None

        self.width = width
        self.height = height

        self.canvas = tk.Canvas(self, width=self.width + 2, height=self.height + 2,
                                bg=bg_canvas, highlightthickness=0)

        self.vert_button = [tk.Frame(self, width=self.width-20, height=8, bg=colour),
                                tk.Frame(self, width=self.width-20, height=8, bg=colour)]

        self.hori_button = tk.Frame(self, width=self.width-4, height=self.height-20, bg=colour)

        self.label = tk.Label(self.hori_button, text=self.text,
                              bg=self.colour, font=font, fg=self.fg)

        self.hori_button.pack_propagate(0)

        if align == "center":
            self.label.place(x=(self.width-4)/2, y=(self.height-20)/2, anchor="center")
        elif align == "left":
            self.label.place(x=20, y=(self.height-20)/2, anchor="w")

        self.elements = rounded_rect(self.canvas, 1, 1, self.width, self.height, 20, colour)

        for btn in [self.hori_button, self.label]:
            btn.bind("<Enter>", self.hover)
            btn.bind("<Leave>", self.unhover)
            btn.bind("<Button-1>", self.click)

        self.canvas.pack(side='left')

        self.canvas.create_window(12, 5, window=self.vert_button[0], anchor="nw")
        self.canvas.create_window(12, 52, window=self.vert_button[1], anchor="nw")
        self.canvas.create_window(5, 12, window=self.hori_button, anchor="nw")

    def hover(self, event):
        for btn in self.vert_button + [self.hori_button, self.label]:
            btn["bg"] = self.active_colour

        for el in self.elements:
            self.canvas.itemconfig(el, fill=self.active_colour)
            self.canvas.itemconfig(el, outline=self.active_colour)

    def unhover(self, event):
        for btn in self.vert_button + [self.hori_button, self.label]:
            btn["bg"] = self.colour

        for el in self.elements:
            self.canvas.itemconfig(el, fill=self.colour)
            self.canvas.itemconfig(el, outline=self.colour)

    def bind_to_click(self, func):
        self.click_func = func

    def click(self, event):
        if self.click_func:
            self.click_func()
