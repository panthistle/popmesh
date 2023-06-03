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


import math
from random import seed, uniform

from mathutils import Quaternion, Vector

from . import mlrps as ModLrps
from . import mpath as ModPath


# ------------------------------------------------------------------------------
#
# -------------------------- POPMESH HELPERS  ----------------------------------


def falloff_lists(npts, dct):

    k = dct["idx"]
    itm = dct["itm"]
    mir = dct["mir"]
    reps = min(int(npts / itm), dct["reps"])
    gap = dct["gap"]
    f2 = dct["f2"]
    i_lst = [i % npts for i in range(k, k + itm)]
    if (itm == 1) or (not dct["lerp"]):
        v_lst = [1] * itm
    else:
        div = itm if dct["cyc"] else itm - 1
        v_lst = ModLrps.ease_list(dct["ease"], 1 / div, dct["exp"], mir, itm)
        if dct["rev"]:
            v_lst = [1 - i for i in v_lst]
    if npts == itm or reps == 1:
        return i_lst, v_lst
    iinc = gap + 1
    ict = itm + gap
    mv_lst = v_lst.copy()
    for i in range(reps - 1):
        ict += itm
        if ict > npts:
            break
        k = i_lst[-1] + iinc
        i_lst += [j % npts for j in range(k, k + itm)]
        v_lst = [f2 * j for j in v_lst]
        mv_lst += v_lst
        ict += gap
    return i_lst[:npts], mv_lst[:npts]


def vector_rotdiff(a, b):

    d = a.dot(b)
    w = a.length * b.length + d
    yzsum = a[1] + a[2]
    if w < 0.0001 and yzsum == 0:
        return Quaternion((0, 0, 0, 1))
    c = a.cross(b)
    q = Quaternion((d, *c))
    q.w += q.magnitude
    return q.normalized()


def path_rots(locs, dv, cyclic):

    if cyclic:
        l1, l2 = locs[0], locs[-1]
    else:
        l1 = locs[-1] + (locs[-1] - locs[-2])
        l2 = locs[0] + (locs[0] - locs[1])
    locs.append(l1)
    b = locs[1] - l2
    rots = [vector_rotdiff(dv, b)]
    for i in range(1, len(locs) - 1):
        a = b
        b = locs[i + 1] - locs[i - 1]
        q = vector_rotdiff(a, b) @ rots[-1]
        rots.append(q)
    locs.pop()
    return rots


def gscan_cl(pts, lines):

    scan = []
    for j in range(lines):
        loop = j * pts
        scan += [i + loop for i in range(pts)] + [loop]
    return scan


def gfaces(pts, lines, scan):

    return [
        [
            scan[i + j * pts],
            scan[i + 1 + j * pts],
            scan[i + pts + 1 + j * pts],
            scan[i + pts + j * pts],
        ]
        for j in range(lines - 1)
        for i in range(pts - 1)
    ]


# ------------------------------------------------------------------------------
#
# ----------------------------- POP CLASS --------------------------------------


class PopEx:
    """path-on-path class"""

    def __init__(self, path_dct, prof_dct):
        self._set_path(path_dct)
        self._set_profile(prof_dct)

    @property
    def rings(self):
        return self._path.npts

    @property
    def rpts(self):
        return self._profile.npts

    @property
    def path_closed(self):
        return self._path.closed

    @property
    def profile_closed(self):
        return self._profile.closed

    # POP DATA - INITIALIZE

    def _set_path(self, dct):
        clsd = dct["closed"]
        rev = False
        offset = dct["idx"]
        provider = dct["provider"]
        if provider == "line":
            segs = dct["res_lin"]
            dim = dct["lin_dim"]
            lerp = dct["lin_lerp"]
            exp = dct["lin_exp"]
            self._path = ModPath.Line(dim, segs, lerp, exp, clsd, offset, rev)
        elif provider == "spiral":
            points = dct["res_spi"]
            dim = dct["spi_dim"]
            revs = dct["spi_revs"]
            self._path = ModPath.Spiral(dim, points, revs, clsd, offset, rev)
        elif provider == "rectangle":
            res = dct["res_rct"]
            dim = [dct["rct_dim"][0], dct["rct_dim"][2]]
            self._path = ModPath.Rectangle(dim, res, clsd, offset, rev)
            self._path.round_segs = dct["round_segs"]
            self._path.round_off = dct["round_off"]
        elif provider == "ellipse":
            res = dct["res_ell"]
            dim = [dct["ell_dim"][0], dct["ell_dim"][2]]
            step = dct["bump"]
            fac = dct["bump_val"]
            exp = dct["bump_exp"]
            self._path = ModPath.Ellipse(dim, res, step, fac, exp, clsd, offset, rev)
        else:
            dim = dct["u_dim"]
            udim = dct["user_dim"]
            bbc = dct["user_bbc"]
            verts = dct["upv"]
            self._path = ModPath.Custom(dim, udim, bbc, verts, clsd, offset, rev)
        self._endcaps = dct["endcaps"]
        self._pathlocs = self._path.get_locs()
        self._pathrots = [Quaternion()] * self._path.npts
        self._spinrots = [Quaternion()] * self._path.npts
        self._spinaxis = Vector((0, 0, 1))
        self._spinang = 0
        self._follow_limit = True

    def _set_profile(self, dct):
        clsd = dct["closed"]
        rev = dct["reverse"]
        offset = dct["idx"]
        provider = dct["provider"]
        if provider == "line":
            segs = dct["res_lin"]
            dim = dct["lin_dim"]
            lerp = dct["lin_lerp"]
            exp = dct["lin_exp"]
            self._profile = ModPath.Line(dim, segs, lerp, exp, clsd, offset, rev)
        elif provider == "rectangle":
            dim = dct["rct_dim"]
            res = dct["res_rct"]
            self._profile = ModPath.Rectangle(dim, res, clsd, offset, rev)
            self._profile.round_segs = dct["round_segs"]
            self._profile.round_off = dct["round_off"]
        elif provider == "ellipse":
            dim = dct["ell_dim"]
            res = dct["res_ell"]
            step = dct["bump"]
            fac = dct["bump_val"]
            exp = dct["bump_exp"]
            self._profile = ModPath.Ellipse(dim, res, step, fac, exp, clsd, offset, rev)
        else:
            dim = dct["u_dim"]
            udim = dct["user_dim"]
            bbc = dct["user_bbc"]
            verts = dct["upv"]
            self._profile = ModPath.Custom(dim, udim, bbc, verts, clsd, offset, rev)
        locs = self._profile.get_locs_xy()
        self._proflocs = [[loc.copy() for loc in locs] for _ in range(self._path.npts)]

    # POP DATA - MODIFY

    def add_blend_profile(self, dct):
        pts = self._profile.npts
        clsd = self._profile.closed
        rev = dct["reverse"]
        offset = dct["idx"]
        provider = dct["provider"]
        if provider == "line":
            dim = dct["lin_dim"]
            segs = pts - 1
            lerp = dct["lin_lerp"]
            exp = dct["lin_exp"]
            bln_prof = ModPath.Line(dim, segs, lerp, exp, clsd, offset, rev)
        elif provider == "rectangle":
            dim = dct["rct_dim"]
            r = int(pts / 2)
            res = [r - int(r / 2), int(r / 2)]
            bln_prof = ModPath.Rectangle(dim, res, clsd, offset, rev)
            bln_prof.round_segs = dct["round_segs"]
            bln_prof.round_off = dct["round_off"]
        elif provider == "ellipse":
            dim = dct["ell_dim"]
            step = dct["bump"]
            fac = dct["bump_val"]
            exp = dct["bump_exp"]
            bln_prof = ModPath.Ellipse(dim, pts, step, fac, exp, clsd, offset, rev)
        else:
            dim = dct["u_dim"]
            udim = dct["user_dim"]
            bbc = dct["user_bbc"]
            verts = dct["upv"]
            bln_prof = ModPath.Custom(dim, udim, bbc, verts, clsd, offset, rev)
        if not dct["abs_dim"]:
            bln_prof.dim = [i * j for i, j in zip(self._profile.dim, dim)]
        blocs = bln_prof.get_locs_xy()
        ils, fls = falloff_lists(self._path.npts, dct["params"])
        for i, f in zip(ils, fls):
            fac = dct["fac"] * f
            for j in range(pts):
                dl = (blocs[j] - self._proflocs[i][j]) * fac
                self._proflocs[i][j] += dl

    def spin_rotate(self, a, sa, follow_limit):
        if not (a or sa):
            return 0
        rings = self._path.npts
        self._spinang = sa
        self._follow_limit = follow_limit
        if not sa:
            self._spinrots = [Quaternion(self._spinaxis, a) for _ in range(rings)]
            return 0
        div = rings if self._path.closed else rings - 1
        dt = sa / div
        self._spinrots = [Quaternion(self._spinaxis, a + dt * i) for i in range(rings)]
        return 0

    def path_locations(self, dct):
        fac = dct["fac"]
        if not fac:
            return 0
        ils, fls = falloff_lists(self._path.npts, dct["params"])
        if dct["abs_move"]:
            vec = Vector(dct["axis"]).normalized()
            for i, f in zip(ils, fls):
                val = fac * f
                self._pathlocs[i] += vec * val
        else:
            for i, f in zip(ils, fls):
                val = fac * f
                vec = self._pathlocs[i].normalized()
                self._pathlocs[i] += vec * val
        return 0

    def prof_locations(self, dct):
        fac = dct["fac"]
        if not fac:
            return 0
        ils, fls = falloff_lists(self._profile.npts, dct["params"])
        pils, pfls = falloff_lists(self._path.npts, dct["gprams"])
        if dct["abs_move"]:
            vec = Vector([*dct["axis"], 0]).normalized()
            for i, p in zip(pils, pfls):
                for j, f in zip(ils, fls):
                    val = fac * p * f
                    self._proflocs[i][j] += vec * val
        else:
            for i, p in zip(pils, pfls):
                for j, f in zip(ils, fls):
                    val = fac * p * f
                    vec = self._proflocs[i][j].normalized()
                    self._proflocs[i][j] += vec * val
        return 0

    def noiz_move(self, vfac, amp, ns):
        if not amp:
            return 0
        locs = self._pathlocs
        seed(ns)
        self._pathlocs = [
            loc + Vector([i * uniform(-amp, amp) for i in vfac]) for loc in locs
        ]
        return 0

    # POP DATA - RETURN

    def _pathrots_update(self, orilocs):
        offset = self._path.offset
        sid = self._path.npts - offset
        locs = orilocs[sid:] + orilocs[:sid]
        rots = path_rots(locs, self._spinaxis, self._path.closed)
        return rots[offset:] + rots[:offset]

    def get_locs(self):
        pa_l = self._pathlocs
        self._pathrots = self._pathrots_update(pa_l)
        pa_r = self._pathrots
        sp_r = self._spinrots
        pr_l = self._proflocs
        locs = []
        for pal, prl, par, spr in zip(pa_l, pr_l, pa_r, sp_r):
            locs += [par @ spr @ p + pal for p in prl]
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
            scan = list(range(rpts * rings))
            pts = rpts
        if self._path.closed:
            cfl = list(range(rpts))
            limit = 0
            tau = 2 * math.pi
            da = self._spinang % tau
            if follow_limit:
                eps = 1e-5
                if da > eps:
                    dt = tau / rpts
                    for t in range(rpts):
                        val = t * dt + eps
                        if val > da:
                            limit = t
                            break
                    cfl = cfl[limit:] + cfl[:limit]
            else:
                hpi = math.pi * 0.5
                if hpi <= da < 3 * hpi:
                    cfl = cfl[::-1]
            if prof_closed:
                cfl += [limit]
            scan += cfl
            return gfaces(pts, rings + 1, scan)
        faces = gfaces(pts, rings, scan)
        rsegs = rpts if prof_closed else rpts - 1
        limit = len(faces) - self._path.offset * rsegs
        faces = faces[:limit] + faces[limit + rsegs :]
        if self._endcaps:
            faces.append(list(range(rpts))[::-1])
            npts = rpts * rings
            faces.append(list(range(npts - rpts, npts)))
        return faces

    # POP DATA - RECYCLE LOCATIONS [NOIZ]

    def noiz_locs(self, locs, vfac, amp, ns):
        if not amp:
            return locs
        seed(ns)
        locs = [loc + Vector([i * uniform(-amp, amp) for i in vfac]) for loc in locs]
        return locs

    # POP DATA - ANIMATION

    def save_state(self):
        self._pathstore = [loc.copy() for loc in self._pathlocs]
        self._profstore = [[loc.copy() for loc in pl] for pl in self._proflocs]

    def update_path(self, dim, fac):
        if self._path.name == "line":
            self._path.exp = fac
        elif self._path.name == "spiral":
            self._path.revs = fac
        elif self._path.name in ["ellipse", "rectangle"]:
            dim = [dim[0], dim[2]]
            if self._path.name == "ellipse":
                self._path.fac = fac
        self._path.dim = dim
        self._pathlocs = self._path.get_locs()

    def update_profile(self, dim, fac):
        if self._profile.name == "line":
            self._profile.exp = fac
        elif self._profile.name == "ellipse":
            self._profile.fac = fac
        self._profile.dim = dim
        locs = self._profile.get_locs_xy()
        self._proflocs = [[loc.copy() for loc in locs] for _ in range(self._path.npts)]

    def reset_pathlocs(self):
        self._pathlocs = [loc.copy() for loc in self._pathstore]

    def reset_proflocs(self):
        self._proflocs = [[loc.copy() for loc in pl] for pl in self._profstore]

    def roll_angle(self, a):
        q = Quaternion(self._spinaxis, a)
        rots = self._spinrots
        self._spinrots = [rot @ q for rot in rots]
