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

from . import mcnst as ModCnst
from . import mmpop as ModPop


# ------------------------------------------------------------------------------
#
# ----------------------------- PROPERTIES -------------------------------------


class PTDBLNPOPM_float3(bpy.types.PropertyGroup):

    vert: bpy.props.FloatVectorProperty(
        size=3, default=(0, 0, 0), subtype="TRANSLATION"
    )


class PTDBLNPOPM_anim_index(bpy.types.PropertyGroup):

    active: bpy.props.BoolProperty(
        name="Index", description="animate index", default=False, options={"HIDDEN"}
    )
    offset: bpy.props.IntProperty(
        name="Offset",
        description="index offset",
        default=0,
        min=-ModCnst.MAX_IDX_OFF,
        max=ModCnst.MAX_IDX_OFF,
        options={"HIDDEN"},
    )
    beg: bpy.props.IntProperty(
        name="Start",
        description="start keyframe",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    stp: bpy.props.IntProperty(
        name="Step",
        description="keyframe step",
        default=1,
        min=1,
        options={"HIDDEN"},
    )


class PTDBLNPOPM_anim_amount(bpy.types.PropertyGroup):

    active: bpy.props.BoolProperty(
        name="Factor", description="animate factor", default=False, options={"HIDDEN"}
    )
    fac: bpy.props.FloatProperty(
        name="Target Factor",
        description="factor target",
        default=0,
        min=-ModCnst.MAX_FAC,
        max=ModCnst.MAX_FAC,
        options={"HIDDEN"},
    )
    mirror: bpy.props.BoolProperty(
        name="Mirror", description="mirror animation", default=False, options={"HIDDEN"}
    )
    cycles: bpy.props.IntProperty(
        name="Cycles",
        description="mirror cycles",
        default=1,
        min=1,
        options={"HIDDEN"},
    )


class PTDBLNPOPM_anim_rots(bpy.types.PropertyGroup):

    active: bpy.props.BoolProperty(
        name="Rotate", description="animate rotation", default=False, options={"HIDDEN"}
    )
    fac: bpy.props.FloatProperty(
        name="Angle",
        description="[degrees] to rotate per keyframe",
        default=0,
        min=-3,
        max=3,
        subtype="ANGLE",
        options={"HIDDEN"},
    )
    beg: bpy.props.IntProperty(
        name="Start",
        description="start keyframe",
        default=1,
        min=1,
        options={"HIDDEN"},
    )
    end: bpy.props.IntProperty(
        name="End",
        description="end keyframe",
        default=1,
        min=1,
        options={"HIDDEN"},
    )


class PTDBLNPOPM_params(bpy.types.PropertyGroup):
    def params_npts_updates(self, npts):
        self.npts = npts
        self.idx = min(npts - 1, self.idx)
        self.itm = min(npts, self.itm)
        self.reps = min(npts, self.reps)
        self.gap = min(npts, self.gap)

    def params_idx_get(self):
        return self.get("idx", 0)

    def params_idx_set(self, value):
        self["idx"] = value % self.npts if self.npts else 0

    def params_itm_get(self):
        return self.get("itm", 1)

    def params_itm_set(self, value):
        hi = max(1, self.npts)
        self["itm"] = min(max(1, value), hi)

    def params_reps_get(self):
        return self.get("reps", 1)

    def params_reps_set(self, value):
        hi = max(1, self.npts)
        self["reps"] = min(max(1, value), hi)

    def params_gap_get(self):
        return self.get("gap", 0)

    def params_gap_set(self, value):
        hi = max(0, self.npts)
        self["gap"] = min(max(0, value), hi)

    npts: bpy.props.IntProperty(default=0)
    lerp: bpy.props.BoolProperty(
        name="Lerp", description="interpolation", default=False
    )
    mir: bpy.props.BoolProperty(
        name="Mirror", description="interpolation mirror", default=False
    )
    ease: bpy.props.EnumProperty(
        name="Ease",
        description="interpolation type",
        items=(
            ("IN", "in", "ease in"),
            ("OUT", "out", "ease out"),
            ("IN-OUT", "in-out", "ease in and out"),
            ("LINEAR", "linear", "no easing"),
        ),
        default="IN-OUT",
    )
    exp: bpy.props.FloatProperty(
        name="Exponent",
        description="interpolation exponent",
        default=1,
        min=ModCnst.MIN_EXP,
        max=ModCnst.MAX_EXP,
    )
    cyc: bpy.props.BoolProperty(
        name="Lag", description="interpolation excludes last increment", default=False
    )
    f2: bpy.props.FloatProperty(
        name="Factor", description="enhance-fade", default=1, min=-2, max=2
    )
    idx: bpy.props.IntProperty(
        name="Offset",
        description="index offset",
        default=0,
        get=params_idx_get,
        set=params_idx_set,
    )
    itm: bpy.props.IntProperty(
        name="Items",
        description="group items",
        default=1,
        get=params_itm_get,
        set=params_itm_set,
    )
    reps: bpy.props.IntProperty(
        name="Repeats",
        description="repeats",
        default=1,
        get=params_reps_get,
        set=params_reps_set,
    )
    gap: bpy.props.IntProperty(
        name="Gap",
        description="gap between repeats",
        default=0,
        get=params_gap_get,
        set=params_gap_set,
    )
    rev: bpy.props.BoolProperty(
        name="Back", description="reverse direction", default=False
    )

    def to_dct(self):
        d = {}
        for key in self.__annotations__.keys():
            d[key] = getattr(self, key)
        return d


class PTDBLNPOPM_pathloc(bpy.types.PropertyGroup):
    def pathloc_active_update(self, context):
        if not self.active:
            self.ani_idx.active = False
            self.ani_fac.active = False

    name: bpy.props.StringProperty(default="Locs")
    active: bpy.props.BoolProperty(default=False, update=pathloc_active_update)
    fac: bpy.props.FloatProperty(default=0)
    axis: bpy.props.FloatVectorProperty(size=3, default=(1, 1, 1))
    abs_move: bpy.props.BoolProperty(default=False)
    params: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)
    ani_fac: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_amount)

    def to_dct(self):
        d = {"fac": self.fac, "axis": self.axis, "abs_move": self.abs_move}
        d["params"] = self.params.to_dct()
        return d


class PTDBLNPOPM_profloc(bpy.types.PropertyGroup):
    def profloc_update(self, context):
        if not self.active:
            self.ani_itm_idx.active = False
            self.ani_idx.active = False
            self.ani_fac.active = False

    name: bpy.props.StringProperty(default="Locs")
    active: bpy.props.BoolProperty(default=False, update=profloc_update)
    fac: bpy.props.FloatProperty(default=0)
    axis: bpy.props.FloatVectorProperty(size=2, default=(1, 1))
    abs_move: bpy.props.BoolProperty(default=False)
    params: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    gprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    ani_itm_idx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)
    ani_fac: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_amount)

    def to_dct(self):
        d = {"fac": self.fac, "axis": self.axis, "abs_move": self.abs_move}
        d["params"] = self.params.to_dct()
        d["gprams"] = self.gprams.to_dct()
        return d


class PTDBLNPOPM_spro(bpy.types.PropertyGroup):
    def spro_active_update(self, context):
        if not self.active:
            self.ani_rot.active = False
        pool = context.scene.ptdblnpopm_pool
        if pool.callbacks:
            bpy.ops.ptdblnpopm.update_default()

    active: bpy.props.BoolProperty(
        name="Toggle",
        description="enable/disable edits",
        default=False,
        update=spro_active_update,
        options={"HIDDEN"},
    )
    rot_ang: bpy.props.FloatProperty(default=0, subtype="ANGLE")
    spin_ang: bpy.props.FloatProperty(default=0, subtype="ANGLE")
    follow_limit: bpy.props.BoolProperty(default=True)
    ani_rot: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_rots)


class PTDBLNPOPM_pathed(bpy.types.PropertyGroup):
    def pathed_rings_updates(self, rings):
        self.rings = rings
        self.idx = min(rings - 1, self.idx)
        self.bump = min(int(rings / 2), self.bump)

    def pathed_idx_get(self):
        return self.get("idx", 0)

    def pathed_idx_set(self, value):
        self["idx"] = (value % self.rings) if self.rings else 0

    def pathed_bump_get(self):
        return self.get("bump", 1)

    def pathed_bump_set(self, value):
        hi = int(self.rings / 2) if self.rings else 1
        self["bump"] = min(max(1, value), hi)

    def pathed_closed_update(self, context):
        if self.closed:
            self.endcaps = False

    def pathed_round_segs_get(self):
        return self.get("round_segs", 0)

    def pathed_round_segs_set(self, value):
        if self.rings < 8:
            val = 0
        else:
            hi = int(self.rings / 4) - 1
            val = min(max(0, value), hi)
        self["round_segs"] = val

    rings: bpy.props.IntProperty(default=12)
    user_dim: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    user_bbc: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    upv: bpy.props.CollectionProperty(type=PTDBLNPOPM_float3)
    user_name: bpy.props.StringProperty(default="none")
    u_dim: bpy.props.FloatVectorProperty(size=3, default=[ModCnst.DEF_DIM_PATH] * 3)
    lin_dim: bpy.props.FloatVectorProperty(size=3, default=[ModCnst.DEF_DIM_PATH] * 3)
    lin_lerp: bpy.props.EnumProperty(
        name="Ease",
        description="interpolation type",
        items=(
            ("IN", "in", "ease in"),
            ("OUT", "out", "ease out"),
            ("IN-OUT", "in-out", "ease in and out"),
            ("LINEAR", "linear", "no easing"),
        ),
        default="IN-OUT",
    )
    lin_exp: bpy.props.FloatProperty(
        name="Factor",
        default=1,
        description="interpolation exponent",
        min=ModCnst.MIN_EXP,
        max=ModCnst.MAX_EXP,
    )
    spi_dim: bpy.props.FloatProperty(
        name="Size",
        description="path dimensions",
        default=ModCnst.DEF_DIM_PATH,
    )
    spi_revs: bpy.props.FloatProperty(
        name="Revolutions",
        default=0.5,
        description="spherical spiral revolutions",
        min=-ModCnst.MAX_FAC,
        max=ModCnst.MAX_FAC,
    )
    ell_dim: bpy.props.FloatVectorProperty(
        size=3, default=[ModCnst.DEF_DIM_PATH, 0, ModCnst.DEF_DIM_PATH]
    )
    bump: bpy.props.IntProperty(
        name="Steps",
        default=1,
        description="interpolation steps",
        get=pathed_bump_get,
        set=pathed_bump_set,
    )
    bump_val: bpy.props.FloatProperty(
        name="Factor",
        default=0,
        description="amount",
        min=-ModCnst.MAX_FAC,
        max=ModCnst.MAX_FAC,
    )
    bump_exp: bpy.props.FloatProperty(
        name="Exponent",
        default=2,
        description="interpolation exponent",
        min=ModCnst.MIN_EXP,
        max=ModCnst.MAX_EXP,
    )
    rct_dim: bpy.props.FloatVectorProperty(
        size=3, default=[ModCnst.DEF_DIM_PATH, 0, ModCnst.DEF_DIM_PATH]
    )
    round_segs: bpy.props.IntProperty(
        name="Segments",
        default=0,
        description="rounding segments",
        get=pathed_round_segs_get,
        set=pathed_round_segs_set,
    )
    round_off: bpy.props.FloatProperty(
        name="Radius", description="rounding offset", default=0.5
    )
    idx: bpy.props.IntProperty(
        name="Offset",
        default=0,
        description="index offset",
        get=pathed_idx_get,
        set=pathed_idx_set,
    )
    closed: bpy.props.BoolProperty(
        name="Closed",
        default=False,
        description="closed or open path",
        update=pathed_closed_update,
    )
    endcaps: bpy.props.BoolProperty(
        name="Endcaps", description="open path end faces - ngons", default=False
    )

    def to_dct(self, exclude=[]):
        d = {}
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            elif key == "upv":
                d[key] = [i.vert for i in self.upv]
            else:
                d[key] = getattr(self, key)
        return d


class PTDBLNPOPM_path(bpy.types.PropertyGroup):
    def path_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.callbacks:
            if self.provider == "custom":
                bpy.ops.ptdblnpopm.update_user(caller="path")
            else:
                bpy.ops.ptdblnpopm.update_preset(caller="path")

    def path_user_check(self, object):
        return object.type == "MESH"

    def path_user_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.callbacks:
            bpy.ops.ptdblnpopm.update_user(caller="path")

    clean: bpy.props.BoolProperty(default=False)
    provider: bpy.props.EnumProperty(
        name="Path",
        description="path selection",
        items=(
            ("line", "line", "line"),
            ("ellipse", "ellipse", "ellipse"),
            ("rectangle", "rectangle", "rectangle"),
            ("spiral", "spiral", "sphere spiral"),
            ("custom", "custom", "user path"),
        ),
        default="line",
        update=path_update,
        options={"HIDDEN"},
    )
    res_lin: bpy.props.IntProperty(
        name="Segments",
        description="path segments",
        default=11,
        min=2,
        max=ModCnst.MAX_SEGS - 1,
        update=path_update,
        options={"HIDDEN"},
    )
    res_spi: bpy.props.IntProperty(
        name="Segments",
        description="path segments",
        default=7,
        min=4,
        max=int(ModCnst.MAX_SEGS / 2) + 1,
        update=path_update,
        options={"HIDDEN"},
    )
    res_rct: bpy.props.IntVectorProperty(
        name="Segments",
        description="path segments",
        size=2,
        default=(3, 3),
        min=1,
        max=int(ModCnst.MAX_SEGS / 4),
        update=path_update,
        options={"HIDDEN"},
    )
    res_ell: bpy.props.IntProperty(
        name="Segments",
        description="path segments",
        default=12,
        min=3,
        max=ModCnst.MAX_SEGS,
        update=path_update,
        options={"HIDDEN"},
    )
    user_ob: bpy.props.PointerProperty(
        type=bpy.types.Object, poll=path_user_check, update=path_user_update
    )
    pathed: bpy.props.PointerProperty(type=PTDBLNPOPM_pathed)
    ani_dim: bpy.props.BoolProperty(
        name="Size", description="animate dimensions", default=False, options={"HIDDEN"}
    )
    ani_spi_dim: bpy.props.FloatProperty(
        name="Target Size",
        description="path size target",
        default=ModCnst.DEF_DIM_PATH,
        options={"HIDDEN"},
    )
    ani_eru_dim: bpy.props.FloatVectorProperty(
        name="Target Size",
        description="path size target",
        size=3,
        default=(0, 0, 0),
        options={"HIDDEN"},
    )
    ani_fac: bpy.props.BoolProperty(
        name="Factor", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_lin_exp: bpy.props.FloatProperty(
        name="Target Exponent",
        description="interpolation exponent target",
        default=1,
        min=ModCnst.MIN_EXP,
        max=ModCnst.MAX_EXP,
        options={"HIDDEN"},
    )
    ani_spi_revs: bpy.props.FloatProperty(
        name="Target Revolutions",
        description="spiral revolutions target",
        default=0.5,
        min=-ModCnst.MAX_FAC,
        max=ModCnst.MAX_FAC,
        options={"HIDDEN"},
    )
    ani_fac_val: bpy.props.FloatProperty(
        name="Target Bump",
        description="bump value target",
        default=1,
        min=-ModCnst.MAX_FAC,
        max=ModCnst.MAX_FAC,
        options={"HIDDEN"},
    )
    ani_mirror: bpy.props.BoolProperty(
        name="Mirror", description="mirror animation", default=False, options={"HIDDEN"}
    )
    ani_cycles: bpy.props.IntProperty(
        name="Cycles",
        description="mirror cycles",
        default=1,
        min=1,
        options={"HIDDEN"},
    )

    def to_dct(self):
        d = dict.fromkeys(["provider", "res_rct", "res_ell", "res_lin", "res_spi"])
        for key in d.keys():
            d[key] = getattr(self, key)
        d.update(self.pathed.to_dct())
        return d


class PTDBLNPOPM_profed(bpy.types.PropertyGroup):
    def profed_rpts_updates(self, rpts):
        self.rpts = rpts
        self.idx = min(rpts - 1, self.idx)
        self.bump = min(int(rpts / 2), self.bump)

    def profed_idx_get(self):
        return self.get("idx", 0)

    def profed_idx_set(self, value):
        self["idx"] = (value % self.rpts) if self.rpts else 0

    def profed_bump_get(self):
        return self.get("bump", 1)

    def profed_bump_set(self, value):
        hi = int(self.rpts / 2) if self.rpts else 1
        self["bump"] = min(max(1, value), hi)

    def profed_round_segs_get(self):
        return self.get("round_segs", 0)

    def profed_round_segs_set(self, value):
        if self.rpts < 8:
            val = 0
        else:
            hi = int(self.rpts / 4) - 1
            val = min(max(0, value), hi)
        self["round_segs"] = val

    rpts: bpy.props.IntProperty(default=12)
    reverse: bpy.props.BoolProperty(
        name="Reverse", description="reverse vertex-order", default=False
    )
    idx: bpy.props.IntProperty(
        name="Offset",
        default=0,
        description="index offset",
        get=profed_idx_get,
        set=profed_idx_set,
    )
    closed: bpy.props.BoolProperty(
        name="Closed", description="closed or open profile", default=True
    )
    user_dim: bpy.props.FloatVectorProperty(size=2, default=(0, 0))
    user_bbc: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    upv: bpy.props.CollectionProperty(type=PTDBLNPOPM_float3)
    user_name: bpy.props.StringProperty(default="none")
    u_dim: bpy.props.FloatVectorProperty(size=2, default=[ModCnst.DEF_DIM_PROF] * 2)
    lin_dim: bpy.props.FloatVectorProperty(size=2, default=[ModCnst.DEF_DIM_PROF] * 2)
    lin_lerp: bpy.props.EnumProperty(
        name="Ease",
        description="interpolation type",
        items=(
            ("IN", "in", "ease in"),
            ("OUT", "out", "ease out"),
            ("IN-OUT", "in-out", "ease in and out"),
            ("LINEAR", "linear", "no easing"),
        ),
        default="IN-OUT",
    )
    lin_exp: bpy.props.FloatProperty(
        name="Factor",
        default=1,
        description="interpolation exponent",
        min=ModCnst.MIN_EXP,
        max=ModCnst.MAX_EXP,
    )
    ell_dim: bpy.props.FloatVectorProperty(size=2, default=[ModCnst.DEF_DIM_PROF] * 2)
    bump: bpy.props.IntProperty(
        name="Steps",
        default=1,
        description="interpolation steps",
        get=profed_bump_get,
        set=profed_bump_set,
    )
    bump_val: bpy.props.FloatProperty(
        name="Factor",
        default=0,
        description="amount",
        min=-ModCnst.MAX_FAC,
        max=ModCnst.MAX_FAC,
    )
    bump_exp: bpy.props.FloatProperty(
        name="Exponent",
        default=2,
        description="interpolation exponent",
        min=ModCnst.MIN_EXP,
        max=ModCnst.MAX_EXP,
    )
    rct_dim: bpy.props.FloatVectorProperty(size=2, default=[ModCnst.DEF_DIM_PROF] * 2)
    round_segs: bpy.props.IntProperty(
        name="Segments",
        description="rounding segments",
        default=0,
        get=profed_round_segs_get,
        set=profed_round_segs_set,
    )
    round_off: bpy.props.FloatProperty(
        name="Radius", description="rounding offset", default=0.5
    )

    def to_dct(self, exclude=[]):
        d = {}
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            elif key == "upv":
                d[key] = [i.vert for i in self.upv]
            else:
                d[key] = getattr(self, key)
        return d


class PTDBLNPOPM_prof(bpy.types.PropertyGroup):
    def prof_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.callbacks:
            if self.provider == "custom":
                bpy.ops.ptdblnpopm.update_user(caller="prof")
            else:
                bpy.ops.ptdblnpopm.update_preset(caller="prof")

    def prof_user_check(self, object):
        return object.type == "MESH"

    def prof_user_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.callbacks:
            bpy.ops.ptdblnpopm.update_user(caller="prof")

    clean: bpy.props.BoolProperty(default=False)
    provider: bpy.props.EnumProperty(
        name="Profile",
        description="profile selection",
        items=(
            ("line", "line", "line"),
            ("ellipse", "ellipse", "ellipse"),
            ("rectangle", "rectangle", "rectangle"),
            ("custom", "custom", "user profile"),
        ),
        default="rectangle",
        update=prof_update,
        options={"HIDDEN"},
    )
    res_lin: bpy.props.IntProperty(
        name="Segments",
        description="profile segments",
        default=11,
        min=2,
        max=ModCnst.MAX_SEGS - 1,
        update=prof_update,
        options={"HIDDEN"},
    )
    res_rct: bpy.props.IntVectorProperty(
        name="Segments",
        description="profile segments",
        size=2,
        default=(3, 3),
        min=1,
        max=int(ModCnst.MAX_SEGS / 4),
        update=prof_update,
        options={"HIDDEN"},
    )
    res_ell: bpy.props.IntProperty(
        name="Segments",
        description="profile segments",
        default=12,
        min=3,
        max=ModCnst.MAX_SEGS,
        update=prof_update,
        options={"HIDDEN"},
    )
    user_ob: bpy.props.PointerProperty(
        type=bpy.types.Object, poll=prof_user_check, update=prof_user_update
    )
    profed: bpy.props.PointerProperty(type=PTDBLNPOPM_profed)
    ani_dim: bpy.props.BoolProperty(
        name="Size", description="animate dimensions", default=False, options={"HIDDEN"}
    )
    ani_eru_dim: bpy.props.FloatVectorProperty(
        name="Target Size",
        description="profile size target",
        size=2,
        default=(0, 0),
        options={"HIDDEN"},
    )
    ani_fac: bpy.props.BoolProperty(
        name="Factor", description="animate value", default=False, options={"HIDDEN"}
    )
    ani_lin_exp: bpy.props.FloatProperty(
        name="Target Exponent",
        description="interpolation exponent target",
        default=1,
        min=ModCnst.MIN_EXP,
        max=ModCnst.MAX_EXP,
        options={"HIDDEN"},
    )
    ani_fac_val: bpy.props.FloatProperty(
        name="Target Bump",
        description="bump value target",
        default=1,
        min=-ModCnst.MAX_FAC,
        max=ModCnst.MAX_FAC,
        options={"HIDDEN"},
    )
    ani_mirror: bpy.props.BoolProperty(
        name="Mirror", description="mirror animation", default=False, options={"HIDDEN"}
    )
    ani_cycles: bpy.props.IntProperty(
        name="Cycles",
        description="mirror cycles",
        default=1,
        min=1,
        options={"HIDDEN"},
    )

    def to_dct(self):
        d = dict.fromkeys(["provider", "res_rct", "res_ell", "res_lin"])
        for key in d.keys():
            d[key] = getattr(self, key)
        d.update(self.profed.to_dct())
        return d


class PTDBLNPOPM_blnd(bpy.types.PropertyGroup):
    def blnd_user_check(self, object):
        return object.type == "MESH"

    def blnd_user_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.callbacks:
            bpy.ops.ptdblnpopm.blnd_update_user()

    def blnd_active_update(self, context):
        if not self.active:
            self.ani_idx.active = False
            self.ani_fac = False

    def blnd_provider_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.callbacks:
            if self.provider == "custom":
                bpy.ops.ptdblnpopm.blnd_update_user()
            else:
                bpy.ops.ptdblnpopm.blnd_update_preset()

    name: bpy.props.StringProperty(default="Blend")
    provider: bpy.props.EnumProperty(
        name="Blend-profile",
        description="blend-profile type",
        items=(
            ("line", "line", "line"),
            ("ellipse", "ellipse", "ellipse"),
            ("rectangle", "rectangle", "rectangle"),
            ("custom", "custom", "user profile"),
        ),
        default="ellipse",
        update=blnd_provider_update,
        options={"HIDDEN"},
    )
    user_ob: bpy.props.PointerProperty(
        type=bpy.types.Object, poll=blnd_user_check, update=blnd_user_update
    )
    active: bpy.props.BoolProperty(default=False, update=blnd_active_update)
    blnded: bpy.props.PointerProperty(type=PTDBLNPOPM_profed)
    fac: bpy.props.FloatProperty(default=1)
    abs_dim: bpy.props.BoolProperty(default=True)
    params: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)
    ani_fac: bpy.props.BoolProperty(
        name="Factor", description="animate factor", default=False, options={"HIDDEN"}
    )
    ani_fac_val: bpy.props.FloatProperty(
        name="Target Factor",
        default=0,
        description="factor target",
        min=0,
        max=1,
        options={"HIDDEN"},
    )
    ani_fac_mirror: bpy.props.BoolProperty(
        name="Mirror", description="mirror animation", default=False, options={"HIDDEN"}
    )
    ani_fac_cycles: bpy.props.IntProperty(
        name="Cycles",
        description="mirror cycles",
        default=1,
        min=1,
        options={"HIDDEN"},
    )

    def to_dct(self):
        d = dict.fromkeys(["provider", "fac", "abs_dim"])
        for key in d.keys():
            d[key] = getattr(self, key)
        d.update(self.blnded.to_dct())
        d["params"] = self.params.to_dct()
        return d


class PTDBLNPOPM_noiz(bpy.types.PropertyGroup):
    def noiz_active_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if not self.active:
            self.ani_p_noiz = False
            self.ani_f_noiz = False
        if pool.callbacks:
            bpy.ops.ptdblnpopm.update_default()

    active: bpy.props.BoolProperty(
        name="Toggle",
        description="enable/disable edits",
        default=False,
        update=noiz_active_update,
        options={"HIDDEN"},
    )
    p_noiz: bpy.props.FloatProperty(default=0)
    f_noiz: bpy.props.FloatProperty(default=0)
    vfac: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    nseed: bpy.props.IntProperty(default=0)
    ani_p_noiz: bpy.props.BoolProperty(
        name="Path", default=False, description="animate path noise", options={"HIDDEN"}
    )
    ani_p_noiz_val: bpy.props.FloatProperty(
        name="Target",
        description="target strength",
        default=0,
        min=0,
        options={"HIDDEN"},
    )
    ani_f_noiz: bpy.props.BoolProperty(
        name="Detail",
        default=False,
        description="animate detail noise",
        options={"HIDDEN"},
    )
    ani_f_noiz_val: bpy.props.FloatProperty(
        name="Target",
        description="target strength",
        default=0,
        min=0,
        options={"HIDDEN"},
    )
    ani_seed: bpy.props.BoolProperty(
        name="Clock Seed",
        description="animated seed",
        default=False,
        options={"HIDDEN"},
    )
    ani_blin: bpy.props.IntProperty(
        name="Blend-in",
        default=1,
        description="blend-in keyframes",
        min=1,
        options={"HIDDEN"},
    )
    ani_blout: bpy.props.IntProperty(
        name="Blend-out",
        default=1,
        description="blend-out keyframes",
        min=1,
        options={"HIDDEN"},
    )


class PTDBLNPOPM_track(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(default="Track")
    owner: bpy.props.StringProperty(default="mesh")
    t_name: bpy.props.StringProperty(default="name")
    active: bpy.props.BoolProperty(default=True)
    ac_beg: bpy.props.IntProperty(default=1)
    ac_end: bpy.props.IntProperty(default=1)
    sa_beg: bpy.props.IntProperty(default=1)
    sa_end: bpy.props.IntProperty(default=1)
    s_beg: bpy.props.IntProperty(default=1)
    s_end: bpy.props.IntProperty(default=1)
    s_sca: bpy.props.FloatProperty(default=1)
    s_rep: bpy.props.FloatProperty(default=1)
    s_bak: bpy.props.BoolProperty(default=False)
    s_bln: bpy.props.StringProperty(default="REPLACE")
    s_blendin: bpy.props.IntProperty(default=0)
    s_blendout: bpy.props.IntProperty(default=0)
    s_blendauto: bpy.props.BoolProperty(default=False)
    s_xpl: bpy.props.StringProperty(default="HOLD")

    def to_dct(self, exclude=[]):
        d = {}
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            d[key] = getattr(self, key)
        return d


class PTDBLNPOPM_rngs(bpy.types.PropertyGroup):
    def rngs_edit_update(self, context):
        pool = context.scene.ptdblnpopm_pool
        if pool.callbacks:
            bpy.ops.ptdblnpopm.update_ranges()

    active: bpy.props.BoolProperty(
        name="Toggle",
        description="active range faces",
        default=False,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    invert: bpy.props.BoolProperty(
        name="Invert",
        description="invert selections",
        default=False,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    rndsel: bpy.props.BoolProperty(
        name="Random",
        description="random selections ",
        default=False,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    rbeg: bpy.props.IntProperty(
        name="Begin",
        description="range first index",
        default=0,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    rend: bpy.props.IntProperty(
        name="End",
        description="range length",
        default=12,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    ritm: bpy.props.IntProperty(
        name="Items",
        description="items per iteration",
        default=1,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    rstp: bpy.props.IntProperty(
        name="Step",
        description="iteration step",
        default=1,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    pbeg: bpy.props.IntProperty(
        name="Begin",
        description="range first index",
        default=0,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    pend: bpy.props.IntProperty(
        name="End",
        description="range length",
        default=12,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    pitm: bpy.props.IntProperty(
        name="Items",
        description="items per iteration",
        default=1,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    pstp: bpy.props.IntProperty(
        name="Step",
        description="iteration step",
        default=1,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    nseed: bpy.props.IntProperty(
        name="Seed",
        description="random seed",
        default=0,
        min=0,
        update=rngs_edit_update,
        options={"HIDDEN"},
    )
    sindz = {"lst": []}


class PTDBLNPOPM_obrot(bpy.types.PropertyGroup):
    def obrot_active_update(self, context):
        if not self.active:
            self.ani_rot.active = False
        pool = context.scene.ptdblnpopm_pool
        if pool.callbacks:
            bpy.ops.ptdblnpopm.update_default()

    active: bpy.props.BoolProperty(
        name="Toggle",
        description="enable/disable edits",
        default=False,
        update=obrot_active_update,
        options={"HIDDEN"},
    )
    axis: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 1))
    rot_ang: bpy.props.FloatProperty(default=0, subtype="ANGLE")
    ani_rot: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_rots)


class PTDBLNPOPM_pool(bpy.types.PropertyGroup):
    def pool_act_name_get(self):
        return self.get("act_name", "Action")

    def pool_act_name_set(self, value):
        v = value.strip()
        self["act_name"] = v if v else "Action"

    def pool_show_wire_update(self, context):
        if self.callbacks:
            bpy.ops.ptdblnpopm.display_options(option="show_wire")

    def pool_auto_smooth_update(self, context):
        if self.callbacks:
            bpy.ops.ptdblnpopm.display_options(option="auto_smooth")

    def pool_shade_smooth_update(self, context):
        if self.callbacks:
            bpy.ops.ptdblnpopm.display_options(option="shade_smooth")

    path: bpy.props.PointerProperty(type=PTDBLNPOPM_path)
    prof: bpy.props.PointerProperty(type=PTDBLNPOPM_prof)
    spro: bpy.props.PointerProperty(type=PTDBLNPOPM_spro)
    noiz: bpy.props.PointerProperty(type=PTDBLNPOPM_noiz)
    rngs: bpy.props.PointerProperty(type=PTDBLNPOPM_rngs)
    obrot: bpy.props.PointerProperty(type=PTDBLNPOPM_obrot)
    pathloc: bpy.props.CollectionProperty(type=PTDBLNPOPM_pathloc)
    pathloc_idx: bpy.props.IntProperty(name="Locs", default=-1, options={"HIDDEN"})
    profloc: bpy.props.CollectionProperty(type=PTDBLNPOPM_profloc)
    profloc_idx: bpy.props.IntProperty(name="Locs", default=-1, options={"HIDDEN"})
    blnd: bpy.props.CollectionProperty(type=PTDBLNPOPM_blnd)
    blnd_idx: bpy.props.IntProperty(name="Blend", default=-1, options={"HIDDEN"})
    trax: bpy.props.CollectionProperty(type=PTDBLNPOPM_track)
    trax_idx: bpy.props.IntProperty(name="Track", default=-1, options={"HIDDEN"})
    pop_mesh: bpy.props.PointerProperty(type=bpy.types.Object)

    callbacks: bpy.props.BoolProperty(default=True)
    replace_mesh: bpy.props.BoolProperty(
        name="replace mesh",
        description=(
            "if selected, New Mesh, Default and Load Preset will replace current mesh"
        ),
        default=False,
        options={"HIDDEN"},
    )
    show_warn: bpy.props.BoolProperty(
        name="show warnings",
        default=True,
        description="show confirmation pop-ups",
        options={"HIDDEN"},
    )
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
        name="Start",
        default=1,
        min=0,
        description="first keyframe number",
        options={"HIDDEN"},
    )
    ani_kf_step: bpy.props.IntProperty(
        name="Step",
        description="distance (in frames) between two successive keyframes",
        default=10,
        min=1,
        options={"HIDDEN"},
    )
    ani_kf_loop: bpy.props.IntProperty(
        name="Loop",
        description="number of keyframes to complete animation",
        default=5,
        min=2,
        options={"HIDDEN"},
    )
    act_name: bpy.props.StringProperty(
        name="Name",
        description="action name",
        default="Action",
        get=pool_act_name_get,
        set=pool_act_name_set,
    )
    act_owner: bpy.props.EnumProperty(
        name="Owner",
        description="action owner data-block",
        items=(("object", "object", "object"), ("mesh", "mesh", "object data")),
        default="mesh",
        options={"HIDDEN"},
    )
    show_wire: bpy.props.BoolProperty(
        name="show wire",
        description="show wireframe",
        default=False,
        update=pool_show_wire_update,
        options={"HIDDEN"},
    )
    auto_smooth: bpy.props.BoolProperty(
        name="auto smooth",
        description="auto smooth normals",
        default=False,
        update=pool_auto_smooth_update,
        options={"HIDDEN"},
    )
    shade_smooth: bpy.props.BoolProperty(
        name="shade smooth",
        description="object smooth shading",
        default=False,
        update=pool_shade_smooth_update,
        options={"HIDDEN"},
    )

    def props_unset(self):
        exclude = [
            "pop_mesh",
            "callbacks",
            "replace_mesh",
            "show_warn",
            "show_wire",
            "auto_smooth",
            "shade_smooth",
        ]
        for key in self.__annotations__.keys():
            if key in exclude:
                continue
            self.property_unset(key)


# ------------------------------------------------------------------------------
#
# ----------------------------- OPERATORS --------------------------------------


# ---- PATH EDITOR


class PTDBLNPOPM_OT_path_edit(bpy.types.Operator):

    bl_label = "Edit [Path]"
    bl_idname = "ptdblnpopm.path_edit"
    bl_description = "path settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def path_edit_dim_x_update(self, context):
        if self.update_dims:
            self.dim[0] = self.dim_x
        if self.ctl_axis == 0:
            x = self.dim_x
            self.dim_y = x * self.dim_xy
            self.dim_z = x * self.dim_xz

    def path_edit_dim_y_update(self, context):
        if self.update_dims:
            self.dim[1] = self.dim_y
        if self.ctl_axis == 1:
            y = self.dim_y
            self.dim_x = y * self.dim_xy
            self.dim_z = y * self.dim_yz

    def path_edit_dim_z_update(self, context):
        if self.update_dims:
            self.dim[2] = self.dim_z
        if self.ctl_axis == 2:
            z = self.dim_z
            self.dim_x = z * self.dim_xz
            self.dim_y = z * self.dim_yz

    def path_edit_axes_lock_update(self, context):
        self.ctl_axis = -1
        self.dim_xy = 1
        self.dim_xz = 1
        self.dim_yz = 1
        if not (self.update_dims and self.axes_lock):
            return None
        if self.dim_x:
            self.ctl_axis = 0
            x = self.dim_x
            self.dim_xy = self.dim_y / x
            self.dim_xz = self.dim_z / x
            return None
        if self.dim_y:
            self.ctl_axis = 1
            y = self.dim_y
            self.dim_xy = self.dim_x / y
            self.dim_yz = self.dim_z / y
            return None
        if self.dim_z:
            self.ctl_axis = 2
            z = self.dim_z
            self.dim_xz = self.dim_x / z
            self.dim_yz = self.dim_y / z

    provider: bpy.props.StringProperty(default="")
    dim_x: bpy.props.FloatProperty(
        name="Size",
        default=0,
        description="path dimensions",
        update=path_edit_dim_x_update,
    )
    dim_y: bpy.props.FloatProperty(
        name="Size",
        default=0,
        description="path dimensions",
        update=path_edit_dim_y_update,
    )
    dim_z: bpy.props.FloatProperty(
        name="Size",
        default=0,
        description="path dimensions",
        update=path_edit_dim_z_update,
    )
    dim: bpy.props.FloatVectorProperty(size=3, default=(0, 0, 0))
    dim_xy: bpy.props.FloatProperty(default=1)
    dim_xz: bpy.props.FloatProperty(default=1)
    dim_yz: bpy.props.FloatProperty(default=1)
    update_dims: bpy.props.BoolProperty(default=False)
    axes_lock: bpy.props.BoolProperty(
        name="Lock",
        default=False,
        description="lock axes",
        update=path_edit_axes_lock_update,
    )
    ctl_axis: bpy.props.IntProperty(default=-1)
    pathed: bpy.props.PointerProperty(type=PTDBLNPOPM_pathed)

    def invoke(self, context, event):
        path = context.scene.ptdblnpopm_pool.path
        self.provider = path.provider
        d = path.pathed.to_dct(exclude=["upv"])
        for key in d.keys():
            setattr(self.pathed, key, d[key])
        if self.provider == "line":
            self.dim = self.pathed.lin_dim
        elif self.provider == "ellipse":
            self.dim = self.pathed.ell_dim
        elif self.provider == "rectangle":
            self.dim = self.pathed.rct_dim
        else:
            self.dim = self.pathed.u_dim
        self.axes_lock = False
        self.update_dims = False
        self.dim_x = self.dim[0]
        self.dim_y = self.dim[1]
        self.dim_z = self.dim[2]
        self.update_dims = True
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        path = pool.path
        if self.provider == "line":
            self.pathed.lin_dim = self.dim
        elif self.provider == "ellipse":
            self.pathed.ell_dim = self.dim
        elif self.provider == "rectangle":
            self.pathed.rct_dim = self.dim
        else:
            self.pathed.u_dim = self.dim
        d = self.pathed.to_dct(exclude=["upv", "rings", "user_dim"])
        for key in d.keys():
            setattr(path.pathed, key, d[key])
        try:
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"path_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def draw(self, context):
        p_name = self.provider
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row()
        if p_name == "spiral":
            row.label(text="Diameter")
            row = sc.row()
            row.label(text="Index")
            row = sc.row()
            row.label(text="Factor")
        else:
            row.label(text="Lock Axes")
            row = sc.row()
            row.label(text="Size")
            row = sc.row()
            row.label(text="Index")
            if p_name == "line":
                row = sc.row()
                row.label(text="Interpolation")
            elif p_name == "rectangle":
                row = sc.row()
                row.label(text="Rounded")
            elif p_name == "ellipse":
                row = sc.row()
                row.label(text="Bumps")
        row = sc.row()
        row.label(text="Options")
        sc = s.column(align=True)
        row = sc.row(align=True)
        pathed = self.pathed
        if p_name == "spiral":
            row.prop(pathed, "spi_dim", text="")
            row = sc.row(align=True)
            row.prop(pathed, "idx", text="")
            row = sc.row(align=True)
            row.prop(pathed, "spi_revs", text="")
        else:
            p_ud = [1, 0, 1]
            if p_name == "line":
                p_ud = [1, 1, 1]
            elif p_name == "custom":
                p_ud = [1 if i else 0 for i in pathed.user_dim]
            row.prop(self, "axes_lock", toggle=True)
            row = sc.row(align=True)
            col = row.column(align=True)
            col.enabled = bool(p_ud[0]) and (self.ctl_axis < 1)
            col.prop(self, "dim_x", text="")
            col = row.column(align=True)
            col.enabled = bool(p_ud[1]) and (self.ctl_axis in [-1, 1])
            col.prop(self, "dim_y", text="")
            col = row.column(align=True)
            col.enabled = bool(p_ud[2]) and (self.ctl_axis in [-1, 2])
            col.prop(self, "dim_z", text="")
            row = sc.row(align=True)
            row.prop(pathed, "idx", text="")
            if p_name == "line":
                row = sc.row(align=True)
                row.prop(pathed, "lin_lerp", text="")
                row.prop(pathed, "lin_exp", text="")
            elif p_name == "rectangle":
                row = sc.row(align=True)
                row.enabled = pathed.rings >= 8
                row.prop(pathed, "round_segs", text="")
                row.prop(pathed, "round_off", text="")
            elif p_name == "ellipse":
                row = sc.row(align=True)
                row.prop(pathed, "bump", text="")
                row.prop(pathed, "bump_val", text="")
                row.prop(pathed, "bump_exp", text="")
        row = sc.row(align=True)
        rc = row.column(align=True)
        rc.prop(pathed, "closed", toggle=True)
        rc = row.column(align=True)
        rc.enabled = not pathed.closed
        rc.prop(pathed, "endcaps", toggle=True)


# ---- PROFILE EDITOR


class PTDBLNPOPM_OT_prof_edit(bpy.types.Operator):

    bl_label = "Edit [Profile]"
    bl_idname = "ptdblnpopm.prof_edit"
    bl_description = "profile settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def prof_edit_dim_x_update(self, context):
        if self.update_dims:
            self.dim[0] = self.dim_x
        if self.ctl_axis == -1:
            self.dim_y = self.dim_x * self.dim_xy

    def prof_edit_dim_y_update(self, context):
        if self.update_dims:
            self.dim[1] = self.dim_y
        if self.ctl_axis == 1:
            self.dim_x = self.dim_y * self.dim_xy

    def prof_edit_axes_lock_update(self, context):
        self.ctl_axis = 0
        self.dim_xy = 1
        if not (self.update_dims and self.axes_lock):
            return None
        if self.dim_x:
            self.ctl_axis = -1
            self.dim_xy = self.dim_y / self.dim_x
            return None
        if self.dim_y:
            self.ctl_axis = 1
            self.dim_xy = self.dim_x / self.dim_y

    provider: bpy.props.StringProperty(default="")
    dim_x: bpy.props.FloatProperty(
        name="Size",
        default=0,
        description="profile dimensions",
        update=prof_edit_dim_x_update,
    )
    dim_y: bpy.props.FloatProperty(
        name="Size",
        default=0,
        description="profile dimensions",
        update=prof_edit_dim_y_update,
    )
    dim: bpy.props.FloatVectorProperty(size=2, default=(0, 0))
    dim_xy: bpy.props.FloatProperty(default=1)
    update_dims: bpy.props.BoolProperty(default=False)
    axes_lock: bpy.props.BoolProperty(
        name="Lock",
        description="lock axes",
        default=False,
        update=prof_edit_axes_lock_update,
    )
    ctl_axis: bpy.props.IntProperty(default=0)
    profed: bpy.props.PointerProperty(type=PTDBLNPOPM_profed)

    def invoke(self, context, event):
        prof = context.scene.ptdblnpopm_pool.prof
        self.provider = prof.provider
        d = prof.profed.to_dct(exclude=["upv"])
        for key in d.keys():
            setattr(self.profed, key, d[key])
        if self.provider == "line":
            self.dim = self.profed.lin_dim
        elif self.provider == "ellipse":
            self.dim = self.profed.ell_dim
        elif self.provider == "rectangle":
            self.dim = self.profed.rct_dim
        else:
            self.dim = self.profed.u_dim
        self.axes_lock = False
        self.update_dims = False
        self.dim_x = self.dim[0]
        self.dim_y = self.dim[1]
        self.update_dims = True
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        prof = pool.prof
        if self.provider == "line":
            self.profed.lin_dim = self.dim
        elif self.provider == "ellipse":
            self.profed.ell_dim = self.dim
        elif self.provider == "rectangle":
            self.profed.rct_dim = self.dim
        else:
            self.profed.u_dim = self.dim
        d = self.profed.to_dct(exclude=["upv", "rpts", "user_dim"])
        for key in d.keys():
            setattr(prof.profed, key, d[key])
        try:
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"prof_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def draw(self, context):
        p_name = self.provider
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text="Lock Axes")
        row = sc.row()
        row.label(text="Size")
        row = sc.row()
        row.label(text="Index")
        if p_name == "line":
            row = sc.row()
            row.label(text="Interpolation")
        elif p_name == "rectangle":
            row = sc.row()
            row.label(text="Rounded")
        elif p_name == "ellipse":
            row = sc.row()
            row.label(text="Bumps")
        row = sc.row()
        row.label(text="Options")
        profed = self.profed
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "axes_lock", toggle=True)
        row = sc.row(align=True)
        col = row.column(align=True)
        col.enabled = self.ctl_axis < 1
        col.prop(self, "dim_x", text="")
        col = row.column(align=True)
        col.enabled = self.ctl_axis > -1
        col.prop(self, "dim_y", text="")
        row = sc.row(align=True)
        row.prop(profed, "idx", text="")
        if p_name == "line":
            row = sc.row(align=True)
            row.prop(profed, "lin_lerp", text="")
            row.prop(profed, "lin_exp", text="")
        elif p_name == "rectangle":
            row = sc.row(align=True)
            row.enabled = profed.rpts >= 8
            row.prop(profed, "round_segs", text="")
            row.prop(profed, "round_off", text="")
        elif p_name == "ellipse":
            row = sc.row(align=True)
            row.prop(profed, "bump", text="")
            row.prop(profed, "bump_val", text="")
            row.prop(profed, "bump_exp", text="")
        row = sc.row(align=True)
        row.prop(profed, "closed", toggle=True)
        row.prop(profed, "reverse", toggle=True)


# ---- PARAMS DRAW-FUNCTION TEMPLATE


def params_layout_template(self, names, use_axis=True):

    params = self.params
    layout = self.layout
    box = layout.box()
    row = box.row(align=True)
    s = row.split(factor=0.3)
    sc = s.column(align=True)
    for n in names:
        row = sc.row()
        if n == "Absolute Axis":
            row.prop(
                self,
                "abs_move",
                text=(n if self.abs_move else "Relative Axis"),
                toggle=True,
            )
        else:
            row.label(text=n)
    col = sc.column()
    lerp_cond = (params.itm > 1) and bool(self.fac)
    col.enabled = lerp_cond
    row = col.row()
    row.prop(params, "lerp", text="Interpolate", toggle=True)
    row = col.row()
    row.label(text="Options")
    sc = s.column(align=True)
    row = sc.row(align=True)
    row.prop(params, "idx", text="")
    row.prop(params, "itm", text="")
    row.prop(params, "rev", toggle=True)
    row = sc.row(align=True)
    row.prop(params, "reps", text="")
    row.prop(params, "f2", text="")
    row.prop(params, "gap", text="")
    if use_axis:
        row = sc.row(align=True)
        row.enabled = self.abs_move
        row.prop(self, "axis", text="")
    row = sc.row(align=True)
    row.prop(self, "fac", text="")
    col = sc.column(align=True)
    col.enabled = lerp_cond and params.lerp
    row = col.row(align=True)
    row.prop(params, "ease", text="")
    row.prop(params, "exp", text="")
    row = col.row(align=True)
    row.prop(params, "mir", toggle=True)
    row.prop(params, "cyc", toggle=True)


# ---- PROFILE-BLENDS COLLECTION ITEM EDITOR


class PTDBLNPOPM_OT_blnd_edit(bpy.types.Operator):

    bl_label = "Edit [Blend]"
    bl_idname = "ptdblnpopm.blnd_edit"
    bl_description = "blend profile settings"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def blnd_edit_dim_x_update(self, context):
        if self.update_dims:
            self.dim[0] = self.dim_x
        if self.ctl_axis == -1:
            self.dim_y = self.dim_x * self.dim_xy

    def blnd_edit_dim_y_update(self, context):
        if self.update_dims:
            self.dim[1] = self.dim_y
        if self.ctl_axis == 1:
            self.dim_x = self.dim_y * self.dim_xy

    def blnd_edit_axes_lock_update(self, context):
        self.ctl_axis = 0
        self.dim_xy = 1
        if not (self.update_dims and self.axes_lock):
            return None
        if self.dim_x:
            self.ctl_axis = -1
            self.dim_xy = self.dim_y / self.dim_x
            return None
        if self.dim_y:
            self.ctl_axis = 1
            self.dim_xy = self.dim_x / self.dim_y

    dim_x: bpy.props.FloatProperty(
        name="Size",
        default=0,
        description="blend-profile dimensions",
        update=blnd_edit_dim_x_update,
    )
    dim_y: bpy.props.FloatProperty(
        name="Size",
        default=0,
        description="blend-profile dimensions",
        update=blnd_edit_dim_y_update,
    )
    dim: bpy.props.FloatVectorProperty(size=2, default=(0, 0))
    dim_xy: bpy.props.FloatProperty(default=1)
    update_dims: bpy.props.BoolProperty(default=False)
    axes_lock: bpy.props.BoolProperty(
        name="Lock",
        description="lock axes",
        default=False,
        update=blnd_edit_axes_lock_update,
    )
    ctl_axis: bpy.props.IntProperty(default=0)
    provider: bpy.props.StringProperty(default="")
    fac: bpy.props.FloatProperty(
        name="Factor", description="amount", default=1, min=0, max=1
    )
    abs_dim: bpy.props.BoolProperty(
        name="Absolute Size",
        description="relative or absolute dimensions",
        default=True,
    )
    blnded: bpy.props.PointerProperty(type=PTDBLNPOPM_profed)
    params: bpy.props.PointerProperty(type=PTDBLNPOPM_params)

    def copy_from_pg(self, item):
        d = item.blnded.to_dct(exclude=["upv"])
        for key in d.keys():
            setattr(self.blnded, key, d[key])
        d = item.params.to_dct()
        for key in d.keys():
            setattr(self.params, key, d[key])

    def copy_to_pg(self, item):
        d = self.blnded.to_dct(exclude=["upv", "rpts", "user_dim"])
        for key in d.keys():
            setattr(item.blnded, key, d[key])
        d = self.params.to_dct()
        for key in d.keys():
            setattr(item.params, key, d[key])

    @classmethod
    def poll(cls, context):
        pool = context.scene.ptdblnpopm_pool
        return bool(pool.blnd) and pool.blnd[pool.blnd_idx].active

    def invoke(self, context, event):
        pool = context.scene.ptdblnpopm_pool
        item = pool.blnd[pool.blnd_idx]
        self.provider = item.provider
        self.fac = item.fac
        self.abs_dim = item.abs_dim
        self.copy_from_pg(item)
        if self.provider == "line":
            self.dim = self.blnded.lin_dim
        elif self.provider == "ellipse":
            self.dim = self.blnded.ell_dim
        elif self.provider == "rectangle":
            self.dim = self.blnded.rct_dim
        else:
            self.dim = self.blnded.u_dim
        self.axes_lock = False
        self.update_dims = False
        self.dim_x = self.dim[0]
        self.dim_y = self.dim[1]
        self.update_dims = True
        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        pool = scene.ptdblnpopm_pool
        pool.callbacks = False
        item = pool.blnd[pool.blnd_idx]
        item.fac = self.fac
        item.abs_dim = self.abs_dim
        if self.provider == "line":
            self.blnded.lin_dim = self.dim
        elif self.provider == "ellipse":
            self.blnded.ell_dim = self.dim
        elif self.provider == "rectangle":
            self.blnded.rct_dim = self.dim
        else:
            self.blnded.u_dim = self.dim
        self.copy_to_pg(item)
        try:
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"blnd_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def draw(self, context):
        p_name = self.provider
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        row = sc.row()
        row.label(text="Lock Axes")
        row = sc.row()
        row.prop(
            self,
            "abs_dim",
            text=("Absolute Size" if self.abs_dim else "Relative Size"),
            toggle=True,
        )
        row = sc.row()
        row.label(text="Offset")
        if p_name == "line":
            row = sc.row()
            row.label(text="Interpolation")
        elif p_name == "rectangle":
            row = sc.row()
            row.label(text="Rounded")
        elif p_name == "ellipse":
            row = sc.row()
            row.label(text="Bumps")
        row = sc.row()
        row.label(text="Vertex Order")
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(self, "axes_lock", toggle=True)
        row = sc.row(align=True)
        col = row.column(align=True)
        col.enabled = self.ctl_axis < 1
        col.prop(self, "dim_x", text="")
        col = row.column(align=True)
        col.enabled = self.ctl_axis > -1
        col.prop(self, "dim_y", text="")
        blnded = self.blnded
        row = sc.row(align=True)
        row.prop(blnded, "idx", text="")
        if p_name == "line":
            row = sc.row(align=True)
            row.prop(blnded, "lin_lerp", text="")
            row.prop(blnded, "lin_exp", text="")
        elif p_name == "rectangle":
            row = sc.row(align=True)
            row.enabled = blnded.rpts >= 8
            row.prop(blnded, "round_segs", text="")
            row.prop(blnded, "round_off", text="")
        elif p_name == "ellipse":
            row = sc.row(align=True)
            row.prop(blnded, "bump", text="")
            row.prop(blnded, "bump_val", text="")
            row.prop(blnded, "bump_exp", text="")
        row = sc.row(align=True)
        row.prop(blnded, "reverse", toggle=True)
        names = ["Items", "Repeats", "Factor"]
        params_layout_template(self, names, use_axis=False)


# ---- PATH LOCATIONS COLLECTION ITEM EDITOR


class PTDBLNPOPM_OT_pathloc_edit(bpy.types.Operator):

    bl_label = "Locations [Path]"
    bl_idname = "ptdblnpopm.pathloc_edit"
    bl_description = "path locations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    fac: bpy.props.FloatProperty(
        name="Factor",
        description="amount",
        default=0,
        min=-ModCnst.MAX_FAC,
        max=ModCnst.MAX_FAC,
    )
    axis: bpy.props.FloatVectorProperty(
        name="Influence",
        description="axis factor",
        size=3,
        default=(1, 1, 1),
        min=-1,
        max=1,
    )
    abs_move: bpy.props.BoolProperty(
        name="Absolute", description="absolute or relative axis", default=False
    )
    params: bpy.props.PointerProperty(type=PTDBLNPOPM_params)

    def copy_from_pg(self, item):
        d = item.params.to_dct()
        for key in d.keys():
            setattr(self.params, key, d[key])

    def copy_to_pg(self, item):
        d = self.params.to_dct()
        for key in d.keys():
            setattr(item.params, key, d[key])

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
        pool.callbacks = False
        item = pool.pathloc[pool.pathloc_idx]
        item.fac = self.fac
        item.abs_move = self.abs_move
        item.axis = self.axis
        self.copy_to_pg(item)
        try:
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"pathloc_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def draw(self, context):
        names = ["Items", "Repeats", "Absolute Axis", "Factor"]
        params_layout_template(self, names, use_axis=True)


# ---- PROFILE LOCATIONS COLLECTION ITEM EDITOR


class PTDBLNPOPM_OT_profloc_edit(bpy.types.Operator):

    bl_label = "Locations [Profile]"
    bl_idname = "ptdblnpopm.profloc_edit"
    bl_description = "profile locations"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    fac: bpy.props.FloatProperty(
        name="Factor",
        description="amount",
        default=0,
        min=-ModCnst.MAX_FAC,
        max=ModCnst.MAX_FAC,
    )
    axis: bpy.props.FloatVectorProperty(
        name="Influence",
        description="axis factor",
        size=2,
        default=(1, 1),
        min=-1,
        max=1,
    )
    abs_move: bpy.props.BoolProperty(
        name="Absolute", description="absolute or relative axis", default=False
    )
    params: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    gprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)

    def copy_from_pg(self, item):
        pa = item.params.to_dct()
        gp = item.gprams.to_dct()
        for pkey, gkey in zip(pa.keys(), gp.keys()):
            setattr(self.params, pkey, pa[pkey])
            setattr(self.gprams, gkey, gp[gkey])

    def copy_to_pg(self, item):
        pa = self.params.to_dct()
        gp = self.gprams.to_dct()
        for pkey, gkey in zip(pa.keys(), gp.keys()):
            setattr(item.params, pkey, pa[pkey])
            setattr(item.gprams, gkey, gp[gkey])

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
        pool.callbacks = False
        item = pool.profloc[pool.profloc_idx]
        item.fac = self.fac
        item.axis = self.axis
        item.abs_move = self.abs_move
        self.copy_to_pg(item)
        try:
            ModPop.scene_update(scene)
        except Exception as my_err:
            pool.callbacks = True
            print(f"profloc_edit: {my_err.args}")
            self.report({"INFO"}, f"{my_err.args}")
            return {"CANCELLED"}
        pool.callbacks = True
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        s = row.split(factor=0.3)
        sc = s.column(align=True)
        names = ["Groups", "Repeats"]
        for n in names:
            row = sc.row()
            row.label(text=n)
        gprams = self.gprams
        col = sc.column()
        plerp_cond = gprams.itm > 1
        col.enabled = plerp_cond
        row = col.row()
        row.prop(gprams, "lerp", text="Interpolate", toggle=True)
        row = col.row()
        row.label(text="Options")
        sc = s.column(align=True)
        row = sc.row(align=True)
        row.prop(gprams, "idx", text="")
        row.prop(gprams, "itm", text="")
        row.prop(gprams, "rev", toggle=True)
        row = sc.row(align=True)
        row.prop(gprams, "reps", text="")
        row.prop(gprams, "f2", text="")
        row.prop(gprams, "gap", text="")
        col = sc.column(align=True)
        col.enabled = plerp_cond and gprams.lerp
        row = col.row(align=True)
        row.prop(gprams, "ease", text="")
        row.prop(gprams, "exp", text="")
        row = col.row(align=True)
        row.prop(gprams, "mir", toggle=True)
        row.prop(gprams, "cyc", toggle=True)
        names = ["Points", "Repeats", "Absolute Axis", "Factor"]
        params_layout_template(self, names, use_axis=True)


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------

classes = (
    PTDBLNPOPM_float3,
    PTDBLNPOPM_anim_index,
    PTDBLNPOPM_anim_amount,
    PTDBLNPOPM_anim_rots,
    PTDBLNPOPM_params,
    PTDBLNPOPM_pathloc,
    PTDBLNPOPM_profloc,
    PTDBLNPOPM_spro,
    PTDBLNPOPM_pathed,
    PTDBLNPOPM_path,
    PTDBLNPOPM_profed,
    PTDBLNPOPM_prof,
    PTDBLNPOPM_blnd,
    PTDBLNPOPM_noiz,
    PTDBLNPOPM_track,
    PTDBLNPOPM_rngs,
    PTDBLNPOPM_obrot,
    PTDBLNPOPM_pool,
    PTDBLNPOPM_OT_path_edit,
    PTDBLNPOPM_OT_prof_edit,
    PTDBLNPOPM_OT_blnd_edit,
    PTDBLNPOPM_OT_pathloc_edit,
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

    pool = bpy.context.scene.ptdblnpopm_pool
    pool.callbacks = False
    pool.pop_mesh = None
    pool.callbacks = True

    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.ptdblnpopm_pool
    del bpy.types.Scene.ptdblnpopm_profed
    del bpy.types.Scene.ptdblnpopm_pathed
    del bpy.types.Scene.ptdblnpopm_params
