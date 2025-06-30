"""This function saves the results of the analysis.

Input are the results, no output.
"""


import datetime
import numpy as np
import xlsxwriter
import pyqtgraph as pg
import pyqtgraph.exporters


class AnalysisSaver:
    """Only class, does all the job."""
    def __init__(self, filename, raw_data_fname, numb_angs, membs_tcks, memb_sects, colors4map, select_frame_value, vol, alg1_alg2_combo):

        if filename[-4:] != "xlsx":
            filename  +=  ".xlsx"

        angs    =  np.linspace(0, 2 * np.pi, numb_angs + 1)                   # create the array of angles
        book    =  xlsxwriter.Workbook(filename)
        sheet1  =  book.add_worksheet("Sheet1")
        sheet2  =  book.add_worksheet("Info")

        sheet1.write(0, 0, "Angle")
        sheet1.write(0, 1, "Tag")
        sheet1.write(0, 2, "Thickness")
        for cc in range(numb_angs):
            sheet1.write(cc + 1, 0, str(np.round(np.degrees(angs[cc]), 2)) + "-" + str(np.round(np.degrees(angs[cc + 1]), 2)))    # writes the angles interval
            sheet1.write(cc + 1, 1, membs_tcks[cc, 0])
            sheet1.write(cc + 1, 2, membs_tcks[cc, 1])

        sheet1.write(2, 5, "Average")
        sheet1.write(3, 5, membs_tcks[:, 1].mean())
        sheet1.write(6, 5, "Standard Deviation")
        sheet1.write(7, 5, membs_tcks[:, 1].std())
        sheet1.write(10, 5, "Volume")
        sheet1.write(11, 5, vol)

        sheet2.write(0, 0, "Raw Data filename")
        sheet2.write(0, 1, raw_data_fname)

        sheet2.write(2, 0, "Selected Frame")
        sheet2.write(2, 1, select_frame_value)

        sheet2.write(4, 0, "algorithm")
        sheet2.write(4, 1, alg1_alg2_combo)

        sheet2.write(6, 0, "Date")
        sheet2.write(6, 1, datetime.date.today().strftime("%d%b%Y"))

        book.close()

        w       =  pg.image(memb_sects.sectors * memb_sects.memb_clean)
        mycmap  =  pg.ColorMap(np.linspace(0, 1, memb_sects.sectors.max()), color=colors4map)
        w.setColorMap(mycmap)
        for kk in range(len(memb_sects.pos_tags)):
            mm  =  pg.TextItem(str(memb_sects.pos_tags[kk][0]))
            mm.setPos(memb_sects.pos_tags[kk][1], memb_sects.pos_tags[kk][2])
            w.addItem(mm)
        exporter  =  pg.exporters.ImageExporter(w.imageItem)
        exporter.parameters()['width']   =  1000   # (note this also affects height parameter)
        exporter.parameters()['height']  =  1000   # (note this also affects height parameter)
        exporter.export(filename[:filename.rfind("/")] + '/MembraneSectors.png')
