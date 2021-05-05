class State:
    def __init__(self):
        self.ax_index = 1
        self.numbers = {}

    def set_graph_infos(self, currency, candles, axs, graph_widget):
        self.currency = currency
        self.candles = candles
        self.axs = axs
        self.graph_widget = graph_widget
