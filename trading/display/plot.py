import finplot as fplt


def set_plot_colors():
    """ Modify finplot color parameters to have a nice dark mode"""
    fplt.background = '#131726'
    fplt.odd_plot_background = '#131722'
    fplt.candle_bull_color = '#26A69A'
    fplt.candle_bear_color = '#EF5350'
    fplt.candle_bull_body_color = fplt.candle_bull_color
    fplt.candle_bear_body_color = '#EF5350'
    fplt.volume_bull_color = '#1C5E5E'
    fplt.volume_bear_color = '#813539'
    fplt.volume_bull_body_color = fplt.volume_bull_color
    fplt.cross_hair_color = '#d9d9d9'


def create_fplt_widgets(window, rows=2):
    widgets = fplt.create_plot_widget(window, rows=rows)
    for widget in widgets:
        widget.ax_widget.getAxis('left').setTextPen('#d9d9d9')
        widget.ax_widget.getAxis('bottom').setTextPen('#d9d9d9')
        widget.ax_widget.getAxis('left').setPen('#d9d9d9')
        widget.ax_widget.getAxis('bottom').setPen('#d9d9d9')
        widget.ax_widget.set_visible(crosshair=True, xaxis=True, yaxis=True, xgrid=True, ygrid=True)

    return widgets

def plot_main_window(data):
    """plot candles + volumes"""
    candles = data["candles"][['time','open','close','high','low']]
    fplt.candlestick_ochl(candles)
    volumes = data["candles"][['time','open','close','volume']]
    fplt.volume_ocv(volumes, ax=data["axs"][0].overlay())
    fplt.show(qt_exec=False)
