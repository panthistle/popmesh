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


import math

from mathutils import Quaternion, Vector

from . import mpath as ModPATH


# ------------------------------------------------------------------------------
#
# ---------------------------- POPEX HELPERS -----------------------------------


def falloff_lists(npts, dct):
    itm = dct["itm"]
    reps = dct["reps"]
    k = dct["idx"]
    repfoff = dct["repfoff"]
    foffstp = dct["repfstp"]
    mir = dct["mir"]
    iinc = dct["gap"] + 1
    ditm = itm
    dstp = 1
    if dct["rev"]:
        iinc = -iinc
        ditm = -itm
        dstp = -1

    i_lst = [i % npts for i in range(k, k + ditm, dstp)]
    if (itm == 1) or (dct["ease"] == "OFF"):
        v_lst = [1] * itm
    else:
        div = itm if dct["cyc"] else itm - 1
        v_lst = ModPATH.it_list(dct["ease"], 1 / div, dct["exp"], mir, itm)
        sref = dct["reflect"]
        if sref == "3":
            v_lst = [i if i >= 0.5 else 1 - i for i in v_lst]
        elif sref == "2":
            v_lst = [i if i <= 0.5 else 1 - i for i in v_lst]
        elif sref == "1":
            v_lst = [1 - i for i in v_lst]
    if (npts == itm) or (reps == 1):
        return i_lst, v_lst
    tlst = v_lst.copy()
    if foffstp > 1:
        fct = 1
        for i in range(reps - 1):
            foff = 1
            fct += 1
            if fct > foffstp:
                fct = 1
                foff = repfoff
            k = i_lst[-1] + iinc
            i_lst += [j % npts for j in range(k, k + ditm, dstp)]
            tlst = [foff * j for j in tlst]
            v_lst += tlst
        return i_lst[:npts], v_lst[:npts]
    for i in range(reps - 1):
        k = i_lst[-1] + iinc
        i_lst += [j % npts for j in range(k, k + ditm, dstp)]
        tlst = [repfoff * j for j in tlst]
        v_lst += tlst
    return i_lst[:npts], v_lst[:npts]


def path_rots(locs, dv, cyclic):
    if cyclic:
        l2 = locs[-1]
        locs.append(locs[0])
    else:
        l2 = locs[0] + (locs[0] - locs[1])
        locs.append(locs[-1] + (locs[-1] - locs[-2]))
    a = locs[1] - l2
    if isinstance(dv, str):
        rots = [a.to_track_quat("Z", dv)]
        for i in range(1, len(locs) - 1):
            rots.append((locs[i + 1] - locs[i - 1]).to_track_quat("Z", dv))
    else:
        rots = [dv.rotation_difference(a)]
        for i in range(1, len(locs) - 1):
            b = locs[i + 1] - locs[i - 1]
            rots.append(a.rotation_difference(b) @ rots[-1])
            a = b
    locs.pop()
    return rots


def gscan_cl(pts, lines):
    def sgen():
        for j in range(lines):
            loop = j * pts
            for i in range(pts):
                yield i + loop
            yield loop

    s = sgen()
    return tuple(s)


def gfaces(pts, lines, scan):
    return [
        (
            scan[i + j * pts],
            scan[i + 1 + j * pts],
            scan[i + pts + 1 + j * pts],
            scan[i + pts + j * pts],
        )
        for j in range(lines - 1)
        for i in range(pts - 1)
    ]


# ------------------------------------------------------------------------------
#
# ----------------------------- POP CLASS --------------------------------------


class PopEx:
    """path-on-path class"""

    _tau = 2 * math.pi
    _hpi = 0.5 * math.pi
    _eps = 1e-5

    def __init__(self, path_dct, prof_dct):
        self.meshrot_active = False
        self.pathrot_active = False
        self._z_axis = Vector((0, 0, 1))
        self._path = getattr(ModPATH, path_dct["provider"].capitalize())()
        self.modify_path(path_dct)
        self._profile = getattr(ModPATH, prof_dct["provider"].capitalize())()
        self.modify_profile(prof_dct)

    # RESET

    def reset_pathlocs(self):
        self._pathlocs = []

    def reset_proflocs(self):
        self._proflocs = []

    def reset_profrots(self):
        self._profrots = []
        self._twistang = 0
        self._follow_limit = True

    # MODIFY

    def _pathlocs_get(self):
        return [loc.copy() for loc in self._pathstore]

    def _proflocs_get(self):
        if self._prof_align_angle:
            q = Quaternion(self._z_axis, self._prof_align_angle)
            locs = [q @ loc for loc in self._profstore]
            return [[loc.copy() for loc in locs] for _ in range(self._path.npts)]
        return [[loc.copy() for loc in self._profstore] for _ in range(self._path.npts)]

    def modify_path(self, dct):
        dct["reverse"] = False
        self._path.update(dct)
        self._endcaps = dct["endcaps"]
        self._pathupfixed = dct["upfixed"]
        self._pathupaxis = dct["upaxis"]
        self.reset_pathlocs()
        self._pathstore = self._path.get_locs()

    def modify_profile(self, dct):
        self._profile.update(dct)
        self._prof_align_angle = dct["rot_align"]
        self.reset_proflocs()
        self.reset_profrots()
        self._profstore = self._profile.get_locs()

    def prof_blend(self, dct):
        if not dct["fac"]:
            return
        provider = dct["provider"]
        bln_prof = getattr(ModPATH, provider.capitalize())()
        rpts = self._profile.npts
        dct[f"res_{provider[:3]}"] = rpts
        dct["closed"] = self._profile.closed
        bln_prof.update(dct)
        blocs = bln_prof.get_locs()
        if dct["rot_align"]:
            q = Quaternion(self._z_axis, dct["rot_align"])
            blocs = [q @ loc for loc in blocs]
        if not self._proflocs:
            self._proflocs = self._proflocs_get()
        nids, nfvs = falloff_lists(self._path.npts, dct["nprams"])
        ids, fvs = falloff_lists(rpts, dct["iprams"])
        fac = dct["fac"]
        for i, f in zip(nids, nfvs):
            if not f:
                continue
            df = fac * f
            for j, p in zip(ids, fvs):
                if not p:
                    continue
                dv = (blocs[j] - self._proflocs[i][j]) * (df * p)
                self._proflocs[i][j] += dv

    def mesh_rotate(self, axis, angle, pivot):
        self._meshaxis = axis
        self._meshpivot = Vector(pivot)
        self._meshrot = Quaternion(axis, angle)

    def path_rotate(self, axis, angle):
        self._pathaxis = axis
        self._pathrot = Quaternion(axis, angle)

    def prof_rotate(self, roll, twist, follow_limit):
        rings = self._path.npts
        self._twistang = twist
        self._follow_limit = follow_limit
        axis = self._z_axis
        if not twist:
            self._profrots = [Quaternion(axis, roll)] * rings
            return
        div = rings if self._path.closed else rings - 1
        dt = twist / div
        self._profrots = [Quaternion(axis, roll + dt * i) for i in range(rings)]

    def path_locations(self, dct):
        fac = dct["fac"]
        if not fac:
            return
        axis = Vector(dct["axis"])
        if not axis.length:
            return
        axis *= fac
        if not self._pathlocs:
            self._pathlocs = self._pathlocs_get()
        nids, nfvs = falloff_lists(self._path.npts, dct["nprams"])
        if dct["abs_move"]:
            for i, f in zip(nids, nfvs):
                if not f:
                    continue
                self._pathlocs[i] += axis * f
        else:
            for i, f in zip(nids, nfvs):
                if not f:
                    continue
                dv = self._pathstore[i].normalized()
                for j in range(3):
                    self._pathlocs[i][j] += dv[j] * axis[j] * f

    def prof_locations(self, dct):
        fac = dct["fac"]
        if not fac:
            return
        axis = Vector(dct["axis"])
        if not axis.length:
            return
        axis *= fac
        if not self._proflocs:
            self._proflocs = self._proflocs_get()
        rings = self._path.npts
        rpts = self._profile.npts
        nids, nfvs = falloff_lists(rings, dct["nprams"])
        ids, fvs = falloff_lists(rpts, dct["iprams"])
        if dct["abs_move"]:
            for i, f in zip(nids, nfvs):
                if not f:
                    continue
                for j, p in zip(ids, fvs):
                    if not p:
                        continue
                    self._proflocs[i][j] += axis * (f * p)
        else:
            for i, f in zip(nids, nfvs):
                if not f:
                    continue
                for j, p in zip(ids, fvs):
                    if not p:
                        continue
                    dv = self._proflocs[i][j].normalized()
                    df = f * p
                    for k in range(2):
                        self._proflocs[i][j][k] += dv[k] * axis[k] * df

    # RETURN

    @property
    def rings(self):
        return self._path.npts

    @property
    def rpts(self):
        return self._profile.npts

    def _pathrots_update(self, orilocs):
        offset = self._path.offset
        sid = self._path.npts - offset
        locs = orilocs[sid:] + orilocs[:sid]
        dv = self._pathupaxis if self._pathupfixed else self._z_axis
        rots = path_rots(locs, dv, self._path.closed)
        return rots[offset:] + rots[:offset]

    def get_locs(self):
        pa_l = self._pathlocs if self._pathlocs else self._pathstore
        if self.pathrot_active:
            pa_l = [self._pathrot @ v for v in pa_l]
        pa_r = self._pathrots_update(pa_l)
        pr_l = self._proflocs if self._proflocs else self._proflocs_get()
        if self._profrots:
            locs = [
                q @ s @ p + v
                for q, s, v, prl in zip(pa_r, self._profrots, pa_l, pr_l)
                for p in prl
            ]
        else:
            locs = [q @ p + v for q, v, prl in zip(pa_r, pa_l, pr_l) for p in prl]
        if self.meshrot_active:
            p = self._meshpivot
            return [self._meshrot @ (v - p) + p for v in locs]
        return locs

    def get_faces(self):
        rings = self._path.npts
        rpts = self._profile.npts
        prof_closed = self._profile.closed
        follow_limit = self._follow_limit
        if prof_closed:
            scan = gscan_cl(rpts, rings)
            pts = rpts + 1
            follow_limit = True
        else:
            scan = tuple(range(rpts * rings))
            pts = rpts
        if self._path.closed:
            cfl = tuple(range(rpts))
            limit = 0
            da = self._twistang % PopEx._tau
            if follow_limit:
                if da > PopEx._eps:
                    dt = PopEx._tau / rpts
                    for i in range(rpts):
                        val = dt * i + PopEx._eps
                        if val > da:
                            limit = i
                            break
                    cfl = cfl[limit:] + cfl[:limit]
            else:
                if PopEx._hpi <= da < 3 * PopEx._hpi:
                    cfl = cfl[::-1]
            if prof_closed:
                cfl += (limit,)
            scan += cfl
            return gfaces(pts, rings + 1, scan)
        faces = gfaces(pts, rings, scan)
        rsegs = rpts if prof_closed else rpts - 1
        limit = len(faces) - self._path.offset * rsegs
        faces = faces[:limit] + faces[limit + rsegs :]
        if self._endcaps:
            npts = rpts * rings
            faces.extend([tuple(range(rpts))[::-1], tuple(range(npts - rpts, npts))])
        return faces

    # ANIMATION

    def path_anim_update(self, *args):
        self._path.anim_update(*args)
        self._pathstore = self._path.get_locs()
        self.reset_pathlocs()

    def prof_anim_update(self, *args):
        self._profile.anim_update(*args)
        self._profstore = self._profile.get_locs()
        self.reset_proflocs()

    def meshrot_anim_angle(self, angle):
        self._meshrot @= Quaternion(self._meshaxis, angle)

    def pathrot_anim_angle(self, angle):
        self._pathrot @= Quaternion(self._pathaxis, angle)

    def roll_anim_angle(self, angle):
        q = Quaternion(self._z_axis, angle)
        self._profrots = [rot @ q for rot in self._profrots]
