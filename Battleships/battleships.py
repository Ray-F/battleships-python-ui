# # # # # # # # # # # # # # # # # # # #
#
# Created 11th June 2018, Raymond Feng
#
# Updated: 22nd July 2018
#
# Purpose: Main battleships game class
#
# # # # # # # # # # # # # # # # # # # #

version = 3.00


import tkinter as tk
import random
import datetime
import os.path

from frameworks.custom_widgets import *


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

        theme = Colours(manager.theme)

        self.bar = tk.Frame(self, width=800, height=25, bg=theme.GRAY_DARK)
        self.bar.pack(side='top', pady=(60, 0))

        self.title = tk.Label(self, text="BATTLESHIPS", font=("Tw Cen MT", 100, "bold"), fg=theme.GRAY_BLACK)
        self.title.pack(side='top', padx=(26, 240), pady=(20, 10))

        self.main_frame = tk.Frame(self, width=750, height=320, bg=theme.WHITE)
        self.main_frame.pack(side='bottom')

        self.main_frame.grid_propagate(0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

        info_frame = tk.Canvas(self.main_frame, width=480, height=320, highlightthickness=0)
        info_frame.grid(column=0, row=0, sticky='nw')
        rounded_rect(info_frame, 0, 0, int(info_frame["width"]), int(info_frame["height"]), 50, colour=theme.GRAY_LIGHT)


        info_frame_text = ['>bBeta Release V{:.2f}'.format(version),
                           '>lLEADERBOARDS',
                           '']

        for mode in ('easy', 'normal', 'hard', 'master'):

            info_frame_text.append('{} Mode:\t{} wins – {} losses'.format(mode.upper(),
                                                                                        manager.stats[mode][0],
                                                                                        manager.stats[mode][1]))

        info_frame_text += ['\n','>sDesigned by Raymond Feng, 2018.', '>sGo to  http://www.spprax.com  to find out more']

        leaderboards_frame = CustomLongText(info_frame, text=info_frame_text, height=270, width=300,
                                            fg=theme.GRAY_BLACK, bg=theme.GRAY_LIGHT)

        info_frame.create_window(int(info_frame["width"])/ 2, int(info_frame['height']) / 2,
                                 window=leaderboards_frame, anchor='center', tag='window')


        buttons_frame = tk.Frame(self.main_frame, width=256, height=int(self.main_frame["height"]))
        buttons_frame.grid(column=1, row=0, sticky='nw')
        buttons_frame.pack_propagate(False)

        new_game_button = CustomButton(buttons_frame, text="New Game", width=250, height=80,
                                       colour=theme.CYAN, fg=theme.WHITE, active=theme.CYAN_DARK)

        new_game_button.bind_to_click(lambda: switch_screen('setup'))
        new_game_button.place(x=0, y=-1, anchor='nw')

        load_button = CustomButton(buttons_frame, text="Load Saved", width=250, height=80,
                                   colour=theme.TURQUOISE, fg=theme.WHITE, active=theme.TURQUOISE_DARK)
        load_button.place(x=0, y=84, anchor='nw')

        close_button = CustomButton(buttons_frame, text="✘", width=80, height=60,
                                    colour=theme.RED, fg=theme.WHITE, active=theme.RED_DIM)

        close_button.place(x=251, y=int(self.main_frame["height"]), anchor="se")

        close_button.bind_to_click(lambda: root.destroy())

        def load_screen():
            saves = SavesFrame(info_frame)

            info_frame.delete('window')
            info_frame.create_window(240, 160, window=saves, anchor='center', tag='window')

            load_button.destroy()

            close_button = CustomButton(buttons_frame, text="⏎", width=80, height=60,
                                        colour=theme.GOLD, fg=theme.WHITE, active=theme.GOLD_DARK)
            close_button.place(x=251, y=int(self.main_frame["height"]), anchor="se")

            close_button.bind_to_click(lambda: switch_screen('splash'))

        load_button.bind_to_click(load_screen)


### Frame within splash saves, inside the splash screen ###
class SavesFrame(tk.Frame):
    def __init__(self, parent):

        theme = Colours(manager.theme)
        super().__init__(parent)
        self["bg"] = theme.GRAY_LIGHT

        def delete(save, index):
            for child in save.winfo_children():
                child.destroy()

            save["bg"] = theme.GRAY
            new_id = tk.Label(save, text="EMPTY SAVE", font=("Tw Cen MT", 12), fg=theme.WHITE, bg=theme.GRAY)
            new_id.place(x=10, y=5, anchor='nw')

            del manager.saved_games[index]

        def open_save(save, index):
            game = Game()
            game.import_data(manager.saved_games[index])
            switch_screen('game', game)

            del manager.saved_games[index]


        for i in range(3):
            save = None

            bg = theme.GRAY
            if len(manager.saved_games) > i:
                bg = theme.WHITE
                save = manager.saved_games[i]


            save_frame = tk.Frame(self, width=400, height=80, bg=bg)

            similar_labels = []

            id_label = tk.Label(save_frame, text="{}SAVE #{}".format("" if save else "EMPTY ", i + 1),
                                font=("Tw Cen MT", 12))
            similar_labels.append(id_label)

            id_label.place(x=10, y=5, anchor='nw')

            if save:
                date_label = tk.Label(save_frame, text=save["date"].strftime('%A %-I:%M%p, %d %b %Y'),
                                      font=("Tw Cen MT", 12))
                similar_labels.append(date_label)
                date_label.place(x=390, y=5, anchor='ne')

                mode_label = tk.Label(save_frame, text="Difficulty", font=("Tw Cen MT", 16))
                similar_labels.append(mode_label)
                mode_label.place(x=30, y=45, anchor='w')

                mode = tk.Label(save_frame, text=save["difficulty"].upper(), font=("Tw Cen MT", 20, "bold"))
                similar_labels.append(mode)
                mode.place(x=90, y=45, anchor='w')


                player_count = 0
                for ship in save["player_ships"]:
                    for coord in save["player_hit"]:
                        if coord in ship:
                            player_count += 1

                comp_count = 0
                for ship in save["computer_ships"]:
                    for coord in save["computer_hit"]:
                        if coord in ship:
                            comp_count += 1

                avg_game = round(max(player_count * 100/ 17, comp_count * 100 / 17), 1)
                avg_game_label = tk.Label(save_frame, text="{}% of game completed".format(avg_game),
                                          font=("Tw Cen MT", 12))
                similar_labels.append(avg_game_label)
                avg_game_label.place(x=30, y=60, anchor='w')

                delete_button = CustomButton(save_frame, text="Delete", width=60, height=30, font=("Tw Cen Mt", 12),
                                             fg=theme.WHITE, colour=theme.RED, active=theme.RED_DIM)
                delete_button.place(x=390, y=65, anchor='se')

                delete_button.bind_to_click(lambda arg=save_frame, arg2=i: delete(arg, arg2))

                open_button = CustomButton(save_frame, text="Open", width=60, height=30, font=("Tw Cen MT", 12),
                                           fg=theme.WHITE, colour=theme.GREEN, active=theme.GREEN_DIM)
                open_button.place(x=325, y=65, anchor='se')
                open_button.bind_to_click(lambda arg=save_frame, arg2=i: open_save(arg, arg2))


            for label in similar_labels:
                label["fg"] = theme.GRAY_BLACK if save else theme.WHITE
                label["bg"] = bg


            save_frame.grid(column=0, row=i, pady=(0, 5))

### Board setup – Window ###
class SetupWindow(tk.Frame):
    ### NB: The SetupWindow frame is split into 3 main column areas.
    # The first column area is for the progress bar.
    # The second column area is for the main game grid and ships container
    # The third column area is for the display grid, as well as the game stats

    def __init__(self, parent):
        super().__init__(parent)

        theme = Colours(manager.theme)
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

        small_grid_container = tk.Frame(right_container, bg=theme.GRAY_BLACK, width=220, height=200)
        small_grid_container.pack(side='top', pady=(0, 10))

        help_label = tk.Label(small_grid_container, text="SETUP GUIDE", font=("Tw Cen MT", 20, "bold"),
                              bg=theme.GRAY_BLACK, fg=theme.WHITE)
        help_label.pack(pady=5)

        help_text = ['1) Click on a white ship to select,      '
                     '\nthen hover over grid to set ship.',
                     '\n2) Rotate a ship by right-clicking\n on the grid.',
                     '3) Click mode to toggle difficutly.']

        help_desc = CustomLongText(small_grid_container, text=help_text, width=220, height=160,
                                   bg=theme.GRAY_DARK, fg=theme.WHITE, side='left')
        help_desc["pady"] = 10

        help_desc.pack()

        difficulty_container = tk.Frame(right_container, width=220, height=52, bg=theme.GRAY_DARK)
        difficulty_container.pack(pady=(0, 10))
        difficulty_container.pack_propagate(0)

        difficulty_label = tk.Label(difficulty_container, text="MODE\nSELECTION", font=("Tw Cen MT", 12, "bold"),
                                    fg=theme.WHITE, bg=theme.GRAY_DARK, anchor='e', justify='right')
        difficulty_label.pack(side='left', padx=(10, 0))

        self.difficulty_button_hover = theme.GRADIENT[1]
        difficulty_button = tk.Label(difficulty_container, text='NORMAL', font=("Tw Cen MT", 24, "bold"),
                                     fg=theme.WHITE, bg=theme.GRAY_BLACK, width=12, height=2, padx=20)
        difficulty_button.pack(side='left', padx=(10, 0))

        def difficulty_change():
            modes = ['easy', 'normal', 'hard', 'master']

            current_index = modes.index(difficulty_button["text"].lower())

            if modes[-1] == difficulty_button["text"].lower():
                self.game.difficulty = modes[0]
            else:
                self.game.difficulty = modes[current_index + 1]

            difficulty_button["bg"] = theme.GRADIENT[modes.index(self.game.difficulty)]
            self.difficulty_button_hover = theme.GRADIENT[modes.index(self.game.difficulty)]
            difficulty_button["text"] = self.game.difficulty.upper()


        difficulty_button.bind("<Enter>", lambda event: difficulty_button.config(bg=self.difficulty_button_hover))
        difficulty_button.bind("<Leave>", lambda event: difficulty_button.config(bg=theme.GRAY_BLACK))

        difficulty_button.bind("<Button-1>", lambda event: difficulty_change())

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
                self.game.add_computer_ships(self.game.computer_logic.generate_layout())

                switch_screen('game', args=self.game)

        start_game_button = CustomButton(info_frame, text="GO!", height=150, width=200,
                                         colour=theme.GREEN, fg=theme.GREEN_DARK, active=theme.GREEN_DIM,
                                         font=("Tw Cen MT", 40, "bold"), bg_canvas=theme.GRAY_LIGHT)
        start_game_button.bind_to_click(start_game)
        start_game_button.pack(pady=(0, 10))

        control_frame = tk.Frame(right_container, bg=theme.GRAY_LIGHT, width=220, height=60)
        control_frame.pack(pady=10)

        back_button = CustomButton(control_frame, text="⏎", width=120, height=40,
                                   colour=theme.GOLD, fg=theme.WHITE, active=theme.GOLD_DARK,
                                   bg_canvas=theme.GRAY_LIGHT)
        back_button.place(x=10, y=51, anchor='sw')
        back_button.bind_to_click(lambda: switch_screen('splash'))

        close_button = CustomButton(control_frame, text="✘", width=70, height=40,
                                    colour=theme.RED, fg=theme.WHITE, active=theme.RED_DIM,
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

        theme = Colours(manager.theme)
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

        bottom_filler = tk.Frame(main_container, width=int(self.main_grid["width"]), height=130,
                                 highlightthickness=0, bg=theme.GRAY_DARK)
        bottom_filler.pack_propagate(0)

        bottom_filler.pack(pady=(0, 10))

        last_location = tk.Label(bottom_filler, text="––",
                                 fg=theme.WHITE, bg=theme.GRAY_BLACK,
                                 font=("Tw Cen MT", 60, "bold"), height=2, width=4)

        self.main_grid.linked_coordinate = last_location

        last_label = tk.Label(bottom_filler, text="Last Location", fg=theme.WHITE, bg=theme.GRAY_DARK,
                              font=("Tw Cen MT", 24, "bold"))

        last_location.pack(side='left')
        last_label.pack(side='left', padx=20)

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
        percentage_text = tk.Label(small_grid_info, text="0.00%", fg=theme.GREEN, bg=theme.GRAY_BLACK,
                                   font=("Tw Cen MT", 30, "bold"))
        percentage_text.grid(column=1, row=0, sticky='e')
        self.small_grid.linked_percentage = percentage_text


        small_grid_details = tk.Frame(small_grid_container, width=220, height=130,
                                      bg=theme.GRAY_LIGHT, highlightthickness=10, highlightbackground=theme.GRAY)
        small_grid_details.pack()
        small_grid_details.pack_propagate(0)

        details = ['>bCURRENT STATS',
                   'Games won:       {1} out of {0}\n'
                   'Games lost:        {2} out of {0}'.format(manager.stats[self.game.difficulty][0] + manager.stats[self.game.difficulty][1],
                                                              manager.stats[self.game.difficulty][0],
                                                              manager.stats[self.game.difficulty][1]),
                   'Difficulty:  {}'.format(game.difficulty.upper())]

        fonts = {">b": ("Tw Cen MT", 14, "bold"),
                 "default": ("Tw Cen MT", 14)}

        longlabel = CustomLongText(small_grid_details, text=details,
                                   fg=theme.GRAY_BLACK, bg=theme.GRAY_LIGHT,
                                   width=200, height=110, fonts=fonts)
        longlabel.pack(pady=15)

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

        resign_button = CustomButton(control_frame, text="⚑", width=120, height=40,
                                    colour=theme.GOLD, fg=theme.WHITE, active=theme.GOLD_DARK,
                                    bg_canvas=theme.GRAY_LIGHT)
        resign_button.place(x=10, y=51, anchor='sw')
        resign_button.bind_to_click(lambda: self.game.check_win(override=True))


        def close():
            background = theme.GRAY_BLACK

            popup = Popup(root, text="Do you wish to save this game?",
                          subtext="Note: Oldest game will be deleted if memory is full.",
                          bg=background, fg=theme.WHITE, stay=True)
            popup["height"] = 140
            popup.coords(popup.main, int(popup["width"]) / 2, 35)
            popup.coords(popup.sub, int(popup["width"]) / 2, 60)

            container = tk.Frame(bg=background)

            save = CustomButton(container, text="Yes", colour=theme.GREEN, fg=theme.WHITE,
                                       active=theme.GREEN_DARK, bg_canvas=background,
                                       width=200, height=40)

            close = CustomButton(container, text="No", colour=theme.RED, fg=theme.WHITE,
                                        active=theme.RED_DIM, bg_canvas=background,
                                        width=200, height=40)
            def return_to_splash(save):
                if save:
                    data = self.game.get_data_summary()
                    manager.save_game(data)
                    manager.export_to_file()

                popup.destroy()
                container.destroy()
                switch_screen('splash')

            close.bind_to_click(lambda: return_to_splash(save=False))
            save.bind_to_click(lambda: return_to_splash(save=True))

            save.pack(side='left', padx=10)
            close.pack(side='right', padx=10)

            container.place(x=root.winfo_width() / 2, y=root.winfo_height() / 2 + 35, anchor='center')

            root.after(10000, container.destroy)

        close_button = CustomButton(control_frame, text="✘", width=70, height=40,
                                    colour=theme.RED, fg=theme.WHITE, active=theme.RED_DIM, bg_canvas=theme.GRAY_LIGHT)
        close_button.place(x=210, y=51, anchor="se")

        close_button.bind_to_click(lambda: close())


### Game object with management on how the game runs ###
class Game(object):
    def __init__(self):

        # Difficulty selection range: easy, normal, hard, master
        self.difficulty = "normal"
        self.date = datetime.datetime.today()
        self.theme = Colours(manager.theme)

        self.manager = manager
        self.game_over = False

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

    # Sets the ships on player's board to the layout from setup
    def add_player_ships(self, ships_array):
        self.player_ships = copy.deepcopy(ships_array)
        self.player_remaining_ships = copy.deepcopy(ships_array)

    # Sets out predefined ships for startup
    def add_computer_ships(self, ships_array):
        self.computer_ships = copy.deepcopy(ships_array)
        self.computer_remaining_ships = copy.deepcopy(ships_array)

    def set_boards(self, player_board, computer_board):
        self.player_board = player_board
        self.computer_board = computer_board

    # Exporting game data
    def get_data_summary(self):
        data = {"difficulty": self.difficulty, "date": self.date,
                "player_ships": self.player_ships,
                "player_hit": self.player_board_hit,

                "computer_ships": self.computer_ships,
                "computer_hit": self.computer_board_hit,
                "computer_cache": self.computer_logic.cached_ship_coords}

        return data

    # Imports all the game data
    def import_data(self, data):
        self.difficulty = data["difficulty"]

        self.add_player_ships(data["player_ships"])
        self.player_board_hit = data["player_hit"]

        self.add_computer_ships(data["computer_ships"])
        self.computer_board_hit = data["computer_hit"]
        self.computer_logic.cached_ship_coords = data["computer_cache"]

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

                    return(board_name, ship_sunk, current_ship)

            # Did not hit a ship
            else:
                hit_coord = None
                counter = 0
                max = {'easy': 1,
                       'normal': 2,
                       'hard': 3,
                       'master': 5}.get(self.difficulty, 1)

                # Gives the computer up to '4 virtual turns' on hard difficulty
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
    def check_win(self, override=False):

        if self.game_over:
            return

        result = override

        for ship in self.player_remaining_ships:
            if len(ship) > 0: break
        else: result = 'computer'

        for ship in self.computer_remaining_ships:
            if len(ship) > 0: break
        else: result = 'player'

        bg_colour = self.theme.GREEN_DIM

        if result == 'player':
            print("Player wins the game!")
            self.manager.stats[self.difficulty][0] += 1

        elif result == 'computer':
            print("Computer wins the game!")
            self.manager.stats[self.difficulty][1] += 1
            bg_colour = self.theme.RED

        elif result:
            print("Player resigns.")
            self.manager.stats[self.difficulty][1] += 1
            bg_colour = self.theme.RED

        if result:
            manager.export_to_file()
            self.game_over = True

            def popup_appear():
                switch_screen('splash')

                subtext = "Current score: {} wins and {} losses on {} difficulty".format(manager.stats[self.difficulty][0],
                                                                                         manager.stats[self.difficulty][1],
                                                                                         self.difficulty.upper())

                result_popup = Popup(root, text="YOU {}!".format("WON" if (result == "player") else "LOST"),
                                     bg=bg_colour, fg=self.theme.WHITE, fill=True,
                                     subtext=subtext)

            root.after(1200, popup_appear)

        return result

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

    # Based on pre-existing boards, generate layout
    # Next version will have automatic generators for layout
    def generate_layout(self):

        ship_lengths = [2, 3, 3, 4, 5]
        direction = ['right', 'bottom']

        computer_ships = []
        coords = []

        while len(ship_lengths) > 0:
            x = random.randint(1, 10)
            y = random.randint(1, 10)

            length = random.choice(ship_lengths)

            ship_coords = CoordUtils.get_coords_along_side((x, y), random.choice(direction), length)

            if ship_coords:
                for coord in ship_coords:
                    if coord in coords:
                        break
                else:
                    computer_ships.append(ship_coords)
                    [coords.append(coord) for coord in ship_coords]
                    ship_lengths.remove(length)

        return computer_ships


### Manager for reading / writing to files for saving ###
class Manager(object):
    def __init__(self):
        self.saved_games = []

        # Note: [0] is wins, [1] is losses
        self.stats = {'easy': [0, 0],
                      'normal': [0, 0],
                      'hard': [0, 0],
                      'master': [0, 0]}

        self.theme = "default"

    # Export all saved games (3) and scores to file
    def export_to_file(self):
        with open('bin/stats.bts', 'w') as file:
            file.write(str(self.stats))

        with open('bin/saves.bts', 'w') as file:
            file.write(str(self.saved_games))

    # Imports all saved games (3) and scores to memory
    def import_to_memory(self):
        if os.path.isfile('bin/stats.bts'):
            with open('bin/stats.bts', 'r') as file:
                self.stats = eval(file.read())

        if os.path.isfile('bin/saves.bts'):
            with open('bin/saves.bts', 'r') as file:
                self.saved_games = eval(file.read())

    # Resets the scores to 0
    def reset_scores(self):
        self.stats = {'easy': [0, 0],
                      'normal': [0, 0],
                      'hard': [0, 0],
                      'master': [0, 0]}

    # Replaces old games if all saves are full
    def save_game(self, game_data_summary):
        if len(self.saved_games) > 2:
            del self.saved_games[0]

        self.saved_games.append(game_data_summary)



if __name__ == "__main__":

    manager = Manager()
    manager.import_to_memory()

    root = tk.Tk()

    root.wm_geometry("850x600")
    root.wm_resizable(0, 0)
    root.wm_title("Battleships V{:.2f} beta".format(version))

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

    manager.export_to_file()
