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
# ----------------------------- IMPORTS ----------------------------------------


import bpy
import os
import json

from bpy_extras.io_utils import ImportHelper, ExportHelper

from . import mpopm as ModPOPM
from . import mfnop as ModFNOP


# ------------------------------------------------------------------------------
#
# ------------------------------- BMOPS ----------------------------------------


# ---- POP OPERATORS


class PTDBLNPOPM_OT_pop_simple_update(bpy.types.Operator):
    bl_label = "Simple Update"
    bl_idname = "ptdblnpopm.pop_simple_update"
    bl_description = "pop simple update"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        try:
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"pop_simple_update: {my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_facerange_react(bpy.types.Operator):
    bl_label = "Range Active Toggle"
    bl_idname = "ptdblnpopm.facerange_react"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    active: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        if getattr(properties, "active"):
            return "disable active range faces"
        return "enable active range faces"

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        try:
            pool.rngs.active = not self.active
            # scene updates
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"facerange_react: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_pop_reset(bpy.types.Operator):
    bl_label = "Update Settings"
    bl_idname = "ptdblnpopm.pop_reset"
    bl_description = "update mesh - load default settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    newdef: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        nd = getattr(properties, "newdef")
        if nd:
            return "update mesh - load default settings"
        return "update mesh - load current settings"

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        ModFNOP.validate_scene_object(context.scene, pool.pop_mesh)
        if bool(pool.pop_mesh) and pool.replace_mesh and pool.show_warn:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        try:
            trash = pool.trax_idx >= 0
            pool.trax.clear()
            pool.trax_idx = -1
            pool.animorph = False
            if pool.pop_mesh and pool.replace_mesh:
                me = pool.pop_mesh.data
                if me.animation_data:
                    me.animation_data_clear()
                if trash:
                    print("---- popmesh pop_reset: delete trash")
                    bpy.ops.outliner.orphans_purge(do_recursive=True)
            else:
                pool.pop_mesh = ModFNOP.get_new_mesh(scene)
            if self.newdef:
                pool.props_unset()
            pool.pop_mesh.data.use_auto_smooth = pool.auto_smooth
            pool.pop_mesh.show_wire = pool.show_wire
            ModPOPM.scene_update(scene, setup="all")
        except Exception as my_err:
            pool.update_ok = True
            print(f"pop_reset: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_setup_provider(bpy.types.Operator):
    bl_label = "Provider Update"
    bl_idname = "ptdblnpopm.setup_provider"
    bl_description = "pop provider setup"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    caller: bpy.props.StringProperty(default="path", options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        caller = self.caller
        if caller == "prof":
            ndims = 2
            pg = pool.prof
            for item in pool.blnd:
                item.active = False
            pg_edit = pg.profed
        else:
            ndims = 3
            pg = pool.path
            pg_edit = pg.pathed
        provider = pg.provider
        pg_edit.upv.clear()
        try:
            if provider != "custom":
                ModPOPM.scene_update(scene, setup=caller)
                pool.update_ok = True
                return {"FINISHED"}
            ModFNOP.validate_scene_object(scene, pg.user_ob)
            ob = pg.user_ob
            if not ob:
                raise Exception("invalid object!")
            verts = ModPOPM.user_mesh_verts(ob.data)
            for v in verts:
                i = pg_edit.upv.add()
                i.vert = v
            for i in range(ndims):
                v = round(ob.dimensions[i], 5)
                pg_edit.user_dim[i] = v
                pg_edit.cust_dim[i] = v
            pg.user_ob = None
            ModPOPM.scene_update(scene, setup=caller)
        except Exception as my_err:
            pg.clean = False
            pg.user_ob = None
            pool.update_ok = True
            print(f"{caller} provider setup: {my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_update_preset(bpy.types.Operator):
    bl_label = "Preset Update"
    bl_idname = "ptdblnpopm.update_preset"
    bl_description = "pop setup - preset resolution"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    caller: bpy.props.StringProperty(default="none", options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        caller = self.caller
        try:
            if caller == "prof":
                for item in pool.blnd:
                    item.active = False
            ModPOPM.scene_update(scene, setup=caller)
        except Exception as my_err:
            pool.update_ok = True
            print(f"update_preset: {my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_display_options(bpy.types.Operator):
    bl_label = "Display"
    bl_idname = "ptdblnpopm.display_options"
    bl_description = "shading options"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    option: bpy.props.StringProperty(default="show_wire", options={"HIDDEN"})

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.update_ok = False
        try:
            ob = pool.pop_mesh
            if self.option == "shade_smooth":
                me = ob.data
                smooth = [pool.shade_smooth] * len(me.polygons)
                me.polygons.foreach_set("use_smooth", smooth)
                me.update()
            elif self.option == "auto_smooth":
                ob.data.use_auto_smooth = pool.auto_smooth
            else:
                ob.show_wire = pool.show_wire
        except Exception as my_err:
            pool.update_ok = True
            print(f"display_options: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_pathrot_edit(bpy.types.Operator):
    bl_label = "Rotation [Path]"
    bl_idname = "ptdblnpopm.pathrot_edit"
    bl_description = "path rotation"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    axis: bpy.props.FloatVectorProperty(
        name="axis",
        description="rotation axis",
        size=3,
        default=(0, 0, 1),
        min=-1,
        max=1,
    )
    angle: bpy.props.FloatProperty(
        name="angle", description="rotation angle", default=0, subtype="ANGLE"
    )
    pivot: bpy.props.FloatVectorProperty(
        name="pivot", size=3, default=(0, 0, 0), description="rotation pivot"
    )
    piv_object: bpy.props.BoolProperty(
        name="path", default=False, description="use path center"
    )
    batt: bpy.props.BoolProperty(
        name="order", default=False, description="rotation sequence"
    )

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopm_pool.pathrot.active

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        pathrot = pool.pathrot
        self.axis = pathrot.axis
        self.angle = pathrot.angle
        self.pivot = pathrot.pivot
        self.piv_object = pathrot.piv_object
        self.batt = pathrot.batt
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        pathrot = pool.pathrot
        pathrot.axis = self.axis
        pathrot.angle = self.angle
        pathrot.pivot = self.pivot
        pathrot.piv_object = self.piv_object
        pathrot.batt = self.batt
        try:
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"pathrot_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        names = ("Axis", "Angle", "Order", "Pivot")
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "axis", text="")
        row = sc.row(align=True)
        row.prop(self, "angle", text="")
        row = sc.row(align=True)
        cap = "before orientation" if self.batt else "after orientation"
        row.prop(self, "batt", text=cap, toggle=True)
        row = sc.row(align=True)
        row.prop(self, "piv_object", text="use path", toggle=True)
        row = sc.row(align=True)
        row.enabled = not self.piv_object
        row.prop(self, "pivot", text="")


class PTDBLNPOPM_OT_profrot_edit(bpy.types.Operator):
    bl_label = "Rotation [Profile]"
    bl_idname = "ptdblnpopm.profrot_edit"
    bl_description = "profile twist and roll"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    roll: bpy.props.FloatProperty(
        name="roll", description="constant rotation angle", default=0, subtype="ANGLE"
    )
    twist: bpy.props.FloatProperty(
        name="twist",
        description="interpolated rotation angle",
        default=0,
        subtype="ANGLE",
    )
    follow_limit: bpy.props.BoolProperty(
        name="follow limit",
        description=(
            "faceloop seam offset calculation method: follow-limit is the default,"
            " it may be changed when the path is closed and the profile is open"
        ),
        default=True,
    )
    seam_lock: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopm_pool.profrot.active

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        self.seam_lock = pool.prof.profed.closed or not pool.path.pathed.closed
        profrot = pool.profrot
        self.roll = profrot.roll
        self.twist = profrot.twist
        self.follow_limit = self.seam_lock or profrot.follow_limit
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        profrot = pool.profrot
        profrot.roll = self.roll
        profrot.twist = self.twist
        profrot.follow_limit = self.follow_limit
        try:
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"profrot_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        names = ("Angle", "Seam")
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "twist", text="")
        row.prop(self, "roll", text="")
        row = sc.row(align=True)
        row.enabled = not self.seam_lock
        row.prop(self, "follow_limit", toggle=True)


class PTDBLNPOPM_OT_meshrot_edit(bpy.types.Operator):
    bl_label = "Rotation [Mesh]"
    bl_idname = "ptdblnpopm.meshrot_edit"
    bl_description = "mesh rotation"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    axis: bpy.props.FloatVectorProperty(
        name="axis",
        description="rotation axis",
        size=3,
        default=(0, 0, 1),
        min=-1,
        max=1,
    )
    angle: bpy.props.FloatProperty(
        name="angle", description="rotation angle", default=0, subtype="ANGLE"
    )
    pivot: bpy.props.FloatVectorProperty(
        name="pivot", size=3, default=(0, 0, 0), description="rotation pivot"
    )

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopm_pool.meshrot.active

    def invoke(self, context, event):
        meshrot = context.scene.ptdblnpopm_pool.meshrot
        self.axis = meshrot.axis
        self.angle = meshrot.angle
        self.pivot = meshrot.pivot
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        meshrot = pool.meshrot
        meshrot.axis = self.axis
        meshrot.angle = self.angle
        meshrot.pivot = self.pivot
        try:
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"meshrot_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        scn = s.column(align=True)
        scv = s.column(align=True)
        names = ("Axis", "Angle", "Pivot")
        vals = ("axis", "angle", "pivot")
        for n, v in zip(names, vals):
            row = scn.row()
            row.label(text=n)
            row = scv.row(align=True)
            row.prop(self, v, text="")


class PTDBLNPOPM_OT_pop_noiz(bpy.types.Operator):
    bl_label = "Noise [Mesh]"
    bl_idname = "ptdblnpopm.pop_noiz"
    bl_description = "noise distortion"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    ampli: bpy.props.FloatProperty(
        name="amplitude", description="noise amount", default=0, min=0
    )
    nseed: bpy.props.IntProperty(
        name="seed", description="random seed", default=0, min=0
    )
    vfac: bpy.props.FloatVectorProperty(
        name="axis", description="axis factor", size=3, default=(0, 0, 0), min=0, max=1
    )

    @classmethod
    def poll(cls, context):
        return context.scene.ptdblnpopm_pool.noiz.active

    def invoke(self, context, event):
        noiz = context.scene.ptdblnpopm_pool.noiz
        self.ampli = noiz.ampli
        self.nseed = noiz.nseed
        self.vfac = noiz.vfac
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        noiz = pool.noiz
        noiz.ampli = self.ampli
        noiz.nseed = self.nseed
        noiz.vfac = self.vfac
        try:
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"pop_noiz: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        c = box.column(align=True)
        s = c.split(factor=0.25)
        sc = s.column(align=True)
        names = ("Amplitude", "Seed", "Influence")
        for n in names:
            row = sc.row()
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "ampli", text="")
        row = sc.row(align=True)
        row.prop(self, "nseed", text="")
        row = sc.row(align=True)
        row.prop(self, "vfac", text="")


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
        pool.update_ok = False
        cname = self.cname
        iname = self.iname
        try:
            coll = getattr(pool, cname)
            item = coll.add()
            item.active = False
            item.nprams.npts = pool.path.pathed.npts
            if cname == "profloc":
                item.iprams.npts = pool.prof.profed.npts
            idx = len(coll) - 1
            setattr(pool, iname, idx)
        except Exception as my_err:
            pool.update_ok = True
            print(f"{cname}_add: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_citem_copy(bpy.types.Operator):
    bl_label = "Copy"
    bl_idname = "ptdblnpopm.citem_copy"
    bl_description = "new edit - copy from active"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})

    def dct_to_pg(self, d, item, cname):
        npar = d.pop("nprams")
        for key in npar.keys():
            setattr(item.nprams, key, npar[key])
        if cname == "profloc":
            ipar = d.pop("iprams")
            for key in ipar.keys():
                setattr(item.iprams, key, ipar[key])
        for key in d.keys():
            setattr(item, key, d[key])

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.update_ok = False
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
            pool.update_ok = True
            print(f"{cname}_copy: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
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
        pool.update_ok = False
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
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"{cname}_enable: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
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
        pool.update_ok = False
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
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"{cname}_remove: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_citem_move(bpy.types.Operator):
    bl_label = "Stack"
    bl_idname = "ptdblnpopm.citem_move"
    bl_description = "change stack order"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    cname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    iname: bpy.props.StringProperty(default="", options={"HIDDEN"})
    move_down: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
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
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"{cname}_move: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


# ---- BLEND-PROFILE COLLECTION OPERATORS


class PTDBLNPOPM_OT_setup_blnd_provider(bpy.types.Operator):
    bl_label = "Provider Update"
    bl_idname = "ptdblnpopm.setup_blnd_provider"
    bl_description = "blend provider setup"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        npts = pool.prof.profed.npts
        item = pool.blnd[pool.blnd_idx]
        i_ed = item.blnded
        i_ed.upv.clear()
        provider = item.provider
        try:
            if provider != "custom":
                if (provider == "polygon") and (npts < 6):
                    raise Exception("vertex count mismatch!")
                i_ed.npts = npts
                if item.active:
                    ModPOPM.scene_update(scene)
                pool.update_ok = True
                return {"FINISHED"}
            ModFNOP.validate_scene_object(scene, item.user_ob)
            ob = item.user_ob
            if not ob:
                raise Exception("invalid object!")
            verts = ModPOPM.user_mesh_verts(ob.data)
            if len(verts) != npts:
                raise Exception("vertex count mismatch!")
            for v in verts:
                i = i_ed.upv.add()
                i.vert = v
            for i in range(2):
                v = round(ob.dimensions[i], 5)
                i_ed.user_dim[i] = v
                i_ed.cust_dim[i] = v
            i_ed.npts = npts
            item.user_ob = None
            if item.active:
                ModPOPM.scene_update(scene)
        except Exception as my_err:
            item.user_ob = None
            item.active = False
            pool.update_ok = True
            print(f"blend provider setup: {my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_blnd_add(bpy.types.Operator):
    bl_label = "Add"
    bl_idname = "ptdblnpopm.blnd_add"
    bl_description = "new edit"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    clone: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    @classmethod
    def description(cls, context, properties):
        clone = getattr(properties, "clone")
        if clone:
            return "new edit - profile clone"
        return "new edit"

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.update_ok = False
        try:
            item = pool.blnd.add()
            item.active = False
            if self.clone:
                prof = pool.prof
                d = prof.profed.to_dct(exclude={"upv"})
                for key in d.keys():
                    setattr(item.blnded, key, d[key])
                item.provider = prof.provider
                if item.provider == "custom":
                    for v in prof.profed.upv:
                        i = item.blnded.upv.add()
                        i.vert = v.vert
            else:
                item.blnded.npts = pool.prof.profed.npts
            item.nprams.npts = pool.path.pathed.npts
            item.iprams.npts = pool.prof.profed.npts
            pool.blnd_idx = len(pool.blnd) - 1
        except Exception as my_err:
            pool.update_ok = True
            print(f"blnd_add: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
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
        pool.update_ok = False
        npts = pool.prof.profed.npts
        try:
            if self.doall:
                if self.flagall:
                    for item in pool.blnd:
                        if item.provider in {"line", "wave", "arc", "ellipse"}:
                            item.active = True
                        elif item.provider == "polygon":
                            item.active = npts > 5
                        else:
                            item.active = len(item.blnded.upv) == npts
                else:
                    for item in pool.blnd:
                        item.active = False
            else:
                item = pool.blnd[pool.blnd_idx]
                if item.active:
                    item.active = False
                else:
                    if item.provider in {"line", "wave", "arc", "ellipse"}:
                        item.active = True
                    elif item.provider == "polygon":
                        item.active = npts > 5
                        if not item.active:
                            raise Exception("vertex count mismatch!")
                    else:
                        item.active = len(item.blnded.upv) == npts
                        if not item.active:
                            raise Exception("vertex count mismatch!")
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"blnd_enable: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
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
        pool.update_ok = False
        try:
            if self.doall:
                pool.blnd.clear()
                pool.blnd_idx = -1
            else:
                idx = pool.blnd_idx
                pool.blnd.remove(idx)
                pool.blnd_idx = min(max(0, idx - 1), len(pool.blnd) - 1)
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"blnd_remove: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_blnd_move(bpy.types.Operator):
    bl_label = "Stack"
    bl_idname = "ptdblnpopm.blnd_move"
    bl_description = "change stack order"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    move_down: bpy.props.BoolProperty(default=False, options={"HIDDEN"})

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        idx = pool.blnd_idx
        try:
            if self.move_down:
                if idx < len(pool.blnd) - 1:
                    pool.blnd.move(idx, idx + 1)
                    pool.blnd_idx += 1
            elif idx > 0:
                pool.blnd.move(idx, idx - 1)
                pool.blnd_idx -= 1
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"blnd_move: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


# ---- FILE I/O OPERATORS


class PTDBLNPOPM_OT_write_setts(bpy.types.Operator, ExportHelper):
    bl_label = "Save Settings"
    bl_idname = "ptdblnpopm.write_setts"
    bl_description = "save current settings to .json file"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    filename_ext = ".json"

    def invoke(self, context, event):
        self.filepath = "popmesh_settings"
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.update_ok = False
        try:
            fpath = self.filepath
            path = os.path.dirname(fpath)
            os.makedirs(path, exist_ok=True)
            data = ModFNOP.setts_to_json(pool)
            with open(fpath, mode="w") as f:
                json.dump(data, f, indent=2)
        except Exception as my_err:
            pool.update_ok = True
            print(f"write_setts: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_read_setts(bpy.types.Operator, ImportHelper):
    bl_label = "Load Settings"
    bl_idname = "ptdblnpopm.read_setts"
    bl_description = "update mesh - load settings from .json file"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    filter_glob: bpy.props.StringProperty(default="*.json;*.txt", options={"HIDDEN"})

    def invoke(self, context, event):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        ModFNOP.validate_scene_object(scene, pool.pop_mesh)
        self.filepath = ""
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        try:
            fpath = self.filepath
            if not os.path.isfile(fpath):
                raise Exception("invalid file path")
            with open(fpath, mode="r") as f:
                data = json.load(f)
            trash = pool.trax_idx >= 0
            pool.trax.clear()
            pool.trax_idx = -1
            pool.animorph = False
            replace_mesh = pool.replace_mesh
            pool.props_unset()
            ModFNOP.json_to_setts(data, pool)
            if pool.pop_mesh and replace_mesh:
                me = pool.pop_mesh.data
                if me.animation_data:
                    me.animation_data_clear()
                if trash:
                    print("---- popmesh read_setts: delete trash")
                    bpy.ops.outliner.orphans_purge(do_recursive=True)
            else:
                pool.pop_mesh = ModFNOP.get_new_mesh(scene)
            pool.pop_mesh.data.use_auto_smooth = pool.auto_smooth
            pool.pop_mesh.show_wire = pool.show_wire
            ModPOPM.scene_update(scene, setup="all")
        except Exception as my_err:
            pool.update_ok = True
            print(f"read_setts: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        layout = self.layout
        if bool(pool.pop_mesh) and pool.replace_mesh and pool.show_warn:
            row = layout.row(align=True)
            row.label(text="WARNING! This will discard all changes")


# ---- ANIMATION OPERATORS


class PTDBLNPOPM_OT_animorph_setup(bpy.types.Operator):
    bl_label = "Exit Animation Mode"
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
        pool.update_ok = False
        try:
            me = pool.pop_mesh.data
            if me.animation_data:
                me.animation_data_clear()
            if pool.trax:
                print("---- popmesh animode: delete trash")
                bpy.ops.outliner.orphans_purge(do_recursive=True)
            pool.trax.clear()
            pool.trax_idx = -1
            if self.exiting:
                pool.animorph = False
            else:
                me.animation_data_create()
                pool.animorph = True
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"animorph_setup: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_anicycmirend(bpy.types.Operator):
    bl_label = "Set Frame Range"
    bl_idname = "ptdblnpopm.anicycmirend"
    bl_description = "set frame range in the Timeline"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        try:
            start = pool.ani_kf_start
            step = pool.ani_kf_step
            loop = pool.ani_kf_loop
            scene.frame_start = start
            scene.frame_end = (start - 1) + (loop - 1) * step
        except Exception as my_err:
            pool.update_ok = True
            print(f"anicycmirend: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_anicalc(bpy.types.Operator):
    bl_label = "Anicalc"
    bl_idname = "ptdblnpopm.anicalc"
    bl_description = "animation calculations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        scene = context.scene
        clc = scene.ptdblnpopm_pool.anicalc
        caller = clc.calc_type
        try:
            if caller == "loop":
                val = clc.items * clc.step // clc.offset + clc.start
                clc.info = str(val)
            elif caller == "offsets":
                offsets = sorted(ModFNOP.anicalc_factors(clc.items))[:-1]
                clc.info = ", ".join(str(i) for i in offsets)
            else:
                loop = clc.loop
                if not loop % 2:
                    self.report({"INFO"}, "loop should be odd, positive integer!")
                hlp = loop // 2
                cycles = sorted(ModFNOP.anicalc_factors(hlp))
                clc.info = ", ".join(str(i) for i in cycles)
        except Exception as my_err:
            clc.info = ""
            print(f"anicalc: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        return {"FINISHED"}


# ---- NLA-TRACK COLLECTION OPERATORS


class PTDBLNPOPM_OT_track_edit(bpy.types.Operator):
    bl_label = "Edit [Track]"
    bl_idname = "ptdblnpopm.track_edit"
    bl_description = "track settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def track_update(self, context):
        if self.update_pause:
            return None
        fval = (self.sa_end - self.sa_beg) * self.s_sca * self.s_rep
        self.s_end = self.s_beg + int(fval)
        if not self.s_blendauto:
            self.s_blendin = self.s_blendin

    def track_sa_beg_get(self):
        return self.get("sa_beg", 1)

    def track_sa_beg_set(self, value):
        val = min(max(self.ac_beg, value), self.ac_end - 1)
        if not self.update_pause and (val >= self.sa_end):
            val = self.sa_end - 1
        self["sa_beg"] = val

    def track_sa_end_get(self):
        return self.get("sa_end", 2)

    def track_sa_end_set(self, value):
        val = min(max(self.ac_beg + 1, value), self.ac_end)
        if not self.update_pause and (val <= self.sa_beg):
            val = self.sa_beg + 1
        self["sa_end"] = val

    def track_s_blin_get(self):
        return self.get("s_blendin", 0)

    def track_s_blin_set(self, value):
        frms = self.s_end - self.s_beg
        self["s_blendin"] = min(max(0, value), frms)

    def track_s_blin_update(self, context):
        self.s_blendout = self.get("s_blendout", 0)

    def track_s_blout_get(self):
        return self.get("s_blendout", 0)

    def track_s_blout_set(self, value):
        frms = (self.s_end - self.s_beg) - self.s_blendin
        self["s_blendout"] = min(max(0, value), frms)

    def track_blauto_update(self, context):
        if self.s_blendauto:
            self.s_blendin = 0
            self.s_blendout = 0

    update_pause: bpy.props.BoolProperty(default=True)
    ac_beg: bpy.props.IntProperty(default=1)
    ac_end: bpy.props.IntProperty(default=1)
    sa_beg: bpy.props.IntProperty(
        name="first",
        description="first frame from action to use",
        default=1,
        get=track_sa_beg_get,
        set=track_sa_beg_set,
        update=track_update,
    )
    sa_end: bpy.props.IntProperty(
        name="last",
        description="last frame from action to use",
        default=2,
        get=track_sa_end_get,
        set=track_sa_end_set,
        update=track_update,
    )
    s_beg: bpy.props.IntProperty(
        name="start frame",
        description="start frame number",
        default=1,
        min=1,
        update=track_update,
    )
    s_end: bpy.props.IntProperty(default=2)
    s_sca: bpy.props.FloatProperty(
        name="scale",
        description="scaling factor",
        default=1,
        min=0.001,
        max=100,
        update=track_update,
    )
    s_rep: bpy.props.FloatProperty(
        name="repeat",
        description="number of times to repeat selected range",
        default=1,
        min=1,
        max=100,
        update=track_update,
    )
    s_bln: bpy.props.EnumProperty(
        name="blend type",
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
        name="blend-in",
        description="blend-in frames",
        default=0,
        get=track_s_blin_get,
        set=track_s_blin_set,
        update=track_s_blin_update,
    )
    s_blendout: bpy.props.IntProperty(
        name="blend-out",
        description="blend-out frames",
        default=0,
        get=track_s_blout_get,
        set=track_s_blout_set,
    )
    s_blendauto: bpy.props.BoolProperty(
        name="auto blend",
        description="use auto-blend",
        default=False,
        update=track_blauto_update,
    )
    s_xpl: bpy.props.EnumProperty(
        name="extrapolation",
        description="extrapolate: action to take for gaps past the strip extents",
        items=(
            ("NOTHING", "nothing", "nothing"),
            ("HOLD", "hold", "hold"),
            ("HOLD_FORWARD", "hold forward", "hold forward"),
        ),
        default="HOLD",
    )
    s_bak: bpy.props.BoolProperty(
        name="reverse", description="play in reverse", default=False
    )

    def copy_from_pg(self, item):
        d = self.as_keywords(ignore=("update_pause",))
        for key in d.keys():
            d[key] = getattr(item, key)
            setattr(self, key, d[key])

    def copy_to_pg(self, item):
        d = self.as_keywords(ignore=("update_pause", "ac_beg", "ac_end"))
        for key in d.keys():
            d[key] = getattr(self, key)
            setattr(item, key, d[key])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        item = pool.trax[pool.trax_idx]
        self.update_pause = True
        self.copy_from_pg(item)
        self.update_pause = False
        self.track_update(context)
        return self.execute(context)

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.update_ok = False
        item = pool.trax[pool.trax_idx]
        self.copy_to_pg(item)
        try:
            ob = pool.pop_mesh
            strip = ob.data.animation_data.nla_tracks[item.t_name].strips[0]
            strip.scale = self.s_sca
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
        except Exception as my_err:
            pool.update_ok = True
            print(f"track_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        c = box.column(align=True)
        s = c.split(factor=0.3)
        col = s.column(align=True)
        names = (
            "Action Range",
            "Start Frame",
            "Scale/Repeat",
            "Blend Type",
            "Blend In/Out",
            "Playback",
        )
        for n in names:
            row = col.row()
            row.label(text=n)
        col = s.column(align=True)
        row = col.row(align=True)
        row.prop(self, "sa_beg", text="")
        row.prop(self, "sa_end", text="")
        row = col.row(align=True)
        row.prop(self, "s_beg", text="")
        row = col.row(align=True)
        row.prop(self, "s_sca", text="")
        row.prop(self, "s_rep", text="")
        row = col.row(align=True)
        row.prop(self, "s_bln", text="")
        row.prop(self, "s_blendauto", toggle=True)
        row = col.row(align=True)
        row.enabled = not self.s_blendauto
        row.prop(self, "s_blendin", text="")
        row.prop(self, "s_blendout", text="")
        row = col.row(align=True)
        row.prop(self, "s_xpl", text="")
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
        pool.update_ok = False
        ob = pool.pop_mesh
        try:
            if self.doall:
                boo_mute = not self.flagall
                for track in ob.data.animation_data.nla_tracks:
                    track.mute = boo_mute
                for item in pool.trax:
                    item.active = not boo_mute
            else:
                item = pool.trax[pool.trax_idx]
                ob.data.animation_data.nla_tracks[item.t_name].mute = item.active
                item.active = not item.active
        except Exception as my_err:
            pool.update_ok = True
            print(f"track_enable: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
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
        pool.update_ok = False
        try:
            me = pool.pop_mesh.data
            if self.doall:
                nt = [t for t in me.animation_data.nla_tracks]
                for t in nt:
                    me.animation_data.nla_tracks.remove(t)
                pool.trax.clear()
                pool.trax_idx = -1
            else:
                idx = pool.trax_idx
                item = pool.trax[idx]
                t = me.animation_data.nla_tracks.get(item.t_name)
                if t:
                    me.animation_data.nla_tracks.remove(t)
                pool.trax.remove(idx)
                pool.trax_idx = min(max(0, idx - 1), len(pool.trax) - 1)
            print("---- popmesh track_remove: delete trash")
            bpy.ops.outliner.orphans_purge(do_recursive=True)
        except Exception as my_err:
            pool.update_ok = True
            print(f"track_remove: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_track_copy(bpy.types.Operator):
    bl_label = "Copy"
    bl_idname = "ptdblnpopm.track_copy"
    bl_description = "new track - copy from active"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.update_ok = False
        ob = pool.pop_mesh
        try:
            target = pool.trax[pool.trax_idx]
            actest = bpy.data.actions.get(target.t_name)
            if not actest:
                raise Exception("null action reference!")
            action = actest.copy()
            name = action.name
            d = target.to_dct()
            source = pool.trax.add()
            for key in d.keys():
                setattr(source, key, d[key])
            source.name = f"{source.name}_copy"
            source.t_name = name
            idx = len(pool.trax) - 1
            pool.trax.move(idx, 0)
            pool.trax_idx = 0
            track = ob.data.animation_data.nla_tracks.new()
            track.name = name
            track.mute = not source.active
            start = int(action.frame_range[0])
            strip = track.strips.new(name, start, action)
            strip.scale = source.s_sca
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
            pool.update_ok = True
            print(f"track_copy: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


class PTDBLNPOPM_OT_anim_action(bpy.types.Operator):
    bl_label = "Animation"
    bl_idname = "ptdblnpopm.anim_action"
    bl_description = "new track - compile animation action"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        pool = context.scene.ptdblnpopm_pool
        pool.update_ok = False

        # ------------------ action evaluation -------------------#

        try:
            if not pool.pop_anim_state_eval():
                raise Exception("no animation values!")
        except Exception as my_err:
            pool.update_ok = True
            print(f"anim_action (acteval): {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}

        # ---------------------- shortcuts -----------------------#

        loop = pool.ani_kf_loop
        path = pool.path
        prof = pool.prof
        meshrot = pool.meshrot
        pathrot = pool.pathrot
        profrot = pool.profrot
        noiz = pool.noiz

        # ----------------- interpolation Lists ------------------#

        try:
            path_flag = path.anim_state()
            if path_flag:
                path_d = ModFNOP.aniact_path_edit_dict(path, loop)
            prof_flag = prof.anim_state()
            if prof_flag:
                prof_d = ModFNOP.aniact_prof_edit_dict(prof, loop)
            meshrot_play = meshrot.active and meshrot.anim_state()
            if meshrot_play:
                meshrot_angs = ModFNOP.aniact_rotation_list(meshrot.ani_rot, loop)
            pathrot_play = pathrot.active and pathrot.anim_state()
            if pathrot_play:
                pathrot_angs = ModFNOP.aniact_rotation_list(pathrot.ani_rot, loop)
            profrot_play = profrot.active and profrot.anim_state()
            if profrot_play:
                profrot_angs = ModFNOP.aniact_rotation_list(profrot.ani_rot, loop)
            pathloc_d = ModFNOP.aniact_edvals_dict(pool.pathloc, loop, twodim=False)
            blnd_d = ModFNOP.aniact_blendvals_dict(pool.blnd, loop)
            profloc_d = ModFNOP.aniact_edvals_dict(pool.profloc, loop, twodim=True)
            if noiz.active:
                nsd = None if (noiz.anim_state() and noiz.ani_seed) else noiz.nseed
                noiz_d = {"seed": nsd, "ampli": ModFNOP.aniact_noiz_list(noiz, loop)}
        except Exception as my_err:
            pool.update_ok = True
            print(f"anim_action (lrplst): {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}

        # --------------- animation loop updates -----------------#

        sindz = pool.rngs.sindz_get()
        sindz_on = pool.rngs.active
        nlocs = path.pathed.npts * prof.profed.npts
        try:
            pop = ModPOPM.new_pop_instance(pool)
            if meshrot.active:
                pop.mesh_rotate(meshrot.axis, meshrot.angle, meshrot.pivot)
            if pathrot.active:
                pop.path_rotate(
                    pathrot.axis,
                    pathrot.angle,
                    pathrot.pivot,
                    pathrot.piv_object,
                    pathrot.batt,
                )
            if profrot.active:
                pop.prof_rotate(profrot.roll)
            kloc = []
            for i in range(loop):
                pop.reset_edlocs()
                if path_flag:
                    pop.path_anim_update(*(v[i] for v in path_d.values()))
                if prof_flag:
                    pop.prof_anim_update(*(v[i] for v in prof_d.values()))
                for dct, nids, ams in zip(
                    pathloc_d["dcts"], pathloc_d["nids"], pathloc_d["ams"]
                ):
                    dct["nprams"]["idx"] = nids[i]
                    dct["fac"] = ams[i]
                    pop.path_locations(dct)
                for dct, nids, ams, ids in zip(
                    blnd_d["dcts"],
                    blnd_d["nids"],
                    blnd_d["ams"],
                    blnd_d["ids"],
                ):
                    dct["nprams"]["idx"] = nids[i]
                    dct["fac"] = ams[i]
                    dct["iprams"]["idx"] = ids[i]
                    pop.prof_blend(dct)
                for dct, nids, ams, ids in zip(
                    profloc_d["dcts"],
                    profloc_d["nids"],
                    profloc_d["ams"],
                    profloc_d["ids"],
                ):
                    dct["nprams"]["idx"] = nids[i]
                    dct["fac"] = ams[i]
                    dct["iprams"]["idx"] = ids[i]
                    pop.prof_locations(dct)
                if meshrot_play:
                    pop.meshrot_anim_angle(meshrot_angs[i])
                if pathrot_play:
                    pop.pathrot_anim_angle(pathrot_angs[i])
                if profrot_play:
                    pop.roll_anim_angle(profrot_angs[i])
                locs = pop.get_locs()
                if noiz.active:
                    locs = ModPOPM.noiz_locs(
                        locs, noiz.vfac, noiz_d["ampli"][i], noiz_d["seed"]
                    )
                if sindz_on:
                    locs = [locs[j] for j in range(nlocs) if j in sindz]
                kloc.append(locs)
        except Exception as my_err:
            pool.update_ok = True
            print(f"anim_action (animloop): {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}

        # ---------------- action fcurves loop -------------------#

        a_name = pool.act_name
        k_beg = pool.ani_kf_start
        k_stp = pool.ani_kf_step
        kls = [int(pool.ani_kf_type)] * loop
        fls = [k_beg + i * k_stp for i in range(loop)]
        try:
            popme = pool.pop_mesh.data
            active_locs = len(popme.vertices)
            trk = pool.trax.add()
            action = bpy.data.actions.new(a_name)
            for p in range(active_locs):
                dp = f"vertices[{p}].co"
                for di in range(3):
                    vls = [kloc[k][p][di] for k in range(loop)]
                    ModFNOP.aniact_fcurve_create(action, dp, di, fls, vls, kls, loop)
            ModFNOP.aniact_nla_track_add(popme, action)
            trk.name = a_name
            trk.t_name = action.name
            k_end = fls[-1]
            trk.ac_beg = k_beg
            trk.ac_end = k_end
            trk.sa_beg = k_beg
            trk.sa_end = k_end
            trk.s_beg = k_beg
            trk.s_end = k_end
            idx = len(pool.trax) - 1
            pool.trax.move(idx, 0)
            pool.trax_idx = 0
        except Exception as my_err:
            pool.update_ok = True
            print(f"anim_action (actnla): {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------


classes = (
    PTDBLNPOPM_OT_pop_simple_update,
    PTDBLNPOPM_OT_facerange_react,
    PTDBLNPOPM_OT_pop_reset,
    PTDBLNPOPM_OT_setup_provider,
    PTDBLNPOPM_OT_update_preset,
    PTDBLNPOPM_OT_display_options,
    PTDBLNPOPM_OT_pathrot_edit,
    PTDBLNPOPM_OT_profrot_edit,
    PTDBLNPOPM_OT_meshrot_edit,
    PTDBLNPOPM_OT_pop_noiz,
    PTDBLNPOPM_OT_citem_add,
    PTDBLNPOPM_OT_citem_copy,
    PTDBLNPOPM_OT_citem_enable,
    PTDBLNPOPM_OT_citem_remove,
    PTDBLNPOPM_OT_citem_move,
    PTDBLNPOPM_OT_setup_blnd_provider,
    PTDBLNPOPM_OT_blnd_add,
    PTDBLNPOPM_OT_blnd_enable,
    PTDBLNPOPM_OT_blnd_remove,
    PTDBLNPOPM_OT_blnd_move,
    PTDBLNPOPM_OT_write_setts,
    PTDBLNPOPM_OT_read_setts,
    PTDBLNPOPM_OT_animorph_setup,
    PTDBLNPOPM_OT_anicycmirend,
    PTDBLNPOPM_OT_anicalc,
    PTDBLNPOPM_OT_track_edit,
    PTDBLNPOPM_OT_track_enable,
    PTDBLNPOPM_OT_track_remove,
    PTDBLNPOPM_OT_track_copy,
    PTDBLNPOPM_OT_anim_action,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
