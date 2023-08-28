import hdl21 as h
import hdl21.prefix as hp

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
    time = h.Param(default=1*hp.UNIT, dtype=h.Prefixed, desc="Time of the simulation")

@h.generator
def static_bus_signal(params : bus_signal_params) -> h.Module:

    bits = twos_complement(params.inp, params.width)

    vsources = h.Module()
    vsources.vout = h.Output(width=params.width)
    vsources.vss = h.Port()

    for n in range(params.width):

        vsources.add(h.Vdc(dc=1.8 * bits[n])(p=vsources.vout[n], n=vsources.vss), name=f"vdc{n}")

    return vsources

# Good for cycling through all binary numbers
@h.generator
def dynamic_bus_signal(params : bus_signal_params) -> h.Module:

    vsources = h.Module()
    vsources.vout = h.Output(width=params.width)
    vsources.vss = h.Port()

    for n in range(params.width):

        vsources.add(
            h.PulseVoltageSource(
                delay=params.time / (2**(n+1)),
                v1=0,
                v2=1.8,
                period=params.time / (2**(n)),
                rise=1*hp.NANO,
                fall=1*hp.NANO,
                width=params.time / (2**(n+1)),
            )(
                p=vsources.vout[n],
                n=vsources.vss), 
            name=f"vdc{n}"
        )

    return vsources

@h.generator
def dynamic_step_signal(params : bus_signal_params) -> h.Module:

    vsources = h.Module()
    vsources.vout = h.Output(width=params.width)
    vsources.vss = h.Port()

    for n in range(params.width):

        if n != params.width - 1 :
            vsources.add(
                h.PulseVoltageSource(
                    delay= (n+1) * params.time / (2*params.width),
                    v1=0,
                    v2=1.8,
                    period=params.time/2,
                    rise=1*hp.NANO,
                    fall=1*hp.NANO,
                    width=params.time/2 - ((n+1) * params.time / (2*params.width)),
                )(
                    p=vsources.vout[n],
                    n=vsources.vss),
            name = f"vdc{n}",
            )
        else: 
            vsources.add(
                h.PulseVoltageSource(
                    delay= params.time / 2,
                    v1=0,
                    v2=1.8,
                    period=params.time,
                    rise=1*hp.NANO,
                    fall=1*hp.NANO,
                    width=params.time,
                )(
                    p=vsources.vout[n],
                    n=vsources.vss),
            name = f"vdc{n}",
            )

    return vsources