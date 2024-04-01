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
import bmesh

from random import seed, randint, uniform

from . import mdata as ModDATA


# ------------------------------------------------------------------------------
#
# ----------------------- USER OBJECT VERTS ------------------------------------


def user_mesh_verts(me):
    bm = bmesh.new(use_operators=False)
    bm.from_mesh(me)
    pts = len(bm.verts)
    if pts < 3:
        raise Exception("not enough vertices!")
    if not bm.edges:
        raise Exception("could not determine vertex order!")
    initial = None
    if not bm.faces:
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
# --------------------- RANDOM INDEX ANIMATION UPDATES -------------------------


def aniact_index_offset_list(inst, idx, loop):
    def anim_ids(base, inc, beg, stp, loop):
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

    def anim_ids_rnd(base, inc, beg, stp, rndseed, loop):
        beg = min(loop, beg)
        ids = [base] * beg
        if loop > beg:
            d = loop - beg
            seed(rndseed)
            val = randint(base - inc, base + inc)
            ct = 0
            for i in range(d - 1):
                ids.append(val)
                ct += 1
                if ct == stp:
                    val = randint(base - inc, base + inc)
                    ct = 0
            ids.append(base)
        return ids

    if not inst.active:
        return [idx] * loop
    if inst.offrnd:
        return anim_ids_rnd(idx, inst.offset, inst.beg, inst.stp, inst.offrndseed, loop)
    return anim_ids(idx, inst.offset, inst.beg, inst.stp, loop)


# ------------------------------------------------------------------------------
#
# ------------------------- SCENE UPDATES --------------------------------------


def noiz_locs(locs, axis, amp, ns):
    if not amp:
        return locs
    val = sum(1 if i else 0 for i in axis)
    if not val:
        return locs
    seed(ns)
    npts = len(locs)
    for j, fac in enumerate(axis):
        if fac:
            for i in range(npts):
                locs[i][j] += fac * uniform(-amp, amp)
    return locs


def new_pop_instance(pool):
    path = pool.path
    path.clean = (path.provider != "custom") or (len(path.pathed.upv) > 2)
    if not path.clean:
        raise Exception("user path, not enough vertices!")
    prof = pool.prof
    prof.clean = (prof.provider != "custom") or (len(prof.profed.upv) > 2)
    if not prof.clean:
        raise Exception("user profile, not enough vertices!")
    return ModDATA.PopEx(pool.to_dct(), path.to_dct(), prof.to_dct())


def update_prof_dependents(pool, rpts):
    pool.prof.profed.npts = rpts
    for item in pool.profloc:
        item.iprams.npts = rpts
    for item in pool.blnd:
        item.blnded.npts = rpts
        item.iprams.npts = rpts


def update_path_dependents(pool, rings):
    pool.path.pathed.npts = rings
    for item in pool.pathloc:
        item.nprams.npts = rings
    for item in pool.profloc:
        item.nprams.npts = rings
    for item in pool.blnd:
        item.nprams.npts = rings


def update_all_dependents(pool, rings, rpts):
    pool.path.pathed.npts = rings
    pool.prof.profed.npts = rpts
    for item in pool.pathloc:
        item.nprams.npts = rings
    for item in pool.profloc:
        item.iprams.npts = rpts
        item.nprams.npts = rings
    for item in pool.blnd:
        item.blnded.npts = rpts
        item.iprams.npts = rpts
        item.nprams.npts = rings


def pop_update(pop, pool):
    pgi = pool.meshrot
    if pgi.active:
        pop.mesh_rotate(pgi.axis, pgi.angle, pgi.pivot)
    pgi = pool.pathrot
    if pgi.active:
        pop.path_rotate(pgi.axis, pgi.angle, pgi.pivot, pgi.piv_object, pgi.batt)
    pgi = pool.profrot
    if pgi.active:
        pop.prof_rotate(pgi.roll)
    for item in pool.pathloc:
        if item.active:
            pop.path_locations(item.to_dct())
    for item in pool.blnd:
        if item.active:
            pop.prof_blend(item.to_dct())
    for item in pool.profloc:
        if item.active:
            pop.prof_locations(item.to_dct())


def mesh_rebuild(me, verts, faces, smooth, remove_loose_verts=False):
    flat = not smooth
    tmp_me = bpy.data.meshes.new("tmp_me")
    tmp_me.from_pydata(verts, [], faces, shade_flat=flat)
    bm = bmesh.new(use_operators=False)
    bm.from_mesh(tmp_me)
    if remove_loose_verts:
        lvs = [v for v in bm.verts if not v.link_faces]
        for v in lvs:
            bm.verts.remove(v)
    bm.to_mesh(me)
    bm.free()
    me.update()
    bpy.data.meshes.remove(tmp_me)


def rngids_calc(npts, k, itm, gap, reps):
    ids = [i % npts for i in range(k, k + itm)]
    if (npts == itm) or (reps < 2):
        return ids
    iinc = gap + 1
    for i in range(reps - 1):
        k = ids[-1] + iinc
        ids += [j % npts for j in range(k, k + itm)]
    return ids[:npts]


def range_indices_update(rngs, rings, rpts, faces):
    rngs.rbeg = rngs.rbeg % rings
    rngs.ritm = min(rngs.ritm, rings)
    rngs.rgap = min(rngs.rgap, rings - rngs.ritm)
    grp = rngs.ritm + rngs.rgap
    hi = rings // grp
    hi += 0 if rings % grp < rngs.ritm else 1
    rngs.rstp = min(rngs.rstp, hi)
    rids = rngids_calc(rings, rngs.rbeg, rngs.ritm, rngs.rgap, rngs.rstp)
    rngs.pbeg = rngs.pbeg % rpts
    rngs.pitm = min(rngs.pitm, rpts)
    rngs.pgap = min(rngs.pgap, rpts - rngs.pitm)
    grp = rngs.pitm + rngs.pgap
    hi = rpts // grp
    hi += 0 if rpts % grp < rngs.pitm else 1
    rngs.pstp = min(rngs.pstp, hi)
    pids = rngids_calc(rpts, rngs.pbeg, rngs.pitm, rngs.pgap, rngs.pstp)
    inds = [r * rpts + p for r in rids for p in pids]
    nfaces = len(faces)
    if rngs.invert:
        inds_set = set(inds)
        inds = [i for i in range(nfaces) if i not in inds_set]
    if rngs.rndsel:
        seed(rngs.nseed)
        inds_len = len(inds)
        rfi = [randint(0, inds_len - 1) for _ in range(inds_len)]
        inds = [inds[i] for i in rfi]
    inds_set = set(i for i in inds if i < nfaces)
    faces = [faces[i] for i in inds_set]
    rngs.sindz_set(set(i for f in faces for i in f))
    return faces


def pop_mesh_update(pool, verts, rings, rpts, faces):
    ob = pool.pop_mesh
    rngs = pool.rngs
    if rngs.active:
        if not pool.path.pathed.closed:
            rings = rings + 1 if pool.path.pathed.endcaps else rings - 1
        rpts = rpts if pool.prof.profed.closed else rpts - 1
        faces = range_indices_update(rngs, rings, rpts, faces)
    mesh_rebuild(ob.data, verts, faces, pool.shade_smooth, rngs.active)


def scene_update(scene, setup="none"):
    pool = scene.ptdblnpopm_pool
    pop = new_pop_instance(pool)
    rings = pop.rings
    rpts = pop.rpts
    if setup == "all":
        update_all_dependents(pool, rings, rpts)
    elif setup == "path":
        update_path_dependents(pool, rings)
    elif setup == "prof":
        update_prof_dependents(pool, rpts)
    pop_update(pop, pool)
    verts = pop.get_locs()
    if pool.noiz.active:
        verts = noiz_locs(verts, pool.noiz.vfac, pool.noiz.ampli, pool.noiz.nseed)
    faces = pop.get_faces()
    pop_mesh_update(pool, verts, rings, rpts, faces)
