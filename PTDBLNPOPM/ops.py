
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
# ----------------------------- IMPORTS ----------------------------------------

import bpy
import os
import json

from mathutils import Quaternion, Vector
from bpy_extras.io_utils import ImportHelper, ExportHelper

from . import mcnst as ModCnst
from . import mmpop as ModPop


# ------------------------------------------------------------------------------
#
# ----------------------------- OPERATORS --------------------------------------

def validate_scene_object(scene, ob):

    if ob and (ob.name not in scene.objects):
        bpy.data.objects.remove(ob)


def clear_edit_collections(props):
    # *** callbacks must be disabled ***

    props.plox.clear()
    props.plox_idx = -1
    props.plox_disabled = False
    props.proflox.clear()
    props.proflox_idx = -1
    props.proflox_disabled = False
    props.blpc.clear()
    props.blpc_idx = -1
    props.blpc_disabled = False


def restore_defaults(props):
    # *** callbacks must be disabled ***

    # path
    path = props.path
    path.upv.clear()
    path.user_ob = None
    path.closed = False
    keys = ('endcaps', 'idx', 'res_lin', 'lin_dim', 'lin_lerp', 'lin_exp',
            'lin_axis', 'res_spi', 'spi_dim', 'spi_revs', 'user_bbc', 'u_dim',
            'res_rct', 'rct_dim', 'round_segs', 'round_off', 'res_ell',
            'ell_dim', 'bump', 'bump_val', 'bump_exp', 'provider')
    for key in keys:
        path.property_unset(key)
    # prof
    prof = props.prof
    prof.upv.clear()
    prof.user_ob = None
    keys = ('res_rct', 'round_segs', 'round_off', 'rct_dim', 'res_ell',
            'ell_dim', 'bump', 'bump_val', 'bump_exp', 'user_bbc', 'u_dim',
            'closed', 'reverse', 'idx', 'provider')
    for key in keys:
        prof.property_unset(key)
    # edit collections
    for item in props.blpc:
        item.upv.clear()
        item.user_ob = None
    clear_edit_collections(props)
    # edit pointers
    props.spro.active = False
    props.noiz.active = False
    props.rngs.active = False
    props.obrot.active = False
    # shading options / warnings
    keys = ('show_warn', 'show_wire', 'auto_smooth', 'shade_smooth')
    for key in keys:
        props.property_unset(key)


# ---- POP OPERATORS

class PTDBLNPOPM_OT_update_default(bpy.types.Operator):

    bl_label = "Update"
    bl_idname = "ptdblnpopm.update_default"
    bl_description = "pop setup"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        try:
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'update_default: {my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_new_mesh(bpy.types.Operator):

    bl_label = "New"
    bl_idname = "ptdblnpopm.new_mesh"
    bl_description = "new mesh from current settings"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            props.callbacks = False
            # switch possible animation state
            # - allow old mesh to keep animations -
            props.trax.clear()
            props.trax_idx = -1
            props.trax_disabled = False
            props.animorph = False
            # create new mesh / store reference
            name = 'pop_mesh'
            me = bpy.data.meshes.new(name)
            ob = bpy.data.objects.new(name, me)
            scene.collection.objects.link(ob)
            ob.rotation_mode = 'QUATERNION'
            props.pop_mesh = ob
            # validate current settings
            if not(props.path.clean and props.prof.clean):
                # use default setup
                restore_defaults(props)
            props.callbacks = True
            # scene updates
            ModPop.mesh_smooth_normals(ob, props.auto_smooth)
            ModPop.mesh_show_wire(ob, props.show_wire)
            ModPop.scene_update(scene)
        except Exception as my_err:
            props.callbacks = True
            print(f'new_mesh: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_pop_reset(bpy.types.Operator):

    bl_label = "Reset"
    bl_idname = "ptdblnpopm.pop_reset"
    bl_description = "reset mesh - load default settings"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        ob = props.pop_mesh
        try:
            props.callbacks = False
            # use default setup
            restore_defaults(props)
            props.callbacks = True
            # scene updates
            ModPop.mesh_smooth_normals(ob, props.auto_smooth)
            ModPop.mesh_show_wire(ob, props.show_wire)
            ModPop.scene_update(scene)
        except Exception as my_err:
            props.callbacks = True
            print(f'pop_reset: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_update_ranges(bpy.types.Operator):

    bl_label = "Default Update"
    bl_idname = "ptdblnpopm.update_ranges"
    bl_description = "pop update - ranges"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            ModPop.scene_update(scene, setup='range')
        except Exception as my_err:
            print(f'update_ranges: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_update_preset(bpy.types.Operator):

    bl_label = "Update Preset"
    bl_idname = "ptdblnpopm.update_preset"
    bl_description = "pop setup - preset"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    # callers: ['path', 'prof']
    caller: bpy.props.StringProperty(default='none', options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            props.callbacks = False
            # clear corresponding user_ob / verts collection
            if self.caller == 'path':
                props.path.user_ob = None
                props.path.upv.clear()
            else:
                props.prof.user_ob = None
                props.prof.upv.clear()
                for item in props.blpc:
                    item.active = False
            props.callbacks = True
            ModPop.scene_update(scene, setup='all')
        except Exception as my_err:
            props.callbacks = True
            print(f'update_preset: {my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_update_user(bpy.types.Operator):

    bl_label = "Update User"
    bl_idname = "ptdblnpopm.update_user"
    bl_description = "pop setup - user"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    # callers: ['path', 'prof']
    caller: bpy.props.StringProperty(default='none', options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            props.callbacks = False
            # get caller pg
            if self.caller == 'prof':
                ndims = 2
                pg = props.prof
                for item in props.blpc:
                    item.active = False
            else:
                ndims = 3
                pg = props.path
            # user object validation
            validate_scene_object(scene, pg.user_ob)
            ob = pg.user_ob
            props.callbacks = True
            if not ob:
                # scene update checks invalid path/profile
                ModPop.scene_update(scene, setup='all')
                return {'FINISHED'}
            # get user mesh verts [raises invalid-data Exception]
            verts = ModPop.user_mesh_verts(ob.data)
            # replace user-pg verts
            pg.upv.clear()
            for v in verts:
                i = pg.upv.add()
                i.vert = v
            # property group updates
            for i in range(ndims):
                v = round(ob.dimensions[i], 5)
                v = min(max(ModCnst.MIN_DIM, v), ModCnst.MAX_DIM)
                pg.user_dim[i] = v
                pg.u_dim[i] = v
            bb = ob.bound_box
            pg.user_bbc = 0.125 * sum((Vector(b) for b in bb), Vector())
            # scene update
            ModPop.scene_update(scene, setup='all')
        except Exception as my_err:
            props.callbacks = True
            print(f'update_user: {my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_pop_rotate(bpy.types.Operator):

    bl_label = "Rotation [Object]"
    bl_idname = "ptdblnpopm.pop_rotate"
    bl_description = "object rotation"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    axis: bpy.props.FloatVectorProperty(name='Axis',
            description='rotation axis', size=3, default=[0, 0, 1],
            min=-1, max=1)
    rot_ang: bpy.props.FloatProperty(name='Angle',
            description='rotation angle', default=0, subtype='ANGLE')

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopm_props.obrot.active

    def invoke(self, context, event):
        obrot = context.scene.ptdblnpopm_props.obrot
        # self updates
        self.axis = obrot.axis
        self.rot_ang = obrot.rot_ang
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        obrot = props.obrot
        # property group updates
        obrot.axis = self.axis
        obrot.rot_ang = self.rot_ang
        try:
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'pop_rotate: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text='Angle')
        row = sc.row()
        row.label(text='Axis')
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, 'rot_ang', text='')
        row = sc.row(align=True)
        row.prop(self, 'axis', text='')


class PTDBLNPOPM_OT_display_options(bpy.types.Operator):

    bl_label = "Display"
    bl_idname = "ptdblnpopm.display_options"
    bl_description = "shading options"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    option: bpy.props.StringProperty(default='show_wire', options={'HIDDEN'})

    def execute(self, context):
        props = context.scene.ptdblnpopm_props
        try:
            ob = props.pop_mesh
            if self.option == 'shade_smooth':
                ModPop.mesh_smooth_shade(ob, props.shade_smooth)
            elif self.option == 'auto_smooth':
                ModPop.mesh_smooth_normals(ob, props.auto_smooth)
            else:
                ModPop.mesh_show_wire(ob, props.show_wire)
        except Exception as my_err:
            print(f'display_options: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


# ---- PATH OPERATORS

class PTDBLNPOPM_OT_path_edit(bpy.types.Operator):

    bl_label = "Edit [Path]"
    bl_idname = "ptdblnpopm.path_edit"
    bl_description = "path settings"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def path_idx_get(self):
        return self.get('idx', 0)

    def path_idx_set(self, value):
        self['idx'] = value % self.rings

    def path_edit_step_get(self):
        return self.get('step', 1)

    def path_edit_step_set(self, value):
        self['step'] = min(max(1, value), int(self.rings / 2))

    def path_edit_dim_x_update(self, context):
        if self.update_dims:
            self.dim[0] = self.dim_x
        if self.ctl_axis == 0:
            x = self.dim_x
            self.dim_y = x * self.dim_xy
            self.dim_z = x * self.dim_xz

    def path_edit_dim_y_update(self, context):
        if self.update_dims:
            self.dim[1] = self.dim_y
        if self.ctl_axis == 1:
            y = self.dim_y
            self.dim_x = y * self.dim_xy
            self.dim_z = y * self.dim_yz

    def path_edit_dim_z_update(self, context):
        if self.update_dims:
            self.dim[2] = self.dim_z
        if self.ctl_axis == 2:
            z = self.dim_z
            self.dim_x = z * self.dim_xz
            self.dim_y = z * self.dim_yz

    def path_edit_axes_lock_update(self, context):
        self.ctl_axis = -1
        self.dim_xy = 1
        self.dim_xz = 1
        self.dim_yz = 1
        if not (self.update_dims and self.axes_lock):
            return None
        if self.dim_x:
            self.ctl_axis = 0
            x = self.dim_x
            self.dim_xy = 1 if x == 0 else self.dim_y / x
            self.dim_xz = 1 if x == 0 else self.dim_z / x
            return None
        if self.dim_y:
            self.ctl_axis = 1
            y = self.dim_y
            self.dim_xy = 1 if y == 0 else self.dim_x / y
            self.dim_yz = 1 if y == 0 else self.dim_z / y
            return None
        if self.dim_z:
            self.ctl_axis = 2
            z = self.dim_z
            self.dim_xz = 1 if z == 0 else self.dim_x / z
            self.dim_yz = 1 if z == 0 else self.dim_y / z

    def path_edit_closed_update(self, context):
        if self.closed:
            self.endcaps = False

    def path_edit_round_segs_get(self):
        return self.get('round_segs', 0)

    def path_edit_round_segs_set(self, value):
        if self.rings < 8:
            val = 0
        else:
            hi = int(self.rings / 4) - 1
            val = min(max(0, value), hi)
        self['round_segs'] = val

    rings: bpy.props.IntProperty(default=0)
    provider: bpy.props.StringProperty(default='')
    user_dim: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0])
    dim_x: bpy.props.FloatProperty(name='Size',
            description='path dimensions', default=0,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM,
            update=path_edit_dim_x_update)
    dim_y: bpy.props.FloatProperty(name='Size',
            description='path dimensions', default=0,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM,
            update=path_edit_dim_y_update)
    dim_z: bpy.props.FloatProperty(name='Size',
            description='path dimensions', default=0,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM,
            update=path_edit_dim_z_update)
    dim: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0])
    dim_xy: bpy.props.FloatProperty(default=1)
    dim_xz: bpy.props.FloatProperty(default=1)
    dim_yz: bpy.props.FloatProperty(default=1)
    update_dims: bpy.props.BoolProperty(default=False)
    axes_lock: bpy.props.BoolProperty(name='Lock',
            description='lock axes', default=False,
            update=path_edit_axes_lock_update)
    ctl_axis: bpy.props.IntProperty(default=-1)
    # all paths
    idx: bpy.props.IntProperty(name='Offset',
            description='index offset', default=0,
            get=path_idx_get, set=path_idx_set)
    # line-path
    lin_dim: bpy.props.FloatProperty(name='Length',
            description='path dimensions', default=ModCnst.DEF_DIM_PATH,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM)
    lin_axis: bpy.props.FloatVectorProperty(name='Direction', size=3,
            default=[1, 0, 0], min=-1, max=1)
    lin_lerp: bpy.props.EnumProperty(name='Ease',
            description='interpolation type',
            items=( ('IN', 'in', 'ease in'),
                    ('OUT', 'out', 'ease out'),
                    ('IN-OUT', 'in-out', 'ease in and out') ),
            default='IN-OUT')
    lin_exp: bpy.props.FloatProperty(name='Factor',
            description='interpolation exponent',
            default=1, min=ModCnst.MIN_EXP, max=ModCnst.MAX_EXP)
    # spherical spiral path
    spi_dim: bpy.props.FloatProperty(name='Size',
            description='path dimensions', default=ModCnst.DEF_DIM_PATH,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM)
    spi_revs: bpy.props.FloatProperty(name='Revolutions',
            description='spherical spiral revolutions', default=0.5,
            min=-ModCnst.MAX_FAC, max=ModCnst.MAX_FAC)
    # ellipse
    bump: bpy.props.IntProperty(name='V-bumps',
            description='effect steps', default=1,
            get=path_edit_step_get, set=path_edit_step_set)
    bump_val: bpy.props.FloatProperty(name='Factor',
            description='bump value', default=0,
            min=-ModCnst.MAX_FAC, max=ModCnst.MAX_FAC)
    bump_exp: bpy.props.FloatProperty(name='V-exponent',
            description='effect interpolation exponent', default=2,
            min=ModCnst.MIN_EXP, max=ModCnst.MAX_EXP)
    # rectangle (rounded corners)
    round_segs: bpy.props.IntProperty(name='Segments',
            description='rounding segments', default=0,
            get=path_edit_round_segs_get, set=path_edit_round_segs_set)
    round_off: bpy.props.FloatProperty(name='Radius',
            description='rounding offset', default=0.5)
    # user
    closed: bpy.props.BoolProperty(name='Closed',
            description='closed or open path', default=True,
            update=path_edit_closed_update)
    # user and line
    endcaps: bpy.props.BoolProperty(name='Endcaps',
            description='open path end faces - ngons', default=False)

    def invoke(self, context, event):
        path = context.scene.ptdblnpopm_props.path
        # self updates
        pd = self.as_keywords(ignore=('dim_x', 'dim_y', 'dim_z', 'dim_xy',
                                        'dim_xz', 'dim_yz', 'dim', 'ctl_axis',
                                        'axes_lock', 'update_dims'))
        for key in pd.keys():
            setattr(self, key, getattr(path, key))
        if self.provider == 'ellipse':
            self.dim = path.ell_dim
        elif self.provider == 'rectangle':
            self.dim = path.rct_dim
        else:
            self.dim = path.u_dim
        self.axes_lock = False
        self.update_dims = False
        self.dim_x = self.dim[0]
        self.dim_y = self.dim[1]
        self.dim_z = self.dim[2]
        self.update_dims = True
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        path = props.path
        # property group updates
        pd = self.as_keywords(ignore=('rings', 'provider', 'user_dim', 'dim_x',
                                    'dim_y', 'dim_z', 'dim_xy', 'dim_xz',
                                    'dim_yz', 'dim', 'ctl_axis', 'axes_lock',
                                    'update_dims'))
        for key in pd.keys():
            setattr(path, key, getattr(self, key))
        if self.provider == 'ellipse':
            path.ell_dim = self.dim
        elif self.provider == 'rectangle':
            path.rct_dim = self.dim
        else:
            path.u_dim = self.dim
        try:
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'path_edit: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def draw(self, context):
        p_name = self.provider
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row()
        if p_name == 'line':
            row.label(text='Length')
            row = sc.row()
            row.label(text='Direction')
            row = sc.row()
            row.label(text='Index')
            row = sc.row()
            row.label(text='Interpolation')
            row = sc.row()
            row.label(text='Options')
        elif p_name == 'spiral':
            row.label(text='Diameter')
            row = sc.row()
            row.label(text='Index')
            row = sc.row()
            row.label(text='Factor')
        else:
            row.label(text='Lock Axes')
            row = sc.row()
            row.label(text='Size')
            row = sc.row()
            row.label(text='Index')
            row = sc.row()
        if p_name == 'rectangle':
            row.label(text='Rounded')
        elif p_name == 'ellipse':
            row.label(text='Bumps')
        elif p_name == 'custom':
            row.label(text='Options')

        sc = s.column(align=True)
        row = sc.row(align=True)
        if p_name == 'line':
            row.prop(self, 'lin_dim', text='')
            row = sc.row(align=True)
            row.prop(self, 'lin_axis', text='')
            row = sc.row(align=True)
            row.prop(self, 'idx', text='')
            row = sc.row(align=True)
            row.prop(self, 'lin_lerp', text='')
            row.prop(self, 'lin_exp', text='')
            row = sc.row(align=True)
            row.prop(self, 'endcaps', toggle=True)
        elif p_name == 'spiral':
            row.prop(self, 'spi_dim', text='')
            row = sc.row(align=True)
            row.prop(self, 'idx', text='')
            row = sc.row(align=True)
            row.prop(self, 'spi_revs', text='')
        else:
            p_ud = [1,1,0]
            if p_name == 'custom':
                p_ud = [1 if i else 0 for i in self.user_dim]
            row.prop(self, 'axes_lock', toggle=True)
            row = sc.row(align=True)
            col = row.column(align=True)
            col.enabled = bool(p_ud[0]) and (self.ctl_axis < 1)
            col.prop(self, 'dim_x', text='')
            col = row.column(align=True)
            col.enabled = bool(p_ud[1]) and (self.ctl_axis in [-1, 1])
            col.prop(self, 'dim_y', text='')
            col = row.column(align=True)
            col.enabled = bool(p_ud[2]) and (self.ctl_axis in [-1, 2])
            col.prop(self, 'dim_z', text='')
            row = sc.row(align=True)
            row.prop(self, 'idx', text='')
            if p_name == 'custom':
                row = sc.row(align=True)
                rc = row.column(align=True)
                rc.prop(self, 'closed', toggle=True)
                rc = row.column(align=True)
                rc.enabled = not self.closed
                rc.prop(self, 'endcaps', toggle=True)
            elif p_name == 'rectangle':
                row = sc.row(align=True)
                row.enabled = self.rings >= 8
                row.prop(self, 'round_segs', text='')
                row.prop(self, 'round_off', text='')
            elif p_name == 'ellipse':
                row = sc.row(align=True)
                row.prop(self, 'bump', text='')
                row.prop(self, 'bump_val', text='')
                row.prop(self, 'bump_exp', text='')


class PTDBLNPOPM_OT_ploc_add(bpy.types.Operator):

    bl_label = "Add"
    bl_idname = "ptdblnpopm.ploc_add"
    bl_description = "new edit"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        props = context.scene.ptdblnpopm_props
        try:
            item = props.plox.add()
            item.active = False
            props.plox_idx = len(props.plox) - 1
        except Exception as my_err:
            print(f'ploc_add: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_ploc_copy(bpy.types.Operator):

    bl_label = "Copy"
    bl_idname = "ptdblnpopm.ploc_copy"
    bl_description = "copy edit"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def dct_to_pg(self, d, item):
        pd = d.pop('params')
        for key in pd.keys():
            setattr(item.params, key, pd[key])
        for key in d.keys():
            setattr(item, key, d[key])

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            source = props.plox[props.plox_idx]
            d = source.to_dct()
            item = props.plox.add()
            # data transfer
            self.dct_to_pg(d, item)
            props.plox_idx = len(props.plox) - 1
        except Exception as my_err:
            print(f'ploc_copy: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_ploc_enable(bpy.types.Operator):

    bl_label = "Enable"
    bl_idname = "ptdblnpopm.ploc_enable"
    bl_description = "enable/disable edits"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    doall: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            if self.doall:
                boo = props.plox_disabled
                for item in props.plox:
                    item.active = boo
                props.plox_disabled = not boo
            else:
                item = props.plox[props.plox_idx]
                item.active = not item.active
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'ploc_enable: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_ploc_remove(bpy.types.Operator):

    bl_label = "Remove"
    bl_idname = "ptdblnpopm.ploc_remove"
    bl_description = "remove edits"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    doall: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def invoke(self, context, event):
        props = context.scene.ptdblnpopm_props
        if props.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            if self.doall:
                props.plox.clear()
                props.plox_idx = -1
            else:
                idx = props.plox_idx
                props.plox.remove(idx)
                props.plox_idx = min(max(0, idx - 1), len(props.plox) - 1)
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'ploc_remove: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_ploc_move(bpy.types.Operator):

    bl_label = "Move"
    bl_idname = "ptdblnpopm.ploc_move"
    bl_description = "Order edits"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    move_down: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        idx = props.plox_idx
        try:
            if self.move_down:
                if idx < len(props.plox) - 1:
                    props.plox.move(idx, idx + 1)
                    props.plox_idx += 1
            elif idx > 0:
                props.plox.move(idx, idx - 1)
                props.plox_idx -= 1
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'ploc_move: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_ploc_edit(bpy.types.Operator):

    bl_label = "Locations [Path]"
    bl_idname = "ptdblnpopm.ploc_edit"
    bl_description = "path locations"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def plox_idx_get(self):
        return self.get('idx', 0)

    def plox_idx_set(self, value):
        self['idx'] = value % self.rings

    def plox_itm_get(self):
        return self.get('itm', 1)

    def plox_itm_set(self, value):
        self['itm'] = min(max(1, value), self.rings)

    def plox_reps_get(self):
        return self.get('reps', 1)

    def plox_reps_set(self, value):
        self['reps'] = min(max(1, value), self.rings)

    def plox_gap_get(self):
        return self.get('gap', 0)

    def plox_gap_set(self, value):
        self['gap'] = min(max(0, value), self.rings)

    rings: bpy.props.IntProperty(default=0)
    fac: bpy.props.FloatProperty(name='Distance', description='move factor',
            default=0, min=-ModCnst.MAX_FAC, max=ModCnst.MAX_FAC)
    axis: bpy.props.FloatVectorProperty(name='Axis', description='move axis',
            size=3, default=[1, 1, 1], min=-1, max=1)
    abs_move: bpy.props.BoolProperty(name='Absolute',
        description='absolute or relative axis', default=False)
    mir: bpy.props.BoolProperty(name='Mirror',
            description='interpolation mirror', default=False)
    lerp: bpy.props.BoolProperty(name='Lerp',
            description='move interpolation', default=True)
    f2: bpy.props.FloatProperty(name='Factor', description='enhance-fade',
            default=1, min=-2, max=2)
    ease: bpy.props.EnumProperty(name='Ease',
            description='interpolation type',
            items=( ('IN', 'in', 'ease in'),
                    ('OUT', 'out', 'ease out'),
                    ('IN-OUT', 'in-out', 'ease in and out') ),
            default='IN-OUT')
    exp: bpy.props.FloatProperty(name='Exponent',
            description='interpolation exponent', default=1,
            min=ModCnst.MIN_EXP, max=ModCnst.MAX_EXP)
    idx: bpy.props.IntProperty(name='Offset', description='index offset',
            default=0, get=plox_idx_get, set=plox_idx_set)
    itm: bpy.props.IntProperty(name='Items', description='group items',
            default=1, get=plox_itm_get, set=plox_itm_set)
    reps: bpy.props.IntProperty(name='Repeats', description='effect repeats',
            default=1, get=plox_reps_get, set=plox_reps_set)
    gap: bpy.props.IntProperty(name='Gap', description='gap between repeats',
            default=0, get=plox_gap_get, set=plox_gap_set)
    rev: bpy.props.BoolProperty(name='Back', description='reverse direction',
             default=False)

    def copy_from_pg(self, item):
        pkeys = ('idx', 'itm', 'reps', 'gap', 'ease',
                 'exp', 'mir', 'lerp', 'f2', 'rev')
        params = item.params
        for key in pkeys:
            setattr(self, key, getattr(params, key))

    def copy_to_pg(self, item):
        pkeys = ('idx', 'itm', 'reps', 'gap', 'ease',
                 'exp', 'mir', 'lerp', 'f2', 'rev')
        params = item.params
        for key in pkeys:
            setattr(params, key, getattr(self, key))

    def invoke(self, context, event):
        props = context.scene.ptdblnpopm_props
        item = props.plox[props.plox_idx]
        # self updates
        self.rings = props.path.rings
        self.fac = item.fac
        self.axis = item.axis
        self.abs_move = item.abs_move
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        item = props.plox[props.plox_idx]
        # property group updates
        item.fac = self.fac
        item.axis = self.axis
        item.abs_move = self.abs_move
        self.copy_to_pg(item)
        try:
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'ploc_edit: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        names = ['Items', 'Factor', 'Axis', 'Repeats',
                 'Interpolation', 'Options']
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, 'idx', text='')
        row.prop(self, 'itm', text='')
        row.prop(self, 'rev', toggle=True)
        row = sc.row(align=True)
        row.prop(self, 'fac', text='')
        row.prop(self, 'abs_move', toggle=True)
        row = sc.row(align=True)
        row.enabled = self.abs_move
        row.prop(self, 'axis', text='')
        row = sc.row(align=True)
        row.prop(self, 'reps', text='')
        row.prop(self, 'f2', text='')
        row.prop(self, 'gap', text='')
        row = sc.row(align=True)
        col = row.column(align=True)
        col.prop(self, 'lerp', toggle=True)
        col = row.column(align=True)
        col.enabled = self.lerp
        col.prop(self, 'mir', toggle=True)
        row = sc.row(align=True)
        row.enabled = self.lerp
        row.prop(self, 'ease', text='')
        row.prop(self, 'exp', text='')


class PTDBLNPOPM_OT_spinroll(bpy.types.Operator):

    bl_label = "Spinroll [Path]"
    bl_idname = "ptdblnpopm.spinroll"
    bl_description = "path roll and spin rotations"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    rings: bpy.props.IntProperty(default=0)
    rot_ang: bpy.props.FloatProperty(name='Roll Angle',
            description='roll', default=0, subtype='ANGLE')
    spin_ang: bpy.props.FloatProperty(name='Spin Angle',
            description='spin', default=0, subtype='ANGLE')
    follow_limit: bpy.props.BoolProperty(name='Follow Limit',
            description='straight-offset seam', default=True)
    seam_lock: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopm_props.spro.active

    def invoke(self, context, event):
        props = context.scene.ptdblnpopm_props
        # self updates
        self.rings = props.path.rings
        self.seam_lock = props.prof.closed
        spro = props.spro
        self.rot_ang = spro.rot_ang
        self.spin_ang = spro.spin_ang
        self.follow_limit = True if self.seam_lock else spro.follow_limit
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        spro = props.spro
        # property group updates
        spro.rot_ang = self.rot_ang
        spro.spin_ang = self.spin_ang
        spro.follow_limit = self.follow_limit
        try:
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'spinroll: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text='Angle')
        row = sc.row()
        row.label(text='Seam Offset')
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, 'rot_ang', text='')
        row.prop(self, 'spin_ang', text='')
        row = sc.row(align=True)
        row.enabled = not self.seam_lock
        row.prop(self, 'follow_limit', toggle=True)


# ---- PROFILE OPERATORS

class PTDBLNPOPM_OT_prof_edit(bpy.types.Operator):

    bl_label = "Edit [Profile]"
    bl_idname = "ptdblnpopm.prof_edit"
    bl_description = "profile settings"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def prof_idx_get(self):
        return self.get('idx', 0)

    def prof_idx_set(self, value):
        self['idx'] = value % self.rpts

    def prof_edit_step_get(self):
        return self.get('step', 1)

    def prof_edit_step_set(self, value):
        self['step'] = min(max(1, value), int(self.rpts / 2))

    def prof_edit_dim_x_update(self, context):
        if self.update_dims:
            self.dim[0] = self.dim_x
        if self.ctl_axis == 0:
            self.dim_y = self.dim_x * self.dim_xy

    def prof_edit_dim_y_update(self, context):
        if self.update_dims:
            self.dim[1] = self.dim_y
        if self.ctl_axis == 1:
            self.dim_x = self.dim_y * self.dim_xy

    def prof_edit_axes_lock_update(self, context):
        self.ctl_axis = -1
        self.dim_xy = 1
        if not (self.update_dims and self.axes_lock):
            return None
        if self.dim_x:
            self.ctl_axis = 0
            x = self.dim_x
            self.dim_xy = 1 if x == 0 else self.dim_y / x
            return None
        if self.dim_y:
            self.ctl_axis = 1
            y = self.dim_y
            self.dim_xy = 1 if y == 0 else self.dim_x / y

    def prof_edit_round_segs_get(self):
        return self.get('round_segs', 0)

    def prof_edit_round_segs_set(self, value):
        if self.rpts < 8:
            val = 0
        else:
            hi = int(self.rpts / 4) - 1
            val = min(max(0, value), hi)
        self['round_segs'] = val

    rpts: bpy.props.IntProperty(default=0)
    provider: bpy.props.StringProperty(default='')
    user_dim: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0])
    dim_x: bpy.props.FloatProperty(name='Size',
            description='profile dimensions', default=0,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM,
            update=prof_edit_dim_x_update)
    dim_y: bpy.props.FloatProperty(name='Size',
            description='profile dimensions', default=0,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM,
            update=prof_edit_dim_y_update)
    dim: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0])
    dim_xy: bpy.props.FloatProperty(default=1)
    update_dims: bpy.props.BoolProperty(default=False)
    axes_lock: bpy.props.BoolProperty(name='Lock',
            description='lock axes', default=False,
            update=prof_edit_axes_lock_update)
    ctl_axis: bpy.props.IntProperty(default=-1)
    # all profiles
    reverse: bpy.props.BoolProperty(name='Reverse',
            description='reverse vertex-order', default=False)
    idx: bpy.props.IntProperty(name='Offset',
            description='index offset', default=0,
            get=prof_idx_get, set=prof_idx_set)
    # user-profile
    closed: bpy.props.BoolProperty(name='Closed',
            description='closed or open profile', default=True)
    # ellipse
    bump: bpy.props.IntProperty(name='V-bumps',
            description='effect steps', default=1,
            get=prof_edit_step_get, set=prof_edit_step_set)
    bump_val: bpy.props.FloatProperty(name='Factor',
            description='bump value', default=0,
            min=-ModCnst.MAX_FAC, max=ModCnst.MAX_FAC)
    bump_exp: bpy.props.FloatProperty(name='V-exponent',
            description='interpolation exponent',
            default=2, min=ModCnst.MIN_EXP, max=ModCnst.MAX_EXP)
    # rectangle (rounded corners)
    round_segs: bpy.props.IntProperty(name='Segments',
            description='rounding segments', default=0,
            get=prof_edit_round_segs_get, set=prof_edit_round_segs_set)
    round_off: bpy.props.FloatProperty(name='Radius',
            description='rounding offset', default=0.5)

    def invoke(self, context, event):
        prof = context.scene.ptdblnpopm_props.prof
        # self updates
        pd = self.as_keywords(ignore=('dim_x', 'dim_y', 'dim_xy', 'dim',
                                    'ctl_axis', 'axes_lock', 'update_dims'))
        for key in pd.keys():
            setattr(self, key, getattr(prof, key))
        if self.provider == 'ellipse':
            self.dim = prof.ell_dim
        elif self.provider == 'rectangle':
            self.dim = prof.rct_dim
        else:
            self.dim = prof.u_dim
        self.axes_lock = False
        self.update_dims = False
        self.dim_x = self.dim[0]
        self.dim_y = self.dim[1]
        self.update_dims = True
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        prof = props.prof
        # property group updates
        pd = self.as_keywords(ignore=('rpts', 'provider', 'user_dim', 'dim_x',
                                    'dim_y', 'dim_xy', 'dim', 'ctl_axis',
                                    'axes_lock', 'update_dims'))
        for key in pd.keys():
            setattr(prof, key, getattr(self, key))
        if self.provider == 'ellipse':
            prof.ell_dim = self.dim
        elif self.provider == 'rectangle':
            prof.rct_dim = self.dim
        else:
            prof.u_dim = self.dim
        try:
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'prof_edit: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def draw(self, context):
        p_name = self.provider
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text='Lock Axes')
        row = sc.row()
        row.label(text='Size')
        row = sc.row()
        row.label(text='Index')
        row = sc.row()
        if p_name == 'rectangle':
            row.label(text='Rounded')
            row = sc.row()
            row.label(text='Vertex Order')
        elif p_name == 'ellipse':
            row.label(text='Bumps')
            row = sc.row()
            row.label(text='Vertex Order')
        else:
            row.label(text='Options')

        p_ud = [1,1,0]
        if p_name == 'custom':
            p_ud = [1 if i else 0 for i in self.user_dim]
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, 'axes_lock', toggle=True)
        row = sc.row(align=True)
        col = row.column(align=True)
        col.enabled = bool(p_ud[0]) and (self.ctl_axis < 1)
        col.prop(self, 'dim_x', text='')
        col = row.column(align=True)
        col.enabled = bool(p_ud[1]) and (self.ctl_axis in [-1, 1])
        col.prop(self, 'dim_y', text='')
        row = sc.row(align=True)
        row.prop(self, 'idx', text='')
        if p_name == 'rectangle':
            row = sc.row(align=True)
            row.enabled = self.rpts >= 8
            row.prop(self, 'round_segs', text='')
            row.prop(self, 'round_off', text='')
            row = sc.row(align=True)
        elif p_name == 'ellipse':
            row = sc.row(align=True)
            row.prop(self, 'bump', text='')
            row.prop(self, 'bump_val', text='')
            row.prop(self, 'bump_exp', text='')
            row = sc.row(align=True)
        else:
            row = sc.row(align=True)
            row.prop(self, 'closed', toggle=True)
        row.prop(self, 'reverse', toggle=True)


class PTDBLNPOPM_OT_profloc_add(bpy.types.Operator):

    bl_label = "Add"
    bl_idname = "ptdblnpopm.profloc_add"
    bl_description = "new edit"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        props = context.scene.ptdblnpopm_props
        try:
            item = props.proflox.add()
            item.active = False
            props.proflox_idx = len(props.proflox) - 1
        except Exception as my_err:
            print(f'profloc_add: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_profloc_copy(bpy.types.Operator):

    bl_label = "Copy"
    bl_idname = "ptdblnpopm.profloc_copy"
    bl_description = "copy edit"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def dct_to_pg(self, d, item):
        pd = d.pop('params')
        for key in pd.keys():
            setattr(item.params, key, pd[key])
        pd = d.pop('gprams')
        for key in pd.keys():
            setattr(item.gprams, key, pd[key])
        for key in d.keys():
            setattr(item, key, d[key])

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            source = props.proflox[props.proflox_idx]
            d = source.to_dct()
            item = props.proflox.add()
            # data transfer
            self.dct_to_pg(d, item)
            props.proflox_idx = len(props.proflox) - 1
        except Exception as my_err:
            print(f'profloc_copy: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_profloc_enable(bpy.types.Operator):

    bl_label = "Enable"
    bl_idname = "ptdblnpopm.profloc_enable"
    bl_description = "enable/disable edits"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    doall: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            if self.doall:
                boo = props.proflox_disabled
                for item in props.proflox:
                    item.active = boo
                props.proflox_disabled = not boo
            else:
                item = props.proflox[props.proflox_idx]
                item.active = not item.active
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'profloc_enable: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_profloc_remove(bpy.types.Operator):

    bl_label = "Remove"
    bl_idname = "ptdblnpopm.profloc_remove"
    bl_description = "remove edits"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    doall: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def invoke(self, context, event):
        props = context.scene.ptdblnpopm_props
        if props.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            if self.doall:
                props.proflox.clear()
                props.proflox_idx = -1
            else:
                idx = props.proflox_idx
                props.proflox.remove(idx)
                props.proflox_idx = min(
                    max(0, idx - 1), len(props.proflox) - 1)
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'profloc_remove: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_profloc_move(bpy.types.Operator):

    bl_label = "Move"
    bl_idname = "ptdblnpopm.profloc_move"
    bl_description = "Order edits"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    move_down: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        idx = props.proflox_idx
        try:
            if self.move_down:
                if idx < len(props.proflox) - 1:
                    props.proflox.move(idx, idx + 1)
                    props.proflox_idx += 1
            elif idx > 0:
                props.proflox.move(idx, idx - 1)
                props.proflox_idx -= 1
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'profloc_move: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_profloc_edit(bpy.types.Operator):

    bl_label = "Locations [Profile]"
    bl_idname = "ptdblnpopm.profloc_edit"
    bl_description = "profile locations"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def proflocs_idx_get(self):
        return self.get('idx', 0)

    def proflocs_idx_set(self, value):
        self['idx'] = value % self.rpts

    def proflocs_itm_get(self):
        return self.get('itm', 1)

    def proflocs_itm_set(self, value):
        self['itm'] = min(max(1, value), self.rpts)

    def proflocs_reps_get(self):
        return self.get('reps', 1)

    def proflocs_reps_set(self, value):
        self['reps'] = min(max(1, value), self.rpts)

    def proflocs_gap_get(self):
        return self.get('gap', 0)

    def proflocs_gap_set(self, value):
        self['gap'] = min(max(0, value), self.rpts)

    def proflocs_pidx_get(self):
        return self.get('pidx', 0)

    def proflocs_pidx_set(self, value):
        self['pidx'] = value % self.rings

    def proflocs_pitm_get(self):
        return self.get('pitm', 1)

    def proflocs_pitm_set(self, value):
        self['pitm'] = min(max(1, value), self.rings)

    def proflocs_preps_get(self):
        return self.get('preps', 1)

    def proflocs_preps_set(self, value):
        self['preps'] = min(max(1, value), self.rings)

    def proflocs_pgap_get(self):
        return self.get('pgap', 0)

    def proflocs_pgap_set(self, value):
        self['pgap'] = min(max(0, value), self.rings)

    rings: bpy.props.IntProperty(default=0)
    rpts: bpy.props.IntProperty(default=0)
    fac: bpy.props.FloatProperty(name='Distance', description='move factor',
            default=0, min=-ModCnst.MAX_FAC, max=ModCnst.MAX_FAC)
    axis: bpy.props.FloatVectorProperty(name='Axis', description='move axis',
            size=3, default=[1, 1, 0], min=-1, max=1)
    mir: bpy.props.BoolProperty(name='Mirror',
            description='interpolation mirror', default=False)
    lerp: bpy.props.BoolProperty(name='Lerp',
            description='move interpolation', default=True)
    f2: bpy.props.FloatProperty(name='Factor', description='enhance-fade',
            default=1, min=-2, max=2)
    ease: bpy.props.EnumProperty(name='Ease',
            description='interpolation type',
            items=( ('IN', 'in', 'ease in'),
                    ('OUT', 'out', 'ease out'),
                    ('IN-OUT', 'in-out', 'ease in and out') ),
            default='IN-OUT')
    exp: bpy.props.FloatProperty(name='Exponent',
            description='interpolation exponent', default=1,
            min=ModCnst.MIN_EXP, max=ModCnst.MAX_EXP)
    rev: bpy.props.BoolProperty(name='Back', description='reverse direction',
            default=False)
    idx: bpy.props.IntProperty(name='Offset', description='index offset',
            default=0, get=proflocs_idx_get, set=proflocs_idx_set)
    itm: bpy.props.IntProperty(name='Items', description='group items',
            default=1, get=proflocs_itm_get, set=proflocs_itm_set)
    reps: bpy.props.IntProperty(name='Repeats', description='repeats',
            default=1, get=proflocs_reps_get, set=proflocs_reps_set)
    gap: bpy.props.IntProperty(name='Gap', description='gap between repeats',
            default=0, get=proflocs_gap_get, set=proflocs_gap_set)

    pmir: bpy.props.BoolProperty(name='Mirror',
            description='interpolation mirror', default=False)
    plerp: bpy.props.BoolProperty(name='Lerp',
            description='path index interpolation', default=True)
    pf2: bpy.props.FloatProperty(name='Factor', description='enhance-fade',
            default=1, min=-2, max=2)
    pease: bpy.props.EnumProperty(name='Ease',
            description='interpolation type',
            items=( ('IN', 'in', 'ease in'),
                    ('OUT', 'out', 'ease out'),
                    ('IN-OUT', 'in-out', 'ease in and out') ),
            default='IN-OUT')
    pexp: bpy.props.FloatProperty(name='Exponent',
            description='interpolation exponent', default=1,
            min=ModCnst.MIN_EXP, max=ModCnst.MAX_EXP)
    prev: bpy.props.BoolProperty(name='Back', description='reverse direction',
            default=False)
    pidx: bpy.props.IntProperty(name='Offset', description='path index offset',
            default=0, get=proflocs_pidx_get, set=proflocs_pidx_set)
    pitm: bpy.props.IntProperty(name='Items', description='path group items',
            default=1, get=proflocs_pitm_get, set=proflocs_pitm_set)
    preps: bpy.props.IntProperty(name='Repeats', description='path repeats',
            default=1, get=proflocs_preps_get, set=proflocs_preps_set)
    pgap: bpy.props.IntProperty(name='Gap', description='gap between repeats',
            default=0, get=proflocs_pgap_get, set=proflocs_pgap_set)

    def copy_from_pg(self, item):
        pkeys = ('idx', 'itm', 'reps', 'gap', 'ease',
                 'exp', 'mir', 'lerp', 'f2', 'rev')
        params = item.params
        gprams = item.gprams
        for key in pkeys:
            setattr(self, key, getattr(params, key))
            setattr(self, f'p{key}', getattr(gprams, key))

    def copy_to_pg(self, item):
        pkeys = ('idx', 'itm', 'reps', 'gap', 'ease',
                 'exp', 'mir', 'lerp', 'f2', 'rev')
        params = item.params
        gprams = item.gprams
        for key in pkeys:
            setattr(params, key, getattr(self, key))
            setattr(gprams, key, getattr(self, f'p{key}'))

    def invoke(self, context, event):
        props = context.scene.ptdblnpopm_props
        item = props.proflox[props.proflox_idx]
        # self updates
        self.rings = props.path.rings
        self.rpts = props.prof.rpts
        self.fac = item.fac
        self.axis = item.axis
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        item = props.proflox[props.proflox_idx]
        # property group updates
        item.fac = self.fac
        item.axis = self.axis
        self.copy_to_pg(item)
        try:
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'profloc_edit: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        names = ['Items', 'Repeats', 'Interpolation', 'Options']
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, 'pidx', text='')
        row.prop(self, 'pitm', text='')
        row.prop(self, 'prev', toggle=True)
        row = sc.row(align=True)
        row.prop(self, 'preps', text='')
        row.prop(self, 'pf2', text='')
        row.prop(self, 'pgap', text='')
        row = sc.row(align=True)
        col = row.column(align=True)
        col.prop(self, 'plerp', toggle=True)
        col = row.column(align=True)
        col.enabled = self.plerp
        col.prop(self, 'pmir', toggle=True)
        row = sc.row(align=True)
        row.enabled = self.plerp
        row.prop(self, 'pease', text='')
        row.prop(self, 'pexp', text='')

        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        names = ['Points', 'Factor', 'Axis', 'Repeats', 'Interpolation',
                 'Options']
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, 'idx', text='')
        row.prop(self, 'itm', text='')
        row.prop(self, 'rev', toggle=True)
        row = sc.row(align=True)
        row.prop(self, 'fac', text='')
        row = sc.row(align=True)
        row.prop(self, 'axis', index=0, text='')
        row.prop(self, 'axis', index=1, text='')
        row = sc.row(align=True)
        row.prop(self, 'reps', text='')
        row.prop(self, 'f2', text='')
        row.prop(self, 'gap', text='')
        row = sc.row(align=True)
        col = row.column(align=True)
        col.prop(self, 'lerp', toggle=True)
        col = row.column(align=True)
        col.enabled = self.lerp
        col.prop(self, 'mir', toggle=True)
        row = sc.row(align=True)
        row.enabled = self.lerp
        row.prop(self, 'ease', text='')
        row.prop(self, 'exp', text='')


# ---- BLEND-PROFILE OPERATORS

class PTDBLNPOPM_OT_blp_update_preset(bpy.types.Operator):

    bl_label = "Update"
    bl_idname = "ptdblnpopm.blp_update_preset"
    bl_description = "blend-profile update"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            item = props.blpc[props.blpc_idx]
            props.callbacks = False
            item.user_ob = None
            item.upv.clear()
            props.callbacks = True
            # active state
            if (item.provider == 'rectangle') and item.active:
                item.active = (props.prof.rpts % 2 == 0)
                if not item.active:
                    print('blp_update_preset: odd-verts mismatch!')
            ModPop.scene_update(scene)
        except Exception as my_err:
            props.callbacks = True
            print(f'blp_update_preset: {my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_blp_update_user(bpy.types.Operator):

    bl_label = "User blend-profile setup"
    bl_idname = "ptdblnpopm.blp_update_user"
    bl_description = "Setup user blend-profile data"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        rpts = props.prof.rpts
        try:
            item = props.blpc[props.blpc_idx]
            run_update = item.active
            # user object validation
            props.callbacks = False
            validate_scene_object(scene, item.user_ob)
            props.callbacks = True
            ob = item.user_ob
            if not ob:
                check = (len(item.upv) == rpts)
                if not check:
                    print(f'blp_update_user: vert-count mismatch!')
                elif run_update:
                    # scene updates
                    ModPop.scene_update(scene)
                return {'FINISHED'}
            # get user verts [raises invalid-data Exception]
            verts = ModPop.user_mesh_verts(ob.data)
            if len(verts) != rpts:
                raise Exception('vert-count mismatch!')
            # replace user blnd-profile verts
            item.upv.clear()
            for v in verts:
                i = item.upv.add()
                i.vert = v
            # property group updates
            for i in range(2):
                v = round(ob.dimensions[i], 5)
                v = min(max(ModCnst.MIN_DIM, v), ModCnst.MAX_DIM)
                item.user_dim[i] = v
                item.u_dim[i] = v
            bb = ob.bound_box
            item.user_bbc = 0.125 * sum((Vector(b) for b in bb), Vector())
            if run_update:
                # scene updates
                ModPop.scene_update(scene)
        except Exception as my_err:
            props.callbacks = True
            print(f'blp_update_user: {my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_blp_add(bpy.types.Operator):

    bl_label = "Add"
    bl_idname = "ptdblnpopm.blp_add"
    bl_description = "new edit"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        props = context.scene.ptdblnpopm_props
        try:
            item = props.blpc.add()
            item.active = False
            props.blpc_idx = len(props.blpc) - 1
        except Exception as my_err:
            print(f'blp_add: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_blp_enable(bpy.types.Operator):

    bl_label = "Enable"
    bl_idname = "ptdblnpopm.blp_enable"
    bl_description = "enable/disable edits"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    doall: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        rpts = props.prof.rpts
        try:
            if self.doall:
                props.blpc_disabled = not props.blpc_disabled
                for item in props.blpc:
                    if props.blpc_disabled:
                        item.active = False
                    else:
                        if item.provider == 'ellipse':
                            item.active = True
                        elif item.provider == 'rectangle':
                            item.active = (rpts % 2 == 0)
                        else:
                            item.active = (len(item.upv) == rpts)
            else:
                item = props.blpc[props.blpc_idx]
                if item.active:
                    item.active = False
                else:
                    if item.provider == 'ellipse':
                        item.active = True
                    elif item.provider == 'rectangle':
                        item.active = (rpts % 2 == 0)
                        if not item.active:
                            raise Exception('odd-verts mismatch!')
                    else:
                        item.active = (len(item.upv) == rpts)
                        if not item.active:
                            raise Exception('vert-count mismatch!')
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'blp_enable: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_blp_remove(bpy.types.Operator):

    bl_label = "Remove"
    bl_idname = "ptdblnpopm.blp_remove"
    bl_description = "remove edits"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    doall: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def invoke(self, context, event):
        props = context.scene.ptdblnpopm_props
        if props.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            if self.doall:
                props.callbacks = False
                for blp in props.blpc:
                    blp.user_ob = None
                props.callbacks = True
                props.blpc.clear()
                props.blpc_idx = -1
            else:
                idx = props.blpc_idx
                props.callbacks = False
                props.blpc[idx].user_ob = None
                props.callbacks = True
                props.blpc.remove(idx)
                props.blpc_idx = min(max(0, idx - 1), len(props.blpc) - 1)
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            props.callbacks = True
            print(f'blp_remove: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_blp_move(bpy.types.Operator):

    bl_label = "Move"
    bl_idname = "ptdblnpopm.blp_move"
    bl_description = "Order edits"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    move_down: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        idx = props.blpc_idx
        try:
            if self.move_down:
                if idx < len(props.blpc) - 1:
                    props.blpc.move(idx, idx + 1)
                    props.blpc_idx += 1
            elif idx > 0:
                props.blpc.move(idx, idx - 1)
                props.blpc_idx -= 1
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'blp_move: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_blp_edit(bpy.types.Operator):

    bl_label = "Edit [Blend]"
    bl_idname = "ptdblnpopm.blp_edit"
    bl_description = "edit blend profile"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def blp_idx_off_get(self):
        return self.get('idx_off', 0)

    def blp_idx_off_set(self, value):
        self['idx_off'] = value % self.rpts

    def blp_bump_get(self):
        return self.get('bump', 1)

    def blp_bump_set(self, value):
        self['bump'] = min(max(1, value), int(self.rpts / 2))

    def blp_edit_dim_x_update(self, context):
        if self.update_dims:
            self.dim[0] = self.dim_x
        if self.ctl_axis == 0:
            self.dim_y = self.dim_x * self.dim_xy

    def blp_edit_dim_y_update(self, context):
        if self.update_dims:
            self.dim[1] = self.dim_y
        if self.ctl_axis == 1:
            self.dim_x = self.dim_y * self.dim_xy

    def blp_edit_axes_lock_update(self, context):
        self.ctl_axis = -1
        self.dim_xy = 1
        if not (self.update_dims and self.axes_lock):
            return None
        if self.dim_x:
            self.ctl_axis = 0
            x = self.dim_x
            self.dim_xy = 1 if x == 0 else self.dim_y / x
            return None
        if self.dim_y:
            self.ctl_axis = 1
            y = self.dim_y
            self.dim_xy = 1 if y == 0 else self.dim_x / y

    def blp_edit_round_segs_get(self):
        return self.get('round_segs', 0)

    def blp_edit_round_segs_set(self, value):
        if self.rpts < 8:
            val = 0
        else:
            hi = int(self.rpts / 4) - 1
            val = min(max(0, value), hi)
        self['round_segs'] = val

    # blending
    def blp_idx_get(self):
        return self.get('idx', 0)

    def blp_idx_set(self, value):
        self['idx'] = value % self.rings

    def blp_itm_get(self):
        return self.get('itm', 1)

    def blp_itm_set(self, value):
        self['itm'] = min(max(1, value), self.rings)

    def blp_reps_get(self):
        return self.get('reps', 1)

    def blp_reps_set(self, value):
        self['reps'] = min(max(1, value), self.rings)

    def blp_gap_get(self):
        return self.get('gap', 0)

    def blp_gap_set(self, value):
        self['gap'] = min(max(0, value), self.rings)

    # blp editing
    rings: bpy.props.IntProperty(default=0)
    rpts: bpy.props.IntProperty(default=0)
    provider: bpy.props.StringProperty(default='')
    user_dim: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0])
    dim_x: bpy.props.FloatProperty(name='Size',
            description='blend-profile dimensions', default=0,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM,
            update=blp_edit_dim_x_update)
    dim_y: bpy.props.FloatProperty(name='Size',
            description='blend-profile dimensions', default=0,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM,
            update=blp_edit_dim_y_update)
    dim: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0])
    dim_xy: bpy.props.FloatProperty(default=1)
    update_dims: bpy.props.BoolProperty(default=False)
    axes_lock: bpy.props.BoolProperty(name='Lock',
            description='lock axes', default=False,
            update=blp_edit_axes_lock_update)
    ctl_axis: bpy.props.IntProperty(default=-1)

    # all blends
    reverse: bpy.props.BoolProperty(name='Reverse',
            description='reverse vertex-order', default=False)
    idx_off: bpy.props.IntProperty(name='Offset',
            description='index offset', default=0,
            get=blp_idx_off_get, set=blp_idx_off_set)
    # ellipse
    bump: bpy.props.IntProperty(name='V-bumps',
            description='effect repeats', default=1,
            get=blp_bump_get, set=blp_bump_set)
    bump_val: bpy.props.FloatProperty(name='V-bump',
            description='effect value', default=0,
            min=-ModCnst.MAX_FAC, max=ModCnst.MAX_FAC)
    bump_exp: bpy.props.FloatProperty(name='V-exponent',
            description='interpolation exponent',
            default=2, min=ModCnst.MIN_EXP, max=ModCnst.MAX_EXP)
    # rectangle (rounded corners)
    round_segs: bpy.props.IntProperty(name='Segments',
            description='rounding segments', default=0,
            get=blp_edit_round_segs_get, set=blp_edit_round_segs_set)
    round_off: bpy.props.FloatProperty(name='Radius',
            description='rounding offset', default=0.5)

    # blending parameters
    idx: bpy.props.IntProperty(name='Offset', description='index offset',
            default=0, get=blp_idx_get, set=blp_idx_set)
    itm: bpy.props.IntProperty(name='Items', description='group items',
            default=1, get=blp_itm_get, set=blp_itm_set)
    reps: bpy.props.IntProperty(name='Repeats', description='repeats',
            default=1, get=blp_reps_get, set=blp_reps_set)
    gap: bpy.props.IntProperty(name='Gap', description='gap between repeats',
            default=0, get=blp_gap_get, set=blp_gap_set)
    ease: bpy.props.EnumProperty(name='Ease', description='interpolation type',
            items=( ('IN', 'in', 'ease in'),
                    ('OUT', 'out', 'ease out'),
                    ('IN-OUT', 'in-out', 'ease in and out') ),
            default='IN-OUT')
    exp: bpy.props.FloatProperty(name='Exponent',
            description='interpolation exponent', default=1,
            min=ModCnst.MIN_EXP, max=ModCnst.MAX_EXP)
    mir: bpy.props.BoolProperty(name='Mirror',
            description='interpolation mirror', default=False)
    lerp: bpy.props.BoolProperty(name='Lerp',
            description='blend interpolation', default=True)
    fac: bpy.props.FloatProperty(name='Factor', description='amount factor',
            default=1, min=0, max=1)
    f2: bpy.props.FloatProperty(name='Factor', description='enhance-fade',
            default=1, min=0, max=1)
    abs_dim: bpy.props.BoolProperty(name='Absolute Size',
            description='relative or absolute dimensions', default=True)
    rev: bpy.props.BoolProperty(name='Back', description='reverse direction',
            default=False)

    def copy_from_pg(self, d, item):
        pkeys = ('idx', 'itm', 'reps', 'gap', 'ease',
                 'exp', 'mir', 'lerp', 'f2', 'rev')
        params = item.params
        for key in d.keys():
            if key in pkeys:
                d[key] = getattr(params, key)
            else:
                d[key] = getattr(item, key)
            setattr(self, key, d[key])

    def copy_to_pg(self, d, item):
        pkeys = ('idx', 'itm', 'reps', 'gap', 'ease',
                 'exp', 'mir', 'lerp', 'f2', 'rev')
        params = item.params
        for key in d.keys():
            d[key] = getattr(self, key)
            if key in pkeys:
                setattr(params, key, d[key])
            else:
                setattr(item, key, d[key])

    @classmethod
    def poll(cls, context):
        props = context.scene.ptdblnpopm_props
        return bool(props.blpc) and props.blpc[props.blpc_idx].active

    def invoke(self, context, event):
        props = context.scene.ptdblnpopm_props
        item = props.blpc[props.blpc_idx]
        # self updates
        self.rings = props.path.rings
        self.rpts = props.prof.rpts
        d = self.as_keywords(ignore=('rings', 'rpts', 'dim_x', 'dim_y', 'dim',
                                    'dim_xy', 'ctl_axis', 'axes_lock',
                                    'update_dims'))
        self.copy_from_pg(d, item)
        if self.provider == 'ellipse':
            self.dim = item.ell_dim
        elif self.provider == 'rectangle':
            self.dim = item.rct_dim
        else:
            self.dim = item.u_dim
        self.axes_lock = False
        self.update_dims = False
        self.dim_x = self.dim[0]
        self.dim_y = self.dim[1]
        self.update_dims = True
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        item = props.blpc[props.blpc_idx]
        # property group updates
        d = self.as_keywords(ignore=('rings', 'rpts', 'provider', 'user_dim',
                                    'dim_x', 'dim_y', 'dim_xy', 'dim',
                                    'ctl_axis', 'axes_lock', 'update_dims'))
        self.copy_to_pg(d, item)
        if self.provider == 'ellipse':
            item.ell_dim = self.dim
        elif self.provider == 'rectangle':
            item.rct_dim = self.dim
        else:
            item.u_dim = self.dim
        try:
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'blp_edit: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def draw(self, context):
        p_name = self.provider
        layout = self.layout
        # profile setup
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text='Lock Axes')
        row = sc.row()
        row.label(text='Size')
        row = sc.row()
        row.label(text='Offset')
        if p_name == 'rectangle':
            row = sc.row()
            row.label(text='Rounded')
        elif p_name == 'ellipse':
            row = sc.row()
            row.label(text='Bumps')
        row = sc.row()
        row.label(text='Vertex Order')

        p_ud = [1,1,0]
        if p_name == 'custom':
            p_ud = [1 if i else 0 for i in self.user_dim]
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, 'axes_lock', toggle=True)
        row = sc.row(align=True)
        col = row.column(align=True)
        col.enabled = bool(p_ud[0]) and (self.ctl_axis < 1)
        col.prop(self, 'dim_x', text='')
        col = row.column(align=True)
        col.enabled = bool(p_ud[1]) and (self.ctl_axis in [-1, 1])
        col.prop(self, 'dim_y', text='')
        row = sc.row(align=True)
        row.prop(self, 'idx_off', text='')
        if self.provider == 'rectangle':
            row = sc.row(align=True)
            row.enabled = self.rpts >= 8
            row.prop(self, 'round_segs', text='')
            row.prop(self, 'round_off', text='')
        elif self.provider == 'ellipse':
            row = sc.row(align=True)
            row.prop(self, 'bump', text='')
            row.prop(self, 'bump_val', text='')
            row.prop(self, 'bump_exp', text='')
        row = sc.row(align=True)
        row.prop(self, 'reverse', toggle=True)

        # blend setup
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        names = ['Factor', 'Items', 'Repeats', 'Interpolation',
                 'Options']
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, 'fac', text='')
        row.prop(self, 'abs_dim', toggle=True)
        row = sc.row(align=True)
        row.prop(self, 'idx', text='')
        row.prop(self, 'itm', text='')
        row.prop(self, 'rev', toggle=True)
        row = sc.row(align=True)
        row.prop(self, 'reps', text='')
        row.prop(self, 'f2', text='')
        row.prop(self, 'gap', text='')
        row = sc.row(align=True)
        col = row.column(align=True)
        col.prop(self, 'lerp', toggle=True)
        col = row.column(align=True)
        col.enabled = self.lerp
        col.prop(self, 'mir', toggle=True)
        row = sc.row(align=True)
        row.enabled = self.lerp
        row.prop(self, 'ease', text='')
        row.prop(self, 'exp', text='')


# ---- NOISE OPERATOR

class PTDBLNPOPM_OT_pop_noise(bpy.types.Operator):

    bl_label = "Noise"
    bl_idname = "ptdblnpopm.pop_noise"
    bl_description = "pseudo-random noise distorion"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    p_noise: bpy.props.FloatProperty(name='Path Noise',
            description='strength', default=0, min=0, max=ModCnst.MAX_NOIZ)
    f_noise: bpy.props.FloatProperty(name='Detail Noise',
            description='strength', default=0, min=0, max=ModCnst.MAX_NOIZ)
    nseed: bpy.props.IntProperty(name='Seed',
             description='random seed', default=0, min=0)
    vfac: bpy.props.FloatVectorProperty(name='Factor',
            description='axis factor', size=3, default=[0, 0, 0], min=0, max=1)

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopm_props.noiz.active

    def invoke(self, context, event):
        noiz = context.scene.ptdblnpopm_props.noiz
        # self updates
        pd = self.as_keywords()
        for key in pd.keys():
            setattr(self, key, getattr(noiz, key))
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        noiz = props.noiz
        # property group updates
        pd = self.as_keywords()
        for key in pd.keys():
            setattr(noiz, key, getattr(self, key))
        try:
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'pop_noise: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        c = box.column(align=True)
        s = c.split(factor=0.3)
        sc = s.column(align=True)
        names = ['Strength', 'Seed', 'Factors']
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, 'p_noise', text='')
        row.prop(self, 'f_noise', text='')
        row = sc.row(align=True)
        row.prop(self, 'nseed', text='')
        row = sc.row(align=True)
        row.prop(self, 'vfac', text='')


# ---- FILE I/O OPERATORS

class PTDBLNPOPM_OT_write_setts(bpy.types.Operator, ExportHelper):

    bl_label = "Save Preset"
    bl_idname = "ptdblnpopm.write_setts"
    bl_description = "save settings to json file"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    filename_ext = ".json"

    def invoke(self, context, event):
        self.filepath = "pop_setts"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        props = context.scene.ptdblnpopm_props
        file = self.filepath
        path = os.path.dirname(file)
        os.makedirs(path, exist_ok=True)
        try:
            data = self.setts_to_json(props)
            with open(file, mode='w') as f:
                json.dump(data, f, indent=2)
        except Exception as my_err:
            print(f'write_setts: {my_err.args}')
            self.report({'WARNING'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def setts_to_json(self, pg):

        d = {}
        exclude = ['clean', 'user_ob', 'plox_idx', 'plox_disabled',
                   'proflox_idx', 'proflox_disabled', 'blpc_idx',
                   'blpc_disabled', 'trax', 'trax_idx', 'trax_disabled',
                   'callbacks', 'animorph', 'act_name', 'act_owner',
                   'pop_mesh']
        vecprops = [bpy.props.IntVectorProperty, bpy.props.FloatVectorProperty]
        for key in pg.__annotations__.keys():
            if key in exclude:
                continue
            prop_type = pg.__annotations__[key].function
            if prop_type == bpy.props.PointerProperty:
                d[key] = self.setts_to_json(getattr(pg, key))
            elif prop_type == bpy.props.CollectionProperty:
                d[key] = [self.setts_to_json(i) for i in getattr(pg, key)]
            elif prop_type in vecprops:
                d[key] = list(getattr(pg, key))
            else:
                d[key] = getattr(pg, key)
        return d


class PTDBLNPOPM_OT_read_setts(bpy.types.Operator, ImportHelper):

    bl_label = "Load Preset"
    bl_idname = "ptdblnpopm.read_setts"
    bl_description = "reset mesh - load settings from json file"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    filter_glob: bpy.props.StringProperty(
        default='*.json;*.txt', options={'HIDDEN'})

    def invoke(self, context, event):
        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        file = self.filepath
        if not os.path.isfile(file):
            print('invalid file path')
            self.report({'WARNING'}, 'invalid file path')
            return {'CANCELLED'}
        try:
            with open(file, mode='r') as f:
                data = json.load(f)
            props.callbacks = False
            # clear collections
            props.path.upv.clear()
            props.path.user_ob = None
            props.prof.upv.clear()
            props.prof.user_ob = None
            for item in props.blpc:
                item.upv.clear()
                item.user_ob = None
            clear_edit_collections(props)
            # update properties
            self.json_to_setts(data, props)
            props.callbacks = True
            props.animorph = False  # just in case
            # scene updates
            ob = props.pop_mesh
            ModPop.mesh_smooth_normals(ob, props.auto_smooth)
            ModPop.mesh_show_wire(ob, props.show_wire)
            ModPop.scene_update(scene, setup='all')
        except Exception as my_err:
            props.callbacks = True
            print(f'read_setts: {my_err.args}')
            self.report({'WARNING'}, 'invalid data')
            return {'CANCELLED'}
        return {'FINISHED'}

    def json_to_setts(self, d, pg):
        # *** callbacks must be disabled

        x_seg = ModCnst.MAX_SEGS + 1
        for key in d.keys():
            if key not in pg.__annotations__.keys():
                continue
            prop_type = pg.__annotations__[key].function
            if prop_type == bpy.props.PointerProperty:
                self.json_to_setts(d[key], getattr(pg, key))
            elif prop_type == bpy.props.CollectionProperty:
                if key == 'blpc':
                    for cob in d[key]:
                        el = pg.blpc.add()
                        self.json_to_setts(cob, el)
                    pg.blpc_idx = len(pg.blpc) - 1
                elif key == 'plox':
                    for cob in d[key]:
                        el = pg.plox.add()
                        self.json_to_setts(cob, el)
                    pg.plox_idx = len(pg.plox) - 1
                elif key == 'proflox':
                    for cob in d[key]:
                        el = pg.proflox.add()
                        self.json_to_setts(cob, el)
                    pg.proflox_idx = len(pg.proflox) - 1
                elif (key == 'upv') and len(d[key]) < x_seg:
                    for cob in d[key]:
                        el = pg.upv.add()
                        self.json_to_setts(cob, el)
            else:
                setattr(pg, key, d[key])


# ---- ANIMATION OPERATORS

class PTDBLNPOPM_OT_animorph_setup(bpy.types.Operator):

    bl_label = "Exit Animation Mode?"
    bl_idname = "ptdblnpopm.animorph_setup"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    exiting: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        aniout = getattr(properties, 'exiting')
        if aniout:
            return "remove all animation data"
        return "enter animation mode"

    def invoke(self, context, event):
        props = context.scene.ptdblnpopm_props
        if self.exiting and props.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        ob = props.pop_mesh
        try:
            if self.exiting:
                ModPop.anim_data_remove(ob)
                ModPop.anim_data_remove(ob.data)
                props.trax.clear()
                props.trax_idx = -1
                props.animorph = False
            else:
                if not ob.animation_data:
                    ob.animation_data_create()
                if not ob.data.animation_data:
                    ob.data.animation_data_create()
                props.animorph = True
            props.trax_disabled = False
            # scene updates
            ModPop.scene_update(scene)
        except Exception as my_err:
            print(f'animorph_setup: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_anicycmirend(bpy.types.Operator):

    bl_label = "Set Frame Range"
    bl_idname = "ptdblnpopm.anicycmirend"
    bl_description = "set animation frame range in the Timeline"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        try:
            start = props.ani_kf_start
            step = props.ani_kf_step
            loop = props.ani_kf_loop
            iters = props.ani_kf_iters
            end = self.end_frame(start, step, loop, iters)
            scene.frame_start = start
            scene.frame_end = end
        except Exception as my_err:
            print(f'anicycmirend: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def end_frame(self, start, step, loop, itr):
        # return end frame of mirror-loop
        start -= 1
        maxit = int(loop / 2)
        itr = maxit if itr > maxit else itr
        grp = int(loop / itr)
        if grp % 2 == 0:
            sub = grp * step if itr > grp and itr < maxit else 0
            return start + (loop - 1) * step - sub
        m = grp + 1
        f = grp - 1
        f += 1 if itr > m else 0
        sub = step if itr == maxit and loop % 2 == 0 else 0
        return start + f * itr * step - sub


class PTDBLNPOPM_OT_track_edit(bpy.types.Operator):

    bl_label = "Edit [Track]"
    bl_idname = "ptdblnpopm.track_edit"
    bl_description = "track settings"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def track_sa_beg_get(self):
        return self.get('sa_beg', 1)

    def track_sa_beg_set(self, value):
        self['sa_beg'] = min(max(self.ac_beg, value), self.ac_end - 1)

    def track_sa_end_get(self):
        return self.get('sa_end', 1)

    def track_sa_end_set(self, value):
        self['sa_end'] = min(max(self.sa_beg + 1, value), self.ac_end)

    def track_s_end_get(self):
        return self.get('s_end', 1)

    def track_s_end_set(self, value):
        self['s_end'] = max(self.s_beg + 1, value)

    def track_s_blin_get(self):
        return self.get('s_blendin', 0)

    def track_s_blin_set(self, value):
        frms = self.s_end - self.s_beg
        self['s_blendin'] = min(max(0, value), frms)

    def track_s_blout_get(self):
        return self.get('s_blendout', 0)

    def track_s_blout_set(self, value):
        frms = (self.s_end - self.s_beg) - self.s_blendin
        self['s_blendout'] = min(max(0, value), frms)

    def track_blauto_update(self, context):
        if self.s_blendauto:
            self.s_blendin = 0
            self.s_blendout = 0

    name: bpy.props.StringProperty(default='noname')
    ac_beg: bpy.props.IntProperty(default=1)
    ac_end: bpy.props.IntProperty(default=1)
    sa_beg: bpy.props.IntProperty(name='First',
            description='first frame from action to use in the strip',
            default=1, get=track_sa_beg_get, set=track_sa_beg_set)
    sa_end: bpy.props.IntProperty(name='Last',
            description='last frame from action to use in the strip',
            default=1, get=track_sa_end_get, set=track_sa_end_set)
    s_beg: bpy.props.IntProperty(name='First',
            description='strip first frame', default=1, min=1)
    s_end: bpy.props.IntProperty(name='Last',
            description='strip last frame',
            default=10, get=track_s_end_get, set=track_s_end_set)
    s_rep: bpy.props.FloatProperty(name='Repeat',
            description='number of times to repeat action range', default=1,
            min=0.1, max=10)
    s_bln: bpy.props.EnumProperty(name='Blend Type',
            description='method of combining strip with accumulated result',
            items=( ('REPLACE', 'replace', 'replace'),
                    ('COMBINE', 'combine', 'combine'),
                    ('ADD', 'add', 'add'),
                    ('SUBTRACT', 'subtract', 'subtract'),
                    ('MULTIPLY', 'multiply', 'multiply') ),
            default='REPLACE')
    s_blendin: bpy.props.IntProperty(name='Blend-In',
            description='strip blend-in frames', default=0,
            get=track_s_blin_get, set=track_s_blin_set)
    s_blendout: bpy.props.IntProperty(name='Blend-Out',
            description='strip blend-out frames', default=0,
            get=track_s_blout_get, set=track_s_blout_set)
    s_blendauto: bpy.props.BoolProperty(name='Auto Blend',
            description='use strip auto-blend', default=False,
            update=track_blauto_update)
    s_xpl: bpy.props.EnumProperty(name='Extrapolation',
            description='action to take for gaps past the strip extents',
            items=( ('NOTHING', 'nothing', 'nothing'),
                    ('HOLD', 'hold', 'hold first/last'),
                    ('HOLD_FORWARD', 'hold forward', 'hold last') ),
            default='HOLD')

    def invoke(self, context, event):
        props = context.scene.ptdblnpopm_props
        item = props.trax[props.trax_idx]
        # self updates
        pd = self.as_keywords()
        for key in pd.keys():
            setattr(self, key, getattr(item, key))
        return self.execute(context)

    def execute(self, context):
        props = context.scene.ptdblnpopm_props
        item = props.trax[props.trax_idx]
        # property group updates
        pd = self.as_keywords(ignore=('name', 'ac_beg', 'ac_end'))
        for key in pd.keys():
            setattr(item, key, getattr(self, key))
        try:
            ob = props.pop_mesh
            ref = ob.data if item.owner == 'mesh' else ob
            strip = ref.animation_data.nla_tracks[item.t_name].strips[0]
            # must assign repeat before frames, to update scale
            strip.repeat = self.s_rep
            strip.action_frame_start = self.sa_beg
            strip.action_frame_end = self.sa_end
            strip.frame_start = self.s_beg
            strip.frame_end = self.s_end
            strip.blend_type = self.s_bln
            # auto must be assigned before in/out, otherwise it
            # cancels out in/out values even if it is False
            strip.use_auto_blend = self.s_blendauto
            strip.blend_in = self.s_blendin
            strip.blend_out = self.s_blendout
            strip.extrapolation = self.s_xpl
            # display-property update
            item.s_sca = strip.scale
        except Exception as my_err:
            print(f'track_edit: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        c = box.column(align=True)
        s = c.split(factor=0.3)
        col = s.column(align=True)
        names = ['Name', 'Action', 'Strip', 'Repeats', 'Blend Type',
                 'Blend In/Out', '', 'Extrapolate']
        for n in names:
            row = col.row()
            row.label(text=n)
        col = s.column(align=True)
        row = col.row(align=True)
        row.label(text=self.name)
        row = col.row(align=True)
        row.prop(self, 'sa_beg', text='')
        row.prop(self, 'sa_end', text='')
        row = col.row(align=True)
        row.prop(self, 's_beg', text='')
        row.prop(self, 's_end', text='')
        row = col.row(align=True)
        row.prop(self, 's_rep', text='')
        row = col.row(align=True)
        row.prop(self, 's_bln', text='')
        row = col.row(align=True)
        row.prop(self, 's_blendauto', toggle=True)
        row = col.row(align=True)
        row.enabled = not self.s_blendauto
        row.prop(self, 's_blendin', text='')
        row.prop(self, 's_blendout', text='')
        row = col.row(align=True)
        row.prop(self, 's_xpl', text='')


class PTDBLNPOPM_OT_track_enable(bpy.types.Operator):

    bl_label = "Enable"
    bl_idname = "ptdblnpopm.track_enable"
    bl_description = "enable/disable tracks"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    doall: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def execute(self, context):
        props = context.scene.ptdblnpopm_props
        ob = props.pop_mesh
        try:
            if self.doall:
                boo_mute = not props.trax_disabled
                for track in ob.animation_data.nla_tracks:
                    track.mute = boo_mute
                for track in ob.data.animation_data.nla_tracks:
                    track.mute = boo_mute
                for item in props.trax:
                    item.active = not boo_mute
                props.trax_disabled = boo_mute
            else:
                item = props.trax[props.trax_idx]
                ref = ob.data if item.owner == 'mesh' else ob
                ref.animation_data.nla_tracks[item.t_name].mute = item.active
                item.active = not item.active
        except Exception as my_err:
            print(f'track_enable: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_track_remove(bpy.types.Operator):

    bl_label = "Remove"
    bl_idname = "ptdblnpopm.track_remove"
    bl_description = "remove tracks"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    doall: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    def invoke(self, context, event):
        props = context.scene.ptdblnpopm_props
        if props.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        props = context.scene.ptdblnpopm_props
        ob = props.pop_mesh
        try:
            if self.doall:
                # remove all tracks
                ModPop.nla_track_remove_all(ob)
                ModPop.nla_track_remove_all(ob.data)
                props.trax.clear()
                props.trax_idx = -1
            else:
                # remove selected track
                idx = props.trax_idx
                item = props.trax[idx]
                ref = ob.data if item.owner == 'mesh' else ob
                ModPop.nla_track_remove(ref, item.t_name)
                props.trax.remove(idx)
                props.trax_idx = min(max(0, idx - 1), len(props.trax) - 1)
        except Exception as my_err:
            print(f'track_remove: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_track_copy(bpy.types.Operator):

    bl_label = "Copy"
    bl_idname = "ptdblnpopm.track_copy"
    bl_description = "new track - copy selected"
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def dct_to_pg(self, d, pg):
        for key in d.keys():
            setattr(pg, key, d[key])

    def execute(self, context):
        props = context.scene.ptdblnpopm_props
        ob = props.pop_mesh
        try:
            source = props.trax[props.trax_idx]
            actest = bpy.data.actions.get(source.t_name)
            if not actest:
                raise Exception('null action reference!')
            action = actest.copy()
            name = action.name
            ref = ob.data if source.owner == 'mesh' else ob
            # update collection
            newtrk = props.trax.add()
            props.trax_idx = len(props.trax) - 1
            # data transfer
            d = source.to_dct()
            self.dct_to_pg(d, newtrk)
            newtrk.t_name = name
            # add new track/strip/action
            track = ref.animation_data.nla_tracks.new()
            track.name = name
            start = int(action.frame_range[0])
            strip = track.strips.new(name, start, action)
            strip.blend_type = newtrk.s_bln
            strip.use_auto_blend = newtrk.s_blendauto
            strip.blend_in = newtrk.s_blendin
            strip.blend_out = newtrk.s_blendout
            strip.extrapolation = newtrk.s_xpl
        except Exception as my_err:
            print(f'track_copy: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}


class PTDBLNPOPM_OT_ani_action(bpy.types.Operator):

    bl_label = "Add Animation Action"
    bl_idname = "ptdblnpopm.ani_action"
    bl_description = ("compile animation fcurves and assign to new "
                      "NLA Track - might take some time ;)")
    bl_options = {'REGISTER', 'INTERNAL', 'UNDO'}

    def execute(self, context):
        props = context.scene.ptdblnpopm_props
        ob = props.pop_mesh
        loop = props.ani_kf_loop
        object_act = (props.act_owner == 'object')
        if object_act:
            if ob.rotation_mode != 'QUATERNION':
                print(f'ani_action: object rotation mode is not QUATERNION!')
                self.report({'INFO'}, 'rotation mode')
                return {'CANCELLED'}
            # --- interpolation lists - obrot
            d = self.sys_rot_dict(props, loop)
            if not d['sys_rot']:
                print(f'ani_action: no animation values!')
                self.report({'INFO'}, 'no animation values')
                return {'CANCELLED'}
            sys_rot_flags = d['flags']
            sys_rot = d['srq']
            sys_rinc = d['srinc']
        else:
            if not self.act_loc_state(props):
                print(f'ani_action: no animation values!')
                self.report({'INFO'}, 'no animation values')
                return {'CANCELLED'}
            # --- interpolation lists
            # --- path
            path = props.path
            d = self.path_edit_dict(path, loop)
            path_ret = d['path_ret']
            if path_ret:
                path_dim = d['path_dim']
                path_fac = d['path_fac']
            # --- prof
            prof = props.prof
            d = self.prof_edit_dict(prof, loop)
            prof_ret = d['prof_ret']
            if prof_ret:
                prof_dim = d['prof_dim']
                prof_fac = d['prof_fac']
            # --- spinroll
            spro = props.spro
            if spro.ani_rot:
                a = spro.ani_rot_ang
                rot_angs = self.spinroll_list(spro, a, loop)
            # --- plox
            active_plox = []
            pl_ids = []
            pl_ams = []
            for item in props.plox:
                if item.active:
                    active_plox.append(item.to_dct())
                    pl_ids.append(self.coll_index_list(item.ani_idx,
                                                       item.params.idx, loop))
                    pl_ams.append(self.poploc_fac_list(item, loop))
            # --- blends
            active_blends = []
            bl_ids = []
            bl_ams = []
            for item in props.blpc:
                if item.active:
                    active_blends.append(item.to_dct())
                    bl_ids.append(self.coll_index_list(item.ani_idx,
                                                       item.params.idx, loop))
                    bl_ams.append(self.blnd_fac_list(item, loop))
            # --- proflox
            active_pflox = []
            pf_ids = []
            pf_pids = []
            pf_ams = []
            for item in props.proflox:
                if item.active:
                    active_pflox.append(item.to_dct())
                    pf_ids.append(self.coll_index_list(item.ani_idx,
                                                       item.params.idx, loop))
                    pf_pids.append(self.coll_index_list(item.ani_itm_idx,
                                                        item.gprams.idx, loop))
                    pf_ams.append(self.poploc_fac_list(item, loop))
            # --- noise
            noiz = props.noiz
            nse_seed = None if noiz.ani_seed else noiz.nseed
            nse_path = self.noise_list(noiz, noiz.ani_p_noise, noiz.p_noise,
                                       noiz.ani_p_noise_val, loop)
            nse_fine = self.noise_list(noiz, noiz.ani_f_noise, noiz.f_noise,
                                       noiz.ani_f_noise_val, loop)
            # --- animation setup
            # get new pop (path/profile without transforms)
            pop = ModPop.get_new_pop(props)
            # store original path/prof locations
            pop.save_state()
            # add spin
            if spro.active:
                pop.spin_rotate(spro.rot_ang, spro.spin_ang, spro.follow_limit)
        # compile animation lists
        if object_act:
            ksys = []
            for i in range(loop):
                if sys_rot_flags[i] > 0:
                    sys_rot @= sys_rinc
                ksys.append(sys_rot.copy())
        else:
            kloc = []
            for i in range(loop):
                if path_ret:
                    pop.update_path(path_dim[i], path_fac[i])
                else:
                    pop.reset_pathlocs()
                if prof_ret:
                    pop.update_profile(prof_dim[i], prof_fac[i])
                else:
                    pop.reset_proflocs()
                for dct, ids, ams in zip(active_plox, pl_ids, pl_ams):
                    dct['params']['idx'] = ids[i]
                    dct['fac'] = ams[i]
                    pop.path_locations(dct)
                for dct, ids, ams in zip(active_blends, bl_ids, bl_ams):
                    dct['params']['idx'] = ids[i]
                    dct['fac'] = ams[i]
                    pop.add_blend_profile(dct)
                for dct, ids, pids, ams in zip(active_pflox, pf_ids,
                                               pf_pids, pf_ams):
                    dct['params']['idx'] = ids[i]
                    dct['gprams']['idx'] = pids[i]
                    dct['fac'] = ams[i]
                    pop.prof_locations(dct)
                if spro.ani_rot:
                    pop.roll_angle(rot_angs[i])
                locs = self.get_poplocs(pop, props, nse_path[i], nse_fine[i],
                                        nse_seed)
                kloc.append(locs)
        # action info
        a_name = props.act_name
        k_beg = props.ani_kf_start
        k_stp = props.ani_kf_step
        k_lrp = int(props.ani_kf_type)
        fl = [k_beg + i * k_stp for i in range(loop)]
        try:
            # add uilist-track
            trk = props.trax.add()
            if object_act:
                # pop rotation : object action
                name = f'{ob.name}_{a_name}'
                action = bpy.data.actions.new(name)
                dp = 'rotation_quaternion'
                for di in range(4):
                    vl = [q[di] for q in ksys]
                    self.fc_create(action, dp, di, fl, vl, k_lrp)
                # add NLA track / specify owner
                self.nla_track_add(ob, action)
                trk.owner = 'object'
            else:
                # mesh coords : data action
                name = f'{ob.name}_data_{a_name}'
                action = bpy.data.actions.new(name)
                nvs = len(ob.data.vertices)
                for p in range(nvs):
                    dp = f'vertices[{p}].co'
                    for di in range(3):
                        vl = [kloc[k][p][di] for k in range(loop)]
                        self.fc_create(action, dp, di, fl, vl, k_lrp)
                # add NLA track / specify owner
                self.nla_track_add(ob.data, action)
                trk.owner = 'mesh'
            # update/select new uilist-track
            trk.name = a_name
            trk.t_name = action.name
            k_end = fl[-1]
            trk.ac_beg = k_beg
            trk.ac_end = k_end
            trk.sa_beg = k_beg
            trk.sa_end = k_end
            trk.s_beg = k_beg
            trk.s_end = k_end
            props.trax_idx = len(props.trax) - 1
        except Exception as my_err:
            print(f'ani_action: {my_err.args}')
            self.report({'INFO'}, f'{my_err.args}')
            return {'CANCELLED'}
        return {'FINISHED'}

    def act_loc_state(self, props):
        # mesh-data action flag
        path = props.path
        if (path.ani_dim or path.ani_fac):
            return True
        prof = props.prof
        if (prof.ani_dim or prof.ani_fac):
            return True
        for item in props.plox:
            if (item.ani_idx.active or item.ani_fac.active):
                return True
        for item in props.proflox:
            if (item.ani_idx.active or item.ani_itm_idx.active
                    or item.ani_fac.active):
                return True
        if props.spro.ani_rot:
            return True
        for item in props.blpc:
            if (item.ani_idx.active or item.ani_fac):
                return True
        noiz = props.noiz
        if (noiz.ani_p_noise or noiz.ani_f_noise):
            return True
        return False

    def sys_rot_dict(self, props, loop):
        # return object rotation, increment and in-out flags
        d = {'sys_rot': False}
        obrot = props.obrot
        if not obrot.ani_rot or (obrot.ani_rot_ang == 0):
            return d
        d['sys_rot'] = True
        axis = Vector(obrot.axis).normalized()
        d['srq'] = Quaternion(axis, obrot.rot_ang)
        d['srinc'] = Quaternion(axis, obrot.ani_rot_ang)
        f1 = obrot.ani_rot_beg
        flags = [0 if f1 > (i + 1) else 1 for i in range(loop)]
        f2 = obrot.ani_rot_end
        if f2 > f1 and f2 < loop:
            d = loop - f2
            flags[f2:] = [0] * d
        d['flags'] = flags
        return d

    def index_list(self, flag, base, inc, beg, stp, loop):
        # return index-offset list
        if not flag:
            return [base] * loop
        beg = loop if beg > loop else beg
        ids = [base] * beg
        if loop > beg:
            d = loop - beg
            base += inc
            ct = 0
            for i in range(d):
                ids.append(base)
                ct += 1
                if ct == stp:
                    base += inc
                    ct = 0
        return ids

    def coll_index_list(self, inst, idx, loop):
        # return blp/ploc/profloc index-offset list
        return self.index_list(inst.active, idx, inst.offset, inst.beg,
                               inst.stp, loop)

    def linear_list(self, dt, m, cnt):
        if not m:
            return [dt * i for i in range(cnt)]
        dt2 = 2 * dt
        return [dt2 * i if (dt * i) < 0.5 else 2 - dt2 * i for i in range(cnt)]

    def value_list(self, flag, v1, v2, mirror, itr, loop):
        # return value interpolation list
        if not flag or (v1 == v2):
            return [v1] * loop
        if mirror:
            maxit = int(loop / 2)
            itr = maxit if itr > maxit else itr
            grp = int(loop / itr)
            even_grp = (grp % 2 == 0)
            div = grp if even_grp else grp - 1
            lst = self.linear_list(1 / div, True, grp)
            if loop > grp:
                m = int(loop / div) + 1
                l2 = lst[1:] + [lst[0]] if even_grp else lst[1:]
                lst = [lst[0]] + l2 * m
            return [v1 + (v2 - v1) * lst[i] for i in range(loop)]
        lst = self.linear_list(1 / (loop - 1), False, loop)
        return [v1 + (v2 - v1) * i for i in lst]

    def path_edit_dict(self, path, loop):
        # return path dim/value lists
        d = {'path_ret': False}
        adim = path.ani_dim
        afac = path.ani_fac
        if not (adim or afac):
            return d
        d['path_ret'] = True
        mirr = path.ani_sty_mirror
        cycl = path.ani_sty_cycles
        path_fac = [0] * loop
        p_name = path.provider
        if p_name == 'line':
            path_dim = self.value_list(adim, path.lin_dim, path.ani_lin_dim,
                                       mirr, cycl, loop)
            path_fac = self.value_list(afac, path.lin_exp, path.ani_lin_exp,
                                       mirr, cycl, loop)
        elif p_name == 'spiral':
            path_dim = self.value_list(adim, path.spi_dim, path.ani_spi_dim,
                                       mirr, cycl, loop)
            path_fac = self.value_list(afac, path.spi_revs, path.ani_spi_revs,
                                       mirr, cycl, loop)
        else:
            if p_name == 'ellipse':
                p_erud = path.ell_dim
            elif p_name == 'rectangle':
                p_erud = path.rct_dim
            else:
                p_erud = path.u_dim
            p = []
            for i in range(3):
                p.append(self.value_list(adim, p_erud[i], path.ani_eru_dim[i],
                                         mirr, cycl, loop))
            path_dim = [[p[0][i], p[1][i], p[2][i]] for i in range(loop)]
            if p_name == 'ellipse':
                path_fac = self.value_list(afac, path.bump_val,
                                           path.ani_fac_val, mirr, cycl, loop)
        d['path_dim'] = path_dim
        d['path_fac'] = path_fac
        return d

    def prof_edit_dict(self, prof, loop):
        # return prof dim/value lists
        d = {'prof_ret': False}
        adim = prof.ani_dim
        afac = prof.ani_fac
        if not (adim or afac):
            return d
        d['prof_ret'] = True
        mirr = prof.ani_sty_mirror
        cycl = prof.ani_sty_cycles
        prof_fac = [0] * loop
        p_name = prof.provider
        if p_name == 'ellipse':
            p_erud = prof.ell_dim
        elif p_name == 'rectangle':
            p_erud = prof.rct_dim
        else:
            p_erud = prof.u_dim
        p = []
        for i in range(3):
            p.append(self.value_list(adim, p_erud[i], prof.ani_eru_dim[i],
                                     mirr, cycl, loop))
        prof_dim = [[p[0][i], p[1][i], p[2][i]] for i in range(loop)]
        if p_name == 'ellipse':
            prof_fac = self.value_list(afac, prof.bump_val, prof.ani_fac_val,
                                       mirr, cycl, loop)
        d['prof_dim'] = prof_dim
        d['prof_fac'] = prof_fac
        return d

    def poploc_fac_list(self, inst, loop):
        # return ploc/profloc factor list
        return self.value_list(inst.ani_fac.active, inst.fac,
                               inst.ani_fac.fac, inst.ani_fac.mirror,
                               inst.ani_fac.cycles, loop)

    def blnd_fac_list(self, item, loop):
        # return blend-profile factor list
        return self.value_list(item.ani_fac, item.fac,
                               item.ani_fac_val, item.ani_fac_mirror,
                               item.ani_fac_cycles, loop)

    def spinroll_list(self, spro, a, loop):
        # return roll-angles list
        f1 = spro.ani_rot_beg
        angs = [0 if f1 > (i + 1) else a for i in range(loop)]
        f2 = spro.ani_rot_end
        if f2 > f1 and f2 < loop:
            d = loop - f2
            angs[f2:] = [0] * d
        return angs

    def value_bln_list(self, v1, v2, f1, f2, loop):
        # return value interpolation list with blend-in/out option
        f1 = 0 if f1 < 2 else f1
        f2 = 0 if f2 < 2 else f2
        vals = []
        if f1 > 0:
            f1 = loop if f1 > loop else f1
            v = v2 - v1
            d = f1 - 1
            vals += [v1 + v * i / d for i in range(f1)]
        hold = loop - f1
        if hold > 0:
            f2 = hold if f2 > hold else f2
            if hold > f2:
                hold -= f2
                vals += [v2 for _ in range(hold)]
            if f2 > 0:
                v = v1 - v2
                vlst = [v2 + v * i / f2 for i in range(1, f2)]
                vals += vlst + [v1]
        return vals

    def noise_list(self, noiz, flag, v1, v2, loop):
        # return noise amplitude list
        if not noiz.active:
            return [0] * loop
        if not flag or (v1 == v2):
            return [v1] * loop
        if noiz.ani_seed:
            v = v2 if v2 != 0 else v1
            return [v] * loop
        f1 = noiz.ani_blin
        f2 = noiz.ani_blout
        return self.value_bln_list(v1, v2, f1, f2, loop)

    def get_poplocs(self, pop, props, nse_path, nse_fine, nse_seed):
        # path noise
        noiz = props.noiz
        if noiz.active:
            pop.noise_move(noiz.vfac, nse_path, nse_seed)
        locs = pop.get_locs()
        # (detail noise)
        if noiz.active:
            locs = pop.noise_locs(locs, noiz.vfac, nse_fine, nse_seed)
        return locs

    def fc_create(self, action, dp, di, fl, vl, ki):
        # new fcurve
        fc = action.fcurves.new(data_path=dp, index=di)
        items = len(fl)
        fc.keyframe_points.add(count=items)
        fc.keyframe_points.foreach_set('co', [i for fv in zip(fl, vl)
                                              for i in fv])
        fc.keyframe_points.foreach_set('interpolation', [ki] * items)
        fc.update()

    def nla_track_add(self, ob, action):
        # add nla track to object, action to new strip
        name = action.name
        track = ob.animation_data.nla_tracks.new()
        track.name = name
        start = int(action.frame_range[0])
        strip = track.strips.new(name, start, action)
        strip.blend_type = ModCnst.DEF_TRK_BLN
        strip.use_auto_blend = ModCnst.DEF_TRK_BLENDAUTO
        strip.blend_in = ModCnst.DEF_TRK_BLENDIN
        strip.blend_out = ModCnst.DEF_TRK_BLENDOUT
        strip.extrapolation = ModCnst.DEF_TRK_XPL


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------

classes = (
    PTDBLNPOPM_OT_update_default,
    PTDBLNPOPM_OT_new_mesh,
    PTDBLNPOPM_OT_pop_reset,
    PTDBLNPOPM_OT_update_ranges,
    PTDBLNPOPM_OT_update_preset,
    PTDBLNPOPM_OT_update_user,
    PTDBLNPOPM_OT_pop_rotate,
    PTDBLNPOPM_OT_display_options,
    PTDBLNPOPM_OT_path_edit,
    PTDBLNPOPM_OT_prof_edit,
    PTDBLNPOPM_OT_ploc_add,
    PTDBLNPOPM_OT_ploc_copy,
    PTDBLNPOPM_OT_ploc_enable,
    PTDBLNPOPM_OT_ploc_remove,
    PTDBLNPOPM_OT_ploc_move,
    PTDBLNPOPM_OT_ploc_edit,
    PTDBLNPOPM_OT_profloc_add,
    PTDBLNPOPM_OT_profloc_copy,
    PTDBLNPOPM_OT_profloc_enable,
    PTDBLNPOPM_OT_profloc_remove,
    PTDBLNPOPM_OT_profloc_move,
    PTDBLNPOPM_OT_profloc_edit,
    PTDBLNPOPM_OT_blp_update_preset,
    PTDBLNPOPM_OT_blp_update_user,
    PTDBLNPOPM_OT_blp_add,
    PTDBLNPOPM_OT_blp_enable,
    PTDBLNPOPM_OT_blp_remove,
    PTDBLNPOPM_OT_blp_move,
    PTDBLNPOPM_OT_blp_edit,
    PTDBLNPOPM_OT_spinroll,
    PTDBLNPOPM_OT_pop_noise,
    PTDBLNPOPM_OT_write_setts,
    PTDBLNPOPM_OT_read_setts,
    PTDBLNPOPM_OT_animorph_setup,
    PTDBLNPOPM_OT_anicycmirend,
    PTDBLNPOPM_OT_track_edit,
    PTDBLNPOPM_OT_track_enable,
    PTDBLNPOPM_OT_track_remove,
    PTDBLNPOPM_OT_track_copy,
    PTDBLNPOPM_OT_ani_action,
)


def register():

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)


def unregister():

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
