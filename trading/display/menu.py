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

from trading.indicators.indicators import (
    mma,
    parabolic_sar,
    rsi
)
import trading.ext.finplot as fplt
import pyqtgraph as pg

from trading.get_data import get_candle_data

font_size = 12

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
        self.numbers = {}
        self.indicator_widget("MMA", self.show_mma, self.number_changed_mma)
        self.addSeparator()
        self.indicator_widget("ParabolicSar", self.show_parabolic)
        self.indicator_widget("RSI", self.show_rsi)

    def indicator_widget(self, label_text, show_method, changed_method=None):
        # Label for Indicator
        label = QLabel()
        label.setText(label_text)
        label.setFont(QFont("Arial", font_size))
        self.addWidget(label)

        # Number widget for Indicator
        if changed_method:
            self.numbers[label_text] = 20
            number_widget = QLineEdit()
            number_widget.setValidator(QIntValidator())
            number_widget.setMaxLength(3)
            number_widget.setFont(QFont("Arial", font_size))
            number_widget.setMaximumWidth(55)
            number_widget.setAlignment(Qt.AlignRight)
            number_widget.setText(str(self.numbers[label_text]))
            number_widget.textChanged.connect(changed_method)
            self.addWidget(number_widget)

        # MMA action
        action = QAction("&+", self)
        action.setFont(QFont("Arial", font_size))
        action.triggered.connect(show_method)
        self.addAction(action)

    def number_changed_mma(self, text):
        self.numbers["MMA"] = int(text)
        print(self.numbers["MMA"])

    def show_parabolic(self):
        df = parabolic_sar(self.candles)
        fplt.plot(df["time"], df["Parabolic_SAR"], ax=self.axs[0], legend=f"parabolic_sar", style="o", color="#43a7e3")
        fplt.show(qt_exec=False)

    def show_mma(self):
        df = mma(self.candles, self.numbers["MMA"])
        fplt.plot(df["time"], df[f"MMA{self.numbers['MMA']}"], ax=self.axs[0], legend=f"mma{self.numbers['MMA']}")
        fplt.show(qt_exec=False)

    def show_rsi(self):
        df = rsi(self.candles)
        self.widget.layout.addWidget(self.axs[1].ax_widget) 
        fplt.plot(df["time"], df["RSI14"], ax=self.axs[1], legend=f"rsi14")
        # fplt.set_y_range(-1.4, +3.7, ax=self.axs[1])
        fplt.show(qt_exec=False)

    def set_graph_infos(self, currency, candles, widget):
        self.currency = currency
        self.candles = candles["candles"]
        self.axs = candles["axs"]
        self.widget = widget
