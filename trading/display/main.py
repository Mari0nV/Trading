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
import trading.ext.finplot as fplt
import pyqtgraph as pg

from trading.get_data import get_candle_data


currencies = ["ETHEUR", "BTCUSDT"]


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

        # Add active tab
        currency = currencies[0]
        tab = QWidget()
        tab.layout = QVBoxLayout(self)
        tab.label = QLabel(currency)
        tab.fplt_widget = pg.PlotWidget(
            plotItem=fplt.create_plot_widget(self.window())
        )
        self.candles.setdefault(currency, {"candles": get_candle_data(currency)})
        fplt.candlestick_ochl(self.candles[currency]["candles"])
        tab.layout.addWidget(tab.label)
        tab.layout.addWidget(tab.fplt_widget)  #.ax_widget)
        self.window().axs = [tab.fplt_widget.getPlotItem()]  # required property of window
        self.candles[currency]["ax"] = self.window().axs[0]
        tab.setLayout(tab.layout)
        self.addTab(tab, currency)
        self.ind_toolbar.set_graph_infos(currency, self.candles[currency])
        
        # add other tabs
        for currency in currencies[1:]:
            tab = QWidget()
            tab.layout = QVBoxLayout(self)
            tab.label = QLabel(currency)
            tab.layout.addWidget(tab.label)
            self.addTab(tab, currency)

        self.setLayout(self.layout)
        self.currentChanged.connect(self.onChange)

    def onChange(self, tab_index):
        currency = self.currentWidget().label.text()
        print("currency: ", currency)
        if currency not in self.candles:
            self.candles.setdefault(currency, {"candles": get_candle_data(currency)})
            self.currentWidget().fplt_widget = pg.PlotWidget(
                plotItem=fplt.create_plot_widget(self.window())
            )
            self.currentWidget().layout.addWidget(self.currentWidget().label)
            self.currentWidget().layout.addWidget(self.currentWidget().fplt_widget)  #.ax_widget)
            self.window().axs = [self.currentWidget().fplt_widget.getPlotItem()]  # required property of window
            self.candles[currency]["ax"] = self.window().axs[0]
            fplt.candlestick_ochl(self.candles[currency]["candles"])
            self.currentWidget().setLayout(self.currentWidget().layout)
            fplt.show(qt_exec=False)
        self.ind_toolbar.set_graph_infos(currency, self.candles[currency])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
