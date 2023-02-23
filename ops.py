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


def get_new_mesh(scene):

    name = "pop_mesh"
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    ob.rotation_mode = "QUATERNION"
    return ob


# ---- POP OPERATORS


class PTDBLNPOPM_OT_update_default(bpy.types.Operator):

    bl_label = "Update"
    bl_idname = "ptdblnpopm.update_default"
    bl_description = "pop update"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = context.scene.ptdblnpopm_pool
        pool.callbacks = False
        try:
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"update_default: {my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_pop_reset(bpy.types.Operator):

    bl_label = "Discard changes"
    bl_idname = "ptdblnpopm.pop_reset"
    bl_description = "new mesh - use default settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    newdef: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        nd = getattr(properties, "newdef")
        if nd:
            return "new mesh - use default settings"
        return "new mesh - use current settings"

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        validate_scene_object(context.scene, pool.pop_mesh)
        if bool(pool.pop_mesh) and pool.replace_mesh and pool.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        try:
            pool.trax.clear()
            pool.trax_idx = -1
            pool.animorph = False
            if bool(pool.pop_mesh) and pool.replace_mesh:
                ModPop.anim_data_remove(pool.pop_mesh)
                ModPop.anim_data_remove(pool.pop_mesh.data)
            else:
                pool.pop_mesh = get_new_mesh(scene)
            if self.newdef:
                pool.props_unset()
            ModPop.mesh_smooth_normals(pool.pop_mesh, pool.auto_smooth)
            ModPop.mesh_show_wire(pool.pop_mesh, pool.show_wire)
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"pop_reset: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_update_ranges(bpy.types.Operator):

    bl_label = "Default Update"
    bl_idname = "ptdblnpopm.update_ranges"
    bl_description = "pop update - ranges"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        try:
            ModPop.scene_update(scene, setup="range")
        except Exception as my_err:
            pool.callbacks = True
            print(f"update_ranges: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_update_preset(bpy.types.Operator):

    bl_label = "Update Preset"
    bl_idname = "ptdblnpopm.update_preset"
    bl_description = "pop setup - preset"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    caller: bpy.props.StringProperty(default="none", options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        try:
            if self.caller == "prof":
                for item in pool.blnd:
                    item.active = False
            ModPop.scene_update(scene, setup="all")
        except Exception as my_err:
            pool.callbacks = True
            print(f"update_preset: {my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_update_user(bpy.types.Operator):

    bl_label = "Update User"
    bl_idname = "ptdblnpopm.update_user"
    bl_description = "pop setup - user"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    caller: bpy.props.StringProperty(default="none", options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        if self.caller == "prof":
            ndims = 2
            pg = pool.prof
            for item in pool.blnd:
                item.active = False
            pg_edit = pg.profed
        else:
            ndims = 3
            pg = pool.path
            pg_edit = pg.pathed
        try:
            validate_scene_object(scene, pg.user_ob)
            ob = pg.user_ob
            if not ob:
                ModPop.scene_update(scene, setup="all")
                pool.callbacks = True
                return {"FINISHED"}
            verts = ModPop.user_mesh_verts(ob.data)
            pg_edit.upv.clear()
            for v in verts:
                i = pg_edit.upv.add()
                i.vert = v
            for i in range(ndims):
                v = round(ob.dimensions[i], 5)
                pg_edit.user_dim[i] = v
                pg_edit.u_dim[i] = v
            bb = ob.bound_box
            pg_edit.user_bbc = 0.125 * sum((Vector(b) for b in bb), Vector())
            pg_edit.user_name = ob.name
            pg.user_ob = None
            ModPop.scene_update(scene, setup="all")
        except Exception as my_err:
            pg.user_ob = None
            pg_edit.user_name = "none"
            pool.callbacks = True
            print(f"update_user: {my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_pop_rotate(bpy.types.Operator):

    bl_label = "Rotation [Object]"
    bl_idname = "ptdblnpopm.pop_rotate"
    bl_description = "object rotation"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    axis: bpy.props.FloatVectorProperty(
        name="Axis",
        description="rotation axis",
        size=3,
        default=(0, 0, 1),
        min=-1,
        max=1,
    )
    rot_ang: bpy.props.FloatProperty(
        name="Angle", description="rotation angle", default=0, subtype="ANGLE"
    )

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopm_pool.obrot.active

    def invoke(self, context, event):
        obrot = context.scene.ptdblnpopm_pool.obrot
        self.axis = obrot.axis
        self.rot_ang = obrot.rot_ang
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        obrot = pool.obrot
        obrot.axis = self.axis
        obrot.rot_ang = self.rot_ang
        try:
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"pop_rotate: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text="Angle")
        row = sc.row()
        row.label(text="Axis")
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "rot_ang", text="")
        row = sc.row(align=True)
        row.prop(self, "axis", text="")


class PTDBLNPOPM_OT_pop_noiz(bpy.types.Operator):

    bl_label = "Location Noise"
    bl_idname = "ptdblnpopm.pop_noiz"
    bl_description = "location noise"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    p_noiz: bpy.props.FloatProperty(
        name="Path", description="path noise", default=0, min=0
    )
    f_noiz: bpy.props.FloatProperty(
        name="Detail", description="detail noise", default=0, min=0
    )
    nseed: bpy.props.IntProperty(
        name="Seed", description="random seed", default=0, min=0
    )
    vfac: bpy.props.FloatVectorProperty(
        name="Axis", description="axis factor", size=3, default=(0, 0, 0), min=0, max=1
    )

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopm_pool.noiz.active

    def invoke(self, context, event):
        noiz = context.scene.ptdblnpopm_pool.noiz
        self.p_noiz = noiz.p_noiz
        self.f_noiz = noiz.f_noiz
        self.nseed = noiz.nseed
        self.vfac = noiz.vfac
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        noiz = pool.noiz
        noiz.p_noiz = self.p_noiz
        noiz.f_noiz = self.f_noiz
        noiz.nseed = self.nseed
        noiz.vfac = self.vfac
        try:
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"pop_noiz: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        c = box.column(align=True)
        s = c.split(factor=0.3)
        sc = s.column(align=True)
        names = ["Amplitude", "Seed", "Influence"]
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "p_noiz", text="")
        row.prop(self, "f_noiz", text="")
        row = sc.row(align=True)
        row.prop(self, "nseed", text="")
        row = sc.row(align=True)
        row.prop(self, "vfac", text="")


class PTDBLNPOPM_OT_display_options(bpy.types.Operator):

    bl_label = "Display"
    bl_idname = "ptdblnpopm.display_options"
    bl_description = "shading options"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    option: bpy.props.StringProperty(default="show_wire", options={"HIDDEN"})

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.callbacks = False
        try:
            ob = pool.pop_mesh
            if self.option == "shade_smooth":
                ModPop.mesh_smooth_shade(ob, pool.shade_smooth)
            elif self.option == "auto_smooth":
                ModPop.mesh_smooth_normals(ob, pool.auto_smooth)
            else:
                ModPop.mesh_show_wire(ob, pool.show_wire)
        except Exception as my_err:
            pool.callbacks = True
            print(f"display_options: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_discard_verts(bpy.types.Operator):

    bl_label = "Discard"
    bl_idname = "ptdblnpopm.discard_verts"
    bl_description = "discard unused vertices"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    caller: bpy.props.StringProperty(default="none", options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        try:
            if self.caller == "path" and pool.path.provider != "custom":
                pool.path.pathed.upv.clear()
                pool.path.pathed.user_name = "none"
            elif self.caller == "prof" and pool.prof.provider != "custom":
                pool.prof.profed.upv.clear()
                pool.prof.profed.user_name = "none"
            elif self.caller == "blnd":
                for item in pool.blnd:
                    if item.provider != "custom":
                        item.blnded.upv.clear()
                        item.blnded.user_name = "none"
        except Exception as my_err:
            pool.callbacks = True
            print(f"discard_verts: {my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


# ---- PATHLOC/PROFLOC COLLECTIONS OPERATORS


class PTDBLNPOPM_OT_citem_add(bpy.types.Operator):

    bl_label = "Add"
    bl_idname = "ptdblnpopm.citem_add"
    bl_description = "new edit"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.callbacks = False
        cname = self.cname
        iname = self.iname
        try:
            coll = getattr(pool, cname)
            item = coll.add()
            item.active = False
            if cname == "pathloc":
                item.params.params_npts_updates(pool.path.pathed.rings)
            else:
                item.params.params_npts_updates(pool.prof.profed.rpts)
                item.gprams.params_npts_updates(pool.path.pathed.rings)
            idx = len(coll) - 1
            setattr(pool, iname, idx)
        except Exception as my_err:
            pool.callbacks = True
            print(f"{cname}_add: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_citem_copy(bpy.types.Operator):

    bl_label = "Copy"
    bl_idname = "ptdblnpopm.citem_copy"
    bl_description = "copy edit"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})

    def dct_to_pg(self, d, item, cname):
        p = d.pop("params")
        for key in p.keys():
            setattr(item.params, key, p[key])
        if cname == "profloc":
            g = d.pop("gprams")
            for key in g.keys():
                setattr(item.gprams, key, g[key])
        for key in d.keys():
            setattr(item, key, d[key])

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.callbacks = False
        cname = self.cname
        iname = self.iname
        try:
            coll = getattr(pool, cname)
            idx = getattr(pool, iname)
            target = coll[idx]
            d = target.to_dct()
            item = coll.add()
            self.dct_to_pg(d, item, cname)
            idx = len(coll) - 1
            setattr(pool, iname, idx)
        except Exception as my_err:
            pool.callbacks = True
            print(f"{cname}_copy: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_citem_enable(bpy.types.Operator):

    bl_label = "Enable"
    bl_idname = "ptdblnpopm.citem_enable"
    bl_description = "enable/disable edits"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})
    flagall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        cname = self.cname
        iname = self.iname
        try:
            coll = getattr(pool, cname)
            if self.doall:
                for item in coll:
                    item.active = self.flagall
            else:
                idx = getattr(pool, iname)
                item = coll[idx]
                item.active = not item.active
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"{cname}_enable: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_citem_remove(bpy.types.Operator):

    bl_label = "Remove"
    bl_idname = "ptdblnpopm.citem_remove"
    bl_description = "remove edits"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        if pool.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        cname = self.cname
        iname = self.iname
        try:
            coll = getattr(pool, cname)
            if self.doall:
                coll.clear()
                setattr(pool, iname, -1)
            else:
                idx = getattr(pool, iname)
                coll.remove(idx)
                idx = min(max(0, idx - 1), len(coll) - 1)
                setattr(pool, iname, idx)
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"{cname}_remove: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_citem_move(bpy.types.Operator):

    bl_label = "Move"
    bl_idname = "ptdblnpopm.citem_move"
    bl_description = "Order edits"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    move_down: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        cname = self.cname
        iname = self.iname
        try:
            coll = getattr(pool, cname)
            idx = getattr(pool, iname)
            if self.move_down:
                if idx < len(coll) - 1:
                    cidx = idx + 1
                    coll.move(idx, cidx)
                    setattr(pool, iname, cidx)
            elif idx > 0:
                cidx = idx - 1
                coll.move(idx, cidx)
                setattr(pool, iname, cidx)
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"{cname}_move: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_spro(bpy.types.Operator):

    bl_label = "Spinroll [Path]"
    bl_idname = "ptdblnpopm.spro"
    bl_description = "path roll and spin rotations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    rings: bpy.props.IntProperty(default=0)
    rot_ang: bpy.props.FloatProperty(
        name="Roll", default=0, description="constant rotation angle", subtype="ANGLE"
    )
    spin_ang: bpy.props.FloatProperty(
        name="Spin",
        default=0,
        description="interpolated rotation angle",
        subtype="ANGLE",
    )
    follow_limit: bpy.props.BoolProperty(
        name="Follow Limit",
        description=(
            "seam-faceloop offset calculation method: enabled by default but may"
            " be changed if the path is closed and the profile is open"
        ),
        default=True,
    )
    seam_lock: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopm_pool.spro.active

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        self.rings = pool.path.pathed.rings
        self.seam_lock = pool.prof.profed.closed or not pool.path.pathed.closed
        spro = pool.spro
        self.rot_ang = spro.rot_ang
        self.spin_ang = spro.spin_ang
        self.follow_limit = self.seam_lock or spro.follow_limit
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        spro = pool.spro
        spro.rot_ang = self.rot_ang
        spro.spin_ang = self.spin_ang
        spro.follow_limit = self.follow_limit
        try:
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"spro: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text="Angle")
        row = sc.row()
        row.label(text="Seam Offset")
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "rot_ang", text="")
        row.prop(self, "spin_ang", text="")
        row = sc.row(align=True)
        row.enabled = not self.seam_lock
        row.prop(self, "follow_limit", toggle=True)


# ---- PROFILE-BLENDS COLLECTION OPERATORS


class PTDBLNPOPM_OT_blnd_update_preset(bpy.types.Operator):

    bl_label = "Update"
    bl_idname = "ptdblnpopm.blnd_update_preset"
    bl_description = "blend-profile update"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        rpts = pool.prof.profed.rpts
        try:
            item = pool.blnd[pool.blnd_idx]
            i_ed = item.blnded
            if item.provider == "rectangle":
                if rpts % 2 == 0:
                    i_ed.profed_rpts_updates(rpts)
                elif item.active:
                    item.active = False
                    raise Exception("odd-verts mismatch!")
            else:
                i_ed.profed_rpts_updates(rpts)
            if item.active:
                ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"blnd_update_preset: {my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_blnd_update_user(bpy.types.Operator):

    bl_label = "User blend-profile setup"
    bl_idname = "ptdblnpopm.blnd_update_user"
    bl_description = "Setup user blend-profile data"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        rpts = pool.prof.profed.rpts
        try:
            item = pool.blnd[pool.blnd_idx]
            i_ed = item.blnded
            validate_scene_object(scene, item.user_ob)
            ob = item.user_ob
            if not ob:
                if len(i_ed.upv) != rpts:
                    raise Exception("vert-count mismatch!")
                elif item.active:
                    ModPop.scene_update(scene)
                pool.callbacks = True
                return {"FINISHED"}
            verts = ModPop.user_mesh_verts(ob.data)
            if len(verts) != rpts:
                raise Exception("vert-count mismatch!")
            i_ed.upv.clear()
            for v in verts:
                i = i_ed.upv.add()
                i.vert = v
            for i in range(2):
                v = round(ob.dimensions[i], 5)
                i_ed.user_dim[i] = v
                i_ed.u_dim[i] = v
            bb = ob.bound_box
            i_ed.user_bbc = 0.125 * sum((Vector(b) for b in bb), Vector())
            i_ed.user_name = ob.name
            i_ed.profed_rpts_updates(rpts)
            item.user_ob = None
            if item.active:
                ModPop.scene_update(scene)
        except Exception as my_err:
            item.user_ob = None
            if len(i_ed.upv) != rpts:
                i_ed.upv.clear()
                i_ed.user_name = "none"
                item.active = False
            pool.callbacks = True
            print(f"blnd_update_user: {my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_blnd_add(bpy.types.Operator):

    bl_label = "Add"
    bl_idname = "ptdblnpopm.blnd_add"
    bl_description = "new edit"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.callbacks = False
        try:
            item = pool.blnd.add()
            item.active = False
            item.blnded.profed_rpts_updates(pool.prof.profed.rpts)
            item.params.params_npts_updates(pool.path.pathed.rings)
            pool.blnd_idx = len(pool.blnd) - 1
        except Exception as my_err:
            pool.callbacks = True
            print(f"blnd_add: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_blnd_enable(bpy.types.Operator):

    bl_label = "Enable"
    bl_idname = "ptdblnpopm.blnd_enable"
    bl_description = "enable/disable edits"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})
    flagall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        rpts = pool.prof.profed.rpts
        try:
            if self.doall:
                if self.flagall:
                    for item in pool.blnd:
                        if item.provider in ["line", "ellipse"]:
                            item.active = True
                        elif item.provider == "rectangle":
                            item.active = rpts % 2 == 0
                        else:
                            item.active = len(item.blnded.upv) == rpts
                else:
                    for item in pool.blnd:
                        item.active = False
            else:
                item = pool.blnd[pool.blnd_idx]
                if item.active:
                    item.active = False
                else:
                    if item.provider in ["line", "ellipse"]:
                        item.active = True
                    elif item.provider == "rectangle":
                        item.active = rpts % 2 == 0
                        if not item.active:
                            raise Exception("odd-verts mismatch!")
                    else:
                        item.active = len(item.blnded.upv) == rpts
                        if not item.active:
                            raise Exception("vert-count mismatch!")
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"blnd_enable: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_blnd_remove(bpy.types.Operator):

    bl_label = "Remove"
    bl_idname = "ptdblnpopm.blnd_remove"
    bl_description = "remove edits"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        if pool.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        try:
            if self.doall:
                pool.blnd.clear()
                pool.blnd_idx = -1
            else:
                idx = pool.blnd_idx
                pool.blnd.remove(idx)
                pool.blnd_idx = min(max(0, idx - 1), len(pool.blnd) - 1)
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"blnd_remove: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_blnd_move(bpy.types.Operator):

    bl_label = "Move"
    bl_idname = "ptdblnpopm.blnd_move"
    bl_description = "Order edits"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    move_down: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        idx = pool.blnd_idx
        try:
            if self.move_down:
                if idx < len(pool.blnd) - 1:
                    pool.blnd.move(idx, idx + 1)
                    pool.blnd_idx += 1
            elif idx > 0:
                pool.blnd.move(idx, idx - 1)
                pool.blnd_idx -= 1
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"blnd_move: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


# ---- FILE I/O OPERATORS


class PTDBLNPOPM_OT_write_setts(bpy.types.Operator, ExportHelper):

    bl_label = "Save Preset"
    bl_idname = "ptdblnpopm.write_setts"
    bl_description = "save current settings to .json file"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    filename_ext = ".json"

    def invoke(self, context, event):
        self.filepath = "popmesh_preset"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.callbacks = False
        try:
            fpath = self.filepath
            path = os.path.dirname(fpath)
            os.makedirs(path, exist_ok=True)
            data = self.setts_to_json(pool)
            with open(fpath, mode="w") as f:
                json.dump(data, f, indent=2)
        except Exception as my_err:
            pool.callbacks = True
            print(f"write_setts: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def setts_to_json(self, pg):
        d = {}
        exclude = [
            "clean",
            "user_ob",
            "pathloc_idx",
            "profloc_idx",
            "blnd_idx",
            "trax",
            "trax_idx",
            "callbacks",
            "animorph",
            "act_name",
            "act_owner",
            "pop_mesh",
            "replace_mesh",
            "show_warn",
        ]
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
    bl_description = "new mesh - load settings from .json file"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    filter_glob: bpy.props.StringProperty(default="*.json;*.txt", options={"HIDDEN"})

    def invoke(self, context, event):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        validate_scene_object(scene, pool.pop_mesh)
        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        try:
            fpath = self.filepath
            if not os.path.isfile(fpath):
                raise Exception("invalid file path")
            with open(fpath, mode="r") as f:
                data = json.load(f)
            pool.trax.clear()
            pool.trax_idx = -1
            pool.animorph = False
            replace_mesh = pool.replace_mesh
            pool.props_unset()
            self.json_to_setts(data, pool)
            pool.animorph = False
            if bool(pool.pop_mesh) and replace_mesh:
                ModPop.anim_data_remove(pool.pop_mesh)
                ModPop.anim_data_remove(pool.pop_mesh.data)
            else:
                pool.pop_mesh = get_new_mesh(scene)
            ModPop.mesh_smooth_normals(pool.pop_mesh, pool.auto_smooth)
            ModPop.mesh_show_wire(pool.pop_mesh, pool.show_wire)
            ModPop.scene_update(scene, setup="all")
        except Exception as my_err:
            pool.callbacks = True
            print(f"read_setts: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        layout = self.layout
        if bool(pool.pop_mesh) and pool.replace_mesh and pool.show_warn:
            row = layout.row(align=True)
            row.label(text="WARNING! This will discard all changes")

    def json_to_setts(self, d, pg):
        x_seg = ModCnst.MAX_SEGS + 1
        for key in d.keys():
            if key not in pg.__annotations__.keys():
                continue
            prop_type = pg.__annotations__[key].function
            if prop_type == bpy.props.PointerProperty:
                self.json_to_setts(d[key], getattr(pg, key))
            elif prop_type == bpy.props.CollectionProperty:
                sub_d = d[key]
                sub_pg = getattr(pg, key)
                if key == "upv":
                    if len(sub_d) < x_seg:
                        for k in sub_d:
                            el = sub_pg.add()
                            self.json_to_setts(k, el)
                else:
                    iname = f"{key}_idx"
                    for k in sub_d:
                        el = sub_pg.add()
                        self.json_to_setts(k, el)
                    setattr(pg, iname, len(sub_pg) - 1)
            else:
                setattr(pg, key, d[key])


# ---- ANIMATION OPERATORS


class PTDBLNPOPM_OT_animorph_setup(bpy.types.Operator):

    bl_label = "Exit Animation Mode?"
    bl_idname = "ptdblnpopm.animorph_setup"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    exiting: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        aniout = getattr(properties, "exiting")
        if aniout:
            return "remove all animation data"
        return "enter animation mode"

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        if self.exiting and pool.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        ob = pool.pop_mesh
        try:
            ModPop.anim_data_remove(ob)
            ModPop.anim_data_remove(ob.data)
            pool.trax.clear()
            pool.trax_idx = -1
            if self.exiting:
                pool.animorph = False
            else:
                ob.animation_data_create()
                ob.data.animation_data_create()
                pool.animorph = True
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"animorph_setup: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_anicycmirend(bpy.types.Operator):

    bl_label = "Set Frame Range"
    bl_idname = "ptdblnpopm.anicycmirend"
    bl_description = "set frame range in the Timeline"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        try:
            start = pool.ani_kf_start
            step = pool.ani_kf_step
            loop = pool.ani_kf_loop
            scene.frame_start = start
            scene.frame_end = (start - 1) + (loop - 1) * step
        except Exception as my_err:
            pool.callbacks = True
            print(f"anicycmirend: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_track_edit(bpy.types.Operator):

    bl_label = "Edit [Track]"
    bl_idname = "ptdblnpopm.track_edit"
    bl_description = "track settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def track_sa_beg_get(self):
        return self.get("sa_beg", 1)

    def track_sa_beg_set(self, value):
        self["sa_beg"] = min(max(self.ac_beg, value), self.ac_end - 1)

    def track_sa_end_get(self):
        return self.get("sa_end", 1)

    def track_sa_end_set(self, value):
        self["sa_end"] = min(max(self.sa_beg + 1, value), self.ac_end)

    def track_s_end_get(self):
        return self.get("s_end", 1)

    def track_s_end_set(self, value):
        self["s_end"] = max(self.s_beg + 1, value)

    def track_s_blin_get(self):
        return self.get("s_blendin", 0)

    def track_s_blin_set(self, value):
        frms = self.s_end - self.s_beg
        self["s_blendin"] = min(max(0, value), frms)

    def track_s_blout_get(self):
        return self.get("s_blendout", 0)

    def track_s_blout_set(self, value):
        frms = (self.s_end - self.s_beg) - self.s_blendin
        self["s_blendout"] = min(max(0, value), frms)

    def track_blauto_update(self, context):
        if self.s_blendauto:
            self.s_blendin = 0
            self.s_blendout = 0

    ac_beg: bpy.props.IntProperty(default=1)
    ac_end: bpy.props.IntProperty(default=1)
    sa_beg: bpy.props.IntProperty(
        name="First",
        description="first frame from action to use in the strip",
        default=1,
        get=track_sa_beg_get,
        set=track_sa_beg_set,
    )
    sa_end: bpy.props.IntProperty(
        name="Last",
        description="last frame from action to use in the strip",
        default=1,
        get=track_sa_end_get,
        set=track_sa_end_set,
    )
    s_beg: bpy.props.IntProperty(
        name="First", description="strip first frame", default=1, min=1
    )
    s_end: bpy.props.IntProperty(
        name="Last",
        description="strip last frame",
        default=10,
        get=track_s_end_get,
        set=track_s_end_set,
    )
    s_rep: bpy.props.FloatProperty(
        name="Repeat",
        description="number of times to repeat action range",
        default=1,
        min=0.1,
        max=10,
    )
    s_bln: bpy.props.EnumProperty(
        name="Blend Type",
        description="method of combining strip with accumulated result",
        items=(
            ("REPLACE", "replace", "replace"),
            ("COMBINE", "combine", "combine"),
            ("ADD", "add", "add"),
            ("SUBTRACT", "subtract", "subtract"),
            ("MULTIPLY", "multiply", "multiply"),
        ),
        default="REPLACE",
    )
    s_blendin: bpy.props.IntProperty(
        name="Blend-In",
        description="strip blend-in frames",
        default=0,
        get=track_s_blin_get,
        set=track_s_blin_set,
    )
    s_blendout: bpy.props.IntProperty(
        name="Blend-Out",
        description="strip blend-out frames",
        default=0,
        get=track_s_blout_get,
        set=track_s_blout_set,
    )
    s_blendauto: bpy.props.BoolProperty(
        name="Auto Blend",
        description="use strip auto-blend",
        default=False,
        update=track_blauto_update,
    )
    s_xpl: bpy.props.EnumProperty(
        name="Extrapolation",
        description="action to take for gaps past the strip extents",
        items=(
            ("NOTHING", "nothing", "nothing"),
            ("HOLD", "hold", "hold first/last"),
            ("HOLD_FORWARD", "hold forward", "hold last"),
        ),
        default="HOLD",
    )
    s_bak: bpy.props.BoolProperty(
        name="Reverse", description="play in reverse", default=False
    )

    def copy_from_pg(self, item):
        d = self.as_keywords()
        for key in d.keys():
            d[key] = getattr(item, key)
            setattr(self, key, d[key])

    def copy_to_pg(self, item):
        d = self.as_keywords(ignore=("ac_beg", "ac_end"))
        for key in d.keys():
            d[key] = getattr(self, key)
            setattr(item, key, d[key])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        item = pool.trax[pool.trax_idx]
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.callbacks = False
        item = pool.trax[pool.trax_idx]
        self.copy_to_pg(item)
        try:
            ob = pool.pop_mesh
            ref = ob.data if item.owner == "mesh" else ob
            strip = ref.animation_data.nla_tracks[item.t_name].strips[0]
            strip.repeat = self.s_rep
            strip.action_frame_start = self.sa_beg
            strip.action_frame_end = self.sa_end
            strip.frame_start = self.s_beg
            strip.frame_end = self.s_end
            strip.blend_type = self.s_bln
            strip.use_auto_blend = self.s_blendauto
            strip.blend_in = self.s_blendin
            strip.blend_out = self.s_blendout
            strip.extrapolation = self.s_xpl
            strip.use_reverse = self.s_bak
            item.s_sca = strip.scale
        except Exception as my_err:
            pool.callbacks = True
            print(f"track_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        c = box.column(align=True)
        s = c.split(factor=0.3)
        col = s.column(align=True)
        names = [
            "Action",
            "Strip",
            "Blend Type",
            "Blend In/Out",
            "Extrapolate",
            "Repeats",
            "Playback",
        ]
        for n in names:
            row = col.row()
            row.label(text=n)
        col = s.column(align=True)
        row = col.row(align=True)
        row.prop(self, "sa_beg", text="")
        row.prop(self, "sa_end", text="")
        row = col.row(align=True)
        row.prop(self, "s_beg", text="")
        row.prop(self, "s_end", text="")
        row = col.row(align=True)
        row.prop(self, "s_bln", text="")
        row.prop(self, "s_blendauto", toggle=True)
        row = col.row(align=True)
        row.enabled = not self.s_blendauto
        row.prop(self, "s_blendin", text="")
        row.prop(self, "s_blendout", text="")
        row = col.row(align=True)
        row.prop(self, "s_xpl", text="")
        row = col.row(align=True)
        row.prop(self, "s_rep", text="")
        row = col.row(align=True)
        row.prop(self, "s_bak", toggle=True)


class PTDBLNPOPM_OT_track_enable(bpy.types.Operator):

    bl_label = "Enable"
    bl_idname = "ptdblnpopm.track_enable"
    bl_description = "mute/unmute tracks"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})
    flagall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.callbacks = False
        ob = pool.pop_mesh
        try:
            if self.doall:
                boo_mute = not self.flagall
                for track in ob.animation_data.nla_tracks:
                    track.mute = boo_mute
                for track in ob.data.animation_data.nla_tracks:
                    track.mute = boo_mute
                for item in pool.trax:
                    item.active = not boo_mute
            else:
                item = pool.trax[pool.trax_idx]
                ref = ob.data if item.owner == "mesh" else ob
                ref.animation_data.nla_tracks[item.t_name].mute = item.active
                item.active = not item.active
        except Exception as my_err:
            pool.callbacks = True
            print(f"track_enable: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_track_remove(bpy.types.Operator):

    bl_label = "Remove"
    bl_idname = "ptdblnpopm.track_remove"
    bl_description = "remove tracks"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    doall: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        if pool.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.callbacks = False
        ob = pool.pop_mesh
        try:
            if self.doall:
                ModPop.nla_track_remove_all(ob)
                ModPop.nla_track_remove_all(ob.data)
                pool.trax.clear()
                pool.trax_idx = -1
            else:
                idx = pool.trax_idx
                item = pool.trax[idx]
                ref = ob.data if item.owner == "mesh" else ob
                ModPop.nla_track_remove(ref, item.t_name)
                pool.trax.remove(idx)
                pool.trax_idx = min(max(0, idx - 1), len(pool.trax) - 1)
        except Exception as my_err:
            pool.callbacks = True
            print(f"track_remove: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_track_copy(bpy.types.Operator):

    bl_label = "Copy"
    bl_idname = "ptdblnpopm.track_copy"
    bl_description = "new track - copy selected"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.callbacks = False
        ob = pool.pop_mesh
        try:
            target = pool.trax[pool.trax_idx]
            actest = bpy.data.actions.get(target.t_name)
            if not actest:
                raise Exception("null action reference!")
            action = actest.copy()
            name = action.name
            ref = ob.data if target.owner == "mesh" else ob
            d = target.to_dct()
            source = pool.trax.add()
            pool.trax_idx = len(pool.trax) - 1
            for key in d.keys():
                setattr(source, key, d[key])
            source.t_name = name
            track = ref.animation_data.nla_tracks.new()
            track.name = name
            track.mute = not source.active
            start = int(action.frame_range[0])
            strip = track.strips.new(name, start, action)
            strip.repeat = source.s_rep
            strip.action_frame_start = source.sa_beg
            strip.action_frame_end = source.sa_end
            strip.frame_start = source.s_beg
            strip.frame_end = source.s_end
            strip.blend_type = source.s_bln
            strip.use_auto_blend = source.s_blendauto
            strip.blend_in = source.s_blendin
            strip.blend_out = source.s_blendout
            strip.extrapolation = source.s_xpl
            strip.use_reverse = source.s_bak
        except Exception as my_err:
            pool.callbacks = True
            print(f"track_copy: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_ani_action(bpy.types.Operator):

    bl_label = "Add Animation Action"
    bl_idname = "ptdblnpopm.ani_action"
    bl_description = "new track: compile animation action / assign new NLA Track"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.callbacks = False
        ob = pool.pop_mesh
        loop = pool.ani_kf_loop
        object_act = pool.act_owner == "object"
        if object_act:
            if ob.rotation_mode != "QUATERNION":
                pool.callbacks = True
                print(f"ani_action: object rotation mode is not QUATERNION!")
                self.report({"INFO"}, "rotation mode")
                return {"CANCELLED"}
            obrot_d = self.obrot_dict(pool.obrot, loop)
            if not obrot_d["ani_rot"]:
                pool.callbacks = True
                print(f"ani_action: no animation values!")
                self.report({"INFO"}, "no animation values")
                return {"CANCELLED"}
        else:
            if not self.act_loc_state(pool):
                pool.callbacks = True
                print(f"ani_action: no animation values!")
                self.report({"INFO"}, "no animation values")
                return {"CANCELLED"}
            path = pool.path
            path_d = self.path_edit_dict(path, loop)
            prof = pool.prof
            prof_d = self.prof_edit_dict(prof, loop)
            spro = pool.spro
            if spro.ani_rot.active:
                spro_angs = self.spro_anglist(spro.ani_rot, loop)
            pathloc_d = {"dcts": [], "ids": [], "ams": []}
            active_pathloc = []
            pl_ids = []
            pl_ams = []
            for item in pool.pathloc:
                if item.active:
                    pathloc_d["dcts"].append(item.to_dct())
                    pathloc_d["ids"].append(
                        self.coll_index_list(item.ani_idx, item.params.idx, loop)
                    )
                    pathloc_d["ams"].append(self.poploc_fac_list(item, loop))
            blnd_d = {"dcts": [], "ids": [], "ams": []}
            for item in pool.blnd:
                if item.active:
                    blnd_d["dcts"].append(item.to_dct())
                    blnd_d["ids"].append(
                        self.coll_index_list(item.ani_idx, item.params.idx, loop)
                    )
                    blnd_d["ams"].append(self.blnd_fac_list(item, loop))
            profloc_d = {"dcts": [], "ids": [], "ams": [], "pids": []}
            for item in pool.profloc:
                if item.active:
                    profloc_d["dcts"].append(item.to_dct())
                    profloc_d["ids"].append(
                        self.coll_index_list(item.ani_idx, item.params.idx, loop)
                    )
                    profloc_d["pids"].append(
                        self.coll_index_list(item.ani_itm_idx, item.gprams.idx, loop)
                    )
                    profloc_d["ams"].append(self.poploc_fac_list(item, loop))
            noiz = pool.noiz
            noiz_d = {}
            noiz_d["seed"] = None if noiz.ani_seed else noiz.nseed
            noiz_d["path"] = self.noiz_list(
                noiz, noiz.ani_p_noiz, noiz.p_noiz, noiz.ani_p_noiz_val, loop
            )
            noiz_d["fine"] = self.noiz_list(
                noiz, noiz.ani_f_noiz, noiz.f_noiz, noiz.ani_f_noiz_val, loop
            )
            pop = ModPop.get_new_pop(pool)
            pop.save_state()
            if spro.active:
                pop.spin_rotate(spro.rot_ang, spro.spin_ang, spro.follow_limit)
        if object_act:
            ksys = []
            obrot_q = obrot_d["srq"]
            obrot_flags = obrot_d["flags"]
            obrot_srinc = obrot_d["srinc"]
            for i in range(loop):
                if obrot_flags[i] > 0:
                    obrot_q @= obrot_srinc
                ksys.append(obrot_q.copy())
        else:
            sindz = pool.rngs.sindz["lst"]
            sindz_on = pool.rngs.active
            nlocs = path.pathed.rings * prof.profed.rpts
            kloc = []
            for i in range(loop):
                if path_d["ret"]:
                    pop.update_path(path_d["dim"][i], path_d["fac"][i])
                else:
                    pop.reset_pathlocs()
                if prof_d["ret"]:
                    pop.update_profile(prof_d["dim"][i], prof_d["fac"][i])
                else:
                    pop.reset_proflocs()
                for dct, ids, ams in zip(
                    pathloc_d["dcts"], pathloc_d["ids"], pathloc_d["ams"]
                ):
                    dct["params"]["idx"] = ids[i]
                    dct["fac"] = ams[i]
                    pop.path_locations(dct)
                for dct, ids, ams in zip(blnd_d["dcts"], blnd_d["ids"], blnd_d["ams"]):
                    dct["params"]["idx"] = ids[i]
                    dct["fac"] = ams[i]
                    pop.add_blend_profile(dct)
                for dct, ids, pids, ams in zip(
                    profloc_d["dcts"],
                    profloc_d["ids"],
                    profloc_d["pids"],
                    profloc_d["ams"],
                ):
                    dct["params"]["idx"] = ids[i]
                    dct["gprams"]["idx"] = pids[i]
                    dct["fac"] = ams[i]
                    pop.prof_locations(dct)
                if spro.ani_rot.active:
                    pop.roll_angle(spro_angs[i])
                locs = self.get_poplocs(
                    pop, pool, noiz_d["path"][i], noiz_d["fine"][i], noiz_d["seed"]
                )
                if sindz_on:
                    locs = [locs[j] for j in range(nlocs) if j in sindz]
                kloc.append(locs)
        a_name = pool.act_name
        k_beg = pool.ani_kf_start
        k_stp = pool.ani_kf_step
        k_lrp = int(pool.ani_kf_type)
        fl = [k_beg + i * k_stp for i in range(loop)]
        try:
            trk = pool.trax.add()
            if object_act:
                name = f"{ob.name}_{a_name}"
                action = bpy.data.actions.new(name)
                dp = "rotation_quaternion"
                for di in range(4):
                    vl = [q[di] for q in ksys]
                    self.fc_create(action, dp, di, fl, vl, k_lrp)
                self.nla_track_add(ob, action)
                trk.owner = "object"
            else:
                name = f"{ob.name}_data_{a_name}"
                action = bpy.data.actions.new(name)
                nvs = len(ob.data.vertices)
                for p in range(nvs):
                    dp = f"vertices[{p}].co"
                    for di in range(3):
                        vl = [kloc[k][p][di] for k in range(loop)]
                        self.fc_create(action, dp, di, fl, vl, k_lrp)
                self.nla_track_add(ob.data, action)
                trk.owner = "mesh"
            trk.name = a_name
            trk.t_name = action.name
            k_end = fl[-1]
            trk.ac_beg = k_beg
            trk.ac_end = k_end
            trk.sa_beg = k_beg
            trk.sa_end = k_end
            trk.s_beg = k_beg
            trk.s_end = k_end
            pool.trax_idx = len(pool.trax) - 1
        except Exception as my_err:
            pool.callbacks = True
            print(f"ani_action: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def act_loc_state(self, pool):
        path = pool.path
        if path.ani_dim:
            return True
        if path.provider in ["spiral", "line", "ellipse"] and path.ani_fac:
            return True
        prof = pool.prof
        if prof.ani_dim:
            return True
        if prof.provider in ["line", "ellipse"] and prof.ani_fac:
            return True
        for item in pool.pathloc:
            if item.ani_idx.active or item.ani_fac.active:
                return True
        for item in pool.profloc:
            if item.ani_idx.active or item.ani_itm_idx.active or item.ani_fac.active:
                return True
        if pool.spro.ani_rot.active:
            return True
        for item in pool.blnd:
            if item.ani_idx.active or item.ani_fac:
                return True
        noiz = pool.noiz
        if noiz.ani_p_noiz or noiz.ani_f_noiz:
            return True
        return False

    def obrot_dict(self, obrot, loop):
        d = {"ani_rot": False}
        ani_rot = obrot.ani_rot
        if not ani_rot.active or (ani_rot.fac == 0):
            return d
        d["ani_rot"] = True
        axis = Vector(obrot.axis).normalized()
        d["srq"] = Quaternion(axis, obrot.rot_ang)
        d["srinc"] = Quaternion(axis, ani_rot.fac)
        f1 = ani_rot.beg
        flags = [0 if f1 > (i + 1) else 1 for i in range(loop)]
        f2 = ani_rot.end
        if f1 < f2 < loop:
            d = loop - f2
            flags[f2:] = [0] * d
        d["flags"] = flags
        return d

    def index_list(self, flag, base, inc, beg, stp, loop):
        if not flag:
            return [base] * loop
        beg = min(loop, beg)
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
        return self.index_list(inst.active, idx, inst.offset, inst.beg, inst.stp, loop)

    def linear_list(self, dt, m, cnt):
        if not m:
            return [dt * i for i in range(cnt)]
        dt2 = 2 * dt
        return [dt2 * i if (dt * i) < 0.5 else 2 - dt2 * i for i in range(cnt)]

    def value_list(self, flag, v1, v2, mirror, cycles, loop):
        if not flag or (v1 == v2):
            return [v1] * loop
        if mirror:
            cycles = min(int(loop / 2), cycles)
            grp = int(loop / cycles)
            odd_grp = grp % 2 != 0
            div = grp - 1 if (odd_grp or cycles == 1) else grp
            lst = self.linear_list(1 / div, True, grp)
            if loop > grp:
                m = int(loop / div) + 1
                l2 = lst[1:] if odd_grp else lst[1:] + lst[0:1]
                lst = lst[0:1] + l2 * m
            return [v1 + (v2 - v1) * lst[i] for i in range(loop)]
        lst = self.linear_list(1 / (loop - 1), False, loop)
        return [v1 + (v2 - v1) * i for i in lst]

    def path_edit_dict(self, path, loop):
        d = {"ret": False}
        adim = path.ani_dim
        afac = path.ani_fac
        if not (adim or afac):
            return d
        d["ret"] = True
        mirr = path.ani_mirror
        cycl = path.ani_cycles
        path_fac = [0] * loop
        p_name = path.provider
        if p_name == "spiral":
            path_dim = self.value_list(
                adim, path.pathed.spi_dim, path.ani_spi_dim, mirr, cycl, loop
            )
            path_fac = self.value_list(
                afac, path.pathed.spi_revs, path.ani_spi_revs, mirr, cycl, loop
            )
        else:
            if p_name == "line":
                p_erud = path.pathed.lin_dim
            elif p_name == "ellipse":
                p_erud = path.pathed.ell_dim
            elif p_name == "rectangle":
                p_erud = path.pathed.rct_dim
            else:
                p_erud = path.pathed.u_dim
            p = []
            for i in range(3):
                p.append(
                    self.value_list(
                        adim, p_erud[i], path.ani_eru_dim[i], mirr, cycl, loop
                    )
                )
            path_dim = [[p[0][i], p[1][i], p[2][i]] for i in range(loop)]
            if p_name == "line":
                path_fac = self.value_list(
                    afac, path.pathed.lin_exp, path.ani_lin_exp, mirr, cycl, loop
                )
            elif p_name == "ellipse":
                path_fac = self.value_list(
                    afac, path.pathed.bump_val, path.ani_fac_val, mirr, cycl, loop
                )
        d["dim"] = path_dim
        d["fac"] = path_fac
        return d

    def prof_edit_dict(self, prof, loop):
        d = {"ret": False}
        adim = prof.ani_dim
        afac = prof.ani_fac
        if not (adim or afac):
            return d
        d["ret"] = True
        mirr = prof.ani_mirror
        cycl = prof.ani_cycles
        prof_fac = [0] * loop
        p_name = prof.provider
        if p_name == "line":
            p_erud = prof.profed.lin_dim
        elif p_name == "ellipse":
            p_erud = prof.profed.ell_dim
        elif p_name == "rectangle":
            p_erud = prof.profed.rct_dim
        else:
            p_erud = prof.profed.u_dim
        p = []
        for i in range(2):
            p.append(
                self.value_list(adim, p_erud[i], prof.ani_eru_dim[i], mirr, cycl, loop)
            )
        prof_dim = [[p[0][i], p[1][i]] for i in range(loop)]
        if p_name == "line":
            prof_fac = self.value_list(
                afac, prof.profed.lin_exp, prof.ani_lin_exp, mirr, cycl, loop
            )
        elif p_name == "ellipse":
            prof_fac = self.value_list(
                afac, prof.profed.bump_val, prof.ani_fac_val, mirr, cycl, loop
            )
        d["dim"] = prof_dim
        d["fac"] = prof_fac
        return d

    def poploc_fac_list(self, inst, loop):
        return self.value_list(
            inst.ani_fac.active,
            inst.fac,
            inst.ani_fac.fac,
            inst.ani_fac.mirror,
            inst.ani_fac.cycles,
            loop,
        )

    def blnd_fac_list(self, item, loop):
        return self.value_list(
            item.ani_fac,
            item.fac,
            item.ani_fac_val,
            item.ani_fac_mirror,
            item.ani_fac_cycles,
            loop,
        )

    def spro_anglist(self, ani_rot, loop):
        a = ani_rot.fac
        f1 = ani_rot.beg
        angs = [0 if f1 > (i + 1) else a for i in range(loop)]
        f2 = ani_rot.end
        if f1 < f2 < loop:
            d = loop - f2
            angs[f2:] = [0] * d
        return angs

    def value_bln_list(self, v1, v2, f1, f2, loop):
        f1 = 0 if f1 < 2 else f1
        f2 = 0 if f2 < 2 else f2
        vals = []
        if f1 > 0:
            f1 = min(loop, f1)
            v = v2 - v1
            d = f1 - 1
            vals += [v1 + v * i / d for i in range(f1)]
        hold = loop - f1
        if hold > 0:
            f2 = min(hold, f2)
            if hold > f2:
                hold -= f2
                vals += [v2 for _ in range(hold)]
            if f2 > 0:
                v = v1 - v2
                vlst = [v2 + v * i / f2 for i in range(1, f2)]
                vals += vlst + [v1]
        return vals

    def noiz_list(self, noiz, flag, v1, v2, loop):
        if not noiz.active:
            return [0] * loop
        if not flag or (v1 == v2):
            return [v1] * loop
        if noiz.ani_seed:
            v = v2 if v2 else v1
            return [v] * loop
        f1 = noiz.ani_blin
        f2 = noiz.ani_blout
        return self.value_bln_list(v1, v2, f1, f2, loop)

    def get_poplocs(self, pop, pool, nse_path, nse_fine, nse_seed):
        noiz = pool.noiz
        if noiz.active:
            pop.noiz_move(noiz.vfac, nse_path, nse_seed)
        locs = pop.get_locs()
        if noiz.active:
            locs = pop.noiz_locs(locs, noiz.vfac, nse_fine, nse_seed)
        return locs

    def fc_create(self, action, dp, di, fl, vl, ki):
        fc = action.fcurves.new(data_path=dp, index=di)
        items = len(fl)
        fc.keyframe_points.add(count=items)
        fc.keyframe_points.foreach_set("co", [i for fv in zip(fl, vl) for i in fv])
        fc.keyframe_points.foreach_set("interpolation", [ki] * items)
        fc.update()

    def nla_track_add(self, ob, action):
        name = action.name
        track = ob.animation_data.nla_tracks.new()
        track.name = name
        start = int(action.frame_range[0])
        strip = track.strips.new(name, start, action)
        strip.blend_type = "REPLACE"
        strip.use_auto_blend = False
        strip.blend_in = 0
        strip.blend_out = 0
        strip.extrapolation = "HOLD"


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------


classes = (
    PTDBLNPOPM_OT_update_default,
    PTDBLNPOPM_OT_pop_reset,
    PTDBLNPOPM_OT_update_ranges,
    PTDBLNPOPM_OT_update_preset,
    PTDBLNPOPM_OT_update_user,
    PTDBLNPOPM_OT_pop_rotate,
    PTDBLNPOPM_OT_pop_noiz,
    PTDBLNPOPM_OT_display_options,
    PTDBLNPOPM_OT_discard_verts,
    PTDBLNPOPM_OT_citem_add,
    PTDBLNPOPM_OT_citem_copy,
    PTDBLNPOPM_OT_citem_enable,
    PTDBLNPOPM_OT_citem_remove,
    PTDBLNPOPM_OT_citem_move,
    PTDBLNPOPM_OT_blnd_update_preset,
    PTDBLNPOPM_OT_blnd_update_user,
    PTDBLNPOPM_OT_blnd_add,
    PTDBLNPOPM_OT_blnd_enable,
    PTDBLNPOPM_OT_blnd_remove,
    PTDBLNPOPM_OT_blnd_move,
    PTDBLNPOPM_OT_spro,
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
