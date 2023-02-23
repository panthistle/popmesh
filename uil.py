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


# ------------------------------------------------------------------------------
#
# ---------------------------- USER INTERFACE ----------------------------------

# ---- USER LISTS


class PTDBLNPOPM_UL_pathloc(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "RADIOBUT_ON" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPM_UL_profloc(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "RADIOBUT_ON" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPM_UL_blnd(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "RADIOBUT_ON" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPM_UL_trax(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "RADIOBUT_ON" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


# ---- PANELS


def pop_mesh_valid(scene, ob):

    if ob and (ob.name in scene.objects):
        return True
    return False


def pop_mesh_rotate_valid(scene, ob):

    if ob and (ob.name in scene.objects):
        return ob.rotation_mode == "QUATERNION"
    return False


def edit_panels_ok(pool):

    return pool.path.clean and pool.prof.clean


def coll_ops_tmpl(bcol, pool, cname, iname, coll_ob, coll_idx, ops_on):

    col = bcol.column(align=True)
    row = col.row(align=True)
    rc = row.column(align=True)
    c_op = rc.operator("ptdblnpopm.citem_add")
    c_op.cname = cname
    c_op.iname = iname
    boo = coll_ob[coll_idx].active if ops_on else False
    rc = row.column(align=True)
    rc.enabled = boo
    c_op = rc.operator("ptdblnpopm.citem_copy")
    c_op.cname = cname
    c_op.iname = iname
    c = col.column(align=True)
    c.enabled = ops_on
    row = c.row(align=True)
    user_list = f"PTDBLNPOPM_UL_{cname}"
    row.template_list(user_list, "", pool, cname, pool, iname, rows=2, maxrows=4)
    row = c.row(align=True)
    col = row.column(align=True)
    c_op = col.operator("ptdblnpopm.citem_enable", text="Disable" if boo else "Enable")
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = False
    col = row.column(align=True)
    c_op = col.operator("ptdblnpopm.citem_remove", text="Remove")
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = False
    col = row.column(align=True)
    col.enabled = coll_idx > 0
    c_op = col.operator("ptdblnpopm.citem_move", icon="TRIA_UP", text="")
    c_op.cname = cname
    c_op.iname = iname
    c_op.move_down = False
    row = c.row(align=True)
    col = row.column(align=True)
    col.enabled = len(coll_ob) > 1
    boo = False
    for i in coll_ob:
        if i.active:
            boo = True
            break
    c_op = col.operator(
        "ptdblnpopm.citem_enable",
        text="Disable All" if boo else "Enable All",
    )
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = True
    c_op.flagall = not boo
    col = row.column(align=True)
    col.enabled = len(coll_ob) > 1
    c_op = col.operator("ptdblnpopm.citem_remove", text="Remove All")
    c_op.cname = cname
    c_op.iname = iname
    c_op.doall = True
    col = row.column(align=True)
    col.enabled = coll_idx < (len(coll_ob) - 1)
    c_op = col.operator("ptdblnpopm.citem_move", icon="TRIA_DOWN", text="")
    c_op.cname = cname
    c_op.iname = iname
    c_op.move_down = True


def anim_rot_tmpl(c, ob):

    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, "active", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.active
    col.prop(ob, "fac", text="")
    row = c.row(align=True)
    row.enabled = ob.active
    row.prop(ob, "beg", text="")
    row.prop(ob, "end", text="")


def anim_ind_tmpl(c, ob, cap):

    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, "active", toggle=True, text=cap)
    col = row.column(align=True)
    col.enabled = ob.active
    col.prop(ob, "offset", text="")
    row = c.row(align=True)
    row.enabled = ob.active
    row.prop(ob, "beg", text="")
    row.prop(ob, "stp", text="")


def anim_fac_tmpl(c, ob):

    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, "active", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.active
    col.prop(ob, "fac", text="")
    row = c.row(align=True)
    row.enabled = ob.active
    col = row.column(align=True)
    col.prop(ob, "mirror", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.mirror
    col.prop(ob, "cycles", text="")


class PTDBLNPOPM_PT_ui:

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Mpop"


class PTDBLNPOPM_PT_ui_setup(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Setup"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        layout = self.layout
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        edpans_ok = edit_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.enabled = edpans_ok
        rc.operator("ptdblnpopm.pop_reset", text="New Mesh").newdef = False
        rc = row.column(align=True)
        rc.operator("ptdblnpopm.pop_reset", text="New Default").newdef = True
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.operator("ptdblnpopm.read_setts")
        rc = row.column(align=True)
        rc.enabled = edpans_ok
        rc.operator("ptdblnpopm.write_setts")
        row = col.row(align=True)
        row.enabled = mesh_ok
        cap = 'replace "' + (pool.pop_mesh.name if mesh_ok else "none") + '"'
        row.prop(pool, "replace_mesh", text=cap, toggle=True)
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = mesh_ok and edpans_ok
        row.prop(pool, "auto_smooth", toggle=True)
        row.prop(pool, "shade_smooth", toggle=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.enabled = mesh_ok and edpans_ok
        rc.prop(pool, "show_wire", toggle=True)
        rc = row.column(align=True)
        rc.prop(pool, "show_warn", toggle=True)


class PTDBLNPOPM_PT_ui_pop_rotate(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Object Rotation"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        obrot = pool.obrot
        mesh_rotate_ok = pop_mesh_rotate_valid(scene, pool.pop_mesh)
        edpans_ok = edit_panels_ok(pool)
        layout = self.layout
        layout.enabled = mesh_rotate_ok and edpans_ok
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopm.pop_rotate", text="Edit")
        row.prop(
            obrot,
            "active",
            text="",
            toggle=True,
            icon="CHECKMARK" if obrot.active else "PROP_OFF",
        )
        c = bcol.column(align=True)
        c.enabled = obrot.active
        c.label(text="Animation Options")
        anim_rot_tmpl(c, obrot.ani_rot)


class PTDBLNPOPM_PT_ui_path_edit(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Path"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        path = pool.path
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        path_setup = mesh_ok and pool.prof.clean and not pool.animorph
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = path_setup
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text="Type")
        row = sc.row()
        if path.provider == "custom":
            row.label(text="Select")
        else:
            row.label(text="Res")
        row = sc.row()
        row.enabled = False
        row.label(text="Source")
        row = sc.row()
        row.enabled = False
        row.label(text="Verts")
        sc = s.column(align=True)
        row = sc.row()
        row.prop(path, "provider", text="")
        row = sc.row()
        if path.provider == "custom":
            row.prop(path, "user_ob", text="")
        elif path.provider == "line":
            row.prop(path, "res_lin", text="")
        elif path.provider == "spiral":
            row.prop(path, "res_spi", text="")
        elif path.provider == "rectangle":
            row.prop(path, "res_rct", text="")
        else:
            row.prop(path, "res_ell", text="")
        row = sc.row()
        row.enabled = False
        info = f"{path.pathed.user_name}" if path.provider == "custom" else "preset"
        row.label(text=info)
        row = sc.row()
        row.enabled = False
        info = f"{path.pathed.rings} vertices" if path.clean else "... missing data!"
        row.label(text=info)
        path_edit = mesh_ok and edit_panels_ok(pool)
        row = col.row(align=True)
        row.enabled = path_edit
        row.operator("ptdblnpopm.path_edit", text="Edit")
        unvs = len(path.pathed.upv) if path.provider != "custom" else 0
        row = col.row(align=True)
        row.enabled = bool(unvs)
        row.operator(
            "ptdblnpopm.discard_verts", text=f"Discard {unvs} unused verts"
        ).caller = "path"
        c = bcol.column(align=True)
        c.enabled = path_edit
        c.label(text="Animation Options")
        if path.provider == "spiral":
            dprop = "ani_spi_dim"
            fprop = "ani_spi_revs"
        else:
            dprop = "ani_eru_dim"
            fprop = "ani_lin_exp" if path.provider == "line" else "ani_fac_val"
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(path, "ani_dim", text="Size", toggle=True)
        col = row.column(align=True)
        col.enabled = path.ani_dim
        row = col.row(align=True)
        if path.provider in ["ellipse", "rectangle"]:
            row.prop(path, dprop, index=0, text="")
            row.prop(path, dprop, index=2, text="")
        elif path.provider == "custom":
            for i in range(3):
                if path.pathed.user_dim[i]:
                    row.prop(path, dprop, index=i, text="")
        else:
            row.prop(path, dprop, text="")
        if path.provider in ["line", "ellipse", "spiral"]:
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(path, "ani_fac", toggle=True)
            col = row.column(align=True)
            col.enabled = path.ani_fac
            col.prop(path, fprop, text="")
        row = c.row(align=True)
        row.enabled = path.ani_dim or path.ani_fac
        col = row.column(align=True)
        col.prop(path, "ani_mirror", toggle=True)
        col = row.column(align=True)
        col.enabled = path.ani_mirror
        col.prop(path, "ani_cycles", text="")


class PTDBLNPOPM_PT_ui_prof_edit(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Profile"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        prof = pool.prof
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        prof_setup = mesh_ok and pool.path.clean and not pool.animorph
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = prof_setup
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text="Type")
        row = sc.row()
        if prof.provider == "custom":
            row.label(text="Select")
        else:
            row.label(text="Res")
        row = sc.row()
        row.enabled = False
        row.label(text="Source")
        row = sc.row()
        row.enabled = False
        row.label(text="Verts")
        sc = s.column(align=True)
        row = sc.row()
        row.prop(prof, "provider", text="")
        row = sc.row()
        if prof.provider == "custom":
            row.prop(prof, "user_ob", text="")
        elif prof.provider == "line":
            row.prop(prof, "res_lin", text="")
        elif prof.provider == "rectangle":
            row.prop(prof, "res_rct", text="")
        else:
            row.prop(prof, "res_ell", text="")
        row = sc.row()
        row.enabled = False
        info = f"{prof.profed.user_name}" if prof.provider == "custom" else "preset"
        row.label(text=info)
        row = sc.row()
        row.enabled = False
        info = f"{prof.profed.rpts} vertices" if prof.clean else "... missing data!"
        row.label(text=info)
        prof_edit = mesh_ok and edit_panels_ok(pool)
        row = col.row(align=True)
        row.enabled = prof_edit
        row.operator("ptdblnpopm.prof_edit", text="Edit")
        unvs = len(prof.profed.upv) if prof.provider != "custom" else 0
        row = col.row(align=True)
        row.enabled = bool(unvs)
        row.operator(
            "ptdblnpopm.discard_verts", text=f"Discard {unvs} unused verts"
        ).caller = "prof"
        c = bcol.column(align=True)
        c.enabled = prof_edit
        c.label(text="Animation Options")
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(prof, "ani_dim", text="Size", toggle=True)
        col = row.column(align=True)
        col.enabled = prof.ani_dim
        row = col.row(align=True)
        row.prop(prof, "ani_eru_dim", text="")
        if prof.provider in ["line", "ellipse"]:
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(prof, "ani_fac", toggle=True)
            col = row.column(align=True)
            col.enabled = prof.ani_fac
            fprop = "ani_lin_exp" if prof.provider == "line" else "ani_fac_val"
            col.prop(prof, fprop, text="")
        row = c.row(align=True)
        row.enabled = prof.ani_dim or prof.ani_fac
        col = row.column(align=True)
        col.prop(prof, "ani_mirror", toggle=True)
        col = row.column(align=True)
        col.enabled = prof.ani_mirror
        col.prop(prof, "ani_cycles", text="")


class PTDBLNPOPM_PT_ui_spro(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Path Spin"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        spro = pool.spro
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        edpans_ok = edit_panels_ok(pool)
        layout = self.layout
        layout.enabled = mesh_ok and edpans_ok
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopm.spro", text="Edit")
        row.prop(
            spro,
            "active",
            text="",
            toggle=True,
            icon="CHECKMARK" if spro.active else "PROP_OFF",
        )
        c = bcol.column(align=True)
        c.enabled = spro.active
        c.label(text="Animation Options")
        anim_rot_tmpl(c, spro.ani_rot)


class PTDBLNPOPM_PT_ui_pathlocs(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Path Locations"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        edpans_ok = edit_panels_ok(pool)
        layout = self.layout
        layout.enabled = mesh_ok and edpans_ok
        box = layout.box()
        bcol = box.column()
        pathloc = pool.pathloc
        pathlocidx = pool.pathloc_idx
        ops_on = bool(pathloc)
        coll_ops_tmpl(bcol, pool, "pathloc", "pathloc_idx", pathloc, pathlocidx, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = pathloc[pathlocidx]
            row = col.row()
            row.enabled = item.active
            row.operator("ptdblnpopm.pathloc_edit", text="Edit")
            c = bcol.column(align=True)
            c.enabled = item.active
            c.label(text="Animation Options")
            anim_ind_tmpl(c, item.ani_idx, "Index")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPM_PT_ui_blends(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Blends"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        edpans_ok = edit_panels_ok(pool)
        layout = self.layout
        layout.enabled = mesh_ok and edpans_ok
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopm.blnd_add")
        pblnd = pool.blnd
        pblndid = pool.blnd_idx
        ops_on = bool(pblnd)
        c = col.column(align=True)
        c.enabled = ops_on
        row = c.row(align=True)
        row.template_list(
            "PTDBLNPOPM_UL_blnd",
            "",
            pool,
            "blnd",
            pool,
            "blnd_idx",
            rows=2,
            maxrows=4,
        )
        row = c.row(align=True)
        boo = pblnd[pblndid].active if ops_on else False
        rc = row.column(align=True)
        rc.operator(
            "ptdblnpopm.blnd_enable", text="Disable" if boo else "Enable"
        ).doall = False
        rc = row.column(align=True)
        rc.operator("ptdblnpopm.blnd_remove", text="Remove").doall = False
        rc = row.column(align=True)
        rc.enabled = pblndid > 0
        rc.operator("ptdblnpopm.blnd_move", icon="TRIA_UP", text="").move_down = False
        row = c.row(align=True)
        rc = row.column(align=True)
        rc.enabled = len(pblnd) > 1
        boo = False
        for i in pblnd:
            if i.active:
                boo = True
                break
        blen_op = rc.operator(
            "ptdblnpopm.blnd_enable",
            text="Disable All" if boo else "Enable All",
        )
        blen_op.doall = True
        blen_op.flagall = not boo
        rc = row.column(align=True)
        rc.enabled = len(pblnd) > 1
        rc.operator("ptdblnpopm.blnd_remove", text="Remove All").doall = True
        rc = row.column(align=True)
        rc.enabled = pblndid < len(pblnd) - 1
        rc.operator("ptdblnpopm.blnd_move", icon="TRIA_DOWN", text="").move_down = True
        if ops_on:
            col = bcol.column()
            item = pblnd[pblndid]
            row = col.row(align=True)
            c = row.column(align=True)
            c.prop(item, "provider", text="")
            c = row.column(align=True)
            c.enabled = item.provider == "custom"
            c.prop(item, "user_ob", text="")
            col = bcol.column(align=True)
            row = col.row(align=True)
            row.enabled = False
            s = row.split(factor=0.30)
            sc = s.column(align=True)
            row = sc.row()
            row.label(text="Source: ")
            sc = s.column(align=True)
            i_ed = item.blnded
            row = sc.row()
            info = f"{i_ed.user_name}" if item.provider == "custom" else "preset"
            row.label(text=info)
            row = col.row(align=True)
            row.enabled = item.active
            row.operator("ptdblnpopm.blnd_edit", text="Edit")
            unvs = sum(len(i.blnded.upv) for i in pblnd if i.provider != "custom")
            row = col.row(align=True)
            row.enabled = bool(unvs)
            row.operator(
                "ptdblnpopm.discard_verts", text=f"Discard {unvs} unused verts"
            ).caller = "blnd"
            c = bcol.column(align=True)
            c.enabled = item.active
            c.label(text="Animation Options")
            anim_ind_tmpl(c, item.ani_idx, "Index")
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(item, "ani_fac", toggle=True)
            col = row.column(align=True)
            col.enabled = item.ani_fac
            col.prop(item, "ani_fac_val", text="")
            row = c.row(align=True)
            row.enabled = item.ani_fac
            col = row.column(align=True)
            col.prop(item, "ani_fac_mirror", toggle=True)
            col = row.column(align=True)
            col.enabled = item.ani_fac_mirror
            col.prop(item, "ani_fac_cycles", text="")
        else:
            col = bcol.column()
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPM_PT_ui_proflocs(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Profile Locations"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        edpans_ok = edit_panels_ok(pool)
        layout = self.layout
        layout.enabled = mesh_ok and edpans_ok
        box = layout.box()
        bcol = box.column()
        profloc = pool.profloc
        proflocidx = pool.profloc_idx
        ops_on = bool(profloc)
        coll_ops_tmpl(bcol, pool, "profloc", "profloc_idx", profloc, proflocidx, ops_on)
        col = bcol.column(align=True)
        if ops_on:
            item = profloc[proflocidx]
            row = col.row()
            row.enabled = item.active
            row.operator("ptdblnpopm.profloc_edit", text="Edit")
            c = bcol.column(align=True)
            c.enabled = item.active
            c.label(text="Animation Options")
            anim_ind_tmpl(c, item.ani_itm_idx, "Item Index")
            anim_ind_tmpl(c, item.ani_idx, "Point Index")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            col.enabled = False
            col.label(text="no edits")


class PTDBLNPOPM_PT_ui_noiz(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Location Noise"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        noiz = pool.noiz
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        edpans_ok = edit_panels_ok(pool)
        layout = self.layout
        layout.enabled = mesh_ok and edpans_ok
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopm.pop_noiz", text="Edit")
        row.prop(
            noiz,
            "active",
            text="",
            toggle=True,
            icon="CHECKMARK" if noiz.active else "PROP_OFF",
        )
        c = bcol.column(align=True)
        c.enabled = noiz.active
        c.label(text="Animation Options")
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(noiz, "ani_p_noiz", toggle=True)
        col = row.column(align=True)
        col.enabled = noiz.ani_p_noiz
        col.prop(noiz, "ani_p_noiz_val", text="")
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(noiz, "ani_f_noiz", toggle=True)
        col = row.column(align=True)
        col.enabled = noiz.ani_f_noiz
        col.prop(noiz, "ani_f_noiz_val", text="")
        opt_on = noiz.ani_p_noiz or noiz.ani_f_noiz
        row = c.row(align=True)
        row.enabled = opt_on
        row.prop(noiz, "ani_seed", toggle=True)
        row = c.row(align=True)
        row.enabled = opt_on and not noiz.ani_seed
        row.prop(noiz, "ani_blin", text="")
        row.prop(noiz, "ani_blout", text="")


class PTDBLNPOPM_PT_ui_ranges(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Face Range"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        rngs = pool.rngs
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        edpans_ok = edit_panels_ok(pool)
        layout = self.layout
        layout.enabled = mesh_ok and edpans_ok and not pool.animorph
        box = layout.box()
        bcol = box.column()
        row = bcol.row(align=True)
        col = row.column(align=True)
        col.prop(rngs, "active", text="Active", toggle=True)
        col = row.column(align=True)
        col.enabled = rngs.active
        col.prop(rngs, "invert", toggle=True)
        s = bcol.split(factor=0.3)
        s.enabled = rngs.active
        col = s.column(align=True)
        row = col.row(align=True)
        row.label(text="")
        row = col.row(align=True)
        row.alignment = "RIGHT"
        row.label(text="Begin:")
        row = col.row(align=True)
        row.alignment = "RIGHT"
        row.label(text="End:")
        row = col.row(align=True)
        row.alignment = "RIGHT"
        row.label(text="Step:")
        row = col.row(align=True)
        row.alignment = "RIGHT"
        row.label(text="Items:")
        col = s.column(align=True)
        row = col.row(align=True)
        row.label(text="Path")
        row = col.row(align=True)
        row.prop(rngs, "rbeg", text="")
        row = col.row(align=True)
        row.prop(rngs, "rend", text="")
        row = col.row(align=True)
        row.prop(rngs, "rstp", text="")
        row = col.row(align=True)
        row.prop(rngs, "ritm", text="")
        col = s.column(align=True)
        row = col.row(align=True)
        row.label(text="Profile")
        row = col.row(align=True)
        row.prop(rngs, "pbeg", text="")
        row = col.row(align=True)
        row.prop(rngs, "pend", text="")
        row = col.row(align=True)
        row.prop(rngs, "pstp", text="")
        row = col.row(align=True)
        row.prop(rngs, "pitm", text="")
        row = bcol.row(align=True)
        row.enabled = rngs.active
        col = row.column(align=True)
        col.prop(rngs, "rndsel", text="Randomize", toggle=True)
        col = row.column(align=True)
        col.enabled = rngs.rndsel
        col.prop(rngs, "nseed", text="")


class PTDBLNPOPM_PT_ui_animode(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Animation"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        edpans_ok = edit_panels_ok(pool)
        layout = self.layout
        layout.enabled = mesh_ok and edpans_ok
        animode_on = pool.animorph
        cap = "Leave Animode" if animode_on else "Enter Animode"
        box = layout.box()
        bcol = box.column()
        row = bcol.row()
        row.operator("ptdblnpopm.animorph_setup", text=cap).exiting = animode_on
        col = bcol.column(align=True)
        col.enabled = animode_on
        row = col.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.label(text="Action:")
        row = sc.row(align=True)
        row.label(text="Owner:")
        row = sc.row(align=True)
        row.label(text="Lerp:")
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(pool, "act_name", text="")
        row = sc.row(align=True)
        row.prop(pool, "act_owner", text="")
        row = sc.row(align=True)
        row.prop(pool, "ani_kf_type", text="")
        c = bcol.column(align=True)
        c.enabled = animode_on
        row = c.row(align=True)
        row.prop(pool, "ani_kf_start", text="")
        row.prop(pool, "ani_kf_step", text="")
        row.prop(pool, "ani_kf_loop", text="")
        row = c.row(align=True)
        row.operator("ptdblnpopm.anicycmirend")
        trax = pool.trax
        traxidx = pool.trax_idx
        nla_on = animode_on and bool(trax)
        col = bcol.column(align=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.enabled = animode_on
        rc.operator("ptdblnpopm.ani_action", text="Add")
        rc = row.column(align=True)
        rc.enabled = nla_on
        rc.operator("ptdblnpopm.track_copy", text="Copy")
        col = col.column(align=True)
        col.enabled = nla_on
        row = col.row(align=True)
        row.template_list(
            "PTDBLNPOPM_UL_trax",
            "",
            pool,
            "trax",
            pool,
            "trax_idx",
            rows=2,
            maxrows=4,
        )
        row = col.row(align=True)
        boo = trax[traxidx].active if nla_on else False
        c = row.column(align=True)
        c.operator(
            "ptdblnpopm.track_enable", text="Disable" if boo else "Enable"
        ).doall = False
        c = row.column(align=True)
        c.operator("ptdblnpopm.track_remove", text="Remove").doall = False
        row = col.row(align=True)
        c = row.column(align=True)
        c.enabled = len(trax) > 1
        boo = False
        for i in trax:
            if i.active:
                boo = True
                break
        trken_op = c.operator(
            "ptdblnpopm.track_enable",
            text="Disable All" if boo else "Enable All",
        )
        trken_op.doall = True
        trken_op.flagall = not boo
        c = row.column(align=True)
        c.enabled = len(trax) > 1
        c.operator("ptdblnpopm.track_remove", text="Remove All").doall = True
        c = col.column(align=True)
        if nla_on:
            item = trax[traxidx]
            row = c.row()
            row.enabled = item.active
            row.operator("ptdblnpopm.track_edit", text="Edit")
            box = c.box()
            box.enabled = False
            row = box.row(align=True)
            s = row.split(factor=0.6)
            sc = s.column(align=True)
            row = sc.row(align=True)
            row.label(text="Action Frames:")
            row = sc.row(align=True)
            row.label(text="Strip Frames:")
            row = sc.row(align=True)
            row.label(text="Repeats:")
            row = sc.row(align=True)
            row.label(text="Scale:")
            sc = s.column(align=True)
            row = sc.row(align=True)
            row.label(text=f"{item.sa_beg} - {item.sa_end}")
            row = sc.row(align=True)
            row.label(text=f"{item.s_beg} - {item.s_end}")
            row = sc.row(align=True)
            row.label(text=f"{item.s_rep:.4f}")
            row = sc.row(align=True)
            row.label(text=f"{item.s_sca:.4f}")
        else:
            c.label(text="track info")


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------

classes = (
    PTDBLNPOPM_UL_pathloc,
    PTDBLNPOPM_UL_profloc,
    PTDBLNPOPM_UL_blnd,
    PTDBLNPOPM_UL_trax,
    PTDBLNPOPM_PT_ui_setup,
    PTDBLNPOPM_PT_ui_path_edit,
    PTDBLNPOPM_PT_ui_prof_edit,
    PTDBLNPOPM_PT_ui_blends,
    PTDBLNPOPM_PT_ui_spro,
    PTDBLNPOPM_PT_ui_pathlocs,
    PTDBLNPOPM_PT_ui_proflocs,
    PTDBLNPOPM_PT_ui_noiz,
    PTDBLNPOPM_PT_ui_pop_rotate,
    PTDBLNPOPM_PT_ui_ranges,
    PTDBLNPOPM_PT_ui_animode,
)


def register():

    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
