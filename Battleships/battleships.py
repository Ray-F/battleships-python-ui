import tkinter as tk
import random
import datetime

from frameworks.custom_widgets import *


theme_selection = "default"


def switch_screen(screen, args=None):

    global current_screen

    if current_screen != None: current_screen.destroy()

    if screen == 'splash': current_screen = SplashScreen(root)

    if screen == 'setup': current_screen = SetupWindow(root)

    if screen == 'game': current_screen = GameWindow(root, args)

    current_screen.pack()

    white = tk.Frame(root, bg='white', width=1000, height=1000)
    white.place(x=0, y=0, anchor='nw')

    root.after(50, white.destroy)


### Loading screen to access new or saved game ###
class SplashScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        theme = Colours(theme_selection)

        self.bar = tk.Frame(self, width=800, height=25, bg=theme.GRAY_DARK)
        self.bar.pack(side='top', pady=(60, 0))

        self.title = tk.Label(self, text="BATTLESHIPS", font=("Tw Cen MT", 100, "bold"), fg=theme.GRAY_DARK)
        self.title.pack(side='top', padx=(25, 250), pady=(20, 10))

        self.main_frame = tk.Frame(self, width=750, height=320, bg=theme.WHITE)
        self.main_frame.pack(side='bottom')

        self.main_frame.grid_propagate(0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

        self.info_frame = tk.Canvas(self.main_frame, width=480, height=320, highlightthickness=0)
        self.info_frame.grid(column=0, row=0, sticky='nw')

        rules = ['>bHello World!',
                 'My name is Raymond Feng',
                 'The rules of this game are simple.',
                 'Make sure to follow these rules.',
                 ">lHelp me Harshal.",
                 ">mHelp me!"]

        rules_frame = tk.Frame(self.info_frame, width=400, height=280, bg=theme.GRAY_LIGHT)
        rounded_rect(self.info_frame, 0, 0, int(self.info_frame["width"]), 319, 50, colour=theme.GRAY_LIGHT)

        for line in rules:
            font = ("Tw Cen MT", 16)

            if line[:2] in [">b", ">m", ">l", ">s"]:

                font_types = {">b": ("Tw Cen MT", 24, "bold"),
                              ">m": ("Tw Cen MT", 30, "italic"),
                              ">l": ("Tw Cen MT", 20),
                              ">s": ("Tw Cen MT", 14)}

                font = font_types.get(line[:2], ("Tw Cen MT", 16))
                line_formatted = line[2:]
            else:
                line_formatted = line

            rules_text = tk.Label(rules_frame, text=line_formatted, font=font,
                                  bg=theme.GRAY_LIGHT)
            rules_text.pack()

        self.info_window = self.info_frame.create_window(int(self.info_frame['width'])/2, 160, window=rules_frame, anchor='center', tag='window')

        self.buttons_frame = tk.Frame(self.main_frame, width=256, height=int(self.main_frame["height"]))
        self.buttons_frame.grid(column=1, row=0, sticky='nw')
        self.buttons_frame.pack_propagate(False)

        new_game_button = CustomButton(self.buttons_frame, text="New Game", width=250, height=80,
                                       colour=theme.CYAN, fg=theme.WHITE, active=theme.CYAN_DARK)

        new_game_button.bind_to_click(lambda: switch_screen('setup'))
        new_game_button.place(x=0, y=-1, anchor='nw')

        load_button = CustomButton(self.buttons_frame, text="Load Saved", width=250, height=80,
                                   colour=theme.TURQUOISE, fg=theme.WHITE, active=theme.TURQUOISE_DARK)
        load_button.place(x=0, y=90, anchor='nw')

        self.close_button = CustomButton(self.buttons_frame, text="✘ ", width=80, height=60,
                                    colour=theme.RED, fg=theme.WHITE, active=theme.RED_DARK)

        self.close_button.place(x=251, y=int(self.main_frame["height"]), anchor="se")

        self.close_button.bind_to_click(lambda: root.destroy())

        def replace_rules(frame):
            self.info_frame.delete('window')
            self.info_frame.create_window(270, 160, window=frame, anchor='center', tag='window')

            self.close_button = CustomButton(self.buttons_frame, text="⏎ ", width=80, height=60,
                                        colour=theme.GOLD, fg=theme.WHITE, active=theme.GOLD_DARK)
            self.close_button.place(x=251, y=int(self.main_frame["height"]), anchor="se")

            self.close_button.bind_to_click(lambda: switch_screen('splash'))

        load_button.bind_to_click(lambda: replace_rules(SavesFrame(self.info_frame)))


### Frame within splash saves, inside the splash screen ###
class SavesFrame(tk.Frame):
    def __init__(self, parent):

        theme = Colours(theme_selection)
        super().__init__(parent)

        self["bg"] = theme.GRAY_LIGHT

        save_1 = tk.Frame(self, width=400, height=80)
        save_1.grid(column=0, row=0, pady=2)

        save_2 = tk.Frame(self, width=400, height=80)
        save_2.grid(column=0, row=1, pady=2)

        save_3 = tk.Frame(self, width=400, height=80)
        save_3.grid(column=0, row=2, pady=2)


### Board setup – Window ###
class SetupWindow(tk.Frame):
    ### NB: The SetupWindow frame is split into 3 main column areas.
    # The first column area is for the progress bar.
    # The second column area is for the main game grid and ships container
    # The third column area is for the display grid, as well as the game stats

    def __init__(self, parent):
        super().__init__(parent)

        theme = Colours(theme_selection)
        self.game = Game()

        ## Left container for the progress bar and text ##
        progress_container = tk.Frame(self, bg=theme.GRAY_LIGHT, height=570)
        progress_container.grid(column=0, row=0, sticky='n', pady=15)
        progress_container.pack_propagate(False)

        # Label for progress bar
        progress_label = tk.Label(progress_container, text="Battleships\nRemaining", font=("Tw Cen Mt", 24, "bold"),
                                  fg=theme.GRAY_DARK, bg=theme.GRAY_LIGHT)
        progress_label.pack(side='bottom', pady=(10, 20))

        # Actual progress bar
        self.progress_bar = ProgressBar(progress_container, direction="down",
                                        colours=(theme.GRAY, theme.GRAY_BLACK), bg_canvas=theme.GRAY_LIGHT)
        self.progress_bar.pack(side='bottom')

        # Linking progress bar width to bounding countainer (progress_container)
        progress_container["width"] = int(self.progress_bar["width"]) + 20


        ## Middle container for the grid and ships ##
        main_container = tk.Frame(self, bg=theme.WHITE)
        main_container.grid(column=1, row=0, padx=10, pady=15)

        self.main_grid = CustomGrid(main_container, multiplier=4,
                                    progress_bar=self.progress_bar, bottom_hidden=True, is_game_board=False)
        self.main_grid.pack()

        ships_container = tk.Canvas(main_container, width=int(self.main_grid["width"]), height=130,
                                    highlightthickness=0, bg=theme.GRAY_DARK)

        self.current_ship_selection = None

        def return_current_length(ship):
            if self.main_grid.selection_length != 0:
                self.current_ship_selection.selected = False
                self.current_ship_selection.unhover(None)

            self.main_grid.selection_length = ship.length
            self.main_grid.selection_dir = ship.dir
            self.current_ship_selection = ship

        self.ships = [Ship(ships_container, 40, 15, length=2, dir='v'),
                      Ship(ships_container, 90, 15, length=3, dir='v'),
                      Ship(ships_container, 140, 15, length=3, dir='v'),
                      Ship(ships_container, 220, 15, length=5),
                      Ship(ships_container, 220, 65, length=4)]

        ships_container.pack(pady=(0, 10))

        for ship in self.ships: ship.bind_to_click(return_current_length)


        ## Right container for the small grid and button/info display ##
        right_container = tk.Frame(self)
        right_container.grid(column=2, row=0, sticky='n', pady=15)

        small_grid_container = tk.Frame(right_container, bg=theme.GRAY_BLACK)
        small_grid_container.pack(side='top', pady=(0, 10))

        self.small_grid = CustomGrid(small_grid_container, multiplier=2, progress_bar=None, disabled=True,
                                     bottom_hidden=True, is_game_board=False)
        self.small_grid.pack(side='top')


        small_grid_info = tk.Frame(small_grid_container, width=220, height=40, bg=theme.GRAY_BLACK)
        small_grid_info.pack()
        small_grid_info.grid_propagate(0)

        left_text = tk.Label(small_grid_info, text="YOUR\nTERRITORY", justify='right',
                             font=("Tw Cen MT", 13, "bold"), fg=theme.WHITE, bg=theme.GRAY_BLACK)

        left_text.grid(column=0, row=0, sticky='w', padx=(5, 10))

        percentage_text = tk.Label(small_grid_info, text="–––– %",
                                   fg=theme.GRAY, bg=theme.GRAY_BLACK, font=("Tw Cen MT", 30, "bold"))
        percentage_text.grid(column=1, row=0, sticky='e')

        right_text = tk.Label(small_grid_info, text="HIT",
                              fg=theme.WHITE, bg=theme.GRAY_BLACK, font=("Tw Cen MT", 12, "bold"))
        right_text.grid(column=2, row=0, sticky='e', padx=(5, 0), pady=(14, 0))

        info_frame = tk.Frame(right_container, bg=theme.GRAY_LIGHT, width=220, height=230)
        info_frame.pack()

        info_frame.pack_propagate(0)

        def reset_board():
            self.main_grid.update_canvas()
            self.main_grid.selection = []
            self.main_grid.selection_length = 0
            self.main_grid.selection_dir = 'h'

            for ship in self.ships:
                ship.selected = False
                ship.unhover(None)

        reset_board_button = CustomButton(info_frame, text="RESET BOARD", height=40, width=200, align='center',
                                          colour=theme.ORANGE, fg=theme.ORANGE_DARK, active=theme.ORANGE_DIM,
                                          font=("Tw Cen MT", 20, "bold"), bg_canvas=theme.GRAY_LIGHT)
        reset_board_button.pack(pady=10)
        reset_board_button.bind_to_click(reset_board)

        def start_game():
            for ship in self.ships:
                if ship.selected == False:
                    popup = Popup(parent, text="All ships must be placed!", bg=theme.RED, fg="white")
                    break
            else:
                self.game.add_player_ships(self.main_grid.selection)

                computer_ships = [["G1", "G2", "G3", "G4", "G5"],
                                  ["A10", "B10", "C10", "D10"],
                                  ["C5", "D5", "E5"],
                                  ["I8", "I9", "I10"],
                                  ["J9", "J10"]]

                self.game.add_computer_ships(computer_ships)

                switch_screen('game', args=self.game)

        start_game_button = CustomButton(info_frame, text="GO!", height=150, width=200,
                                         colour=theme.GREEN, fg=theme.GREEN_DARK, active=theme.GREEN_DIM,
                                         font=("Tw Cen MT", 40, "bold"), bg_canvas=theme.GRAY_LIGHT)
        start_game_button.bind_to_click(start_game)
        start_game_button.pack(pady=(0, 10))

        control_frame = tk.Frame(right_container, bg=theme.GRAY_LIGHT, width=220, height=60)
        control_frame.pack(pady=10)

        back_button = CustomButton(control_frame, text="⏎ ", width=120, height=40,
                                   colour=theme.GOLD, fg=theme.WHITE, active=theme.GOLD_DARK,
                                   bg_canvas=theme.GRAY_LIGHT)
        back_button.place(x=10, y=51, anchor='sw')
        back_button.bind_to_click(lambda: switch_screen('splash'))

        close_button = CustomButton(control_frame, text="✘ ", width=70, height=40,
                                    colour=theme.RED, fg=theme.WHITE, active=theme.RED_DARK,
                                    bg_canvas=theme.GRAY_LIGHT)
        close_button.place(x=210, y=51, anchor="se")
        close_button.bind_to_click(lambda: root.destroy())


### The main "Game" Window ###
class GameWindow(tk.Frame):
    ### NB: The GameWindow frame is split into 3 main column areas.
    # The first column area is for the progress bar.
    # The second column area is for the main game grid and ships container
    # The third column area is for the display grid, as well as the game stats

    def __init__(self, parent, game):
        super().__init__(parent)

        theme = Colours(theme_selection)
        self.game = game

        ## Left container for the progress bar and text ##
        progress_container = tk.Frame(self, bg=theme.GRAY_LIGHT, height=570)
        progress_container.grid(column=0, row=0, sticky='n', pady=15)
        progress_container.pack_propagate(False)

        # Label for progress bar
        progress_label = tk.Label(progress_container, text="Opponent\nShips", font=("Tw Cen Mt", 24, "bold"),
                                  fg=theme.GRAY_BLACK, bg=theme.GRAY_LIGHT)
        progress_label.pack(side='bottom', pady=(10, 20))

        # Actual progress bar
        self.progress_bar = ProgressBar(progress_container, direction="down",
                                        colours=(theme.RED, theme.RED_DARK), bg_canvas=theme.GRAY_LIGHT)
        self.progress_bar.pack(side='bottom')

        # Linking progress bar width to bounding countainer (progress_container)
        progress_container["width"] = int(self.progress_bar["width"]) + 20


        ## Middle container for the grid and ships ##
        main_container = tk.Frame(self, bg=theme.WHITE)
        main_container.grid(column=1, row=0, padx=10, pady=15)


        self.main_grid = CustomGrid(main_container, multiplier=4,
                                    progress_bar=self.progress_bar, bottom_hidden=True,
                                    is_game_board=True, game=self.game, owner='computer')
        self.game.computer_board = self.main_grid
        self.main_grid.pack()

        self.ships_container = tk.Canvas(main_container, width=int(self.main_grid["width"]), height=130,
                                         highlightthickness=0, bg=theme.GRAY_DARK)

        self.ships_container.pack(pady=(0, 10))


        ## Right container for the small grid and button/info display ##
        right_container = tk.Frame(self)
        right_container.grid(column=2, row=0, sticky='n', pady=15)

        small_grid_container = tk.Frame(right_container)
        small_grid_container.pack(side='top', pady=(0, 10))

        self.small_grid = CustomGrid(small_grid_container, multiplier=2, progress_bar=None,
                                     disabled=True, bottom_hidden=True, game=self.game, owner='player')

        self.game.player_board = self.small_grid
        self.small_grid.show_hidden_ships()

        self.small_grid.pack(side='top')


        small_grid_info = tk.Frame(small_grid_container, width=220, height=40, bg=theme.GRAY_BLACK)
        small_grid_info.pack()
        small_grid_info.grid_propagate(0)

        # Text displayed in the small grid, static
        tk.Label(small_grid_info, text="YOUR\nTERRITORY", justify='right',
                             font=("Tw Cen MT", 13, "bold"), fg=theme.WHITE,
                             bg=theme.GRAY_BLACK).grid(column=0, row=0, sticky='w', padx=10)

        tk.Label(small_grid_info, text="HIT", fg=theme.WHITE, bg=theme.GRAY_BLACK,
                 font=("Tw Cen MT", 12, "bold")).grid(column=2, row=0, sticky='e',
                                                      padx=(5, 0), pady=(14, 0))

        # Percentage of player ships sunk, variable
        percentage_text = tk.Label(small_grid_info, text="0.0%", fg=theme.GREEN, bg=theme.GRAY_BLACK,
                                   font=("Tw Cen MT", 30, "bold"))
        percentage_text.grid(column=1, row=0, sticky='e')
        self.small_grid.linked_percentage = percentage_text


        small_grid_details = tk.Frame(small_grid_container, width=220, height=130,
                                      bg=theme.GRAY_LIGHT, highlightthickness=10, highlightbackground=theme.GRAY)
        small_grid_details.pack()
        small_grid_details.pack_propagate(0)

        tk.Label(small_grid_details, text="put some details about\n number of ships remaining\nand what ships they are",
                 bg=theme.GRAY_LIGHT, font=("Tw Cen MT", 13), fg=theme.GRAY_BLACK).pack(pady=10)

        info_frame = tk.Frame(right_container, bg=theme.GRAY_BLACK, width=220, height=100)
        info_frame.pack()

        info_frame.pack_propagate(0)

        turn_status = tk.Label(info_frame, text="PLAYER's", fg=theme.RED,
                               font=("Tw Cen MT", 30, "bold"), width=12)
        turn_status.pack(side='top', pady=(20, 0), ipady=5)

        self.game.status = turn_status

        tk.Label(info_frame, text="TURN", fg=theme.GRAY_LIGHT,
                 font=("Tw Cen MT", 14, "bold"), bg=theme.GRAY_BLACK).pack()


        control_frame = tk.Frame(right_container, bg=theme.GRAY_LIGHT, width=220, height=60)
        control_frame.pack(pady=10)

        back_button = CustomButton(control_frame, text="⚑ ", width=120, height=40,
                                   colour=theme.GOLD, fg=theme.WHITE, active=theme.GOLD_DARK, bg_canvas=theme.GRAY_LIGHT)
        back_button.place(x=10, y=51, anchor='sw')

        close_button = CustomButton(control_frame, text="✘ ", width=70, height=40,
                                    colour=theme.RED, fg=theme.WHITE, active=theme.RED_DARK, bg_canvas=theme.GRAY_LIGHT)

        close_button.place(x=210, y=51, anchor="se")

        close_button.bind_to_click(lambda: root.destroy())


### Game object with management on how the game runs ###
class Game(object):
    def __init__(self):
        self.difficulty = "normal"
        self.date = datetime.datetime
        self.theme = Colours("default")

        self.manager = manager

        # Structured as individual ships
        self.player_ships = []
        self.player_remaining_ships = []

        self.computer_ships = []
        self.computer_remaining_ships = []

        # Structured as alpha-num coords
        self.player_board_hit = []
        self.computer_board_hit = []

        self.player_board = None
        self.computer_board = None
        self.status = None

        self.computer_logic = ComputerLogic()

    def add_player_ships(self, ships_array):
        self.player_ships = copy.deepcopy(ships_array)
        self.player_remaining_ships = copy.deepcopy(ships_array)

    def add_computer_ships(self, ships_array):
        self.computer_ships = copy.deepcopy(ships_array)
        self.computer_remaining_ships = copy.deepcopy(ships_array)

    def set_boards(self, player_board, computer_board):
        self.player_board = player_board
        self.computer_board = computer_board

    # Exporting game
    def export_data(self):
        data = {"difficulty": ,
                "date": ,
                ""}

    # After any position is played (coord in alpha-num)
    def game_control(self, coord, board_name):

        # If last move was played on the computer's board (the big grid)
        if board_name == 'computer':
            self.computer_board_hit.append(coord)

            for ship in self.computer_remaining_ships:

                # Checks if the last move hit a ship
                if coord in ship:

                    # Finds the original ship
                    current_ship = self.computer_ships[self.computer_remaining_ships.index(ship)]
                    name = Ship.get_name(len(current_ship))
                    ship_sunk = False

                    # If the length of the current ship (before hit) was 1 (i.e 1 more hit dead)
                    if len(ship) == 1:
                        ship_sunk = True
                        print("Computer's {} is now sunk!".format(name))

                    # Removes the hit square from remaining spaces
                    ship.remove(coord)

                    self.check_win()

                    return(board_name, ship_sunk, current_ship)

            # Did not hit a ship
            else:
                hit_coord = None
                counter = 0
                # max = {'easy': 2,
                #        'normal': 3,
                #        'hard': 4,
                #        'master': 5}.get(self.difficulty, 1)
                max = 100

                # Gives the computer up to '3 virtual turns' on hard difficulty
                while counter < max:
                    hit_coord = CoordUtils.convert_type(self.computer_logic.make_move())

                    # Checks if 'hit_coord' hits a ship
                    for ship in self.player_remaining_ships:
                        if CoordUtils.convert_type(hit_coord) in ship:
                            counter += 100
                            break
                    else:
                        counter += 1

                def next():
                    self.player_board.hit(None, self.player_board.coord_to_rect(hit_coord), override=True)

                root.after(1000, next)

                self.status["text"] = "COMPUTER's"
                self.status["fg"] = self.theme.GOLD
                return ('player',)

        # If computer was the one who played the last move
        elif board_name == 'player':
            self.player_board_hit.append(coord)

            for ship in self.player_remaining_ships:

                # Checks if the last move hit a ship
                if coord in ship:

                    # Finds the original ship for aesthetic purposes
                    current_ship = self.player_ships[self.player_remaining_ships.index(ship)]
                    name = Ship.get_name(len(current_ship))
                    ship_sunk = False

                    # If the length of the current ship (before hit) was 1 (i.e 1 more hit dead)
                    if len(ship) == 1:
                        ship_sunk = True
                        print("Player's {} is now sunk!".format(name))

                    # Removes the hit square from remaining spaces
                    ship.remove(coord)

                    hit_coord = CoordUtils.convert_type(self.computer_logic.square_hit(coord, sunk=ship_sunk, ship=current_ship))

                    def next():
                        self.player_board.hit(None, self.player_board.coord_to_rect(hit_coord), override=True)
                        self.check_win()

                    root.after(1000, next)

                    return(board_name, ship_sunk, current_ship)

            # Didn't hit a ship
            else:
                self.status["text"] = "PLAYER's"
                self.status["fg"] = self.theme.RED
                self.turn_counter = 0

                self.computer_board.disabled = False
                return ('computer',)

    # Check if all remaining occupied squares are hit – backend
    def check_win(self):
        result = False

        for ship in self.player_remaining_ships:
            if len(ship) > 0: break
        else: result = 'computer'

        for ship in self.computer_remaining_ships:
            if len(ship) > 0: break
        else: result = 'player'

        bg_colour = self.theme.GREEN_DARK

        if result == 'player':
            print("Player wins the game!")
            self.manager.wins += 1

        elif result == 'computer':
            print("Computer wins the game!")
            self.manager.losses += 1
            bg_colour = self.theme.RED

        if result:
            switch_screen('splash')

            subtext = "Current score: {} wins and {} losses on {} difficulty".format(self.manager.wins, self.manager.losses, self.difficulty.upper())

            result_popup = Popup(root, text="YOU {}!".format("LOST" if (result == 'computer') else "WON"),
                                 bg=bg_colour, fg=self.theme.WHITE, fill=True,
                                 subtext=subtext)


### How the computer decides to play, best to its ability ###
# Note: Computer gameplay difficulty is determined through the 'game' class
###
class ComputerLogic(object):
    def __init__(self):

        # Alpha-num list of coordinates on the board that have yet to be hit
        self.grid = []

        for x in range(10):
            for y in range(10):
                self.grid.append(CoordUtils.convert_type(x + 1) + str(y + 1))

        # Alpha-num list of coordinates with ships
        self.cached_ship_coords = []

    # Returns a coordinate that has yet to be hit, in alpha-num form
    def make_move(self):

        # If no ships were hit in previous turns, make random move
        if len(self.cached_ship_coords) == 0:
            coord = random.choice(self.grid)
            surrounding = CoordUtils.get_surrounding_coords(coord)

            for surrounding_coord in surrounding:

                # Checks to see if there are any spaces around the coordinate,
                # since there isn't a point in hitting into an enclosed area
                if CoordUtils.convert_type(surrounding_coord) in self.grid:
                    self.grid.remove(coord)
                    return coord
            else:
                return self.make_move()

        # If a ship was recently hit (i.e cached), hit around
        else:

            # If two or more ship spaces have been hit
            if len(self.cached_ship_coords) > 1:

                # For every coordinate with a hit ship in it, check around
                for i in range(0, len(self.cached_ship_coords)):
                    sides = [CoordUtils.get_side_coord(self.cached_ship_coords[i], 'left'),
                             CoordUtils.get_side_coord(self.cached_ship_coords[i], 'right'),
                             CoordUtils.get_side_coord(self.cached_ship_coords[i], 'top'),
                             CoordUtils.get_side_coord(self.cached_ship_coords[i], 'bottom')]

                    linked_sides = []
                    converted_sides = []

                    for side in sides:
                        if side: converted_sides.append(CoordUtils.convert_type(side))
                        else: converted_sides.append(None)

                        if side and CoordUtils.convert_type(side) in self.cached_ship_coords:
                            linked_sides.append(CoordUtils.convert_type(side))

                    # If the two hit spaces aren't 'connected', choose random side (REDUNDANCY)
                    if len(linked_sides) == 0:
                        while True:
                            target = random.choice(converted_sides)

                            if target and target in self.grid:
                                self.grid.remove(target)
                                return target

                    # If only one side of the hit square is hit
                    if len(linked_sides) == 1:
                        index = converted_sides.index(linked_sides[0])

                        if index == 0 and converted_sides[1] in self.grid:
                            self.grid.remove(converted_sides[1])
                            return converted_sides[1]

                        elif index == 1 and converted_sides[0] in self.grid:
                            self.grid.remove(converted_sides[0])
                            return converted_sides[0]

                        elif index == 2 and converted_sides[3] in self.grid:
                            self.grid.remove(converted_sides[3])
                            return converted_sides[3]

                        elif index == 3 and converted_sides[2] in self.grid:
                            self.grid.remove(converted_sides[2])
                            return converted_sides[2]

                        else:
                            continue

                    # If both sides of the hit square are hit, continue to next hit coord
                    if len(linked_sides) == 2:
                        continue

            surrounding_coords = CoordUtils.get_surrounding_coords(self.cached_ship_coords[0])

            potential_targets = []

            for coord in surrounding_coords:
                if CoordUtils.convert_type(coord) in self.grid:
                    potential_targets.append(CoordUtils.convert_type(coord))

            if len(potential_targets) != 0:
                # DUMB VERSION – RANDOM SELECTION
                target = random.choice(potential_targets)
                self.grid.remove(target)

                return target
            else:
                self.cached_ship_coords = []
                return self.make_move()


    # Note: "square" argument is for a coord in alpha-num form (i.e D4)
    def square_hit(self, coord, sunk=False, ship=None):
        if sunk:
            self.cached_ship_coords = [coord for coord in self.cached_ship_coords if coord not in ship]

        else:
            self.cached_ship_coords.append(coord)

        next_move = self.make_move()
        return next_move


### Manager for reading / writing to files for saving ###
class Manager(object):
    def __init__(self):
        self.saved_games = {}

        self.wins = 0
        self.losses = 0

    # Export all saved games (3) and scores to file
    def export_to_file(self):
        pass

    # Imports all saved games (3) and scores to memory
    def import_to_memory(self):
        pass

    # Resets the scores to 0
    def reset_scores(self):
        self.wins, self.losses = 0, 0


if __name__ == "__main__":

    manager = Manager()
    manager.import_to_memory()

    root = tk.Tk()

    root.wm_geometry("850x600")
    root.wm_resizable(0, 0)
    root.wm_title("Battleships V1.54 alpha")

    # For setting the application for gameplay, easy to debug without having
    # to setup ships every single time
    def debugger():
        game = Game()

        game.add_computer_ships([["G1", "G2", "G3", "G4", "G5"],
                                 ["A10", "B10", "C10", "D10"],
                                 ["C5", "D5", "E5"],
                                 ["I8", "I9", "I10"],
                                 ["F9", "F10"]])

        game.add_player_ships([["G1", "G2", "G3", "G4", "G5"],
                               ["A10", "B10", "C10", "D10"],
                               ["C5", "D5", "E5"],
                               ["I8", "I9", "I10"],
                               ["F9", "F10"]])

        switch_screen('game', game)

    # The 'frame' that's displayed on the application window
    current_screen = None

    switch_screen('splash')

    root.mainloop()
