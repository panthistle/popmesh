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

from mathutils import Matrix, Quaternion, Vector

from . import mlrps as ModLrps


# ------------------------------------------------------------------------------
#
# --------------------- PATH/PROFILE LOCATION PROVIDERS ------------------------


class Line:
    """straight line: xyz-path, xy-profile"""

    def __init__(self, dim, segs, lerp, exp, closed, offset, reverse):
        self._dim = [i for i in dim]
        self._res = segs + 1
        self._lerp = lerp
        self.exp = exp
        self.offset = offset
        self.reverse = reverse
        self.closed = closed
        self.name = "line"

    @property
    def npts(self):
        return self._res

    @property
    def dim(self):
        return self._dim.copy()

    @dim.setter
    def dim(self, val):
        self._dim = [i for i in val]

    def get_locs_xy(self):
        v = Vector((*self._dim, 0))
        return self._ret_locs(v)

    def get_locs(self):
        v = Vector(self._dim)
        return self._ret_locs(v)

    def _ret_locs(self, dim):
        res = self._res
        dt = 1 / (res - 1)
        tl = ModLrps.ease_list(self._lerp, dt, self.exp, False, res)
        base = -0.5 * dim
        locs = [base + dim * t for t in tl]
        if self.reverse:
            locs.reverse()
        sid = self.offset
        return locs[sid:] + locs[:sid]


class Rectangle:
    """rectangle: xz-path, xy-profile"""

    def __init__(self, dim, res, closed, offset, reverse):
        self._dim = [i for i in dim]
        self._res = [i for i in res]
        self._pts = [i + 1 for i in res]
        self._round_segs = 0
        self.offset = offset
        self.reverse = reverse
        self.round_off = 0.2
        self.closed = closed
        self.name = "rectangle"

    @property
    def npts(self):
        return 2 * sum(self._res)

    @property
    def dim(self):
        return self._dim.copy()

    @dim.setter
    def dim(self, val):
        self._dim = [i for i in val]

    @property
    def round_segs(self):
        return self._round_segs

    @round_segs.setter
    def round_segs(self, val):
        self._round_segs = val
        if 4 * (val + 1) > self.npts:
            self._round_segs = 0

    def get_locs_xy(self):
        dim = self._dim
        rad = [i / 2 for i in dim]
        res = self._res
        pts = self._pts
        sid = self.offset
        if self._round_segs < 1:
            a, b = self._side_increments(dim, rad, res, pts)
            locs = (
                [Vector((rad[0] - a[i], rad[1], 0)) for i in range(pts[0])]
                + [Vector((-rad[0], rad[1] - b[i], 0)) for i in range(1, pts[1])]
                + [Vector((-rad[0] + a[i], -rad[1], 0)) for i in range(1, pts[0])]
                + [Vector((rad[0], -rad[1] + b[i], 0)) for i in range(1, pts[1] - 1)]
            )
            if self.reverse:
                locs.reverse()
            return locs[sid:] + locs[:sid]
        roff = self.round_off
        dist = [i - 2 * roff for i in dim]
        d = self._roundata(res, roff, dim)
        incs = d["incs"]
        vecs = [Vector((roff * math.cos(inc), roff * math.sin(inc), 0)) for inc in incs]
        spts = d["spts"]
        axis = Vector((0, 0, 1))
        rc = (rad[0] - roff, rad[1] - roff, 0)
        locs = self._round_locs(rc, 0, axis, vecs)
        locs += self._side_locs(locs[-1], (-1, 0, 0), dist[0], spts[0] + 1)[1:]
        rc = (-rad[0] + roff, rad[1] - roff, 0)
        locs += self._round_locs(rc, 0.5, axis, vecs)
        locs += self._side_locs(locs[-1], (0, -1, 0), dist[1], spts[1] + 1)[1:]
        rc = (-rad[0] + roff, -rad[1] + roff, 0)
        locs += self._round_locs(rc, 1, axis, vecs)
        locs += self._side_locs(locs[-1], (1, 0, 0), dist[0], spts[0] + 1)[1:]
        rc = (rad[0] - roff, -rad[1] + roff, 0)
        locs += self._round_locs(rc, 1.5, axis, vecs)
        locs += self._side_locs(locs[-1], (0, 1, 0), dist[1], spts[1] + 1)[1:]
        if self.reverse:
            locs.reverse()
        return locs[sid:] + locs[:sid]

    def get_locs(self):
        locs = self.get_locs_xy()
        q = Quaternion((1, 0, 0), 0.5 * math.pi)
        return [q @ loc for loc in locs]

    def _side_increments(self, dim, rad, res, pts):
        a = [i * dim[0] / res[0] for i in range(pts[0])]
        b = [i * dim[1] / res[1] for i in range(pts[1])]
        return [a, b]

    def _roundata(self, res, roff, dim):
        rpts = self._round_segs + 1
        diff = self.npts - 4 * rpts
        spts = [0, 0]
        if diff > 0:
            if res[0] == res[1]:
                d = int(diff / 4)
                spts = [d, d]
            else:
                d = [i - rpts for i in res]
                spts = [0 if i <= 0 else (i - 1 if 2 * i > diff else i) for i in d]
        ang = 0.5 * math.pi
        incs = [ang * i / (rpts - 1) for i in range(rpts)]
        return {"spts": spts, "incs": incs}

    def _round_locs(self, pivot, fac, axis, vecs):
        lm = Matrix.Translation(pivot)
        rm = Matrix.Rotation(fac * math.pi, 4, axis)
        mat = lm @ rm
        return [mat @ v for v in vecs]

    def _side_locs(self, vpos, ldir, dist, spts):
        if spts < 2:
            return []
        vdir = Vector(ldir)
        dt = dist / spts
        return [vpos + vdir * (dt * i) for i in range(spts)]


class Ellipse:
    """ellipse: xz-path, xy-profile"""

    def __init__(self, dim, res, step, fac, exp, closed, offset, reverse):
        self._dim = [i for i in dim]
        self._res = res
        self._step = step
        self._exp = exp
        self.offset = offset
        self.fac = fac
        self.closed = closed
        self.reverse = reverse
        self.name = "ellipse"

    @property
    def npts(self):
        return self._res

    @property
    def dim(self):
        return self._dim.copy()

    @dim.setter
    def dim(self, val):
        self._dim = [i for i in val]

    def get_locs_xy(self):
        sid = self.offset
        if self.fac == 0:
            a, b = self._coords()
            locs = [Vector((x, y, 0)) for x, y in zip(a, b)]
            if self.reverse:
                locs.reverse()
            return locs[sid:] + locs[:sid]
        d = self._factor_coords()
        a, b = d["c"]
        locs = [Vector((x, y, 0)) for x, y in zip(a, b)]
        ta, tb = d["t"]
        mloc = Matrix.Translation((ta, tb, 0)).inverted()
        sa, sb = d["s"]
        msca = Matrix.Diagonal((sa, sb, 1, 1))
        tmat = msca @ mloc
        locs = [tmat @ loc for loc in locs]
        if self.reverse:
            locs.reverse()
        return locs[sid:] + locs[:sid]

    def get_locs(self):
        locs = self.get_locs_xy()
        q = Quaternion((1, 0, 0), 0.5 * math.pi)
        return [q @ loc for loc in locs]

    def _coords(self):
        rad = [i / 2 for i in self._dim]
        res = self._res
        dt = 2 * math.pi / res
        a = [rad[0] * math.cos(dt * i) for i in range(res)]
        b = [rad[1] * math.sin(dt * i) for i in range(res)]
        return [a, b]

    def _factor_coords(self):
        rad = [i / 2 for i in self._dim]
        fac = self.fac
        exp = self._exp
        res = self._res
        step = self._step
        grp = math.ceil(res / step)
        dt = math.pi / grp
        lst = [fac * math.sin(dt * i) ** exp for i in range(grp)]
        lst *= step
        dt = 2 * math.pi / res
        a = [(rad[0] + lst[i]) * math.cos(dt * i) for i in range(res)]
        b = [(rad[1] + lst[i]) * math.sin(dt * i) for i in range(res)]
        lsort = sorted(a)
        amin, amax = lsort[0], lsort[-1]
        lsort = sorted(b)
        bmin, bmax = lsort[0], lsort[-1]
        ra = (amax - amin) / 2
        rb = (bmax - bmin) / 2
        sa = 0 if ra == 0 else rad[0] / ra
        sb = 0 if rb == 0 else rad[1] / rb
        ta = amin + ra
        tb = bmin + rb
        return {"c": [a, b], "t": [ta, tb], "s": [sa, sb]}


class Spiral:
    """spherical spiral: xyz-path"""

    def __init__(self, dim, points, revs, closed, offset, reverse):
        self._points = points
        self._res = 2 * (points - 1)
        self.offset = offset
        self.dim = dim
        self.revs = revs
        self.closed = closed
        self.reverse = reverse
        self.name = "spiral"

    @property
    def npts(self):
        return self._res

    def get_locs(self):
        dim = self.dim
        rad = dim / 2
        c = 2 * self.revs
        pts = self._points
        dt = math.pi / (pts - 1)
        t = [dt * i for i in range(pts)]
        locs = [
            Vector(
                (
                    rad * math.sin(i) * math.cos(c * i),
                    rad * math.sin(i) * math.sin(c * i),
                    rad * math.cos(i),
                )
            )
            for i in t
        ]
        qrot = Quaternion((0, 0, 1), math.pi)
        locs += [qrot @ loc for loc in locs][::-1][1:-1]
        if self.reverse:
            locs.reverse()
        sid = self.offset
        return locs[sid:] + locs[:sid]


class Custom:
    """user-mesh verts: xyz-path, xy-profile"""

    def __init__(self, dim, user_dim, bbc, verts, closed, offset, reverse):
        self._dim = [i for i in dim]
        self._udim = [i for i in user_dim]
        self._oc = Vector(bbc)
        self._olocs = [v for v in verts]
        self._res = len(verts)
        self.reverse = reverse
        self.closed = closed
        self.offset = offset
        self.name = "custom"

    @property
    def npts(self):
        return self._res

    @property
    def dim(self):
        return self._dim.copy()

    @dim.setter
    def dim(self, val):
        self._dim = [i for i in val]

    def get_locs_xy(self):
        xdl = [1, 1]
        return self._ret_locs(xdl)

    def get_locs(self):
        xdl = [1]
        return self._ret_locs(xdl)

    def _ret_locs(self, xdl):
        psca = [i / j if j else 1 for i, j in zip(self._dim, self._udim)]
        msca = Matrix.Diagonal((*psca, *xdl))
        oc = self._oc
        locs = [msca @ (v - oc) for v in self._olocs]
        if self.reverse:
            locs.reverse()
        sid = self.offset
        return locs[sid:] + locs[:sid]
