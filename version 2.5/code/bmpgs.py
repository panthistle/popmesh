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

from . import mpopm as ModPOPM
from . import mpdop as ModPDOP


# ------------------------------------------------------------------------------
#
# -------------------------------- BMPGS ---------------------------------------


# ---- BMPGS PROPERTIES


class PTDBLNPOPM_vec3(bpy.types.PropertyGroup):
    vert: bpy.props.FloatVectorProperty(
        size=3, default=(0, 0, 0), subtype="TRANSLATION"
    )


class PTDBLNPOPM_anim_index(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(
        name="index", description="animate index", default=False, options={"HIDDEN"}
    )
    offrnd: bpy.props.BoolProperty(
        name="random",
        description="random index value in [idx-offset, idx+offset]",
        default=False,
        options={"HIDDEN"},
    )
    offrndseed: bpy.props.IntProperty(
        name="seed", description="random seed", default=0, min=0, options={"HIDDEN"}
    )
    offset: bpy.props.IntProperty(
        name="offset",
        description="index offset",
        default=0,
        options={"HIDDEN"},
    )
    beg: bpy.props.IntProperty(
        name="start", description="start keyframe", default=1, min=1, options={"HIDDEN"}
    )
    stp: bpy.props.IntProperty(
        name="step", description="keyframe step", default=1, min=1, options={"HIDDEN"}
    )


class PTDBLNPOPM_anim_mirror(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(
        name="mirror", description="target mirror", default=False, options={"HIDDEN"}
    )
    cycles: bpy.props.IntProperty(
        name="repeat", description="mirror cycles", default=1, min=1, options={"HIDDEN"}
    )


class PTDBLNPOPM_anim_amount(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(
        name="factor", description="animate factor", default=False, options={"HIDDEN"}
    )
    fac: bpy.props.FloatProperty(
        name="target", description="factor", default=0, options={"HIDDEN"}
    )
    mirror: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_mirror)


class PTDBLNPOPM_anim_rots(bpy.types.PropertyGroup):
    active: bpy.props.BoolProperty(
        name="rotate", description="animate rotation", default=False, options={"HIDDEN"}
    )
    fac: bpy.props.FloatProperty(
        name="angle",
        description="[degrees] to rotate per keyframe",
        default=0,
        min=-3.14,
        max=3.14,
        subtype="ANGLE",
        options={"HIDDEN"},
    )
    beg: bpy.props.IntProperty(
        name="start", description="from keyframe", default=1, min=1, options={"HIDDEN"}
    )
    end: bpy.props.IntProperty(
        name="end", description="to keyframe", default=1, min=1, options={"HIDDEN"}
    )


class PTDBLNPOPM_params(bpy.types.PropertyGroup):
    def params_npts_update(self, context):
        self.idx = self.get("idx", 0)
        self.itm = self.get("itm", 1)

    def params_idx_get(self):
        return self.get("idx", 0)

    def params_idx_set(self, value):
        den = self.get("npts", 1)
        self["idx"] = value % den

    def params_itm_get(self):
        return self.get("itm", 1)

    def params_itm_set(self, value):
        self["itm"] = min(max(1, value), self.get("npts", 1))

    def params_itm_update(self, context):
        self.gap = self.get("gap", 0)

    def params_gap_get(self):
        return self.get("gap", 0)

    def params_gap_set(self, value):
        hi = max(0, self.get("npts", 1) - self.get("itm", 1))
        self["gap"] = min(max(0, value), hi)

    def params_gap_update(self, context):
        self.reps = self.get("reps", 1)

    def params_reps_get(self):
        return self.get("reps", 1)

    def params_reps_set(self, value):
        num = self.get("npts", 1)
        itm = self.get("itm", 1)
        den = itm + self.get("gap", 0)
        hi = num // den
        hi += 0 if num % den < itm else 1
        self["reps"] = min(max(1, value), hi)

    def params_reps_update(self, context):
        self.repflip = self.get("repflip", 0)

    def params_repfstp_get(self):
        return self.get("repfstp", 1)

    def params_repfstp_set(self, value):
        self["repfstp"] = min(max(1, value), self.get("reps", 1))

    npts: bpy.props.IntProperty(default=12, update=params_npts_update)
    ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=(
            ("OFF", "off", "no interpolation"),
            ("LINEAR", "linear", "linear"),
            ("IN", "in", "ease in"),
            ("OUT", "out", "ease out"),
            ("IN-OUT", "in-out", "ease in and out"),
        ),
        default="OFF",
    )
    exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    cyc: bpy.props.BoolProperty(
        name="lag", description="interpolation excludes last increment", default=False
    )
    mir: bpy.props.BoolProperty(
        name="mirror", description="interpolation mirror", default=False
    )
    rev: bpy.props.BoolProperty(
        name="reverse", description="reverse direction", default=False
    )
    reflect: bpy.props.EnumProperty(
        name="reflect",
        description="inverted interpolation values",
        items=(
            ("0", "none", "do not use"),
            ("1", "all", "reflect all"),
            ("2", "highs", "filter lows"),
            ("3", "lows", "filter highs"),
        ),
        default="0",
    )
    idx: bpy.props.IntProperty(
        name="offset",
        description="index offset",
        default=0,
        get=params_idx_get,
        set=params_idx_set,
    )
    itm: bpy.props.IntProperty(
        name="items",
        description="group items",
        default=1,
        get=params_itm_get,
        set=params_itm_set,
        update=params_itm_update,
    )
    gap: bpy.props.IntProperty(
        name="gap",
        description="number of items between groups",
        default=0,
        get=params_gap_get,
        set=params_gap_set,
        update=params_gap_update,
    )
    reps: bpy.props.IntProperty(
        name="groups",
        description="number of groups",
        default=1,
        get=params_reps_get,
        set=params_reps_set,
        update=params_reps_update,
    )
    repfstp: bpy.props.IntProperty(
        name="step",
        description="falloff step",
        default=1,
        get=params_repfstp_get,
        set=params_repfstp_set,
    )
    repfoff: bpy.props.FloatProperty(
        name="step factor", description="enhance-fade (falloff step factor)", default=1
    )

    def to_dct(self, exclude=set()):
        d = {}
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            d[key] = getattr(self, key)
        return d


class PTDBLNPOPM_pathloc(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Location")
    active: bpy.props.BoolProperty(default=False)
    fac: bpy.props.FloatProperty(default=0)
    axis: bpy.props.FloatVectorProperty(size=3, default=(1, 1, 1))
    abs_move: bpy.props.BoolProperty(default=False)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)
    ani_fac: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_amount)

    def anim_state(self):
        return self.ani_nidx.active or self.ani_fac.active

    def to_dct(self):
        d = {"fac": self.fac, "axis": self.axis, "abs_move": self.abs_move}
        d["nprams"] = self.nprams.to_dct()
        return d


class PTDBLNPOPM_pathrot(bpy.types.PropertyGroup):
    def pathrot_active_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.pop_simple_update()

    active: bpy.props.BoolProperty(
        name="toggle",
        description="enable/disable rotation",
        default=False,
        update=pathrot_active_update,
        options={"HIDDEN"},
    )
    axis: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 1))
    angle: bpy.props.FloatProperty(default=0, subtype="ANGLE")
    pivot: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    piv_object: bpy.props.BoolProperty(default=False)
    batt: bpy.props.BoolProperty(default=False)
    ani_rot: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_rots)

    def anim_state(self):
        return self.ani_rot.active


class PTDBLNPOPM_profloc(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Location")
    active: bpy.props.BoolProperty(default=False)
    fac: bpy.props.FloatProperty(default=0)
    axis: bpy.props.FloatVectorProperty(size=3, default=(1, 1, 0))
    abs_move: bpy.props.BoolProperty(default=False)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)
    ani_fac: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_amount)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)

    def anim_state(self):
        return self.ani_nidx.active or self.ani_fac.active or self.ani_idx.active

    def to_dct(self):
        d = {"fac": self.fac, "axis": self.axis, "abs_move": self.abs_move}
        d["nprams"] = self.nprams.to_dct()
        d["iprams"] = self.iprams.to_dct()
        return d


class PTDBLNPOPM_profrot(bpy.types.PropertyGroup):
    def profrot_active_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.pop_simple_update()

    active: bpy.props.BoolProperty(
        name="toggle",
        description="enable/disable rotation",
        default=False,
        update=profrot_active_update,
        options={"HIDDEN"},
    )
    roll: bpy.props.FloatProperty(default=0, subtype="ANGLE")
    twist: bpy.props.FloatProperty(default=0, subtype="ANGLE")
    follow_limit: bpy.props.BoolProperty(default=True)
    ani_rot: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_rots)

    def anim_state(self):
        return self.ani_rot.active


def path_prof_lerp_items():
    items = (
        ("LINEAR", "linear", "linear"),
        ("IN", "in", "ease in"),
        ("OUT", "out", "ease out"),
        ("IN-OUT", "in-out", "ease in and out"),
    )
    return items


class PTDBLNPOPM_pathed(bpy.types.PropertyGroup):
    def pathed_npts_update(self, context):
        self.ellstep = self.get("ellstep", 1)
        self.pol_sid = self.get("pol_sid", 3)

    def pathed_ellstep_get(self):
        return self.get("ellstep", 1)

    def pathed_ellstep_set(self, value):
        hi = max(1, self.get("npts", 1) // 2)
        self["ellstep"] = min(max(1, value), hi)

    def pathed_polsid_get(self):
        return self.get("pol_sid", 3)

    def pathed_polsid_set(self, value):
        hi = min(max(3, self.get("npts", 1) // 2), 20)
        self["pol_sid"] = min(max(3, value), hi)

    def pathed_polcoff_get(self):
        return self.get("pol_coff", 0)

    def pathed_polcoff_set(self, value):
        self["pol_coff"] = 0 if value < 0.001 else value

    def pathed_polsidcoff_update(self, context):
        self.pol_cres = self.get("pol_cres", 0)

    def pathed_polcres_get(self):
        return self.get("pol_cres", 0)

    def pathed_polcres_set(self, value):
        if not self.pol_coff:
            self["pol_cres"] = 0
        else:
            npts = self.get("npts", 3)
            sides = min(npts // 2, self.pol_sid)
            xtra = npts - 2 * sides
            seg = (2 * sides + xtra - xtra % sides) // sides - 1
            self["pol_cres"] = min(max(0, value), seg)

    npts: bpy.props.IntProperty(default=12, update=pathed_npts_update)
    user_dim: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    user_piv: bpy.props.FloatVectorProperty(
        name="pivot",
        description="custom shape origin",
        size=3,
        default=(0, 0, 0),
    )
    upv: bpy.props.CollectionProperty(type=PTDBLNPOPM_vec3)
    cust_dim: bpy.props.FloatVectorProperty(
        name="size", description="path dimensions", size=3, default=(8, 8, 8)
    )
    lin_dim: bpy.props.FloatProperty(name="length", description="length", default=8)
    lin_ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=path_prof_lerp_items(),
        default="LINEAR",
    )
    lin_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    wav_dim: bpy.props.FloatProperty(name="length", description="length", default=8)
    wav_amp: bpy.props.FloatProperty(
        name="amplitude", description="amplitude", default=0.5
    )
    wav_frq: bpy.props.FloatProperty(
        name="frequency", description="wave cycles", default=1
    )
    wav_pha: bpy.props.FloatProperty(name="phase", description="angle shift", default=0)
    arc_dim: bpy.props.FloatProperty(
        name="chord",
        description="chord length",
        default=8,
    )
    arc_fac: bpy.props.FloatProperty(
        name="factor",
        description="variant factor of radius vs. sagitta",
        default=4,
    )
    arc_off: bpy.props.FloatProperty(
        name="offset",
        description="circle center offset",
        default=0,
    )
    ell_dim: bpy.props.FloatVectorProperty(
        name="size", description="ellipse dimensions", size=2, default=(8, 8)
    )
    ellstep: bpy.props.IntProperty(
        name="steps",
        description="interpolation steps",
        default=1,
        get=pathed_ellstep_get,
        set=pathed_ellstep_set,
    )
    ellstep_val: bpy.props.FloatProperty(name="factor", description="amount", default=0)
    ellstep_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    pol_dim: bpy.props.FloatVectorProperty(
        name="size", description="polygon dimensions", size=2, default=(8, 8)
    )
    pol_sid: bpy.props.IntProperty(
        name="sides",
        description="polygon sides",
        default=3,
        get=pathed_polsid_get,
        set=pathed_polsid_set,
        update=pathed_polsidcoff_update,
    )
    pol_coff: bpy.props.FloatProperty(
        name="offset",
        description="bevel offset",
        default=0.1,
        get=pathed_polcoff_get,
        set=pathed_polcoff_set,
        update=pathed_polsidcoff_update,
    )
    pol_cres: bpy.props.IntProperty(
        name="segments",
        description="bevel segments",
        default=0,
        get=pathed_polcres_get,
        set=pathed_polcres_set,
    )
    pol_ang: bpy.props.FloatProperty(
        name="slope",
        description="polygon start angle",
        default=0,
        subtype="ANGLE",
    )
    pol_ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=path_prof_lerp_items(),
        default="LINEAR",
    )
    pol_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    hel_dim: bpy.props.FloatVectorProperty(
        name="size", description="width", size=2, default=(8, 8)
    )
    hel_len: bpy.props.FloatProperty(name="size", description="length", default=8)
    hel_stp: bpy.props.FloatProperty(
        name="frequency", description="revolutions", default=2
    )
    hel_fac: bpy.props.FloatProperty(
        name="width factor", description="grow / shrink", default=1
    )
    hel_pha: bpy.props.FloatProperty(name="phase", description="angle shift", default=0)
    hel_invert: bpy.props.BoolProperty(
        name="invert", description="inverted width factor", default=False
    )
    hel_hlrp: bpy.props.BoolProperty(
        name="length", description="interpolate length", default=False
    )
    hel_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    hel_mir: bpy.props.BoolProperty(
        name="mirror", description="width interpolation mirror", default=False
    )
    hel_ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=path_prof_lerp_items(),
        default="LINEAR",
    )
    spi_dim: bpy.props.FloatProperty(
        name="diameter",
        description="spherical spiral diameter",
        default=8,
    )
    spi_revs: bpy.props.FloatProperty(
        name="frequency", description="revolutions", default=1
    )

    def pathed_orientation_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.pop_simple_update()

    def pathed_closed_update(self, context):
        if self.closed:
            self.endcaps = False
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.pop_simple_update()

    def pathed_endcaps_update(self, context):
        if self.closed:
            return None
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.pop_simple_update()

    upfixed: bpy.props.BoolProperty(
        name="fixed up",
        description="fixed up-axis orientation",
        default=False,
        update=pathed_orientation_update,
        options={"HIDDEN"},
    )
    upaxis: bpy.props.EnumProperty(
        name="up axis",
        description="up-axis selection",
        items=(("X", "X", "X axis"), ("Y", "Y", "Y axis")),
        default="Y",
        update=pathed_orientation_update,
        options={"HIDDEN"},
    )
    closed: bpy.props.BoolProperty(
        name="closed",
        description="closed or open path",
        default=False,
        update=pathed_closed_update,
        options={"HIDDEN"},
    )
    endcaps: bpy.props.BoolProperty(
        name="endcaps",
        description="end cap (polygonal face) for open path",
        default=False,
        update=pathed_endcaps_update,
        options={"HIDDEN"},
    )

    def to_dct(self, exclude=set()):
        d = {}
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            if key == "upv":
                d[key] = [i.vert for i in self.upv]
            else:
                d[key] = getattr(self, key)
        return d


class PTDBLNPOPM_path(bpy.types.PropertyGroup):
    def path_provider_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.setup_provider(caller="path")

    def path_res_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.update_preset(caller="path")

    def path_user_ob_check(self, object):
        return object.type == "MESH"

    def path_user_ob_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.setup_provider(caller="path")

    clean: bpy.props.BoolProperty(default=False)
    provider: bpy.props.EnumProperty(
        name="path",
        description="path selection",
        items=(
            ("line", "line", "line"),
            ("wave", "wave", "wave"),
            ("arc", "arc", "arc"),
            ("ellipse", "ellipse", "ellipse"),
            ("polygon", "polygon", "polygon"),
            ("helix", "helix", "helix"),
            ("spiral", "spiral", "spherical spiral"),
            ("custom", "custom", "user path"),
        ),
        default="line",
        update=path_provider_update,
        options={"HIDDEN"},
    )
    res_lin: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=12,
        min=3,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_wav: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=12,
        min=3,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_arc: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=12,
        min=3,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_ell: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=12,
        min=3,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_pol: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=12,
        min=6,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_hel: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=24,
        min=4,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    res_spi: bpy.props.IntProperty(
        name="nodes",
        description="path resolution",
        default=24,
        min=4,
        soft_max=100,
        update=path_res_update,
        options={"HIDDEN"},
    )
    user_ob: bpy.props.PointerProperty(
        name="mesh object",
        description="custom path provider",
        type=bpy.types.Object,
        poll=path_user_ob_check,
        update=path_user_ob_update,
    )
    pathed: bpy.props.PointerProperty(type=PTDBLNPOPM_pathed)
    ani_dim: bpy.props.BoolProperty(
        name="size", description="animate dimensions", default=False, options={"HIDDEN"}
    )
    ani_dim_mirror: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_mirror)
    ani_lin_dim: bpy.props.FloatProperty(
        name="target",
        description="length",
        default=8,
        options={"HIDDEN"},
    )
    ani_wav_dim: bpy.props.FloatProperty(
        name="target",
        description="length",
        default=8,
        options={"HIDDEN"},
    )
    ani_arc_dim: bpy.props.FloatProperty(
        name="target",
        description="chord",
        default=8,
        options={"HIDDEN"},
    )
    ani_spi_dim: bpy.props.FloatProperty(
        name="target",
        description="diameter",
        default=8,
        options={"HIDDEN"},
    )
    ani_dim_2d: bpy.props.FloatVectorProperty(
        name="target",
        description="size",
        size=2,
        default=(8, 8),
        options={"HIDDEN"},
    )
    ani_dim_3d: bpy.props.FloatVectorProperty(
        name="target",
        description="size",
        size=3,
        default=(8, 8, 8),
        options={"HIDDEN"},
    )
    ani_fac: bpy.props.BoolProperty(
        name="factor", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac_mirror: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_mirror)
    ani_fac2: bpy.props.BoolProperty(
        name="factor2", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac2_mirror: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_mirror)
    ani_fac3: bpy.props.BoolProperty(
        name="factor3", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac3_mirror: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_mirror)
    ani_fac4: bpy.props.BoolProperty(
        name="factor4", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac4_mirror: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_mirror)
    ani_lin_exp: bpy.props.FloatProperty(
        name="target",
        description="exponent",
        default=2,
        min=0.2,
        max=5,
        options={"HIDDEN"},
    )
    ani_wav_amp: bpy.props.FloatProperty(
        name="target", description="amplitude", default=0.5, options={"HIDDEN"}
    )
    ani_wav_frq: bpy.props.FloatProperty(
        name="target", description="frequency", default=1, options={"HIDDEN"}
    )
    ani_wav_pha: bpy.props.FloatProperty(
        name="target", description="phase", default=0, options={"HIDDEN"}
    )
    ani_arc_fac: bpy.props.FloatProperty(
        name="target", description="factor", default=4, options={"HIDDEN"}
    )
    ani_ellstep_val: bpy.props.FloatProperty(
        name="target", description="factor", default=0, options={"HIDDEN"}
    )
    ani_hel_len: bpy.props.FloatProperty(
        name="target", description="length", default=8, options={"HIDDEN"}
    )
    ani_hel_fac: bpy.props.FloatProperty(
        name="target", description="width factor", default=1, options={"HIDDEN"}
    )
    ani_hel_stp: bpy.props.FloatProperty(
        name="target", description="frequency", default=2, options={"HIDDEN"}
    )
    ani_hel_pha: bpy.props.FloatProperty(
        name="target", description="phase", default=0, options={"HIDDEN"}
    )
    ani_spi_revs: bpy.props.FloatProperty(
        name="target", description="frequency", default=1, options={"HIDDEN"}
    )

    def anim_state(self):
        if self.ani_dim:
            return True
        provider = self.provider
        if provider == "helix" and (self.ani_fac2 or self.ani_fac3 or self.ani_fac4):
            return True
        if provider == "wave" and (self.ani_fac2 or self.ani_fac3):
            return True
        fac_paths = {"wave", "arc", "helix", "spiral", "line", "ellipse"}
        return self.ani_fac and (provider in fac_paths)

    def to_dct(self):
        d = dict.fromkeys(
            (
                "provider",
                "res_lin",
                "res_wav",
                "res_arc",
                "res_ell",
                "res_pol",
                "res_hel",
                "res_spi",
            )
        )
        for key in d.keys():
            d[key] = getattr(self, key)
        xvs = set() if self.provider == "custom" else {"upv"}
        d.update(self.pathed.to_dct(exclude=xvs))
        return d


class PTDBLNPOPM_profed(bpy.types.PropertyGroup):
    def profed_npts_update(self, context):
        self.idx = self.get("idx", 0)
        self.ellstep = self.get("ellstep", 1)
        self.pol_sid = self.get("pol_sid", 3)

    def profed_idx_get(self):
        return self.get("idx", 0)

    def profed_idx_set(self, value):
        den = self.get("npts", 1)
        self["idx"] = value % den

    def profed_ellstep_get(self):
        return self.get("ellstep", 1)

    def profed_ellstep_set(self, value):
        hi = max(1, self.get("npts", 1) // 2)
        self["ellstep"] = min(max(1, value), hi)

    def profed_polsid_get(self):
        return self.get("pol_sid", 3)

    def profed_polsid_set(self, value):
        hi = min(max(3, self.get("npts", 1) // 2), 20)
        self["pol_sid"] = min(max(3, value), hi)

    def profed_polcoff_get(self):
        return self.get("pol_coff", 0)

    def profed_polcoff_set(self, value):
        self["pol_coff"] = 0 if value < 0.001 else value

    def profed_polsidcoff_update(self, context):
        self.pol_cres = self.get("pol_cres", 0)

    def profed_polcres_get(self):
        return self.get("pol_cres", 0)

    def profed_polcres_set(self, value):
        if not self.pol_coff:
            self["pol_cres"] = 0
        else:
            npts = self.get("npts", 3)
            sides = min(npts // 2, self.get("pol_sid", 3))
            xtra = npts - 2 * sides
            seg = (2 * sides + xtra - xtra % sides) // sides - 1
            self["pol_cres"] = min(max(0, value), seg)

    npts: bpy.props.IntProperty(default=12, update=profed_npts_update)
    user_dim: bpy.props.FloatVectorProperty(size=2, default=(0, 0))
    user_piv: bpy.props.FloatVectorProperty(
        name="pivot",
        description="custom shape origin",
        size=3,
        default=(0, 0, 0),
    )
    upv: bpy.props.CollectionProperty(type=PTDBLNPOPM_vec3)
    cust_dim: bpy.props.FloatVectorProperty(
        name="size", description="profile dimensions", size=2, default=(2, 2)
    )
    lin_dim: bpy.props.FloatProperty(name="length", description="length", default=2)
    lin_ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=path_prof_lerp_items(),
        default="LINEAR",
    )
    lin_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    wav_dim: bpy.props.FloatProperty(name="length", description="length", default=2)
    wav_amp: bpy.props.FloatProperty(
        name="amplitude", description="amplitude", default=0.5
    )
    wav_frq: bpy.props.FloatProperty(
        name="frequency", description="wave cycles", default=1
    )
    wav_pha: bpy.props.FloatProperty(name="phase", description="angle shift", default=0)
    arc_dim: bpy.props.FloatProperty(
        name="chord",
        description="chord length",
        default=2,
    )
    arc_fac: bpy.props.FloatProperty(
        name="factor",
        description="variant factor of radius vs. sagitta",
        default=1,
    )
    arc_off: bpy.props.FloatProperty(
        name="offset",
        description="circle center offset",
        default=0,
    )
    ell_dim: bpy.props.FloatVectorProperty(
        name="size", description="ellipse dimensions", size=2, default=(2, 2)
    )
    ellstep: bpy.props.IntProperty(
        name="steps",
        description="interpolation steps",
        default=1,
        get=profed_ellstep_get,
        set=profed_ellstep_set,
    )
    ellstep_val: bpy.props.FloatProperty(name="factor", description="amount", default=0)
    ellstep_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    pol_dim: bpy.props.FloatVectorProperty(
        name="size", description="polygon dimensions", size=2, default=(2, 2)
    )
    pol_sid: bpy.props.IntProperty(
        name="sides",
        description="polygon sides",
        default=3,
        get=profed_polsid_get,
        set=profed_polsid_set,
        update=profed_polsidcoff_update,
    )
    pol_coff: bpy.props.FloatProperty(
        name="offset",
        description="bevel offset",
        default=0.1,
        get=profed_polcoff_get,
        set=profed_polcoff_set,
        update=profed_polsidcoff_update,
    )
    pol_cres: bpy.props.IntProperty(
        name="segments",
        description="bevel segments",
        default=0,
        get=profed_polcres_get,
        set=profed_polcres_set,
    )
    pol_ang: bpy.props.FloatProperty(
        name="slope",
        description="polygon start angle",
        default=0,
        subtype="ANGLE",
    )
    pol_ease: bpy.props.EnumProperty(
        name="ease",
        description="interpolation type",
        items=path_prof_lerp_items(),
        default="LINEAR",
    )
    pol_exp: bpy.props.FloatProperty(
        name="exponent",
        description="interpolation exponent",
        default=2,
        min=0.2,
        max=5,
    )
    idx: bpy.props.IntProperty(
        name="offset",
        description="index offset",
        default=0,
        get=profed_idx_get,
        set=profed_idx_set,
    )
    rot_align: bpy.props.FloatProperty(
        name="angle",
        description="rotation",
        default=0,
        subtype="ANGLE",
    )

    def profed_closed_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.pop_simple_update()

    closed: bpy.props.BoolProperty(
        name="closed",
        description="closed or open profile",
        default=False,
        update=profed_closed_update,
        options={"HIDDEN"},
    )

    def to_dct(self, exclude=set()):
        d = {}
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            if key == "upv":
                d[key] = [i.vert for i in self.upv]
            else:
                d[key] = getattr(self, key)
        return d


def prof_blnd_provider_items():
    items = (
        ("line", "line", "line"),
        ("wave", "wave", "wave"),
        ("arc", "arc", "arc"),
        ("ellipse", "ellipse", "ellipse"),
        ("polygon", "polygon", "polygon"),
        ("custom", "custom", "user profile"),
    )
    return items


class PTDBLNPOPM_prof(bpy.types.PropertyGroup):
    def prof_provider_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.setup_provider(caller="prof")

    def prof_res_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.update_preset(caller="prof")

    def prof_user_ob_check(self, object):
        return object.type == "MESH"

    def prof_user_ob_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.setup_provider(caller="prof")

    clean: bpy.props.BoolProperty(default=False)
    provider: bpy.props.EnumProperty(
        name="profile",
        description="profile selection",
        items=prof_blnd_provider_items(),
        default="line",
        update=prof_provider_update,
        options={"HIDDEN"},
    )
    res_lin: bpy.props.IntProperty(
        name="points",
        description="profile resolution",
        default=12,
        min=3,
        soft_max=100,
        update=prof_res_update,
        options={"HIDDEN"},
    )
    res_wav: bpy.props.IntProperty(
        name="points",
        description="profile resolution",
        default=12,
        min=3,
        soft_max=100,
        update=prof_res_update,
        options={"HIDDEN"},
    )
    res_arc: bpy.props.IntProperty(
        name="points",
        description="profile resolution",
        default=12,
        min=3,
        soft_max=100,
        update=prof_res_update,
        options={"HIDDEN"},
    )
    res_ell: bpy.props.IntProperty(
        name="points",
        description="profile resolution",
        default=12,
        min=3,
        soft_max=100,
        update=prof_res_update,
        options={"HIDDEN"},
    )
    res_pol: bpy.props.IntProperty(
        name="points",
        description="profile resolution",
        default=12,
        min=6,
        soft_max=100,
        update=prof_res_update,
        options={"HIDDEN"},
    )
    user_ob: bpy.props.PointerProperty(
        name="mesh object",
        description="custom profile provider",
        type=bpy.types.Object,
        poll=prof_user_ob_check,
        update=prof_user_ob_update,
    )
    profed: bpy.props.PointerProperty(type=PTDBLNPOPM_profed)
    ani_dim: bpy.props.BoolProperty(
        name="size", description="animate dimensions", default=False, options={"HIDDEN"}
    )
    ani_dim_mirror: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_mirror)
    ani_lin_dim: bpy.props.FloatProperty(
        name="target",
        description="length",
        default=2,
        options={"HIDDEN"},
    )
    ani_wav_dim: bpy.props.FloatProperty(
        name="target",
        description="length",
        default=2,
        options={"HIDDEN"},
    )
    ani_arc_dim: bpy.props.FloatProperty(
        name="target",
        description="chord",
        default=2,
        options={"HIDDEN"},
    )
    ani_epc_dim: bpy.props.FloatVectorProperty(
        name="target",
        description="size",
        size=2,
        default=(2, 2),
        options={"HIDDEN"},
    )
    ani_fac: bpy.props.BoolProperty(
        name="factor", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac_mirror: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_mirror)
    ani_fac2: bpy.props.BoolProperty(
        name="factor 2", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac2_mirror: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_mirror)
    ani_fac3: bpy.props.BoolProperty(
        name="factor 3", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac3_mirror: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_mirror)
    ani_lin_exp: bpy.props.FloatProperty(
        name="target",
        description="exponent",
        default=2,
        min=0.2,
        max=5,
        options={"HIDDEN"},
    )
    ani_wav_amp: bpy.props.FloatProperty(
        name="target", description="amplitude", default=0.5, options={"HIDDEN"}
    )
    ani_wav_frq: bpy.props.FloatProperty(
        name="target", description="frequency", default=1, options={"HIDDEN"}
    )
    ani_wav_pha: bpy.props.FloatProperty(
        name="target", description="phase", default=0, options={"HIDDEN"}
    )
    ani_arc_fac: bpy.props.FloatProperty(
        name="target", description="factor", default=1, options={"HIDDEN"}
    )
    ani_ellstep_val: bpy.props.FloatProperty(
        name="target", description="factor", default=0, options={"HIDDEN"}
    )

    def anim_state(self):
        if self.ani_dim:
            return True
        if self.provider == "wave" and (self.ani_fac2 or self.ani_fac3):
            return True
        fac_profs = {"wave", "arc", "line", "ellipse"}
        return self.ani_fac and (self.provider in fac_profs)

    def to_dct(self):
        d = dict.fromkeys(
            (
                "provider",
                "res_lin",
                "res_wav",
                "res_arc",
                "res_ell",
                "res_pol",
            )
        )
        for key in d.keys():
            d[key] = getattr(self, key)
        xvs = set() if self.provider == "custom" else {"upv"}
        d.update(self.profed.to_dct(exclude=xvs))
        return d


class PTDBLNPOPM_blnd(bpy.types.PropertyGroup):
    def blnd_provider_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.setup_blnd_provider()

    def blnd_user_ob_check(self, object):
        return object.type == "MESH"

    def blnd_user_ob_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.setup_blnd_provider()

    name: bpy.props.StringProperty(default="Blend")
    provider: bpy.props.EnumProperty(
        name="blend profile",
        description="blend profile selection",
        items=prof_blnd_provider_items(),
        default="line",
        update=blnd_provider_update,
        options={"HIDDEN"},
    )
    user_ob: bpy.props.PointerProperty(
        name="mesh object",
        description="custom blend profile provider",
        type=bpy.types.Object,
        poll=blnd_user_ob_check,
        update=blnd_user_ob_update,
    )
    active: bpy.props.BoolProperty(default=False)
    blnded: bpy.props.PointerProperty(type=PTDBLNPOPM_profed)
    fac: bpy.props.FloatProperty(default=0)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    ani_nidx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)
    ani_fac: bpy.props.BoolProperty(
        name="factor", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_fac_val: bpy.props.FloatProperty(
        name="target",
        default=0,
        description="blend factor",
        min=-1,
        max=1,
        options={"HIDDEN"},
    )
    ani_fac_mirror: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_mirror)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)

    def anim_state(self):
        return self.ani_nidx.active or self.ani_fac or self.ani_idx.active

    def to_dct(self):
        d = {"provider": self.provider, "fac": self.fac}
        xvs = set() if self.provider == "custom" else {"upv"}
        d.update(self.blnded.to_dct(exclude=xvs))
        d["nprams"] = self.nprams.to_dct()
        d["iprams"] = self.iprams.to_dct()
        return d


class PTDBLNPOPM_noiz(bpy.types.PropertyGroup):
    def noiz_active_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.pop_simple_update()

    active: bpy.props.BoolProperty(
        name="toggle",
        description="enable/disable noise",
        default=False,
        update=noiz_active_update,
        options={"HIDDEN"},
    )
    ampli: bpy.props.FloatProperty(default=0)
    vfac: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    nseed: bpy.props.IntProperty(default=0)
    ani_noiz: bpy.props.BoolProperty(
        name="noise",
        description="animate noise",
        default=False,
        options={"HIDDEN"},
    )
    ani_seed: bpy.props.BoolProperty(
        name="clock seed",
        description="animated seed",
        default=False,
        options={"HIDDEN"},
    )
    ani_blin: bpy.props.IntProperty(
        name="blend-in",
        description="number of keyframes to full effect",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    ani_blout: bpy.props.IntProperty(
        name="blend-out",
        description="number of keyframes to no effect",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    ani_stp: bpy.props.IntProperty(
        name="step", description="keyframe step", default=1, min=1, options={"HIDDEN"}
    )

    def anim_state(self):
        return self.ani_noiz


class PTDBLNPOPM_track(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="Track")
    t_name: bpy.props.StringProperty(default="name")
    active: bpy.props.BoolProperty(default=True)
    ac_beg: bpy.props.IntProperty(default=1)
    ac_end: bpy.props.IntProperty(default=2)
    s_sca: bpy.props.FloatProperty(default=1)
    s_rep: bpy.props.FloatProperty(default=1)
    sa_beg: bpy.props.IntProperty(default=1)
    sa_end: bpy.props.IntProperty(default=2)
    s_beg: bpy.props.IntProperty(default=1)
    s_end: bpy.props.IntProperty(default=2)
    s_blend: bpy.props.StringProperty(default="REPLACE")
    s_blauto: bpy.props.BoolProperty(default=False)
    s_blin: bpy.props.IntProperty(default=0)
    s_blout: bpy.props.IntProperty(default=0)
    s_xpl: bpy.props.StringProperty(default="HOLD")
    s_bak: bpy.props.BoolProperty(default=False)
    st_warp: bpy.props.BoolProperty(default=False)
    st_curve: bpy.props.StringProperty(default="12")
    st_ease: bpy.props.StringProperty(default="0")
    st_ctrl: bpy.props.BoolProperty(default=False)
    st_fra: bpy.props.IntProperty(default=1)

    def to_dct(self, exclude=set()):
        d = {}
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            d[key] = getattr(self, key)
        return d


class PTDBLNPOPM_rngs(bpy.types.PropertyGroup):
    def rngs_common_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.pop_simple_update()

    active: bpy.props.BoolProperty(default=False)
    invert: bpy.props.BoolProperty(
        name="invert",
        description="invert selections",
        default=False,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    rndsel: bpy.props.BoolProperty(
        name="randomize",
        description="random selections",
        default=False,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    rbeg: bpy.props.IntProperty(
        name="path: offset",
        description="index offset",
        default=0,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    ritm: bpy.props.IntProperty(
        name="path: items",
        description="group items",
        default=1,
        min=1,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    rgap: bpy.props.IntProperty(
        name="path: gap",
        description="number of items between groups",
        default=0,
        min=0,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    rstp: bpy.props.IntProperty(
        name="path: groups",
        description="number of groups",
        default=1,
        min=1,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    pbeg: bpy.props.IntProperty(
        name="profile: offset",
        description="index offset",
        default=0,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    pitm: bpy.props.IntProperty(
        name="profile: items",
        description="group items",
        default=1,
        min=1,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    pgap: bpy.props.IntProperty(
        name="profile: gap",
        description="number of items between groups",
        default=0,
        min=0,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    pstp: bpy.props.IntProperty(
        name="profile: groups",
        description="number of groups",
        default=1,
        min=1,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    nseed: bpy.props.IntProperty(
        name="seed",
        description="random seed",
        default=0,
        min=0,
        update=rngs_common_update,
        options={"HIDDEN"},
    )
    _sindz = {"data": set()}

    def sindz_get(self):
        return self._sindz["data"]

    def sindz_set(self, value):
        self._sindz["data"] = value


class PTDBLNPOPM_meshrot(bpy.types.PropertyGroup):
    def meshrot_active_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.update_ok:
            bpy.ops.ptdblnpopm.pop_simple_update()

    active: bpy.props.BoolProperty(
        name="toggle",
        description="enable/disable rotation",
        default=False,
        update=meshrot_active_update,
        options={"HIDDEN"},
    )
    axis: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 1))
    angle: bpy.props.FloatProperty(default=0, subtype="ANGLE")
    pivot: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    ani_rot: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_rots)

    def anim_state(self):
        return self.ani_rot.active


class PTDBLNPOPM_anicalc(bpy.types.PropertyGroup):
    info: bpy.props.StringProperty(name="results", description="results", default="")

    def anicalc_type_update(self, context):
        bpy.ops.ptdblnpopm.anicalc(current=False)

    calc_type: bpy.props.EnumProperty(
        name="calculation",
        description="calculation",
        items=(
            ("offsets", "offsets", "index offsets from items"),
            ("loop", "loop", "loop from [items, offset, start, step]"),
            ("cycles", "cycles", "mirror cycles from loop"),
            ("strip", "time scale", "strip time scale from control frame and function"),
        ),
        default="offsets",
        update=anicalc_type_update,
        options={"HIDDEN"},
    )
    loop: bpy.props.IntProperty(
        name="loop",
        description="total keyframes",
        default=5,
        min=2,
        options={"HIDDEN"},
    )
    items: bpy.props.IntProperty(
        name="items",
        description="items (nodes or points)",
        default=12,
        min=3,
        options={"HIDDEN"},
    )

    def anicalc_offset_get(self):
        return self.get("offset", 1)

    def anicalc_offset_set(self, value):
        den = self.get("items", 3) - 1
        self["offset"] = max(1, value % den)

    offset: bpy.props.IntProperty(
        name="offset",
        description="index offset",
        default=1,
        get=anicalc_offset_get,
        set=anicalc_offset_set,
        options={"HIDDEN"},
    )
    start: bpy.props.IntProperty(
        name="start",
        description="start keyframe",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    step: bpy.props.IntProperty(
        name="step",
        description="keyframe step",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    exp: bpy.props.EnumProperty(
        name="timewarp curve",
        description="warp function",
        items=(
            ("2", "quad", "quadratic"),
            ("3", "cube", "cubic"),
            ("4", "quart", "quartic"),
            ("5", "quint", "quintic"),
        ),
        default="2",
        options={"HIDDEN"},
    )
    fra: bpy.props.IntProperty(
        name="frame",
        description="control frame",
        default=2,
        min=2,
        options={"HIDDEN"},
    )
    first: bpy.props.IntProperty(
        name="first",
        description="first frame",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    last: bpy.props.IntProperty(
        name="last",
        description="last frame",
        default=3,
        min=3,
        options={"HIDDEN"},
    )


class PTDBLNPOPM_pool(bpy.types.PropertyGroup):
    path: bpy.props.PointerProperty(type=PTDBLNPOPM_path)
    pathrot: bpy.props.PointerProperty(type=PTDBLNPOPM_pathrot)
    blnd: bpy.props.CollectionProperty(type=PTDBLNPOPM_blnd)
    blnd_idx: bpy.props.IntProperty(name="Blend", default=-1, options={"HIDDEN"})
    prof: bpy.props.PointerProperty(type=PTDBLNPOPM_prof)
    profrot: bpy.props.PointerProperty(type=PTDBLNPOPM_profrot)
    noiz: bpy.props.PointerProperty(type=PTDBLNPOPM_noiz)
    meshrot: bpy.props.PointerProperty(type=PTDBLNPOPM_meshrot)
    pathloc: bpy.props.CollectionProperty(type=PTDBLNPOPM_pathloc)
    pathloc_idx: bpy.props.IntProperty(name="Locs", default=-1, options={"HIDDEN"})
    profloc: bpy.props.CollectionProperty(type=PTDBLNPOPM_profloc)
    profloc_idx: bpy.props.IntProperty(name="Locs", default=-1, options={"HIDDEN"})
    rngs: bpy.props.PointerProperty(type=PTDBLNPOPM_rngs)
    trax: bpy.props.CollectionProperty(type=PTDBLNPOPM_track)
    trax_idx: bpy.props.IntProperty(name="Track", default=-1, options={"HIDDEN"})
    pop_mesh: bpy.props.PointerProperty(type=bpy.types.Object)
    anicalc: bpy.props.PointerProperty(type=PTDBLNPOPM_anicalc)
    update_ok: bpy.props.BoolProperty(default=True)
    replace_mesh: bpy.props.BoolProperty(
        name="replace mesh",
        description=(
            "if enabled, running any of the 'Load ...' commands "
            "will replace the current mesh"
        ),
        default=False,
        options={"HIDDEN"},
    )
    show_warn: bpy.props.BoolProperty(
        name="show warnings",
        description="show confirmation pop-ups",
        default=False,
        options={"HIDDEN"},
    )

    def pool_act_name_get(self):
        return self.get("act_name", "Action")

    def pool_act_name_set(self, value):
        v = value.strip()
        self["act_name"] = v if v else "Action"

    animorph: bpy.props.BoolProperty(default=False)
    ani_kf_type: bpy.props.EnumProperty(
        name="key_type",
        description="keyframe interpolation",
        items=(
            ("0", "Constant", "constant interpolation", 0),
            ("1", "Linear", "linear interpolation", 1),
            ("2", "Bezier", "bezier interpolation", 2),
        ),
        default="1",
        options={"HIDDEN"},
    )
    ani_kf_start: bpy.props.IntProperty(
        name="start",
        description="first keyframe number",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    ani_kf_step: bpy.props.IntProperty(
        name="step",
        description="frame-distance between two successive keyframes",
        default=10,
        min=1,
        options={"HIDDEN"},
    )
    ani_kf_loop: bpy.props.IntProperty(
        name="loop",
        description="number of keyframes to complete animation",
        default=5,
        min=2,
        options={"HIDDEN"},
    )
    act_name: bpy.props.StringProperty(
        name="name",
        description="action name",
        default="Action",
        get=pool_act_name_get,
        set=pool_act_name_set,
    )

    def pool_show_wire_update(self, context):
        if self.update_ok:
            bpy.ops.ptdblnpopm.display_options(option="show_wire")

    def pool_shade_smooth_update(self, context):
        if self.update_ok:
            bpy.ops.ptdblnpopm.display_options(option="shade_smooth")

    show_wire: bpy.props.BoolProperty(
        name="show wire",
        description="show wireframe",
        default=False,
        update=pool_show_wire_update,
        options={"HIDDEN"},
    )
    shade_smooth: bpy.props.BoolProperty(
        name="shade smooth",
        description="object smooth shading",
        default=False,
        update=pool_shade_smooth_update,
        options={"HIDDEN"},
    )

    def pop_anim_state_eval(self):
        if self.meshrot.active and self.meshrot.anim_state():
            return True
        if self.noiz.active and self.noiz.anim_state():
            return True
        if self.pathrot.active and self.pathrot.anim_state():
            return True
        if self.profrot.active and self.profrot.anim_state():
            return True
        if self.path.anim_state():
            return True
        if self.prof.anim_state():
            return True
        for item in self.pathloc:
            if item.active and item.anim_state():
                return True
        for item in self.profloc:
            if item.active and item.anim_state():
                return True
        for item in self.blnd:
            if item.active and item.anim_state():
                return True
        return False

    def to_dct(self):
        return {
            "meshrot_active": self.meshrot.active,
            "pathrot_active": self.pathrot.active,
            "twistang": self.profrot.twist if self.profrot.active else 0,
            "follow_limit": self.profrot.follow_limit,
        }

    def props_unset(self):
        exclude = {
            "pop_mesh",
            "update_ok",
            "replace_mesh",
            "show_warn",
            "show_wire",
            "shade_smooth",
            "anicalc",
        }
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            self.property_unset(key)


# ---- BMPGS OPERATORS


class PTDBLNPOPM_OT_path_edit(bpy.types.Operator):
    bl_label = "Edit [Path]"
    bl_idname = "ptdblnpopm.path_edit"
    bl_description = "path settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    provider: bpy.props.StringProperty(default="")
    pathed: bpy.props.PointerProperty(type=PTDBLNPOPM_pathed)

    def invoke(self, context, event):
        path = context.scene.ptdblnpopm_pool.path
        self.provider = path.provider
        xcl = {"upv", "closed", "endcaps", "upfixed", "upaxis"}
        d = path.pathed.to_dct(exclude=xcl)
        for key in d.keys():
            setattr(self.pathed, key, d[key])
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        path = pool.path
        xcl = {"npts", "upv", "closed", "endcaps", "upfixed", "upaxis"}
        d = self.pathed.to_dct(exclude=xcl)
        for key in d.keys():
            setattr(path.pathed, key, d[key])
        try:
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"path_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        cns = s.column(align=True)
        cvs = s.column(align=True)
        getattr(ModPDOP, self.provider)(cns, cvs, self.pathed)


class PTDBLNPOPM_OT_prof_edit(bpy.types.Operator):
    bl_label = "Edit [Profile]"
    bl_idname = "ptdblnpopm.prof_edit"
    bl_description = "profile settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    provider: bpy.props.StringProperty(default="")
    profed: bpy.props.PointerProperty(type=PTDBLNPOPM_profed)

    def invoke(self, context, event):
        prof = context.scene.ptdblnpopm_pool.prof
        self.provider = prof.provider
        d = prof.profed.to_dct(exclude={"upv", "closed", "reverse"})
        for key in d.keys():
            setattr(self.profed, key, d[key])
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        prof = pool.prof
        d = self.profed.to_dct(exclude={"npts", "upv", "closed", "reverse"})
        for key in d.keys():
            setattr(prof.profed, key, d[key])
        try:
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"prof_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        cns = s.column(align=True)
        cvs = s.column(align=True)
        getattr(ModPDOP, self.provider)(cns, cvs, self.profed, isprof=True)


class PTDBLNPOPM_OT_blnd_edit(bpy.types.Operator):
    bl_label = "Edit [Blend]"
    bl_idname = "ptdblnpopm.blnd_edit"
    bl_description = "blend profile settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    provider: bpy.props.StringProperty(default="")
    fac: bpy.props.FloatProperty(
        name="factor", description="blend factor", default=0, min=-1, max=1
    )
    selview: bpy.props.EnumProperty(
        name="options",
        description="view options",
        items=(
            ("blend", "blend", "blend"),
            ("points", "points", "points"),
            ("nodes", "nodes", "nodes"),
            ("all", "all", "all"),
        ),
        default="all",
    )
    blnded: bpy.props.PointerProperty(type=PTDBLNPOPM_profed)
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)

    def copy_from_pg(self, item):
        d = item.blnded.to_dct(exclude={"upv", "closed"})
        for key in d.keys():
            setattr(self.blnded, key, d[key])
        ipar = item.iprams.to_dct()
        npar = item.nprams.to_dct()
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(self.iprams, ikey, ipar[ikey])
            setattr(self.nprams, nkey, npar[nkey])

    def copy_to_pg(self, item):
        d = self.blnded.to_dct(exclude={"npts", "upv", "closed"})
        for key in d.keys():
            setattr(item.blnded, key, d[key])
        ipar = self.iprams.to_dct(exclude={"npts"})
        npar = self.nprams.to_dct(exclude={"npts"})
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(item.iprams, ikey, ipar[ikey])
            setattr(item.nprams, nkey, npar[nkey])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        item = pool.blnd[pool.blnd_idx]
        self.provider = item.provider
        self.fac = item.fac
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        item = pool.blnd[pool.blnd_idx]
        item.fac = self.fac
        self.copy_to_pg(item)
        try:
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"blnd_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        if self.selview in {"nodes", "all"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.nprams, ("Nodes", "Groups"))
        if self.selview in {"points", "all"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.iprams, ("Points", "Groups"))
        if self.selview in {"blend", "all"}:
            box = layout.box()
            row = box.row(align=True)
            s = row.split(factor=0.25)
            cns = s.column(align=True)
            cvs = s.column(align=True)
            getattr(ModPDOP, self.provider)(cns, cvs, self.blnded, isprof=True)
        row = layout.row(align=True)
        row.prop(self, "selview", expand=True)
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.label(text="Align")
        row = sc.row(align=True)
        row.label(text="Factor")
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self.blnded, "idx", text="")
        row.prop(self.blnded, "rot_align", text="")
        row = sc.row(align=True)
        row.prop(self, "fac", text="")


class PTDBLNPOPM_OT_pathloc_edit(bpy.types.Operator):
    bl_label = "Locations [Path]"
    bl_idname = "ptdblnpopm.pathloc_edit"
    bl_description = "path locations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    fac: bpy.props.FloatProperty(name="factor", description="amount", default=0)
    axis: bpy.props.FloatVectorProperty(
        name="influence",
        description="axis factor",
        size=3,
        default=(1, 1, 1),
        min=-1,
        max=1,
    )
    abs_move: bpy.props.BoolProperty(
        name="move",
        description="relative or absolute translation (path space)",
        default=False,
    )
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)

    def copy_from_pg(self, item):
        d = item.nprams.to_dct()
        for key in d.keys():
            setattr(self.nprams, key, d[key])

    def copy_to_pg(self, item):
        d = self.nprams.to_dct(exclude={"npts"})
        for key in d.keys():
            setattr(item.nprams, key, d[key])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        item = pool.pathloc[pool.pathloc_idx]
        self.fac = item.fac
        self.abs_move = item.abs_move
        self.axis = item.axis
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        item = pool.pathloc[pool.pathloc_idx]
        item.fac = self.fac
        item.abs_move = self.abs_move
        item.axis = self.axis
        self.copy_to_pg(item)
        try:
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"pathloc_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        ModPDOP.params_layout_draw(box, self.nprams, ("Nodes", "Groups"))
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        names = ("Translation", "Axis", "Factor")
        for n in names:
            row = sc.row(align=True)
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(
            self,
            "abs_move",
            text=("absolute" if self.abs_move else "relative"),
            toggle=True,
        )
        row = sc.row(align=True)
        row.prop(self, "axis", text="")
        row = sc.row(align=True)
        row.prop(self, "fac", text="")


class PTDBLNPOPM_OT_profloc_edit(bpy.types.Operator):
    bl_label = "Locations [Profile]"
    bl_idname = "ptdblnpopm.profloc_edit"
    bl_description = "profile locations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    fac: bpy.props.FloatProperty(name="factor", description="amount", default=0)
    axis: bpy.props.FloatVectorProperty(
        name="influence",
        description="axis factor",
        size=3,
        default=(1, 1, 0),
        min=-1,
        max=1,
    )
    abs_move: bpy.props.BoolProperty(
        name="move",
        description="relative or absolute translation (profile space)",
        default=False,
    )
    selview: bpy.props.EnumProperty(
        name="options",
        description="view options",
        items=(
            ("points", "points", "points"),
            ("nodes", "nodes", "nodes"),
            ("both", "both", "both"),
        ),
        default="both",
    )
    iprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    nprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)

    def copy_from_pg(self, item):
        ipar = item.iprams.to_dct()
        npar = item.nprams.to_dct()
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(self.iprams, ikey, ipar[ikey])
            setattr(self.nprams, nkey, npar[nkey])

    def copy_to_pg(self, item):
        ipar = self.iprams.to_dct(exclude={"npts"})
        npar = self.nprams.to_dct(exclude={"npts"})
        for ikey, nkey in zip(ipar.keys(), npar.keys()):
            setattr(item.iprams, ikey, ipar[ikey])
            setattr(item.nprams, nkey, npar[nkey])

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        item = pool.profloc[pool.profloc_idx]
        self.fac = item.fac
        self.axis = item.axis
        self.abs_move = item.abs_move
        self.copy_from_pg(item)
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.update_ok = False
        item = pool.profloc[pool.profloc_idx]
        item.fac = self.fac
        item.axis = self.axis
        item.abs_move = self.abs_move
        self.copy_to_pg(item)
        try:
            ModPOPM.scene_update(scene)
        except Exception as my_err:
            pool.update_ok = True
            print(f"profloc_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.update_ok = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        if self.selview in {"nodes", "both"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.nprams, ("Nodes", "Groups"))
        if self.selview in {"points", "both"}:
            box = layout.box()
            ModPDOP.params_layout_draw(box, self.iprams, ("Points", "Groups"))
        row = layout.row(align=True)
        row.prop(self, "selview", expand=True)
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.25)
        sc = s.column(align=True)
        names = ("Translation", "Axis", "Factor")
        for n in names:
            row = sc.row(align=True)
            row.label(text=n)
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(
            self,
            "abs_move",
            text=("absolute" if self.abs_move else "relative"),
            toggle=True,
        )
        row = sc.row(align=True)
        row.prop(self, "axis", text="")
        row = sc.row(align=True)
        row.prop(self, "fac", text="")


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------


classes = (
    PTDBLNPOPM_vec3,
    PTDBLNPOPM_anim_index,
    PTDBLNPOPM_anim_mirror,
    PTDBLNPOPM_anim_amount,
    PTDBLNPOPM_anim_rots,
    PTDBLNPOPM_params,
    PTDBLNPOPM_pathed,
    PTDBLNPOPM_profed,
    PTDBLNPOPM_path,
    PTDBLNPOPM_pathloc,
    PTDBLNPOPM_pathrot,
    PTDBLNPOPM_prof,
    PTDBLNPOPM_blnd,
    PTDBLNPOPM_profloc,
    PTDBLNPOPM_profrot,
    PTDBLNPOPM_noiz,
    PTDBLNPOPM_meshrot,
    PTDBLNPOPM_rngs,
    PTDBLNPOPM_track,
    PTDBLNPOPM_anicalc,
    PTDBLNPOPM_pool,
    PTDBLNPOPM_OT_path_edit,
    PTDBLNPOPM_OT_pathloc_edit,
    PTDBLNPOPM_OT_prof_edit,
    PTDBLNPOPM_OT_blnd_edit,
    PTDBLNPOPM_OT_profloc_edit,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)
    bpy.types.Scene.ptdblnpopm_params = bpy.props.PointerProperty(
        type=PTDBLNPOPM_params
    )
    bpy.types.Scene.ptdblnpopm_pathed = bpy.props.PointerProperty(
        type=PTDBLNPOPM_pathed
    )
    bpy.types.Scene.ptdblnpopm_profed = bpy.props.PointerProperty(
        type=PTDBLNPOPM_profed
    )
    bpy.types.Scene.ptdblnpopm_pool = bpy.props.PointerProperty(type=PTDBLNPOPM_pool)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.ptdblnpopm_pool
    del bpy.types.Scene.ptdblnpopm_profed
    del bpy.types.Scene.ptdblnpopm_pathed
    del bpy.types.Scene.ptdblnpopm_params
