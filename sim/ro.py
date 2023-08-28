import hdl21 as h
from sky130_hdl21.digital_cells import high_density as s

@h.paramclass
class RO_params:

    stages = h.Param(default=7, dtype=int, desc="Number of stages in the ring oscillator")

@h.generator
def gen_RO(params : RO_params) -> h.Module:

    ro = h.Module(name="ro")
    ro.VSS, ro.VDD, ro.ENABLE = 3 * h.Port()
    ro.stages = h.Port(width = params.stages)

    for i in range(params.stages):

        ro.add(
            s.nand2_1()(
                A = ro.stages[i % params.stages],
                B = ro.ENABLE,
                Y = ro.stages[(i+1) % params.stages],
                VGND = ro.VSS,
                VNB = ro.VSS,
                VPWR = ro.VDD,
                VPB = ro.VDD
            ),
            name=f"inv_{i}"
        )

    out = h.Module()
    out.VDD,out.VSS,out.ENABLE,out.BIAS = 4 * h.Port()
    out.stages = h.Signal(width=params.stages-1)

    out.add(
        ro()(VSS=out.VSS,
             VDD=out.VDD,
             stages=h.Concat(out.stages,out.BIAS),
             ENABLE=out.ENABLE),
        name="ro"
    )

    return out

@h.generator
def gen_VCRO(params : RO_params) -> h.Module:


    vcro = h.Module()
    vcro.VSS, vcro.VDD = 2 * h.Port()
    vcro.CTRL, vcro.OUT, vcro.ENABLE = 3 * h.Port()
    vcro.BIAS = h.Signal()

    vcro.add(
        gen_RO(params)(
            VSS=vcro.VSS,
            VDD=vcro.VDD,
            BIAS=vcro.BIAS,
            ENABLE=vcro.ENABLE
        )
        , name="ro"
    )

    vcro.add(
        s.inv_2()(
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