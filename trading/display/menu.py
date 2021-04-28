from PyQt5.QtWidgets import (
    QAction,
    QLabel,
    QLineEdit,
    QMenu,
    QMenuBar,
    QToolBar
)
from PyQt5.QtGui import (
    QFont,
    QIntValidator
)
from PyQt5.QtCore import Qt

from trading.indicators.indicators import mma
import trading.ext.finplot as fplt
import pyqtgraph as pg

from trading.get_data import get_candle_data


class Menu(QMenuBar):
    def __init__(self, parent):
        super(QMenuBar, self).__init__(parent)
        self._createActions()
        currencyMenu = QMenu("&Currency", self)
        currencyMenu.addAction(self.ethAction)
        currencyMenu.addAction(self.btcAction)
        self.addMenu(currencyMenu)
    
    def _createActions(self):
        self.ethAction = QAction("&ETH", self)
        self.ethAction.triggered.connect(self.show_eth)
        self.btcAction = QAction("&BTC", self)
        self.btcAction.triggered.connect(self.show_btc)
    
    def show_eth(self):
        print("ETH")
    
    def show_btc(self):
        print("BTC")

class IndicatorsToolBar(QToolBar):
    def __init__(self, parent):
        super(QToolBar, self).__init__(parent)

        # Label for MMA
        self.mma_label = QLabel()
        self.mma_label.setText("MMA")
        self.mma_label.setFont(QFont("Arial", 18))
        self.addWidget(self.mma_label)

        # Number widget for MMA
        self.number = 20
        self.number_widget = QLineEdit()
        self.number_widget.setValidator(QIntValidator())
        self.number_widget.setMaxLength(3)
        self.number_widget.setFont(QFont("Arial", 18))
        self.number_widget.setMaximumWidth(55)
        self.number_widget.setAlignment(Qt.AlignRight)
        self.number_widget.setText(str(self.number))
        self.number_widget.textChanged.connect(self.number_changed)
        self.addWidget(self.number_widget)

        # MMA action
        self.mma_action = QAction("&+", self)
        self.mma_action.setFont(QFont("Arial", 18))
        self.mma_action.triggered.connect(self.show_mma)
        self.addAction(self.mma_action)
    
    def number_changed(self, text):
        self.number = int(text)
        print(self.number)

    def show_mma(self):
        df = mma(self.candles, self.number)
        fplt.plot(df["time"], df[f"MMA{self.number}"], ax=self.ax, legend=f'mma{self.number}')
        fplt.show(qt_exec=False)

    def set_graph_infos(self, currency, candles):
        self.currency = currency
        self.candles = candles["candles"]
        self.ax = candles["ax"]
