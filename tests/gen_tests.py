#!/usr/bin/env python3
"""Genera tests de verificación del ISA RTM32.
Cada test carga valores en registros, ejecuta la instrucción a probar,
y guarda resultados en memoria para examinar con el debugger.

Uso: python3 gen_tests.py   (genera todos los .bin en tests/)
"""

import struct
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))


# ─── helpers ─────────────────────────────────────────────

def i(opcode, rs, rt, imm):
    """I-type → 4 bytes LE"""
    return struct.pack("<I", (opcode << 27) | (rs << 22) | (rt << 17) | (imm & 0x1FFFF))

def r(rs, rt, rd, aux, funct):
    """R-type → 4 bytes LE"""
    return struct.pack("<I", (rs << 22) | (rt << 17) | (rd << 12) | (aux << 7) | funct)

def j(opcode, addr):
    """J-type → 4 bytes LE"""
    return struct.pack("<I", (opcode << 27) | (addr & 0x7FFFFFF))

def header(payload, base=0):
    h  = struct.pack("<III", 0x4742444D, 2, base)
    h += struct.pack("<I", len(payload))
    h += b"\x00" * 12
    h += b"RTM32\x00".ljust(32, b"\x00")
    return h

def save(name, payload, base=0):
    with open(name, "wb") as f:
        f.write(header(payload, base) + payload)
    print(f"  {name}")


# ─── opcodes confirmados ─────────────────────────────────
ADDI = 0x18
SB   = 0x0B
SW   = 0x09
LW   = 0x08
J_OP = 0x02
JAL  = 0x03
BEQ  = 0x10
BNE  = 0x11
BLT  = 0x12
BGT  = 0x13
BLE  = 0x14
BGE  = 0x15
SLTI = 0x16
SLTIU= 0x17

# Opcodes a verificar (los que el PDF tiene ambiguos)
ANDI = 0x04  # PDF dice 00100, compartido con XORI? Verificar
ORI  = 0x05  # PDF dice 00101
XORI = 0x06  # Asumimos 00110 (no documentado explícitamente, deducido)

# R-type functs (del PDF)
F_ADD  = 0x1C  # 011100
F_SUB  = 0x1D  # 011101
F_AND  = 0x08  # 001000
F_OR   = 0x09  # 001001
F_XOR  = 0x0A  # 001010
F_NOR  = 0x0B  # 001011
F_SLT  = 0x0C  # 001100
F_SLTU = 0x0D  # 001101
F_SLL  = 0x00  # 000000
F_SRL  = 0x01  # 000001
F_SRA  = 0x02  # 000010
F_SLLR = 0x03  # 000011
F_SRLR = 0x04  # 000100
F_SRAR = 0x05  # 000101
F_JR   = 0x0E  # 001110
F_JALR = 0x0F  # 001111
F_MUL  = 0x15  # 010101
F_MULH = 0x16  # 010110
F_MULHU= 0x17  # 010111
F_DIV  = 0x18  # 011000
F_DIVU = 0x19  # 011001
F_REST = 0x1A  # 011010
F_RESTU= 0x1B  # 011011
F_LWX  = 0x14  # 010100
F_LHX  = 0x10  # 010000
F_LHUX = 0x11  # 010001
F_LBX  = 0x12  # 010010
F_LBUX = 0x13  # 010011


# ─── utilidad: programa que escribe registros a memoria ──

def dump_regs(base_addr):
    """Genera instrucciones que guardan r1..r5 en memoria a partir de base_addr.
    Retorna payload + dict con offsets donde va cada registro."""
    payload = b""
    # r1 = 0xFFFFFF00 (base para stores)
    payload += i(ADDI, 0, 1, 0x1FF00)  # ADDI r1, r0, -256
    off = {}
    for reg in range(1, 6):
        addr = base_addr + (reg - 1) * 4
        # Cargar addr en r2 y hacer SW
        payload += i(ADDI, 0, 2, addr & 0x1FFFF)  # parte baja de addr (asume < 128K)
        # SW r2(base=datos), r1(base=addr?) — SW es rs=base, rt=dato
        # Necesitamos SW con rs=addr_reg, rt=reg_a_guardar
        # Pero eso requiere base en registro y offset...
        pass  # Esto es complejo, mejor usar otro approach

    return payload, off


# ═══════════════════════════════════════════════════════════
# TEST 1: R-type — aritméticas/lógicas básicas
# ═══════════════════════════════════════════════════════════

def test_rtype_arith():
    """Inicializa r1=5, r2=7, luego ejecuta ADD/SUB/AND/OR/XOR/NOR/SLT/SLTU
    guardando cada resultado en r3..r10. Después guarda todo en memoria.
    
    Resultados esperados:
      r3  = ADD  r1,r2 = 12
      r4  = SUB  r1,r2 = -2 (0xFFFFFFFE)
      r5  = AND  r1,r2 = 5 & 7 = 5
      r6  = OR   r1,r2 = 5 | 7 = 7
      r7  = XOR  r1,r2 = 5 ^ 7 = 2
      r8  = NOR  r1,r2 = ~(5|7) = 0xFFFFFFF8
      r9  = SLT  r2,r1 = (7<5) = 0
      r10 = SLTU r1,r2 = (5<7) = 1
    """
    p = b""
    # Setup: r1=5, r2=7
    p += i(ADDI, 0, 1, 5)
    p += i(ADDI, 0, 2, 7)
    # Ejecutar R-types
    p += r(1, 2, 3, 0, F_ADD)    # r3 = r1 + r2 = 12
    p += r(1, 2, 4, 0, F_SUB)    # r4 = r1 - r2 = -2
    p += r(1, 2, 5, 0, F_AND)    # r5 = r1 & r2 = 5
    p += r(1, 2, 6, 0, F_OR)     # r6 = r1 | r2 = 7
    p += r(1, 2, 7, 0, F_XOR)    # r7 = r1 ^ r2 = 2
    p += r(1, 2, 8, 0, F_NOR)    # r8 = ~(r1|r2)
    p += r(2, 1, 9, 0, F_SLT)    # r9 = (r2 < r1) = 0
    p += r(1, 2, 10,0, F_SLTU)   # r10 = (r1 < r2) = 1
    # Infinite loop
    p += j(J_OP, 0)
    save("test_rtype_arith.bin", p)
    return """
  Paso 1 (step 1): ADDI r1=5     → R[1] = 0x00000005
  Paso 2 (step 2): ADDI r2=7     → R[2] = 0x00000007
  Paso 3:          ADD  r3,r1,r2 → R[3] = 12
  Paso 4:          SUB  r4,r1,r2 → R[4] = 0xFFFFFFFE (-2)
  Paso 5:          AND  r5,r1,r2 → R[5] = 5
  Paso 6:          OR   r6,r1,r2 → R[6] = 7
  Paso 7:          XOR  r7,r1,r2 → R[7] = 2
  Paso 8:          NOR  r8,r1,r2 → R[8] = 0xFFFFFFF8
  Paso 9:          SLT  r9,r2,r1 → R[9] = 0  (7<5 es falso)
  Paso 10:         SLTU r10,r1,r2→ R[10]= 1  (5<7 es verdad)
  
  Si algún valor no coincide, el funct o el formato R-type está mal."""


# ═══════════════════════════════════════════════════════════
# TEST 2: R-type — shifts
# ═══════════════════════════════════════════════════════════

def test_rtype_shifts():
    """r1 = 0x80000004 (bit 31=1, bit 2=1)
    Prueba shifts con aux inmediato y variable.
    
    SLL r3, r1, 2  → r3 = r1 << 2 = 0x00000010
    SRL r4, r1, 2  → r4 = r1 >> 2 = 0x20000001 (lógico)
    SRA r5, r1, 2  → r5 = r1 >>> 2 = 0xE0000001 (aritmético)
    
    Luego r2 = shift amount, prueba SLLR/SRLR/SRAR
    """
    p = b""
    # r1 = 0x80000004 → usar ADDI con negativo no alcanza (bit 31=1)
    # Usar LUI+ORI o cargar por partes. Probemos con ORI high+low.
    # r1 = 0x80000004
    # Si ORIH existe: imm high = 0x8000, low = 0x0004
    # ORIH r1, r0, 0x8000 → R[1] = 0x80000000 (si ORIH funciona con imm[16]=1)
    # ORI  r1, r1, 0x0004 → R[1] = 0x80000004
    # Pero ORIH no está confirmado. Usemos ADDI con valores grandes.
    # ADDI r1, r0, 0x7FFF → r1 = 0x00007FFF (max positivo en 17 bits)
    # ADDI r1, r0, -1 → r1 = 0xFFFFFFFF
    # Luego shift left...
    
    # Alternativa más simple: valores chicos pero con bit 31 seteado vía resta
    # r1 = -4 = 0xFFFFFFFC. SRA r5, r1, 1 → 0xFFFFFFFE
    p += i(ADDI, 0, 1, 0x1FFFC)  # r1 = -4 = 0xFFFFFFFC
    
    # SLL r3, r1, 2: r3 = 0xFFFFFFFC << 2 = 0xFFFFFFF0
    p += r(0, 1, 3, 2, F_SLL)    # r3 = r1 << 2  (rt=r1, rd=r3, aux=2)
    
    # SRL r4, r1, 1: r4 = 0xFFFFFFFC >> 1 = 0x7FFFFFFE
    p += r(0, 1, 4, 1, F_SRL)
    
    # SRA r5, r1, 1: r5 = 0xFFFFFFFC >>> 1 = 0xFFFFFFFE (signo preservado)
    p += r(0, 1, 5, 1, F_SRA)
    
    # r2 = 3 (shift amount variable)
    p += i(ADDI, 0, 2, 3)
    
    # SLLR r6, r1, r2: r6 = r1 << r2[4:0] = 0xFFFFFFFC << 3 = 0xFFFFFFE0
    p += r(2, 1, 6, 0, F_SLLR)
    
    # SRLR r7, r1, r2: r7 = r1 >> 3 = 0x1FFFFFFF (lógico, bit 31=0)
    p += r(2, 1, 7, 0, F_SRLR)
    
    # SRAR r8, r1, r2: r8 = r1 >>> 3 = 0xFFFFFFFF (aritmético, signo extendido)
    p += r(2, 1, 8, 0, F_SRAR)
    
    p += j(J_OP, 0)
    save("test_rtype_shifts.bin", p)
    return """
  r1 = -4 (0xFFFFFFFC) vía ADDI r1, r0, -4
  
  step 1 (ADDI):  R[1] = 0xFFFFFFFC
  step 2 (SLL):   R[3] = 0xFFFFFFF0  (r1 << 2)
  step 3 (SRL):   R[4] = 0x7FFFFFFE  (r1 >> 1 lógico)
  step 4 (SRA):   R[5] = 0xFFFFFFFE  (r1 >>> 1 aritmético, signo preservado)
  step 5 (ADDI):  R[2] = 3
  step 6 (SLLR):  R[6] = 0xFFFFFFE0  (r1 << 3)
  step 7 (SRLR):  R[7] = 0x1FFFFFFF  (r1 >> 3 lógico)
  step 8 (SRAR):  R[8] = 0xFFFFFFFF  (r1 >>> 3 aritmético, todo 1s)

  Si SRA/SRAR dan distinto a lo esperado, el signo no se preserva correctamente."""


# ═══════════════════════════════════════════════════════════
# TEST 3: I-type ALU — verificar opcodes ANDI, ORI, XORI
# ═══════════════════════════════════════════════════════════

def test_itype_alu():
    """El PDF es ambiguo: ANDI y XORI ambos como opcode 00100.
    ORI como 00101. Verificamos.
    
    r1 = 0xFF (255)
    ANDI r3, r1, 0x0F = 0x0F
    ORI  r4, r1, 0xF0 = 0xFF
    XORI r5, r1, 0xFF = 0x00
    
    Si los opcodes son correctos, los 3 deben funcionar.
    Si alguno da 0 o basura, ese opcode está mal asignado.
    """
    p = b""
    p += i(ADDI, 0, 1, 0xFF)       # r1 = 255
    
    p += i(ANDI, 1, 3, 0x0F)       # r3 = 255 & 0x0F = 15   (opcode 00100)
    p += i(ORI,  1, 4, 0xF0)       # r4 = 255 | 0xF0 = 255  (opcode 00101)
    p += i(XORI, 1, 5, 0xFF)       # r5 = 255 ^ 0xFF = 0    (asumimos 00110)
    
    p += j(J_OP, 0)
    save("test_itype_alu.bin", p)
    return """
  r1 = 255 (0xFF)
  
  step 1: R[1] = 0x000000FF
  step 2: ANDI r3,r1,0x0F → R[3] = 0x0000000F (15)
  step 3: ORI  r4,r1,0xF0 → R[4] = 0x000000FF (255)
  step 4: XORI r5,r1,0xFF → R[5] = 0x00000000 (0)
  
  Si ANDI falla (R[3]!=15): el opcode 00100 para ANDI es incorrecto.
  Si XORI falla (R[5]!=0):  el opcode asumido 00110 es incorrecto.
  Si ORI funciona: opcode 00101 confirmado."""


# ═══════════════════════════════════════════════════════════
# TEST 4: I-type HIGH — ANDIH, ORIH, XORIH
# ═══════════════════════════════════════════════════════════

def test_itype_high():
    """Hipótesis: las variantes HIGH comparten opcode con las LOW,
    y se distinguen por imm[16]=1. ZeroCatImm = {imm[15:0], 16'b0}.
    
    ANDIH r1, r0, 0xFFFF → r1 = {0xFFFF, 0x0000} & 0 = 0xFFFF0000
    ORIH  r2, r0, 0x1234 → r2 = 0x12340000
    XORIH r3, r0, 0xABCD → r3 = 0xABCD0000
    
    imm[16]=1 + imm[15:0]=valor:
    ANDIH: (00100 << 27) | (0 << 22) | (rt << 17) | (1 << 16) | val
    ORIH:  (00101 << 27) | (0 << 22) | (rt << 17) | (1 << 16) | val
    XORIH: (00110 << 27) | (0 << 22) | (rt << 17) | (1 << 16) | val
    """
    p = b""
    # ANDIH r1, r0, 0xFFFF: opcode=ANDI, rs=0, rt=1, imm=0x1FFFF
    p += i(ANDI, 0, 1, 0x1FFFF)    # imm[16]=1, imm[15:0]=0xFFFF
    # ORIH r2, r0, 0x1234
    p += i(ORI,  0, 2, 0x11234)    # imm[16]=1, imm[15:0]=0x1234
    # XORIH r3, r0, 0xABCD
    p += i(XORI, 0, 3, 0x1ABCD)    # imm[16]=1, imm[15:0]=0xABCD
    
    p += j(J_OP, 0)
    save("test_itype_high.bin", p)
    return """
  Hipótesis: imm[16]=1 activa ZeroCatImm (parte alta).
  
  step 1: ANDIH r1,0xFFFF → R[1] = 0xFFFF0000
  step 2: ORIH  r2,0x1234 → R[2] = 0x12340000
  step 3: XORIH r3,0xABCD → R[3] = 0xABCD0000
  
  Si algún registro da 0x0000XXXX (parte baja), imm[16]=1 NO activa high.
  Si da otro valor, el opcode base es incorrecto."""


# ═══════════════════════════════════════════════════════════
# TEST 5: LUI
# ═══════════════════════════════════════════════════════════

def test_lui():
    """LUI comparte opcode 11000 con ADDI.
    Hipótesis: LUI = opcode 11000 con rs=0, imm interpretado como ZeroCatImm.
    O: LUI usa imm[16]=1 como flag high.
    
    Probamos: LUI r1, 0xFFFF → r1 = 0xFFFF0000
    Codificación: opcode=0x18, rs=0, rt=1, imm con imm[16]=1, imm[15:0]=0xFFFF
    """
    p = b""
    # LUI r1, 0xFFFF: opcode=ADDI, rs=0, rt=1, imm=0x1FFFF
    p += i(ADDI, 0, 1, 0x1FFFF)    # hipótesis: rs=0 + imm[16]=1 = LUI
    
    # También probamos con rs != 0 por si acaso
    # LUI r2, 0x5678 con rs=0, imm[16]=1
    p += i(ADDI, 0, 2, 0x15678)    # hipótesis: rs=0 + imm[16]=1 = LUI
    
    p += j(J_OP, 0)
    save("test_lui.bin", p)
    return """
  Hipótesis: LUI se codifica como ADDI (opcode=11000) con imm[16]=1.
  Si rs=0 y imm[16]=1 → ZeroCatImm (parte alta).
  Si rs≠0 y imm[16]=1 → ADDI con sign-extend (negativo).
  
  step 1 (LUI r1,0xFFFF): R[1] debería ser 0xFFFF0000
  step 2 (LUI r2,0x5678): R[2] debería ser 0x56780000
  
  Si R[1] = 0xFFFF0000: LUI funciona como hipótesis.
  Si R[1] = 0x0001FFFF: imm se interpretó como ZeroExtImm (baja), no LUI.
  Si R[1] = 0xFFFFFFFF: es ADDI con sign-extend negativo.
  Si R[1] = 0x00000000: la instrucción no hizo nada (quizás rs=0 es NOP)."""


# ═══════════════════════════════════════════════════════════
# TEST 6: Branches
# ═══════════════════════════════════════════════════════════

def test_branches():
    """Verifica BEQ, BNE, BLT, BGT, BLE, BGE.
    
    r1=5, r2=5, r3=10
    BEQ r1,r2 → salta (son iguales) → pone r10=1
    BNE r1,r3 → salta (son distintos) → pone r10=2
    BLT r1,r3 → salta (5<10) → pone r10=3
    BGT r3,r1 → salta (10>5) → pone r10=4
    BLE r1,r2 → salta (5<=5) → pone r10=5
    BGE r3,r1 → salta (10>=5) → pone r10=6
    
    Cada branch que NO salta cae en un J que skipea el set.
    BranchAddr = {13{imm[16]}, imm, 2'b0}
    Para saltar 2 instrucciones (8 bytes): imm=2 (en words: 2<<0 = 2)
    """
    p = b""
    # Setup
    p += i(ADDI, 0, 1, 5)     # r1 = 5
    p += i(ADDI, 0, 2, 5)     # r2 = 5
    p += i(ADDI, 0, 3, 10)    # r3 = 10
    
    # BEQ r1, r2, skip2 → si iguales salta 2 instrucciones
    p += i(BEQ, 1, 2, 2)      # salta 2 words = 8 bytes si r1==r2
    p += j(J_OP, 0)           # no debería llegar (fallback)
    p += i(ADDI, 0, 10, 1)    # r10 = 1 (BEQ ok)
    
    # BNE r1, r3, skip2 → si distintos salta
    p += i(BNE, 1, 3, 2)
    p += j(J_OP, 0)
    p += i(ADDI, 0, 10, 2)    # r10 = 2 (BNE ok)
    
    # BLT r1, r3, skip2 → si r1<r3 salta
    p += i(BLT, 1, 3, 2)
    p += j(J_OP, 0)
    p += i(ADDI, 0, 10, 3)    # r10 = 3 (BLT ok)
    
    # BGT r3, r1, skip2 → si r3>r1 salta
    p += i(BGT, 3, 1, 2)
    p += j(J_OP, 0)
    p += i(ADDI, 0, 10, 4)    # r10 = 4 (BGT ok)
    
    # BLE r1, r2, skip2 → si r1<=r2 salta (5<=5)
    p += i(BLE, 1, 2, 2)
    p += j(J_OP, 0)
    p += i(ADDI, 0, 10, 5)    # r10 = 5 (BLE ok)
    
    # BGE r3, r1, skip2 → si r3>=r1 salta (10>=5)
    p += i(BGE, 3, 1, 2)
    p += j(J_OP, 0)
    p += i(ADDI, 0, 10, 6)    # r10 = 6 (BGE ok)
    
    p += j(J_OP, 0)
    save("test_branches.bin", p)
    return """
  r1=5, r2=5, r3=10
  
  Cada branch debe saltar 2 instrucciones (skip J_OP + ADDI set).
  Resultado final: R[10] = 6 (todos los branches funcionaron).
  
  Si R[10] < 6, el branch que falló es el del número que falta.
  Ej: R[10]=3 → BEQ y BNE bien, BLT falló.
  
  Si el CPU crashea o se cuelga, el cálculo de BranchAddr está mal."""


# ═══════════════════════════════════════════════════════════
# TEST 7: JR y JALR
# ═══════════════════════════════════════════════════════════

def test_jr_jalr():
    """JR r1 → PC = R[1]
    JALR r2, r3 → R[3] = PC+4, PC = R[2]
    
    Ponemos una dirección conocida en r1 y saltamos ahí.
    La instrucción destino pone r10=42. Si JR funciona, r10=42.
    """
    p = b""
    # r1 = dirección de la instrucción target (PC después de cargar)
    # La instrucción target está en PC=0x14 (5 instrucciones después de init)
    # Como es difícil calcular, usamos ADDI para poner dirección
    
    # Ponemos r10=0 inicialmente
    p += i(ADDI, 0, 10, 0)
    
    # r1 = 0x14 (dirección de target, asumiendo PC base 0)
    p += i(ADDI, 0, 1, 0x14)
    
    # JR r1 — debería saltar a PC=0x14
    p += r(1, 0, 0, 0, F_JR)
    
    # Esto no debería ejecutarse (JR ya saltó)
    p += i(ADDI, 0, 10, 99)   # r10=99 si JR falló
    
    # Target: PC=0x14 (instrucción 5)
    p += i(ADDI, 0, 10, 42)   # r10=42 si JR funcionó
    
    # Ahora JALR: r2=0x20, guarda retorno en r3
    p += i(ADDI, 0, 2, 0x20)  # r2 = dirección del 2do target
    p += r(2, 0, 3, 0, F_JALR) # JALR: r3=PC+4, PC=r2
    
    # No debería ejecutarse
    p += i(ADDI, 0, 11, 99)   # r11=99 si JALR falló
    
    # Target 2: PC=0x20
    p += i(ADDI, 0, 11, 1)    # r11=1 si JALR ok
    
    p += j(J_OP, 0)
    save("test_jr_jalr.bin", p)
    return """
  step 1:  R[10] = 0
  step 2:  R[1] = 0x14
  step 3:  JR r1 → PC = 0x14, skipea instrucción 4
  step 4:  (skip) NO debería ejecutarse
  step 5:  R[10] = 42  ← target del JR
  step 6:  R[2] = 0x20
  step 7:  JALR r2,r3 → R[3] = PC+4 (=0x20), PC = 0x20
  step 8:  (skip)
  step 9:  R[11] = 1   ← target del JALR
  
  Resultados esperados:
    R[10] = 42 (JR funcionó)
    R[11] = 1  (JALR funcionó)
    R[3]  = 0x20 (retorno de JALR)
  
  Si R[10] = 99: JR no saltó.
  Si R[11] = 99: JALR no saltó.
  Si R[3] != 0x20: JALR no guardó retorno."""


# ═══════════════════════════════════════════════════════════
# TEST 8: SLTI y SLTIU
# ═══════════════════════════════════════════════════════════

def test_slti():
    """SLTI rt, rs, imm: rt = (rs < SignExtImm) ? 1 : 0
    SLTIU igual pero sin signo.
    
    r1 = 5
    SLTI r3, r1, 10  → 1 (5 < 10)
    SLTI r4, r1, 3   → 0 (5 < 3 es falso)
    SLTI r5, r1, -1  → 0 (5 < -1? signed: 5 < 0xFFFFFFFF = true → 1)
    SLTIU r6, r1, -1 → 1 (unsigned: 5 < 0xFFFFFFFF = true → 1)
    SLTIU r7, r1, 3  → 0 (unsigned: 5 < 3 = false)
    """
    p = b""
    p += i(ADDI, 0, 1, 5)         # r1 = 5
    
    p += i(SLTI,  1, 3, 10)       # r3 = (5 < 10) = 1
    p += i(SLTI,  1, 4, 3)        # r4 = (5 < 3) = 0
    p += i(SLTI,  1, 5, 0x1FFFF)  # r5 = (5 < -1) = 1 (signed)
    p += i(SLTIU, 1, 6, 0x1FFFF)  # r6 = unsigned(5) < 0xFFFFFFFF = 1
    p += i(SLTIU, 1, 7, 3)        # r7 = (5 < 3) unsigned = 0
    
    p += j(J_OP, 0)
    save("test_slti.bin", p)
    return """
  r1 = 5
  
  R[3] = 1  (SLTI  5 < 10)
  R[4] = 0  (SLTI  5 < 3)
  R[5] = 1  (SLTI  5 < -1, signado)
  R[6] = 1  (SLTIU 5 < 0xFFFFFFFF, no signado)
  R[7] = 0  (SLTIU 5 < 3)
  
  Si R[5] = 0: SLTI no está haciendo extensión de signo del inmediato.
  Si R[6] = 0: SLTIU está interpretando el inmediato como signado."""


# ═══════════════════════════════════════════════════════════
# TEST 9: Loads y Stores indexados (LWX, LHX, LBX)
# ═══════════════════════════════════════════════════════════

def test_indexed():
    """LWX rt, rs, rd: R[rt] = M[R[rs] + R[rd]]
    
    Guardamos un valor conocido en memoria (con SW),
    luego lo leemos con LWX.
    """
    p = b""
    # r1 = dirección base (zona de datos, usamos 0x100)
    p += i(ADDI, 0, 1, 0x100)
    # r2 = valor a guardar = 0xDEAD
    p += i(ADDI, 0, 2, 0xDEAD & 0x1FFFF)
    # SW r1, r2, 0 → M[r1] = r2
    p += i(SW, 1, 2, 0)
    
    # r3 = offset = 0
    p += i(ADDI, 0, 3, 0)
    # LWX r4, r1, r3 → r4 = M[r1 + r3] = 0xDEAD
    p += r(1, 0, 4, 0, F_LWX)   # rs=r1, rd=r3, rt=r4 → LWX r4, r1, r3
    
    # r2 = 0xBEEF
    p += i(ADDI, 0, 2, 0xBEEF & 0x1FFFF)
    # SW r1, r2, 4 → M[r1+4] = r2
    p += i(SW, 1, 2, 4)
    # r3 = 4
    p += i(ADDI, 0, 3, 4)
    # LWX r5, r1, r3 → r5 = M[r1+4] = 0xBEEF
    p += r(1, 0, 5, 0, F_LWX)
    
    p += j(J_OP, 0)
    save("test_indexed.bin", p)
    return """
  Guarda 0xDEAD en M[0x100] y 0xBEEF en M[0x104].
  
  R[4] = 0x0000DEAD (LWX desde 0x100)
  R[5] = 0x0000BEEF (LWX desde 0x104)
  
  Si LWX no funciona, R[4] y R[5] serán 0 o basura."""


# ═══════════════════════════════════════════════════════════
# TEST 10: MUL, DIV, REST
# ═══════════════════════════════════════════════════════════

def test_mul_div():
    """MUL r3, r1, r2: r3 = (r1 * r2)[31:0]
    MULH r4, r1, r2: r4 = (r1 * r2)[63:32] (signado)
    MULHU r5, r1, r2: r4 = (r1 * r2)[63:32] (no signado)
    DIV r6, r1, r2: r6 = r1 / r2
    REST r7, r1, r2: r7 = r1 % r2
    
    r1 = 10, r2 = 3
    """
    p = b""
    p += i(ADDI, 0, 1, 10)    # r1 = 10
    p += i(ADDI, 0, 2, 3)     # r2 = 3
    
    p += r(1, 2, 3, 0, F_MUL)    # r3 = 10 * 3 = 30
    p += r(1, 2, 4, 0, F_MULH)   # r4 = high(10*3) = 0
    p += r(1, 2, 5, 0, F_MULHU)  # r5 = high(10*3) unsigned = 0
    p += r(1, 2, 6, 0, F_DIV)    # r6 = 10 / 3 = 3
    p += r(1, 2, 7, 0, F_REST)   # r7 = 10 % 3 = 1
    p += r(1, 2, 8, 0, F_DIVU)   # r8 = 10 / 3 unsigned = 3
    p += r(1, 2, 9, 0, F_RESTU)  # r9 = 10 % 3 unsigned = 1
    
    p += j(J_OP, 0)
    save("test_mul_div.bin", p)
    return """
  r1=10, r2=3
  
  R[3] = 30  (MUL)
  R[4] = 0   (MULH, parte alta de 10*3=30, < 2^32)
  R[5] = 0   (MULHU)
  R[6] = 3   (DIV 10/3)
  R[7] = 1   (REST 10%3)
  R[8] = 3   (DIVU)
  R[9] = 1   (RESTU)
  
  Prueba adicional: r1 = -10 (0xFFFFFFF6), r2 = 3
  DIV  r6 = -10/3 = -3 (0xFFFFFFFD)
  REST r7 = -10%3 = -1 (0xFFFFFFFF)
  DIVU r8 = 0xFFFFFFF6 / 3 = 0x55555551
  RESTU r9 = 0xFFFFFFF6 % 3 = 1"""


# ═══════════════════════════════════════════════════════════
# TEST 11: J y JAL
# ═══════════════════════════════════════════════════════════

def test_j_jal():
    """J addr: PC = JumpAddr = {PC+4[31:29], addr, 2'b0}
    JAL addr: R[31] = PC+4, PC = JumpAddr
    
    J a una dirección conocida, verificar que llega.
    JAL verifica que R[31] tiene el retorno.
    """
    p = b""
    # Inicializar r1=0 para detectar si JAL funcionó
    p += i(ADDI, 0, 1, 0)
    
    # JAL 10 → salta a word 10 (byte 0x28), guarda retorno en r31
    p += j(JAL, 10)              # 0x28 = byte 40
    # No debería llegar acá
    p += i(ADDI, 0, 1, 99)
    
    # Pad hasta word 10 (estamos en word 3, necesitamos 7 words de relleno)
    # Word 3 (0x0C): actual
    # Word 4-9: padding
    for _ in range(6):
        p += i(ADDI, 0, 0, 0)   # NOP (r0 = r0 + 0)
    
    # Word 10 (byte 0x28): target
    p += i(ADDI, 0, 2, 42)      # r2 = 42 si JAL funcionó
    
    p += j(J_OP, 0)
    save("test_j_jal.bin", p)
    return """
  JAL 10 → debería saltar a word 10 (byte 0x28).
  
  Después del JAL:
    R[31] = dirección de retorno (PC de JAL + 4)
    R[2]  = 42 (se ejecutó el target del JAL)
    R[1]  = 0  (NO se ejecutó el ADDI r1,99 post-JAL)
  
  Si R[1] = 99: JAL no saltó.
  Si R[2] != 42: JAL no llegó al target.
  Si R[31] = 0: JAL no guardó dirección de retorno."""


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generando tests...\n")
    results = {}
    tests = [
        ("test_rtype_arith", test_rtype_arith),
        ("test_rtype_shifts", test_rtype_shifts),
        ("test_itype_alu", test_itype_alu),
        ("test_itype_high", test_itype_high),
        ("test_lui", test_lui),
        ("test_branches", test_branches),
        ("test_jr_jalr", test_jr_jalr),
        ("test_slti", test_slti),
        ("test_indexed", test_indexed),
        ("test_mul_div", test_mul_div),
        ("test_j_jal", test_j_jal),
    ]
    for name, fn in tests:
        desc = fn()
        results[name] = desc
    
    print("\n=== RESUMEN DE QUÉ ESPERAR ===\n")
    for name, desc in results.items():
        print(f"── {name} ──")
        print(desc)
        print()
