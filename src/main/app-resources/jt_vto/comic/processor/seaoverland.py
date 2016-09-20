# Sea Over Land Function, Paolo Oliveri, Jun 22, 2016
# This function ONLY works with numpy.ma masked 2D arrays or ND arrays
# working with the last two axes (not working with NaNs or other)
# Update for shift matrix RAM allocation improvement
# -*- coding: utf-8 -*-
from __future__ import print_function, division
import sys
import numpy as np
import numpy.ma as ma
# np.set_printoptions(threshold=np.nan)  # It slows debugging


def seaoverland(input_matrix, nloop=1):  # depth is to select the number of consequential mask points to fill
    # depth loop
    if np.sum(input_matrix.mask) == 0:  # nothing to flood
        print('WARNING 23. Field does not have any land point. Exiting.', file=sys.stderr)
        return input_matrix
    infill_value = input_matrix.fill_value
    for loop in range(nloop):
        if loop == 0:
            original_mask = input_matrix.mask
            output_matrix = np.where(input_matrix.filled() == infill_value, 0, input_matrix.filled())
        else:
            if np.sum(output_matrix.mask) == 0:  # nothing more to flood
                print('WARNING 23. Field does not have anymore land points,', str(loop), 'steps were sufficient to flood it completely.', file=sys.stderr)
                return output_matrix
            original_mask = output_matrix.mask
            output_matrix = np.where(output_matrix.filled() == infill_value, 0, output_matrix.filled())
        # Create a nD 3D matrix that contains values  shifted in one of the 8 possible directions
        # of the last two axes compared to the original matrix
        shift_matrix = ma.array(np.zeros(shape=output_matrix.shape),
                                mask=False, fill_value=infill_value, dtype=float)
        weight_matrix = ma.array(np.zeros(shape=output_matrix.shape),
                                 mask=False, fill_value=infill_value, dtype=float)
        # up shift
        shift_matrix[..., : - 1, :] = output_matrix[..., 1:, :]
        weight_matrix[..., : - 1, :] = np.where(original_mask[..., 1:, :], 0, 1)
        # down shift
        shift_matrix[..., 1:, :] += output_matrix[..., 0: - 1, :]
        weight_matrix[..., 1:, :] += np.where(original_mask[..., 0: - 1, :], 0, 1)
        # left shift
        shift_matrix[..., :, : - 1] += output_matrix[..., :, 1:]
        weight_matrix[..., :, : - 1] += np.where(original_mask[..., :, 1:], 0, 1)
        # right shift
        shift_matrix[..., :, 1:] += output_matrix[..., :, : - 1]
        weight_matrix[..., :, 1:] += np.where(original_mask[..., :, : - 1], 0, 1)
        # up-left shift
        shift_matrix[..., : - 1, : - 1] += output_matrix[..., 1:, 1:]
        weight_matrix[..., : - 1, : - 1] += np.where(original_mask[..., 1:, 1:], 0, 1)
        # up-right shift
        shift_matrix[..., : - 1, 1:] += output_matrix[..., 1:, : - 1]
        weight_matrix[..., : - 1, 1:] += np.where(original_mask[..., 1:, : - 1], 0, 1)
        # down-left shift
        shift_matrix[..., 1:, : - 1] += output_matrix[..., : - 1, 1:]
        weight_matrix[..., 1:, : - 1] += np.where(original_mask[..., : - 1, 1:], 0, 1)
        # down-right shift
        shift_matrix[..., 1:, 1:] += output_matrix[..., : - 1, : - 1]
        weight_matrix[..., 1:, 1:] += np.where(original_mask[..., : - 1, : - 1], 0, 1)
        # Mask the matrices where there are zeros
        shift_matrix = ma.masked_where(shift_matrix == 0, shift_matrix)
        weight_matrix = ma.masked_where(weight_matrix == 0, weight_matrix)
        # Mediate the shift matrix among the third dimension
        mean_matrix = shift_matrix / weight_matrix
        # Replace input masked points with new ones belonging to the mean matrix
        output_matrix = ma.array(np.where(mean_matrix.mask + original_mask, mean_matrix, output_matrix),
                                     mask=mean_matrix.mask, fill_value=infill_value, dtype=float)
    return output_matrix
