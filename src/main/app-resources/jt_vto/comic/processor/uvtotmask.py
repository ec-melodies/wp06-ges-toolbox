# Umask, Vmask to Tmask Function, Paolo Oliveri, May 13 2016
# This function ONLY works with numpy.ma masked ND arrays with N >=3,
# working with the last two axes (not working with NaNs or other)
# -*- coding: utf-8 -*-
import numpy as np
# np.set_printoptions(threshold=np.nan)  # It slows debugging


def uvtotmask(umask, vmask):
    if umask.shape == vmask.shape:
        tumask = np.zeros(shape=umask.shape, dtype=int)
        tvmask = np.zeros(shape=vmask.shape, dtype=int)
        umask = 1 * np.invert(umask)
        vmask = 1 * np.invert(vmask)
        tumask[..., :, 1:] = umask[..., :, 1:] + umask[..., :, : -1]
        tvmask[..., 1:, :] = vmask[..., 1:, :] + vmask[..., : -1, :]
        tmask = tumask + tvmask
        tmask = np.invert(tmask.astype(bool))
    else:
        raise ValueError('umask and vmask have not the same size.')
    return tmask
