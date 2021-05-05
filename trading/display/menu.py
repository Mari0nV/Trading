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
    directional_movement,
    mma,
    parabolic_sar,
    rsi
)
import finplot as fplt
import pyqtgraph as pg
import json
from json import JSONDecodeError
from trading.get_data import get_candle_data
from trading.display.utils import save

font_size = 12
granularity = "1d"

class Menu(QMenuBar):
    def __init__(self, parent):
        super(QMenuBar, self).__init__(parent)
        self._createActions()
        currencyMenu = QMenu("&Granularity", self)
        currencyMenu.addAction(self.ethAction)
        currencyMenu.addAction(self.btcAction)
        self.addMenu(currencyMenu)
    
    def _createActions(self):
        self.ethAction = QAction("&D", self)
        self.ethAction.triggered.connect(self.daily_g)
        self.btcAction = QAction("&4h", self)
        self.btcAction.triggered.connect(self.fourh_g)
    
    def daily_g(self):
        global granularity
        granularity = "1d"
    
    def fourh_g(self):
        global granularity
        granularity = "4h"


class IndicatorsToolBar(QToolBar):
    def __init__(self, parent):
        super(QToolBar, self).__init__(parent)
        self.ax_index = 1
        self.numbers = {}
        self.indicator_widget("MMA", self.show_mma, self.number_changed_mma)
        self.addSeparator()
        self.indicator_widget("ParabolicSar", self.show_parabolic)
        self.indicator_widget("RSI", self.show_rsi)
        self.indicator_widget("ADX", self.show_adx)

    def indicator_widget(self, label_text, show_method, changed_method=None):
        if changed_method:
            # Label for Indicator
            label = QLabel()
            label.setText(label_text)
            label.setFont(QFont("Arial", font_size))
            self.addWidget(label)

            # Number widget for Indicator
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
            action_name = "&+"
        else:
            action_name = f"&{label_text}+"

        # MMA action
        action = QAction(action_name, self)
        action.setFont(QFont("Arial", font_size))
        action.triggered.connect(show_method)
        self.addAction(action)

    def number_changed_mma(self, text):
        self.numbers["MMA"] = int(text)
        print(self.numbers["MMA"])

    @save
    def show_parabolic(self):
        df = parabolic_sar(self.candles)
        fplt.plot(df["time"], df["Parabolic_SAR"], ax=self.axs[0], legend=f"parabolic_sar", style="o", color="#43a7e3")
        fplt.show(qt_exec=False)

    @save
    def show_mma(self):
        df = mma(self.candles, self.numbers["MMA"])
        fplt.plot(df["time"], df[f"MMA{self.numbers['MMA']}"], ax=self.axs[0], legend=f"MMA{self.numbers['MMA']}")
        fplt.show(qt_exec=False)

    @save
    def show_rsi(self):
        df = rsi(self.candles)
        self.widget.layout.addWidget(self.axs[self.ax_index].ax_widget, stretch=1)
        fplt.plot(df["time"], df["RSI14"], ax=self.axs[self.ax_index], legend=f"RSI")
        fplt.add_band(30, 70, color="#211739", ax=self.axs[self.ax_index])
        fplt.show(qt_exec=False)
        self.ax_index += 1
    
    @save
    def show_adx(self):
        df = directional_movement(self.candles)
        self.widget.layout.addWidget(self.axs[self.ax_index].ax_widget, stretch=1)
        fplt.plot(df["time"], df["ADX14"], ax=self.axs[self.ax_index], color="#304aea", legend=f"ADX")
        fplt.plot(df["time"], df["DI+14"], ax=self.axs[self.ax_index], color="#26A69A", legend=f"DI+")
        fplt.plot(df["time"], df["DI-14"], ax=self.axs[self.ax_index], color="#EF5350", legend=f"DI-")
        # fplt.set_y_range(-1.4, +3.7, ax=self.axs[1])
        fplt.show(qt_exec=False)
        self.ax_index += 1

    def set_graph_infos(self, currency, candles, widget):
        self.currency = currency
        self.candles = candles["candles"]
        self.axs = candles["axs"]
        self.widget = widget
