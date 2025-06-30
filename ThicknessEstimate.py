"""This function estimates the average thickness in the different sectors.

Inputs are membrane and sectors.
"""


import numpy as np
from skimage.measure import regionprops_table


class ThicknessEstimate:
    """Only class, does all the job"""
    def __init__(self, memb_clean, sectors):

        memb_sects  =  memb_clean * sectors                                                                 # split the clean membrane in sectors
        sect_idxs   =  np.unique(sectors[sectors != 0])
        rgp_mb      =  regionprops_table(memb_sects, properties=["label", "axis_major_length", "area"])     # for each sector region properties
        membs_tcks  =  np.zeros((sect_idxs.size, 2))                                                     # initialize output matrix: label and thickness

        for cnt, gg in enumerate(sect_idxs):
            ll  =  np.where(rgp_mb["label"] == gg)[0]
            # print(ll)
            if ll.size == 1:
                membs_tcks[cnt, :]  =  rgp_mb["label"][ll[0]], rgp_mb["area"][ll[0]] / rgp_mb["axis_major_length"][ll[0]]       # thickness is estimated as ratio between area and the length of the major axis (ellipsoidal fitting)
            elif ll.size == 0:
                membs_tcks[cnt, 0]  =  gg

        self.membs_tcks  =  membs_tcks
