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
# ---------------------------- ADDON INFO --------------------------------------


bl_info = {
    "name": "PTDBLNPOPM",
    "description": "path-on-path mesh",
    "author": "Pan Thistle",
    "version": (1, 0, 0),
    "blender": (2, 93, 0),
    "location": "View3D > UI",
    "doc_url": "https://github.com/panthistle/popmesh",
    "category": "Mesh",
}


# ------------------------------------------------------------------------------
#
# ----------------------------- IMPORTS ----------------------------------------


from . import pgs
from . import ops
from . import uil


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------


def register():
    pgs.register()
    ops.register()
    uil.register()


def unregister():
    uil.unregister()
    ops.unregister()
    pgs.unregister()
