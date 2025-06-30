"""This function estimates the thickness of a membrane.
Input data is the b&w rough image of the membra (2D ofcourse)

"""

import numpy as np
# from shapely.geometry import Point, Polygon
from skimage.morphology import label
from skimage.measure import regionprops_table
from skimage.morphology import square
from skimage.filters import median
from scipy.ndimage import binary_closing, binary_erosion, binary_fill_holes
# import pyqtgraph as pg
import matplotlib.path as mpltPath

import CustomProgressBar


def define_sector3(frame_shape, coords):
    """This class defines a circular sector"""
    mask  =  np.zeros(frame_shape, dtype=np.uint8)       # initialize output matrix
    path  =  mpltPath.Path(coords)                       # initialize the path with the verteces
    pps   =  list()
    for x in range(frame_shape[0]):
        for y in range(frame_shape[1]):
            pps.append([x, y])                           # create a list of coordinates to span over all the image

    inside  =  path.contains_points(pps)                 # boolean list of coordinates inside the polygon
    kk      =  np.where(inside)[0]                       # select the True values
    for ii in kk:
        mask[pps[ii][0], pps[ii][1]]  =  1               # fill accordingly the b&w matrix image
    return mask


class ContourFinder:
    """Find the membrane"""
    def __init__(self, img_bw):

        img_cl    =  binary_closing(img_bw, iterations=6).astype(np.uint8)
        img_lbl   =  label(img_cl)
        # rgp       =  regionprops_table(img_lbl, properties=["label", "solidity", "centroid"])
        rgp       =  regionprops_table(img_lbl, properties=["label", "area", "centroid"])
        # contour   =  (img_lbl == rgp["label"][np.argmin(rgp["solidity"])]) * np.uint8(1)
        contour   =  (img_lbl == rgp["label"][np.argmax(rgp["area"])]) * np.uint8(1)
        dbl_cntr  =  label(contour - binary_erosion(contour))
        # cntrd     =  [np.round(rgp["centroid-0"][np.argmin(rgp["solidity"])]).astype(int), np.round(rgp["centroid-1"][np.argmin(rgp["solidity"])]).astype(int)]
        cntrd     =  [np.round(rgp["centroid-0"][np.argmax(rgp["area"])]).astype(int), np.round(rgp["centroid-1"][np.argmax(rgp["area"])]).astype(int)]
        fill_ext  =  binary_fill_holes(dbl_cntr)
        # int_cntr  =  (binary_erosion(fill_ext) + dbl_cntr) == 2
        int_cntr  =  (binary_erosion(fill_ext) + np.sign(dbl_cntr)) == 2
        ext_cntr  =  fill_ext ^ binary_erosion(fill_ext)
        fill_int  =  binary_fill_holes(int_cntr)

        self.int_cntr  =  int_cntr
        self.ext_cntr  =  ext_cntr
        self.img_fin   =  dbl_cntr
        self.cntrd     =  cntrd
        self.fill_int  =  fill_int
        self.fill_ext  =  fill_ext
        # pg.image(self.img_fin)
        # pg.image(self.int_cntr + 2 * self.ext_cntr)


class CreateSectors:
    """Study the thickness of the membrane"""
    def __init__(self, fill_ext, fill_int, cntrd, num_sect):

        memb_img    =  (fill_ext ^ fill_int) * np.uint8(1)        # membrane image obtained as boolean product
        memb_clean  =  median(memb_img, square(5))                # median filter to smooth
        angs        =  np.linspace(0, 2 * np.pi, num_sect + 1)    # angles to define sectors
        xlen, ylen  =  fill_int.shape
        sectors     =  np.zeros_like(memb_img)

        pbar  =  CustomProgressBar.ProgressBar(total1=angs.size - 1)
        pbar.update_progressbar(0)
        pbar.show()

        for kk in range(angs.size - 1):
            pbar.update_progressbar(kk)
            xy_pos0  =  None                                          # initialization of the coordinate of the intersection between segment and edges
            xy_pos1  =  None                                          # initialization of the coordinate of the intersection between segment and edges
            if angs[kk] == 0:
                xy_pos0  =  np.array([xlen, cntrd[1]])                # in case the angle is a multiple of pi/2 tang is inifinitive, so we have to set it manually
            elif angs[kk] == np.pi / 2:
                xy_pos0  =  np.array([cntrd[0], ylen])
            elif angs[kk] == np.pi:
                xy_pos0  =  np.array([0, cntrd[1]])
            elif angs[kk] == 3 * np.pi / 2:
                xy_pos0  =  np.array([cntrd[0], 0])
            elif angs[kk] != 0 and angs[kk] != np.pi / 2 and angs[kk] != np.pi and angs[kk] != 3 * np.pi / 2:   # if the angle is not a multiple of pi/2, we have to define the two intersections between segment and edges and choose the good one
                xy_pos0     =  np.zeros((4, 2))                      # initialize the matrix with two points
                b           =  cntrd[1] - np.tan(angs[kk]) * cntrd[0]      # intercept of the segment
                xy_pos0[0]  =  - b / np.tan(angs[kk]), 0                   # coordinate of the intersection of the segment with edges or their prolongations
                xy_pos0[1]  =  (xlen - b) / np.tan(angs[kk]), ylen
                xy_pos0[2]  =  0, b
                xy_pos0[3]  =  xlen, xlen * np.tan(angs[kk]) + b
                neg_vals    =  np.where(xy_pos0 < 0)[0]
                for uu in neg_vals[::-1]:
                    xy_pos0   =  np.delete(xy_pos0, uu, axis=0)

                excee_vals_x  =  np.where(xy_pos0[:, 0] > xlen)[0]
                for vv_x in excee_vals_x:
                    xy_pos0  =  np.delete(xy_pos0, vv_x, axis=0)

                excee_vals_y  =  np.where(xy_pos0[:, 1] > ylen)[0]
                for vv_y in excee_vals_y:
                    xy_pos0  =  np.delete(xy_pos0, vv_y, axis=0)

                if 0 < angs[kk] < np.pi and np.where(xy_pos0[:, 1] < cntrd[1])[0].size:
                    xy_pos0  =  np.delete(xy_pos0, np.where(xy_pos0[:, 1] < cntrd[1])[0][0], axis=0)
                else:
                    xy_pos0  =  np.delete(xy_pos0, np.where(xy_pos0[:, 1] > cntrd[1])[0][0], axis=0)

                xy_pos0  =  np.squeeze(xy_pos0)

            if angs[kk + 1] == 0:
                xy_pos1  =  xlen, cntrd[1]
            elif angs[kk + 1] == np.pi / 2:
                xy_pos1  =  cntrd[0], ylen
            elif angs[kk + 1] == np.pi:
                xy_pos1  =  0, cntrd[1]
            elif angs[kk + 1] == 3 * np.pi / 2:
                xy_pos1  =  cntrd[0], 0
            elif angs[kk + 1] != 0 and angs[kk + 1] != np.pi / 2 and angs[kk + 1] != np.pi and angs[kk + 1] != 3 * np.pi / 2:
                xy_pos1     =  np.zeros((4, 2))
                b           =  cntrd[1] - np.tan(angs[kk + 1]) * cntrd[0]
                xy_pos1[0]  =  - b / np.tan(angs[kk + 1]), 0
                xy_pos1[1]  =  (xlen - b) / np.tan(angs[kk + 1]), ylen
                xy_pos1[2]  =  0, b
                xy_pos1[3]  =  xlen, xlen * np.tan(angs[kk + 1]) + b
                neg_vals    =  np.where(xy_pos1 < 0)[0]
                for uu in neg_vals[::-1]:
                    xy_pos1   =  np.delete(xy_pos1, uu, axis=0)
                #     neg_vals  =  np.where(xy_pos1 < 0)[0]

                excee_vals_x  =  np.where(xy_pos1[:, 0] > xlen)[0]
                for vv_x in excee_vals_x:
                    xy_pos1  =  np.delete(xy_pos1, vv_x, axis=0)

                excee_vals_y  =  np.where(xy_pos1[:, 1] > ylen)[0]
                for vv_y in excee_vals_y:
                    xy_pos1  =  np.delete(xy_pos1, vv_y, axis=0)

                if 0 < angs[kk + 1] < np.pi and np.where(xy_pos1[:, 1] < cntrd[1])[0].size > 0:
                    xy_pos1  =  np.delete(xy_pos1, np.where(xy_pos1[:, 1] < cntrd[1])[0][0], axis=0)
                else:
                    xy_pos1  =  np.delete(xy_pos1, np.where(xy_pos1[:, 1] > cntrd[1])[0][0], axis=0)

                xy_pos1  =  np.squeeze(xy_pos1)

            # Sectors are defined as regions included between two segments starting at the center and cutting the edge of the square. If both segments
            # cut the same edge, the sector is identified by the two intersections and the center. If segments do not cut the same edge, the sector
            # is instead identified by four points: center, intersections of the segments with the edges and the corner of the frame in between.

            if 0 in xy_pos0 - xy_pos1:          # if the two variable have a commont point, than the two segment intersect the same edge, so three point are enough to define the sector
                sectors  +=  (kk + 1) * define_sector3([xlen, ylen], [xy_pos0, xy_pos1, cntrd]) * (1 - np.sign(sectors))

            else:                               # if the two segments cross different edges we need to add the proper corner to identify the sector
                if xy_pos0[0] == xlen and xy_pos1[1] == ylen:      # a segment cross the vertical right edge, the other crosses the horizontal buttom one
                    sectors  +=  (kk + 1) * define_sector3([xlen, ylen], [xy_pos0.tolist(), [xlen, ylen], xy_pos1, cntrd]) * (1 - np.sign(sectors))
                elif xy_pos0[1] == ylen and xy_pos1[0] == 0:     # a segment crosses the horizontal buttom edge, the other the vertical left
                    sectors  +=  (kk + 1) * define_sector3([xlen, ylen], [xy_pos0.tolist(), [0, ylen], xy_pos1, cntrd]) * (1 - np.sign(sectors))
                elif xy_pos0[0] == 0 and xy_pos1[1] == 0:        # a segment crosses the horizontal top edge, the other crosses the vertical left
                    sectors  +=  (kk + 1) * define_sector3([xlen, ylen], [xy_pos0.tolist(), [0, 0], xy_pos1, cntrd]) * (1 - np.sign(sectors))
                elif xy_pos0[1] == 0 and xy_pos1[0] == xlen:     # a segment crosses the horizontal top edge, the other crosses the vertical right
                    sectors  +=  (kk + 1) * define_sector3([xlen, ylen], [xy_pos0.tolist(), [xlen, 0], xy_pos1, cntrd]) * (1 - np.sign(sectors))

        pbar.close()

        sectors[cntrd[0], cntrd[1]]  =  0
        pos_tags  =  list()
        rgp_sect  =  regionprops_table(sectors * memb_clean, properties=["label", "centroid"])
        for cnt, lb in enumerate(rgp_sect["label"]):
            pos_tags.append([lb, rgp_sect["centroid-0"][cnt], rgp_sect["centroid-1"][cnt]])

        self.sectors     =  sectors
        self.memb_clean  =  memb_clean
        self.pos_tags    =  pos_tags


# class ProgressBar(QtWidgets.QWidget):
#     """Simple progress bar widget"""
#     def __init__(self, parent=None, total1=20):
#         super().__init__(parent)
#         self.name_line1  =  QtWidgets.QLineEdit()
#
#         self.progressbar  =  QtWidgets.QProgressBar()
#         self.progressbar.setMinimum(1)
#         self.progressbar.setMaximum(total1)
#
#         main_layout  =  QtWidgets.QGridLayout()
#         main_layout.addWidget(self.progressbar, 0, 0)
#
#         self.setLayout(main_layout)
#         self.setWindowTitle("Progress")
#         self.setGeometry(500, 300, 300, 50)
#
#     def update_progressbar(self, val1):
#         """update the progressbar"""
#         self.progressbar.setValue(val1)
#         QtWidgets.qApp.processEvents()



                # if xy_pos0[0] == xlen and xy_pos1[1] == 0:
                #     sectors  +=  (kk + 1) * define_sector2((xlen, ylen), [xy_pos0.tolist()[0], [xlen, 0], xy_pos1.tolist()[0], cntrd])
                # if xy_pos0[1] == 0 and xy_pos1[0] == 0:
                #     sectors  +=  (kk + 1) * define_sector2((xlen, ylen), [xy_pos0.tolist()[0], [0, 0], xy_pos1.tolist()[0], cntrd])
                # if xy_pos0[0] == 0 and xy_pos1[1] == ylen:
                #     sectors  +=  (kk + 1) * define_sector2((xlen, ylen), [xy_pos0.tolist()[0], [0, ylen], xy_pos1.tolist()[0], cntrd])
                # if xy_pos0[1] == 0 and xy_pos1[0] == xlen:
                #     sectors  +=  (kk + 1) * define_sector2((xlen, ylen), [xy_pos0.tolist()[0], [xlen, ylen], xy_pos1.tolist()[0], cntrd])

# class DefineSector:
#     """This class defines a circular sector"""
#     def __init__(self, frame_shape, ctrs, ang0, ang1):
#
#         mask  =  np.zeros(frame_shape, dtype=np.uint8)
#         for x in range(frame_shape[0]):
#             print(x)
#             for y in range(frame_shape[1]):
#                 if ctrs[1] + (x - ctrs[0]) * np.sin(ang0) < y < ctrs[1] + (x - ctrs[0]) * np.sin(ang1):
#                     mask[x, y]  =  1





# def define_sector(frame_shape, ctrs, ang0, ang1):
#     """This class defines a circular sector"""
#     mask  =  np.zeros(frame_shape, dtype=np.uint8)
#     for x in range(frame_shape[0]):
#         # print(x)
#         for y in range(frame_shape[1]):
#             if ctrs[1] + (x - ctrs[0]) * np.sin(ang0) < y < ctrs[1] + (x - ctrs[0]) * np.sin(ang1):
#                 mask[x, y]  =  1
#     return mask
#
#
# def define_sector2(frame_shape, coords):
#     """This class defines a circular sector"""
#     mask  =  np.zeros(frame_shape, dtype=np.uint8)
#     poly  =  Polygon(coords)
#     for x in range(frame_shape[0]):
#         # print(x)
#         for y in range(frame_shape[1]):
#             mask[x, y]  =  poly.contains(Point(x, y))
#     return mask
#
