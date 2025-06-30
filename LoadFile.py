"""This function loads .dv files as numpy array.

"""

# import javabridge
# import bioformats
import numpy as np
import mrc

# path  =  '/home/atrullo/Dropbox/Cyril_Alexia/20201210_RI508_BJ_DNA-DAPI_Pha-TRITC_stainingLMNA-on_LMNA-A488_cond-0p5kPa_010_SIR_ALX.dv'
# path  =  '/home/atrullo/Dropbox/Cyril_Alexia/Data/20201210_RI508_BJ_DNA-DAPI_Pha-TRITC_stainingLMNA-on_LMNA-A488_cond-50kPa_015_SIR_ALX.dv'


class LoadFile:
    """Only class, does all the job"""
    def __init__(self, path):

        img_fin  =  mrc.imread(path)
        img_fin  =  np.rot90(img_fin, k=3, axes=(2, 3))    # just manipulate to put it in imagej format
        img_fin  =  np.moveaxis(img_fin, [0], [3])

        self.img_fin  =  img_fin


# class LoadFile:
#     """Only class, does all the job"""
#     def __init__(self, path):
#
#         img_fin  =  None
#         # javabridge.start_vm(class_path=bioformats.JARS)
#
#         # aa  =  list()
#         # for z_idx in range(1000):
#         #     try:
#         #         aa.append(bioformats.load_image(path, c=None, z=z_idx, t=0))
#         #     except Exception:
#         #         break
#         #
#         #     img_fin  =  np.zeros((len(aa),) + aa[0].shape)
#         #     for zz, bb in enumerate(aa):
#         #         img_fin[zz]  =  bb
#         #
#         # javabridge.kill_vm()
#
#         img_fin  =  mrc.imread(path)
#         # img_fin  =  img_fin[:, :, ::-1]
#         img_fin  =  np.rot90(img_fin, k=3, axes=(2, 3))
#
#         self.img_fin  =  img_fin
