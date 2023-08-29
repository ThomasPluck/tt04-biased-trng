import hdl21 as h
from sky130_hdl21.digital_cells import high_density as s

@h.paramclass
class RO_params:

    stages = h.Param(default=7, dtype=int, desc="Number of stages in the ring oscillator")

@h.generator
def gen_VCRO(params : RO_params) -> h.Module:

    vcro = h.Module(name="VCRO")
    vcro.VSS, vcro.VDD, vcro.ENABLE, vcro.CTRL, vcro.OUT= 5* h.Port()
    vcro.BIAS = h.Signal()
    vcro.stages = h.Signal(width = params.stages)

    for i in range(params.stages):

        vcro.add(
            s.nand2_2()(
                A = vcro.stages[i % params.stages],
                B = vcro.ENABLE,
                Y = vcro.stages[(i+1) % params.stages],
                VGND = vcro.VSS,
                VNB = vcro.VSS,
                VPWR = vcro.VDD,
                VPB = vcro.VDD
            ),
            name=f"inv_{i}"
        )

    vcro.add(
        s.inv_2()(
            A = vcro.stages[-1],
            Y = vcro.BIAS,
            VGND = vcro.VSS,
            VNB = vcro.VSS,
            VPWR = vcro.VDD,
            VPB = vcro.VDD
        ),
        name="buf_inv"
    )

    vcro.add(
        s.inv_16()(
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
        s.inv_16()(
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