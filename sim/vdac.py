# Modified from https://github.com/iic-jku/tt03-tempsensor/blob/main/src/vdac_cell.v
import hdl21 as h
from hdl21.prefix import n, p
from sky130_hdl21.digital_cells import high_density as s
from sky130_hdl21 import Sky130LogicParams as lp
import sky130_hdl21 as sky130

p = lp()

@h.module
class vDAC_cell:

    VSS, VDD = 2 * h.Port()
    i_sign, i_data, i_enable = 3 * h.Input()
    vout = h.Output()

    #! Control logic
    # npu_pd = ~i_data;
    npu_pd = s.inv_1(p)(A=i_data,
                        VGND = VSS,
                        VNB = VSS,
                        VPWR = VDD,
                        VPB = VDD)

    # en_vref = i_enable & (~(i_sign ^ i_data))
    xor = s.xor2_1(p)(A=i_sign,
                      B=i_data,
                      VGND = VSS,
                      VNB = VSS,
                      VPWR = VDD,
                      VPB = VDD)
    
    en_vref = s.and2_1(p)(A=i_enable,
                       B=xor.X,
                       VGND = VSS,
                       VNB = VSS,
                       VPWR = VDD,
                       VPB = VDD)
    # en_vref = and1.X

    # en_pupd = i_enable & (i_sign^i_data);
    ixor = s.inv_1(p)(A=xor.X,
                      VGND = VSS,
                      VNB = VSS,
                      VPWR = VDD,
                      VPB = VDD
                      )
    en_pupd = s.and2_1(p)(A=i_enable,
                       B=ixor.Y,
                       VGND=VSS,
                       VNB=VSS,
                       VPWR=VDD,
                       VPB=VDD)
    # en_pupd = and2.X

    # Modules
    cell_1 = s.einvp_1(p)(A=npu_pd.Y, TE=en_pupd.X, Z=vout,
                          VGND=VSS,VNB=VSS,VPWR=VDD,VPB=VDD)
    cell_2 = s.einvp_1(p)(A=vout, TE=en_vref.X, Z=vout,
                          VGND=VSS,VNB=VSS,VPWR=VDD,VPB=VDD)


@h.paramclass
class vDAC_Params:
    
        npar = h.Param(default=2, dtype=int, desc="Number of parallel cells")
        ncells = h.Param(default=6, dtype=int, desc="Number of cells per parallel cell")

@h.generator
def gen_vDAC_cells(params : vDAC_Params) -> h.Module:

    cell = h.Module()
    cell.VSS, cell.VDD = 2 * h.Port()
    cell.i_sign, cell.i_data, cell.i_enable = 3 * h.Input()
    cell.vout = h.Output()

    # Connect multiple VDAC cells
    for n in range(params.npar):

        cell.add(
            vDAC_cell()(
                i_sign=cell.i_sign,
                i_data=cell.i_data,
                i_enable=cell.i_enable,
                vout=cell.vout,
                VSS=cell.VSS,
                VDD=cell.VDD,
            ),
            name=f"cell{n}",
        )

    return cell


@h.generator
def gen_vDAC(params : vDAC_Params) -> h.Module:
    
    vdac = h.Module()

    vdac.inp_bus = h.Input(width=params.ncells)
    vdac.enable = h.Input()
    vdac.vout = h.Output()
    vdac.VSS, vdac.VDD = 2 * h.Port()

    for n in range(params.ncells - 1):

        vdac.add(
            gen_vDAC_cells(params)(
                i_sign=vdac.inp_bus[params.ncells - 1],
                i_data=vdac.inp_bus[n],
                i_enable=vdac.enable,
                vout=vdac.vout,
                VSS=vdac.VSS,
                VDD=vdac.VDD,
            ),
            name=f"paracell{n}",
        )

    return vdac


def twos_complement(num, width):

    max_value = 2 ** (width - 1) - 1

    if num > max_value or num < -max_value - 1:
        raise ValueError("Number falls outside the width")

    if num < 0:
        num = (1 << width) + num

    binary = bin(num)[2:].zfill(width)

    return [int(b) for b in binary][::-1]


@h.paramclass
class bus_signal_params:
    width = h.Param(default=6, dtype=int, desc="Width of the bus")
    inp = h.Param(default=0, dtype=int, desc="Input value")

@h.generator
def bus_signal(params : bus_signal_params) -> h.Module:

    bits = twos_complement(params.inp, params.width)

    vsources = h.Module()
    vsources.vout = h.Output(width=params.width)
    vsources.vss = h.Port()

    for n in range(params.width):

        vsources.add(h.Vdc(dc=1.8 * bits[n])(p=vsources.vout[n], n=vsources.vss), name=f"vdc{n}")

    return vsources