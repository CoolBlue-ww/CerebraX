import sys, math, time
from collections import deque
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np

# ---------- 独立线程：高频生产数据 ----------
class DataProducer(QThread):
    new_data = pyqtSignal(float)  # 把最新 1 个点送回主线程

    def __init__(self, sample_rate=2000):
        super().__init__()
        self.sample_rate = sample_rate
        self.period = 1 / sample_rate
        self.running = True

    def stop(self):
        self.running = False
        self.wait()

    def run(self):
        """以固定频率产生数据"""
        t = 0
        while self.running:
            t += self.period
            value = 1.5 * math.sin(2 * math.pi * 240 * t) + 0.3 * np.random.randn()
            self.new_data.emit(value)
            time.sleep(self.period)  # 精确控制采样间隔

# ---------- 主窗口 ----------
class HighSpeedPlotWindow(QMainWindow):
    def __init__(self, buffer_size=10000):
        super().__init__()
        self.setWindowTitle("PyQtGraph 高速滚动波形")
        self.resize(900, 400)

        # 1. 构建界面
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Amplitude')
        self.plot_widget.setLabel('bottom', 'Samples')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        layout.addWidget(self.plot_widget)

        # 2. 初始化曲线
        self.buffer = deque([0.0] * buffer_size, maxlen=buffer_size)
        self.curve = self.plot_widget.plot(pen='y')

        # 3. 启动数据线程
        self.producer = DataProducer(sample_rate=2000)  # 2 kHz
        self.producer.new_data.connect(self.append_data)
        self.producer.start()

        # 4. 用 QTimer 控制刷新率（与采样率解耦）
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_plot)
        self.update_timer.start(16)  # ~60 FPS

    def append_data(self, value: float):
        """主线程槽函数，线程安全地收数据"""
        self.buffer.append(value)

    def refresh_plot(self):
        """批量刷新界面，降低 CPU"""
        self.curve.setData(np.array(self.buffer))

    def closeEvent(self, event):
        self.producer.stop()
        event.accept()

# ---------- 入口 ----------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = HighSpeedPlotWindow(buffer_size=10000)
    w.show()
    sys.exit(app.exec_())