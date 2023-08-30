import hdl21 as h
from sky130_hdl21.digital_cells import high_density as s

@h.paramclass
class RO_params:

    stages = h.Param(default=7, dtype=int, desc="Number of stages in the ring oscillator")
    rows = h.Param(default=4, dtype=int, desc="Number of rows to average across the ring oscillator")

@h.generator
def gen_RO(params : RO_params) -> h.Module:

    ro = h.Module(name="RO")
    ro.VSS, ro.VDD, ro.ENABLE = 3 * h.Port()
    ro.stages = h.Port(width=params.stages)

    for i in range(params.stages):
            
            ro.add(
                s.nand2_1()(
                    A = ro.stages[i],
                    B = ro.ENABLE,
                    Y = ro.stages[(i+1) % params.stages],
                    VGND = ro.VSS,
                    VNB = ro.VSS,
                    VPWR = ro.VDD,
                    VPB = ro.VDD
                ),
                name=f"inv_{i}"
            )

    wrap = h.Module(name="wrap")
    wrap.VSS, wrap.VDD, wrap.ENABLE = 3 * h.Port()
    wrap.SQ2TRI = h.Port()
    wrap.stages = h.Signal(width=params.stages-1)
    wrap.add(ro()(VSS=wrap.VSS,
                  VDD=wrap.VDD,
                  ENABLE=wrap.ENABLE,
                  stages=h.Concat(wrap.stages, wrap.SQ2TRI)
                  ), name="ro")

    wrap2 = h.Module(name="wrap2")
    wrap2.VSS, wrap2.VDD, wrap2.ENABLE = 3 * h.Port()
    wrap2.SQ2TRI = h.Port()

    for i in range(params.rows):
        wrap2.add(wrap()(VSS=wrap2.VSS,
                        VDD=wrap2.VDD,
                        ENABLE=wrap2.ENABLE,
                        SQ2TRI=wrap2.SQ2TRI,
                        ), name=f"ro_{i}")

    return wrap2


@h.generator
def gen_VCRO(params : RO_params) -> h.Module:

    vcro = h.Module(name="VCRO")
    vcro.VSS, vcro.VDD, vcro.ENABLE, vcro.CTRL, vcro.OUT= 5* h.Port()
    vcro.SQ2TRI, vcro.TRI2SQ, vcro.BIAS = 3 * h.Signal()

    vcro.add(
        gen_RO(params)(
            VSS=vcro.VSS,
            VDD=vcro.VDD,
            ENABLE=vcro.ENABLE,
            SQ2TRI=vcro.SQ2TRI,
        ),
        name="ro"
    )

    vcro.add(
        s.inv_2()(
            A = vcro.SQ2TRI,
            Y = vcro.TRI2SQ,
            VGND = vcro.VSS,
            VNB = vcro.VSS,
            VPWR = vcro.VDD,
            VPB = vcro.VDD
        ),
        name="buf_inv"
    )

    vcro.add(
        s.inv_2()(
            A = vcro.TRI2SQ,
            Y = vcro.BIAS,
            VGND = vcro.VSS,
            VNB = vcro.VSS,
            VPWR = vcro.VDD,
            VPB = vcro.VDD
        ),
        name="buf_inv2"
    )

    vcro.add(
        s.inv_4()(
            A = vcro.CTRL,
            Y = vcro.BIAS,
            VGND = vcro.VSS,
            VNB = vcro.VSS,
            VPWR = vcro.VDD,
            VPB = vcro.VDD
        ),
        name="bias_inv"
    )

    vcro.add(
        s.inv_2()(
            A = vcro.BIAS,
            Y = vcro.OUT,
            VGND = vcro.VSS,
            VNB = vcro.VSS,
            VPWR = vcro.VDD,
            VPB = vcro.VDD
        ),
        name="out_inv"
    )

    return vcro