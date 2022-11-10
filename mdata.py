
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

import math

from random import seed, uniform
from mathutils import Matrix, Quaternion, Vector


# ------------------------------------------------------------------------------
#
# -------------------------- POPMESH HELPERS  ----------------------------------

def ease_out(t, p, m):

    if m:
        return (2 * t)**p if t < 0.5 else (2 - 2 * t)**p
    return t**p


def ease_in(t, p, m):

    if m:
        return 1 - (1 - 2 * t)**p if t < 0.5 else 1 - (2 * t - 1)**p
    return 1 - (1 - t)**p


def ease_in_out(t, p, m):

    if m:
        v = math.sin(t * math.pi)
        return v**p
    return (2 * t)**p / 2 if t < 0.5 else 1 - ((2 - 2 * t)**p / 2)


def ease_list(ease, dt, p, m, count):

    if ease == 'OUT':
        return [ease_out(i * dt, p, m) for i in range(count)]
    if ease == 'IN':
        return [ease_in(i * dt, p, m) for i in range(count)]
    # default 'IN-OUT'
    return [ease_in_out(i * dt, p, m) for i in range(count)]


def falloff_lists(npts, dct, closed=True):

    k = dct['idx']
    itm = dct['itm']
    mir = dct['mir']
    reps = dct['reps']
    gap = dct['gap']
    f2 = dct['f2']

    i_lst = [i % npts for i in range(k, k+itm)]
    full = (npts == itm)
    if (itm == 1) or (not dct['lerp']):
        v_lst = [1] * itm
    else:
        div = itm if (closed and full and mir) else itm-1
        v_lst = ease_list(dct['ease'], 1/div, dct['exp'], mir, itm)
        if dct['rev']:
            v_lst = [1-i for i in v_lst]
    if full or (reps == 1):
        return i_lst, v_lst
    groups = int(npts/itm) + 1
    reps = groups if reps > groups else reps
    iinc = gap + 1
    ict = itm + gap
    mv_lst = v_lst.copy()
    for i in range(reps-1):
        # check whether capacity allows full group repeat
        ict += itm
        if ict > npts:
            break
        k = i_lst[-1] + iinc
        i_lst += [j % npts for j in range(k, k+itm)]
        v_lst = [f2 * j for j in v_lst]
        mv_lst += v_lst
        ict += gap
    return i_lst[:npts], mv_lst[:npts]


def q_short(q1, q2):

    if round(q1.normalized().dot(q2.normalized()), 5) < 0:
        q2.negate()
    return q2


def vector_rotdiff(a, b):

    c = a.cross(b)
    q = Quaternion((a.dot(b), *c))
    q.w += q.magnitude
    return q.normalized()


def path_rots(locs, cyclic):

    if cyclic:
        p = [locs[-1]] + locs + [locs[0]]
    else:
        p = ( [locs[0] + (locs[0] - locs[1])] + locs
              + [locs[-1] + (locs[-1] - locs[-2])] )
    dv = Vector((0, 0, 1))
    b = p[2] - p[0]
    q = vector_rotdiff(dv, b)
    rots = [q]
    pts = len(p)
    for i in range(2, pts-1):
        a = b
        b = (p[i+1] - p[i-1])
        q = vector_rotdiff(a, b) @ rots[-1]
        rots.append(q)
    return rots


def gscan_cl(pts, lines):

    scan = []
    for j in range(lines):
        loop = j * pts
        scan += [i + loop for i in range(pts)] + [loop]
    return scan


def gfaces(pts, lines, scan):

    return [[scan[i + j * pts], scan[i + 1 + j * pts],
             scan[i + pts + 1 + j * pts], scan[i + pts + j * pts]]
            for j in range(lines - 1) for i in range(pts - 1)]


# ------------------------------------------------------------------------------
#
# --------------------- PATH/PROFILE LOCATION PROVIDERS ------------------------

class Line:
    """ straight line: path only """

    def __init__(self, dim, segs, axis, lerp, exp, offset):
        self.dim = dim
        self._res = segs + 1
        self.axis = Vector(axis).normalized()
        self._lerp = lerp
        self.exp = exp
        self.offset = offset
        self.closed = False
        self.name = 'line'

    @property
    def npts(self):
        return self._res

    def get_locs(self):
        res = self._res
        dt = 1 / (res-1)
        if self.exp == 1:
            tl = [i * dt for i in range(res)]
        else:
            tl = ease_list(self._lerp, dt, self.exp, False, res)
        dim3 = self.axis * self.dim
        base = self.axis * (-self.dim/2)
        locs = [base + dim3 * t for t in tl]
        sid = self.offset
        return locs[sid:] + locs[:sid]


class Rectangle:
    """ xy-shape rectangle: path/profile """

    def __init__(self, dim, res, offset, reverse):
        self._dim = [dim[i] for i in range(2)]
        self._res = [i for i in res]
        self._pts = [i + 1 for i in res]
        self._round_segs = 0
        self.offset = offset
        self.reverse = reverse
        self.round_off = 0.2
        self.closed = True
        self.name = 'rectangle'

    @property
    def npts(self):
        return 2 * sum(self._res)

    @property
    def dim(self):
        return self._dim.copy()

    @dim.setter
    def dim(self, val):
        self._dim = [val[i] for i in range(2)]

    @property
    def round_segs(self):
        return self._round_segs

    @round_segs.setter
    def round_segs(self, val):
        if 4 * (val + 1) > self.npts:
            self._round_segs = 0
        else:
            self._round_segs = val

    def get_locs(self):
        dim = self._dim
        rad = [i / 2 for i in dim]
        res = self._res
        pts = self._pts
        sid = self.offset
        if self._round_segs < 1:
            incx = [i * dim[0] / res[0] for i in range(pts[0])]
            incy = [i * dim[1] / res[1] for i in range(pts[1])]
            locs = ([Vector((rad[0] - incx[i], rad[1], 0))
                     for i in range(pts[0])]
                    + [Vector((-rad[0], rad[1] - incy[i], 0))
                       for i in range(1, pts[1])]
                    + [Vector((-rad[0] + incx[i], -rad[1], 0))
                       for i in range(1, pts[0])]
                    + [Vector((rad[0], -rad[1] + incy[i], 0))
                       for i in range(1, pts[1] - 1)]
                    )
            if self.reverse:
                locs.reverse()
            return locs[sid:] + locs[:sid]

        # number of corner points
        rpts = self._round_segs + 1
        # number of side points
        diff = self.npts - 4 * rpts
        spts = [0, 0]
        if diff > 0:
            if res[0] == res[1]:
                d = int(diff / 4)
                spts = [d, d]
            else:
                d = [i - rpts for i in res]
                spts = [0 if i <= 0 else i-1 if 2*i > diff else i for i in d]
        roff = self.round_off
        # side lengths excluding offsets
        dist = [dim[i] - 2 * roff for i in range(2)]
        # corner locations
        ang = 0.5 * math.pi
        incs = [i * ang / (rpts - 1) for i in range(rpts)]
        pts = [Vector((roff * math.cos(inc), roff * math.sin(inc), 0))
               for inc in incs]
        # counter-clock rotate/translate corner and side points
        # right-far
        rc = (rad[0] - roff, rad[1] - roff, 0)
        locs = self._round_locs(rc, 0, pts)
        locs += self._side_locs(locs[-1], (-1, 0, 0), dist[0], spts[0]+1)[1:]
        # left-far
        rc = (-rad[0] + roff, rad[1] - roff, 0)
        locs += self._round_locs(rc, 0.5, pts)
        locs += self._side_locs(locs[-1], (0, -1, 0), dist[1], spts[1]+1)[1:]
        # left-near
        rc = (-rad[0] + roff, -rad[1] + roff, 0)
        locs += self._round_locs(rc, 1, pts)
        locs += self._side_locs(locs[-1], (1, 0, 0), dist[0], spts[0]+1)[1:]
        # right-near
        rc = (rad[0] - roff, -rad[1] + roff, 0)
        locs += self._round_locs(rc, 1.5, pts)
        locs += self._side_locs(locs[-1], (0, 1, 0), dist[1], spts[1]+1)[1:]
        if self.reverse:
            locs.reverse()
        return locs[sid:] + locs[:sid]

    def _round_locs(self, c, fac, pts):
        lm = Matrix.Translation(c)
        rm = Matrix.Rotation(fac * math.pi, 4, 'Z')
        mat = lm @ rm
        return [mat @ v for v in pts]

    def _side_locs(self, loc, vdir, dist, pts):
        if pts < 2:
            return []
        vdir = Vector(vdir)
        incs = [i * dist / pts for i in range(pts)]
        return [loc + vdir * inc for inc in incs]


class Ellipse:
    """ xy-shape ellipse: path/profile """

    def __init__(self, dim, res, step, fac, exp, offset, reverse):
        self._dim = [dim[i] for i in range(2)]
        self._res = res
        self._step = step
        self._exp = exp
        self.offset = offset
        self.reverse = reverse
        self.fac = fac
        self.closed = True
        self.name = 'ellipse'

    @property
    def npts(self):
        return self._res

    @property
    def dim(self):
        return self._dim.copy()

    @dim.setter
    def dim(self, val):
        self._dim = [val[i] for i in range(2)]

    def get_locs(self):
        dim = self._dim
        rad = [dim[i] / 2 for i in range(2)]
        fac = self.fac
        exp = self._exp
        res = self._res
        sid = self.offset
        t = 2 * math.pi / res
        if fac == 0:
            locs = [Vector((rad[0] * math.cos(i*t),
                            rad[1] * math.sin(i*t), 0))
                    for i in range(res)]
            if self.reverse:
                locs.reverse()
            return locs[sid:] + locs[:sid]

        step = self._step
        grp = math.ceil(res / step)
        inc = math.pi / grp
        lst = [fac * math.sin(i*inc)**exp for i in range(grp)]
        lst *= step
        locs = [Vector(((rad[0] + lst[i]) * math.cos(i*t),
                        (rad[1] + lst[i]) * math.sin(i*t), 0))
                for i in range(res)]
        # conform position/scale
        lsort = sorted(locs, key=lambda i: i[0])
        x = [lsort[0][0], lsort[-1][0]]
        lsort = sorted(locs, key=lambda i: i[1])
        y = [lsort[0][1], lsort[-1][1]]
        rx = (x[1] - x[0]) / 2
        ry = (y[1] - y[0]) / 2
        mloc = Matrix.Translation((x[0] + rx, y[0] + ry, 0)).inverted()
        sx = 0 if rx == 0 else rad[0] / rx
        sy = 0 if ry == 0 else rad[1] / ry
        msca = Matrix.Diagonal((sx, sy, 1, 1))
        tmat = msca @ mloc
        locs = [tmat @ loc for loc in locs]
        if self.reverse:
            locs.reverse()
        return locs[sid:] + locs[:sid]


class Spiral:
    """ spherical spiral (poles on z-axis): path only """

    def __init__(self, dim, points, revs, offset):
        self._points = points
        self._res = 2 * (points - 1)
        self.offset = offset
        self.dim = dim
        self.revs = revs
        self.closed = True
        self.name = 'spiral'

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
        locs = [Vector((rad * math.sin(i) * math.cos(c * i),
                        rad * math.sin(i) * math.sin(c * i),
                        rad * math.cos(i))) for i in t]
        qrot = Quaternion((0, 0, 1), math.pi)
        locs += [qrot @ loc for loc in locs][::-1][1:-1]
        sid = self.offset
        return locs[sid:] + locs[:sid]


class Custom:
    """ user-mesh verts: path/profile """

    def __init__(self, dim, odim, bbc, verts, closed, offset, reverse):
        self._dim = [dim[i] for i in range(3)]
        self._odim = [odim[i] for i in range(3)]
        self._oc = Vector(bbc)
        self._olocs = [Vector(v) for v in verts]
        self._res = len(verts)
        self.reverse = reverse
        self.closed = closed
        self.offset = offset
        self.name = 'custom'

    @property
    def npts(self):
        return self._res

    @property
    def dim(self):
        return self._dim.copy()

    @dim.setter
    def dim(self, val):
        self._dim = [val[i] for i in range(3)]

    def get_locs(self):
        dim = self._dim
        odim = self._odim
        ms = Matrix()
        for i in range(3):
            ms[i][i] = dim[i] / odim[i] if odim[i] else 0
        oc = self._oc
        locs = [ms @ (v-oc) for v in self._olocs]
        if self.reverse:
            locs.reverse()
        sid = self.offset
        return locs[sid:] + locs[:sid]


# ------------------------------------------------------------------------------
#
# ----------------------------- POP CLASS --------------------------------------

class PopEx:
    """ path-on-path class """

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
        # set path container from dictionary
        offset = dct['idx']
        reverse = False
        provider = dct['provider']
        if provider == 'line':
            dim = dct['lin_dim']
            segs = dct['res_lin']
            axis = dct['lin_axis']
            lerp = dct['lin_lerp']
            exp = dct['lin_exp']
            self._path = Line(dim, segs, axis, lerp, exp, offset)
        elif provider == 'spiral':
            dim = dct['spi_dim']
            points = dct['res_spi']
            revs = dct['spi_revs']
            self._path = Spiral(dim, points, revs, offset)
        elif provider == 'rectangle':
            dim = dct['rct_dim']
            res = dct['res_rct']
            self._path = Rectangle(dim, res, offset, reverse)
            self._path.round_segs = dct['round_segs']
            self._path.round_off = dct['round_off']
        elif provider == 'ellipse':
            dim = dct['ell_dim']
            res = dct['res_ell']
            step = dct['bump']
            fac = dct['bump_val']
            exp = dct['bump_exp']
            self._path = Ellipse(dim, res, step, fac, exp, offset, reverse)
        else:
            dim = dct['u_dim']
            udim = dct['user_dim']
            bbc = dct['user_bbc']
            verts = dct['upv']
            closed = dct['closed']
            self._path = Custom(dim, udim, bbc, verts, closed, offset, reverse)
        # initialize pop data
        self._endcaps = dct['endcaps']
        self._pathlocs = self._path.get_locs()
        self._pathrots = [Quaternion()] * self._path.npts
        self._spinrots = []

    def _set_profile(self, dct):
        # set profile container from dictionary *** after 'set_path'
        offset = dct['idx']
        reverse = dct['reverse']
        provider = dct['provider']
        if provider == 'ellipse':
            dim = dct['ell_dim']
            res = dct['res_ell']
            step = dct['bump']
            fac = dct['bump_val']
            exp = dct['bump_exp']
            self._profile = Ellipse(dim, res, step, fac, exp, offset, reverse)
        elif provider == 'rectangle':
            dim = dct['rct_dim']
            res = dct['res_rct']
            self._profile = Rectangle(dim, res, offset, reverse)
            self._profile.round_segs = dct['round_segs']
            self._profile.round_off = dct['round_off']
        else:
            dim = dct['u_dim']
            userdim = dct['user_dim']
            bbc = dct['user_bbc']
            verts = dct['upv']
            closed = dct['closed']
            self._profile = Custom(dim, userdim, bbc, verts, closed, offset,
                                   reverse)
        # initialize pop data
        self._spinaxis = (0, 0, 1)
        self._spinang = 0
        self._follow_limit = True
        rings = self._path.npts
        locs = self._profile.get_locs()
        self._proflocs = [[loc.copy() for loc in locs] for _ in range(rings)]

    # POP DATA - MODIFY

    def add_blend_profile(self, dct):
        # update 'proflocs'
        pts = self._profile.npts
        offset = dct['idx_off']
        reverse = dct['reverse']
        provider = dct['provider']
        if provider == 'rectangle':
            dim = dct['rct_dim']
            r = int(pts / 2)
            res = [r - int(r / 2), int(r / 2)]
            bln_prof = Rectangle(dim, res, offset, reverse)
            bln_prof.round_segs = dct['round_segs']
            bln_prof.round_off = dct['round_off']
        elif provider == 'ellipse':
            dim = dct['ell_dim']
            step = dct['bump']
            fac = dct['bump_val']
            exp = dct['bump_exp']
            bln_prof = Ellipse(dim, pts, step, fac, exp, offset, reverse)
        else:
            dim = dct['u_dim']
            userdim = dct['user_dim']
            bbc = dct['user_bbc']
            verts = dct['upv']
            closed = self._profile.closed
            bln_prof = Custom(dim, userdim, bbc, verts, closed, offset,
                              reverse)
        if not dct['abs_dim']:
            dims = [self._profile.dim[i] for i in range(2)]
            d = [dims[i] * dim[i] for i in range(2)]
            bln_prof.dim = d + [0]
        blocs = bln_prof.get_locs()
        ils, fls = falloff_lists(self._path.npts, dct['params'],
                                 self._path.closed)
        for i, f in zip(ils, fls):
            fac = dct['fac'] * f
            for j in range(pts):
                dl = (blocs[j] - self._proflocs[i][j]) * fac
                self._proflocs[i][j] += dl

    def spin_rotate(self, ang, spang, follow_limit):
        # update 'spinang', 'spinrots', 'follow_limit'
        if (ang == 0) and (spang == 0):
            return
        rings = self._path.npts
        self._spinang = spang
        self._follow_limit = follow_limit
        if spang == 0:
            angs = [ang] * rings
        else:
            div = rings if self._path.closed else rings - 1
            dt = spang / div
            angs = [ang + dt * i for i in range(rings)]
        self._spinrots = [Quaternion(self._spinaxis, a) for a in angs]

    def path_locations(self, dct):
        # update 'pathlocs'
        val = dct['fac']
        if val == 0:
            return
        ils, fls = falloff_lists(self._path.npts, dct['params'],
                                 self._path.closed)
        axis = dct['axis']
        if dct['abs_move']:
            vec = Vector(axis).normalized()
            for i, f in zip(ils, fls):
                fac = val * f
                self._pathlocs[i] += vec * fac
        else:
            for i, f in zip(ils, fls):
                fac = val * f
                vec = self._pathlocs[i].normalized()
                self._pathlocs[i] += vec * fac

    def prof_locations(self, dct):
        # update 'proflocs'
        val = dct['fac']
        if val == 0:
            return
        ils, fls = falloff_lists(self._profile.npts, dct['params'],
                                 self._profile.closed)
        pils, pfls = falloff_lists(self._path.npts, dct['gprams'],
                                   self._path.closed)
        axis = dct['axis']
        for i, p in zip(pils, pfls):
            for j, f in zip(ils, fls):
                fac = val * p * f
                loc = self._proflocs[i][j]
                vec = Vector([x*y for x, y in zip(axis, loc)]).normalized()
                self._proflocs[i][j] += vec * fac

    def noise_move(self, vfac, amp, ns):
        # update 'pathlocs'
        if amp == 0:
            return
        v = Vector(vfac)
        locs = self._pathlocs
        seed(ns)
        a = amp
        self._pathlocs = [p + v * uniform(-a, a) for p in locs]

    # POP DATA - RETURN

    def _pathrots_update(self):
        # set/update 'pathrots' based on path locations
        locs = self._pathlocs
        offset = self._path.offset
        sid = self._path.npts - offset
        locs = locs[sid:] + locs[:sid]
        rots = path_rots(locs, self._path.closed)
        rots = rots[offset:] + rots[:offset]
        rots_0 = self._pathrots
        # get short quat path (for animation loops)
        self._pathrots = [q_short(q0, q) for q0, q in zip(rots_0, rots)]

    def get_locs(self):
        # return final locations list
        pa_l = self._pathlocs
        self._pathrots_update()
        pa_r = self._pathrots
        sp_r = self._spinrots
        pr_l = self._proflocs
        locs = []
        if bool(sp_r):
            for pal, prl, par, spr in zip(pa_l, pr_l, pa_r, sp_r):
                locs += [par @ spr @ p + pal for p in prl]
        else:
            for pal, prl, par in zip(pa_l, pr_l, pa_r):
                locs += [par @ p + pal for p in prl]
        return locs

    def get_faces(self):
        rings = self._path.npts
        rpts = self._profile.npts
        prof_closed = self._profile.closed
        follow_limit = self._follow_limit
        if prof_closed:
            # closed-ring scan
            scan = gscan_cl(rpts, rings)
            pts = rpts + 1
            follow_limit = True
        else:
            # standard scan
            scan = list(range(rpts * rings))
            pts = rpts
        if self._path.closed:
            # closed-grid faces
            fr = list(range(rpts))
            # adjust order of indices [spin]
            limit = 0
            tau = 2 * math.pi
            da = self._spinang % tau
            if follow_limit:
                eps = 1e-5 # 0.00001
                if da > eps:
                    dt = tau/rpts
                    for t in range(rpts):
                        val = t*dt + eps
                        if val > da:
                            limit = t
                            break
                    fr = fr[limit:] + fr[:limit]
            else:
                hpi = math.pi * 0.5
                if hpi <= da < 3*hpi:
                    fr = fr[::-1]
            if prof_closed:
                # close the ring
                fr += [limit]
            # close the grid
            scan += fr
            return gfaces(pts, rings + 1, scan)
        # open-grid faces
        faces = gfaces(pts, rings, scan)
        rsegs = rpts if prof_closed else rpts - 1
        limit = len(faces) - self._path.offset * rsegs
        faces = faces[:limit] + faces[limit+rsegs:]
        if self._endcaps:
            faces.append(list(range(rpts))[::-1])
            npts = rpts * rings
            faces.append(list(range(npts-rpts, npts)))
        return faces

    # POP DATA - RECYCLE

    def noise_locs(self, locs, vfac, amp, ns):
        # recycle location vectors 'locs'
        if amp == 0:
            return locs
        v = Vector(vfac)
        seed(ns)
        locs = [loc + v * uniform(-amp, amp) for loc in locs]
        return locs

    # POP DATA - ANIMATION

    def save_state(self):
        # create store-copies of original path/profile locations
        locs = self._pathlocs
        self._pathstore = [loc.copy() for loc in locs]
        locs = self._proflocs
        self._profstore = [[l.copy() for l in pl] for pl in locs]

    def update_path(self, dim, fac):
        # update 'pathlocs' for current iteration
        if self._path.name == 'line':
            self._path.exp = fac
        elif self._path.name == 'spiral':
            self._path.revs = fac
        elif self._path.name == 'ellipse':
            self._path.fac = fac
        self._path.dim = dim
        self._pathlocs = self._path.get_locs()

    def update_profile(self, dim, fac):
        # update 'proflocs' for current iteration
        if self._profile.name == 'ellipse':
            self._profile.fac = fac
        self._profile.dim = dim
        locs = self._profile.get_locs()
        rings = self._path.npts
        self._proflocs = [[loc for loc in locs] for _ in range(rings)]

    def reset_pathlocs(self):
        # reset 'pathlocs' for current iteration
        locs = self._pathstore
        self._pathlocs = [loc.copy() for loc in locs]

    def reset_proflocs(self):
        # reset 'proflocs' for current iteration
        locs = self._profstore
        self._proflocs = [[l.copy() for l in pl] for pl in locs]

    def roll_angle(self, a):
        # update 'spinrots' for current iteration
        q = Quaternion(self._spinaxis, a)
        rots = self._spinrots
        self._spinrots = [rot @ q for rot in rots]
