
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

import bpy

from . import mcnst as ModCnst


# ------------------------------------------------------------------------------
#
# ----------------------------- PROPERTIES -------------------------------------

class PTDBLNPOPM_float3(bpy.types.PropertyGroup):

    vert: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0])


class PTDBLNPOPM_anim_index(bpy.types.PropertyGroup):

    active: bpy.props.BoolProperty(name='Index', description='animate index',
            default=False, options={'HIDDEN'})
    offset: bpy.props.IntProperty(name='Offset', description='index offset',
            default=0, min=-ModCnst.MAX_IDX_OFF, max=ModCnst.MAX_IDX_OFF,
            options={'HIDDEN'})
    beg: bpy.props.IntProperty(name='Start', description='start keyframe',
            default=1, min=1, max=ModCnst.MAX_INOUT, options={'HIDDEN'})
    stp: bpy.props.IntProperty(name='Step', description='keyframe step',
            default=1, min=1, max=ModCnst.MAX_INOUT, options={'HIDDEN'})


class PTDBLNPOPM_anim_amount(bpy.types.PropertyGroup):

    active: bpy.props.BoolProperty(name='Factor',
            description='animate factor', default=False, options={'HIDDEN'})
    fac: bpy.props.FloatProperty(name='Target Factor',
            description='factor target', default=0, min=-ModCnst.MAX_FAC,
            max=ModCnst.MAX_FAC, options={'HIDDEN'})
    mirror: bpy.props.BoolProperty(name='Mirror',
            description='mirror animation', default=False, options={'HIDDEN'})
    cycles: bpy.props.IntProperty(name='Cycles',
            description='mirror cycles', default=1, min=1,
            max=ModCnst.MAX_INOUT, options={'HIDDEN'})


class PTDBLNPOPM_params(bpy.types.PropertyGroup):

    lerp: bpy.props.BoolProperty(default=False)
    ease: bpy.props.StringProperty(default='IN-OUT')
    exp: bpy.props.FloatProperty(default=1)
    mir: bpy.props.BoolProperty(default=False)
    f2: bpy.props.FloatProperty(default=1)
    idx: bpy.props.IntProperty(default=0)
    itm: bpy.props.IntProperty(default=1)
    reps: bpy.props.IntProperty(default=1)
    gap: bpy.props.IntProperty(default=0)
    rev: bpy.props.BoolProperty(default=False)

    def to_dct(self):
        d = {}
        for key in self.__annotations__.keys():
            d[key] = getattr(self, key)
        return d


class PTDBLNPOPM_ploc(bpy.types.PropertyGroup):

    def ploc_active_update(self, context):
        if not self.active:
            self.ani_idx.active = False
            self.ani_fac.active = False

    name: bpy.props.StringProperty(default='Locs')
    active: bpy.props.BoolProperty(default=False, update=ploc_active_update)
    # OT_ploc_edit - OPERATOR STORE
    fac: bpy.props.FloatProperty(default=0)
    axis: bpy.props.FloatVectorProperty(size=3, default=[1, 1, 1])
    abs_move: bpy.props.BoolProperty(default=False)
    params: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    # ANIMATION
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)
    ani_fac: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_amount)

    def to_dct(self):
        d = {'fac': self.fac, 'axis': list(self.axis),
            'abs_move': self.abs_move}
        d['params'] = self.params.to_dct()
        return d


class PTDBLNPOPM_profloc(bpy.types.PropertyGroup):

    def profloc_update(self, context):
        if not self.active:
            self.ani_itm_idx.active = False
            self.ani_idx.active = False
            self.ani_fac.active = False

    name: bpy.props.StringProperty(default='Locs')
    active: bpy.props.BoolProperty(default=False, update=profloc_update)
    # OT_profloc_edit - OPERATOR STORE
    fac: bpy.props.FloatProperty(default=0)
    axis: bpy.props.FloatVectorProperty(size=3, default=[1, 1, 0])
    params: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    gprams: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    # ANIMATION
    ani_itm_idx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)
    ani_fac: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_amount)

    def to_dct(self):
        d = {'fac': self.fac, 'axis': list(self.axis)}
        d['params'] = self.params.to_dct()
        d['gprams'] = self.gprams.to_dct()
        return d


class PTDBLNPOPM_spinroll(bpy.types.PropertyGroup):

    def sproll_active_update(self, context):
        if not self.active:
            self.ani_rot = False
        props = context.scene.ptdblnpopm_props
        if props.callbacks:
            bpy.ops.ptdblnpopm.update_default()

    active: bpy.props.BoolProperty(name='Toggle',
            description='enable/disable spinroll edits', default=False,
            update=sproll_active_update, options={'HIDDEN'})
    # OT_spinroll - OPERATOR STORE
    rot_ang: bpy.props.FloatProperty(default=0, subtype='ANGLE')
    spin_ang: bpy.props.FloatProperty(default=0, subtype='ANGLE')
    follow_limit: bpy.props.BoolProperty(default=True)
    # ANIMATION
    ani_rot: bpy.props.BoolProperty(name='Roll', description='animate roll',
            default=False, options={'HIDDEN'})
    ani_rot_ang: bpy.props.FloatProperty(name='Angle',
            description='[degrees] to rotate per keyframe', default=0, min=-3,
            max=3, subtype='ANGLE', options={'HIDDEN'})
    ani_rot_beg: bpy.props.IntProperty(name='Start',
            description='start keyframe', default=1, min=1,
            max=ModCnst.MAX_INOUT, options={'HIDDEN'})
    ani_rot_end: bpy.props.IntProperty(name='End', description='end keyframe',
            default=1, min=1, max=ModCnst.MAX_INOUT, options={'HIDDEN'})


class PTDBLNPOPM_path(bpy.types.PropertyGroup):

    def path_update(self, context):
        props = context.scene.ptdblnpopm_props
        if props.callbacks:
            if self.provider == 'custom':
                bpy.ops.ptdblnpopm.update_user(caller='path')
            else:
                bpy.ops.ptdblnpopm.update_preset(caller='path')

    def path_user_check(self, object):
        return (object.type == 'MESH')

    def path_user_update(self, context):
        props = context.scene.ptdblnpopm_props
        if props.callbacks:
            bpy.ops.ptdblnpopm.update_user(caller='path')

    clean: bpy.props.BoolProperty(default=False)
    rings: bpy.props.IntProperty(default=0)
    provider: bpy.props.EnumProperty(name='Path',
            description='path selection',
            items=( ('line', 'line', 'straight line'),
                    ('ellipse', 'ellipse', 'ellipse'),
                    ('rectangle', 'rectangle', 'rectangle'),
                    ('spiral', 'spiral', 'sphere spiral'),
                    ('custom', 'custom', 'user path') ),
            default='line', update=path_update, options={'HIDDEN'})
    res_lin: bpy.props.IntProperty(name='Segments',
            description='path segments', default=11,
            min=2, max=ModCnst.MAX_SEGS - 1,
            update=path_update, options={'HIDDEN'})
    res_spi: bpy.props.IntProperty(name='Segments',
            description='path segments', default=7,
            min=4, max=int(ModCnst.MAX_SEGS / 2) + 1,
            update=path_update, options={'HIDDEN'})
    res_rct: bpy.props.IntVectorProperty(name='Segments',
            description='path segments', size=2, default=[3, 3],
            min=1, max=int(ModCnst.MAX_SEGS / 4),
            update=path_update, options={'HIDDEN'})
    res_ell: bpy.props.IntProperty(name='Segments',
            description='path segments', default=12,
            min=3, max=ModCnst.MAX_SEGS,
            update=path_update, options={'HIDDEN'})
    user_ob: bpy.props.PointerProperty(type=bpy.types.Object,
            poll=path_user_check, update=path_user_update)
    user_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PATH] * 3)
    user_bbc: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0])
    upv: bpy.props.CollectionProperty(type=PTDBLNPOPM_float3)
    # OT_path_edit - OPERATOR STORE
    # line path
    lin_dim: bpy.props.FloatProperty(default=ModCnst.DEF_DIM_PATH)
    lin_axis: bpy.props.FloatVectorProperty(size=3, default=[1, 0, 0])
    lin_lerp: bpy.props.StringProperty(default='IN-OUT')
    lin_exp: bpy.props.FloatProperty(default=1)
    # spiral path
    spi_dim: bpy.props.FloatProperty(default=ModCnst.DEF_DIM_PATH)
    spi_revs: bpy.props.FloatProperty(default=0.5)
    # user paths
    u_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PATH] * 3)
    # ellipse
    ell_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PATH, ModCnst.DEF_DIM_PATH, 0])
    bump: bpy.props.IntProperty(default=1)
    bump_val: bpy.props.FloatProperty(default=0)
    bump_exp: bpy.props.FloatProperty(default=2)
    # rectangle
    rct_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PATH, ModCnst.DEF_DIM_PATH, 0])
    round_segs: bpy.props.IntProperty(default=0)
    round_off: bpy.props.FloatProperty(default=0.5)
    # all paths
    idx: bpy.props.IntProperty(default=0)
    closed: bpy.props.BoolProperty(default=True)
    # open paths [line/user]
    endcaps: bpy.props.BoolProperty(default=False)
    # ANIMATION
    ani_dim: bpy.props.BoolProperty(name='Size',
            description='animate dimensions', default=False, options={'HIDDEN'})
    ani_lin_dim: bpy.props.FloatProperty(name='Target Size',
            description='path size target', default=ModCnst.DEF_DIM_PATH,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM, options={'HIDDEN'})
    ani_spi_dim: bpy.props.FloatProperty(name='Target Size',
            description='path size target', default=ModCnst.DEF_DIM_PATH,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM, options={'HIDDEN'})
    ani_eru_dim: bpy.props.FloatVectorProperty(name='Target Size',
            description='path size target', size=3,
            default=[ModCnst.DEF_DIM_PATH] * 3,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM, options={'HIDDEN'})
    ani_fac: bpy.props.BoolProperty(name='Factor',
            description='animate value', default=False, options={'HIDDEN'})
    ani_lin_exp: bpy.props.FloatProperty(name='Target Exponent',
            description='line length exponent target', default=1,
            min=ModCnst.MIN_EXP, max=ModCnst.MAX_EXP, options={'HIDDEN'})
    ani_spi_revs: bpy.props.FloatProperty(name='Target Revolutions',
            description='spiral revolutions target', default=0.5,
            min=-ModCnst.MAX_FAC, max=ModCnst.MAX_FAC, options={'HIDDEN'})
    ani_fac_val: bpy.props.FloatProperty(name='Target Bump',
            description='bump value target', default=1,
            min=-ModCnst.MAX_FAC, max=ModCnst.MAX_FAC, options={'HIDDEN'})
    ani_sty_mirror: bpy.props.BoolProperty(name='Mirror',
            description='mirror animation', default=False, options={'HIDDEN'})
    ani_sty_cycles: bpy.props.IntProperty(name='Cycles',
            description='mirror cycles', default=1,
            min=1, max=ModCnst.MAX_INOUT, options={'HIDDEN'})

    def to_dct(self):
        d = dict.fromkeys(['provider', 'user_dim', 'ell_dim', 'rct_dim',
                           'u_dim', 'lin_dim', 'spi_dim', 'res_rct',
                           'res_ell', 'res_lin', 'res_spi', 'lin_lerp',
                           'lin_exp', 'lin_axis', 'spi_revs', 'round_segs',
                           'round_off', 'bump', 'bump_val', 'bump_exp',
                           'user_bbc', 'idx', 'closed', 'endcaps'])
        vecprops = [bpy.props.IntVectorProperty, bpy.props.FloatVectorProperty]
        for key in d.keys():
            if self.__annotations__[key].function in vecprops:
                d[key] = list(getattr(self, key))
            else:
                d[key] = getattr(self, key)
        d['upv'] = [list(i.vert) for i in self.upv]
        return d


class PTDBLNPOPM_prof(bpy.types.PropertyGroup):

    def prof_update(self, context):
        props = context.scene.ptdblnpopm_props
        if props.callbacks:
            if self.provider == 'custom':
                bpy.ops.ptdblnpopm.update_user(caller='prof')
            else:
                bpy.ops.ptdblnpopm.update_preset(caller='prof')

    def prof_user_check(self, object):
        return (object.type == 'MESH')

    def prof_user_update(self, context):
        props = context.scene.ptdblnpopm_props
        if props.callbacks:
            bpy.ops.ptdblnpopm.update_user(caller='prof')

    clean: bpy.props.BoolProperty(default=False)
    rpts: bpy.props.IntProperty(default=0)
    provider: bpy.props.EnumProperty(name='Profile',
            description='profile selection',
            items=( ('ellipse', 'ellipse', 'ellipse'),
                    ('rectangle', 'rectangle', 'rectangle'),
                    ('custom', 'custom', 'user profile') ),
            default='rectangle', update=prof_update, options={'HIDDEN'})
    res_rct: bpy.props.IntVectorProperty(name='Segments',
            description='profile segments', size=2, default=[3, 3], min=1,
            max=int(ModCnst.MAX_SEGS / 4), update=prof_update,
            options={'HIDDEN'})
    res_ell: bpy.props.IntProperty(name='Segments',
            description='profile segments', default=12,
            min=3, max=ModCnst.MAX_SEGS, update=prof_update, options={'HIDDEN'})
    user_ob: bpy.props.PointerProperty(type=bpy.types.Object,
            poll=prof_user_check, update=prof_user_update)
    user_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PROF, ModCnst.DEF_DIM_PROF, 0])
    user_bbc: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0])
    upv: bpy.props.CollectionProperty(type=PTDBLNPOPM_float3)
    # OT_prof_edit - OPERATOR STORE
    # all profs
    closed: bpy.props.BoolProperty(default=True)
    reverse: bpy.props.BoolProperty(default=False)
    idx: bpy.props.IntProperty(default=0)
    # user prof
    u_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PROF, ModCnst.DEF_DIM_PROF, 0])
    # ellipse
    ell_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PROF, ModCnst.DEF_DIM_PROF, 0])
    bump: bpy.props.IntProperty(default=1)
    bump_val: bpy.props.FloatProperty(default=0)
    bump_exp: bpy.props.FloatProperty(default=2)
    # rectangle (rounded corners)
    rct_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PROF, ModCnst.DEF_DIM_PROF, 0])
    round_segs: bpy.props.IntProperty(default=0)
    round_off: bpy.props.FloatProperty(default=0.5)
    # ANIMATION
    ani_dim: bpy.props.BoolProperty(name='Size',
            description='animate dimensions', default=False, options={'HIDDEN'})
    ani_eru_dim: bpy.props.FloatVectorProperty(name='Target Size',
            description='profile size target', size=3,
            default=[ModCnst.DEF_DIM_PROF] * 3,
            min=ModCnst.MIN_DIM, max=ModCnst.MAX_DIM, options={'HIDDEN'})
    ani_fac: bpy.props.BoolProperty(name='Factor',
            description='animate value', default=False, options={'HIDDEN'})
    ani_fac_val: bpy.props.FloatProperty(name='Target Bump',
            description='bump value target', default=1,
            min=-ModCnst.MAX_FAC, max=ModCnst.MAX_FAC, options={'HIDDEN'})
    ani_sty_mirror: bpy.props.BoolProperty(name='Mirror',
            description='mirror animation', default=False, options={'HIDDEN'})
    ani_sty_cycles: bpy.props.IntProperty(name='Cycles',
            description='mirror cycles', default=1,
            min=1, max=ModCnst.MAX_INOUT, options={'HIDDEN'})

    def to_dct(self):
        d = dict.fromkeys(['provider', 'user_dim', 'res_rct', 'res_ell',
                            'ell_dim', 'rct_dim', 'u_dim', 'round_segs',
                            'round_off', 'bump', 'bump_val', 'bump_exp',
                            'user_bbc', 'reverse', 'idx', 'closed'])
        vecprops = [bpy.props.IntVectorProperty, bpy.props.FloatVectorProperty]
        for key in d.keys():
            if self.__annotations__[key].function in vecprops:
                d[key] = list(getattr(self, key))
            else:
                d[key] = getattr(self, key)
        d['upv'] = [list(i.vert) for i in self.upv]
        return d


class PTDBLNPOPM_blp(bpy.types.PropertyGroup):

    def blp_user_check(self, object):
        return (object.type == 'MESH')

    def blp_user_update(self, context):
        props = context.scene.ptdblnpopm_props
        if props.callbacks:
            bpy.ops.ptdblnpopm.blp_update_user()

    def blp_active_update(self, context):
        if not self.active:
            self.ani_idx.active = False
            self.ani_fac = False

    def blp_provider_update(self, context):
        props = context.scene.ptdblnpopm_props
        if props.callbacks:
            if self.provider == 'custom':
                bpy.ops.ptdblnpopm.blp_update_user()
            else:
                bpy.ops.ptdblnpopm.blp_update_preset()

    name: bpy.props.StringProperty(default='Blend')
    # [blp segments are determined by main profile]
    provider: bpy.props.EnumProperty(name='Blend-profile',
            description='blend-profile type',
            items=( ('ellipse', 'ellipse', 'ellipse'),
                    ('rectangle', 'rectangle', 'rectangle'),
                    ('custom', 'custom', 'user profile') ),
            default='ellipse', update=blp_provider_update, options={'HIDDEN'})
    user_ob: bpy.props.PointerProperty(type=bpy.types.Object,
            poll=blp_user_check, update=blp_user_update)
    user_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PROF, ModCnst.DEF_DIM_PROF, 0])
    user_bbc: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0])
    upv: bpy.props.CollectionProperty(type=PTDBLNPOPM_float3)
    active: bpy.props.BoolProperty(default=False, update=blp_active_update)
    # OT_blp_edit - OPERATOR STORE
    # all blends
    reverse: bpy.props.BoolProperty(default=False)
    idx_off: bpy.props.IntProperty(default=0)
    # user blnd
    u_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PROF, ModCnst.DEF_DIM_PROF, 0])
    # ellipse
    ell_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PROF, ModCnst.DEF_DIM_PROF, 0])
    bump: bpy.props.IntProperty(default=1)
    bump_val: bpy.props.FloatProperty(default=0)
    bump_exp: bpy.props.FloatProperty(default=2)
    # rectangle
    rct_dim: bpy.props.FloatVectorProperty(size=3,
            default=[ModCnst.DEF_DIM_PROF, ModCnst.DEF_DIM_PROF, 0])
    round_segs: bpy.props.IntProperty(default=0)
    round_off: bpy.props.FloatProperty(default=0.5)
    # BLEND PARAMS
    fac: bpy.props.FloatProperty(default=1)
    abs_dim: bpy.props.BoolProperty(default=True)
    params: bpy.props.PointerProperty(type=PTDBLNPOPM_params)
    # ANIMATION
    ani_idx: bpy.props.PointerProperty(type=PTDBLNPOPM_anim_index)
    ani_fac: bpy.props.BoolProperty(name='Factor',
            description='animate factor', default=False, options={'HIDDEN'})
    ani_fac_val: bpy.props.FloatProperty(name='Target Factor',
            description='factor target', default=0, min=0, max=1,
            options={'HIDDEN'})
    ani_fac_mirror: bpy.props.BoolProperty(name='Mirror',
            description='mirror animation', default=False, options={'HIDDEN'})
    ani_fac_cycles: bpy.props.IntProperty(name='Cycles',
            description='mirror cycles', default=1,
            min=1, max=ModCnst.MAX_INOUT, options={'HIDDEN'})

    def to_dct(self):
        d = dict.fromkeys(['provider', 'user_dim', 'round_segs', 'round_off',
                           'ell_dim', 'rct_dim', 'u_dim', 'bump', 'bump_val',
                           'bump_exp', 'user_bbc', 'reverse', 'idx_off',
                           'fac', 'abs_dim'])
        vecprops = [bpy.props.IntVectorProperty, bpy.props.FloatVectorProperty]
        for key in d.keys():
            if self.__annotations__[key].function in vecprops:
                d[key] = list(getattr(self, key))
            else:
                d[key] = getattr(self, key)
        d['upv'] = [list(i.vert) for i in self.upv]
        d['params'] = self.params.to_dct()
        return d


class PTDBLNPOPM_noise(bpy.types.PropertyGroup):

    def noise_active_update(self, context):
        props = context.scene.ptdblnpopm_props
        if not self.active:
            self.ani_p_noise = False
            self.ani_f_noise = False
        if props.callbacks:
            bpy.ops.ptdblnpopm.update_default()

    active: bpy.props.BoolProperty(name='Toggle',
            description='enable/disable noise edits', default=False,
            update=noise_active_update, options={'HIDDEN'})
    # OT_pop_noise - OPERATOR STORE
    p_noise: bpy.props.FloatProperty(default=0)
    f_noise: bpy.props.FloatProperty(default=0)
    vfac: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 0])
    nseed: bpy.props.IntProperty(default=0)
    # ANIMATION
    ani_p_noise: bpy.props.BoolProperty(name='Path',
            description='animate path noise', default=False, options={'HIDDEN'})
    ani_p_noise_val: bpy.props.FloatProperty(name='Target',
            description='target strength',
            default=0, min=0, max=ModCnst.MAX_NOIZ, options={'HIDDEN'})
    ani_f_noise: bpy.props.BoolProperty(name='Detail',
            description='animate detail noise', default=False,
            options={'HIDDEN'})
    ani_f_noise_val: bpy.props.FloatProperty(name='Target',
            description='target strength',
            default=0, min=0, max=ModCnst.MAX_NOIZ, options={'HIDDEN'})
    ani_seed: bpy.props.BoolProperty(name='Clock Seed',
            description='animated seed', default=False, options={'HIDDEN'})
    ani_blin: bpy.props.IntProperty(name='Blend-in',
            description='blend-in keyframes',
            default=1, min=1, max=ModCnst.MAX_INOUT, options={'HIDDEN'})
    ani_blout: bpy.props.IntProperty(name='Blend-out',
            description='blend-out keyframes',
            default=1, min=1, max=ModCnst.MAX_INOUT, options={'HIDDEN'})


class PTDBLNPOPM_track(bpy.types.PropertyGroup):

    # uilist name
    name: bpy.props.StringProperty(default='Track')
    # owner/refname
    owner: bpy.props.StringProperty(default='mesh')
    t_name: bpy.props.StringProperty(default='name')
    active: bpy.props.BoolProperty(default=True)
    # OT_track_edit - OPERATOR STORE
    ac_beg: bpy.props.IntProperty(default=1)
    ac_end: bpy.props.IntProperty(default=1)
    sa_beg: bpy.props.IntProperty(default=1)
    sa_end: bpy.props.IntProperty(default=1)
    s_beg: bpy.props.IntProperty(default=1)
    s_end: bpy.props.IntProperty(default=1)
    s_sca: bpy.props.FloatProperty(default=1)
    s_rep: bpy.props.FloatProperty(default=1)
    s_bln: bpy.props.StringProperty(default=ModCnst.DEF_TRK_BLN)
    s_blendin: bpy.props.IntProperty(default=ModCnst.DEF_TRK_BLENDIN)
    s_blendout: bpy.props.IntProperty(default=ModCnst.DEF_TRK_BLENDOUT)
    s_blendauto: bpy.props.BoolProperty(default=ModCnst.DEF_TRK_BLENDAUTO)
    s_xpl: bpy.props.StringProperty(default=ModCnst.DEF_TRK_XPL)

    def to_dct(self):
        d = {}
        for key in self.__annotations__.keys():
            d[key] = getattr(self, key)
        return d


class PTDBLNPOPM_rngsel(bpy.types.PropertyGroup):

    def rngsel_edit_update(self, context):
        props = context.scene.ptdblnpopm_props
        if props.callbacks:
            bpy.ops.ptdblnpopm.update_ranges()

    # switch between face-maps OR remove-faces
    use_facemaps: bpy.props.BoolProperty(name='Face Map', default=False,
            description='use face map - do not remove faces',
            update=rngsel_edit_update, options={'HIDDEN'})
    # toggles range-selection availability
    active: bpy.props.BoolProperty(name='Toggle',
            description='active range faces', default=False,
            update=rngsel_edit_update, options={'HIDDEN'})
    invert: bpy.props.BoolProperty(name='Invert',
            description='invert selections', default=False,
            update=rngsel_edit_update, options={'HIDDEN'})
    rndsel: bpy.props.BoolProperty(name='Random',
            description='random selections ', default=False,
            update=rngsel_edit_update, options={'HIDDEN'})
    rbeg: bpy.props.IntProperty(name='Begin',
            description='range first index', default=0,
            update=rngsel_edit_update, options={'HIDDEN'})
    rend: bpy.props.IntProperty(name='End',
            description='range length', default=1,
            update=rngsel_edit_update, options={'HIDDEN'})
    ritm: bpy.props.IntProperty(name='Items',
            description='items per iteration', default=1,
            update=rngsel_edit_update, options={'HIDDEN'})
    rstp: bpy.props.IntProperty(name='Step',
            description='iteration step', default=1,
            update=rngsel_edit_update, options={'HIDDEN'})
    pbeg: bpy.props.IntProperty(name='Begin',
            description='range first index', default=0,
            update=rngsel_edit_update, options={'HIDDEN'})
    pend: bpy.props.IntProperty(name='End',
            description='range length', default=1,
            update=rngsel_edit_update, options={'HIDDEN'})
    pitm: bpy.props.IntProperty(name='Items',
            description='items per iteration', default=1,
            update=rngsel_edit_update, options={'HIDDEN'})
    pstp: bpy.props.IntProperty(name='Step',
            description='iteration step', default=1,
            update=rngsel_edit_update, options={'HIDDEN'})


class PTDBLNPOPM_obrot(bpy.types.PropertyGroup):

    def obrot_active_update(self, context):
        if not self.active:
            self.ani_rot = False
        props = context.scene.ptdblnpopm_props
        if props.callbacks:
            bpy.ops.ptdblnpopm.update_default()

    active: bpy.props.BoolProperty(name='Toggle',
            description='enable/disable rotation edits', default=False,
            update=obrot_active_update, options={'HIDDEN'})
    # OT_pop_rotate - OPERATOR STORE
    axis: bpy.props.FloatVectorProperty(size=3, default=[0, 0, 1])
    rot_ang: bpy.props.FloatProperty(default=0, subtype='ANGLE')
    # ANIMATION
    ani_rot: bpy.props.BoolProperty(name='Rotate',
            description='animate rotation', default=False, options={'HIDDEN'})
    ani_rot_ang: bpy.props.FloatProperty(name='Angle',
            description='[degrees] to rotate per keyframe',
            default=0, min=-3, max=3, subtype='ANGLE', options={'HIDDEN'})
    ani_rot_beg: bpy.props.IntProperty(name='Start',
            description='start keyframe', default=1,
            min=1, max=ModCnst.MAX_INOUT, options={'HIDDEN'})
    ani_rot_end: bpy.props.IntProperty(name='End',
            description='end keyframe', default=1,
            min=1, max=ModCnst.MAX_INOUT, options={'HIDDEN'})


class PTDBLNPOPM_props(bpy.types.PropertyGroup):

    path: bpy.props.PointerProperty(type=PTDBLNPOPM_path)
    prof: bpy.props.PointerProperty(type=PTDBLNPOPM_prof)
    spro: bpy.props.PointerProperty(type=PTDBLNPOPM_spinroll)
    noiz: bpy.props.PointerProperty(type=PTDBLNPOPM_noise)
    rngs: bpy.props.PointerProperty(type=PTDBLNPOPM_rngsel)
    obrot: bpy.props.PointerProperty(type=PTDBLNPOPM_obrot)

    plox: bpy.props.CollectionProperty(type=PTDBLNPOPM_ploc)
    plox_idx: bpy.props.IntProperty(name='Locs', default=-1,
                                    options={'HIDDEN'})
    plox_disabled: bpy.props.BoolProperty(default=False)
    proflox: bpy.props.CollectionProperty(type=PTDBLNPOPM_profloc)
    proflox_idx: bpy.props.IntProperty(name='Locs', default=-1,
                                       options={'HIDDEN'})
    proflox_disabled: bpy.props.BoolProperty(default=False)
    blpc: bpy.props.CollectionProperty(type=PTDBLNPOPM_blp)
    blpc_idx: bpy.props.IntProperty(name='Blend', default=-1,
                                    options={'HIDDEN'})
    blpc_disabled: bpy.props.BoolProperty(default=False)
    trax: bpy.props.CollectionProperty(type=PTDBLNPOPM_track)
    trax_idx: bpy.props.IntProperty(name='Track', default=-1,
                                    options={'HIDDEN'})
    trax_disabled: bpy.props.BoolProperty(default=False)

    pop_mesh: bpy.props.PointerProperty(type=bpy.types.Object)

    # animode events
    def props_act_name_get(self):
        return self.get('act_name', 'Action')

    def props_act_name_set(self, value):
        v = value.strip()
        self['act_name'] = (v if v else 'Action')

    # pop-shading events
    def props_show_wire_update(self, context):
        if self.callbacks:
            bpy.ops.ptdblnpopm.display_options(option='show_wire')

    def props_auto_smooth_update(self, context):
        if self.callbacks:
            bpy.ops.ptdblnpopm.display_options(option='auto_smooth')

    def props_shade_smooth_update(self, context):
        if self.callbacks:
            bpy.ops.ptdblnpopm.display_options(option='shade_smooth')

    # disable ops calls when updating properties from code
    callbacks: bpy.props.BoolProperty(default=True)
    show_warn: bpy.props.BoolProperty(name='Enable Warnings',
            description='show confirmation pop-ups',
            default=True, options={'HIDDEN'})
    # animation
    animorph: bpy.props.BoolProperty(name='animorph',
            description='animation mode', default=False, options={'HIDDEN'})
    ani_kf_type: bpy.props.EnumProperty(name='key_type',
            description='keyframe interpolation',
            items=( ('0', 'Constant', 'constant interpolation', 0),
                    ('1', 'Linear', 'linear interpolation', 1),
                    ('2', 'Bezier', 'bezier interpolation', 2) ),
            default='1', options={'HIDDEN'})
    ani_kf_start: bpy.props.IntProperty(name='Start',
            description='first keyframe number', default=1, options={'HIDDEN'})
    ani_kf_step: bpy.props.IntProperty(name='Step',
            description='distance (in frames) between two successive keyframes',
            default=5, min=1, options={'HIDDEN'})
    ani_kf_loop: bpy.props.IntProperty(name='Loop',
            description='number of keyframes to complete animation',
            default=16, min=2, options={'HIDDEN'})
    ani_kf_iters: bpy.props.IntProperty(name='Mirror Cycles',
            description='number used to calculate range end-frame',
            default=1, min=1, options={'HIDDEN'})
    act_name: bpy.props.StringProperty(name='Name',
            description='action name',
            default='Action', get=props_act_name_get, set=props_act_name_set)
    act_owner: bpy.props.EnumProperty(name='Owner',
            description='action owner data-block',
            items=( ('object', 'object', 'object'),
                    ('mesh', 'mesh', 'object data') ),
            default='mesh', options={'HIDDEN'})
    # pop shading
    show_wire: bpy.props.BoolProperty(name='Wireframe Display',
            description='show wireframe', default=False,
            update=props_show_wire_update, options={'HIDDEN'})
    auto_smooth: bpy.props.BoolProperty(name='Auto smooth',
            description='auto smooth normals', default=False,
            update=props_auto_smooth_update, options={'HIDDEN'})
    shade_smooth: bpy.props.BoolProperty(name='Shade smooth',
            description='smooth shading', default=False,
            update=props_shade_smooth_update, options={'HIDDEN'})


# ------------------------------------------------------------------------------
#
# --------------------------- REGISTRATION -------------------------------------

classes = (
    PTDBLNPOPM_float3,
    PTDBLNPOPM_anim_index,
    PTDBLNPOPM_anim_amount,
    PTDBLNPOPM_params,
    PTDBLNPOPM_ploc,
    PTDBLNPOPM_profloc,
    PTDBLNPOPM_spinroll,
    PTDBLNPOPM_path,
    PTDBLNPOPM_prof,
    PTDBLNPOPM_blp,
    PTDBLNPOPM_noise,
    PTDBLNPOPM_track,
    PTDBLNPOPM_rngsel,
    PTDBLNPOPM_obrot,
    PTDBLNPOPM_props,
)


def register():

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.ptdblnpopm_props = bpy.props.PointerProperty(
        type=PTDBLNPOPM_props)


def unregister():

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.ptdblnpopm_props
