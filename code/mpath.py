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

from mathutils import Matrix, Quaternion, Vector


# ------------------------------------------------------------------------------
#
# ------------------------- INTERPOLATION LISTS --------------------------------


def itlinear(t, m):
    if m:
        return 2 * t if t < 0.5 else 2 - 2 * t
    return t


def itexpo_out(t, p, m):
    if m:
        return (2 * t) ** p if t < 0.5 else (2 - 2 * t) ** p
    return t**p


def itexpo_in(t, p, m):
    if m:
        return 1 - (1 - 2 * t) ** p if t < 0.5 else 1 - (2 * t - 1) ** p
    return 1 - (1 - t) ** p


def itexpo_in_out(t, p, m):
    if m:
        return math.sin(t * math.pi) ** p
    return (2 * t) ** p / 2 if t < 0.5 else 1 - ((2 - 2 * t) ** p / 2)


def it_list(ease, dt, p, m, count):
    if ease == "LINEAR":
        return [itlinear(i * dt, m) for i in range(count)]
    if ease == "OUT":
        return [itexpo_out(i * dt, p, m) for i in range(count)]
    if ease == "IN":
        return [itexpo_in(i * dt, p, m) for i in range(count)]
    return [itexpo_in_out(i * dt, p, m) for i in range(count)]


# ------------------------------------------------------------------------------
#
# --------------------- PATH/PROFILE LOCATION PROVIDERS ------------------------


class Line:
    """straight line (X, from x=dim/2): path, profile"""

    def __init__(self, dct):
        self.name = "line"
        self.update(dct)

    def update(self, dct):
        self.npts = dct["res_lin"]
        self.dim = dct["lin_dim"]
        self.ease = dct["lin_ease"]
        self.exp = dct["lin_exp"]

    def anim_update(self, *args):
        self.dim, self.exp = args

    def get_locs(self):
        dt = 1 / (self.npts - 1)
        fvs = it_list(self.ease, dt, self.exp, False, self.npts)
        vdim = Vector((-self.dim, 0, 0))
        base = -0.5 * vdim
        return [base + vdim * t for t in fvs]


class Wave:
    """sine wave (XY, from x=dim[0]/2, y=0): path, profile"""

    def __init__(self, dct):
        self.name = "wave"
        self.update(dct)

    def update(self, dct):
        self.npts = dct["res_wav"]
        self.dim = dct["wav_dim"]
        self.amp = dct["wav_amp"]
        self.frq = dct["wav_frq"]
        self.pha = dct["wav_pha"]

    def anim_update(self, *args):
        self.dim, self.amp, self.frq, self.pha = args

    def get_locs(self):
        npts = self.npts
        segs = npts - 1
        start = 0.5 * self.dim
        dtx = -self.dim / segs
        dty = self.frq * 2 * math.pi / segs
        return [
            Vector((start + dtx * i, self.amp * math.sin(dty * i + self.pha), 0))
            for i in range(npts)
        ]


class Arc:
    """arc (XY, counterclock from x=dim/2, y=0): path, profile"""

    def __init__(self, dct):
        self.name = "arc"
        self.update(dct)

    def update(self, dct):
        self.npts = dct["res_arc"]
        self.dim = dct["arc_dim"]
        self.fac = dct["arc_fac"]
        self.off = dct["arc_off"]

    def anim_update(self, *args):
        self.dim, self.fac = args

    def get_locs(self):
        w = self.dim
        s = self.fac
        npts = self.npts
        if s == 0:
            dt = w / (npts - 1)
            return [Vector(((w / 2) - dt * i, 0, 0)) for i in range(npts)]
        sp = abs(s)
        r = sp / 2 + w * w / (8 * sp)
        c = Vector((0, self.off + r - sp, 0))
        a = Vector((w / 2, self.off, 0)) - c
        b = Vector((-w / 2, self.off, 0)) - c
        theta = a.angle(b, 0)
        if r < sp:
            theta = 2 * math.pi - theta
        dt = theta / (npts - 1)
        axis = (0, 0, 1) if w < 0 else (0, 0, -1)
        locs = [Quaternion(axis, dt * i) @ a + c for i in range(npts)]
        if s > 0:
            for i, loc in enumerate(locs):
                locs[i][1] -= 2 * loc[1]
        return locs


class Ellipse:
    """ellipse (XY, counterclock from x=dim[0]/2, y=0): path, profile"""

    def __init__(self, dct):
        self.name = "ellipse"
        self.update(dct)

    def update(self, dct):
        self.npts = dct["res_ell"]
        self.dim = [dct["ell_dim"][0], dct["ell_dim"][1]]
        self.step = dct["ellstep"]
        self.exp = dct["ellstep_exp"]
        self.fac = dct["ellstep_val"]

    def anim_update(self, *args):
        self.dim, self.fac = args

    def get_locs(self):
        npts = self.npts
        rad = (self.dim[0] / 2, self.dim[1] / 2)
        if self.fac == 0:
            dt = 2 * math.pi / npts
            return [
                Vector((rad[0] * math.cos(dt * i), rad[1] * math.sin(dt * i), 0))
                for i in range(npts)
            ]
        a, b, loc, sca = self._factor_coords(npts, rad)
        locs = [Vector((x, y, 0)) for x, y in zip(a, b)]
        mloc = Matrix.Translation((*loc, 0)).inverted()
        msca = Matrix.Diagonal((*sca, 1, 1))
        tmat = msca @ mloc
        return [tmat @ loc for loc in locs]

    def _factor_coords(self, npts, rad):
        fac = self.fac
        exp = self.exp
        step = self.step
        grp = math.ceil(npts / step)
        dt = math.pi / grp
        fvs = [fac * math.sin(dt * i) ** exp for i in range(grp)] * step
        dt = 2 * math.pi / npts
        a = [(rad[0] + fvs[i]) * math.cos(dt * i) for i in range(npts)]
        b = [(rad[1] + fvs[i]) * math.sin(dt * i) for i in range(npts)]
        lsort = sorted(a)
        amin, amax = lsort[0], lsort[-1]
        lsort = sorted(b)
        bmin, bmax = lsort[0], lsort[-1]
        ra = (amax - amin) / 2
        rb = (bmax - bmin) / 2
        sa = 0 if not ra else rad[0] / ra
        sb = 0 if not rb else rad[1] / rb
        ta = amin + ra
        tb = bmin + rb
        return a, b, (ta, tb), (sa, sb)


class Polygon:
    """polygon (XY, counterclock from x=dim[0]/2, y=0): path, profile"""

    def __init__(self, dct):
        self.name = "polygon"
        self.update(dct)

    def update(self, dct):
        self.npts = dct["res_pol"]
        self.dim = [dct["pol_dim"][0], dct["pol_dim"][1]]
        t_sides = min(self.npts // 2, dct["pol_sid"])
        t_pts = self.npts - 2 * t_sides
        t_rem = t_pts % t_sides
        t_res = 2 * t_sides + t_pts - t_rem
        t_seg = t_res // t_sides
        self._sides = t_sides
        self._segs = [t_seg + 1 if i < t_rem else t_seg for i in range(t_sides)]
        self._coff = 0 if dct["pol_coff"] < 0.001 else dct["pol_coff"]
        self._cres = 0 if not self._coff else min(dct["pol_cres"], t_seg - 1)
        self.angle = dct["pol_ang"]
        self.ease = dct["pol_ease"]
        self.exp = dct["pol_exp"]

    def anim_update(self, *args):
        self.dim = args[0]

    def get_locs(self):
        coff = self._coff
        cnt = self._sides
        cres = self._cres
        m = Matrix.Rotation(self.angle, 3, "Z")
        s = (self.dim[0] * 0.5, self.dim[1] * 0.5, 1)
        for i in range(3):
            m[i] *= s[i]
        dt = 2 * math.pi / cnt
        pvs = [m @ Vector((math.cos(dt * i), math.sin(dt * i), 0)) for i in range(cnt)]
        pvs.append(pvs[0])
        locs = []
        if not cres:
            for i in range(cnt):
                seg = self._segs[i]
                fvs = it_list(self.ease, 1 / seg, self.exp, False, seg)
                vec = pvs[i + 1] - pvs[i]
                locs += [pvs[i] + vec * t for t in fvs]
            return locs
        for i in range(cnt):
            j = 2 if i == 0 else 1
            a = pvs[i]
            b = pvs[i - j]
            c = pvs[i + 1]
            ab = b - a
            ac = c - a
            if (ab.x * ab.x + ab.y * ab.y) * (ac.x * ac.x + ac.y * ac.y):
                p1 = a + ab.normalized() * coff
                uac = ac.normalized()
                p2 = a + uac * coff
                pc = p1 + uac * coff
                locs += self._bevlocs(p1, p2, pc, cres)
                seg = self._segs[i] - cres
                if seg > 1:
                    b = locs.pop()
                    e = c - uac * coff
                    vec = e - b
                    fvs = it_list(self.ease, 1 / seg, self.exp, False, seg)
                    locs += [b + vec * t for t in fvs]
            else:
                seg = self._segs[i]
                fvs = it_list(self.ease, 1 / seg, self.exp, False, seg)
                locs += [a + ac * t for t in fvs]
        return locs

    def _bevlocs(self, p1, p2, pc, nsegs):
        mt = Matrix.Translation(pc)
        p1, p2 = (mt.inverted() @ v for v in (p1, p2))
        ang = p1.to_2d().angle_signed(Vector((1, 0)), 0)
        mr = Matrix.Rotation(ang, 4, "Z")
        p1, p2 = (mr.inverted() @ v for v in (p1, p2))
        msh = Matrix.Shear("XZ", 4, (p2[0] / p2[1], 0))
        p2 = msh.inverted() @ p2
        mdg = Matrix.Diagonal((p1[0], p2[1], 1, 1))
        bpts = nsegs + 1
        dt = 0.5 * math.pi / nsegs
        bvs = [Vector((math.cos(dt * i), math.sin(dt * i), 0)) for i in range(bpts)]
        mat = mt @ mr @ msh @ mdg
        return [mat @ v for v in bvs]


class Helix:
    """helix (XYZ, counterclock from x=dim[0]/2, y=0, z=dim[2]/2): path"""

    def __init__(self, dct):
        self.name = "helix"
        self.update(dct)

    def update(self, dct):
        self.npts = dct["res_hel"]
        self.dim = [dct["hel_dim"][0], dct["hel_dim"][1]]
        self.length = dct["hel_len"]
        self.steps = dct["hel_stp"]
        self.fac = dct["hel_fac"]
        self.pha = dct["hel_pha"]
        self.hlerp = dct["hel_hlrp"]
        self.exp = dct["hel_exp"]
        self.mir = dct["hel_mir"]
        self.ease = dct["hel_ease"]
        self.invert = dct["hel_invert"]

    def anim_update(self, *args):
        self.dim, self.length, self.fac, self.steps, self.pha = args

    def get_locs(self):
        npts = self.npts
        dt = 1 / (npts - 1)
        height = -self.length
        base = -height / 2
        if not self.hlerp or (self.ease == "LINEAR"):
            dls = [base + height * dt * i for i in range(npts)]
        else:
            fvs = it_list(self.ease, dt, self.exp, False, npts)
            dls = [base + height * t for t in fvs]
        rad = (self.dim[0] / 2, self.dim[1] / 2)
        dif = (rad[0] * self.fac - rad[0], rad[1] * self.fac - rad[1])
        rls = it_list(self.ease, dt, self.exp, self.mir, npts)
        if self.invert and not self.mir:
            rls.reverse()
        dt *= 2 * math.pi * self.steps
        tls = [self.pha + dt * i for i in range(npts)]
        return [
            Vector(
                (
                    (rad[0] + dif[0] * r) * math.cos(t),
                    (rad[1] + dif[1] * r) * math.sin(t),
                    d,
                )
            )
            for r, t, d in zip(rls, tls, dls)
        ]


class Spiral:
    """double spherical spiral (XYZ, counterclock from x=0, y=0, z=dim/2): path"""

    def __init__(self, dct):
        self.name = "spiral"
        self.update(dct)

    def update(self, dct):
        self.npts = dct["res_spi"]
        self._end = 2 if self.npts % 2 else 1
        self._pts = self.npts // 2 + self._end
        self.dim = dct["spi_dim"]
        self.revs = dct["spi_revs"]

    def anim_update(self, *args):
        self.dim, self.revs = args

    def get_locs(self):
        c = self.revs
        pts = self._pts
        rad = self.dim / 2
        dt = math.pi / (pts - 1)
        locs = [
            Vector(
                (
                    rad * math.sin(dt * i) * math.cos(c * dt * i),
                    rad * math.sin(dt * i) * math.sin(c * dt * i),
                    rad * math.cos(dt * i),
                )
            )
            for i in range(pts)
        ]
        q = Quaternion((0, 0, 1), math.pi)
        locs += [q @ loc for loc in locs][::-1][1 : -self._end]
        return locs


class Custom:
    """user-mesh verts: (XYZ) path, (XY) profile"""

    def __init__(self, dct):
        self.name = "custom"
        self.update(dct)

    def update(self, dct):
        self.npts = len(dct["upv"])
        self._udim = [i for i in dct["user_dim"]]
        self.dim = [i for i in dct["cust_dim"]]
        self._oc = Vector(dct["user_piv"])
        self._olocs = dct["upv"]

    def anim_update(self, *args):
        self.dim = args[0]

    def get_locs(self):
        sca = [i / j if j else 0 for i, j in zip(self.dim, self._udim)]
        xdl = (0, 1) if len(sca) < 3 else (1,)
        msca = Matrix.Diagonal((*sca, *xdl))
        oc = self._oc
        return [msca @ (v - oc) for v in self._olocs]
