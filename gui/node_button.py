import tkinter as tk
from functools import partial

from game.node import Node, NodeState


class NodeButton:
    node_state_to_color_mapping = {

    }

    _node_label_names = {
        "state": "state",
        "total_distance": "total_distance",
        "distance_to_source": "distance_to_source",
        "distance_to_target": "distance_to_target",
    }

    def __init__(self, master, node: Node, on_click_callback):
        self._node: Node = node
        self._on_click_callback = on_click_callback

        # button frame
        self._frm: tk.Frame = tk.Frame(master=master, width=500, height=500, relief=tk.GROOVE, borderwidth=1)
        self._frm.grid(row=self._node.x, column=self._node.y)
        self._frm.bind("<Button-1>", partial(self._on_click_callback, button=self))

        # state label
        self._lbl_state = tk.Label(master=self._frm, text=f'{self._node.state.name or ""}', width=4)
        self._lbl_state.grid(row=0, column=0, sticky="nsew")
        self._lbl_state.bind("<Button-1>", partial(self._on_click_callback, button=self))

        # total distance label
        self._lbl_total_distance = tk.Label(master=self._frm, text=f'{self.float_to_string(self._node.total_distance)}',
                                            width=4)
        self._lbl_total_distance.grid(row=0, column=1, sticky="nsew")
        self._lbl_total_distance.bind("<Button-1>", partial(self._on_click_callback, button=self))

        # distance to source label
        self._lbl_distance_to_source = tk.Label(master=self._frm,
                                                text=f'{self.float_to_string(self._node.distance_to_source)}', width=4)
        self._lbl_distance_to_source.grid(row=1, column=0, sticky="nsew")
        self._lbl_distance_to_source.bind("<Button-1>", partial(self._on_click_callback, button=self))

        # distance to target label
        self._lbl_distance_to_target = tk.Label(master=self._frm,
                                                text=f'{self.float_to_string(self._node.distance_to_target)}', width=4)
        self._lbl_distance_to_target.grid(row=1, column=1, sticky="nsew")
        self._lbl_distance_to_target.bind("<Button-1>", partial(self._on_click_callback, button=self))

        # set button to white
        self.update_color(color="white")

    @property
    def node(self):
        return self._node

    @property
    def lbl_state(self):
        return self._lbl_state

    def update_lbl_state(self, state: NodeState = None):
        self._lbl_state['text'] = self._node.state.name if state is None else state.name
        self.update_color(color=self._node.state.value if state is None else state.value)

    @property
    def lbl_total_distance(self):
        return self._lbl_total_distance

    def update_lbl_total_distance(self, value=None):
        self.lbl_total_distance['text'] = f'{self.float_to_string(value or self._node.total_distance)}'

    @property
    def lbl_distance_to_source(self):
        return self._lbl_distance_to_source

    def update_lbl_distance_to_source(self, value=None):
        self._lbl_distance_to_source['text'] = f'{self.float_to_string(value or self._node.distance_to_source)}'

    @property
    def lbl_distance_to_target(self):
        return self._lbl_distance_to_target

    def update_lbl_distance_to_target(self, value=None):
        self._lbl_distance_to_target['text'] = f'{self.float_to_string(value or self._node.distance_to_target)}'

    def float_to_string(self, value: float) -> str:
        return '' if value is None else f'{value:.2f}'

    def update_all(self):
        self.update_lbl_state()
        self.update_lbl_total_distance()
        self.update_lbl_distance_to_source()
        self.update_lbl_distance_to_target()

    def update_color(self, color: str):
        self._lbl_state['bg'] = color
        self._lbl_total_distance['bg'] = color
        self._lbl_distance_to_source['bg'] = color
        self._lbl_distance_to_target['bg'] = color
