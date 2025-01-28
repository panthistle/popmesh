##############################################################################
#                                                                            #
#   PopMesh for Blender  --  Copyright (C) 2024  Pan Thistle                 #
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

#################  FOR USE WITH BLENDER VERSION 3.6  #########################


#bl_info = {
#    "name": "PTDBLNPOPM",
#    "description": "path-on-path mesh generator",
#    "author": "Pan Thistle",
#    "version": (2, 5, 0),
#    "blender": (3, 6, 0),
#    "location": "View3D > UI",
#    "doc_url": "https://panthistle.github.io/pdfs/PMUG25.pdf",
#    "category": "Mesh",
#}


# ------------------------------------------------------------------------------
#
# ----------------------------- IMPORTS ----------------------------------------


from . import bmpgs
from . import bmops
from . import bmuil


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------


def register():
    bmpgs.register()
    bmops.register()
    bmuil.register()


def unregister():
    bmuil.unregister()
    bmops.unregister()
    bmpgs.unregister()
