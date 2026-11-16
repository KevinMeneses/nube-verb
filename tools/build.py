"""Genera nube_verb.jsfx desde src/nube_verb.template.jsfx.
La red de retardos (FDN) va desenrollada con variables sueltas en vez de arreglos: en EEL2 es ~3x más rápido.
Marcadores: //@GEN:<NOMBRE>@ en una línea propia."""
import pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "src/nube_verb.template.jsfx", ROOT / "nube_verb.jsfx"

def par(v): return bin(v).count("1") & 1
def oL(i): return -1 if par(i & 5) else 1          # filas ortogonales de Hadamard
def oR(i): return -1 if par(i & 10) else 1
def inS(i): return -1 if (i >> 1) & 1 else 1
def sgn(x, s): return f"+ {x}" if s > 0 else f"- {x}"
def num(x): return f"{x:.9f}".rstrip("0")

def load(n=16):
    out = []
    for i in range(n):
        out.append(f"  f_kl{i} = lkl[{i}] - 1; f_kh{i} = lkh[{i}] - 1; f_g{i} = lgm[{i}]; f_ap{i} = apN[{i}]; f_cw{i} = mcw[{i}]; f_sw{i} = msw[{i}];")
    for i in range(8):
        out.append(f"  f_id{i} = idN[{i}];")
    return "\n".join(out)

def init(n=16):
    out = []
    for i in range(n):
        out.append(f"f_b{i} = lbuf + {i} * LSZ; f_a{i} = apbuf + {i} * APSZ; f_ls{i} = f_dd{i} = lnT[{i}]; f_di{i} = 0; "
                   f"f_mc{i} = mcos[{i}]; f_ms{i} = msin[{i}]; f_sl{i} = f_sh{i} = 0;")
    for i in range(8):
        out.append(f"f_ib{i} = idbuf + {i} * IDSZ;")
    return "\n".join(out)

def ctrl(n=16):
    out = []
    for i in range(n):
        out.append(f"  f_c = f_mc{i} * f_cw{i} - f_ms{i} * f_sw{i}; f_ms{i} = f_ms{i} * f_cw{i} + f_mc{i} * f_sw{i}; f_mc{i} = f_c; "
                   f"f_ls{i} += (lnT[{i}] - f_ls{i}) * lnk16; f_di{i} = (f_ls{i} + mdep * (1 + f_ms{i}) - f_dd{i}) * 0.0625;")
    return "\n".join(out)

def renorm(n=16):
    return "\n".join(f"f_c = 1 / sqrt(f_mc{i} * f_mc{i} + f_ms{i} * f_ms{i}); f_mc{i} *= f_c; f_ms{i} *= f_c;" for i in range(n))

def diff():
    out = []
    for ch, base in (("L", 0), ("R", 4)):
        src = f"a_p{ch}"
        for k in range(4):
            j = base + k
            out.append(f"f_d = f_ib{j}[(a_iw - f_id{j}) & 4095]; f_w = {src} + idg * f_d; f_ib{j}[a_iw] = f_w; a_d{ch} = f_d - idg * f_w;")
            src = f"a_d{ch}"
    return "\n".join(out)

def read(n):
    out = []
    for i in range(n):
        out += [f"  f_dd{i} += f_di{i}; a_rp = a_w - f_dd{i}; a_ri = floor(a_rp); a_fr = a_rp - a_ri;",
                f"  f_y = f_b{i}[a_ri & 65535]; f_y += (f_b{i}[(a_ri + 1) & 65535] - f_y) * a_fr;",
                f"  f_v = (f_y - f_sl{i}) * glo; f_lp = f_v + f_sl{i}; f_sl{i} = f_lp + f_v; f_y += f_kl{i} * f_lp;",
                f"  f_v = (f_y - f_sh{i}) * ghi; f_lp = f_v + f_sh{i}; f_sh{i} = f_lp + f_v; f_y += f_kh{i} * (f_y - f_lp);",
                f"  f_r{i} = f_y * f_g{i};"]
    out.append("  a_tL = " + " ".join(sgn(f"f_r{i}", oL(i)) for i in range(n)).lstrip("+ ") + ";")
    out.append("  a_tR = " + " ".join(sgn(f"f_r{i}", oR(i)) for i in range(n)).lstrip("+ ") + ";")
    h = 1
    while h < n:
        for i in range(0, n, 2 * h):
            for j in range(i, i + h):
                out.append(f"  f_t = f_r{j}; f_r{j} = f_t + f_r{j + h}; f_r{j + h} = f_t - f_r{j + h};")
        h *= 2
    return "\n".join(out)

def write(n):
    hs = n ** -0.5; out = []
    for i in range(n):
        ch = "R" if i & 1 else "L"
        out += [f"  f_x = f_r{i} * {num(hs)} {sgn('a_d' + ch, inS(i))} {sgn('a_shv * ' + num(hs), oL(i))};",
                f"  f_y = f_a{i}[(a_aw - f_ap{i}) & 8191]; f_x += apg * f_y; f_a{i}[a_aw] = f_x; f_b{i}[a_w] = f_y - apg * f_x;"]
    return "\n".join(out)

def er_load():
    return "\n".join(f"  e_t{k} = erT[{k}]; e_g{k} = erG[{k}];" for k in range(32))

def er_sum():
    # L: tomas pares del lado L, impares del R; R al revés
    def side(ch, off):
        terms = []
        for k in range(16):
            buf = "f_ebL" if (k & 1) == (0 if ch == "L" else 1) else "f_ebR"
            terms.append(f"e_g{off + k} * {buf}[(a_ew - e_t{off + k}) & 65535]")
        return f"  a_e{ch} = " + "\n    + ".join(terms) + ";"
    return side("L", 0) + "\n" + side("R", 16)

GEN = {"ERLOAD": er_load(), "ERSUM": er_sum(), "LOAD": load(), "INIT": init(), "CTRL": ctrl(), "RENORM": renorm(), "DIFF": diff(),
       "READ16": read(16), "READ8": read(8), "WRITE16": write(16), "WRITE8": write(8)}
txt = SRC.read_text()
def sub(m):
    return GEN[m.group(1)]
txt, k = re.subn(r"^[ \t]*//@GEN:(\w+)@[ \t]*$", sub, txt, flags=re.M)
assert k == len(GEN), f"marcadores: {k} de {len(GEN)}"
first, rest = txt.split("\n", 1)
DST.write_text(first + "\n// ARCHIVO GENERADO por tools/build.py desde src/nube_verb.template.jsfx: editar la plantilla.\n" + rest)
print(f"ok: {DST.name} ({len(txt.splitlines())} líneas)")
