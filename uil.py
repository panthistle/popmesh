
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


# ------------------------------------------------------------------------------
#
# ---------------------------- USER INTERFACE ----------------------------------
#
# ---- USER LIST TEMPLATES

class PTDBLNPOPM_UL_plox(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                    active_propname, index):
        self.use_filter_show = False
        cust_icon = 'RADIOBUT_ON' if item.active else 'RADIOBUT_OFF'
        layout.prop(item, 'name', text='', emboss=False, icon=cust_icon)


class PTDBLNPOPM_UL_proflox(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                    active_propname, index):
        self.use_filter_show = False
        cust_icon = 'RADIOBUT_ON' if item.active else 'RADIOBUT_OFF'
        layout.prop(item, 'name', text='', emboss=False, icon=cust_icon)


class PTDBLNPOPM_UL_blpc(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                    active_propname, index):
        self.use_filter_show = False
        cust_icon = 'RADIOBUT_ON' if item.active else 'RADIOBUT_OFF'
        layout.prop(item, 'name', text='', emboss=False, icon=cust_icon)


class PTDBLNPOPM_UL_trax(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data,
                    active_propname, index):
        self.use_filter_show = False
        cust_icon = 'RADIOBUT_ON' if item.active else 'RADIOBUT_OFF'
        layout.prop(item, 'name', text='', emboss=False, icon=cust_icon)


# ------------------------------------------------------------------------------
#
# ---- PANELS

def pop_mesh_valid(scene):

    ob = scene.ptdblnpopm_props.pop_mesh
    if ob and (ob.name in scene.objects):
        return True
    return False


def pop_rotate_valid(scene):

    ob = scene.ptdblnpopm_props.pop_mesh
    if ob and (ob.name in scene.objects):
        return (ob.rotation_mode == 'QUATERNION')
    return False


def edit_panels_ok(props):

    return (props.path.clean and props.prof.clean)


def anim_rot_tmpl(c, ob):

    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, 'ani_rot', toggle=True)
    col = row.column(align=True)
    col.enabled = ob.ani_rot
    col.prop(ob, 'ani_rot_ang', text='')
    row = c.row(align=True)
    row.enabled = ob.ani_rot
    row.prop(ob, 'ani_rot_beg', text='')
    row.prop(ob, 'ani_rot_end', text='')


def anim_ind_tmpl(c, ob, cap):

    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, 'active', toggle=True, text=cap)
    col = row.column(align=True)
    col.enabled = ob.active
    col.prop(ob, 'offset', text='')
    row = c.row(align=True)
    row.enabled = ob.active
    row.prop(ob, 'beg', text='')
    row.prop(ob, 'stp', text='')


def anim_fac_tmpl(c, ob):

    row = c.row(align=True)
    col = row.column(align=True)
    col.prop(ob, 'active', toggle=True)
    col = row.column(align=True)
    col.enabled = ob.active
    col.prop(ob, 'fac', text='')
    row = c.row(align=True)
    row.enabled = ob.active
    col = row.column(align=True)
    col.prop(ob, 'mirror', toggle=True)
    col = row.column(align=True)
    col.enabled = ob.mirror
    col.prop(ob, 'cycles', text='')


class PTDBLNPOPM_PT_ui:

    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_category = "Mpop"


class PTDBLNPOPM_PT_ui_setup(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Setup"

    def draw(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        layout = self.layout
        mesh_ok = pop_mesh_valid(scene)
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.operator('ptdblnpopm.new_mesh')
        rc = row.column(align=True)
        rc.enabled = ( edit_panels_ok(props) and not props.animorph )
        rc.operator('ptdblnpopm.write_setts')
        row = col.row(align=True)
        row.enabled = ( mesh_ok and not props.animorph )
        rc = row.column(align=True)
        rc.operator('ptdblnpopm.pop_reset')
        rc = row.column(align=True)
        rc.operator('ptdblnpopm.read_setts')
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = ( mesh_ok and edit_panels_ok(props) )
        rc = row.column(align=True)
        rc.prop(props, 'auto_smooth', toggle=True)
        rc = row.column(align=True)
        rc.prop(props, 'shade_smooth', toggle=True)
        row = col.row(align=True)
        row.enabled = ( mesh_ok and edit_panels_ok(props) )
        row.prop(props, 'show_wire', toggle=True)
        row = col.row(align=True)
        row.prop(props, 'show_warn', toggle=True)
        row = col.row(align=True)
        row.enabled = False
        obname = f'{props.pop_mesh.name}' if mesh_ok else 'mesh undefined!'
        row.label(text=obname)


class PTDBLNPOPM_PT_ui_pop_rotate(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Object Rotation"

    def draw(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        obrot = props.obrot
        layout = self.layout
        layout.enabled = ( pop_rotate_valid(scene) and edit_panels_ok(props) )
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator('ptdblnpopm.pop_rotate', text='Edit')
        row.prop(obrot, 'active', text='', toggle=True,
                icon = 'CHECKMARK' if obrot.active else 'PROP_OFF')
        c = bcol.column(align=True)
        c.enabled = obrot.active
        c.label(text='Animation Options')
        anim_rot_tmpl(c, obrot)


class PTDBLNPOPM_PT_ui_path_edit(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Path"

    def draw(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        path = props.path
        mesh_ok = pop_mesh_valid(scene)
        layout = self.layout
        path_setup = ( mesh_ok and props.prof.clean and not props.animorph )
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = path_setup
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text='Type')
        row = sc.row()
        if path.provider == 'custom':
            row.label(text='Select')
        else:
            row.label(text='Res')
        row = sc.row()
        row.enabled = False
        row.label(text='Verts')
        sc = s.column(align=True)
        row = sc.row()
        row.prop(path, 'provider', text='')
        row = sc.row()
        if path.provider == 'custom':
            row.prop(path, 'user_ob', text='')
        elif path.provider == 'line':
            row.prop(path, 'res_lin', text='')
        elif path.provider == 'spiral':
            row.prop(path, 'res_spi', text='')
        elif path.provider == 'rectangle':
            row.prop(path, 'res_rct', text='')
        else:
            row.prop(path, 'res_ell', text='')
        row = sc.row()
        row.enabled = False
        row.label(text=f'{path.rings} vertices'
                            if path.clean else '... missing data!')
        path_edit = ( mesh_ok and edit_panels_ok(props) )
        row = col.row(align=True)
        row.enabled = path_edit
        row.operator('ptdblnpopm.path_edit', text='Edit')
        c = bcol.column(align=True)
        c.enabled = mesh_ok
        c.label(text='Animation Options')
        if path.provider == 'line':
            dtext = 'Length'
            dprop = 'ani_lin_dim'
            fprop = 'ani_lin_exp'
        elif path.provider == 'spiral':
            dtext = 'Size'
            dprop = 'ani_spi_dim'
            fprop = 'ani_spi_revs'
        else:
            dtext = 'Size'
            dprop = 'ani_eru_dim'
            fprop = 'ani_fac_val'
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(path, 'ani_dim', text=dtext, toggle=True)
        col = row.column(align=True)
        col.enabled = path.ani_dim
        row = col.row(align=True)
        if path.provider in ['ellipse', 'rectangle']:
            row.prop(path, dprop, index=0, text='')
            row.prop(path, dprop, index=1, text='')
        else:
            row.prop(path, dprop, text='')
        if path.provider in ['line', 'ellipse', 'spiral']:
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(path, 'ani_fac', toggle=True)
            col = row.column(align=True)
            col.enabled = path.ani_fac
            col.prop(path, fprop, text='')
        row = c.row(align=True)
        row.enabled = path.ani_dim or path.ani_fac
        col = row.column(align=True)
        col.prop(path, 'ani_sty_mirror', toggle=True)
        col = row.column(align=True)
        col.enabled = path.ani_sty_mirror
        col.prop(path, 'ani_sty_cycles', text='')


class PTDBLNPOPM_PT_ui_prof_edit(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Profile"

    def draw(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        prof = props.prof
        mesh_ok = pop_mesh_valid(scene)
        layout = self.layout
        prof_setup = ( mesh_ok and props.path.clean and not props.animorph )
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.enabled = prof_setup
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text='Type')
        row = sc.row()
        if prof.provider == 'custom':
            row.label(text='Select')
        else:
            row.label(text='Res')
        row = sc.row()
        row.enabled = False
        row.label(text='Verts')
        sc = s.column(align=True)
        row = sc.row()
        row.prop(prof, 'provider', text='')
        row = sc.row()
        if prof.provider == 'custom':
            row.prop(prof, 'user_ob', text='')
        elif prof.provider == 'rectangle':
            row.prop(prof, 'res_rct', text='')
        else:
            row.prop(prof, 'res_ell', text='')
        row = sc.row()
        row.enabled = False
        row.label(text = f'{prof.rpts} vertices'
                            if prof.clean else '... missing data!')
        prof_edit = ( mesh_ok and edit_panels_ok(props) )
        row = col.row(align=True)
        row.enabled = prof_edit
        row.operator('ptdblnpopm.prof_edit', text='Edit')
        c = bcol.column(align =True)
        c.enabled = mesh_ok
        c.label(text='Animation Options')
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(prof, 'ani_dim', text='Size', toggle=True)
        col = row.column(align=True)
        col.enabled = prof.ani_dim
        row = col.row(align=True)
        row.prop(prof, 'ani_eru_dim', index=0, text='')
        row.prop(prof, 'ani_eru_dim', index=1, text='')
        if prof.provider == 'ellipse':
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(prof, 'ani_fac', toggle=True)
            col = row.column(align=True)
            col.enabled = prof.ani_fac
            col.prop(prof, 'ani_fac_val', text='')
        row = c.row(align=True)
        row.enabled = prof.ani_dim or prof.ani_fac
        col = row.column(align=True)
        col.prop(prof, 'ani_sty_mirror', toggle=True)
        col = row.column(align=True)
        col.enabled = prof.ani_sty_mirror
        col.prop(prof, 'ani_sty_cycles', text='')


class PTDBLNPOPM_PT_ui_spinroll(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Path Spinroll"

    def draw(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        spro = props.spro
        layout = self.layout
        layout.enabled = ( pop_mesh_valid(scene) and edit_panels_ok(props) )
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator('ptdblnpopm.spinroll', text='Edit')
        row.prop(spro, 'active', text='', toggle=True,
                icon = 'CHECKMARK' if spro.active else 'PROP_OFF')
        c = bcol.column(align=True)
        c.enabled = spro.active
        c.label(text='Animation Options')
        anim_rot_tmpl(c, spro)


class PTDBLNPOPM_PT_ui_pathlocs(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Path Locations"

    def draw(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        layout = self.layout
        layout.enabled = ( pop_mesh_valid(scene) and edit_panels_ok(props) )
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.operator('ptdblnpopm.ploc_add')
        plox = props.plox
        ploxidx = props.plox_idx
        ops_on = bool(plox)
        boo = plox[ploxidx].active if ops_on else False
        rc = row.column(align=True)
        rc.enabled = boo
        rc.operator('ptdblnpopm.ploc_copy')
        c = col.column(align=True)
        c.enabled = ops_on
        row = c.row(align=True)
        row.template_list("PTDBLNPOPM_UL_plox", "", props, "plox", props,
                            "plox_idx", rows=2, maxrows=4)
        row = c.row(align=True)
        col = row.column(align=True)
        col.operator('ptdblnpopm.ploc_enable',
                        text='Disable' if boo else 'Enable').doall=False
        col = row.column(align=True)
        col.operator('ptdblnpopm.ploc_remove', text='Remove').doall=False
        col = row.column(align=True)
        col.enabled = (ploxidx > 0)
        col.operator('ptdblnpopm.ploc_move', icon='TRIA_UP',
                        text='').move_down=False
        row = c.row(align=True)
        col = row.column(align=True)
        col.enabled = (len(plox) > 1)
        col.operator('ptdblnpopm.ploc_enable', text='Enable All'
                        if props.plox_disabled else 'Disable All').doall=True
        col = row.column(align=True)
        col.enabled = (len(plox) > 1)
        col.operator('ptdblnpopm.ploc_remove', text='Remove All').doall=True
        col = row.column(align=True)
        col.enabled = (ploxidx < len(plox)-1)
        col.operator('ptdblnpopm.ploc_move', icon='TRIA_DOWN',
                        text='').move_down=True
        col = c.column(align=True)
        if ops_on:
            item = plox[ploxidx]
            row = col.row()
            row.enabled = item.active
            row.operator('ptdblnpopm.ploc_edit', text='Edit')
            c = bcol.column(align=True)
            c.enabled = item.active
            c.label(text='Animation Options')
            anim_ind_tmpl(c, item.ani_idx, 'Index')
            anim_fac_tmpl(c, item.ani_fac)
        else:
            col.enabled = False
            col.label(text = 'no edits')


class PTDBLNPOPM_PT_ui_blends(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Profile Blends"

    def draw(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        layout = self.layout
        layout.enabled = ( pop_mesh_valid(scene) and edit_panels_ok(props) )
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator('ptdblnpopm.blp_add')
        pblpc = props.blpc
        pblpid = props.blpc_idx
        ops_on = bool(pblpc)
        c = col.column(align=True)
        c.enabled = ops_on
        row = c.row(align=True)
        row.template_list("PTDBLNPOPM_UL_blpc", "", props, "blpc", props,
                            "blpc_idx", rows=2, maxrows=4)
        row = c.row(align=True)
        boo = pblpc[pblpid].active if ops_on else False
        col = row.column(align=True)
        col.operator('ptdblnpopm.blp_enable',
                        text='Disable' if boo else 'Enable').doall=False
        col = row.column(align=True)
        col.operator('ptdblnpopm.blp_remove', text='Remove').doall=False
        col = row.column(align=True)
        col.enabled = (pblpid > 0)
        col.operator('ptdblnpopm.blp_move', icon='TRIA_UP',
                        text='').move_down=False
        row = c.row(align=True)
        col = row.column(align=True)
        col.enabled = (len(pblpc) > 1)
        col.operator('ptdblnpopm.blp_enable', text='Enable All'
                        if props.blpc_disabled else 'Disable All').doall=True
        col = row.column(align=True)
        col.enabled = (len(pblpc) > 1)
        col.operator('ptdblnpopm.blp_remove', text='Remove All').doall=True
        col = row.column(align=True)
        col.enabled = (pblpid < len(pblpc)-1)
        col.operator('ptdblnpopm.blp_move', icon='TRIA_DOWN',
                        text='').move_down=True
        if ops_on:
            col = bcol.column()
            item = pblpc[pblpid]
            row = col.row(align=True)
            c = row.column(align=True)
            c.prop(item, 'provider', text='')
            c = row.column(align=True)
            c.enabled = (item.provider == 'custom')
            if item.provider == 'custom':
                c.prop(item, 'user_ob', text='')
            else:
                c.label(text='  Preset')
            row = col.row(align=True)
            row.enabled = item.active
            row.operator('ptdblnpopm.blp_edit', text='Edit')
            c = bcol.column(align=True)
            c.enabled = item.active
            c.label(text='Animation Options')
            anim_ind_tmpl(c, item.ani_idx, 'Index')
            row = c.row(align=True)
            col = row.column(align=True)
            col.prop(item, 'ani_fac', toggle=True)
            col = row.column(align=True)
            col.enabled = item.ani_fac
            col.prop(item, 'ani_fac_val', text='')
            row = c.row(align=True)
            row.enabled = item.ani_fac
            col = row.column(align=True)
            col.prop(item, 'ani_fac_mirror', toggle=True)
            col = row.column(align=True)
            col.enabled = item.ani_fac_mirror
            col.prop(item, 'ani_fac_cycles', text='')
        else:
            col = bcol.column()
            col.enabled = False
            col.label(text = 'no edits')


class PTDBLNPOPM_PT_ui_proflocs(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Profile Locations"

    def draw(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        layout = self.layout
        layout.enabled = ( pop_mesh_valid(scene) and edit_panels_ok(props) )
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.operator('ptdblnpopm.profloc_add')
        prflox = props.proflox
        prfidx = props.proflox_idx
        ops_on = bool(prflox)
        boo = prflox[prfidx].active if ops_on else False
        rc = row.column(align=True)
        rc.enabled = boo
        rc.operator('ptdblnpopm.profloc_copy')
        c = col.column(align=True)
        c.enabled = ops_on
        row = c.row(align=True)
        row.template_list("PTDBLNPOPM_UL_proflox", "", props, "proflox",
                            props, "proflox_idx", rows=2, maxrows=4)
        row = c.row(align=True)
        col = row.column(align=True)
        col.operator('ptdblnpopm.profloc_enable',
                        text='Disable' if boo else 'Enable').doall=False
        col = row.column(align=True)
        col.operator('ptdblnpopm.profloc_remove', text='Remove').doall=False
        col = row.column(align=True)
        col.enabled = (prfidx > 0)
        col.operator('ptdblnpopm.profloc_move', icon='TRIA_UP',
                        text='').move_down=False
        row = c.row(align=True)
        col = row.column(align=True)
        col.enabled = (len(prflox) > 1)
        col.operator('ptdblnpopm.profloc_enable', text='Enable All'
                    if props.proflox_disabled else 'Disable All').doall=True
        col = row.column(align=True)
        col.enabled = (len(prflox) > 1)
        col.operator('ptdblnpopm.profloc_remove',
                        text='Remove All').doall=True
        col = row.column(align=True)
        col.enabled = (prfidx < len(prflox)-1)
        col.operator('ptdblnpopm.profloc_move', icon='TRIA_DOWN',
                        text='').move_down=True
        col = c.column(align=True)
        if ops_on:
            item = prflox[prfidx]
            row = col.row()
            row.enabled = item.active
            row.operator('ptdblnpopm.profloc_edit', text='Edit')
            c = bcol.column(align=True)
            c.enabled = item.active
            c.label(text='Animation Options')
            anim_ind_tmpl(c, item.ani_itm_idx, 'Item Index')
            anim_ind_tmpl(c, item.ani_idx, 'Point Index')
            anim_fac_tmpl(c, item.ani_fac)
        else:
            col.enabled = False
            col.label(text = 'no edits')


class PTDBLNPOPM_PT_ui_noise(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Noise"

    def draw(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        noiz = props.noiz
        layout = self.layout
        layout.enabled = ( pop_mesh_valid(scene) and edit_panels_ok(props) )
        box = layout.box()
        bcol = box.column()
        col = bcol.column(align=True)
        row = col.row(align=True)
        row.operator('ptdblnpopm.pop_noise', text='Edit')
        row.prop(noiz, 'active', text='', toggle=True,
                icon = 'CHECKMARK' if noiz.active else 'PROP_OFF')
        c = bcol.column(align=True)
        c.enabled = noiz.active
        c.label(text='Animation Options')
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(noiz, 'ani_p_noise', toggle=True)
        col = row.column(align=True)
        col.enabled = noiz.ani_p_noise
        col.prop(noiz, 'ani_p_noise_val', text='')
        row = c.row(align=True)
        col = row.column(align=True)
        col.prop(noiz, 'ani_f_noise', toggle=True)
        col = row.column(align=True)
        col.enabled = noiz.ani_f_noise
        col.prop(noiz, 'ani_f_noise_val', text='')
        opt_on = noiz.ani_p_noise or noiz.ani_f_noise
        row = c.row(align=True)
        row.enabled = opt_on
        row.prop(noiz, 'ani_seed', toggle=True)
        row = c.row(align=True)
        row.enabled = opt_on and not noiz.ani_seed
        row.prop(noiz, 'ani_blin', text='')
        row.prop(noiz, 'ani_blout', text='')


class PTDBLNPOPM_PT_ui_ranges(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Face Range"

    def draw(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        rngs = props.rngs
        layout = self.layout
        layout.enabled = ( pop_mesh_valid(scene) and edit_panels_ok(props)
                            and not props.animorph )
        box = layout.box()
        bcol = box.column()
        row = bcol.row(align=True)
        col = row.column(align=True)
        col.prop(rngs, 'active', text='Active', toggle=True)
        col = row.column(align=True)
        col.enabled = rngs.active
        col.prop(rngs, 'invert', toggle=True)
        col = row.column(align=True)
        col.enabled = rngs.active
        col.prop(rngs, 'rndsel', toggle=True)
        s = bcol.split(factor=0.3)
        s.enabled = rngs.active
        col = s.column(align=True)
        row = col.row(align=True)
        row.label(text='')
        row = col.row(align=True)
        row.alignment = 'RIGHT'
        row.label(text='Begin:')
        row = col.row(align = True)
        row.alignment = 'RIGHT'
        row.label(text='End:')
        row = col.row(align=True)
        row.alignment = 'RIGHT'
        row.label(text='Step:')
        row = col.row(align=True)
        row.alignment = 'RIGHT'
        row.label(text='Items:')
        col = s.column(align=True)
        row = col.row(align=True)
        row.label(text='Path')
        row = col.row(align=True)
        row.prop(rngs, 'rbeg', text='')
        row = col.row(align=True)
        row.prop(rngs, 'rend', text='')
        row = col.row(align=True)
        row.prop(rngs, 'rstp', text='')
        row = col.row(align=True)
        row.prop(rngs, 'ritm', text='')
        col = s.column(align=True)
        row = col.row(align=True)
        row.label(text='Profile')
        row = col.row(align=True)
        row.prop(rngs, 'pbeg', text='')
        row = col.row(align=True)
        row.prop(rngs, 'pend', text='')
        row = col.row(align=True)
        row.prop(rngs, 'pstp', text='')
        row = col.row(align=True)
        row.prop(rngs, 'pitm', text='')
        row = bcol.row(align=True)
        row.enabled = rngs.active
        row.prop(rngs, 'use_facemaps', toggle=True)


class PTDBLNPOPM_PT_ui_animode(PTDBLNPOPM_PT_ui, bpy.types.Panel):

    bl_label = "Animation"

    def draw(self, context):
        scene = context.scene
        props = scene.ptdblnpopm_props
        layout = self.layout
        layout.enabled = ( pop_mesh_valid(scene) and edit_panels_ok(props) )
        animode_on = props.animorph
        cap = 'Leave Animode' if animode_on else 'Enter Animode'
        box = layout.box()
        bcol = box.column()
        row = bcol.row()
        row.operator('ptdblnpopm.animorph_setup', text=cap).exiting=animode_on
        col = bcol.column(align=True)
        col.enabled = animode_on
        row = col.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.label(text='Action:')
        row = sc.row(align=True)
        row.label(text='Owner:')
        row = sc.row(align=True)
        row.label(text='Lerp:')
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(props, 'act_name', text='')
        row = sc.row(align=True)
        row.prop(props, 'act_owner', text='')
        row = sc.row(align=True)
        row.prop(props, 'ani_kf_type', text='')
        c = bcol.column(align=True)
        c.enabled = animode_on
        row = c.row(align=True)
        row.prop(props, 'ani_kf_start', text='')
        row.prop(props, 'ani_kf_step', text='')
        row.prop(props, 'ani_kf_loop', text='')
        row = c.row(align=True)
        s = row.split(factor=0.3, align=True)
        sc = s.column(align=True)
        sc.prop(props, 'ani_kf_iters', text='')
        sc = s.column(align=True)
        sc.operator('ptdblnpopm.anicycmirend')
        trax = props.trax
        traxidx = props.trax_idx
        nla_on = ( animode_on and bool(trax) )
        col = bcol.column(align=True)
        row = col.row(align=True)
        rc = row.column(align=True)
        rc.enabled = animode_on
        rc.operator('ptdblnpopm.ani_action', text='Add')
        rc = row.column(align=True)
        rc.enabled = nla_on
        rc.operator('ptdblnpopm.track_copy', text='Copy')
        col = col.column(align=True)
        col.enabled = nla_on
        row = col.row(align=True)
        row.template_list("PTDBLNPOPM_UL_trax", "", props, "trax", props,
                            "trax_idx", rows=2, maxrows=4)
        row = col.row(align=True)
        boo = trax[traxidx].active if nla_on else False
        c = row.column(align=True)
        c.operator('ptdblnpopm.track_enable',
                        text = 'Disable' if boo else 'Enable').doall=False
        c = row.column(align=True)
        c.operator('ptdblnpopm.track_remove', text='Remove').doall=False
        row = col.row(align=True)
        c = row.column(align=True)
        c.enabled = (len(trax) > 1)
        c.operator('ptdblnpopm.track_enable', text = 'Enable All'
                    if props.trax_disabled else 'Disable All').doall=True
        c = row.column(align=True)
        c.enabled = (len(trax) > 1)
        c.operator('ptdblnpopm.track_remove',
                        text='Remove All').doall=True
        c = col.column(align=True)
        if nla_on:
            item = trax[traxidx]
            row = c.row()
            row.enabled = item.active
            row.operator('ptdblnpopm.track_edit', text='Edit')
            box = c.box()
            box.enabled = False
            row = box.row(align=True)
            s = row.split(factor=0.6)
            sc = s.column(align=True)
            row = sc.row(align=True)
            row.label(text='Action Range:')
            row = sc.row(align=True)
            row.label(text='Action Frames:')
            row = sc.row(align=True)
            row.label(text='Strip Frames:')
            row = sc.row(align=True)
            row.label(text='Repeats:')
            row = sc.row(align=True)
            row.label(text='Scale:')
            sc = s.column(align=True)
            row = sc.row(align=True)
            row.label(text = f'{item.ac_beg} - {item.ac_end}')
            row = sc.row(align=True)
            row.label(text = f'{item.sa_beg} - {item.sa_end}')
            row = sc.row(align=True)
            row.label(text = f'{item.s_beg} - {item.s_end}')
            row = sc.row(align=True)
            row.label(text = f'{item.s_rep:.4f}')
            row = sc.row(align = True)
            row.label(text = f'{item.s_sca:.4f}')
        else:
            row = c.row(align=True)
            row.label(text='track info')


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------

classes = (
    PTDBLNPOPM_UL_plox,
    PTDBLNPOPM_UL_proflox,
    PTDBLNPOPM_UL_blpc,
    PTDBLNPOPM_UL_trax,
    PTDBLNPOPM_PT_ui_setup,
    PTDBLNPOPM_PT_ui_path_edit,
    PTDBLNPOPM_PT_ui_prof_edit,
    PTDBLNPOPM_PT_ui_blends,
    PTDBLNPOPM_PT_ui_spinroll,
    PTDBLNPOPM_PT_ui_pathlocs,
    PTDBLNPOPM_PT_ui_proflocs,
    PTDBLNPOPM_PT_ui_noise,
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
