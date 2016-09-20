# -*- coding: utf-8 -*-
# Plugin to compute sea water vertical diffusivity from temperature and potential salinity
# Revision by Paolo Oliveri, May 24, 2016
from __future__ import print_function, division
import sys
import numpy as np
import numpy.ma as ma
import seawater as sw
from comic import type as sp_type
# np.set_printoptions(threshold=np.nan)  # It slows debugging
# This to not display overflow warnings
np.seterr(divide='ignore', invalid='ignore', over='ignore')


# Input - Output
lout = 'votkeavt'   #Vertical diffusivity 
lin = ('votemper', 'vosaline')

epsilon = 1.5e-9
gamma = 0.2


def processor(input_list):
    print('Compute ', lout, 'from ', lin)
    # Select variables
    votemper = input_list['votemper']
    vosaline = input_list['vosaline']
    DepthLayers = votemper.DepthLayers
    LatCells = votemper.LatCells
    # Replicate geometry 3D (to be updated with complete model geometry variables)
    if np.ndim(votemper.LatCells) == 1 and np.ndim(votemper.LonCells) == 1 and np.ndim(votemper.DepthLayers) == 1:
        DepthLayers = np.transpose(np.tile(votemper.DepthLayers,
                                           (votemper.LatCells.shape[0], votemper.LonCells.shape[0], 1)), (2, 0, 1))
        LatCells = np.transpose(np.tile(votemper.LatCells,
                                        (votemper.LonCells.shape[0], 1)), (1, 0))
    # Concatenate latitude, longitude and depth cells at the centers of the grid
    # (COMIC TYPE CHARACTERISTIC reserved procedure)
    depths = 1 / 4 * (DepthLayers[1:, 1:, 1:] + DepthLayers[: - 1, : - 1, 1:] +
                      DepthLayers[: - 1, 1:, : - 1] + DepthLayers[: - 1, : - 1, : - 1])
    vertical_layers = np.empty(shape=depths.shape, dtype=float)
    vertical_layers[0, :, :] = 1 / 4 * (DepthLayers[1, 1:, 1:] + DepthLayers[1, : - 1, 1:] +
                                        DepthLayers[1, 1:, : - 1] + DepthLayers[1, : - 1, : - 1])
    vertical_layers[1:, :, :] = 1 / 4 * ((DepthLayers[2:, 1:, 1:] + DepthLayers[2:, : - 1, 1:] +
                                         DepthLayers[2:, 1:, : - 1] + DepthLayers[2:, : - 1, : - 1]) -
                                         (DepthLayers[1: - 1, 1:, 1:] + DepthLayers[1: - 1, : - 1, 1:] +
                                          DepthLayers[1: - 1, 1:, : - 1] + DepthLayers[1: - 1, : - 1, : - 1]))
    lats = 1 / 4 * (LatCells[1:, 1:] + LatCells[: - 1, 1:] +
                    LatCells[1:, : - 1] + LatCells[: - 1, : - 1])
    print('WARNING 22 : not able to compute correctly vertical integrals, not available complete grid geometry '
                      'depth layers variable.', file=sys.stderr)
    # Cut Time Dimension
    temp = votemper.COSM[0, ...]
    salt = vosaline.COSM[0, ...]
    # 100m depth cut (here we add 1 to depth cut because in the bfrq the z derivative component removes bottom depth)
    cutdepth = 0
    while (depths[cutdepth, :, :] < 100).all():
        cutdepth += 1
    depths = depths[: cutdepth + 1, :, :]
    vertical_layers = vertical_layers[: cutdepth, :, :]
    temp = temp[: cutdepth + 1, :, :]
    salt = salt[: cutdepth + 1, :, :]
    # Compute Pressure 3D
    pressure = sw.pres(depths, lats)
    # Transpose elements to input to seawater module
    swtemp = np.transpose(temp, (0, 2, 1))
    swsalt = np.transpose(salt, (0, 2, 1))
    swpressure = ma.array(np.transpose(pressure, (0, 2, 1)), mask=temp.mask, fill_value=1.e20, dtype=float)
    swlats = np.transpose(lats)
    # BV Frequency calculation 3D
    swn2, q, p_ave = sw.bfrq(swsalt, swtemp, swpressure, swlats)
    # Transpose again axes in the correct order
    n2 = np.transpose(swn2, (0, 2, 1))
    # Integrated BV calculation
    bv_int = np.nansum(n2 * vertical_layers, 0) / np.nansum(vertical_layers, 0)
    bv_int = ma.masked_where(temp.mask[0, ...], bv_int)
    k_vert = ma.array(np.empty(shape=votemper.COSM[:, 0, ...].shape), mask=False, fill_value=1.e20, dtype=float)
    k_vert[0, ...] = (1 / bv_int) * epsilon * gamma
    # Attributes of Characteristic class are (StandardName,
    # VariableName, DepthLayers, LonCells, LatCells, TimeCells, ConcatenatioOfSpatialMaps, MaskedAs=None)
    vertical_diffusivity = sp_type.Characteristic(StandardName='ocean_vertical_diffusivity',
                                                  VariableName='votkeavt', DepthLayers=None,
                                                  LonCells=votemper.LonCells, LatCells=votemper.LatCells,
                                                  TimeCells=votemper.TimeCells, ConcatenatioOfSpatialMaps=k_vert)
    return vertical_diffusivity
