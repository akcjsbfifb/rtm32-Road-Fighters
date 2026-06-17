#!/usr/bin/env python3
"""
RTM32 assembler/disassembler — traduce .asm a snapshot .bin y viceversa.

USO:
    python3 asm.py programa.asm              # ensambla → programa.bin
    python3 asm.py programa.asm salida.bin   # ensambla → salida.bin
    python3 asm.py --dis archivo.bin         # desensambla

ENTRADA (.asm):
    ; comentarios con ; o #
    MNEMO op1, op2, op3

    Registros:     r0..r31  o  $0..$31
    Inmediatos:    42,  -5,  0x1FF,  'h',  '\n'

OPCODES SOPORTADOS:
    ─── Saltos ───
    J      addr          PC = JumpAddr
    JAL    addr          r31 = PC+4; PC = JumpAddr

    ─── Aritméticas inmediatas ───
    ADDI   rt, rs, imm   rt = rs + SignExtImm
    SLTI   rt, rs, imm   rt = (rs < SignExtImm) ? 1 : 0
    SLTIU  rt, rs, imm   rt = (rs < SignExtImm) ? 1 : 0  (sin signo)

    ─── Lógicas inmediatas ───
    ANDI   rt, rs, imm   rt = rs & ZeroExtImm
    ORI    rt, rs, imm   rt = rs | ZeroExtImm
    XORI   rt, rs, imm   rt = rs ^ ZeroExtImm

    ─── Loads/Stores ───
    LW     rt, rs, imm   rt = M[rs + SignExtImm]        (word)
    SW     rs, rt, imm   M[rs + SignExtImm] = rt         (word)
    SH     rs, rt, imm   M[rs + SignExtImm](15:0) = rt   (half)
    SB     rs, rt, imm   M[rs + SignExtImm](7:0) = rt    (byte)
    LH     rt, rs, imm   rt = sign-ext( M[rs+imm](15:0) )
    LHU    rt, rs, imm   rt = zero-ext( M[rs+imm](15:0) )
    LB     rt, rs, imm   rt = sign-ext( M[rs+imm](7:0) )
    LBU    rt, rs, imm   rt = zero-ext( M[rs+imm](7:0) )

    ─── Branches ───
    BEQ    rs, rt, imm   if rs==rt: PC=PC+4+BranchAddr
    BNE    rs, rt, imm   if rs!=rt: PC=PC+4+BranchAddr
    BLT    rs, rt, imm   if rs<rt:  PC=PC+4+BranchAddr
    BGT    rs, rt, imm   if rs>rt:  PC=PC+4+BranchAddr
    BLE    rs, rt, imm   if rs<=rt: PC=PC+4+BranchAddr
    BGE    rs, rt, imm   if rs>=rt: PC=PC+4+BranchAddr

NO SOPORTADO (R-type): SLL, SRL, SRA, SLLR, SRLR, SRAR, AND, OR,
    XOR, NOR, SLT, SLTU, JR, JALR, LHX, LHUX, LBX, LBUX, LWX,
    MUL, MULH, MULHU, DIV, DIVU, REST, RESTU, ADD, SUB, TRAP, RFT
    (usar inst_i() a mano para estas)

REQUIERE: Python 3.6+
"""

import struct
import sys
import re

# ─── Tabla de opcodes (5 bits) ────────────────────────────
OPCODES = {
    # Saltos
    "J":    0x02,   # 00010
    "JAL":  0x03,   # 00011
    # Aritméticas inmediatas
    "ADDI": 0x18,   # 11000
    "SLTI": 0x16,   # 10110
    "SLTIU":0x17,   # 10111
    # Lógicas inmediatas
    "ANDI": 0x04,   # 00100
    "ORI":  0x05,   # 00101
    "XORI": 0x06,   # 00110
    # Loads
    "LW":   0x08,   # 01000
    "LH":   0x0C,   # 01100
    "LHU":  0x0D,   # 01101
    "LB":   0x0E,   # 01110
    "LBU":  0x0F,   # 01111
    # Stores
    "SW":   0x09,   # 01001
    "SH":   0x0A,   # 01010
    "SB":   0x0B,   # 01011
    # Branches
    "BEQ":  0x10,   # 10000
    "BNE":  0x11,   # 10001
    "BLT":  0x12,   # 10010
    "BGT":  0x13,   # 10011
    "BLE":  0x14,   # 10100
    "BGE":  0x15,   # 10101
}

# Mnemónicos que usan orden inverso rs/rt (rs=base, rt=dato)
STORE_MNEM = {"SB", "SW", "SH"}

# Mnemónicos J-type (solo dirección, sin rs/rt)
JUMP_MNEM = {"J", "JAL"}


# ─── Parseo ──────────────────────────────────────────────

def parse_reg(s):
    """'r0'..'r31' o '$0'..'$31' → int"""
    s = s.strip().lower()
    for prefix in ("r", "$"):
        if s.startswith(prefix):
            n = int(s[1:])
            if 0 <= n <= 31:
                return n
            raise ValueError(f"Registro fuera de rango (0-31): {s}")
    raise ValueError(f"Registro inválido: {s}")


def parse_imm(s):
    """Inmediato: decimal, hex (0x...), char ('x'), escape (\\n, \\r, \\t, \\0)"""
    s = s.strip()
    if not s:
        raise ValueError("Inmediato vacío")
    if s.startswith("0x") or s.startswith("0X"):
        return int(s, 16)
    if s.startswith("'") and s.endswith("'"):
        inner = s[1:-1]
        if len(inner) == 1:
            return ord(inner)
        if inner.startswith("\\") and len(inner) == 2:
            esc = {"n": "\n", "r": "\r", "t": "\t", "0": "\0"}
            return ord(esc.get(inner[1], inner[1]))
        raise ValueError(f"Carácter inválido: {s}")
    return int(s)


# ─── Codificación ────────────────────────────────────────

def inst_i(opcode, rs, rt, imm):
    """I-type → 4 bytes little-endian.
    Formato: [31:27]=opcode [26:22]=rs [21:17]=rt [16:0]=imm"""
    word = (opcode << 27) | (rs << 22) | (rt << 17) | (imm & 0x1FFFF)
    return struct.pack("<I", word)


def inst_j(opcode, address):
    """J-type → 4 bytes LE.
    Formato: [31:27]=opcode [26:0]=address"""
    word = (opcode << 27) | (address & 0x7FFFFFF)
    return struct.pack("<I", word)


def assemble_line(line):
    """Traduce una línea de texto a 4 bytes. Retorna None si es comentario/vacía."""
    line = line.strip()
    if not line or line.startswith(";") or line.startswith("#"):
        return None
    if ";" in line:
        line = line[:line.index(";")]
    line = line.strip()
    if not line:
        return None

    parts = re.split(r"[,\s]+", line)
    mnem = parts[0].upper()
    args = [p for p in parts[1:] if p]

    if mnem not in OPCODES:
        raise ValueError(f"Mnemo desconocido: {mnem}")

    opcode = OPCODES[mnem]

    # J-type: J/JAL address
    if mnem in JUMP_MNEM:
        addr = parse_imm(args[0]) & 0x7FFFFFF
        return inst_j(opcode, addr)

    # I-type: 3 operandos
    a, b, imm_str = args[0], args[1], args[2]
    ra = parse_reg(a)
    rb = parse_reg(b)
    imm = parse_imm(imm_str)

    # Stores: sintaxis "SB base, dato, offset" → rs=base, rt=dato
    if mnem in STORE_MNEM:
        rs, rt = ra, rb
    else:
        # Loads, ALU: sintaxis "MNEM rt, rs, imm" → rs=fuente, rt=destino
        rs, rt = rb, ra

    return inst_i(opcode, rs, rt, imm & 0x1FFFF)


# ─── Header snapshot ─────────────────────────────────────

def build_header(payload, base_addr=0):
    """Snapshot .bin: 60 bytes de header + payload.
    Formato: magic(4) version(4) base(4) size(4) pad(12) mode(32)"""
    h  = struct.pack("<III", 0x4742444D, 2, base_addr)  # MDBG, v2, addr
    h += struct.pack("<I", len(payload))                  # size
    h += b"\x00" * 12                                     # padding [16-27]
    h += b"RTM32\x00".ljust(32, b"\x00")                  # mode [28-59]
    assert len(h) == 60
    return h


# ─── Desensamblador ──────────────────────────────────────

def disasm(word):
    """Decodifica una palabra de 32 bits a string.
    No decodifica R-type (opcode 00000)."""
    op = (word >> 27) & 0x1F
    rs = (word >> 22) & 0x1F
    rt = (word >> 17) & 0x1F
    imm = word & 0x1FFFF
    addr = word & 0x7FFFFFF

    mnem = "???"
    for m, o in OPCODES.items():
        if o == op:
            mnem = m
            break

    if op == 0:
        return f"0x{word:08X}  R-TYPE (funct={word & 0x7F})"

    if mnem in JUMP_MNEM:
        return f"0x{word:08X}  {mnem:5s} 0x{addr:07X}"

    # Sign-extend immediate
    imm_s = imm if not (imm & 0x10000) else imm - 0x20000

    if mnem in STORE_MNEM:
        return f"0x{word:08X}  {mnem:5s} r{rt}, r{rs}, {imm_s}"
    else:
        return f"0x{word:08X}  {mnem:5s} r{rt}, r{rs}, {imm_s}"


# ─── CLI ─────────────────────────────────────────────────

def cmd_dis(filename):
    """Modo desensamblador."""
    with open(filename, "rb") as f:
        data = f.read()
    if data[:4] == b"MDBG":
        print(f"; header MDBG v{struct.unpack('<I', data[4:8])[0]}, "
              f"base=0x{struct.unpack('<I', data[8:12])[0]:X}, "
              f"size={struct.unpack('<I', data[12:16])[0]}")
        data = data[60:]
    for i in range(0, len(data), 4):
        word = struct.unpack("<I", data[i:i+4])[0]
        print(f"  [{i:04x}] {data[i:i+4].hex(' '):11s} → {disasm(word)}")


def cmd_asm(infile, outfile=None):
    """Modo ensamblador."""
    if outfile is None:
        outfile = infile.rsplit(".", 1)[0] + ".bin"

    with open(infile) as f:
        lines = f.readlines()

    payload = b""
    print(f"; Ensamblando {infile} → {outfile}")
    for lineno, line in enumerate(lines, 1):
        try:
            code = assemble_line(line)
        except Exception as e:
            print(f"  Error línea {lineno}: {e}")
            sys.exit(1)
        if code is None:
            continue
        payload += code
        word = struct.unpack("<I", code)[0]
        print(f"  [{lineno:3d}] {code.hex(' '):11s} → {disasm(word)}")

    header = build_header(payload)
    with open(outfile, "wb") as f:
        f.write(header + payload)

    print(f"\n→ {outfile} ({len(header)+len(payload)} bytes: "
          f"{len(header)} header + {len(payload)} payload)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] == "--dis":
        if len(sys.argv) < 3:
            print("Uso: python3 asm.py --dis <archivo.bin>")
            sys.exit(1)
        cmd_dis(sys.argv[2])
    else:
        infile = sys.argv[1]
        outfile = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_asm(infile, outfile)
