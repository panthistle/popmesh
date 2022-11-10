
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
import bmesh

from random import randint
from mathutils import Quaternion, Vector

from . import mcnst as ModCnst
from . import mdata as ModData


# ------------------------------------------------------------------------------
#
# --------------------------- ANIMATION ----------------------------------------

def action_remove(action):

    if action:
        fcs = [fc for fc in action.fcurves]
        for fc in fcs:
            action.fcurves.remove(fc)
        bpy.data.actions.remove(action)


def nla_track_remove(ob, track_name):

    track = ob.animation_data.nla_tracks.get(track_name)
    if track:
        ns = []
        for strip in track.strips:
            action_remove(strip.action)
            ns.append(strip)
        for s in ns:
            track.strips.remove(s)
        ob.animation_data.nla_tracks.remove(track)


def nla_track_remove_all(ob):

    nt = []
    for track in ob.animation_data.nla_tracks:
        nt.append(track)
        ns = []
        for strip in track.strips:
            action_remove(strip.action)
            ns.append(strip)
        for s in ns:
            track.strips.remove(s)
    for t in nt:
        ob.animation_data.nla_tracks.remove(t)


def anim_data_remove(ob):

    if ob.animation_data:
        nla_track_remove_all(ob)
        action_remove(ob.animation_data.action)
        ob.animation_data_clear()


# ------------------------------------------------------------------------------
#
# ------------------------------ MESH ------------------------------------------

def mesh_update_bmesh(me, verts, faces):

    bm = bmesh.new(use_operators=False)
    bmv = [bm.verts.new(v) for v in verts]
    for f in faces:
        bm.faces.new((bmv[i] for i in f))
    bm.to_mesh(me)
    me.update()
    bm.free()


def mesh_smooth_normals(ob, toggle=False):

    ob.data.use_auto_smooth = toggle


def mesh_smooth_shade(ob, toggle=False):

    me = ob.data
    smooth_lst = [toggle] * len(me.polygons)
    me.polygons.foreach_set("use_smooth", smooth_lst)
    me.update()


def mesh_show_wire(ob, toggle=False):

    ob.show_wire = toggle


def user_mesh_verts(me):

    bm = bmesh.new(use_operators=False)
    bm.from_mesh(me)
    pts = len(bm.verts)
    if pts < 3 or pts > ModCnst.MAX_SEGS:
        raise Exception('user verts: count out of bounds!')
    if not bool(bm.edges):
        raise Exception('user verts: could not determine order!')
    initial = None
    if not bool(bm.faces):
        for v in bm.verts:
            if len(v.link_edges) == 1:
                initial = v
                break
    bm.verts.ensure_lookup_table()
    if not initial:
        initial = bm.verts[0]
    vert = initial
    prev = None
    for i in range(pts):
        vert.index = i
        next = None
        for v in [e.other_vert(vert) for e in vert.link_edges]:
            if (v != prev and v != initial):
                next = v
        if next == None:
            break
        prev, vert = vert, next
    bm.verts.sort()
    verts = [v.co for v in bm.verts]
    bm.free()
    return verts


# ------------------------------------------------------------------------------
#
# ------------------------- SCENE UPDATES --------------------------------------

def get_new_pop(props):

    path = props.path
    prof = props.prof
    # check user verts
    path.clean = (path.provider != 'custom' or len(path.upv) > 2)
    if not path.clean:
        raise Exception('user path: not enough vertices')
    prof.clean = (prof.provider != 'custom' or len(prof.upv) > 2)
    if not prof.clean:
        raise Exception('user profile: not enough vertices')
    pop = ModData.PopEx(path.to_dct(), prof.to_dct())
    path.closed = pop.path_closed
    prof.closed = pop.profile_closed
    path.rings = pop.rings
    prof.rpts = pop.rpts
    return pop


def update_deps_range(rngs, rings, rpts):

    if rngs.active:
        rngs.rbeg = min(max(0, rngs.rbeg), rings - 1)
        rngs.rend = min(max(rngs.rbeg + 1, rngs.rend), rings)
        rngs.rstp = min(max(1, rngs.rstp), rings)
        rngs.ritm = min(max(1, rngs.ritm), rngs.rstp)
        rngs.pbeg = min(max(0, rngs.pbeg), rpts - 1)
        rngs.pend = min(max(rngs.pbeg + 1, rngs.pend), rpts)
        rngs.pstp = min(max(1, rngs.pstp), rpts)
        rngs.pitm = min(max(1, rngs.pitm), rngs.pstp)
    else:
        rngs.use_facemaps = False


def update_deps_params(ob, items):

    if ob.idx > items - 1:
        ob.idx = items - 1
    if ob.itm > items:
        ob.itm = items
    if ob.reps > items:
        ob.reps = items
    if ob.gap > items:
        ob.gap = items


def update_dependencies(props):

    path = props.path
    rings = path.rings
    mp_rings = int(rings / 2)

    prof = props.prof
    rpts = prof.rpts
    mp_rpts = int(rpts / 2)

    # path
    if path.idx > rings - 1:
        path.idx = rings - 1
    if path.bump > mp_rings:
        path.bump = mp_rings
    # profile
    if prof.idx > rpts - 1:
        prof.idx = rpts - 1
    if prof.bump > mp_rpts:
        prof.bump = mp_rpts
    # plox
    for item in props.plox:
        update_deps_params(item.params, rings)
    # proflox
    for item in props.proflox:
        update_deps_params(item.params, rpts)
        update_deps_params(item.gprams, rings)
    # blends
    for item in props.blpc:
        if item.idx_off > rpts - 1:
            item.idx_off = rpts - 1
        if item.bump > mp_rpts:
            item.bump = mp_rpts
        update_deps_params(item.params, rings)
    # ranges
    update_deps_range(props.rngs, rings, rpts)


def pop_update(pop, props):

    spro = props.spro
    if spro.active:
        pop.spin_rotate(spro.rot_ang, spro.spin_ang, spro.follow_limit)
    for item in props.plox:
        if item.active:
            pop.path_locations(item.to_dct())
    for item in props.blpc:
        if item.active:
            pop.add_blend_profile(item.to_dct())
    for item in props.proflox:
        if item.active:
            pop.prof_locations(item.to_dct())
    noiz = props.noiz
    if noiz.active:
        pop.noise_move(noiz.vfac, noiz.p_noise, noiz.nseed)
    locs = pop.get_locs()
    if noiz.active:
        locs = pop.noise_locs(locs, noiz.vfac, noiz.f_noise, noiz.nseed)
    return locs


def sel_range_list(props, count):

    rngs = props.rngs
    rbeg, rend, rstp, ritm = rngs.rbeg, rngs.rend, rngs.rstp, rngs.ritm
    pbeg, pend, pstp, pitm = rngs.pbeg, rngs.pend, rngs.pstp, rngs.pitm
    segs = props.prof.rpts if props.prof.closed else props.prof.rpts - 1
    rids = [(i + j) * segs for i in range(rbeg, rend, rstp)
            for j in range(ritm)]
    pids = [x + y for x in range(pbeg, pend, pstp) for y in range(pitm)]
    idx = [r + p for r in rids for p in pids if r + p < count]
    if rngs.invert:
        idx = [i for i in range(count) if i not in idx]
    if rngs.rndsel:
        idx_len = len(idx)
        rfi = [randint(0, idx_len - 1) for _ in range(idx_len)]
        idx = [idx[i] for i in rfi]
    return list(set(idx))


def pop_mesh_update(props, verts, faces):

    ob = props.pop_mesh
    ob.face_maps.clear()
    sel_faces = faces
    idsrng = list(range(len(faces)))
    if props.rngs.active:
        idsrng = sel_range_list(props, len(faces))
        if not props.rngs.use_facemaps:
            sel_faces = [faces[idx] for idx in idsrng]
    mesh_update_bmesh(ob.data, verts, sel_faces)
    if props.rngs.use_facemaps:
        fm = ob.face_maps.new()
        fm.add(idsrng)
    obrot = props.obrot
    if ob.rotation_mode == 'QUATERNION':
        if obrot.active:
            axis = Vector(obrot.axis).normalized()
            ob.rotation_quaternion = Quaternion(axis, obrot.rot_ang)
        else:
            ob.rotation_quaternion = (1, 0, 0, 0)
    mesh_smooth_shade(ob, props.shade_smooth)


def scene_update(scene, setup='none'):

    props = scene.ptdblnpopm_props
    pop = get_new_pop(props)
    # update dependent properties
    props.callbacks = False
    if setup == 'all':
        update_dependencies(props)
    elif setup == 'range':
        update_deps_range(props.rngs, props.path.rings, props.prof.rpts)
    if props.pop_mesh.rotation_mode != 'QUATERNION':
        props.obrot.active = False
    props.callbacks = True
    # update mesh
    verts = pop_update(pop, props)
    faces = pop.get_faces()
    pop_mesh_update(props, verts, faces)
