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
import bmesh

from random import seed, randint
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


def mesh_rebuild(me, verts, faces, remove_loose_verts=False):

    bm = bmesh.new(use_operators=False)
    bmv = [bm.verts.new(v) for v in verts]
    for f in faces:
        bm.faces.new((bmv[i] for i in f))
    if remove_loose_verts:
        lvs = [v for v in bm.verts if not v.link_faces]
        for v in lvs:
            bm.verts.remove(v)
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
        raise Exception("user verts: count out of bounds!")
    if not bool(bm.edges):
        raise Exception("user verts: could not determine order!")
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
            if v != prev and v != initial:
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


def get_new_pop(pool):

    path = pool.path
    prof = pool.prof
    path.clean = path.provider != "custom" or len(path.pathed.upv) > 2
    if not path.clean:
        raise Exception("user path: not enough vertices")
    prof.clean = prof.provider != "custom" or len(prof.profed.upv) > 2
    if not prof.clean:
        raise Exception("user profile: not enough vertices")
    pop = ModData.PopEx(path.to_dct(), prof.to_dct())
    return pop


def update_rngs(rngs, rings, rpts):

    if rngs.active:
        rngs.rbeg = min(max(0, rngs.rbeg), rings - 1)
        rngs.rend = min(max(rngs.rbeg + 1, rngs.rend), rings)
        rngs.rstp = min(max(1, rngs.rstp), rings)
        rngs.ritm = min(max(1, rngs.ritm), rngs.rstp)
        rngs.pbeg = min(max(0, rngs.pbeg), rpts - 1)
        rngs.pend = min(max(rngs.pbeg + 1, rngs.pend), rpts)
        rngs.pstp = min(max(1, rngs.pstp), rpts)
        rngs.pitm = min(max(1, rngs.pitm), rngs.pstp)


def update_associations(pool, rings, rpts):

    pool.path.pathed.pathed_rings_updates(rings)
    pool.prof.profed.profed_rpts_updates(rpts)
    for item in pool.pathloc:
        item.params.params_npts_updates(rings)
    for item in pool.profloc:
        item.params.params_npts_updates(rpts)
        item.gprams.params_npts_updates(rings)
    for item in pool.blnd:
        item.blnded.profed_rpts_updates(rpts)
        item.params.params_npts_updates(rings)
    update_rngs(pool.rngs, rings, rpts)


def pop_update(pop, pool):

    spro = pool.spro
    if spro.active:
        pop.spin_rotate(spro.rot_ang, spro.spin_ang, spro.follow_limit)
    for item in pool.pathloc:
        if item.active:
            pop.path_locations(item.to_dct())
    for item in pool.blnd:
        if item.active:
            pop.add_blend_profile(item.to_dct())
    for item in pool.profloc:
        if item.active:
            pop.prof_locations(item.to_dct())
    noiz = pool.noiz
    if noiz.active:
        pop.noiz_move(noiz.vfac, noiz.p_noiz, noiz.nseed)
    locs = pop.get_locs()
    if noiz.active:
        locs = pop.noiz_locs(locs, noiz.vfac, noiz.f_noiz, noiz.nseed)
    return locs


def range_indices_update(rngs, rpts, closed, faces):

    segs = rpts if closed else rpts - 1
    rids = [
        (i + j) * segs
        for i in range(rngs.rbeg, rngs.rend, rngs.rstp)
        for j in range(rngs.ritm)
    ]
    pids = [
        x + y for x in range(rngs.pbeg, rngs.pend, rngs.pstp) for y in range(rngs.pitm)
    ]
    nfaces = len(faces)
    idx_lst = [r + p for r in rids for p in pids if r + p < nfaces]
    if rngs.invert:
        idx_lst = [i for i in range(nfaces) if i not in idx_lst]
    if rngs.rndsel:
        seed(rngs.nseed)
        idx_len = len(idx_lst)
        rfi = [randint(0, idx_len - 1) for _ in range(idx_len)]
        idx_lst = [idx_lst[i] for i in rfi]
    idx_lst = list(set(idx_lst))
    faces = [faces[i] for i in idx_lst]
    rngs.sindz["lst"] = list(set([i for f in faces for i in f]))
    return faces


def pop_mesh_update(pool, verts, faces):

    ob = pool.pop_mesh
    rngs = pool.rngs
    if rngs.active:
        profed = pool.prof.profed
        faces = range_indices_update(rngs, profed.rpts, profed.closed, faces)
    mesh_rebuild(ob.data, verts, faces, rngs.active)
    obrot = pool.obrot
    if ob.rotation_mode == "QUATERNION":
        if obrot.active:
            axis = Vector(obrot.axis).normalized()
            ob.rotation_quaternion = Quaternion(axis, obrot.rot_ang)
        else:
            ob.rotation_quaternion = (1, 0, 0, 0)
    mesh_smooth_shade(ob, pool.shade_smooth)


def scene_update(scene, setup="none"):

    pool = scene.ptdblnpopm_pool
    pop = get_new_pop(pool)
    if setup == "all":
        update_associations(pool, pop.rings, pop.rpts)
    elif setup == "range":
        update_rngs(pool.rngs, pop.rings, pop.rpts)
    if pool.pop_mesh.rotation_mode != "QUATERNION":
        pool.obrot.active = False
    verts = pop_update(pop, pool)
    faces = pop.get_faces()
    pop_mesh_update(pool, verts, faces)
