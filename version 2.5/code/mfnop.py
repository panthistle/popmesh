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

from random import seed, randint


# ------------------------------------------------------------------------------
#
# ------------------------- BMOPS OPERATOR FUNCTIONS ---------------------------


def validate_scene_object(scene, ob):
    if ob and (ob.name not in scene.objects):
        bpy.data.objects.remove(ob)


def get_new_mesh(scene):
    name = "pop_mesh"
    me = bpy.data.meshes.new(name)
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


file_excluded_attributes = {
    "clean",
    "user_ob",
    "pathloc_idx",
    "profloc_idx",
    "blnd_idx",
    "trax",
    "trax_idx",
    "update_ok",
    "animorph",
    "act_name",
    "pop_mesh",
    "replace_mesh",
    "show_warn",
    "show_wire",
    "auto_smooth",
    "shade_smooth",
    "anicalc",
}


def setts_to_json(pg):
    d = {}
    vecprops = [bpy.props.IntVectorProperty, bpy.props.FloatVectorProperty]
    for key in pg.__annotations__.keys():
        if key in file_excluded_attributes:
            continue
        prop_type = pg.__annotations__[key].function
        if prop_type == bpy.props.PointerProperty:
            d[key] = setts_to_json(getattr(pg, key))
        elif prop_type == bpy.props.CollectionProperty:
            d[key] = [setts_to_json(i) for i in getattr(pg, key)]
        elif prop_type in vecprops:
            d[key] = list(getattr(pg, key))
        else:
            d[key] = getattr(pg, key)
    return d


def json_to_setts(d, pg):
    for key in d.keys():
        if (key not in pg.__annotations__.keys()) or (key in file_excluded_attributes):
            continue
        prop_type = pg.__annotations__[key].function
        if prop_type == bpy.props.PointerProperty:
            json_to_setts(d[key], getattr(pg, key))
        elif prop_type == bpy.props.CollectionProperty:
            sub_d = d[key]
            sub_pg = getattr(pg, key)
            if key == "upv":
                for k in sub_d:
                    el = sub_pg.add()
                    json_to_setts(k, el)
            else:
                iname = f"{key}_idx"
                for k in sub_d:
                    el = sub_pg.add()
                    json_to_setts(k, el)
                setattr(pg, iname, len(sub_pg) - 1)
        else:
            setattr(pg, key, d[key])


def anicalc_factors(val):
    return set(
        f for i in range(1, int(val**0.5) + 1) if not val % i for f in (i, val // i)
    )


def aniact_fac_list(mirror, cycles, loop):

    def linear_list(dt, m, cnt):
        if not m:
            return [dt * i for i in range(cnt)]
        dt2 = 2 * dt
        return [dt2 * i if (dt * i) < 0.5 else 2 - dt2 * i for i in range(cnt)]

    if not mirror:
        return linear_list(1 / (loop - 1), False, loop)
    cycles = min(loop // 2, cycles)
    grp = loop // cycles
    odd_grp = bool(grp % 2)
    div = grp - 1 if (odd_grp or cycles == 1) else grp
    lst = linear_list(1 / div, True, grp)
    if loop > grp:
        m = loop // div + 1
        l2 = lst[1:] if odd_grp else lst[1:] + lst[:1]
        lst = lst[:1] + l2 * m
    return [lst[i] for i in range(loop)]


def aniact_path_edit_dict(path, loop):
    d = {}
    adim = path.ani_dim
    dim_mirr = path.ani_dim_mirror.active
    dim_cycl = path.ani_dim_mirror.cycles

    def path_dim_list(pdim, anpdim):
        if not adim:
            return [pdim] * loop
        lst = aniact_fac_list(dim_mirr, dim_cycl, loop)
        return [[v1 + (v2 - v1) * i for v1, v2 in zip(pdim, anpdim)] for i in lst]

    def path_value_list(flag, v1, v2, m, c):
        if not flag or (v1 == v2):
            return [v1] * loop
        lst = aniact_fac_list(m, c, loop)
        diff = v2 - v1
        return [v1 + diff * i for i in lst]

    p_n = path.provider
    if p_n == "custom":
        d["dim"] = path_dim_list(path.pathed.cust_dim, path.ani_dim_3d)
        return d
    if p_n == "polygon":
        d["dim"] = path_dim_list(path.pathed.pol_dim, path.ani_dim_2d)
        return d
    afac = path.ani_fac
    fac_mirr = path.ani_fac_mirror.active
    fac_cycl = path.ani_fac_mirror.cycles
    if p_n == "line":
        d["dim"] = path_value_list(
            adim, path.pathed.lin_dim, path.ani_lin_dim, dim_mirr, dim_cycl
        )
        d["fac"] = path_value_list(
            afac, path.pathed.lin_exp, path.ani_lin_exp, fac_mirr, fac_cycl
        )
        return d
    if p_n == "arc":
        d["dim"] = path_value_list(
            adim, path.pathed.arc_dim, path.ani_arc_dim, dim_mirr, dim_cycl
        )
        d["fac"] = path_value_list(
            afac, path.pathed.arc_fac, path.ani_arc_fac, fac_mirr, fac_cycl
        )
        return d
    if p_n == "spiral":
        d["dim"] = path_value_list(
            adim, path.pathed.spi_dim, path.ani_spi_dim, dim_mirr, dim_cycl
        )
        d["fac"] = path_value_list(
            afac, path.pathed.spi_revs, path.ani_spi_revs, fac_mirr, fac_cycl
        )
        return d
    if p_n == "ellipse":
        d["dim"] = path_dim_list(path.pathed.ell_dim, path.ani_dim_2d)
        d["fac"] = path_value_list(
            afac, path.pathed.ellstep_val, path.ani_ellstep_val, fac_mirr, fac_cycl
        )
        return d
    afac2 = path.ani_fac2
    fac2_mirr = path.ani_fac2_mirror.active
    fac2_cycl = path.ani_fac2_mirror.cycles
    afac3 = path.ani_fac3
    fac3_mirr = path.ani_fac3_mirror.active
    fac3_cycl = path.ani_fac3_mirror.cycles
    if p_n == "wave":
        d["dim"] = path_value_list(
            adim, path.pathed.wav_dim, path.ani_wav_dim, dim_mirr, dim_cycl
        )
        d["fac"] = path_value_list(
            afac, path.pathed.wav_amp, path.ani_wav_amp, fac_mirr, fac_cycl
        )
        d["fac2"] = path_value_list(
            afac2, path.pathed.wav_frq, path.ani_wav_frq, fac2_mirr, fac2_cycl
        )
        d["fac3"] = path_value_list(
            afac3, path.pathed.wav_pha, path.ani_wav_pha, fac3_mirr, fac3_cycl
        )
        return d
    afac4 = path.ani_fac4
    fac4_mirr = path.ani_fac4_mirror.active
    fac4_cycl = path.ani_fac4_mirror.cycles
    d["dim"] = path_dim_list(path.pathed.hel_dim, path.ani_dim_2d)
    d["fac"] = path_value_list(
        afac, path.pathed.hel_len, path.ani_hel_len, fac_mirr, fac_cycl
    )
    d["fac2"] = path_value_list(
        afac2, path.pathed.hel_fac, path.ani_hel_fac, fac2_mirr, fac2_cycl
    )
    d["fac3"] = path_value_list(
        afac3, path.pathed.hel_stp, path.ani_hel_stp, fac3_mirr, fac3_cycl
    )
    d["fac4"] = path_value_list(
        afac4, path.pathed.hel_pha, path.ani_hel_pha, fac4_mirr, fac4_cycl
    )
    return d


def aniact_prof_edit_dict(prof, loop):
    d = {}
    adim = prof.ani_dim
    dim_mirr = prof.ani_dim_mirror.active
    dim_cycl = prof.ani_dim_mirror.cycles

    def prof_seq_list(pdim):
        if not adim:
            return [pdim] * loop
        lst = aniact_fac_list(dim_mirr, dim_cycl, loop)
        anpdim = prof.ani_epc_dim
        return [[v1 + (v2 - v1) * i for v1, v2 in zip(pdim, anpdim)] for i in lst]

    def prof_value_list(flag, v1, v2, m, c):
        if not flag or (v1 == v2):
            return [v1] * loop
        lst = aniact_fac_list(m, c, loop)
        diff = v2 - v1
        return [v1 + diff * i for i in lst]

    p_n = prof.provider
    if p_n == "custom":
        d["dim"] = prof_seq_list(prof.profed.cust_dim)
        return d
    if p_n == "polygon":
        d["dim"] = prof_seq_list(prof.profed.pol_dim)
        return d
    afac = prof.ani_fac
    fac_mirr = prof.ani_fac_mirror.active
    fac_cycl = prof.ani_fac_mirror.cycles
    if p_n == "line":
        d["dim"] = prof_value_list(
            adim, prof.profed.lin_dim, prof.ani_lin_dim, dim_mirr, dim_cycl
        )
        d["fac"] = prof_value_list(
            afac, prof.profed.lin_exp, prof.ani_lin_exp, fac_mirr, fac_cycl
        )
        return d
    if p_n == "arc":
        d["dim"] = prof_value_list(
            adim, prof.profed.arc_dim, prof.ani_arc_dim, dim_mirr, dim_cycl
        )
        d["fac"] = prof_value_list(
            afac, prof.profed.arc_fac, prof.ani_arc_fac, fac_mirr, fac_cycl
        )
        return d
    if p_n == "ellipse":
        d["dim"] = prof_seq_list(prof.profed.ell_dim)
        d["fac"] = prof_value_list(
            afac, prof.profed.ellstep_val, prof.ani_ellstep_val, fac_mirr, fac_cycl
        )
        return d
    afac2 = prof.ani_fac2
    fac2_mirr = prof.ani_fac2_mirror.active
    fac2_cycl = prof.ani_fac2_mirror.cycles
    afac3 = prof.ani_fac3
    fac3_mirr = prof.ani_fac3_mirror.active
    fac3_cycl = prof.ani_fac3_mirror.cycles
    d["dim"] = prof_value_list(
        adim, prof.profed.wav_dim, prof.ani_wav_dim, dim_mirr, dim_cycl
    )
    d["fac"] = prof_value_list(
        afac, prof.profed.wav_amp, prof.ani_wav_amp, fac_mirr, fac_cycl
    )
    d["fac2"] = prof_value_list(
        afac2, prof.profed.wav_frq, prof.ani_wav_frq, fac2_mirr, fac2_cycl
    )
    d["fac3"] = prof_value_list(
        afac3, prof.profed.wav_pha, prof.ani_wav_pha, fac3_mirr, fac3_cycl
    )
    return d


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

    offset = inst.offset
    if not (inst.active and offset):
        return [idx] * loop
    if inst.offrnd:
        return anim_ids_rnd(idx, offset, inst.beg, inst.stp, inst.offrndseed, loop)
    return anim_ids(idx, offset, inst.beg, inst.stp, loop)


def aniact_collval_list(inst, loop):
    v1 = inst.fac
    v2 = inst.ani_fac.fac
    if not inst.ani_fac.active or (v1 == v2):
        return [v1] * loop
    lst = aniact_fac_list(inst.ani_fac.mirror.active, inst.ani_fac.mirror.cycles, loop)
    diff = v2 - v1
    return [v1 + diff * i for i in lst]


def aniact_edvals_dict(coll, loop, twodim=False):
    d = {"dcts": [], "nids": [], "ams": []}
    if twodim:
        d["ids"] = []
    for item in coll:
        if item.active:
            d["dcts"].append(item.to_dct())
            d["nids"].append(
                aniact_index_offset_list(item.ani_nidx, item.nprams.idx, loop)
            )
            if twodim:
                d["ids"].append(
                    aniact_index_offset_list(item.ani_idx, item.iprams.idx, loop)
                )
            d["ams"].append(aniact_collval_list(item, loop))
    return d


def aniact_blndval_list(inst, loop):
    v1 = inst.fac
    v2 = inst.ani_fac_val
    if not inst.ani_fac or (v1 == v2):
        return [v1] * loop
    lst = aniact_fac_list(inst.ani_fac_mirror.active, inst.ani_fac_mirror.cycles, loop)
    diff = v2 - v1
    return [v1 + diff * i for i in lst]


def aniact_blendvals_dict(coll, loop):
    d = {"dcts": [], "ids": [], "nids": [], "ams": []}
    for item in coll:
        if item.active:
            d["dcts"].append(item.to_dct())
            d["ids"].append(
                aniact_index_offset_list(item.ani_idx, item.iprams.idx, loop)
            )
            d["nids"].append(
                aniact_index_offset_list(item.ani_nidx, item.nprams.idx, loop)
            )
            d["ams"].append(aniact_blndval_list(item, loop))
    return d


def aniact_rotation_list(inst, loop):
    fac = inst.fac
    beg = inst.beg
    end = inst.end
    angs = [0 if beg > i else fac for i in range(loop)]
    if end > beg and end < loop:
        d = loop - end
        angs[end:] = [0] * d
    return angs


def aniact_noiz_list(noiz, loop):

    def bln_val_list(amp, beg, end, stp, loop):
        beg = 0 if beg < 2 else beg
        end = 0 if end < 2 else end
        vals = []
        if beg > 0:
            beg = min(loop, beg)
            v = amp / (beg - 1)
            vals += [v * i for i in range(beg)]
        rng = loop - beg
        if rng > 0:
            end = min(rng, end)
            if rng > end:
                rng -= end
                v = amp
                ct = 0
                for i in range(rng):
                    vals.append(v)
                    ct += 1
                    if ct == stp:
                        v = 0 if v == amp else amp
                        ct = 0
            if end > 0:
                v2 = vals[-1]
                v = -v2 / end
                vals += [v2 + v * i for i in range(1, end)] + [0]
        return vals

    amp = noiz.ampli
    if not (noiz.ani_noiz and amp):
        return [amp] * loop
    return bln_val_list(amp, noiz.ani_blin, noiz.ani_blout, noiz.ani_stp, loop)


def aniact_fcurve_create(action, dp, di, fls, vls, kls, loop):
    fc = action.fcurves.new(data_path=dp, index=di)
    fc.keyframe_points.add(count=loop)
    fc.keyframe_points.foreach_set("co", [i for fv in zip(fls, vls) for i in fv])
    fc.keyframe_points.foreach_set("interpolation", kls)


def aniact_nla_track_add(mesh_data, action):
    name = action.name
    track = mesh_data.animation_data.nla_tracks.new()
    track.name = name
    start = int(action.frame_range[0])
    strip = track.strips.new(name, start, action)
    strip.blend_type = "REPLACE"
    strip.use_auto_blend = False
    strip.blend_in = 0
    strip.blend_out = 0
    strip.extrapolation = "HOLD"
