"""Simple tool to compare two multi frame images
keeping update zoom and frame number.
"""


import numpy as np
import pyqtgraph as pg
# from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5 import QtGui, QtCore, QtWidgets


class CompareTool(QtWidgets.QWidget):
    """only class, does all the job"""
    def __init__(self, img1, img2, widgtitle=""):
        QtWidgets.QWidget.__init__(self)

        tabs  =  QtWidgets.QTabWidget()
        tab1  =  QtWidgets.QWidget()
        tab2  =  QtWidgets.QWidget()

        # mycmap  =  np.fromfile("mycmap.bin", "uint16").reshape((10000, 3))  # / 255.0
        # colors4map = []
        # for k in range(mycmap.shape[0]):
        #     colors4map.append(mycmap[k, :])
        # colors4map[0] = np.array([0, 0, 0])
        # mycmap = pg.ColorMap(np.linspace(0, 1, img2.max()), color=colors4map)

        frame1  =  pg.ImageView(self, name='Frame1')
        frame1.ui.menuBtn.hide()
        frame1.ui.roiBtn.hide()
        frame1.setImage(img1)
        frame1.timeLine.sigPositionChanged.connect(self.update_frame2)
#         frame1.setColorMap(mycmap)

        frame2  =  pg.ImageView(self)
        frame2.ui.menuBtn.hide()
        frame2.ui.roiBtn.hide()
        frame2.setImage(img2)
        frame2.view.setXLink('Frame1')
        frame2.view.setYLink('Frame1')
        frame2.timeLine.sigPositionChanged.connect(self.update_frame1)
        frame2.getImageItem().mouseClickEvent  =  self.get_tag
        # frame2.setColorMap(mycmap)

        frame_numb_lbl  =  QtWidgets.QLabel("Frame 0", self)
        frame_numb_lbl.setFixedSize(120, 25)

        frame1_box  =  QtWidgets.QHBoxLayout()
        frame1_box.addWidget(frame1)

        frame2_box  =  QtWidgets.QHBoxLayout()
        frame2_box.addWidget(frame2)

        tab1.setLayout(frame1_box)
        tab2.setLayout(frame2_box)

        tabs.addTab(tab1, "ONE")
        tabs.addTab(tab2, "TWO")

        layout  =  QtWidgets.QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(frame_numb_lbl)

        self.frame1          =  frame1
        self.frame2          =  frame2
        self.img1            =  img1
        self.img2            =  img2
        self.idxs_difr       =  []
        self.frame_numb_lbl  =  frame_numb_lbl

        self.setGeometry(800, 100, 900, 800)
        self.setWindowTitle("CompareTool" + widgtitle)
        self.setWindowIcon(QtGui.QIcon('JD_logo.jpeg'))
        self.setLayout(layout)
        self.show()


#     def closeEvent(self, event):
#         """Close the GUI"""
#         quit_msg  =  "Are you sure you want to exit the program?"
#         reply     =  QtGui.QMessageBox.question(self, 'Message', quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
#
#         if reply == QtGui.QMessageBox.Yes:
#             event.accept()
#         else:
#             event.ignore()
#

    def update_frame2(self):
        self.frame2.setCurrentIndex(self.frame1.currentIndex)
        self.frame_numb_lbl.setText("Frame " + str(self.frame1.currentIndex))


    def update_frame1(self):
        self.frame1.setCurrentIndex(self.frame2.currentIndex)


    def get_tag(self, event):
        event.accept()
        pos        =  event.pos()
        modifiers  =  QtWidgets.QApplication.keyboardModifiers()

        if modifiers  ==  QtCore.Qt.ShiftModifier:
            if self.img2[self.frame2.currentIndex, int(pos.x()), int(pos.y())] != 0:
                self.idxs_difr.append(self.img2[self.frame2.currentIndex, int(pos.x()), int(pos.y())])
                print(self.idxs_difr)
