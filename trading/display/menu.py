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
    ichimoku,
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
import trading.display.config as cfg


class Menu(QMenuBar):
    def __init__(self, parent, state):
        super(QMenuBar, self).__init__(parent)
        self.state = state
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
        cfg.GRANULARITY = "1d"
    
    def fourh_g(self):
        cfg.GRANULARITY = "4h"

class IndicatorsToolBar(QToolBar):
    def __init__(self, parent, state):
        super(QToolBar, self).__init__(parent)
        self.state = state
        self.indicator_widget("MMA", self.show_mma, self.number_changed_mma)
        self.addSeparator()
        self.indicator_widget("ParabolicSar", self.show_parabolic)
        self.indicator_widget("RSI", self.show_rsi)
        self.indicator_widget("ADX", self.show_adx)
        self.indicator_widget("Ichimoku", self.show_ichimoku)

    def add_label(self, text):
        label = QLabel()
        label.setText(text)
        label.setFont(QFont(cfg.FONT, cfg.FONT_SIZE))
        self.addWidget(label)
    
    def add_action(self, action_name, show_method):
        action = QAction(action_name, self)
        action.setFont(QFont(cfg.FONT, cfg.FONT_SIZE))
        action.triggered.connect(show_method)
        self.addAction(action)

    def indicator_widget(self, label_text, show_method, changed_method=None):
        if changed_method:
            # Label for Indicator
            self.add_label(label_text)

            # Number widget for Indicator
            self.state.numbers[label_text] = 20
            number_widget = QLineEdit()
            number_widget.setValidator(QIntValidator())
            number_widget.setMaxLength(3)
            number_widget.setFont(QFont(cfg.FONT, cfg.FONT_SIZE))
            number_widget.setMaximumWidth(55)
            number_widget.setAlignment(Qt.AlignRight)
            number_widget.setText(str(self.state.numbers[label_text]))
            number_widget.textChanged.connect(changed_method)
            self.addWidget(number_widget)
            action_name = "&+"
        else:
            action_name = f"&{label_text}+"

        # Show action
        self.add_action(action_name, show_method)

    def number_changed_mma(self, text):
        self.state.numbers["MMA"] = int(text)
        print(self.state.numbers["MMA"])

    @save
    def show_parabolic(self):
        df = parabolic_sar(self.state.candles)
        fplt.plot(df["time"], df["Parabolic_SAR"], ax=self.state.axs[0], legend=f"parabolic_sar", style="o", color="#43a7e3")
        fplt.show(qt_exec=False)

    @save
    def show_mma(self):
        df = mma(self.state.candles, self.state.numbers["MMA"])
        fplt.plot(df["time"], df[f"MMA{self.state.numbers['MMA']}"], ax=self.state.axs[0], legend=f"MMA{self.state.numbers['MMA']}")
        fplt.show(qt_exec=False)

    @save
    def show_rsi(self):
        df = rsi(self.state.candles)
        self.state.graph_widget.layout.addWidget(self.state.axs[self.state.ax_index].ax_widget, stretch=1)
        fplt.plot(df["time"], df["RSI14"], ax=self.state.axs[self.state.ax_index], legend=f"RSI")
        fplt.add_band(30, 70, color="#211739", ax=self.state.axs[self.state.ax_index])
        fplt.show(qt_exec=False)
        self.state.ax_index += 1
    
    @save
    def show_adx(self):
        df = directional_movement(self.state.candles)
        self.state.graph_widget.layout.addWidget(self.state.axs[self.state.ax_index].ax_widget, stretch=1)
        fplt.plot(df["time"], df["ADX14"], ax=self.state.axs[self.state.ax_index], color="#304aea", legend=f"ADX")
        fplt.plot(df["time"], df["DI+14"], ax=self.state.axs[self.state.ax_index], color="#26A69A", legend=f"DI+")
        fplt.plot(df["time"], df["DI-14"], ax=self.state.axs[self.state.ax_index], color="#EF5350", legend=f"DI-")
        fplt.show(qt_exec=False)
        self.state.ax_index += 1
    
    @save
    def show_ichimoku(self):
        df = ichimoku(self.state.candles)

        # we need to separate lsa and lsb columns into several plots to be able to fill between them
        # with different colors (green if lsa > lsb and red otherwise)
        fill_green = "#192727"
        fill_red = "#2B1D27"
        first_index = df["Ichimoku_LeadingSpanA"].first_valid_index()
        columns = {
            "time": [df["time"][first_index]],
            "lsa": [df["Ichimoku_LeadingSpanA"][first_index]],
            "lsb": [df["Ichimoku_LeadingSpanB"][first_index]],
        }
        green = df["Ichimoku_LeadingSpanA"][first_index] > df["Ichimoku_LeadingSpanB"][first_index]
        for i in range(first_index + 1, len(df)):
            columns["lsa"].append(df["Ichimoku_LeadingSpanA"][i])
            columns["lsb"].append(df["Ichimoku_LeadingSpanB"][i])
            columns["time"].append(df["time"][i])
            if df["Ichimoku_LeadingSpanA"][i] > df["Ichimoku_LeadingSpanB"][i]:
                if not green:
                    plot_a = fplt.plot(columns["time"], columns["lsa"], ax=self.state.axs[0], color="#4BAB4F")
                    plot_b = fplt.plot(columns["time"], columns["lsb"], ax=self.state.axs[0], color="#F25952")
                    fplt.fill_between(plot_a, plot_b, color=fill_red)
                    columns = {
                        "time": [df["time"][i]],
                        "lsa": [df["Ichimoku_LeadingSpanA"][i]],
                        "lsb": [df["Ichimoku_LeadingSpanB"][i]],
                    }
            elif green:
                    plot_a = fplt.plot(columns["time"], columns["lsa"], ax=self.state.axs[0], color="#4BAB4F")
                    plot_b = fplt.plot(columns["time"], columns["lsb"], ax=self.state.axs[0], color="#F25952")
                    fplt.fill_between(plot_a, plot_b, color=fill_green)
                    columns = {
                        "time": [df["time"][i]],
                        "lsa": [df["Ichimoku_LeadingSpanA"][i]],
                        "lsb": [df["Ichimoku_LeadingSpanB"][i]],
                    }

            green = df["Ichimoku_LeadingSpanA"][i] > df["Ichimoku_LeadingSpanB"][i]

        # last plot for lsa and lsb
        plot_a = fplt.plot(columns["time"], columns["lsa"], ax=self.state.axs[0], color="#4BAB4F", legend=f"Leading Span A (Senku Span A)")
        plot_b = fplt.plot(columns["time"], columns["lsb"], ax=self.state.axs[0], color="#F25952", legend=f"Leading Span B (Senku Span B)")
        if green:
            fplt.fill_between(plot_a, plot_b, color=fill_green)
        else:
            fplt.fill_between(plot_a, plot_b, color=fill_red)

        # plot the other ichimoku columns
        fplt.plot(df["time"], df["Ichimoku_LaggingSpan"], ax=self.state.axs[0], color="#459915", legend=f"Lagging Span (Chikou Span)")
        fplt.plot(df["time"], df["Ichimoku_BaseLine"], ax=self.state.axs[0], color="#991515", legend=f"Base Line (Kijun-sen)")
        fplt.plot(df["time"], df["Ichimoku_ConversionLine"], ax=self.state.axs[0], color="#0495FD", legend=f"Conversion Line (Tenkan-sen)")

        fplt.show(qt_exec=False)
