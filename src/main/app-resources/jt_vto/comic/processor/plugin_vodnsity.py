# -*- coding: utf-8 -*-
# Plugin to compute sea water density from temperature and potential salinity
# Revision by Paolo Oliveri, May 24, 2016
from __future__ import print_function, division
import numpy as np
import numpy.ma as ma
import seawater as sw
from comic import type as sp_type
# np.set_printoptions(threshold=np.nan)  # It slows debugging
np.seterr(divide='ignore', invalid='ignore', over='ignore')

# Input - Output
lout = 'vodnsity'    #density
lin = ('votemper', 'vosaline')


# Main program
def processor(input_list):
    print('Compute ', lout, ' from ', lin)
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
    lats = 1 / 4 * (LatCells[1:, 1:] + LatCells[: - 1, 1:] +
                    LatCells[1:, : - 1] + LatCells[: - 1, : - 1])
    # Cut time dimension
    temp = votemper.COSM[0, ...]
    salt = vosaline.COSM[0, ...]
    # Compute Pressure 3D
    pressure = sw.pres(depths, lats)
    # Compute Potential Density field 3D
    density = ma.array(np.empty(shape=votemper.COSM.shape), mask=False, fill_value=1.e20, dtype=float)
    density[0, ...] = sw.dens(salt, temp, pressure)
    # Attributes of Characteristic class are (StandardName,
    # VariableName, DepthLayers, LonCells, LatCells, TimeCells, ConcatenatioOfSpatialMaps, MaskedAs=None)
    potential_d = sp_type.Characteristic(StandardName='sea_water_density',
                                         VariableName='vodnsity', DepthLayers=votemper.DepthLayers,
                                         LonCells=votemper.LonCells, LatCells=votemper.LatCells,
                                         TimeCells=votemper.TimeCells, ConcatenatioOfSpatialMaps=density)
    return potential_d
