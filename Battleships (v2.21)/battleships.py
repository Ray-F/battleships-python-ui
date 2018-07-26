# # # # # # # # # # # # # # # # # # # #
#
# Created 11th June 2018, Raymond Feng
#
# Updated: 22nd July 2018
#
# Purpose: Main battleships game class
#
# # # # # # # # # # # # # # # # # # # #

# Current version of the program.
version = 2.21


import tkinter as tk
import random
import datetime
import os.path

# Custom widgets module
from frameworks.custom_widgets import *


### Function for switching between different screens ###
#   – Screens can be of splash, setup, game (with 'Game' object arg)
#   – Note: All screens (splash, setup etc.) are of type tk.Frame
#####
def switch_screen(screen, args=None):
    global current_screen

    # If there was previously a screen, destroy that screen
    if current_screen != None: current_screen.destroy()

    if screen == 'splash': current_screen = SplashScreen(root)
    elif screen == 'setup': current_screen = SetupWindow(root)
    elif screen == 'game': current_screen = GameWindow(root, args)

    # Packs the new screen frame into the root window
    current_screen.pack()

    # Temporary white frame to hide widgets being destroyed
    white = tk.Frame(root, bg='white', width=1000, height=1000)
    white.place(x=0, y=0, anchor='nw')

    root.after(50, white.destroy)


### Splash screen to load a saved game, start a new game or view scoreboard ###
class SplashScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Uses the colour theme defined at startup
        theme = Colours(manager.theme)

        # Horizontal bar (aesthetic)
        self.bar = tk.Frame(self, width=800, height=25, bg=theme.GRAY_DARK)
        self.bar.pack(side='top', pady=(60, 0))

        # Title (aesthetic)
        self.title = tk.Label(self, text="BATTLESHIPS", font=("Tw Cen MT", 100, "bold"), fg=theme.GRAY_BLACK)
        self.title.pack(side='top', padx=(26, 240), pady=(20, 10))

        # Container for all other elements beneath title
        self.main_frame = tk.Frame(self, width=750, height=320, bg=theme.WHITE)
        self.main_frame.pack(side='bottom')

        self.main_frame.grid_propagate(0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

        # Lefthand side rounded frame for displaying information and scoreboards #
        info_canvas = tk.Canvas(self.main_frame, width=480, height=320, highlightthickness=0)
        info_canvas.grid(column=0, row=0, sticky='nw')

        # Creates a rounded rectangle (aesthetic)
        rounded_rect(info_canvas, 0, 0, int(info_canvas["width"]), int(info_canvas["height"]), 50, colour=theme.GRAY_LIGHT)

        # Outer information text, static
        info_text = ['>bBeta Release V{:.2f}'.format(version),
                     '>lSCOREBOARD',
                     '', '', '', '', '',
                     '\n',
                     '>sDesigned by Raymond Feng, 2018.',
                     '>sGo to  http://www.spprax.com  to find out more']

        scoreboard_text = ['']

        # Appends all the scores for different difficulties into scoreboard_text
        for mode in ('easy', 'normal', 'hard', 'master'):
            scoreboard_text.append('{} Mode:\t{} wins – {} losses'.format(mode.upper(),
                                                                           manager.stats[mode][0],
                                                                           manager.stats[mode][1]))

        # Creates a frame with labels for every element in info_text
        info_labels = CustomLongText(info_canvas, text=info_text, height=270, width=400,
                                           fg=theme.GRAY_BLACK, bg=theme.GRAY_LIGHT)
        info_canvas.create_window(int(info_canvas["width"]) / 2, int(info_canvas['height']) / 2,
                                 window=info_labels, anchor='center', tag='window')

        # Creates a frame with labels for every element in scoreboard_text
        scoreboard_labels = CustomLongText(info_canvas, text=scoreboard_text, height=140, width=400,
                                            fg=theme.GRAY_BLACK, bg=theme.WHITE)
        info_canvas.create_window(int(info_canvas['width']) / 2, int(info_canvas['height']) / 2 + 10,
                                 window=scoreboard_labels, anchor='center', tag='window')

        def reset():
            manager.reset_scores()
            switch_screen('splash')

        reset_score_button = CustomButton(info_canvas, text="Reset Scores", width=90, height=40, font=("Tw Cen MT", 12),
                                          colour=theme.GRAY, fg=theme.WHITE, active=theme.GRAY_DARK, bg_canvas=theme.GRAY_LIGHT)

        reset_score_button.bind_to_click(reset)
        info_canvas.create_window(440, 295, window=reset_score_button, anchor='se', tag='window')

        # Right hand side frame, acts as a buttons container #
        buttons_container = tk.Frame(self.main_frame, width=256, height=int(self.main_frame["height"]))
        buttons_container.grid(column=1, row=0, sticky='nw')
        buttons_container.pack_propagate(False)

        # Creates a button to start a new game, switching to setup window
        new_game_button = CustomButton(buttons_container, text="New Game", width=250, height=80,
                                       colour=theme.CYAN, fg=theme.WHITE, active=theme.CYAN_DARK)
        new_game_button.bind_to_click(lambda: switch_screen('setup'))
        new_game_button.place(x=0, y=-1, anchor='nw')

        # Creates a button to open saves frame
        load_button = CustomButton(buttons_container, text="Load Saved", width=250, height=80,
                                   colour=theme.TURQUOISE, fg=theme.WHITE, active=theme.TURQUOISE_DARK)
        load_button.place(x=0, y=84, anchor='nw')

        # Creates a button to destroy application window
        close_button = CustomButton(buttons_container, text="✘", width=80, height=60,
                                    colour=theme.RED, fg=theme.WHITE, active=theme.RED_DIM)
        close_button.place(x=251, y=int(self.main_frame["height"]), anchor="se")
        close_button.bind_to_click(lambda: root.destroy())

        # Function called when 'load saves' button is pressed #
        def load_screen():

            # Makes a 'saves frame'
            saves = SavesFrame(info_canvas)

            # Deletes all canvas items with tag 'window' (i.e all canvas elements)
            info_canvas.delete('window')
            load_button.destroy()

            # Creates a new window for saves
            info_canvas.create_window(240, 160, window=saves, anchor='center', tag='window')

            # Redefines close_button as back button to splash
            close_button = CustomButton(buttons_container, text="⏎", width=80, height=60,
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

        # Function to delete a save after 'delete' button is pressed #
        def delete(save, index):

            # Destroys all elements within the individual save frame
            for child in save.winfo_children():
                child.destroy()

            # Resets the ind. save frame into an empty save
            save["bg"] = theme.GRAY
            new_id = tk.Label(save, text="EMPTY SAVE", font=("Tw Cen MT", 12), fg=theme.WHITE, bg=theme.GRAY)
            new_id.place(x=10, y=5, anchor='nw')

            # Deletes the saved game from manager's storage
            del manager.saved_games[index]

        # Function to open a save when 'open' button is pressed #
        def open_save(save, index):

            # Makes a new game and imports the data from manager's storage
            game = Game()
            game.import_data(manager.saved_games[index])
            switch_screen('game', game)

            # Deletes the saved game from manager's storage
            del manager.saved_games[index]

        # Creates 3 individual save frames with varying elements inside
        for i in range(3):
            save = None

            bg = theme.GRAY

            # If manager's storage has save, make the frame white and make it the current save
            if len(manager.saved_games) > i:
                bg = theme.WHITE
                save = manager.saved_games[i]

            # Creates an individual save frame
            save_frame = tk.Frame(self, width=400, height=80, bg=bg)

            # Array for laziness... Makes all similar labels have the same colour font
            similar_labels = []

            # ID label (i.e "SAVE #1")
            id_label = tk.Label(save_frame, text="{}SAVE #{}".format("" if save else "EMPTY ", i + 1),
                                font=("Tw Cen MT", 12))
            similar_labels.append(id_label)
            id_label.place(x=10, y=5, anchor='nw')

            # If a save exists, add these elements to the save frame
            if save:

                # The date
                date_label = tk.Label(save_frame, text=save["date"].strftime('%A %-I:%M%p, %d %b %Y'),
                                      font=("Tw Cen MT", 12))
                similar_labels.append(date_label)
                date_label.place(x=390, y=5, anchor='ne')

                # The difficulty mode label
                mode_label = tk.Label(save_frame, text="Difficulty", font=("Tw Cen MT", 16))
                similar_labels.append(mode_label)
                mode_label.place(x=30, y=45, anchor='w')

                # The difficulty mode
                mode = tk.Label(save_frame, text=save["difficulty"].upper(), font=("Tw Cen MT", 20, "bold"))
                similar_labels.append(mode)
                mode.place(x=90, y=45, anchor='w')

                # Checks how many ships on player's board have been hit
                player_count = 0
                for ship in save["player_ships"]:
                    for coord in save["player_hit"]:
                        if coord in ship:
                            player_count += 1

                # Checks how many ships on computer's board have been hit
                comp_count = 0
                for ship in save["computer_ships"]:
                    for coord in save["computer_hit"]:
                        if coord in ship:
                            comp_count += 1

                # Finds the maximum of the two counts, can be used
                # as a crude measure of game's progress to completion
                avg_game = round(max(player_count * 100/ 17, comp_count * 100 / 17), 1)
                avg_game_label = tk.Label(save_frame, text="{}% of game completed".format(avg_game),
                                          font=("Tw Cen MT", 12))
                similar_labels.append(avg_game_label)
                avg_game_label.place(x=30, y=60, anchor='w')

                # Creates a delete button on each frame, to delete the save
                delete_button = CustomButton(save_frame, text="Delete", width=60, height=30, font=("Tw Cen Mt", 12),
                                             fg=theme.WHITE, colour=theme.RED, active=theme.RED_DIM)
                delete_button.place(x=390, y=65, anchor='se')
                delete_button.bind_to_click(lambda arg=save_frame, arg2=i: delete(arg, arg2))

                # Creates a button to open each save into a game window
                open_button = CustomButton(save_frame, text="Open", width=60, height=30, font=("Tw Cen MT", 12),
                                           fg=theme.WHITE, colour=theme.GREEN, active=theme.GREEN_DIM)
                open_button.place(x=325, y=65, anchor='se')
                open_button.bind_to_click(lambda arg=save_frame, arg2=i: open_save(arg, arg2))

            # Changes font fg and bg of all predefined 'similar' labels
            for label in similar_labels:
                label["fg"] = theme.GRAY_BLACK if save else theme.WHITE
                label["bg"] = bg

            # Places each individual save frame into the big save grid (self)
            save_frame.grid(column=0, row=i, pady=(0, 5))


### Board setup Window ###
class SetupWindow(tk.Frame):
    ### NB: The SetupWindow frame is split into 3 main column areas.
    # The first column area is for the progress bar (UNUSED IN SETUP)
    # The second column area is for the main game grid and ships container
    # The third column area is for help information, mode selection and other buttons
    ###

    def __init__(self, parent):
        super().__init__(parent)

        theme = Colours(manager.theme)

        # Creates a new game object
        self.game = Game()

        # Left container for the progress bar and some info text #
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


        # Middle container for the grid and ships #
        main_container = tk.Frame(self, bg=theme.WHITE)
        main_container.grid(column=1, row=0, padx=10, pady=15)

        # The setup grid for player to place ships on
        self.main_grid = CustomGrid(main_container, multiplier=4,
                                    progress_bar=self.progress_bar, bottom_hidden=True, is_game_board=False)
        self.main_grid.pack()

        # The black bottom bar for player to select ships
        ships_container = tk.Canvas(main_container, width=int(self.main_grid["width"]), height=130,
                                    highlightthickness=0, bg=theme.GRAY_DARK)

        self.current_ship_selection = None

        # Gets the length of the ship that's been clicked
        def return_current_length(ship):

            # If a new ship is clicked, unselect current ship
            if self.main_grid.selection_length != 0:
                self.current_ship_selection.selected = False
                self.current_ship_selection.unhover(None)

            # Sets the length to be used on the setup grid as length of new ship
            self.main_grid.selection_length = ship.length
            self.main_grid.selection_dir = ship.dir

            # Sets currently selected ship as current selected ship
            self.current_ship_selection = ship

        # Defines all the ships (length and direction), and their positions in ship container
        self.ships = [Ship(ships_container, 40, 15, length=2, dir='v'),
                      Ship(ships_container, 90, 15, length=3, dir='v'),
                      Ship(ships_container, 140, 15, length=3, dir='v'),
                      Ship(ships_container, 220, 15, length=5),
                      Ship(ships_container, 220, 65, length=4)]

        ships_container.pack(pady=(0, 10))

        # Binds length changer to a ship being clicked
        for ship in self.ships: ship.bind_to_click(return_current_length)


        ## Right container for the small grid and button/info display ##
        right_container = tk.Frame(self)
        right_container.grid(column=2, row=0, sticky='n', pady=15)

        # Container for the help guide and text
        help_container = tk.Frame(right_container, bg=theme.GRAY_BLACK, width=220, height=200)
        help_container.pack(side='top', pady=(0, 10))

        # 'SETUP GUIDE' label
        help_label = tk.Label(help_container, text="SETUP GUIDE", font=("Tw Cen MT", 20, "bold"),
                              bg=theme.GRAY_BLACK, fg=theme.WHITE)
        help_label.pack(pady=(8, 2))

        # Places all the help text
        help_text = ['1) Click on a white ship to select,      '
                     '\nthen hover over grid to set ship.',
                     '\n2) Rotate a ship by right-clicking\n on the grid.',
                     '\n3) Click mode to toggle difficutly.']
        help_desc = CustomLongText(help_container, text=help_text, width=220, height=160,
                                   bg=theme.GRAY_DARK, fg=theme.WHITE, side='left')
        help_desc["pady"] = 10
        help_desc.pack()

        # Container for the difficulty toggle box
        difficulty_container = tk.Frame(right_container, width=220, height=52, bg=theme.GRAY_DARK)
        difficulty_container.pack(pady=(0, 10))
        difficulty_container.pack_propagate(0)

        # 'MODE SELECTION' Label for the difficulty toggle
        difficulty_label = tk.Label(difficulty_container, text="MODE\nSELECTION", font=("Tw Cen MT", 12, "bold"),
                                    fg=theme.WHITE, bg=theme.GRAY_DARK, anchor='e', justify='right')
        difficulty_label.pack(side='left', padx=(10, 0))

        # Defines the startup position of the mode, as NORMAL
        difficulty_button = tk.Label(difficulty_container, text='NORMAL', font=("Tw Cen MT", 24, "bold"),
                                     fg=theme.WHITE, bg=theme.GRAY_BLACK, width=12, height=2, padx=20)
        difficulty_button.pack(side='left', padx=(10, 0))

        self.difficulty_colour = theme.GRADIENT[1]

        # Changes the difficulty if the mode dial is clicked #
        def difficulty_change():
            modes = ['easy', 'normal', 'hard', 'master']

            # Checks to see what the current difficulty is
            current_index = modes.index(difficulty_button["text"].lower())

            # If the current difficulty is 'master', set new difficulty to 'easy'
            # If current difficulty isn't 'master', go to next difficulty in 'modes' array
            if modes[-1] == difficulty_button["text"].lower():
                self.game.difficulty = modes[0]
            else:
                self.game.difficulty = modes[current_index + 1]

            # Sets the new button text and look to match new difficulty
            self.difficulty_colour = theme.GRADIENT[modes.index(self.game.difficulty)]
            difficulty_button["bg"] = self.difficulty_colour
            difficulty_button["text"] = self.game.difficulty.upper()

        # Binds event handlers (aesthetic and click) to the difficulty toggle
        difficulty_button.bind("<Enter>", lambda event: difficulty_button.config(bg=self.difficulty_colour))
        difficulty_button.bind("<Leave>", lambda event: difficulty_button.config(bg=theme.GRAY_BLACK))
        difficulty_button.bind("<Button-1>", lambda event: difficulty_change())

        # Container for buttons 'RESET BOARD' and 'GO!'
        info_frame = tk.Frame(right_container, bg=theme.GRAY_LIGHT, width=220, height=230)
        info_frame.pack()
        info_frame.pack_propagate(0)

        # Function to be called when board is reset #
        def reset_board():

            # Wipes everything off the main grid
            self.main_grid.update_canvas()

            # Sets current selection to none
            self.main_grid.selection = []
            self.main_grid.selection_length = 0
            self.main_grid.selection_dir = 'h'

            # Resets states of all ships in ship container
            for ship in self.ships:
                ship.selected = False
                ship.unhover(None)

        # Creates 'RESET BOARD' button
        reset_board_button = CustomButton(info_frame, text="RESET BOARD", height=40, width=200, align='center',
                                          colour=theme.ORANGE, fg=theme.ORANGE_DARK, active=theme.ORANGE_DIM,
                                          font=("Tw Cen MT", 20, "bold"), bg_canvas=theme.GRAY_LIGHT)
        reset_board_button.pack(pady=10)
        reset_board_button.bind_to_click(reset_board)

        # Function to be called when game is to start #
        def start_game():

            # Checks if all ships have been placed (by checking if there are any
            # unselected ships in ships container), creates popup if not true
            for ship in self.ships:
                if ship.selected == False:
                    popup = Popup(parent, text="All ships must be placed!", bg=theme.RED, fg="white")
                    break

            # Sets player ships to setup grid's current custom layout
            # Auto-generates a new layout for the computer (based on computer_logic brain)
            else:
                self.game.add_player_ships(self.main_grid.selection)
                self.game.add_computer_ships(self.game.computer_logic.generate_layout())

                # Switches the app screen to 'game' window with created game
                switch_screen('game', args=self.game)

        # Creates 'GO!' button
        start_game_button = CustomButton(info_frame, text="GO!", height=150, width=200,
                                         colour=theme.GREEN, fg=theme.GREEN_DARK, active=theme.GREEN_DIM,
                                         font=("Tw Cen MT", 40, "bold"), bg_canvas=theme.GRAY_LIGHT)
        start_game_button.bind_to_click(start_game)
        start_game_button.pack(pady=(0, 10))

        # Control frame is a container for any application related queries
        # like exiting from the game or going back to startup splash
        control_frame = tk.Frame(right_container, bg=theme.GRAY_LIGHT, width=220, height=60)
        control_frame.pack(pady=10)

        # Back to splash – child of control frame
        back_button = CustomButton(control_frame, text="⏎", width=120, height=40,
                                   colour=theme.GOLD, fg=theme.WHITE, active=theme.GOLD_DARK,
                                   bg_canvas=theme.GRAY_LIGHT)
        back_button.place(x=10, y=51, anchor='sw')
        back_button.bind_to_click(lambda: switch_screen('splash'))

        # Close entire application – child of control frame
        close_button = CustomButton(control_frame, text="✘", width=70, height=40,
                                    colour=theme.RED, fg=theme.WHITE, active=theme.RED_DIM,
                                    bg_canvas=theme.GRAY_LIGHT)
        close_button.place(x=210, y=51, anchor="se")
        close_button.bind_to_click(lambda: root.destroy())


### The main Game Window ###
class GameWindow(tk.Frame):
    ### NB: The GameWindow frame is split into 3 main column areas.
    # The first column area is for the progress bar.
    # The second column area is for the main game grid and ships container
    # The third column area is for the display grid, as well as the game stats
    ###

    def __init__(self, parent, game):
        super().__init__(parent)

        theme = Colours(manager.theme)
        self.game = game

        # Left container for the progress bar and text #
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


        # Middle container for the grid and ships #
        main_container = tk.Frame(self, bg=theme.WHITE)
        main_container.grid(column=1, row=0, padx=10, pady=15)

        # Computer's grid (the grid that the player tries to find ships on)
        self.main_grid = CustomGrid(main_container, multiplier=4,
                                    progress_bar=self.progress_bar, bottom_hidden=True,
                                    is_game_board=True, game=self.game, owner='computer')
        self.game.computer_board = self.main_grid
        self.main_grid.pack()

        # Filler space for aesthetic purpose, contains last hit coord
        bottom_filler = tk.Frame(main_container, width=int(self.main_grid["width"]), height=130,
                                 highlightthickness=0, bg=theme.GRAY_DARK)
        bottom_filler.pack_propagate(0)
        bottom_filler.pack(pady=(0, 10))

        # Last location that the player has hit
        last_location = tk.Label(bottom_filler, text="––",
                                 fg=theme.WHITE, bg=theme.GRAY_BLACK,
                                 font=("Tw Cen MT", 60, "bold"), height=2, width=4)

        # Links the last_location label with the main_grid's logic
        self.main_grid.linked_coordinate = last_location

        last_label = tk.Label(bottom_filler, text="Last Location", fg=theme.WHITE, bg=theme.GRAY_DARK,
                              font=("Tw Cen MT", 24, "bold"))
        last_location.pack(side='left')
        last_label.pack(side='left', padx=20)


        # Right container for the small grid and button/info display #
        right_container = tk.Frame(self)
        right_container.grid(column=2, row=0, sticky='n', pady=15)

        # Container for the player's grid
        small_grid_container = tk.Frame(right_container)
        small_grid_container.pack(side='top', pady=(0, 10))

        # Player's grid
        self.small_grid = CustomGrid(small_grid_container, multiplier=2, progress_bar=None,
                                     disabled=True, bottom_hidden=True, game=self.game, owner='player')
        self.game.player_board = self.small_grid
        self.small_grid.pack(side='top')

        # Shows all the ships on the board
        self.small_grid.show_hidden_ships()

        # Information container that belongs to the player's grid
        small_grid_info = tk.Frame(small_grid_container, width=220, height=40, bg=theme.GRAY_BLACK)
        small_grid_info.pack()
        small_grid_info.grid_propagate(0)

        # Generic text – static
        tk.Label(small_grid_info, text="YOUR\nTERRITORY", justify='right',
                             font=("Tw Cen MT", 13, "bold"), fg=theme.WHITE,
                             bg=theme.GRAY_BLACK).grid(column=0, row=0, sticky='w', padx=10)

        tk.Label(small_grid_info, text="HIT", fg=theme.WHITE, bg=theme.GRAY_BLACK,
                 font=("Tw Cen MT", 12, "bold")).grid(column=2, row=0, sticky='e',
                                                      padx=(5, 0), pady=(14, 0))

        # Percentage of player ships sunk
        percentage_text = tk.Label(small_grid_info, text="0.00%", fg=theme.GREEN, bg=theme.GRAY_BLACK,
                                   font=("Tw Cen MT", 30, "bold"))
        percentage_text.grid(column=1, row=0, sticky='e')
        self.small_grid.linked_percentage = percentage_text

        # Stats about the current difficulty mode
        small_grid_details = tk.Frame(small_grid_container, width=220, height=130,
                                      bg=theme.GRAY_LIGHT, highlightthickness=10, highlightbackground=theme.GRAY)
        small_grid_details.pack()
        small_grid_details.pack_propagate(0)

        # Array of all details display text about the difficulty stats
        details = ['>bCURRENT STATS',
                   'Games won:       {1} out of {0}\n'
                   'Games lost:        {2} out of {0}'.format(manager.stats[self.game.difficulty][0] + manager.stats[self.game.difficulty][1],
                                                              manager.stats[self.game.difficulty][0],
                                                              manager.stats[self.game.difficulty][1]),
                   'Difficulty:  {}'.format(game.difficulty.upper())]

        # Defines custom font types for the window
        fonts = {">b": ("Tw Cen MT", 14, "bold"),
                 "default": ("Tw Cen MT", 14)}

        # Creates a frame with labels for every details text
        longlabel = CustomLongText(small_grid_details, text=details,
                                   fg=theme.GRAY_BLACK, bg=theme.GRAY_LIGHT,
                                   width=200, height=110, fonts=fonts)
        longlabel.pack(pady=15)

        # Container for who's turn it currently is
        info_frame = tk.Frame(right_container, bg=theme.GRAY_BLACK, width=220, height=100)
        info_frame.pack()
        info_frame.pack_propagate(0)

        # Label for who's turn it currently is
        turn_status = tk.Label(info_frame, text="PLAYER's", fg=theme.RED,
                               font=("Tw Cen MT", 30, "bold"), width=12)
        turn_status.pack(side='top', pady=(20, 0), ipady=5)

        # Links the game's turn status to the label created above
        self.game.status = turn_status

        # Generic text – static
        tk.Label(info_frame, text="TURN", fg=theme.GRAY_LIGHT,
                 font=("Tw Cen MT", 14, "bold"), bg=theme.GRAY_BLACK).pack()

        # Control frame with options to resign and close game
        control_frame = tk.Frame(right_container, bg=theme.GRAY_LIGHT, width=220, height=60)
        control_frame.pack(pady=10)

        # Button to resign from game (default loss)
        resign_button = CustomButton(control_frame, text="⚑", width=120, height=40,
                                    colour=theme.GOLD, fg=theme.WHITE, active=theme.GOLD_DARK,
                                    bg_canvas=theme.GRAY_LIGHT)
        resign_button.place(x=10, y=51, anchor='sw')
        resign_button.bind_to_click(lambda: self.game.check_win(override=True))


        # Function called when 'close_button' is clicked. Creates a popup #
        # asking whether or not player wishes to save the game. #
        def close():
            background = theme.GRAY_BLACK

            # Creates popup
            popup = Popup(root, text="Do you wish to save this game?",
                          subtext="Note: Oldest game will be deleted if memory is full.",
                          bg=background, fg=theme.WHITE, stay=True)
            popup["height"] = 140

            # Sets the coordinates of where the main and subtext of the popup appear
            # Purpose: To make room for the yes/no buttons
            popup.coords(popup.main, int(popup["width"]) / 2, 35)
            popup.coords(popup.sub, int(popup["width"]) / 2, 60)

            # Container for the buttons
            container = tk.Frame(bg=background)

            # Creates a 'Yes' button, for saving the game.
            save = CustomButton(container, text="Yes", colour=theme.GREEN, fg=theme.WHITE,
                                       active=theme.GREEN_DARK, bg_canvas=background,
                                       width=200, height=40)

            # Creates a 'No' button, for abandoning the game
            close = CustomButton(container, text="No", colour=theme.RED, fg=theme.WHITE,
                                        active=theme.RED_DIM, bg_canvas=background,
                                        width=200, height=40)

            # Function called when any button is clicked, saves game (if applicable)
            # and returns back to startup splash
            def return_to_splash(save):
                if save:

                    # Gets a summary data packet of the current game, saves to manager
                    # and exports save data to a file (saves.bts)
                    data = self.game.get_data_summary()
                    manager.save_game(data)
                    manager.export_to_file()

                # Destroys the popup and the container, returns to splash
                popup.destroy()
                container.destroy()
                switch_screen('splash')

            # Binds clicks of Yes/No buttons to 'return_to_splash' function
            close.bind_to_click(lambda: return_to_splash(save=False))
            save.bind_to_click(lambda: return_to_splash(save=True))

            save.pack(side='left', padx=10)
            close.pack(side='right', padx=10)

            # Places the button container just below the main and subtexts and popup
            container.place(x=root.winfo_width() / 2, y=root.winfo_height() / 2 + 35, anchor='center')

            # Destroys the popup window after 10 seconds if no activity happens.
            root.after(10000, container.destroy)

        # Creates the close_button
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

        # The following (up to #####) links to different elements #
        # in other classes for access to different information #

        # Structured as individual ships (with alpha-num coords), links to the playing grids
        self.player_ships = []
        self.player_remaining_ships = []

        self.computer_ships = []
        self.computer_remaining_ships = []

        # Structured as alpha-num coords, links to the playing grids
        self.player_board_hit = []
        self.computer_board_hit = []

        # Boards are linked to the 'playing grids' in GameWindow
        self.player_board = None
        self.computer_board = None

        # Status is linked to 'turn status' in GameWindow
        self.status = None

        #####

        # Defines the computer's brain for move/layout generation
        self.computer_logic = ComputerLogic()

    ## Sets the ships on player's board to the layout from setup ##
    def add_player_ships(self, ships_array):
        self.player_ships = copy.deepcopy(ships_array)
        self.player_remaining_ships = copy.deepcopy(ships_array)

    ## Sets out predefined ships for computer's board ##
    def add_computer_ships(self, ships_array):
        self.computer_ships = copy.deepcopy(ships_array)
        self.computer_remaining_ships = copy.deepcopy(ships_array)

    ## Sets the game grids (from the GameWindow class) for access to data ##
    def set_boards(self, player_board, computer_board):
        self.player_board = player_board
        self.computer_board = computer_board

    ## Exporting game data ##
    def get_data_summary(self):
        data = {"difficulty": self.difficulty, "date": self.date,
                "player_ships": self.player_ships,
                "player_hit": self.player_board_hit,

                "computer_ships": self.computer_ships,
                "computer_hit": self.computer_board_hit,
                "computer_cache": self.computer_logic.cached_ship_coords}

        return data

    ## Imports all the game data ##
    def import_data(self, data):
        self.difficulty = data["difficulty"]

        self.add_player_ships(data["player_ships"])
        self.player_board_hit = data["player_hit"]

        self.add_computer_ships(data["computer_ships"])
        self.computer_board_hit = data["computer_hit"]
        self.computer_logic.cached_ship_coords = data["computer_cache"]

        self.computer_logic.set_hit_spaces(self.player_board_hit)

    ## After any position is played (coord in alpha-num) ##
    #   – Returns who's turn it is after the play
    #   – Makes necessary changes to ship variables (if any are hit)
    ##
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

                # Sets the current turn to 'COMPUTERS'
                self.status["text"] = "COMPUTER's"
                self.status["fg"] = self.theme.GOLD

                hit_coord = None
                counter = 0
                max = {'easy': 1,
                       'normal': 2,
                       'hard': 3,
                       'master': 4}.get(self.difficulty, 1)

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

                # Plays the coordinate previously generated after 1 second (to simulate 'thinking')
                def next(): self.player_board.hit(None, self.player_board.coord_to_rect(hit_coord), override=True)
                root.after(1000, next)

                # Returns that the next move is on the player's board (i.e computer's turn)
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

                    # Generates a new hit coordinate based on previously hit coordinate
                    hit_coord = CoordUtils.convert_type(self.computer_logic.square_hit(coord, sunk=ship_sunk, ship=current_ship))

                    # Plays predefined coordinate after 1s (simulates 'thinking' time)
                    def next(): self.player_board.hit(None, self.player_board.coord_to_rect(hit_coord), override=True)
                    root.after(1000, next)

                    return(board_name, ship_sunk, current_ship)

            # Didn't hit a ship
            else:

                # Sets turn status
                self.status["text"] = "PLAYER's"
                self.status["fg"] = self.theme.RED
                self.turn_counter = 0

                # Makes the main grid disabled (as it's computer's turn)
                self.computer_board.disabled = False
                return ('computer',)

    ## Check if all remaining occupied squares are hit – backend ##
    def check_win(self, override=False):

        # If game is already over, no point in creating
        # another popup so just returns nothing
        if self.game_over:
            return

        # Sets the current result to override
        result = override
        bg_colour = self.theme.GREEN_DIM

        # If the length of player ships is 0, make computer the winner
        for ship in self.player_remaining_ships:
            if len(ship) > 0: break
        else:

            # Sets result outcome to computer
            result = 'computer'
            print(">>> Player lost!")

            # Increment manager 'loss' stat of current difficulty by 1
            self.manager.stats[self.difficulty][1] += 1
            bg_colour = self.theme.RED

        # If the length of computer ships is 0, make player the winner
        for ship in self.computer_remaining_ships:
            if len(ship) > 0: break
        else:
            result = 'player'
            print(">>> Player wins!")

            # Increments win stat of current difficulty by 1
            self.manager.stats[self.difficulty][0] += 1


        # If player resigns (i.e override = True)
        if result and result not in ("player", "computer"):
            print(">>> Player resigns.")

            # Increments loss stat of current difficulty by 1
            self.manager.stats[self.difficulty][1] += 1
            bg_colour = self.theme.RED

        # If result isn't false (i.e game is over)
        if result:

            # Save information to file
            manager.export_to_file()

            # Sets game over variable to true
            self.game_over = True

            # Makes a result popup appear after 1.2s
            def popup_appear():
                # Switches the screen to startup 'splash' window
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
#####
class ComputerLogic(object):
    def __init__(self):

        # Alpha-num list of coordinates on the board that have yet to be hit
        self.grid = []

        for x in range(10):
            for y in range(10):
                self.grid.append(CoordUtils.convert_type(x + 1) + str(y + 1))

        # Alpha-num list of coordinates with ships
        self.cached_ship_coords = []

    ## Returns a coordinate that has yet to be hit, in alpha-num form ##
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

                    # Checks to see if any sides are linked (i.e contains a previously hit ship)
                    # and appends it to linked sides. Also creates a copy of sides (converted_sides)
                    # in which the type has been converted to alpha-num form
                    for side in sides:
                        if side: converted_sides.append(CoordUtils.convert_type(side))
                        else: converted_sides.append(None)

                        if side and CoordUtils.convert_type(side) in self.cached_ship_coords:
                            linked_sides.append(CoordUtils.convert_type(side))

                    # If the two hit spaces aren't 'connected', choose random side
                    #   – This shouldn't happen, but if it does... backup redundancy
                    if len(linked_sides) == 0:
                        while True:

                            # Randomly choose a target based on a surrounding coordinate
                            target = random.choice(converted_sides)

                            # If the target choosen is in the computer's grid
                            if target and target in self.grid:
                                self.grid.remove(target)
                                return target

                    # If only one side of the hit square is hit
                    if len(linked_sides) == 1:
                        index = converted_sides.index(linked_sides[0])

                        # Checks which side the hit square is on, and hit on the opposite side
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

            # Append to potential_targets if the surrounding coordinate has yet to be hit
            for coord in surrounding_coords:
                if CoordUtils.convert_type(coord) in self.grid:
                    potential_targets.append(CoordUtils.convert_type(coord))

            # Hits the potential_target, else make a random choice
            if len(potential_targets) != 0:
                target = random.choice(potential_targets)
                self.grid.remove(target)

                return target
            else:
                self.cached_ship_coords = []
                return self.make_move()

    ## Note: "square" argument is for a coord in alpha-num form (i.e D4) ##
    def square_hit(self, coord, sunk=False, ship=None):

        # If the ship was sunk, removes sunk_ship_coordinates from the cache
        if sunk: self.cached_ship_coords = [coord for coord in self.cached_ship_coords if coord not in ship]

        # If ship wasn't sunk, add the hit coordinate to the cache
        else: self.cached_ship_coords.append(coord)

        next_move = self.make_move()
        return next_move

    ## Automatically generates the computer's layout ##
    def generate_layout(self):

        # Potential ship types
        ship_lengths = [2, 3, 3, 4, 5]
        direction = ['right', 'bottom']

        computer_ships = []
        coords = []

        # As long as there are still ships to make
        while len(ship_lengths) > 0:

            # Generates random coordinates
            x = random.randint(1, 10)
            y = random.randint(1, 10)

            length = random.choice(ship_lengths)

            # Gets the coordinates of the ship that will be created
            ship_coords = CoordUtils.get_coords_along_side((x, y), random.choice(direction), length)

            # If the new coordinates for the to-be-created ship exist, make it a thing
            # If they don't exist (i.e obstruct another ship or non-exist grid squares),
            # restart the loop. Process continues until all ships have been placed.
            if ship_coords:
                for coord in ship_coords:
                    if coord in coords:
                        break
                else:
                    # Adds new ship to temp 'computer_ships' variable
                    computer_ships.append(ship_coords)
                    [coords.append(coord) for coord in ship_coords]

                    # Removes the current ship length from the list of possible lengths
                    ship_lengths.remove(length)

        return computer_ships

    ## Updates the computer's grid memory by removing previously hit spces ##
    # Note: Coordinates to be in alpha-num form
    def set_hit_spaces(self, hit_spaces):
        for coord in hit_spaces:
            if coord in self.grid:
                self.grid.remove(coord)


### Manager for reading / writing to files for saving ###
class Manager(object):
    def __init__(self):
        self.saved_games = []

        # Note: [0] is wins, [1] is losses
        self.stats = {'easy': [0, 0],
                      'normal': [0, 0],
                      'hard': [0, 0],
                      'master': [0, 0]}

        # Defines theme as 'default' theme
        self.theme = "default"

    ## Export all saved games (3) and scores to file ##
    def export_to_file(self):

        # Writes/overwrites stats.bts file with new stats
        with open('bin/stats.bts', 'w') as file:
            file.write(str(self.stats))

        # Writes/overwrites saves.bts file with new stats
        with open('bin/saves.bts', 'w') as file:
            file.write(str(self.saved_games))

    ## Imports all saved games (3) and scores to memory ##
    def import_to_memory(self):

        # If stats.bts is a file, import everything from stats
        if os.path.isfile('bin/stats.bts'):
            with open('bin/stats.bts', 'r') as file:
                self.stats = eval(file.read())

        # If saves.bts is a file, import everything from saves
        if os.path.isfile('bin/saves.bts'):
            with open('bin/saves.bts', 'r') as file:
                self.saved_games = eval(file.read())

    ## Resets the scores to 0 ##
    def reset_scores(self):
        self.stats = {'easy': [0, 0],
                      'normal': [0, 0],
                      'hard': [0, 0],
                      'master': [0, 0]}
        self.export_to_file()

    ## Replaces old games if all saves are full ##
    def save_game(self, game_data):

        # If current length of saves is greater than 2 (3 or more), delete oldest
        if len(self.saved_games) > 2:
            del self.saved_games[0]

        # Add new save
        self.saved_games.append(game_data)


if __name__ == "__main__":

    # Defines the manager for the application
    manager = Manager()
    manager.import_to_memory()

    root = tk.Tk()

    # Defines starting layout
    root.wm_geometry("850x600")
    root.wm_resizable(0, 0)
    root.wm_title("Battleships V{:.2f} beta".format(version))

    root["bg"] = 'white'

    # The 'frame' that's displayed on the application window
    current_screen = None

    # Makes main window appear as startup splash
    switch_screen('splash')

    root.mainloop()

    # Exports manager stats and saves to file if application is closed.
    manager.export_to_file()
