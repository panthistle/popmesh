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


# ------------------------------------------------------------------------------
#
# ------------------------------- BMUIL ----------------------------------------


# ---- USER LISTS


class PTDBLNPOPM_UL_pathloc(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPM_UL_profloc(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPM_UL_blnd(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


class PTDBLNPOPM_UL_trax(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        self.use_filter_show = False
        cust_icon = "REC" if item.active else "RADIOBUT_OFF"
        layout.prop(item, "name", text="", emboss=False, icon=cust_icon)


# ---- PANELS


def pop_mesh_valid(scene, ob):
    if ob and (ob.name in scene.objects):
        return True
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


def anim_rot_tmpl(c, ob, cap):
    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, "active", text=cap, toggle=True)
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
    col = row.column(align=True)
    col.prop(ob, "offrnd", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.offrnd
    col.prop(ob, "offrndseed", text="")
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
    col.prop(ob.mirror, "active", toggle=True)
    col = row.column(align=True)
    col.enabled = ob.mirror.active
    col.prop(ob.mirror, "cycles", text="")


def anim_fac_mirror_tmpl(c, flag, afm_ob):
    row = c.row(align=True)
    row.enabled = flag
    col = row.column(align=True)
    col.prop(afm_ob, "active", toggle=True)
    col = row.column(align=True)
    col.enabled = afm_ob.active
    col.prop(afm_ob, "cycles", text="")


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
        rc.operator("ptdblnpopm.pop_reset", text="Load Current").newdef = False
        rc = row.column(align=True)
        rc.operator("ptdblnpopm.pop_reset", text="Load Default").newdef = True
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.operator("ptdblnpopm.read_setts", text="Load File")
        rc = row.column(align=True)
        rc.enabled = edpans_ok
        rc.operator("ptdblnpopm.write_setts", text="Save File")
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


class PTDBLNPOPM_PT_ui_path(PTDBLNPOPM_PT_ui, bpy.types.Panel):
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
        col = row.column(align=True)
        col.prop(path, "provider", text="")
        col = row.column(align=True)
        provider = path.provider
        if provider == "custom":
            col.prop(path, "user_ob", text="")
        else:
            col.enabled = path.clean
            col.prop(path, f"res_{provider[:3]}", text="")
        path_edit = mesh_ok and edit_panels_ok(pool)
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = path_edit
        row.operator("ptdblnpopm.path_edit", text="Edit")
        pathed = path.pathed
        col = bcol.column(align=True)
        col.enabled = path_edit
        row = col.row(align=True)
        row.enabled = not pool.animorph
        rc = row.column(align=True)
        rc.prop(pathed, "closed", toggle=True)
        rc = row.column(align=True)
        rc.enabled = not pathed.closed
        rc.prop(pathed, "endcaps", toggle=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.prop(pathed, "upfixed", toggle=True)
        rc = row.column(align=True)
        rc.enabled = pathed.upfixed
        rc.prop(pathed, "upaxis", text="")
        row = col.row(align=True)
        row.enabled = False
        cap = f"nodes: {pathed.npts}" if path.clean else "... missing data!"
        row.label(text=cap)


class PTDBLNPOPM_PT_ui_path_anim(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPM_PT_ui_path"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        path = pool.path
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        provider = path.provider
        if provider == "line":
            dname = "length"
            dprop = "ani_lin_dim"
            fname = "exponent"
            fprop = "ani_lin_exp"
        elif provider == "wave":
            dname = "length"
            dprop = "ani_wav_dim"
            fname = "amplitude"
            fprop = "ani_wav_amp"
            fname2 = "frequency"
            fprop2 = "ani_wav_frq"
            fname3 = "phase"
            fprop3 = "ani_wav_pha"
        elif provider == "arc":
            dname = "chord"
            dprop = "ani_arc_dim"
            fname = "factor"
            fprop = "ani_arc_fac"
        elif provider == "helix":
            dname = "width"
            dprop = "ani_dim_2d"
            fname = "length"
            fprop = "ani_hel_len"
            fname2 = "factor"
            fprop2 = "ani_hel_fac"
            fname3 = "frequency"
            fprop3 = "ani_hel_stp"
            fname4 = "phase"
            fprop4 = "ani_hel_pha"
        elif provider == "spiral":
            dname = "diameter"
            dprop = "ani_spi_dim"
            fname = "frequency"
            fprop = "ani_spi_revs"
        elif provider == "ellipse":
            dname = "size"
            dprop = "ani_dim_2d"
            fname = "factor"
            fprop = "ani_ellstep_val"
        else:
            dname = "size"
            dprop = "ani_dim_3d" if provider == "custom" else "ani_dim_2d"
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(path, "ani_dim", toggle=True, text=dname)
        col = row.column(align=True)
        col.enabled = path.ani_dim
        row = col.row(align=True)
        if provider == "custom":
            for i in range(3):
                if path.pathed.user_dim[i]:
                    row.prop(path, dprop, index=i, text="")
        else:
            row.prop(path, dprop, text="")
        anim_fac_mirror_tmpl(c, path.ani_dim, path.ani_dim_mirror)
        if provider in {"line", "wave", "arc", "ellipse", "helix", "spiral"}:
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(path, "ani_fac", toggle=True, text=fname)
            col = row.column(align=True)
            col.enabled = path.ani_fac
            col.prop(path, fprop, text="")
            anim_fac_mirror_tmpl(c, path.ani_fac, path.ani_fac_mirror)
            if provider in {"wave", "helix"}:
                row = c.row(align=True)
                col = row.column(align=True)
                col.prop(path, "ani_fac2", toggle=True, text=fname2)
                col = row.column(align=True)
                col.enabled = path.ani_fac2
                col.prop(path, fprop2, text="")
                anim_fac_mirror_tmpl(c, path.ani_fac2, path.ani_fac2_mirror)
                row = c.row(align=True)
                col = row.column(align=True)
                col.prop(path, "ani_fac3", toggle=True, text=fname3)
                col = row.column(align=True)
                col.enabled = path.ani_fac3
                col.prop(path, fprop3, text="")
                anim_fac_mirror_tmpl(c, path.ani_fac3, path.ani_fac3_mirror)
                if provider == "helix":
                    row = c.row(align=True)
                    col = row.column(align=True)
                    col.prop(path, "ani_fac4", toggle=True, text=fname4)
                    col = row.column(align=True)
                    col.enabled = path.ani_fac4
                    col.prop(path, fprop4, text="")
                    anim_fac_mirror_tmpl(c, path.ani_fac4, path.ani_fac4_mirror)


class PTDBLNPOPM_PT_ui_pathrot(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "Path Rotation"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pathrot = pool.pathrot
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopm.pathrot_edit", text="Edit")
        row.prop(
            pathrot,
            "active",
            text="",
            toggle=True,
            icon="CHECKMARK" if pathrot.active else "PROP_OFF",
        )
        c = bcol.column(align=True)
        c.enabled = pathrot.active
        c.label(text="animation options")
        anim_rot_tmpl(c, pathrot.ani_rot, "rotate")


class PTDBLNPOPM_PT_ui_pathloc(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "Path Locations"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
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


class PTDBLNPOPM_PT_ui_pathloc_anim(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPM_PT_ui_pathloc"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.pathloc:
            item = pool.pathloc[pool.pathloc_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "node id")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            c.enabled = False
            c.label(text="no selection")


class PTDBLNPOPM_PT_ui_prof(PTDBLNPOPM_PT_ui, bpy.types.Panel):
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
        col = row.column(align=True)
        col.prop(prof, "provider", text="")
        col = row.column(align=True)
        provider = prof.provider
        if provider == "custom":
            col.prop(prof, "user_ob", text="")
        else:
            col.enabled = prof.clean
            col.prop(prof, f"res_{provider[:3]}", text="")
        prof_edit = mesh_ok and edit_panels_ok(pool)
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = prof_edit
        row.operator("ptdblnpopm.prof_edit", text="Edit")
        profed = prof.profed
        col = bcol.column(align=True)
        col.enabled = prof_edit
        row = col.row(align=True)
        row.enabled = not pool.animorph
        row.prop(profed, "closed", toggle=True)
        row = col.row(align=True)
        row.enabled = False
        cap = f"points: {profed.npts}" if prof.clean else "... missing data!"
        row.label(text=cap)


class PTDBLNPOPM_PT_ui_prof_anim(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPM_PT_ui_prof"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        prof = pool.prof
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        provider = prof.provider
        if provider == "line":
            dname = "length"
            dprop = "ani_lin_dim"
            fname = "exponent"
            fprop = "ani_lin_exp"
        elif provider == "wave":
            dname = "length"
            dprop = "ani_wav_dim"
            fname = "amplitude"
            fprop = "ani_wav_amp"
            fname2 = "frequency"
            fprop2 = "ani_wav_frq"
            fname3 = "phase"
            fprop3 = "ani_wav_pha"
        elif provider == "arc":
            dname = "chord"
            dprop = "ani_arc_dim"
            fname = "factor"
            fprop = "ani_arc_fac"
        else:
            dname = "size"
            dprop = "ani_epc_dim"
            fname = "factor"
            fprop = "ani_ellstep_val"
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(prof, "ani_dim", toggle=True, text=dname)
        col = row.column(align=True)
        col.enabled = prof.ani_dim
        row = col.row(align=True)
        if provider == "custom":
            for i in range(2):
                if prof.profed.user_dim[i]:
                    row.prop(prof, dprop, index=i, text="")
        else:
            row.prop(prof, dprop, text="")
        anim_fac_mirror_tmpl(c, prof.ani_dim, prof.ani_dim_mirror)
        if provider in {"line", "wave", "arc", "ellipse"}:
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(prof, "ani_fac", toggle=True, text=fname)
            col = row.column(align=True)
            col.enabled = prof.ani_fac
            col.prop(prof, fprop, text="")
            anim_fac_mirror_tmpl(c, prof.ani_fac, prof.ani_fac_mirror)
            if provider == "wave":
                row = c.row(align=True)
                col = row.column(align=True)
                col.prop(prof, "ani_fac2", toggle=True, text=fname2)
                col = row.column(align=True)
                col.enabled = prof.ani_fac2
                col.prop(prof, fprop2, text="")
                anim_fac_mirror_tmpl(c, prof.ani_fac2, prof.ani_fac2_mirror)
                row = c.row(align=True)
                col = row.column(align=True)
                col.prop(prof, "ani_fac3", toggle=True, text=fname3)
                col = row.column(align=True)
                col.enabled = prof.ani_fac3
                col.prop(prof, fprop3, text="")
                anim_fac_mirror_tmpl(c, prof.ani_fac3, prof.ani_fac3_mirror)


class PTDBLNPOPM_PT_ui_blnd(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "Blends"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopm.blnd_add").clone = False
        row.operator("ptdblnpopm.blnd_add", text="Clone").clone = True
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
            row.enabled = item.active
            row.operator("ptdblnpopm.blnd_edit", text="Edit")


class PTDBLNPOPM_PT_ui_blnd_anim(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPM_PT_ui_blnd"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.blnd:
            item = pool.blnd[pool.blnd_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "node id")
            anim_ind_tmpl(c, item.ani_idx, "point id")
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(item, "ani_fac", toggle=True)
            col = row.column(align=True)
            col.enabled = item.ani_fac
            col.prop(item, "ani_fac_val", text="")
            anim_fac_mirror_tmpl(c, item.ani_fac, item.ani_fac_mirror)
        else:
            c.enabled = False
            c.label(text="no selection")


class PTDBLNPOPM_PT_ui_profrot(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "Profile Rotation"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        profrot = pool.profrot
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopm.profrot_edit", text="Edit")
        row.prop(
            profrot,
            "active",
            text="",
            toggle=True,
            icon="CHECKMARK" if profrot.active else "PROP_OFF",
        )
        c = bcol.column(align=True)
        c.enabled = profrot.active
        c.label(text="animation options")
        anim_rot_tmpl(c, profrot.ani_rot, "roll")


class PTDBLNPOPM_PT_ui_profloc(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "Profile Locations"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
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


class PTDBLNPOPM_PT_ui_profloc_anim(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "animation options"
    bl_parent_id = "PTDBLNPOPM_PT_ui_profloc"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
        box = layout.box()
        c = box.column(align=True)
        if pool.profloc:
            item = pool.profloc[pool.profloc_idx]
            c.enabled = item.active
            anim_ind_tmpl(c, item.ani_nidx, "node id")
            anim_ind_tmpl(c, item.ani_idx, "point id")
            anim_fac_tmpl(c, item.ani_fac)
        else:
            c.enabled = False
            c.label(text="no selection")


class PTDBLNPOPM_PT_ui_meshrot(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "Mesh Rotation"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        meshrot = pool.meshrot
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator("ptdblnpopm.meshrot_edit", text="Edit")
        row.prop(
            meshrot,
            "active",
            text="",
            toggle=True,
            icon="CHECKMARK" if meshrot.active else "PROP_OFF",
        )
        c = bcol.column(align=True)
        c.enabled = meshrot.active
        c.label(text="animation options")
        anim_rot_tmpl(c, meshrot.ani_rot, "rotate")


class PTDBLNPOPM_PT_ui_noiz(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "Mesh Distortion"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        noiz = pool.noiz
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
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
        c.label(text="animation options")
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(noiz, "ani_noiz", toggle=True)
        col = row.column(align=True)
        col.enabled = noiz.ani_noiz
        col.prop(noiz, "ani_seed", toggle=True)
        row = c.row(align=True)
        row.enabled = noiz.ani_noiz
        row.prop(noiz, "ani_blin", text="")
        row.prop(noiz, "ani_blout", text="")
        row.prop(noiz, "ani_stp", text="")


class PTDBLNPOPM_PT_ui_ranges(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "Face Range"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        rngs = pool.rngs
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool) and not pool.animorph
        box = layout.box()
        bcol = box.column()
        row = bcol.row(align=True)
        col = row.column(align=True)
        range_on = rngs.active
        cap = "Disable" if range_on else "Enable"
        col.operator("ptdblnpopm.facerange_react", text=cap).active = range_on
        col = row.column(align=True)
        col.enabled = range_on
        col.prop(rngs, "invert", toggle=True)
        col = bcol.column(align=True)
        col.enabled = range_on
        row = col.row(align=True)
        row.prop(rngs, "rbeg", text="")
        row.prop(rngs, "pbeg", text="")
        row = col.row(align=True)
        row.prop(rngs, "ritm", text="")
        row.prop(rngs, "pitm", text="")
        row = col.row(align=True)
        row.prop(rngs, "rgap", text="")
        row.prop(rngs, "pgap", text="")
        row = col.row(align=True)
        row.prop(rngs, "rstp", text="")
        row.prop(rngs, "pstp", text="")
        row = bcol.row(align=True)
        row.enabled = range_on
        col = row.column(align=True)
        col.prop(rngs, "rndsel", toggle=True)
        col = row.column(align=True)
        col.enabled = rngs.rndsel
        col.prop(rngs, "nseed", text="")


class PTDBLNPOPM_PT_ui_anicalc(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "Anicalc"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        clc = pool.anicalc
        layout = self.layout
        box = layout.box()
        bcol = box.column()
        row = bcol.row(align=True)
        row.prop(clc, "calc_type", text="")
        row.operator("ptdblnpopm.anicalc", text="Calculate")
        row = bcol.row(align=True)
        col = row.column(align=True)
        caller = clc.calc_type
        row = col.row(align=True)
        if caller == "loop":
            row.prop(clc, "items", text="")
            row.prop(clc, "offset", text="")
            row = col.row(align=True)
            row.prop(clc, "start", text="")
            row.prop(clc, "step", text="")
        elif caller == "offsets":
            row.prop(clc, "items", text="")
        else:
            row.prop(clc, "loop", text="")
        row = col.row(align=True)
        row.prop(clc, "info", text="")


class PTDBLNPOPM_PT_ui_animode(PTDBLNPOPM_PT_ui, bpy.types.Panel):
    bl_label = "Animation"

    def draw(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        mesh_ok = pop_mesh_valid(scene, pool.pop_mesh)
        layout = self.layout
        layout.enabled = mesh_ok and edit_panels_ok(pool)
        animode_on = pool.animorph
        cap = "Leave Animode" if animode_on else "Enter Animode"
        box = layout.box()
        bcol = box.column()
        row = bcol.row()
        row.operator("ptdblnpopm.animorph_setup", text=cap).exiting = animode_on
        col = bcol.column(align=True)
        col.enabled = animode_on
        row = col.row(align=True)
        row.prop(pool, "act_name", text="")
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
        rc.operator("ptdblnpopm.anim_action", text="Add")
        rc = row.column(align=True)
        rc.enabled = nla_on
        rc.operator("ptdblnpopm.track_copy", text="Copy")
        col = col.column(align=True)
        col.enabled = nla_on
        row = col.row(align=True)
        row.template_list(
            "PTDBLNPOPM_UL_trax", "", pool, "trax", pool, "trax_idx", rows=2, maxrows=4
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
            names = ("Action Range:", "Strip Frames:", "Scale:", "Repeat:")
            for n in names:
                row = sc.row(align=True)
                row.label(text=n)
            sc = s.column(align=True)
            row = sc.row(align=True)
            row.label(text=f"{item.sa_beg} - {item.sa_end}")
            row = sc.row(align=True)
            row.label(text=f"{item.s_beg} - {item.s_end}")
            row = sc.row(align=True)
            row.label(text=f"{item.s_sca:.4f}")
            row = sc.row(align=True)
            reps = 1.0 if item.st_warp else item.s_rep
            row.label(text=f"{reps:.4f}")
        else:
            c.enabled = False
            c.label(text="no selection")


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------


classes = (
    PTDBLNPOPM_UL_pathloc,
    PTDBLNPOPM_UL_profloc,
    PTDBLNPOPM_UL_blnd,
    PTDBLNPOPM_UL_trax,
    PTDBLNPOPM_PT_ui_setup,
    PTDBLNPOPM_PT_ui_path,
    PTDBLNPOPM_PT_ui_path_anim,
    PTDBLNPOPM_PT_ui_pathloc,
    PTDBLNPOPM_PT_ui_pathloc_anim,
    PTDBLNPOPM_PT_ui_pathrot,
    PTDBLNPOPM_PT_ui_prof,
    PTDBLNPOPM_PT_ui_prof_anim,
    PTDBLNPOPM_PT_ui_blnd,
    PTDBLNPOPM_PT_ui_blnd_anim,
    PTDBLNPOPM_PT_ui_profloc,
    PTDBLNPOPM_PT_ui_profloc_anim,
    PTDBLNPOPM_PT_ui_profrot,
    PTDBLNPOPM_PT_ui_noiz,
    PTDBLNPOPM_PT_ui_meshrot,
    PTDBLNPOPM_PT_ui_ranges,
    PTDBLNPOPM_PT_ui_anicalc,
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
