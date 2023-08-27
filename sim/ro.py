import hdl21 as h
from sky130_hdl21.digital_cells import high_density as s

@h.paramclass
class RO_params:

    stages = h.Param(7, dtype=int, desc="Number of stages in the ring oscillator")

@h.generator
def gen_RO(params : RO_params):

    ro = h.Module()
    ro.VSS, ro.VDD = 2 * h.Port()
    ro.BIAS = h.Port()
    ro.stages = h.Port(width = params.stages)

    for i in range(params.stages):

        ro.add(
            s.inv_8(
                A = ro.stages[i % params.stages],
                Y = ro.stages[(i+1) % params.stages],
                VGND = ro.VSS,
                VNB = ro.VSS,
                VPWR = ro.VDD,
                VPB = ro.VDD
            ),
            name=f"inv_{i}"
        )

    ro.BIAS = ro.stages[-1]

    return ro

@h.generator
def gen_VCRO(params : RO_params):


    vcro = h.Module()
    vcro.VSS, vcro.VDD = 2 * h.Port()
    vcro.CTRL, vcro.BIAS, vcro.OUT = 3 * h.Port()

    vcro.add(
        gen_RO(params)(VSS=vcro.VSS, VDD=vcro.VDD, BIAS=vcro.BIAS)
        , name="ro"
    )

    vcro.add(
        s.inv_4(
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
        s.inv_4(
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