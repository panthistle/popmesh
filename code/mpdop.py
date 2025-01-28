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
# ------------------------- BMPGS OPERATOR FUNCTIONS ---------------------------


def line(cns, cvs, pgob, isprof=False):
    names = ("Length", "Lerp")
    for n in names:
        row = cns.row()
        row.label(text=n)
    row = cvs.row(align=True)
    row.prop(pgob, "lin_dim", text="")
    row = cvs.row(align=True)
    rc = row.column(align=True)
    rc.prop(pgob, "lin_ease", text="")
    rc = row.column(align=True)
    rc.enabled = pgob.lin_ease != "LINEAR"
    rc.prop(pgob, "lin_exp", text="")


def wave(cns, cvs, pgob, isprof=False):
    names = ("Length", "Amplitude", "Factor")
    for n in names:
        row = cns.row()
        row.label(text=n)
    row = cvs.row(align=True)
    row.prop(pgob, "wav_dim", text="")
    row = cvs.row(align=True)
    row.prop(pgob, "wav_amp", text="")
    row = cvs.row(align=True)
    row.prop(pgob, "wav_frq", text="")
    row.prop(pgob, "wav_pha", text="")


def arc(cns, cvs, pgob, isprof=False):
    names = ("Chord", "Factor", "Offset")
    for n in names:
        row = cns.row()
        row.label(text=n)
    row = cvs.row(align=True)
    row.prop(pgob, "arc_dim", text="")
    row = cvs.row(align=True)
    row.prop(pgob, "arc_fac", text="")
    row = cvs.row(align=True)
    row.prop(pgob, "arc_off", text="")


def ellipse(cns, cvs, pgob, isprof=False):
    names = ("Size", "", "Steps")
    for n in names:
        row = cns.row()
        row.label(text=n)
    row = cvs.row(align=True)
    row.prop(pgob, "ell_dim", index=0, text="")
    row = cvs.row(align=True)
    row.prop(pgob, "ell_dim", index=1, text="")
    row = cvs.row(align=True)
    row.prop(pgob, "ellstep", text="")
    row.prop(pgob, "ellstep_val", text="")
    row.prop(pgob, "ellstep_exp", text="")


def polygon(cns, cvs, pgob, isprof=False):
    names = ("Size", "", "Sides", "Corner", "Lerp")
    for n in names:
        row = cns.row()
        row.label(text=n)
    row = cvs.row(align=True)
    row.prop(pgob, "pol_dim", index=0, text="")
    row = cvs.row(align=True)
    row.prop(pgob, "pol_dim", index=1, text="")
    row = cvs.row(align=True)
    row.prop(pgob, "pol_sid", text="")
    row.prop(pgob, "pol_ang", text="")
    row = cvs.row(align=True)
    rc = row.column(align=True)
    rc.prop(pgob, "pol_coff", text="")
    rc = row.column(align=True)
    rc.enabled = pgob.pol_coff > 0.001
    rc.prop(pgob, "pol_cres", text="")
    row = cvs.row(align=True)
    rc = row.column(align=True)
    rc.prop(pgob, "pol_ease", text="")
    rc = row.column(align=True)
    rc.enabled = pgob.pol_ease != "LINEAR"
    rc.prop(pgob, "pol_exp", text="")


def helix(cns, cvs, pgob):
    names = ("Width", "", "Factor", "Length", "Factor", "Lerp")
    for n in names:
        row = cns.row()
        row.label(text=n)
    row = cvs.row(align=True)
    row.prop(pgob, "hel_dim", index=0, text="")
    row = cvs.row(align=True)
    row.prop(pgob, "hel_dim", index=1, text="")
    row = cvs.row(align=True)
    col = row.column(align=True)
    col.prop(pgob, "hel_fac", text="")
    col = row.column(align=True)
    col.enabled = pgob.hel_fac != 1.0
    col.prop(pgob, "hel_mir", text="mirror", toggle=True)
    col = row.column(align=True)
    col.enabled = (pgob.hel_fac != 1.0) and not pgob.hel_mir
    col.prop(pgob, "hel_invert", toggle=True)
    row = cvs.row(align=True)
    col = row.column(align=True)
    col.prop(pgob, "hel_len", text="")
    col = row.column(align=True)
    col.enabled = pgob.hel_ease != "LINEAR"
    col.prop(pgob, "hel_hlrp", text="Ease", toggle=True)
    row = cvs.row(align=True)
    col = row.column(align=True)
    col.prop(pgob, "hel_stp", text="")
    col = row.column(align=True)
    col.prop(pgob, "hel_pha", text="")
    row = cvs.row(align=True)
    rc = row.column(align=True)
    rc.prop(pgob, "hel_ease", text="")
    rc = row.column(align=True)
    rc.enabled = pgob.hel_ease != "LINEAR"
    rc.prop(pgob, "hel_exp", text="")


def spiral(cns, cvs, pgob):
    names = ("Diameter", "Frequency")
    for n in names:
        row = cns.row()
        row.label(text=n)
    row = cvs.row(align=True)
    row.prop(pgob, "spi_dim", text="")
    row = cvs.row(align=True)
    row.prop(pgob, "spi_revs", text="")


def custom(cns, cvs, pgob, isprof=False):
    ndims = 2 if isprof else 3
    n = None
    for i in range(ndims):
        if pgob.user_dim[i]:
            row = cns.row()
            n = "Size" if not n else " "
            row.label(text=n)
            row = cvs.row(align=True)
            row.prop(pgob, "cust_dim", index=i, text="")
    row = cns.row()
    row.label(text="Pivot")
    row = cvs.row(align=True)
    col = row.column(align=True)
    col.prop(pgob, "user_piv", index=0, text="")
    col = row.column(align=True)
    col.prop(pgob, "user_piv", index=1, text="")
    if not isprof:
        col = row.column(align=True)
        col.prop(pgob, "user_piv", index=2, text="")


def params_layout_draw(box, pgob, names):
    row = box.row(align=True)
    s = row.split(factor=0.25)
    sc = s.column(align=True)
    for n in names:
        row = sc.row()
        row.label(text=n)
    row = sc.row()
    row.label(text="Lerp")
    row = sc.row()
    row.label(text="Style")
    sc = s.column(align=True)
    row = sc.row(align=True)
    row.prop(pgob, "idx", text="")
    row.prop(pgob, "itm", text="")
    row.prop(pgob, "gap", text="")
    row = sc.row(align=True)
    row.prop(pgob, "reps", text="")
    row.prop(pgob, "repfoff", text="")
    row.prop(pgob, "repfstp", text="")
    col = sc.column(align=True)
    row = col.row(align=True)
    rc = row.column(align=True)
    rc.prop(pgob, "ease", text="")
    rc = row.column(align=True)
    rc.enabled = pgob.ease not in {"OFF", "LINEAR"}
    rc.prop(pgob, "exp", text="")
    rc = row.column(align=True)
    rc.enabled = pgob.ease != "OFF"
    rc.prop(pgob, "cyc", toggle=True)
    row = col.row(align=True)
    rc = row.column(align=True)
    rc.enabled = pgob.ease != "OFF"
    rc.prop(pgob, "mir", toggle=True)
    rc = row.column(align=True)
    rc.enabled = pgob.ease != "OFF"
    rc.prop(pgob, "reflect", text="")
    rc = row.column(align=True)
    rc.prop(pgob, "rev", toggle=True)
