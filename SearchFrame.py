"""This function finds the frame of the stack with the border.
"""


import numpy as np
from skimage.filters import gaussian, threshold_otsu, laplace
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
# import pyqtgraph as pg


def double_gaussian(x, mu1, sigma1, A1, mu2, sigma2, A2):
    """Double gaussian function for fitting."""
    return A1 * np.exp(-(x - mu1) ** 2 / (2 * sigma1 ** 2)) + A2 * np.exp(-(x - mu2) ** 2 / (2 * sigma2 ** 2))


class SearchFrame:
    """Only class, does all the job"""
    def __init__(self, img, gs_kern=1.):

        img_f    =  gaussian(img, gs_kern)                       # 3D Gaussian of the raw data matrix
        val      =  threshold_otsu(img_f)                        # Otsu threshold of the whole 3D matrix
        img_bff  =  (img_f > val).astype(np.uint8)               # thresholding

        int_prof  =  np.sum(img_bff, axis=(1, 2))                 # intensity profile of the thresholded image
        min_loc   =  find_peaks(int_prof.max() - int_prof)[0]     # find local minima of the profile

        ff        =  [int_prof[k] for k in min_loc]               # values of the intensity at the local minima
        fr_sel    =  min_loc[np.argmax(ff)]
        right_fr  =  img[fr_sel]                                 # the "right" frame is the one with the highest intensity
        # pg.image(img_bff[fr_sel])

        self.img_bff   =  img_bff
        self.right_fr  =  right_fr
        self.img_bw    =  img_bff[fr_sel]
        self.fr_sel    =  fr_sel


class ManualSet2:
    """This function gives the same output as the previous, but the frame is input"""
    def __init__(self, img, fr_select, gs_kern=1.):

        img_f       =  gaussian(img, gs_kern)                       # 3D Gaussian of the raw data matrix
        hh_f        =  np.histogram(img_f, bins=500)
        # p_init      =  [hh_f[0].max(), np.argmax(hh_f[0]), 10, ]
        # popt, pcov  =  curve_fit(double_gaussian, hh_f[1][1:], hh_f[0], )
        val      =  threshold_otsu(img_f)                        # Otsu threshold of the whole 3D matrix
        # val_ref  =  np.argmin(np.abs(hh_f[1] - val))
        # thr_study  =  np.zeros(img_f.shape, dtype=np.int32)
        # for k in range(50):
        #     thr_study  +=  (img_f > hh_f[0][val_ref - k + 25])


        img_bff  =  (img_f > val).astype(np.uint8)               # thresholding

        int_prof  =  np.sum(img_bff, axis=(1, 2))                 # intensity profile of the thresholded image
        min_loc   =  find_peaks(int_prof.max() - int_prof)[0]     # find local minima of the profile
        right_fr  =  img[fr_select]                               # the "right" frame is the one with the highest intensity

        self.img_bff   =  img_bff
        self.right_fr  =  right_fr
        self.img_bw    =  img_bff[fr_select]
        self.fr_sel    =  fr_select


class ManualSet:
    """This function gives the same output as the previous, but the frame is input"""
    def __init__(self, img, fr_select, lg_kern=.9):

        img      -=  img.min()
        img_f     =  laplace(gaussian(img, lg_kern))              # 3D Gaussian of the raw data matrix
        val       =  threshold_otsu(img_f)                        # Otsu threshold of the whole 3D matrix
        img_bff   =  (img_f > val).astype(np.uint8)               # thresholding
        right_fr  =  img[fr_select]                               # the "right" frame is the one with the highest intensity

        self.img_bff   =  img_bff
        self.right_fr  =  right_fr
        self.img_bw    =  img_bff[fr_select]
        self.fr_sel    =  fr_select


class SearchFramePreprocess:
    """Only class, does all the job"""
    def __init__(self, img, fr_select, gs_kern=1.):

        img_f    =  gaussian(img, gs_kern)                       # 3D Gaussian of the raw data matrix
        val      =  threshold_otsu(img_f)                        # Otsu threshold of the whole 3D matrix
        img_bff  =  (img_f > val).astype(np.uint8)               # thresholding

        self.img_bw  =  img_bff[fr_select]
