import asyncio
import logging
import time
import tkinter as tk
from threading import Timer
from typing import List

from game.a_star import AStar
from game.board import Board
from game.game_state import GameState
from game.node import NodeState, Node
from gui.node_button import NodeButton

logger = logging.getLogger(__name__)


class PathFinder:
    _border_effects = {
        "flat": tk.FLAT,
        "sunken": tk.SUNKEN,
        "raised": tk.RAISED,
        "groove": tk.GROOVE,
        "ridge": tk.RIDGE,
    }

    _button_names = {
        "reset": "Reset",
        "board_size": "Set Size",
        "source": "Set Source",
        "target": "Set Target",
        "blocked": "Set Blocked",
        "game_next": "Next",
        "game_fast_forward": "Fast Forward",
    }

    _default_values = {
        "rows": 5,
        "columns": 5,
    }

    _colors = {
        "default": 'SystemButtonFace',
        "warning": 'red',
    }

    _prompt_strings = {
        "board_size": "Set the number of rows and columns for the board.",
        "source": "Select a cell to be the source.",
        "target": "Select a cell to be the target.",
        "blocked": "Select which cells should be blocked.",
        "start_game": "Find path with least steps using A* search algorithm. Press next to iterate."
    }

    def __init__(self):
        self._game_state = GameState.CLEAN

        # window variables
        self._window: tk.Tk = None

        # prompt variables
        self._lbl_prompt: tk.Label = None
        self._prompt: tk.StringVar = None

        # frame board variables
        self._frm_board: tk.Frame = None

        # board buttons
        self._board_node_buttons: List[List[NodeButton]] = None

        # backend board
        self._setup_candidates = {
            "source": None,
            "target": None,
            "blocked": [],
        }
        self._board: Board = None

        # astar algo
        self._astar: AStar = None

        # setup game
        self._setup()

    @property
    def game_state(self):
        return self._game_state

    @game_state.setter
    def game_state(self, game_state: GameState):
        self._game_state = game_state

    def _setup(self):
        # setup window
        self._window = tk.Tk()
        self._window.title("Path Finder")
        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(2, minsize=500)

        # setup prompt frame
        self._frm_prompt = tk.Frame(master=self._window, name='prompt',
                                    relief=self._border_effects["groove"], borderwidth=1)
        self._frm_prompt.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self._frm_prompt.rowconfigure(0, weight=1)
        self._frm_prompt.columnconfigure(0, weight=1)

        # setup prompt label
        self._lbl_prompt = tk.Label(master=self._frm_prompt, text='<Temporary Placeholder>')
        self._lbl_prompt.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        # setup context menu frame
        self._frm_context_menu = tk.Frame(master=self._window, name='context_menu',
                                          relief=self._border_effects["groove"], borderwidth=1)
        self._frm_context_menu.grid(row=0, column=0, sticky="nsew")
        self._frm_context_menu.rowconfigure(0, weight=1)

        # setup reset frame
        self._frm_reset = tk.Frame(master=self._window, name='reset',
                                   relief=self._border_effects["groove"], borderwidth=1)
        self._frm_reset.grid(row=0, column=1, sticky="nsew")
        self._frm_reset.rowconfigure(0, weight=1)
        self._frm_reset.columnconfigure(0, weight=1)

        # setup reset button
        self._btn_reset = tk.Button(master=self._frm_reset, text=self._button_names["reset"],
                                    width=10, command=self._reset_game)
        self._btn_reset.grid(row=0, column=0)

        # setup board frame
        self._frm_board = tk.Frame(master=self._window, name='board',
                                   relief=self._border_effects["groove"])
        self._frm_board.grid(row=2, column=0, columnspan=2)

        # setup legend frame
        self._frm_legend = tk.Frame(master=self._window, name='legend',
                                    relief=self._border_effects["groove"], borderwidth=1)
        self._frm_legend.grid(row=0, column=2, rowspan=2)

        self._lbl_legend_title = tk.Label(master=self._frm_legend, text="Legend", font=("Arial", 10, "bold"))
        self._lbl_legend_title.grid(row=0, column=0, columnspan=2)
        self._lbl_legend_state = tk.Label(master=self._frm_legend, text="Status", font=("Arial", 10))
        self._lbl_legend_state.grid(row=1, column=0)
        self._lbl_legend_state = tk.Label(master=self._frm_legend, text="(Est.) Total Distance", font=("Arial", 10))
        self._lbl_legend_state.grid(row=1, column=1)
        self._lbl_legend_state = tk.Label(master=self._frm_legend, text="(Est.) Dist. to Source", font=("Arial", 10))
        self._lbl_legend_state.grid(row=2, column=0)
        self._lbl_legend_state = tk.Label(master=self._frm_legend, text="(Est.) Dist. to Target", font=("Arial", 10))
        self._lbl_legend_state.grid(row=2, column=1)

        # start by asking user for number of rows and columns
        self._show_setup_board_size()

        # listen for events
        self._window.mainloop()

    def _show_setup_board_size(self):
        """
        display gui for setting up board size
        """
        self.game_state = GameState.SETUP_BOARD_SIZE_BEGIN

        # update prompt
        self._update_prompt(self._prompt_strings["board_size"])

        # setup rows frame
        self._frm_rows = tk.Frame(master=self._frm_context_menu, name='rows')
        self._frm_rows.grid(row=0, column=0, sticky="w")

        # setup rows label
        self._lbl_rows = tk.Label(master=self._frm_rows, text="Rows:", font=("Arial", 14, "bold"))
        self._lbl_rows.grid(row=0, column=0)

        # setup rows entry
        rows_default_value = tk.IntVar()
        rows_default_value.set(self._default_values["rows"])
        self._ent_rows = tk.Entry(master=self._frm_rows, text=rows_default_value, width=5, justify='right')
        self._ent_rows.grid(row=0, column=1)

        # setup columns frame
        self._frm_columns = tk.Frame(master=self._frm_context_menu, name='columns')
        self._frm_columns.grid(row=0, column=1, sticky="w")

        # setup columns label
        self._lbl_columns = tk.Label(master=self._frm_columns, text="Columns:", font=("Arial", 14, "bold"))
        self._lbl_columns.grid(row=0, column=0)

        # setup columns entry
        columns_default_value = tk.IntVar()
        columns_default_value.set(self._default_values["columns"])
        self._ent_columns = tk.Entry(master=self._frm_columns, text=columns_default_value, width=5,
                                     justify='right')
        self._ent_columns.grid(row=0, column=1)

        # setup board button
        self._btn_board_size_set = tk.Button(master=self._frm_context_menu, text=self._button_names["board_size"],
                                             width=10, command=self._btn_setup_board_size_on_click)
        self._btn_board_size_set.grid(row=0, column=4)

    def _btn_setup_board_size_on_click(self) -> None:
        """
        called when self._btn_action is pressed
        """
        # get rows and columns input from respective entries
        try:
            rows = int(self._ent_rows.get())
        except:
            raise ValueError('Rows value is not an int.')
        else:
            try:
                columns = int(self._ent_columns.get())
            except:
                raise ValueError('Columns value is not an int.')
            else:
                # setup board
                self._board = Board(rows=rows, columns=columns)

                # draw board
                self._show_board(rows=rows, columns=columns)

                self._hide_setup_board_size()

    def _hide_setup_board_size(self):
        """
        hide gui for setting up board size
        """
        # clear context menu
        self._clear_context_menu()

        self.game_state = GameState.SETUP_BOARD_SIZE_END

        # go to block nodes setup
        self._show_setup_source()

    def _show_setup_source(self) -> None:
        """
        show gui for setting up source node
        """
        self.game_state = GameState.SETUP_SOURCE_BEGIN

        # update prompt
        self._update_prompt(prompt=self._prompt_strings["source"])

        # setup target button
        self._btn_source_set = tk.Button(master=self._frm_context_menu, text=self._button_names["source"], width=10,
                                         command=self._btn_setup_source_on_click)
        self._btn_source_set.grid(row=0, column=0)

    def _btn_setup_source_on_click(self) -> None:
        source_candidate_button: NodeButton = self._setup_candidates["source"]

        # no source has been set
        if source_candidate_button is None:
            self._show_setup_source()
            self._update_prompt("A source cell is required. " + self._prompt_strings["source"],
                                color=self._colors['warning'])

        else:
            self._board.set_source_node(row=source_candidate_button.node.x, column=source_candidate_button.node.y)

            self._hide_setup_source()

    def _hide_setup_source(self) -> None:
        """
        hide gui for setting up source node
        """
        self._clear_context_menu()

        self.game_state = GameState.SETUP_SOURCE_END

        self._show_setup_target()

    def _show_setup_target(self) -> None:
        """
        show gui for setting up target node
        """
        self.game_state = GameState.SETUP_TARGET_BEGIN

        # update prompt
        self._update_prompt(prompt=self._prompt_strings["target"])

        # setup target button
        self._btn_target_set = tk.Button(master=self._frm_context_menu, text=self._button_names["target"], width=10,
                                         command=self._btn_setup_target_on_click)
        self._btn_target_set.grid(row=0, column=0)

    def _btn_setup_target_on_click(self) -> None:
        target_candidate_button: NodeButton = self._setup_candidates["target"]

        # no target has been set
        if target_candidate_button is None:
            self._show_setup_target()
            self._update_prompt("A target cell is required. " + self._prompt_strings["target"],
                                color=self._colors['warning'])

        else:
            self._board.set_target_node(row=target_candidate_button.node.x, column=target_candidate_button.node.y)

            self._hide_setup_target()

    def _hide_setup_target(self) -> None:
        """
        hide gui for setting up target node
        """
        self._clear_context_menu()

        self.game_state = GameState.SETUP_TARGET_END

        self._show_setup_blocked()

    def _show_setup_blocked(self) -> None:
        """
        show gui for setting up blocked nodes
        """
        self.game_state = GameState.SETUP_BLOCKED_BEGIN

        # update prompt
        self._update_prompt(prompt=self._prompt_strings["blocked"])

        # setup blocked button
        self._btn_set_blocked = tk.Button(master=self._frm_context_menu, text=self._button_names["blocked"], width=10,
                                          command=self._btn_setup_blocked_on_click)
        self._btn_set_blocked.grid(row=0, column=0)

    def _btn_setup_blocked_on_click(self):
        for blocked_button in self._setup_candidates["blocked"]:
            self._board.set_blocked_node(row=blocked_button.node.x, column=blocked_button.node.y)

        self._hide_setup_blocked()

    def _hide_setup_blocked(self):
        """
        hide gui for setting up blocked nodes
        """
        self._clear_context_menu()

        self.game_state = GameState.SETUP_BLOCKED_END

        self._start_game()

    def _start_game(self):
        self.game_state = GameState.START

        # update prompt
        self._update_prompt(prompt=self._prompt_strings["start_game"])

        # setup game next button
        self._btn_game_next = tk.Button(master=self._frm_context_menu, text=self._button_names["game_next"], width=10,
                                        command=self._btn_game_next_on_click)
        self._btn_game_next.grid(row=0, column=0)

        # setup game fast forward button
        self._btn_game_fast_forward = tk.Button(master=self._frm_context_menu,
                                                text=self._button_names["game_fast_forward"], width=10,
                                                command=self._btn_game_fast_forward_on_click)
        self._btn_game_fast_forward.grid(row=0, column=1)

        # setup astar
        self._astar = AStar(board=self._board)

    def _btn_game_next_on_click(self):
        current_node, updated_neighbor_nodes = self._astar.next()

        # still searching for optimal path
        if updated_neighbor_nodes is not None:
            self._board_node_buttons[current_node.x][current_node.y].update_all()

            for neighbor_node in updated_neighbor_nodes:
                self._board_node_buttons[neighbor_node.x][neighbor_node.y].update_all()

        # no more possible nodes to explore, board has no path from source to target
        elif current_node is None:
            self.game_state = GameState.FINISH

            # TODO: handle no solution

        # optimal path found
        else:
            # display path
            path: List[Node] = self._astar.get_path()
            for path_node in path:
                self._board_node_buttons[path_node.x][path_node.y].update_lbl_state()

            # clear context menu
            self._clear_context_menu()

            self.game_state = GameState.FINISH

    def _btn_game_fast_forward_on_click(self):
        while self.game_state != GameState.FINISH:
            self._btn_game_next_on_click()

    def _reset_game(self):
        # delete context menu children
        for context_menu_slave in self._window.nametowidget('.context_menu').grid_slaves():
            context_menu_slave.destroy()

        # delete board children
        for board_slave in self._window.nametowidget('board').grid_slaves():
            board_slave.destroy()

        # clean up instance variables:
        self._board_node_buttons = None
        self._setup_candidates = {
            "source": None,
            "target": None,
            "blocked": [],
        }
        self._board: Board = None
        self._astar: AStar = None

        # reset game state
        self.game_state = GameState.RESET

        # restart setup
        self._show_setup_board_size()

    def _show_board(self, rows: int, columns: int) -> None:
        """
        show board of size rows x columns
        :param rows: row size of board to be built
        :param columns: column size of board to be built
        """
        # show board cells
        self._board_node_buttons = [[None for j in range(columns)] for i in range(rows)]
        for i in range(rows):
            for j in range(columns):
                self._board_node_buttons[i][j] = NodeButton(master=self._frm_board,
                                                            node=self._board.get_node(row=i, column=j),
                                                            on_click_callback=self._btn_board_node_on_click)

    def _hide_board(self):
        self._frm_board.destroy()

    def _btn_board_node_on_click(self, event: tk.Event, button: NodeButton):
        # need event arg to handle event from tk.Widget.bind, even if unused

        existing_source_candidate: NodeButton = self._setup_candidates["source"]
        existing_target_candidate: NodeButton = self._setup_candidates["target"]

        if self._game_state == GameState.SETUP_SOURCE_BEGIN:
            # unmark existing source candidate
            if existing_source_candidate is not None:
                existing_source_candidate.update_lbl_state(state=NodeState.OPEN)

            # mark new source candidate
            button.update_lbl_state(state=NodeState.SRCE)
            self._setup_candidates["source"] = button

        elif self._game_state == GameState.SETUP_TARGET_BEGIN:
            # source node cannot be target node
            if button == existing_source_candidate:
                self._update_prompt("The source cannot be the target. " + self._prompt_strings["target"])

            else:
                # unmark existing target node if exists
                if existing_target_candidate is not None:
                    existing_target_candidate.update_lbl_state(state=NodeState.OPEN)

                # selected a valid target
                button.update_lbl_state(state=NodeState.TRGT)
                self._setup_candidates["target"] = button

        elif self._game_state == GameState.SETUP_BLOCKED_BEGIN:
            # source node cannot be blocked
            if button == existing_source_candidate:
                self._update_prompt("The source cannot be blocked. " + self._prompt_strings["target"])

            # target node cannot be blocked
            elif button == existing_target_candidate:
                self._update_prompt("The target cannot be blocked. " + self._prompt_strings["target"])

            # unset existing blocked node
            elif button.lbl_state["text"] == NodeState.WALL.name:
                button.update_lbl_state(state=NodeState.OPEN)

            # selected a valid cell to be blocked
            else:
                button.update_lbl_state(state=NodeState.WALL)
                self._setup_candidates["blocked"].append(button)

        else:
            pass

    def _update_prompt(self, prompt: str, color='SystemButtonFace'):
        self._lbl_prompt['text'] = prompt

        if self._frm_prompt['bg'] != color or self._lbl_prompt['bg'] != color:
            self._frm_prompt['bg'] = color
            self._lbl_prompt['bg'] = color

    def _clear_context_menu(self):
        for slave in self._frm_context_menu.grid_slaves():
            slave.destroy()
