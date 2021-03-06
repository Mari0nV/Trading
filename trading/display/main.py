import sys
import os
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QDockWidget,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMenuBar,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QTabWidget,
    QLabel
)
from trading.display.menu import Menu, IndicatorsToolBar
import finplot as fplt
import pyqtgraph as pg
import json

from trading.get_data import get_candle_data
from trading.display.plot import (
    create_fplt_widgets,
    plot_main_window,
    set_plot_colors
)
import trading.display.config as cfg
from trading.display.state import State


# Creating the main window
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Custom TradingView'
        self.left = 0
        self.top = 0
        self.width = cfg.WINDOW_WIDTH
        self.height = cfg.WINDOW_HEIGHT
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.state = State()
        self.setMenuBar(Menu(self, self.state))
        self.ind_toolbar = IndicatorsToolBar(self, self.state)
        self.addToolBar(self.ind_toolbar)

        self.central_widget = TabsWidget(self, self.ind_toolbar, self.state)
        self.setCentralWidget(self.central_widget)
        fplt.autoviewrestore()
        fplt.show(qt_exec=False)
        self.show()


class TabsWidget(QTabWidget):
    def __init__(self, parent, ind_toolbar, state):
        super(QTabWidget, self).__init__(parent)
        self.state = state
        self.layout = QVBoxLayout(self)
        self.candles = {}
        self.ind_toolbar = ind_toolbar
        self.nb_tabs = 0

        with open("trading/display/config.json", "r") as fp:
            self.config = json.load(fp)["config"]

        first = True
        for currency, indicators in self.config.items():
            tab = self.create_or_update_tab(f"{currency}", indicators)
            if first:
                active_currency = (currency, tab)
                first = False

        # Tab "+" to add new currency at runtime
        self.create_add_tab()

        self.state.set_graph_infos(
                currency=active_currency[0],
                candles=self.candles[active_currency[0]]["candles"],
                axs=self.candles[active_currency[0]]["axs"],
                graph_widget=active_currency[1]
            )
        self.setLayout(self.layout)
        self.currentChanged.connect(self.onChange)

    def create_add_tab(self):
        tab = QWidget()
        tab.layout = QVBoxLayout(self)
        tab.label = QLabel("+")
        self.addTab(tab, "+")
        self.nb_tabs += 1

    def create_or_update_tab(self, currency, indicators, from_tab=None):
        if not from_tab:
            tab = QWidget()
        else:
            tab = from_tab
        tab.layout = QVBoxLayout(self)
        tab.label = QLabel(currency)
        fplt_widgets = create_fplt_widgets(self.window())
        self.candles.setdefault(
            currency, {
                "candles": get_candle_data( 
                    currency,
                    begin=cfg.START_DATE,
                    end=cfg.END_DATE,
                    granularity=cfg.GRANULARITY
                    )
                }
            )
        tab.layout.addWidget(tab.label)
        tab.layout.addWidget(fplt_widgets[0].ax_widget, stretch=3)
        self.window().axs = fplt_widgets
        self.candles[currency]["axs"] = self.window().axs
        plot_main_window(self.candles[currency])
        tab.setLayout(tab.layout)
        if not from_tab:
            self.addTab(tab, currency)
            self.nb_tabs += 1
        self.state.set_graph_infos(
            currency=currency,
            candles=self.candles[currency]["candles"],
            axs=self.candles[currency]["axs"],
            graph_widget=tab
        )
        for indicator in indicators:
            params = indicator.split("-")
            ind = params[0]
            if len(params) > 1 and params[1].isnumeric():
                self.ind_toolbar.numbers[ind] = int(params[1])
            getattr(self.ind_toolbar, f"show_{ind}")()
        return tab

    def onChange(self, tab_index):
        if tab_index != self.nb_tabs - 1:
            currency = self.currentWidget().label.text()
            print("currency: ", currency)
            self.state.set_graph_infos(
                currency=currency,
                candles=self.candles[currency]["candles"],
                axs=self.candles[currency]["axs"],
                graph_widget=self.currentWidget()
            )
        else:
            currency, ok = QInputDialog.getText(self, "currency input dialog", "Enter currency")
            if ok:
                print(currency)
                self.create_add_tab()
                self.create_or_update_tab(f"{currency}", indicators=[], from_tab=self.currentWidget())
                self.setTabText(tab_index, currency)

if __name__ == '__main__':
    if os.path.exists("trading/display/tmp_config.json"):
        os.remove("trading/display/tmp_config.json")
    set_plot_colors()
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
