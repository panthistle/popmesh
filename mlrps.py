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
# ----------------------------- IMPORTS ----------------------------------------


import math


# ------------------------------------------------------------------------------
#
# ------------------------- INTERPOLATION LISTS --------------------------------


def itlinear(t, m):

    if m:
        return 2 * t if t < 0.5 else 2 - 2 * t
    return t


def ease_out(t, p, m):

    if m:
        return (2 * t) ** p if t < 0.5 else (2 - 2 * t) ** p
    return t**p


def ease_in(t, p, m):

    if m:
        return 1 - (1 - 2 * t) ** p if t < 0.5 else 1 - (2 * t - 1) ** p
    return 1 - (1 - t) ** p


def ease_in_out(t, p, m):

    if m:
        v = math.sin(t * math.pi)
        return v**p
    return (2 * t) ** p / 2 if t < 0.5 else 1 - ((2 - 2 * t) ** p / 2)


def ease_list(ease, dt, p, m, count):

    if ease == "LINEAR":
        return [itlinear(i * dt, m) for i in range(count)]
    if ease == "OUT":
        return [ease_out(i * dt, p, m) for i in range(count)]
    if ease == "IN":
        return [ease_in(i * dt, p, m) for i in range(count)]
    return [ease_in_out(i * dt, p, m) for i in range(count)]
