import sys
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QComboBox,
    QDockWidget,
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


currencies = ["ETHEUR", "BTCUSDT"]
begin = "2020-03-01 00:00:00"
end = "now"
granularity = "1d"


# Creating the main window
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Custom TradingView'
        self.left = 0
        self.top = 0
        self.width = 1200
        self.height = 800
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setMenuBar(Menu(self))
        self.ind_toolbar = IndicatorsToolBar(self)
        self.addToolBar(self.ind_toolbar)

        self.central_widget = TabsWidget(self, self.ind_toolbar)
        self.setCentralWidget(self.central_widget)
        fplt.autoviewrestore()
        fplt.show(qt_exec=False)
        self.show()


class TabsWidget(QTabWidget):
    def __init__(self, parent, ind_toolbar):
        super(QTabWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.candles = {}
        self.ind_toolbar = ind_toolbar

        with open("trading/display/config.json", "r") as fp:
            config = json.load(fp)["config"]

        first = True
        for currency, indicators in config.items():
            tab = QWidget()
            tab.layout = QVBoxLayout(self)
            tab.label = QLabel(currency)
            fplt_widgets = create_fplt_widgets(self.window())
            self.candles.setdefault(
                currency, {
                    "candles": get_candle_data( 
                        currency,
                        begin=begin,
                        end=end,
                        granularity=granularity
                        )
                    }
                )
            tab.layout.addWidget(tab.label)
            tab.layout.addWidget(fplt_widgets[0].ax_widget, stretch=3)
            self.window().axs = fplt_widgets
            self.candles[currency]["axs"] = self.window().axs
            plot_main_window(self.candles[currency])
            tab.setLayout(tab.layout)
            self.addTab(tab, currency)
            self.ind_toolbar.set_graph_infos(
                currency=currency,
                candles=self.candles[currency],
                widget=tab
            )
            if first:
                active_currency = (currency, tab)
                first = False
            for indicator in indicators:
                params = indicator.split("-")
                ind = params[0]
                if len(params) > 1 and params[1].isnumeric():
                    self.ind_toolbar.numbers[ind] = int(params[1])
                getattr(self.ind_toolbar, f"show_{ind}")()

        self.ind_toolbar.set_graph_infos(
                currency=active_currency[0],
                candles=self.candles[active_currency[0]],
                widget=active_currency[1]
            )
        self.setLayout(self.layout)
        self.currentChanged.connect(self.onChange)

    def onChange(self, tab_index):
        currency = self.currentWidget().label.text()
        print("currency: ", currency)
        self.ind_toolbar.set_graph_infos(
            currency=currency,
            candles=self.candles[currency],
            widget=self.currentWidget()
        )


if __name__ == '__main__':
    set_plot_colors()
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
