"""This is the main gui file to work estimate nuclear membrane thickness.

Project of Cyril Esnault and Alexia Pigeot.
Version 1.0, since Marcj 2022
Contact antonio.trullo@igmm.cnrs.fr

"""

import sys
import os
import traceback
from importlib import reload
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
import pyqtgraph as pg

import AnalysisSaver
import LoadFile
import SearchFrame
import ContourFinder
import ThicknessEstimate
import EstimateVolume
import CompareTool


class MainWindow(QtWidgets.QMainWindow):
    """Main windows: coordinates all the actions, algorithms, visualization tools and analysis tools."""
    def __init__(self, parent=None):

        QtWidgets.QMainWindow.__init__(self, parent)
        widget  =  QtWidgets.QWidget(self)
        self.setCentralWidget(widget)

        load_data_action  =  QtWidgets.QAction(QtGui.QIcon('Icons/load-hi.png'), "&Load Data", self)
        load_data_action.setShortcut("Ctrl+L")
        load_data_action.setStatusTip("Load .dv files and the xls output of FQ")
        load_data_action.triggered.connect(self.load_data)

        save_analysis_action  =  QtWidgets.QAction(QtGui.QIcon('Icons/save-md.png'), "&Save Analysis", self)
        save_analysis_action.setShortcut("Ctrl+S")
        save_analysis_action.setStatusTip("Save the analysis in a folder")
        save_analysis_action.triggered.connect(self.save_analysis)

        exit_action  =  QtWidgets.QAction(QtGui.QIcon('Icons/exit.png'), "&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)

        change_settings_action  =  QtWidgets.QAction(QtGui.QIcon('Icons/settings.png'), "&Settings", self)
        change_settings_action.setShortcut("Ctrl+T")
        change_settings_action.setStatusTip("Changes default settings values")
        change_settings_action.triggered.connect(self.settings_changes)

        menubar   =  self.menuBar()

        fileMenu  =  menubar.addMenu("&File")
        fileMenu.addAction(load_data_action)
        fileMenu.addAction(save_analysis_action)
        # fileMenu.addAction(save_spts_action)
        fileMenu.addAction(exit_action)

        modify_menu  =  menubar.addMenu("&Modify")
        modify_menu.addAction(change_settings_action)

        ksf_h  =  np.load('keys_size_factor.npy')[0]
        ksf_w  =  np.load('keys_size_factor.npy')[1]

        fname_raw_lbl  =  QtWidgets.QLabel("File: ", self)
        fname_raw_lbl.setToolTip("Name of the file you are working on")

        frame_idx_lbl  =  QtWidgets.QLabel("Frame 0", self)
        frame_idx_lbl.setToolTip("Frame number")

        frame_raw  =  pg.ImageView(self)
        frame_raw.ui.roiBtn.hide()
        frame_raw.ui.menuBtn.hide()
        # frame_nucs_ellips.view.setXLink("FrameNucsRaw")
        # frame_nucs_ellips.view.setYLink("FrameNucsRaw")
        frame_raw.timeLine.sigPositionChanged.connect(self.frame_raw_index_update)

        frame_selected  =  pg.ImageView(self)
        frame_selected.ui.roiBtn.hide()
        frame_selected.ui.menuBtn.hide()

        frame_contour  =  pg.ImageView(self)
        frame_contour.ui.roiBtn.hide()
        frame_contour.ui.menuBtn.hide()

        frame_contour_sects  =  pg.ImageView(self)
        frame_contour_sects.ui.roiBtn.hide()
        frame_contour_sects.ui.menuBtn.hide()

        tabs_contour    =  QtWidgets.QTabWidget()
        tab_cntrs       =  QtWidgets.QWidget()
        tab_cntr_sects  =  QtWidgets.QWidget()

        tabs_contour.addTab(tab_cntrs, "Contours")
        tabs_contour.addTab(tab_cntr_sects, "Sections")

        frame_contour_box  =  QtWidgets.QVBoxLayout()
        frame_contour_box.addWidget(frame_contour)

        tab_cntrs.setLayout(frame_contour_box)

        frame_contour_sects_box  =  QtWidgets.QVBoxLayout()
        frame_contour_sects_box.addWidget(frame_contour_sects)

        tab_cntr_sects.setLayout(frame_contour_sects_box)

        frame_histgr  =  pg.PlotWidget(self)

        numb_angs_edt  =  QtWidgets.QLineEdit(self)
        numb_angs_edt.textChanged[str].connect(self.numb_angs_var)
        numb_angs_edt.returnPressed.connect(self.numb_angs_run)
        numb_angs_edt.setToolTip('Set the number of angle you want')
        numb_angs_edt.setFixedSize(int(ksf_h * 35), int(ksf_w * 25))

        numb_angs_lbl  =  QtWidgets.QLabel("Numb of angles", self)
        numb_angs_lbl.setFixedSize(int(ksf_h * 110), int(ksf_w * 25))

        numb_angs_box  =  QtWidgets.QHBoxLayout()
        numb_angs_box.addWidget(numb_angs_lbl)
        numb_angs_box.addWidget(numb_angs_edt)

        red_check_toggle  =  QtWidgets.QCheckBox("Red", self)
        red_check_toggle.setFixedSize(int(ksf_h * 106), int(ksf_w * 25))
        red_check_toggle.setToolTip("Visualize red channel")
        red_check_toggle.setChecked(True)
        red_check_toggle.setStyleSheet("color: red")
        red_check_toggle.stateChanged.connect(self.red_mode)

        green_check_toggle  =  QtWidgets.QCheckBox("Green", self)
        green_check_toggle.setFixedSize(int(ksf_h * 120), int(ksf_w * 25))
        green_check_toggle.setToolTip("Visualize green channel")
        green_check_toggle.setChecked(True)
        green_check_toggle.setStyleSheet("color: green")
        green_check_toggle.stateChanged.connect(self.green_mode)

        blue_check_toggle  =  QtWidgets.QCheckBox("Blue", self)
        blue_check_toggle.setFixedSize(int(ksf_h * 110), int(ksf_w * 25))
        blue_check_toggle.setToolTip("Visualize blue channel")
        blue_check_toggle.setChecked(True)
        blue_check_toggle.setStyleSheet("color: blue")
        blue_check_toggle.stateChanged.connect(self.blue_mode)

        select_frame_edt  =  QtWidgets.QLineEdit(self)
        select_frame_edt.textChanged[str].connect(self.select_frame_var)
        select_frame_edt.returnPressed.connect(self.select_frame_run)
        select_frame_edt.setToolTip("Set the frame to work on")
        select_frame_edt.setFixedSize(int(ksf_h * 35), int(ksf_w * 25))

        select_frame_lbl  =  QtWidgets.QLabel("Select Frame", self)
        select_frame_lbl.setFixedSize(int(ksf_h * 110), int(ksf_w * 25))

        select_frame_box  =  QtWidgets.QHBoxLayout()
        select_frame_box.addWidget(select_frame_lbl)
        select_frame_box.addWidget(select_frame_edt)

        idx_red_green_blue_box  =  QtWidgets.QHBoxLayout()
        idx_red_green_blue_box.addWidget(frame_idx_lbl)
        idx_red_green_blue_box.addWidget(red_check_toggle)
        idx_red_green_blue_box.addWidget(green_check_toggle)
        idx_red_green_blue_box.addWidget(blue_check_toggle)

        frame_raw_colors_box  =  QtWidgets.QVBoxLayout()
        frame_raw_colors_box.addWidget(frame_raw)
        frame_raw_colors_box.addLayout(idx_red_green_blue_box)

        frame_selected_box  =  QtWidgets.QVBoxLayout()
        frame_selected_box.addWidget(frame_selected)

        frames_box  =  QtWidgets.QHBoxLayout()
        frames_box.addLayout(frame_raw_colors_box)
        frames_box.addLayout(frame_selected_box)

        frames_cont_hist_box  =  QtWidgets.QHBoxLayout()
        frames_cont_hist_box.addWidget(tabs_contour)
        frames_cont_hist_box.addWidget(frame_histgr)

        ready_busy_lbl  =  QtWidgets.QLabel(self)
        ready_busy_lbl.setFixedSize(int(ksf_h * 45), int(ksf_w * 25))
        ready_busy_lbl.setToolTip("When red the pc is running, when green it is ready")
        ready_busy_lbl.setStyleSheet("background-color: green")

        volume_estimate_btn  =  QtWidgets.QPushButton("Volume", self)
        volume_estimate_btn.clicked.connect(self.volume_estimate)
        volume_estimate_btn.setToolTip('Estimate volume')
        volume_estimate_btn.setFixedSize(int(ksf_h * 95), int(ksf_w * 25))

        alg1_alg2_combo  =  QtWidgets.QComboBox(self)
        alg1_alg2_combo.addItem("Alg1")
        alg1_alg2_combo.addItem("Alg2")
        # alg1_alg2_combo.activated[str].connect(self.alg1_alg2)
        alg1_alg2_combo.setCurrentIndex(0)
        alg1_alg2_combo.setFixedSize(int(ksf_h * 100), int(ksf_w * 25))

        bottom_lbls  =  QtWidgets.QHBoxLayout()
        bottom_lbls.addWidget(ready_busy_lbl)
        bottom_lbls.addStretch()
        bottom_lbls.addWidget(alg1_alg2_combo)
        bottom_lbls.addLayout(select_frame_box)
        bottom_lbls.addLayout(numb_angs_box)
        bottom_lbls.addWidget(volume_estimate_btn)

        layout  =  QtWidgets.QVBoxLayout(widget)
        layout.addWidget(fname_raw_lbl)
        layout.addLayout(frames_box)
        layout.addLayout(frames_cont_hist_box)
        layout.addLayout(bottom_lbls)

        mycmap  =  np.fromfile("mycmap.bin", "uint16").reshape((10000, 3))   # / 255.0
        self.colors4map  =  []
        for k in range(mycmap.shape[0]):
            self.colors4map.append(mycmap[k, :])
        self.colors4map[0]  =  np.array([0, 0, 0])

        self.frame_raw           =  frame_raw
        self.ready_busy_lbl      =  ready_busy_lbl
        self.fname_raw_lbl       =  fname_raw_lbl
        self.frame_selected      =  frame_selected
        self.red_check_toggle    =  red_check_toggle
        self.green_check_toggle  =  green_check_toggle
        self.blue_check_toggle   =  blue_check_toggle
        self.frame_idx_lbl       =  frame_idx_lbl
        self.frame_contour       =  frame_contour
        self.frame_histgr        =  frame_histgr
        self.select_frame_edt    =  select_frame_edt
        self.alg1_alg2_combo     =  alg1_alg2_combo

        self.soft_version  =  "ThicknessGui_v_1"

        self.setGeometry(800, 100, 700, 500)
        self.setWindowTitle(self.soft_version)
        self.setWindowIcon(QtGui.QIcon('Icons/DrosophilaIcon.png'))
        self.show()

    def closeEvent(self, event):
        """Close the GUI, asking confirmation."""
        quit_msg  =  "Are you sure you want to exit the program?"
        reply     =  QtWidgets.QMessageBox.question(self, 'Message', quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def settings_changes(self):
        """Change settings."""
        self.mpp6  =  SettingsChanges()
        self.mpp6.show()
        self.mpp6.procStart.connect(self.settings_update)

    def settings_update(self):
        """Restart the GUI to make changes in button size effective."""
        self.mpp6.close()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def busy_indicator(self):
        """Write a red text (BUSY) as a label on the GUI (bottom left)."""
        self.ready_busy_lbl.setStyleSheet("background-color: red")

    def ready_indicator(self):
        """Write a green text (READY) as a label on the GUI (bottom left)."""
        self.ready_busy_lbl.setStyleSheet("background-color: green")

    def numb_angs_var(self, text):
        """Input the number of angles."""
        self.numb_angs_value  =  int(text)

    def select_frame_var(self, text):
        """Input the frame number to work on."""
        self.select_frame_value  =  int(text)

    def red_mode(self, state):
        """Show/hide red channel in the raw data."""
        if state == QtCore.Qt.Checked:
            self.raw_data2show[:, :, :, 0]  =  np.copy(self.raw_data[:, :, :, 0])
            self.frame_raw.updateImage()
        elif state == QtCore.Qt.Unchecked:
            self.raw_data2show[:, :, :, 0]  =  0
            self.frame_raw.updateImage()

    def green_mode(self, state):
        """Show/hide red channel in the raw data."""
        if state == QtCore.Qt.Checked:
            self.raw_data2show[:, :, :, 1]  =  np.copy(self.raw_data[:, :, :, 1])
            self.frame_raw.updateImage()
        elif state == QtCore.Qt.Unchecked:
            self.raw_data2show[:, :, :, 1]  =  0
            self.frame_raw.updateImage()

    def blue_mode(self, state):
        """Show/hide red channel in the raw data."""
        if state == QtCore.Qt.Checked:
            self.raw_data2show[:, :, :, 2]  =  np.copy(self.raw_data[:, :, :, 2])
            self.frame_raw.updateImage()
        elif state == QtCore.Qt.Unchecked:
            self.raw_data2show[:, :, :, 2]  =  0
            self.frame_raw.updateImage()

    def frame_raw_index_update(self):
        """Update the frame index as a tag on the frame raw."""
        self.frame_idx_lbl.setText("Frame " + str(self.frame_raw.currentIndex))

    def load_data(self):
        """Load raw data file (.dv format)."""
        reload(LoadFile)
        reload(SearchFrame)
        self.busy_indicator()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        self.raw_data_fname  =  None
        self.raw_data        =  None
        self.right_fr        =  None
        self.frame_histgr.clear()

        try:
            self.raw_data_fname  =  str(QtWidgets.QFileDialog.getOpenFileName(None, "Select raw data file to analyze", filter='*.dv')[0])
            self.raw_data        =  LoadFile.LoadFile(self.raw_data_fname).img_fin
            self.raw_data2show   =  np.copy(self.raw_data)
            self.frame_raw.setImage(self.raw_data2show)
            if self.red_check_toggle.checkState() ==  QtCore.Qt.Unchecked:
                self.red_mode(False)
            if self.green_check_toggle.checkState()  ==  QtCore.Qt.Unchecked:
                self.green_mode(False)
            if self.blue_check_toggle.checkState()  ==  QtCore.Qt.Unchecked:
                self.blue_mode(False)
            self.fname_raw_lbl.setText(self.raw_data_fname)
            self.right_fr  =  SearchFrame.SearchFrame(self.raw_data[:, :, :, 1])
            self.frame_selected.setImage(self.right_fr.right_fr)
            self.select_frame_edt.setText(str(self.right_fr.fr_sel))
            try:
                self.frame_selected.removeItem(self.fr2print)
            except AttributeError:
                pass
            self.fr2print  =  pg.TextItem(str(self.right_fr.fr_sel), color='r', anchor=(0, 1))
            self.frame_selected.addItem(self.fr2print)
            if self.alg1_alg2_combo.currentIndex() == 0:
                self.img_cntr  =  ContourFinder.ContourFinder(self.right_fr.img_bw)
            elif self.alg1_alg2_combo.currentIndex() == 1:
                right_fr       =  SearchFrame.ManualSet(self.raw_data[:, :, :, 1], self.right_fr.fr_sel)
                self.img_cntr  =  ContourFinder.ContourFinder(right_fr.img_bw)
            self.frame_contour.setImage(self.img_cntr.int_cntr + 2 * self.img_cntr.ext_cntr)
            self.frame_contour.setPredefinedGradient("thermal")

        except Exception:
            traceback.print_exc()

        self.ready_indicator()

    def numb_angs_run(self):
        """Run the angular study."""
        reload(ContourFinder)
        reload(ThicknessEstimate)
        self.busy_indicator()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()

        try:
            self.memb_sects  =  ContourFinder.CreateSectors(self.img_cntr.fill_ext, self.img_cntr.fill_int, self.img_cntr.cntrd, self.numb_angs_value)
            # pg.image(self.memb_sects.sectors)
            w                =  pg.image(self.memb_sects.sectors * self.memb_sects.memb_clean)
            self.mycmap      =  pg.ColorMap(np.linspace(0, 1, self.memb_sects.sectors.max()), color=self.colors4map)
            w.setColorMap(self.mycmap)
            for kk in range(len(self.memb_sects.pos_tags)):
                mm  =  pg.TextItem(str(self.memb_sects.pos_tags[kk][0]))
                mm.setPos(self.memb_sects.pos_tags[kk][1], self.memb_sects.pos_tags[kk][2])
                w.addItem(mm)
            self.membs_tcks  =  ThicknessEstimate.ThicknessEstimate(self.memb_sects.memb_clean, self.memb_sects.sectors).membs_tcks
            self.frame_histgr.clear()
            self.frame_histgr.plot(self.membs_tcks[:, 1], symbol='x', pen='r')
            text1  =  pg.TextItem("av = " + str(np.round(self.membs_tcks[:, 1].mean(), 3)), border='w', fill=(0, 0, 255, 100))
            text2  =  pg.TextItem("std = " + str(np.round(self.membs_tcks[:, 1].std(), 3)), border='w', fill=(0, 0, 255, 100))
            self.frame_histgr.addItem(text1)
            self.frame_histgr.addItem(text2)
            text1.setPos(self.membs_tcks[:, 1].size, self.membs_tcks[:, 1].max())
            text2.setPos(self.membs_tcks[:, 1].size, self.membs_tcks[:, 1].max() - 5)

        except Exception:
            traceback.print_exc()

        self.ready_indicator()

    def select_frame_run(self):
        """Run the analysis on the manually selected frame."""
        reload(LoadFile)
        reload(SearchFrame)
        self.busy_indicator()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        self.frame_histgr.clear()

        try:
            self.right_fr  =  SearchFrame.ManualSet(self.raw_data[:, :, :, 1], self.select_frame_value)
            self.frame_selected.setImage(self.right_fr.right_fr)
            self.select_frame_edt.setText(str(self.right_fr.fr_sel))
            self.frame_raw.setCurrentIndex(self.right_fr.fr_sel)
            try:
                self.frame_selected.removeItem(self.fr2print)
            except AttributeError:
                pass
            self.fr2print  =  pg.TextItem(str(self.right_fr.fr_sel), color='r', anchor=(0, 1))
            self.frame_selected.addItem(self.fr2print)

            if self.alg1_alg2_combo.currentIndex() == 0:
                self.right_fr  =  SearchFrame.SearchFramePreprocess(self.raw_data[:, :, :, 1], self.select_frame_value)
                self.img_cntr  =  ContourFinder.ContourFinder(self.right_fr.img_bw)
            if self.alg1_alg2_combo.currentIndex() == 1:
                self.right_fr  =  SearchFrame.ManualSet(self.raw_data[:, :, :, 1], self.select_frame_value)
                self.img_cntr  =  ContourFinder.ContourFinder(self.right_fr.img_bw)
            self.frame_contour.setImage(self.img_cntr.int_cntr + 2 * self.img_cntr.ext_cntr)
            self.frame_contour.setPredefinedGradient("thermal")

        except Exception:
            traceback.print_exc()

        self.ready_indicator()

    def volume_estimate(self):
        """Estimate the volume of the cell."""
        reload(EstimateVolume)
        self.busy_indicator()
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()

        try:
            self.img_vol  =  EstimateVolume.EstimateVolume(self.raw_data[:, :, :, 1]).img_fin
            CompareTool.CompareTool(self.raw_data[:, :, :, 1], self.img_vol)
        except Exception:
            traceback.print_exc()

        self.ready_indicator()

    def save_analysis(self):
        """Save analysis."""
        reload(AnalysisSaver)
        filename  =  QtWidgets.QFileDialog.getSaveFileName(None, "Select or Define a Folder to Store the analysis results")[0]
        # folder2write  =  str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select or Define a Folder to Store the analysis results"))
        AnalysisSaver.AnalysisSaver(filename, self.raw_data_fname, self.numb_angs_value, self.membs_tcks, self.memb_sects, self.colors4map, self.select_frame_value, np.sum(self.img_vol), self.alg1_alg2_combo.currentIndex())


class SettingsChanges(QtWidgets.QWidget):
    """Tool to change visualization and analysis parameters."""
    procStart  =  QtCore.pyqtSignal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.ksf_h  =  np.load('keys_size_factor.npy')[0]
        self.ksf_w  =  np.load('keys_size_factor.npy')[1]

        ksf_h_lbl  =  QtWidgets.QLabel("Keys Scale Factor W")

        ksf_h_edt  =  QtWidgets.QLineEdit(self)
        ksf_h_edt.textChanged[str].connect(self.ksf_h_var)
        ksf_h_edt.setToolTip("Sets keys scale size (width)")
        ksf_h_edt.setFixedSize(int(self.ksf_h * 65), int(self.ksf_w * 25))
        ksf_h_edt.setText(str(self.ksf_h))

        ksf_w_lbl  =  QtWidgets.QLabel("Keys Scale Factor H")

        ksf_w_edt  =  QtWidgets.QLineEdit(self)
        ksf_w_edt.textChanged[str].connect(self.ksf_w_var)
        ksf_w_edt.setToolTip("Sets keys scale size (heigth)")
        ksf_w_edt.setFixedSize(int(self.ksf_h * 65), int(self.ksf_w * 25))
        ksf_w_edt.setText(str(self.ksf_w))

        save_btn  =  QtWidgets.QPushButton("Save", self)
        save_btn.clicked.connect(self.save_vars)
        save_btn.setToolTip('Make default the choseen parameters')
        save_btn.setFixedSize(int(self.ksf_h * 50), int(self.ksf_w * 25))

        close_btn  =  QtWidgets.QPushButton("Close", self)
        close_btn.clicked.connect(self.close_)
        close_btn.setToolTip('Close Widget')
        close_btn.setFixedSize(int(self.ksf_h * 50), int(self.ksf_w * 25))

        restart_btn  =  QtWidgets.QPushButton("Refresh", self)
        restart_btn.clicked.connect(self.restart)
        restart_btn.setToolTip('Refresh GUI')
        restart_btn.setFixedSize(int(self.ksf_h * 60), int(self.ksf_w * 25))

        btns_box  =  QtWidgets.QHBoxLayout()
        btns_box.addWidget(save_btn)
        btns_box.addWidget(restart_btn)
        btns_box.addWidget(close_btn)

        layout_grid  =  QtWidgets.QGridLayout()
        layout_grid.addWidget(ksf_h_lbl, 0, 0)
        layout_grid.addWidget(ksf_h_edt, 0, 1)
        layout_grid.addWidget(ksf_w_lbl, 1, 0)
        layout_grid.addWidget(ksf_w_edt, 1, 1)

        layout  =  QtWidgets.QVBoxLayout()
        layout.addLayout(layout_grid)
        layout.addStretch()
        layout.addLayout(btns_box)

        self.setLayout(layout)
        self.setGeometry(300, 300, 60, 60)
        self.setWindowTitle("Settings Tool")

    def ksf_h_var(self, text):
        """Set keys size factor value (hight)."""
        self.ksf_h  =  np.float64(text)

    def ksf_w_var(self, text):
        """Set keys size factor value (width)."""
        self.ksf_w  =  np.float64(text)

    def save_vars(self):
        """Save new settings."""
        np.save('keys_size_factor.npy', [self.ksf_h, self.ksf_w])

    def close_(self):
        """Close the widget."""
        self.close()

    @QtCore.pyqtSlot()
    def restart(self):
        """Send message to main GUI."""
        self.procStart.emit()



def main():
    app         =  QtWidgets.QApplication(sys.argv)
    splash_pix  =  QtGui.QPixmap('Icons/thickness.jpg')
    splash      =  QtWidgets.QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()
    ex  =  MainWindow()
    splash.finish(ex)
    sys.exit(app.exec_())


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':

    main()
    sys.excepthook = except_hook
