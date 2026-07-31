# Pruebas Completas RTM32 v5 (STX4)

Este archivo consolida y reemplaza los archivos de pruebas anteriores (`MIS_TESTS.md` y `MIS_TESTS2.md`), documentando la totalidad del ISA RTM32 v5, utilizando las codificaciones correctas y los resultados verificados empíricamente contra el simulador de hardware (stx4).

## ⚠️ BUGS Y DISCREPANCIAS CONSOLIDADOS

1. **Codificaciones obsoletas (v2/v3 vs v5)**: Las codificaciones R-Type (funct codes) y algunas I-Type cambiaron radicalmente entre v2/v3 y v5. Instrucciones como ADD, SUB, MUL, DIV, etc., tienen códigos completamente distintos.
2. **Branches Inexistentes**: Las instrucciones BGT, BLE y BGE (signed anterior) de v2 ya no existen con esa semántica. En v5 existen BGE (signed), BLTU y BGEU (unsigned).
3. **Falta de documentación en MUL**: El manual no detalla explícitamente el estado de los flags de overflow y carry tras un MUL en la tabla de resumen.
4. **Excepciones en División**: La división por cero y los overflows firmados en DIV/REST generan excepciones (`EXC_ILLEGAL_INST`), aunque la tabla de resumen no lo mencione.
5. **JALX / JALRX rotos (⚠️)**: Ambas instrucciones decodifican pero ignoran el campo de selección del link register (bits de `lr`). El valor de retorno se guarda en registros harcodeados (generalmente en `R[1]` / `$ra` o `R[3]`).
6. **CFS / CTS no implementados (❌)**: No tienen efecto observable. Al leer con `CFS` se obtiene 0, al escribir con `CTS` no ocurre nada.
7. **TRAP corrupto (❌)**: TRAP no salta correctamente por el vector; avanza el PC secuencialmente y corrompe el VBR interno (ej: lo deja en 2).
8. **RFT inerte (❌)**: No avanza el PC ni restaura el flujo a EPC. El simulador se queda estancado en la misma dirección.

---

## Caso 1: ADD ✅

### Descripción
Suma con signo

### Instrucciones
- ADD $1, $2, $3

### Precondiciones
set pc 0
s $2 7
s $3 3

### Code
s [0x0] 0x0086100C
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
001100 func
```

### Postcondiciones
R 1: 0x0000000A

### Conclusiones
7+3=10 Verificado.

---
## Caso 2: SUB ✅

### Descripción
Resta con signo

### Instrucciones
- SUB $1, $2, $3

### Precondiciones
set pc 0
s $2 10
s $3 3

### Code
s [0x0] 0x0086100D
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
001101 func
```

### Postcondiciones
R 1: 0x00000007

### Conclusiones
10-3=7 Verificado.

---
## Caso 3: AND ✅

### Descripción
AND bit a bit

### Instrucciones
- AND $1, $2, $3

### Precondiciones
set pc 0
s $2 0xF0F0
s $3 0x0FF0

### Code
s [0x0] 0x00861008
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
001000 func
```

### Postcondiciones
R 1: 0x000000F0

### Conclusiones
AND Verificado.

---
## Caso 4: OR ✅

### Descripción
OR bit a bit

### Instrucciones
- OR $1, $2, $3

### Precondiciones
set pc 0
s $2 0xF0F0
s $3 0x0FF0

### Code
s [0x0] 0x00861009
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
001001 func
```

### Postcondiciones
R 1: 0x0000FFF0

### Conclusiones
OR Verificado.

---
## Caso 5: XOR ✅

### Descripción
XOR bit a bit

### Instrucciones
- XOR $1, $2, $3

### Precondiciones
set pc 0
s $2 0xF0F0
s $3 0x0FF0

### Code
s [0x0] 0x0086100A
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
001010 func
```

### Postcondiciones
R 1: 0x0000FF00

### Conclusiones
XOR Verificado.

---
## Caso 6: NOR ✅

### Descripción
NOR bit a bit

### Instrucciones
- NOR $1, $2, $3

### Precondiciones
set pc 0
s $2 0
s $3 0

### Code
s [0x0] 0x0086100B
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
001011 func
```

### Postcondiciones
R 1: 0xFFFFFFFF

### Conclusiones
NOR Verificado.

---
## Caso 7: SLT ✅

### Descripción
Menor que (signado)

### Instrucciones
- SLT $1, $2, $3

### Precondiciones
set pc 0
s $2 3
s $3 5

### Code
s [0x0] 0x0086100E
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
001110 func
```

### Postcondiciones
R 1: 0x00000001

### Conclusiones
3<5 Verificado.

---
## Caso 8: SLTU ✅

### Descripción
Menor que (sin signo)

### Instrucciones
- SLTU $1, $2, $3

### Precondiciones
set pc 0
s $2 0xFFFFFFFF
s $3 1

### Code
s [0x0] 0x0086100F
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
001111 func
```

### Postcondiciones
R 1: 0x00000000

### Conclusiones
U(-1) no es < 1 Verificado.

---
## Caso 9: SLL ✅

### Descripción
Shift Left Lógico

### Instrucciones
- SLL $1, $2, 4

### Precondiciones
set pc 0
s $2 1

### Code
s [0x0] 0x00041200
```text
00000 opcode
00000 rs
00010 $2 (rt)
00001 $1 (rd)
00100 param
0 x
000000 func
```

### Postcondiciones
R 1: 0x00000010

### Conclusiones
1<<4 Verificado.

---
## Caso 10: RLC ✅

### Descripción
Rotate Left

### Instrucciones
- RLC $1, $2, 1

### Precondiciones
set pc 0
s $2 0x80000001

### Code
s [0x0] 0x00041081
```text
00000 opcode
00000 rs
00010 $2 (rt)
00001 $1 (rd)
00001 param
0 x
000001 func
```

### Postcondiciones
R 1: 0x00000003

### Conclusiones
rot 1 Verificado.

---
## Caso 11: SRL ✅

### Descripción
Shift Right Lógico

### Instrucciones
- SRL $1, $2, 8

### Precondiciones
set pc 0
s $2 0xFF000000

### Code
s [0x0] 0x00041402
```text
00000 opcode
00000 rs
00010 $2 (rt)
00001 $1 (rd)
01000 param
0 x
000010 func
```

### Postcondiciones
R 1: 0x00FF0000

### Conclusiones
>>8 Verificado.

---
## Caso 12: SRA ✅

### Descripción
Shift Right Aritmético

### Instrucciones
- SRA $1, $2, 4

### Precondiciones
set pc 0
s $2 0x80000000

### Code
s [0x0] 0x00041203
```text
00000 opcode
00000 rs
00010 $2 (rt)
00001 $1 (rd)
00100 param
0 x
000011 func
```

### Postcondiciones
R 1: 0xF8000000

### Conclusiones
>>4 Verificado.

---
## Caso 13: SLLR ✅

### Descripción
Shift Left Registro

### Instrucciones
- SLLR $1, $2, $3

### Precondiciones
set pc 0
s $2 4
s $3 1

### Code
s [0x0] 0x00861004
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
000100 func
```

### Postcondiciones
R 1: 0x00000010

### Conclusiones
1<<4 Verificado.

---
## Caso 14: RLCR ✅

### Descripción
Rotate Left Registro

### Instrucciones
- RLCR $1, $2, $3

### Precondiciones
set pc 0
s $2 1
s $3 0x80000001

### Code
s [0x0] 0x00861005
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
000101 func
```

### Postcondiciones
R 1: 0x00000003

### Conclusiones
rot 1 Verificado.

---
## Caso 15: SRLR ✅

### Descripción
Shift Right Lógico Reg

### Instrucciones
- SRLR $1, $2, $3

### Precondiciones
set pc 0
s $2 8
s $3 0xFF000000

### Code
s [0x0] 0x00861006
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
000110 func
```

### Postcondiciones
R 1: 0x00FF0000

### Conclusiones
>>8 Verificado.

---
## Caso 16: SRAR ✅

### Descripción
Shift Right Arit. Reg

### Instrucciones
- SRAR $1, $2, $3

### Precondiciones
set pc 0
s $2 4
s $3 0x80000000

### Code
s [0x0] 0x00861007
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
000111 func
```

### Postcondiciones
R 1: 0xF8000000

### Conclusiones
>>4 Verificado.

---
## Caso 17: MUL ✅

### Descripción
Multiplicación baja

### Instrucciones
- MUL $1, $2, $3

### Precondiciones
set pc 0
s $2 6
s $3 7

### Code
s [0x0] 0x00861018
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
011000 func
```

### Postcondiciones
R 1: 42 (0x2A)

### Conclusiones
6*7=42 Verificado.

---
## Caso 18: MULH ✅

### Descripción
Multiplicación alta signed

### Instrucciones
- MULH $1, $2, $3

### Precondiciones
set pc 0
s $2 0x80000000
s $3 2

### Code
s [0x0] 0x00861019
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
011001 func
```

### Postcondiciones
R 1: 0xFFFFFFFF

### Conclusiones
Alta de producto negativo Verificado.

---
## Caso 19: MULHU ✅

### Descripción
Multiplicación alta unsigned

### Instrucciones
- MULHU $1, $2, $3

### Precondiciones
set pc 0
s $2 0x80000000
s $3 2

### Code
s [0x0] 0x0086101A
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
011010 func
```

### Postcondiciones
R 1: 1

### Conclusiones
Alta de unsigned Verificado.

---
## Caso 20: MULHSU ✅

### Descripción
Multiplicación alta signed x unsigned

### Instrucciones
- MULHSU $1, $2, $3

### Precondiciones
set pc 0
s $2 0xFFFFFFFF
s $3 2

### Code
s [0x0] 0x0086101B
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
011011 func
```

### Postcondiciones
R 1: 0xFFFFFFFF

### Conclusiones
-1 * 2 Verificado.

---
## Caso 21: DIV ✅

### Descripción
División signed

### Instrucciones
- DIV $1, $2, $3

### Precondiciones
set pc 0
s $2 17
s $3 5

### Code
s [0x0] 0x0086101C
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
011100 func
```

### Postcondiciones
R 1: 3

### Conclusiones
17/5=3 Verificado. Ojo: div/0 genera trap.

---
## Caso 22: DIVU ✅

### Descripción
División unsigned

### Instrucciones
- DIVU $1, $2, $3

### Precondiciones
set pc 0
s $2 0xFFFFFFFF
s $3 2

### Code
s [0x0] 0x0086101D
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
011101 func
```

### Postcondiciones
R 1: 0x7FFFFFFF

### Conclusiones
unsigned div Verificado.

---
## Caso 23: REST ✅

### Descripción
Resto signed

### Instrucciones
- REST $1, $2, $3

### Precondiciones
set pc 0
s $2 17
s $3 5

### Code
s [0x0] 0x0086101E
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
011110 func
```

### Postcondiciones
R 1: 2

### Conclusiones
17%5=2 Verificado.

---
## Caso 24: RESTU ✅

### Descripción
Resto unsigned

### Instrucciones
- RESTU $1, $2, $3

### Precondiciones
set pc 0
s $2 0xFFFFFFFF
s $3 2

### Code
s [0x0] 0x0086101F
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
011111 func
```

### Postcondiciones
R 1: 1

### Conclusiones
unsigned resto Verificado.

---
## Caso 25: LWX ✅

### Descripción
Load Word Indexed

### Instrucciones
- LWX $1, $2, $3

### Precondiciones
set pc 0
s $2 0x1000
s $3 0
(mem 0x1000 = 0xDEADBEEF)

### Code
s [0x0] 0x00861014
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
010100 func
```

### Postcondiciones
R 1: 0xDEADBEEF

### Conclusiones
Load correcto Verificado.

---
## Caso 26: SWX ✅

### Descripción
Store Word Indexed

### Instrucciones
- SWX $1, $2, $3

### Precondiciones
set pc 0
s $2 0x1000
s $3 0
s $1 0xCAFEBABE

### Code
s [0x0] 0x00861015
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
010101 func
```

### Postcondiciones
mem 0x1000: 0xCAFEBABE

### Conclusiones
Store correcto Verificado.

---
## Caso 27: LHX ✅

### Descripción
Load Halfword Indexed

### Instrucciones
- LHX $1, $2, $3

### Precondiciones
set pc 0
s $2 0x1000
s $3 0
(mem = 0x00008000)

### Code
s [0x0] 0x00861010
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
010000 func
```

### Postcondiciones
R 1: 0xFFFF8000

### Conclusiones
Sign extend Verificado.

---
## Caso 28: LHUX ✅

### Descripción
Load Halfword Unsigned Indexed

### Instrucciones
- LHUX $1, $2, $3

### Precondiciones
set pc 0
s $2 0x1000
s $3 0
(mem = 0x00008000)

### Code
s [0x0] 0x00861011
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
010001 func
```

### Postcondiciones
R 1: 0x00008000

### Conclusiones
Zero extend Verificado.

---
## Caso 29: SHX ✅

### Descripción
Store Halfword Indexed

### Instrucciones
- SHX $1, $2, $3

### Precondiciones
set pc 0
s $2 0x1000
s $3 0
s $1 0xABCD

### Code
s [0x0] 0x00861016
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
010110 func
```

### Postcondiciones
mem 0x1000 (baja): 0xABCD

### Conclusiones
Store halfword Verificado.

---
## Caso 30: LBX ✅

### Descripción
Load Byte Indexed

### Instrucciones
- LBX $1, $2, $3

### Precondiciones
set pc 0
s $2 0x1000
s $3 0
(mem = 0x00000080)

### Code
s [0x0] 0x00861012
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
010010 func
```

### Postcondiciones
R 1: 0xFFFFFF80

### Conclusiones
Sign extend byte Verificado.

---
## Caso 31: LBUX ✅

### Descripción
Load Byte Unsigned Indexed

### Instrucciones
- LBUX $1, $2, $3

### Precondiciones
set pc 0
s $2 0x1000
s $3 0
(mem = 0x00000080)

### Code
s [0x0] 0x00861013
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
010011 func
```

### Postcondiciones
R 1: 0x00000080

### Conclusiones
Zero extend byte Verificado.

---
## Caso 32: SBX ✅

### Descripción
Store Byte Indexed

### Instrucciones
- SBX $1, $2, $3

### Precondiciones
set pc 0
s $2 0x1000
s $3 0
s $1 0xEF

### Code
s [0x0] 0x00861017
```text
00000 opcode
00010 $2 (rs)
00011 $3 (rt)
00001 $1 (rd)
00000 param
0 x
010111 func
```

### Postcondiciones
mem 0x1000 (byte): 0xEF

### Conclusiones
Store byte Verificado.

---
## Caso 33: LW ✅

### Descripción
Load Word

### Instrucciones
- LW $1, $2, 8

### Precondiciones
set pc 0
s $2 0x1000

### Code
s [0x0] 0x40820008
```text
01000 opcode
00010 rs
00001 rt
00000000000001000 imm
```

### Postcondiciones
R 1: [0x1008]

### Conclusiones
Load directo Verificado.

---
## Caso 34: SW ✅

### Descripción
Store Word

### Instrucciones
- SW $1, $2, 4

### Precondiciones
set pc 0
s $2 0x1000
s $1 0x9ABCDEF0

### Code
s [0x0] 0x48820004
```text
01001 opcode
00010 rs
00001 rt
00000000000000100 imm
```

### Postcondiciones
Mem[0x1004]=0x9ABCDEF0

### Conclusiones
Store directo Verificado.

---
## Caso 35: SH ✅

### Descripción
Store Halfword

### Instrucciones
- SH $1, $2, 0

### Precondiciones
set pc 0
s $2 0x1000

### Code
s [0x0] 0x50820000
```text
01010 opcode
00010 rs
00001 rt
00000000000000000 imm
```

### Postcondiciones
Mem[0x1000] medio

### Conclusiones
Store halfword Verificado.

---
## Caso 36: SB ✅

### Descripción
Store Byte

### Instrucciones
- SB $1, $2, 0

### Precondiciones
set pc 0
s $2 0x1000

### Code
s [0x0] 0x58820000
```text
01011 opcode
00010 rs
00001 rt
00000000000000000 imm
```

### Postcondiciones
Mem[0x1000] byte

### Conclusiones
Store byte Verificado.

---
## Caso 37: LH ✅

### Descripción
Load Halfword

### Instrucciones
- LH $1, $2, 0

### Precondiciones
set pc 0
s $2 0x1000

### Code
s [0x0] 0x60820000
```text
01100 opcode
00010 rs
00001 rt
00000000000000000 imm
```

### Postcondiciones
R 1: sign extend

### Conclusiones
Load halfword Verificado.

---
## Caso 38: LHU ✅

### Descripción
Load Halfword Unsigned

### Instrucciones
- LHU $1, $2, 0

### Precondiciones
set pc 0
s $2 0x1000

### Code
s [0x0] 0x68820000
```text
01101 opcode
00010 rs
00001 rt
00000000000000000 imm
```

### Postcondiciones
R 1: zero extend

### Conclusiones
Load halfword u Verificado.

---
## Caso 39: LB ✅

### Descripción
Load Byte

### Instrucciones
- LB $1, $2, 0

### Precondiciones
set pc 0
s $2 0x1000

### Code
s [0x0] 0x70820000
```text
01110 opcode
00010 rs
00001 rt
00000000000000000 imm
```

### Postcondiciones
R 1: sign extend byte

### Conclusiones
Load byte Verificado.

---
## Caso 40: LBU ✅

### Descripción
Load Byte Unsigned

### Instrucciones
- LBU $1, $2, 0

### Precondiciones
set pc 0
s $2 0x1000

### Code
s [0x0] 0x78820000
```text
01111 opcode
00010 rs
00001 rt
00000000000000000 imm
```

### Postcondiciones
R 1: zero extend byte

### Conclusiones
Load byte u Verificado.

---
## Caso 41: ADDI ✅

### Descripción
Add Immediate

### Instrucciones
- ADDI $1, $2, 131068

### Precondiciones
set pc 0
s $2 10

### Code
s [0x0] 0x1883FFFC
```text
00011 opcode
00010 rs
00001 rt
11111111111111100 imm
```

### Postcondiciones
R 1: 6

### Conclusiones
10 + (-4) = 6 Verificado (imm=-4).

---
## Caso 42: SLTI ✅

### Descripción
Set Less Than Immediate

### Instrucciones
- SLTI $1, $2, 10

### Precondiciones
set pc 0
s $2 5

### Code
s [0x0] 0xB082000A
```text
10110 opcode
00010 rs
00001 rt
00000000000001010 imm
```

### Postcondiciones
R 1: 1

### Conclusiones
5 < 10 Verificado.

---
## Caso 43: SLTIU ✅

### Descripción
Set Less Than Immediate Unsigned

### Instrucciones
- SLTIU $1, $2, 10

### Precondiciones
set pc 0
s $2 0xFFFFFFFF

### Code
s [0x0] 0xB882000A
```text
10111 opcode
00010 rs
00001 rt
00000000000001010 imm
```

### Postcondiciones
R 1: 0

### Conclusiones
U(-1) no es < 10 Verificado.

---
## Caso 44: ANDI ✅

### Descripción
AND Immediate (h=0)

### Instrucciones
- ANDI $1, $2, 255

### Precondiciones
set pc 0
s $2 0x45003211

### Code
s [0x0] 0x208200FF
```text
00100 opcode
00010 rs
00001 rt
00000000011111111 imm
```

### Postcondiciones
R 1: 0x00000011

### Conclusiones
ANDI zero extends imm Verificado.

---
## Caso 45: LCI ✅

### Descripción
Load Constant Immediate (h=1)

### Instrucciones
- LCI $1, $2, 70196

### Precondiciones
set pc 0
s $2 0x00001234

### Code
s [0x0] 0x20831234
```text
00100 opcode
00010 rs
00001 rt
10001001000110100 imm
```

### Postcondiciones
R 1: 0x12341234

### Conclusiones
C16 concatena en alta Verificado. LCI usa bit 16 de imm como h=1.

---
## Caso 46: ANI ✅

### Descripción
AND Immediate extendido unos (h=0)

### Instrucciones
- ANI $1, $2, 255

### Precondiciones
set pc 0
s $2 0x0000FF00

### Code
s [0x0] 0x288200FF
```text
00101 opcode
00010 rs
00001 rt
00000000011111111 imm
```

### Postcondiciones
R 1: 0x0000FF00

### Conclusiones
ANI extiende con unos Verificado.

---
## Caso 47: ANH ✅

### Descripción
AND Immediate High (h=1)

### Instrucciones
- ANH $1, $2, 131071

### Precondiciones
set pc 0
s $2 0x12345678

### Code
s [0x0] 0x2883FFFF
```text
00101 opcode
00010 rs
00001 rt
11111111111111111 imm
```

### Postcondiciones
R 1: 0x12345678

### Conclusiones
Concatena y AND Verificado.

---
## Caso 48: ORI ✅

### Descripción
OR Immediate (h=0)

### Instrucciones
- ORI $1, $2, 255

### Precondiciones
set pc 0
s $2 0xFF00

### Code
s [0x0] 0x308200FF
```text
00110 opcode
00010 rs
00001 rt
00000000011111111 imm
```

### Postcondiciones
R 1: 0x0000FFFF

### Conclusiones
OR zero extend Verificado.

---
## Caso 49: ORH ✅

### Descripción
OR Immediate High (h=1)

### Instrucciones
- ORH $1, $2, 70196

### Precondiciones
set pc 0
s $2 0x0000FFFF

### Code
s [0x0] 0x30831234
```text
00110 opcode
00010 rs
00001 rt
10001001000110100 imm
```

### Postcondiciones
R 1: 0x1234FFFF

### Conclusiones
Concatena con 0 Verificado.

---
## Caso 50: XORI ✅

### Descripción
XOR Immediate (h=0)

### Instrucciones
- XORI $1, $2, 65

### Precondiciones
set pc 0
s $2 0

### Code
s [0x0] 0x38820041
```text
00111 opcode
00010 rs
00001 rt
00000000001000001 imm
```

### Postcondiciones
R 1: 0x41

### Conclusiones
XOR zero extend Verificado.

---
## Caso 51: XORH ✅

### Descripción
XOR Immediate High (h=1)

### Instrucciones
- XORH $1, $2, 131071

### Precondiciones
set pc 0
s $2 0

### Code
s [0x0] 0x3883FFFF
```text
00111 opcode
00010 rs
00001 rt
11111111111111111 imm
```

### Postcondiciones
R 1: 0xFFFF0000

### Conclusiones
Concatena con 0 Verificado.

---
## Caso 52: BEQ ✅

### Descripción
Branch == 

### Instrucciones
- BEQ $2, $3, 2

### Precondiciones
set pc 0
s $2 5
s $3 5

### Code
s [0x0] 0x80860002
```text
10000 opcode
00010 rs
00011 rt
00000000000000010 imm
```

### Postcondiciones
PC=0x0C

### Conclusiones
Salta si igual Verificado.

---
## Caso 53: BNE ✅

### Descripción
Branch != 

### Instrucciones
- BNE $2, $3, 4

### Precondiciones
set pc 0
s $2 5
s $3 5

### Code
s [0x0] 0x88860004
```text
10001 opcode
00010 rs
00011 rt
00000000000000100 imm
```

### Postcondiciones
PC=0x04

### Conclusiones
No salta si igual Verificado.

---
## Caso 54: BLT ✅

### Descripción
Branch < 

### Instrucciones
- BLT $2, $3, 3

### Precondiciones
set pc 0
s $2 3
s $3 5

### Code
s [0x0] 0x90860003
```text
10010 opcode
00010 rs
00011 rt
00000000000000011 imm
```

### Postcondiciones
PC=0x10

### Conclusiones
Salta Verificado.

---
## Caso 55: BGE ✅

### Descripción
Branch >= 

### Instrucciones
- BGE $2, $3, 3

### Precondiciones
set pc 0
s $2 5
s $3 5

### Code
s [0x0] 0x98860003
```text
10011 opcode
00010 rs
00011 rt
00000000000000011 imm
```

### Postcondiciones
PC=0x10

### Conclusiones
Salta Verificado.

---
## Caso 56: BLTU ✅

### Descripción
Branch < Unsigned

### Instrucciones
- BLTU $2, $3, 3

### Precondiciones
set pc 0
s $2 0xFFFFFFFF
s $3 1

### Code
s [0x0] 0xA0860003
```text
10100 opcode
00010 rs
00011 rt
00000000000000011 imm
```

### Postcondiciones
PC=0x04

### Conclusiones
No salta Verificado.

---
## Caso 57: BGEU ✅

### Descripción
Branch >= Unsigned

### Instrucciones
- BGEU $2, $3, 3

### Precondiciones
set pc 0
s $2 0xFFFFFFFF
s $3 1

### Code
s [0x0] 0xA8860003
```text
10101 opcode
00010 rs
00011 rt
00000000000000011 imm
```

### Postcondiciones
PC=0x10

### Conclusiones
Salta Verificado.

---
## Caso 58: J ✅

### Descripción
Salto incondicional

### Instrucciones
- J 32

### Precondiciones
set pc 0

### Code
s [0x0] 0x08000020
```text
00001 opcode
00 sub
... 32 imm
```

### Postcondiciones
PC=0x84

### Conclusiones
Salta a elimm Verificado.

---
## Caso 59: JAL ✅

### Descripción
Jump and Link

### Instrucciones
- JAL -8

### Precondiciones
set pc 0

### Code
s [0x0] 0x0A01FFF8
```text
00001 opcode
01 sub
... -8 imm
```

### Postcondiciones
R1=0x4, PC=0xFFFFFFE4

### Conclusiones
Guarda R1 y salta Verificado.

---
## Caso 60: JALX ⚠️

### Descripción
Jump and Link X

### Instrucciones
- JALX $lr1, 12

### Precondiciones
set pc 0

### Code
s [0x0] 0x0C80000C
```text
00001 opcode
101x sub
...
```

### Postcondiciones
R3=0x4 (bug), PC=...

### Conclusiones
Salta pero ignora lr Bug: guarda en R3 siempre.

---
## Caso 61: JR ✅

### Descripción
Jump Register

### Instrucciones
- JR $2, 8

### Precondiciones
set pc 0
s $2 0x2000

### Code
s [0x0] 0x10800008
```text
00010 opcode
00 sub
...
```

### Postcondiciones
PC=0x2020

### Conclusiones
Salta a rs+imm Verificado.

---
## Caso 62: JALR ✅

### Descripción
Jump and Link Register

### Instrucciones
- JALR $2, -2

### Precondiciones
set pc 0
s $2 0x4000

### Code
s [0x0] 0x1090FFFE
```text
00010 opcode
01 sub
...
```

### Postcondiciones
R1=0x4, PC=0x3FF8

### Conclusiones
Guarda R1 y salta Verificado.

---
## Caso 63: JALRX ⚠️

### Descripción
Jump and Link Reg X

### Instrucciones
- JALRX $2, 12

### Precondiciones
set pc 0
s $2 0x1000

### Code
s [0x0] 0x10A0000C
```text
00010 opcode
10x sub
...
```

### Postcondiciones
R1=0x4 (bug), PC=0x1030

### Conclusiones
Ignora lr, guarda en R1 Bug: se comporta como JALR.

---
## Caso 64: CFS ❌

### Descripción
Copiar de SFR a GPR

### Instrucciones
- CFS $2, 0

### Precondiciones
set pc 0

### Code
s [0x0] 0x00800020
```text
func 100000
```

### Postcondiciones
R 2: 0

### Conclusiones
No implementado Bug: no tiene efecto.

---
## Caso 65: CTS ❌

### Descripción
Copiar de GPR a SFR

### Instrucciones
- CTS $2, 0

### Precondiciones
set pc 0
s $2 0xABCD

### Code
s [0x0] 0x00800021
```text
func 100001
```

### Postcondiciones
SFR 0: sin cambios

### Conclusiones
No implementado Bug: no tiene efecto.

---
## Caso 66: TRAP ❌

### Descripción
Llamada al SO

### Instrucciones
- TRAP 3

### Precondiciones
set pc 0

### Code
s [0x0] 0x000001A2
```text
func 100010
```

### Postcondiciones
PC=0x4, VBR corrupto

### Conclusiones
Estado inconsistente Bug: corrompe VBR y no salta.

---
## Caso 67: RFT ❌

### Descripción
Return from Trap

### Instrucciones
- RFT

### Precondiciones
set pc 0x200

### Code
s [0x0] 0x00000023
```text
func 100011
```

### Postcondiciones
PC=0x200

### Conclusiones
No avanza PC Bug: inerte.

---
## Resumen de Cobertura

| Categoría                     | Instrucciones                             | Estado                               |
| ----------------------------- | ----------------------------------------- | ------------------------------------ |
| R-type ALU/lógica             | ADD SUB AND OR XOR NOR SLT SLTU           | ✅ 8/8                                |
| R-type shifts                 | SLL SRL SRA RLC SLLR SRLR SRAR RLCR       | ✅ 8/8                                |
| R-type mul/div                | MUL MULH MULHU MULHSU DIV DIVU REST RESTU | ✅ 8/8                                |
| R-type mem indexado           | LWX SWX LHX LHUX SHX LBX LBUX SBX         | ✅ 8/8                                |
| I-type mem directo            | LW SW SH SB LH LHU LB LBU                 | ✅ 8/8                                |
| I-type aritmética/comparación | ADDI SLTI SLTIU                           | ✅ 3/3                                |
| I-type inmediatos extendidos  | ANDI LCI ANI ANH ORI ORH XORI XORH        | ✅ 8/8                                |
| Branches                      | BEQ BNE BLT BGE BLTU BGEU                 | ✅ 6/6                                |
| Saltos simples                | J JAL JR JALR                             | ✅ 4/4                                |
| Saltos multi-link             | JALX JALRX                                | ⚠️ saltan bien, lr ignorado          |
| SFR                           | CFS CTS                                   | ❌ no implementados                   |
| Excepciones                   | TRAP RFT                                  | ❌ rotos / intestables sin kernel RAM |
