# TODO(ian): Could you Ramirez 2005 / PyAstronomy to get estimates besides B-V.
# http://www.hs.uni-hamburg.de/DE/Ins/Per/Czesla/PyA/PyA/pyaslDoc/aslDoc/aslExt_1Doc/ramirez2005.html
# https://github.com/sczesla/PyAstronomy/blob/c0aebeb3601350b50f6b869db0704c77f39d3bf3/src/pyasl/asl/aslExt_1/ramirez2005.py
# https://en.wikipedia.org/wiki/Color_index

def estimate_temperature(star):
    if not('Bmag' in star and 'Vmag' in star):
        return None

    bv = float(star['Bmag'] - star['Vmag'])
    return 4600. * (1/(0.92 * bv + 1.7) + 1/(0.92 * bv + 0.62))
