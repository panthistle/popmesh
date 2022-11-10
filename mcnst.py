
##############################################################################
#                                                                            #
#   PopMesh for Blender 2.93  --  Copyright (C) 2022  Pan Thistle            #
#                                                                            #
#   This program is free software: you can redistribute it and/or modify     #
#   it under the terms of the GNU General Public License as published by     #
#   the Free Software Foundation, either version 3 of the License, or        #
#   (at your option) any later version.                                      #
#                                                                            #
#   This program is distributed in the hope that it will be useful,          #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#   GNU General Public License for more details.                             #
#                                                                            #
#   You should have received a copy of the GNU General Public License        #
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.   #
#                                                                            #
##############################################################################


# ------------------------------------------------------------------------------
#
# ---------------- POPMESH RECOMMENDED GLOBAL SETTINGS -------------------------

# *** Changing the following values may lead to unpredictable behaviour ***


# SEGMENTS
MAX_SEGS = 300

# DIMENSIONS
MIN_DIM = -1000
MAX_DIM = 1000
DEF_DIM_PATH = 20
DEF_DIM_PROF = 5

# FACTORS RANGE IN [1/MAX, MAX] OR [-MAX, MAX]
MAX_FAC = 1000

# NOISE
MAX_NOIZ = 50

# INTERPOLATION EXPONENTS
MIN_EXP = 0.5
MAX_EXP = 5.0

# ANIMATION
MAX_IDX_OFF = 50
MAX_INOUT = 500
DEF_TRK_BLN = 'REPLACE'
DEF_TRK_XPL = 'HOLD'
DEF_TRK_BLENDAUTO = False
DEF_TRK_BLENDIN = 0
DEF_TRK_BLENDOUT = 0
