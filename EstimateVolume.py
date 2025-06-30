"""This function estimùate the volume of the cell.

Input is the raw data matrix (only the channel of interest).
"""


import numpy as np
from skimage.filters import gaussian, threshold_otsu, laplace
from skimage.measure import regionprops_table, label
from scipy.ndimage import binary_fill_holes
from scipy.ndimage import binary_closing

import CustomProgressBar


def check_in_out(msk, x, y):
    """Check if a point is inside or outside the mask."""
    # given a b&w image with a barely ellipsoidal pattern and with missing regions 
    # inside (msk), for a point (x, y) we check it is inside the pattern. We draw a
    # cross with the center in x, y and check that at least 3 of the 4 branches cross
    # the mask. It is not rigourous, but it works for the kind of images we have.

    if msk[x, y] == 1:
        return 1                    # if the point is in a white pixel, no need to check
    else:
        score  =  0                 # define a score
        if msk[x, :y].sum() > 0:    # check if the vertical up branch crosses the mask 
            score  +=  1            # if it does the score increases
        if msk[x, y:].sum() > 0:    # as before
            score  +=  1
        if msk[:x, y].sum() > 0:
            score  +=  1
        if msk[x:, y].sum() > 0:
            score  +=  1
        if score > 2:
            return 1                # if the result is 3 or 4 we consider the point as inside the mask
        elif score <= 2:
            return 0


class EstimateVolume:
    def __init__(self, img):

        gs_kern  =  4.                                          # gaussian smoothing with very big kernel (not searching for details)
        zlen     =  img.shape[0]                                # number of z planes
        img_f    =  np.zeros_like(img)                          # initialize
        for tt in range(zlen):
            img_f[tt]    =  gaussian(img[tt], gs_kern)           # 3D Gaussian of the raw data matrix z by z

        val      =  threshold_otsu(img_f)                        # Otsu threshold of the whole 3D matrix
        img_bff  =  (img_f > val).astype(np.uint8)               # thresholding

        for mm in range(zlen):
            img_bff[mm]  =  binary_fill_holes(img_bff[mm])       # fill holes of the b&w image

        img_lbls_tot  =  label(img_bff)                          # label the connected components
        rgp_tot       =  regionprops_table(img_lbls_tot, properties=["label", "area"])                                  # regionprops of the components
        img_fin2      =  (img_lbls_tot == rgp_tot["label"][np.argmax(rgp_tot["area"])]).astype(np.uint16)               # take just the biggest one

        img_fin   =  np.copy(img_fin2)                                                          # copy of the matrix to work on it
        img_sum   =  np.sign(img_fin2.sum(0))                                                   # sum on z to find all the possible pixels making the cell (involved in the volume)
        one_pts   =  np.asarray(np.where(img_sum != 0)).transpose()                             # array with the coordinates of all these pixels (reshape and reorganized for computational purposes)

        frms2work  =  []                                                                        # initialize the list of frames to work on
        for ll in range(zlen):
            bff  =  regionprops_table(img_fin2[ll], properties=["solidity"])["solidity"]        # for each frame we measure the solidity of the connected components inside
            if bff.size == 1 and bff < 0.8:                                                     # check a component is there (bff.size) and its solidity is low (compact well detected objects have a high value)
                frms2work.append(ll)                                                            # add to the list

        pbar  =  CustomProgressBar.ProgressBar(total1=len(frms2work))
        pbar.show()

        for cnt, frm2work in enumerate(frms2work):
            pbar.update_progressbar(cnt)
            for uu in one_pts:                                                                      # for each of the identified points
                img_fin[frm2work, uu[0], uu[1]]  =  check_in_out(img_fin2[frm2work], uu[0], uu[1])  # use the check_in_out function and add correct the pixel value

            img_fin[frm2work]  =  binary_closing(img_fin[frm2work], iterations=50)                  # result can be noisy (salt and pepper) so closing is needed

        pbar.close()

        self.img_fin  =  img_fin




# int_prof  =  np.sum(img_bff, axis=(1, 2))                 # intensity profile of the thresholded image
# min_loc   =  find_peaks(int_prof.max() - int_prof)[0]     # find local minima of the profile
#
# ff        =  [int_prof[k] for k in min_loc]               # values of the intensity at the local minima
# fr_sel    =  min_loc[np.argmax(ff)]
# right_fr  =  img[fr_sel]                                 # the "right" frame is the one with the highest intensity
# pg.image(img_bff[fr_sel])

