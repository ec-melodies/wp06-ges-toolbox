# -*- coding: utf-8 -*-
# Plugin to compute kinetic energy per unit volume from sea water speed variables
# Revision by Paolo Oliveri, May 24, 2016
from __future__ import print_function, division
import sys
import numpy as np
import numpy.ma as ma
from comic import type as sp_type
from seaoverland import seaoverland
from uvtotmask import uvtotmask

# np.set_printoptions(threshold=np.nan)  # It slows debugging

# Input - Output
lout = 'vokenerg'   #kinetic energy
lin = ('vozocrtx', 'vomecrty')

# Common Constants
rho0 = 1035  # (kg/m^3) Reference Density (Nemo Book 3.4)


# Main program
def processor(input_list):
    print('Compute ', lout, ' from ', lin)
    # Select variables
    vozocrtx = input_list['vozocrtx']
    vomecrty = input_list['vomecrty']
    uLatCells = vozocrtx.LatCells
    uLonCells = vozocrtx.LonCells
    vLatCells = vomecrty.LatCells
    vLonCells = vomecrty.LonCells
    staggered = False
    # Staggered grid check
    if not (np.array_equal(uLatCells, vLatCells) and np.array_equal(uLonCells, vLonCells)):
        staggered = True
        print('WARNING 21 : Input ', lin,
              ' grids are not equal. Treating them as components of a staggered C-grid.', file=sys.stderr)
    # Cut time dimension
    ucur = vozocrtx.COSM[0, ...]
    vcur = vomecrty.COSM[0, ...]
    # Transport variables to T-grid before calculi (more error)
    # if staggered:
    #     # Apply 1 point sea-over-land
    #     ucur = seaoverland(ucur)
    #     vcur = seaoverland(vcur)
    #     ucur[:, 1:, 1:] = 1 / 2 * (ucur[:, 1:, 1:] + ucur[:, 1:, : - 1])
    #     vcur[:, 1:, 1:] = 1 / 2 * (vcur[:, 1:, 1:] + vcur[:, : - 1, 1:])
    #     # Place t-Grid recalculated mask
    #     tmask = uvtotmask(vozocrtx.COSM.mask, vomecrty.COSM.mask)
    #     ucur = ma.masked_where(tmask[0, ...], ucur)
    #     vcur = ma.masked_where(tmask[0, ...], vcur)
    #     staggered = False
    # Compute kinetic energy field
    ucurquad = ma.array(ucur, mask=ucur.mask, fill_value=1.e20, dtype=float)
    vcurquad = ma.array(vcur, mask=vcur.mask, fill_value=1.e20, dtype=float)
    kinetic_energy = ma.array(np.empty(shape=vozocrtx.COSM.shape), mask=True, fill_value=1.e20, dtype=float)
    if staggered:
        # Apply 1 point sea-over-land
        ucur = seaoverland(ucur)
        vcur = seaoverland(vcur)
        # Compute kinetic energy with T-grid transport
        ucurquad[:, 1:, 1:] = 1 / 2 * (ucur[:, 1:, 1:] ** 2 + ucur[:, 1:, : - 1] ** 2)
        vcurquad[:, 1:, 1:] = 1 / 2 * (vcur[:, 1:, 1:] ** 2 + vcur[:, : - 1, 1:] ** 2)
        # Place t-Grid recalculated mask
        tmask = uvtotmask(vozocrtx.COSM.mask, vomecrty.COSM.mask)
    else:
        ucurquad = ucur ** 2
        vcurquad = vcur ** 2
        tmask = vozocrtx.COSM.mask
    kinetic_energy[0, ...] = rho0 / 2 * (ucurquad + vcurquad)
    kinetic_energy = ma.masked_where(tmask, kinetic_energy)
    # Attributes of Characteristic class are (StandardName,
    # VariableName, DepthLayers, LonCells, LatCells, TimeCells, ConcatenatioOfSpatialMaps, MaskedAs=None)
    k_energy = sp_type.Characteristic(StandardName='specific_kinetic_energy_of_sea_water',
                                      VariableName='vokenerg', DepthLayers=vozocrtx.DepthLayers,
                                      LonCells=vomecrty.LonCells, LatCells=vozocrtx.LatCells,
                                      TimeCells=vozocrtx.TimeCells, ConcatenatioOfSpatialMaps=kinetic_energy)
    return k_energy
