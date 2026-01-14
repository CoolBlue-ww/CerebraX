import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication
from PyQt6 import QtWidgets


app = QApplication(sys.argv)
window = pg.GraphicsLayoutWidget(show=True, size=(1920, 1080))
window.setWindowTitle("my window")
# window.setBackground("w")
window.ci.layout.setSpacing(0)
window.ci.layout.setContentsMargins(0,0,0,0)

screen = window.screen()
print(screen.size())
plot1 = window.addPlot(title="my plot1", row=0, col=0)
plot1.hideAxis("left")
plot1.hideAxis("bottom")
plot1.hideAxis("right")
plot1.hideAxis("top")
frame1 = QtWidgets.QGraphicsRectItem(0, 0, 1, 1)
frame1.setPen(pg.mkPen(color="y", width=2))
frame1.setBrush(pg.mkBrush(None))
frame1.setRect(plot1.boundingRect())
frame1.setParentItem(plot1)

# separator1 = pg.InfiniteLine(pos=3, angle=0, pen=pg.mkPen(color="gray", width=2))
# plot1.addItem(separator1)
plot2 = window.addPlot(title="my plot2", row=0, col=1)
# plot2.hideAxis("left")
# plot2.hideAxis("bottom")
# plot2.hideAxis("right")
# plot2.hideAxis("top")
plot3 = window.addPlot(row=1, col=0, colspan=3)
# plot3.hideAxis("left")
# plot3.hideAxis("bottom")
# plot3.hideAxis("right")
# plot3.hideAxis("top")
separator3 = pg.InfiniteLine(angle=0, pos=1.5, pen=pg.mkPen(color="gray", width=1))
plot3.addItem(separator3)
# plot4 = window.addPlot(title="my plot4")

m = np.linspace(0, 10, 100)
n = np.cos(m)

plot1.plot(m, n, pen="w")
plot2.plot(m, n, pen="b")
plot3.plot(m, n, pen="r")

sys.exit(app.exec())

