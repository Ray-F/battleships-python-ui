import tkinter as tk
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


class SplashScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        theme = Colours(theme_selection)

        self.bar = tk.Frame(self, width=800, height=25, bg=theme.GRAY_DARK)
        self.bar.pack(side='top', pady=(60, 0))

        self.title = tk.Label(self, text="BATTLESHIPS", font=("Tw Cen MT", 100, "bold"), fg=theme.GRAY_DARK)
        self.title.pack(side='top', padx=(0, 250), pady=(20, 10))

        self.main_frame = tk.Frame(self, width=800, height=320, bg=theme.WHITE)
        self.main_frame.pack(side='bottom')

        self.main_frame.grid_propagate(0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=0)

        self.info_frame = tk.Canvas(self.main_frame, width=530, height=320, highlightthickness=0)
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

        self.info_window = self.info_frame.create_window(270, 160, window=rules_frame, anchor='center', tag='window')

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


### Frame for loading saves, inside the splash screen ###
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

        ### Left container for the progress bar and text
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


        ### Middle container for the grid and ships
        main_container = tk.Frame(self, bg=theme.WHITE)
        main_container.grid(column=1, row=0, padx=10, pady=15)

        self.main_grid = CustomGrid(main_container, multiplier=4,
                                    progress_bar=self.progress_bar, bottom_hidden=True, is_game_board=False)
        self.main_grid.pack()

        ships_container = tk.Canvas(main_container, width=int(self.main_grid["width"]), height=130,
                                    highlightthickness=0, bg=theme.GRAY_BLACK)

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


        ### Right container for the small grid and button/info display
        right_container = tk.Frame(self)
        right_container.grid(column=2, row=0, sticky='n', pady=15)

        small_grid_container = tk.Frame(right_container, bg=theme.GRAY_BLACK)
        small_grid_container.pack(side='top', pady=(0, 10))

        self.small_grid = CustomGrid(small_grid_container, multiplier=2, progress_bar=None, disabled=True, bottom_hidden=True)
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
                    popup = Popup(parent, text="All ships must be placed!", bg=theme.RED, fg="white", fill=0)
                    break
            else:
                self.game.player_ships = copy.deepcopy(self.main_grid.selection)
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

        ### Left container for the progress bar and text
        progress_container = tk.Frame(self, bg=theme.GRAY_LIGHT, height=570)
        progress_container.grid(column=0, row=0, sticky='n', pady=15)
        progress_container.pack_propagate(False)

        # Label for progress bar
        progress_label = tk.Label(progress_container, text="Opponent\nShips", font=("Tw Cen Mt", 24, "bold"),
                                  fg=theme.GRAY_DARK, bg=theme.GRAY_LIGHT)
        progress_label.pack(side='bottom', pady=(10, 20))

        # Actual progress bar
        self.progress_bar = ProgressBar(progress_container, direction="down",
                                        colours=(theme.RED, theme.RED_DARK), bg_canvas=theme.GRAY_LIGHT)
        self.progress_bar.pack(side='bottom')

        # Linking progress bar width to bounding countainer (progress_container)
        progress_container["width"] = int(self.progress_bar["width"]) + 20


        ### Middle container for the grid and ships
        main_container = tk.Frame(self, bg=theme.WHITE)
        main_container.grid(column=1, row=0, padx=10, pady=15)

        self.main_grid = CustomGrid(main_container, multiplier=4,
                                    progress_bar=self.progress_bar, bottom_hidden=True, is_game_board=True)
        self.main_grid.pack()

        self.ships_container = tk.Canvas(main_container, width=int(self.main_grid["width"]), height=130,
                                         highlightthickness=0, bg=theme.GRAY_DARK)

        self.ships_container.pack(pady=(0, 10))


        ### Right container for the small grid and button/info display
        right_container = tk.Frame(self)
        right_container.grid(column=2, row=0, sticky='n', pady=15)

        small_grid_container = tk.Frame(right_container)
        small_grid_container.pack(side='top', pady=(0, 10))

        self.small_grid = CustomGrid(small_grid_container, multiplier=2, progress_bar=None,
                                     disabled=True, bottom_hidden=True)

        #self.small_grid.add_ships(game.player_ships)
        #self.small_grid.show_hidden_ships()

        self.small_grid.pack(side='top')


        small_grid_info = tk.Frame(small_grid_container, width=220, height=40, bg=theme.GRAY_BLACK)
        small_grid_info.pack()
        small_grid_info.grid_propagate(0)

        # Text displayed in the small grid, static
        tk.Label(small_grid_info, text="YOUR\nTERRITORY", justify='right',
                             font=("Tw Cen MT", 13, "bold"), fg=theme.WHITE,
                             bg=theme.GRAY_BLACK).grid(column=0, row=0, sticky='w', padx=(5, 10))

        tk.Label(small_grid_info, text="HIT", fg=theme.WHITE, bg=theme.GRAY_BLACK,
                 font=("Tw Cen MT", 12, "bold")).grid(column=2, row=0, sticky='e',
                                                      padx=(5, 0), pady=(14, 0))

        # Percentage of player ships sunk, variable
        percentage_text = tk.Label(small_grid_info, text="0.00 %", fg=theme.GREEN, bg=theme.GRAY_BLACK,
                                   font=("Tw Cen MT", 30, "bold"))
        percentage_text.grid(column=1, row=0, sticky='e')


        small_grid_details = tk.Frame(small_grid_container, width=220, height=130, bg=theme.GRAY)
        small_grid_details.pack()

        info_frame = tk.Frame(right_container, bg=theme.GRAY_LIGHT, width=220, height=100)
        info_frame.pack()

        info_frame.pack_propagate(0)


        control_frame = tk.Frame(right_container, bg=theme.GRAY_LIGHT, width=220, height=60)
        control_frame.pack(pady=10)

        back_button = CustomButton(control_frame, text="⚑ ", width=120, height=40,
                                   colour=theme.GOLD, fg=theme.WHITE, active=theme.GOLD_DARK, bg_canvas=theme.GRAY_LIGHT)
        back_button.place(x=10, y=51, anchor='sw')

        close_button = CustomButton(control_frame, text="✘ ", width=70, height=40,
                                    colour=theme.RED, fg=theme.WHITE, active=theme.RED_DARK, bg_canvas=theme.GRAY_LIGHT)

        close_button.place(x=210, y=51, anchor="se")

        close_button.bind_to_click(lambda: root.destroy())


    def layout_setup(self):
        pass

    def create_card(self, container):
        pass



class Game(object):
    def __init__(self):
        self.user = ""
        self.difficulty = ""
        self.date = ""

        self.player_ships = []
        self.player_board_hit = []

        self.computer_ships = []
        self.computer_board_hit = []

    # Writing to a save file
    def export_data():
        pass


class Logic():
    def __init__(self):
        pass


if __name__ == "__main__":
    root = tk.Tk()

    root.wm_geometry("850x600")
    root.wm_resizable(0, 0)
    root.wm_title("Battleships V1.53 alpha")

    current_screen = None

    switch_screen('game')

    root.mainloop()
