##############################################################################
#                                                                            #
#   PopMesh for Blender 2.93  --  Copyright (C) 2023  Pan Thistle            #
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


# *** Changing the following values could result in unpredictable behaviour ***


# PATH/PROFILE MAXIMUM SEGMENTS (int)
MAX_SEGS = 300

# PATH/PROFILE/BLEND DEFAULT DIMENSIONS (float)
DEF_DIM_PATH = 20
DEF_DIM_PROF = 5

# EDIT-COLLECTIONS FACTOR (float, RANGE IN [-MAX_FAC, MAX_FAC])
MAX_FAC = 200

# INTERPOLATION EASING EXPONENTS (float)
MIN_EXP = 0.5
MAX_EXP = 5.0

# ANIMATION
# INDEX OFFSET (int, RANGE IN [-MAX_IDX_OFF, MAX_IDX_OFF]))
MAX_IDX_OFF = 50
