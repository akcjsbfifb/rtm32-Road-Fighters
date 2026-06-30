# Guía de testing manual de instrucciones RTM32 (v0.4)

> Cada sección tiene: qué hace la instrucción, cómo se genera el hex (bit a bit), y comandos exactos para probar. Usá `r` para ver registros, `n` para step.

---

## 1. Arrancar

```bash
# Terminal 1
./rtm32 -d telnet -m 4K

# Terminal 2
telnet localhost 4444
```

Prompt: `RTM32>`. Atajos: `r`=registers, `n`=step, `s`=set, `x`=examine, `c`=continue.

---

## 2. Ritual mínimo (4 pasos)

```
reset                  # CPU a cero. ATENCIÓN: PC queda en 0xF0000000 (KERNEL)
set pc 0               # movemos PC a 0x0 para ejecutar desde ahí
s r2, 5                # cargo operandos
s r3, 7
s [0x0], 0x0086101C    # escribo la instrucción ADD r1,r2,r3 en 0x0
n                      # ejecuto 1 instrucción
r                      # veo resultados
```

**Lo que falló en tu primer intento:** después de `reset` el PC estaba en `0xF0000000`. Escribiste `0x0086101C` en `0x0`, pero el CPU ejecutó lo que había en `0xF0000000` (instrucción basura), no tu ADD. Por eso `r1` siguió en 0 y apareció `CAUSE=0x01`.

---

## 3. Cómo se genera cada hex (la fórmula)

| Tipo   | Layout bit 31 → bit 0                                                |
|--------|----------------------------------------------------------------------|
| I-type | `opcode[31:27] rs[26:22] rt[21:17] imm[16:0]`                       |
| R-type | `00000[31:27] rs[26:22] rt[21:17] rd[16:12] aux[11:7] funct[6:0]`  |
| J-type | `opcode[31:27] address[26:0]`                                        |

- **I-type**: `imm` son 17 bits. Sign-extend a 32. Si `imm[16]=1` en ANDI/ORI/XORI → modo high (ZeroCatImm = {imm[15:0], 16'b0}). Si `imm[16]=1` y `rs=0` en opcode 0x18 → LUI.
- **R-type**: registros por número: $0=0, $1=1, ... $31=31. `aux` = shift amount en shifts. Los indexed loads (LWX, LHX...) usan `rt` como destino y `rd` como offset.
- **Branches**: `PC_nuevo = PC+4 + {13{imm[16]}, imm, 2'b0}`. imm=1 → saltea 1 word (4 bytes) hacia adelante. imm=0x1FFFF → salta 1 word hacia atrás.
- **Jumps**: `PC_nuevo = {PC+4[31:29], address, 2'b0}`. J 4 salta a 0x10.

---

## 4. Casos de test

En todos: `reset` + `set pc 0` antes de empezar. Cada caso incluye la explicación bit a bit del encoding.

---

### 4.1 ADD — Suma (R-type)

**Qué hace:** `$1 = $2 + $3`

**Encoding ADD $1, $2, $3 — 0x0086101C:**

```
bit 31..27 → opcode = 00000    (R-type)
bit 26..22 → rs     = 00010    ($2)
bit 21..17 → rt     = 00011    ($3)
bit 16..12 → rd     = 00001    ($1, destino)
bit 11..7  → aux    = 00000
bit 6..0   → funct  = 0011100  (ADD = 0x1C = 28 decimal)

Juntando los 32 bits:
  00000 00010 00011 00001 00000 0011100
= 0000 0000 1000 0110 0001 0000 0001 1100
= 0    0    8    6    1    0    1    C
= 0x0086101C
```

```bash
reset
set pc 0
s r2, 5
s r3, 7
s [0x0], 0x0086101C
n
r
```

**Esperado:** `r1 = 0x0000000C` (12), `r2 = 5`, `r3 = 7`, `PC = 0x00000004`


---

### 4.2 SUB — Resta (R-type)

**Qué hace:** `$1 = $2 - $3`

**Encoding SUB $1, $2, $3 — 0x0086101D:**

```
bit 31..27 → opcode = 00000    (R-type)
bit 26..22 → rs     = 00010    ($2)
bit 21..17 → rt     = 00011    ($3)
bit 16..12 → rd     = 00001    ($1)
bit 11..7  → aux    = 00000
bit 6..0   → funct  = 0011101  (SUB = 0x1D = 29 decimal)
                                                 ↑
                               único bit diferente vs ADD (0x1C→0x1D)
```

```bash
reset
set pc 0
s r2, 10
s r3, 3
s [0x0], 0x0086101D
n
r
```

**Esperado:** `r1 = 7`

---

### 4.3 ADDI — Suma con inmediato (I-type)

**Qué hace:** `$1 = $2 + sign_extend(imm)`

**Encoding ADDI $1, $2, 5 — 0xC0820005:**

```
bit 31..27 → opcode = 11000    (ADDI = 0x18)
bit 26..22 → rs     = 00010    ($2, fuente)
bit 21..17 → rt     = 00001    ($1, destino)
bit 16..0  → imm    = 0_0000_0000_0000_0101  (5 en 17 bits)

Juntando:
  11000 00010 00001 00000000000000101
= 1100 0000 1000 0010 0000 0000 0000 0101
= C    0    8    2    0    0    0    5
= 0xC0820005
```

```bash
reset
set pc 0
s r2, 10
s [0x0], 0xC0820005
n
r
```

**Esperado:** `r1 = 15`

**Con negativo: ADDI $1, $2, -3 — 0xC083FFFD:**

```
bit 31..27 → opcode = 11000
bit 26..22 → rs     = 00010    ($2)
bit 21..17 → rt     = 00001    ($1)
bit 16..0  → imm    = 1_1111_1111_1111_1101  (-3 en 17 bits: 0x1FFFD)

Juntando:
  11000 00010 00001 11111111111111101
= 1100 0000 1000 0011 1111 1111 1111 1101
= C    0    8    3    F    F    F    D
= 0xC083FFFD
```

```bash
reset
set pc 0
s r2, 10
s [0x0], 0xC083FFFD
n
r
```

**Esperado:** `r1 = 7` (10 + (-3))

---

### 4.4 AND, OR, XOR, NOR (R-type)

Todos usan `$1 = op($2, $3)` con `rs=$2, rt=$3, rd=$1`. Solo cambia `funct` (bits 6..0).

| Instr | funct (7 bits) | Hex completo     | Operación          | r2   | r3   | Esperado r1     |
|-------|----------------|------------------|---------------------|------|------|------------------|
| AND   | `0001000` 0x08 | `0x00861008`     | r1 = r2 & r3        | 0xFF | 0x0F | 0x0F             |
| OR    | `0001001` 0x09 | `0x00861009`     | r1 = r2 \| r3        | 0xF0 | 0x0F | 0xFF             |
| XOR   | `0001010` 0x0A | `0x0086100A`     | r1 = r2 ^ r3        | 0xFF | 0x0F | 0xF0             |
| NOR   | `0001011` 0x0B | `0x0086100B`     | r1 = ~(r2 \| r3)    | 0xF0 | 0x00 | 0xFFFFFF0F       |

**Ejemplo detallado — AND 0x00861008:**

```
00000 00010 00011 00001 00000 0001000
  ↑     ↑     ↑     ↑     ↑      ↑
 R-type $2    $3    $1    0    AND=0x08
```

```bash
# AND
reset && set pc 0 && s r2, 0xFF && s r3, 0x0F && s [0x0], 0x00861008 && n && r
# OR
reset && set pc 0 && s r2, 0xF0 && s r3, 0x0F && s [0x0], 0x00861009 && n && r
# XOR
reset && set pc 0 && s r2, 0xFF && s r3, 0x0F && s [0x0], 0x0086100A && n && r
# NOR
reset && set pc 0 && s r2, 0xF0 && s r3, 0x00 && s [0x0], 0x0086100B && n && r
```

---

### 4.5 ANDI, ORI, XORI (I-type)

**Qué hace:** `$1 = $2 op zero_extend(imm)`. imm se extiende con ceros (16 bits de 0 arriba).

**Encoding ANDI $1, $2, 0xF — 0x2082000F:**

```
bit 31..27 → opcode = 00100    (ANDI = 0x04)
bit 26..22 → rs     = 00010    ($2)
bit 21..17 → rt     = 00001    ($1)
bit 16..0  → imm    = 0_0000_0000_0000_1111  (0xF en 17 bits, imm[16]=0 → modo normal)

00100 00010 00001 00000000000001111
= 0x2082000F
```

| Instr | opcode | Hex             | r2   | Esperado r1 |
|-------|--------|-----------------|------|-------------|
| ANDI  | 0x04   | `0x2082000F`    | 0xFF | 0x0F        |
| ORI   | 0x05   | `0x28820008`    | 0xF0 | 0xF8        |
| XORI  | 0x06   | `0x3082000F`    | 0xFF | 0xF0        |

```bash
# ANDI
reset && set pc 0 && s r2, 0xFF && s [0x0], 0x2082000F && n && r
# ORI
reset && set pc 0 && s r2, 0xF0 && s [0x0], 0x28820008 && n && r
# XORI
reset && set pc 0 && s r2, 0xFF && s [0x0], 0x3082000F && n && r
```

---

### 4.6 ANDIH, ORIH, XORIH — High inmediatas (I-type, imm[16]=1)

**Qué hace:** imm[16]=1 activa `ZeroCatImm = {imm[15:0], 16{1'b0}}`. El inmediato va a los 16 bits **altos**. Ej: ANDIH $1, $2, 0x1234 hace `$1 = $2 & 0x12340000`.

**Encoding ANDIH $1, $2, 0x1234 — 0x20831234:**

```
bit 31..27 → opcode = 00100    (mismo opcode que ANDI)
bit 26..22 → rs     = 00010    ($2)
bit 21..17 → rt     = 00001    ($1)
bit 16..0  → imm    = 1_0001_0010_0011_0100  (0x11234)
                      ↑
                      imm[16]=1 → activa modo HIGH

ANDIH usa ZeroCatImm = {0x1234, 16'b0} = 0x12340000
```

| Instr | opcode | imm[15:0] | Hex             | r2          | Esperado r1    |
|-------|--------|-----------|-----------------|-------------|-----------------|
| ANDIH | 0x04   | 0x1234    | `0x20831234`    | 0xFFFFFFFF  | 0x12340000      |
| ORIH  | 0x05   | 0x5678    | `0x28835678`    | 0           | 0x56780000      |
| XORIH | 0x06   | 0x9ABC    | `0x30839ABC`    | 0           | 0x9ABC0000      |

```bash
# ANDIH
reset && set pc 0 && s r2, 0xFFFFFFFF && s [0x0], 0x20831234 && n && r
# ORIH
reset && set pc 0 && s r2, 0 && s [0x0], 0x28835678 && n && r
# XORIH
reset && set pc 0 && s r2, 0 && s [0x0], 0x30839ABC && n && r
```

---

### 4.7 LUI — Load Upper Immediate (I-type)

**Qué hace:** `$1 = {imm[15:0], 16'b0}`. Es ADDI con `rs=0` e `imm[16]=1`. No suma nada, solo carga.

**Encoding LUI $1, 0x1234 — 0xC0031234:**

```
bit 31..27 → opcode = 11000    (mismo opcode que ADDI, 0x18)
bit 26..22 → rs     = 00000    ($0 = 0, por eso NO suma)
bit 21..17 → rt     = 00001    ($1, destino)
bit 16..0  → imm    = 1_0001_0010_0011_0100  (0x11234)
                      ↑
                      imm[16]=1 con rs=0 → LUI
Resultado: r1 = 0x1234 << 16 = 0x12340000
```

```bash
reset
set pc 0
s [0x0], 0xC0031234
n
r
```

**Esperado:** `r1 = 0x12340000`

---

### 4.8 SLT, SLTU — Set Less Than (R-type)

**Qué hace:** `$1 = ($2 < $3) ? 1 : 0`. SLT usa comparación signed, SLTU unsigned.

**Encoding SLT $1, $2, $3 — 0x0086100C:**

```
00000 00010 00011 00001 00000 0001100
  ↑     ↑     ↑     ↑     ↑      ↑
 R-type $2    $3    $1    0    SLT=0x0C
```

SLTU usa funct `0001101` (0x0D) → `0x0086100D`.

```bash
# SLT: 5 < 10 → true (1)
reset && set pc 0 && s r2, 5 && s r3, 10 && s [0x0], 0x0086100C && n && r

# SLT: 10 < 5 → false (0)
reset && set pc 0 && s r2, 10 && s r3, 5 && s [0x0], 0x0086100C && n && r

# SLTU: -1 (0xFFFFFFFF) < 1 → false (0), porque unsigned 0xFFFFFFFF > 1
reset && set pc 0 && s r2, -1 && s r3, 1 && s [0x0], 0x0086100D && n && r
```

---

### 4.9 SLTI, SLTIU — Set Less Than Immediate (I-type)

**Qué hace:** `$1 = ($2 < sign_extend(imm)) ? 1 : 0`

**Encoding SLTI $1, $2, 10 — 0xB082000A:**

```
bit 31..27 → opcode = 10110    (SLTI = 0x16)
bit 26..22 → rs     = 00010    ($2)
bit 21..17 → rt     = 00001    ($1)
bit 16..0  → imm    = 0_0000_0000_0000_1010  (10)

10110 00010 00001 00000000000001010
= 0xB082000A
```

SLTIU: opcode = 10111 (0x17) → `0xB882000A`

```bash
# SLTI: 5 < 10 → 1
reset && set pc 0 && s r2, 5 && s [0x0], 0xB082000A && n && r

# SLTI: 15 < 10 → 0
reset && set pc 0 && s r2, 15 && s [0x0], 0xB082000A && n && r

# SLTIU: -1 < 1 unsigned → 0 (0xFFFFFFFF no < 1)
reset && set pc 0 && s r2, -1 && s [0x0], 0xB8820001 && n && r
```

---

### 4.10 Shifts inmediatos: SLL, SRL, SRA (R-type)

**Qué hace:** shift por constante. `rs` no se usa (va 0), `aux` contiene el shift amount, `rd`=destino, `rt`=fuente.

**Encoding SLL $1, $2, 4 — 0x00041200:**

```
bit 31..27 → opcode = 00000    (R-type)
bit 26..22 → rs     = 00000    (no se usa en shift inmediato)
bit 21..17 → rt     = 00010    ($2, valor a shiftear)
bit 16..12 → rd     = 00001    ($1, destino)
bit 11..7  → aux    = 00100    (4, cantidad de shift)
bit 6..0   → funct  = 0000000  (SLL = 0x00)

00000 00000 00010 00001 00100 0000000
= 0x00041200
```

| Instr | funct | Hex             | r2          | Esperado r1    |
|-------|-------|-----------------|-------------|-----------------|
| SLL   | 0x00  | `0x00041200`    | 3           | 48 (3 << 4)     |
| SRL   | 0x01  | `0x00041201`    | 0x80        | 8 (0x80 >> 4)   |
| SRA   | 0x02  | `0x00041202`    | 0x80000000  | 0xF8000000      |

```bash
# SLL
reset && set pc 0 && s r2, 3 && s [0x0], 0x00041200 && n && r
# SRL
reset && set pc 0 && s r2, 0x80 && s [0x0], 0x00041201 && n && r
# SRA
reset && set pc 0 && s r2, 0x80000000 && s [0x0], 0x00041202 && n && r
```

Para SRA: 0x80000000 es el número más negativo (bit 31=1). Al shift right aritmético 4 bits, se rellena con 1s → 0xF8000000.

---

### 4.11 Shifts variables: SLLR, SRLR, SRAR (R-type)

**Qué hace:** el shift amount viene de `$rs[4:0]` (5 bits bajos). `rt`=fuente, `rd`=destino, `aux`=0.

**Encoding SLLR $1, $2, $3 — 0x00C41003:**

```
bit 31..27 → opcode = 00000
bit 26..22 → rs     = 00011    ($3: de acá sale el shift amount, bits [4:0])
bit 21..17 → rt     = 00010    ($2: valor a shiftear)
bit 16..12 → rd     = 00001    ($1: destino)
bit 11..7  → aux    = 00000    (no se usa en shift variable)
bit 6..0   → funct  = 0000011  (SLLR = 0x03)

00000 00011 00010 00001 00000 0000011
= 0x00C41003
```

| Instr | funct | Hex             | r2         | r3 | Esperado r1    |
|-------|-------|-----------------|------------|----|-----------------|
| SLLR  | 0x03  | `0x00C41003`    | 3          | 4  | 48              |
| SRLR  | 0x04  | `0x00C41004`    | 0x80       | 4  | 8               |
| SRAR  | 0x05  | `0x00C41005`    | 0x80000000 | 4  | 0xF8000000      |

```bash
# SLLR
reset && set pc 0 && s r2, 3 && s r3, 4 && s [0x0], 0x00C41003 && n && r
# SRLR
reset && set pc 0 && s r2, 0x80 && s r3, 4 && s [0x0], 0x00C41004 && n && r
# SRAR
reset && set pc 0 && s r2, 0x80000000 && s r3, 4 && s [0x0], 0x00C41005 && n && r
```

---

### 4.12 MUL, MULH, MULHU (R-type)

**Qué hace:** multiplicación de 32×32 bits. Resultado completo son 64 bits.

- **MUL**: devuelve los 32 bits **bajos** del producto.
- **MULH**: devuelve los 32 bits **altos** (signed).
- **MULHU**: igual que MULH pero unsigned.

**Encoding MUL $1, $2, $3 — 0x00861015:**

```
00000 00010 00011 00001 00000 0010101
  ↑     ↑     ↑     ↑     ↑      ↑
 R-type $2    $3    $1    0    MUL=0x15
```

```bash
# MUL: 6 × 7 = 42
reset && set pc 0 && s r2, 6 && s r3, 7 && s [0x0], 0x00861015 && n && r

# MULH: 0x10000000 × 0x10 = 0x100000000 → upper 32 = 1
reset && set pc 0 && s r2, 0x10000000 && s r3, 0x10 && s [0x0], 0x00861016 && n && r

# MULHU (misma idea, unsigned)
reset && set pc 0 && s r2, 0x10000000 && s r3, 0x10 && s [0x0], 0x00861017 && n && r
```

---

### 4.13 DIV, DIVU, REST, RESTU (R-type)

**Qué hace:**

- **DIV**: `r1 = r2 / r3` (división entera signed)
- **DIVU**: igual, unsigned
- **REST**: `r1 = r2 % r3` (resto signed)
- **RESTU**: resto unsigned

**Encoding DIV $1, $2, $3 — 0x00861018:**

```
00000 00010 00011 00001 00000 0011000
                                 ↑
                              DIV=0x18
```

| Instr | funct | Hex             | r2  | r3 | Esperado r1 |
|-------|-------|-----------------|-----|----|-------------|
| DIV   | 0x18  | `0x00861018`    | 20  | 6  | 3           |
| DIVU  | 0x19  | `0x00861019`    | 20  | 6  | 3           |
| REST  | 0x1A  | `0x0086101A`    | 20  | 6  | 2           |
| RESTU | 0x1B  | `0x0086101B`    | 20  | 6  | 2           |

```bash
# DIV: 20/6 = 3
reset && set pc 0 && s r2, 20 && s r3, 6 && s [0x0], 0x00861018 && n && r
# REST: 20%6 = 2
reset && set pc 0 && s r2, 20 && s r3, 6 && s [0x0], 0x0086101A && n && r
# DIVU con -20 (0xFFFFFFEC) / 6 → número grande
reset && set pc 0 && s r2, -20 && s r3, 6 && s [0x0], 0x00861019 && n && r
```

---

### 4.14 LW — Load Word (I-type)

**Qué hace:** `$rt = M[$rs + sign_extend(imm)]`. Carga 4 bytes de memoria al registro.

**Encoding LW $1, $2, 0 — 0x40820000:**

```
bit 31..27 → opcode = 01000    (LW = 0x08)
bit 26..22 → rs     = 00010    ($2, dirección base)
bit 21..17 → rt     = 00001    ($1, destino)
bit 16..0  → imm    = 0_0000_0000_0000_0000  (offset 0)

01000 00010 00001 00000000000000000
= 0x40820000
```

```bash
# 1. Escribimos 0xDEADBEEF en dirección 0x1000
reset && set pc 0
s [0x1000], 0xDEADBEEF
# 2. Cargamos dirección base en r2
s r2, 0x1000
# 3. LW r1, r2, 0 → r1 = M[0x1000 + 0]
s [0x0], 0x40820000
n
r
x xw 0x1000 1
```

**Esperado:** `r1 = 0xDEADBEEF`

---

### 4.15 SW — Store Word (I-type)

**Qué hace:** `M[$rs + sign_extend(imm)] = $rt`. Guarda 4 bytes de registro a memoria.

**Encoding SW $1, $2, 0 — 0x48820000:**

```
bit 31..27 → opcode = 01001    (SW = 0x09)
bit 26..22 → rs     = 00010    ($2, dirección base)
bit 21..17 → rt     = 00001    ($1, valor a guardar)
bit 16..0  → imm    = 0

01001 00010 00001 00000000000000000
= 0x48820000
```

```bash
reset && set pc 0
s r1, 0xCAFEBABE
s r2, 0x1000
s [0x0], 0x48820000
n
x xw 0x1000 1
```

**Esperado:** `examine` muestra `CAFEBABE`

---

### 4.16 SH — Store Halfword (I-type)

**Qué hace:** `M[$rs + offset](15:0) = $rt(15:0)`. Guarda los 16 bits bajos.

**Encoding SH $1, $2, 0 — 0x50820000:**

```
opcode = 01010 (SH = 0x0A), rs=$2, rt=$1, imm=0
→ 0x50820000
```

```bash
reset && set pc 0
s r1, 0x1234ABCD
s r2, 0x1000
s [0x0], 0x50820000
n
x xw 0x1000 1
```

**Esperado:** en 0x1000 aparecen los 16 bits bajos de r1 (sujeto a endianness).

---

### 4.17 SB — Store Byte (I-type)

**Qué hace:** `M[$rs + offset](7:0) = $rt(7:0)`. Guarda 1 byte.

**Encoding SB $1, $2, 0 — 0x58820000:**

```
opcode = 01011 (SB = 0x0B), rs=$2, rt=$1, imm=0
→ 0x58820000
```

```bash
reset && set pc 0
s r1, 0x41
s r2, 0x1000
s [0x0], 0x58820000
n
x xb 0x1000 4
```

**Esperado:** primer byte en 0x1000 = `0x41` ('A')

---

### 4.18 LH, LHU — Load Halfword (I-type)

**Qué hace:** carga 16 bits de memoria. LH hace sign-extend a 32 bits, LHU hace zero-extend.

**Encoding LH $1, $2, 0 — 0x60820000:**

```
opcode = 01100 (LH = 0x0C), rs=$2, rt=$1, imm=0
→ 0x60820000
```

LHU: opcode = 01101 (0x0D) → `0x68820000`

```bash
# LH: 0x8000 → sign-extend → 0xFFFF8000
reset && set pc 0 && s [0x1000], 0x00008000 && s r2, 0x1000 && s [0x0], 0x60820000 && n && r

# LHU: 0x8000 → zero-extend → 0x00008000
reset && set pc 0 && s [0x1000], 0x00008000 && s r2, 0x1000 && s [0x0], 0x68820000 && n && r
```

---

### 4.19 LB, LBU — Load Byte (I-type)

**Qué hace:** carga 1 byte. LB sign-extend, LBU zero-extend.

**Encoding LB $1, $2, 0 — 0x70820000 (LBU → 0x78820000):**

```
LB:  opcode = 01110 (0x0E) → 0x70820000
LBU: opcode = 01111 (0x0F) → 0x78820000
```

```bash
# LB: 0x80 → sign-extend → 0xFFFFFF80
reset && set pc 0 && s [0x1000], 0x00000080 && s r2, 0x1000 && s [0x0], 0x70820000 && n && r

# LBU: 0x80 → zero-extend → 0x00000080
reset && set pc 0 && s [0x1000], 0x00000080 && s r2, 0x1000 && s [0x0], 0x78820000 && n && r
```

---

### 4.20 Indexed loads: LWX, LHX, LHUX, LBX, LBUX (R-type)

**Qué hace:** dirección = `R[$rs] + R[$rd]`. El destino es `rt` (OJO: no `rd` como en el resto de R-types).

**Encoding LWX $1, $2, $3 — 0x00823014:**

```
bit 31..27 → opcode = 00000
bit 26..22 → rs     = 00010    ($2: base)
bit 21..17 → rt     = 00001    ($1: destino ← OJO, acá el destino es rt, no rd)
bit 16..12 → rd     = 00011    ($3: offset)
bit 11..7  → aux    = 00000
bit 6..0   → funct  = 0010100  (LWX = 0x14)

00000 00010 00001 00011 00000 0010100
= 0x00823014
```

| Instr | funct | Hex             | Dirección      | Esperado r1    |
|-------|-------|-----------------|----------------|-----------------|
| LWX   | 0x14  | `0x00823014`    | M[0x1000+0x50] | 0xBEEFFACE      |
| LHX   | 0x10  | `0x00823010`    | M[0x1000+0x50] | 0xFFFF8000      |
| LHUX  | 0x11  | `0x00823011`    | M[0x1000+0x50] | 0x00008000      |
| LBX   | 0x12  | `0x00823012`    | M[0x1000+0x50] | 0xFFFFFF80      |
| LBUX  | 0x13  | `0x00823013`    | M[0x1000+0x50] | 0x00000080      |

```bash
# LWX r1, r2, r3 → r1 = M[r2 + r3]
reset && set pc 0 && s [0x1050], 0xBEEFFACE && s r2, 0x1000 && s r3, 0x50 && s [0x0], 0x00823014 && n && r

# LHX (halfword sign-extend)
reset && set pc 0 && s [0x1050], 0x00008000 && s r2, 0x1000 && s r3, 0x50 && s [0x0], 0x00823010 && n && r

# LHUX (halfword zero-extend)
reset && set pc 0 && s [0x1050], 0x00008000 && s r2, 0x1000 && s r3, 0x50 && s [0x0], 0x00823011 && n && r

# LBX (byte sign-extend)
reset && set pc 0 && s [0x1050], 0x00000080 && s r2, 0x1000 && s r3, 0x50 && s [0x0], 0x00823012 && n && r

# LBUX (byte zero-extend)
reset && set pc 0 && s [0x1050], 0x00000080 && s r2, 0x1000 && s r3, 0x50 && s [0x0], 0x00823013 && n && r
```

---

### 4.21 Branches: BEQ, BNE, BLT, BGT, BLE, BGE (I-type)

**Estrategia:** Ponemos el branch en 0x0 y un ADD r4,r5,r6 en 0x8 (target del salto cuando imm=1).

- Si el branch **se toma**: PC salta a 0x8, se ejecuta el ADD, r4 = r5+r6.
- Si el branch **NO se toma**: PC va a 0x4, el ADD no se ejecuta, r4 = 0.

**Encoding BEQ $1, $2, 1 — 0x80440001:**

```
bit 31..27 → opcode = 10000    (BEQ = 0x10)
bit 26..22 → rs     = 00001    ($1)
bit 21..17 → rt     = 00010    ($2)
bit 16..0  → imm    = 0_0000_0000_0000_0001  (1 word forward)

BranchAddr = {13{0}, 1, 00} = 4
PC_nuevo   = PC+4 + 4 = 0 + 4 + 4 = 8   ← salta a 0x8 si r1==r2

10000 00001 00010 00000000000000001
= 0x80440001
```

**Tabla de branches:**

| Instr | Condición (signed) | opcode | Hex en 0x0    | Caso A (tomado)  | Caso B (no tomado) |
|-------|---------------------|--------|---------------|------------------|--------------------|
| BEQ   | r1 == r2            | 0x10   | `0x80440001`  | r1=5, r2=5       | r1=5, r2=99        |
| BNE   | r1 != r2            | 0x11   | `0x88440001`  | r1=5, r2=99      | r1=5, r2=5         |
| BLT   | r1 < r2             | 0x12   | `0x90440001`  | r1=5, r2=10      | r1=10, r2=5        |
| BGT   | r1 > r2             | 0x13   | `0x98440001`  | r1=10, r2=5      | r1=5, r2=10        |
| BLE   | r1 <= r2            | 0x14   | `0xA0440001`  | r1=5, r2=5       | r1=10, r2=5        |
| BGE   | r1 >= r2            | 0x15   | `0xA8440001`  | r1=10, r2=5      | r1=5, r2=10        |

**ADD en 0x8 — 0x014C401C:**

```
00000 00101 00110 00100 00000 0011100
  ↑     ↑     ↑     ↑     ↑      ↑
 R-type $5    $6    $4    0    ADD=0x1C
= 0x014C401C
```

```bash
# --- BEQ test: r1==r2 → TOMADO ---
reset && set pc 0
s [0x8], 0x014C401C       # ADD r4,r5,r6 en target
s r1, 5
s r2, 5
s r5, 10
s r6, 20
s [0x0], 0x80440001        # BEQ r1,r2,1
n
r
# Esperado: PC=0x8, r4=30

# --- BEQ test: r1!=r2 → NO tomado ---
reset && set pc 0
s [0x8], 0x014C401C
s r1, 5
s r2, 99
s r5, 10
s r6, 20
s [0x0], 0x80440001
n
r
# Esperado: PC=0x4, r4=0

# --- BNE test: r1!=r2 → TOMADO ---
reset && set pc 0
s [0x8], 0x014C401C
s r1, 5 && s r2, 99
s r5, 1 && s r6, 2
s [0x0], 0x88440001
n && r
# Esperado: PC=0x8, r4=3

# --- BNE test: r1==r2 → NO tomado ---
reset && set pc 0
s [0x8], 0x014C401C
s r1, 5 && s r2, 5
s r5, 1 && s r6, 2
s [0x0], 0x88440001
n && r
# Esperado: PC=0x4, r4=0
```

Probá BLT, BGT, BLE, BGE con el mismo patrón, cambiando solo el hex en 0x0 y los valores de r1/r2 según la tabla.

---

### 4.22 J — Jump (J-type)

**Qué hace:** `PC = {PC+4[31:29], address, 2'b0}`. J 4 desde 0x0 → PC = 0x10.

**Encoding J 4 — 0x10000004:**

```
bit 31..27 → opcode  = 00010    (J = 0x02)
bit 26..0  → address = 0_0000_0000_0000_0000_0000_0100  (4 en 27 bits)

JumpAddr = {000, 4, 00} = 0x00000010

00010 00000000000000000000000000100
= 0x10000004
```

```bash
reset && set pc 0
s [0x0], 0x10000004
n
r
```

**Esperado:** `PC = 0x00000010`

---

### 4.23 JAL — Jump and Link (J-type)

**Qué hace:** `$31 = PC+4; PC = JumpAddr`. Guarda la dirección de retorno en $31.

**Encoding JAL 4 — 0x18000004:**

```
bit 31..27 → opcode = 00011    (JAL = 0x03)
bit 26..0  → address = 4

00011 00000000000000000000000000100
= 0x18000004
```

```bash
reset && set pc 0
s [0x0], 0x18000004
n
r
```

**Esperado:** `PC = 0x00000010`, `r31 = 0x00000004` (PC+4 de donde estaba JAL)

---

### 4.24 JR — Jump Register (R-type)

**Qué hace:** `PC = R[$rs]`. Salta a la dirección contenida en un registro.

**Encoding JR $31 — 0x07C0000E:**

```
bit 31..27 → opcode = 00000
bit 26..22 → rs     = 11111    ($31, dirección destino)
bit 21..17 → rt     = 00000    (no usado)
bit 16..12 → rd     = 00000    (no usado)
bit 11..7  → aux    = 00000
bit 6..0   → funct  = 0001110  (JR = 0x0E)

00000 11111 00000 00000 00000 0001110
= 0x07C0000E
```

```bash
reset && set pc 0
s r31, 0x100               # dirección a la que queremos saltar
s [0x0], 0x07C0000E
n
r
```

**Esperado:** `PC = 0x00000100`

---

### 4.25 JALR — Jump and Link Register (R-type)

**Qué hace:** `$31 = PC+4; PC = R[$rs]`. Como JR pero guarda retorno.

**Encoding JALR $4 — 0x0100000F:**

```
bit 31..27 → opcode = 00000
bit 26..22 → rs     = 00100    ($4, dirección destino)
bit 21..17 → rt     = 00000
bit 16..12 → rd     = 00000
bit 11..7  → aux    = 00000
bit 6..0   → funct  = 0001111  (JALR = 0x0F)

00000 00100 00000 00000 00000 0001111
= 0x0100000F
```

```bash
reset && set pc 0
s r4, 0x100               # dirección destino
s [0x0], 0x0100000F
n
r
```

**Esperado:** `PC = 0x00000100`, `r31 = 0x00000004`

---

### 4.26 CFS, CTS, TRAP, RFT

**CFS y CTS:** marcados como "no implementados" en la documentación. Saltealos.

**TRAP:** `EPC = PC+4; PC = M[aux << 2]`. Necesitás tener la trap table en memoria.

**RFT:** `PC = EPC`. Retorno de trap.

Probá TRAP/RFT solo si te sobra tiempo y con ayuda del profe.

---

## 5. Template para tu documentación

Copiá esto y completá por cada caso en tu `.md` personal:

```md
# Caso N: [nombre de la instrucción]

## Descripción
[Qué hace la instrucción, qué estoy testeando]

## Instrucciones
- ADD r1, r2, r3
- ...

## Precondiciones
- set pc 0            ; para ejecutar desde 0x0
- s r2, 5             ; primer operando
- s r3, 7             ; segundo operando
- s [0x0], 0x0086101C ; encoding de ADD r1,r2,r3

## Code
bit 31..27 → opcode = 00000 (R-type)
bit 26..22 → rs     = 00010 ($2)
bit 21..17 → rt     = 00011 ($3)
bit 16..12 → rd     = 00001 ($1, destino)
bit 11..7  → aux    = 00000
bit 6..0   → funct  = 0011100 (ADD = 0x1C)
────────────────────────────────
Hex: 0x0086101C

## Postcondiciones
- r → r1 = 0x0000000C (12 = 5+7) ✓
- r2 = 5, r3 = 7 (sin cambios)
- PC = 0x00000004

## Conclusiones
[Anduvo / No anduvo]. [Por qué].
```

---

## 6. Orden recomendado

**Primer día (~30% = ~16 instrucciones):**

1. ADDI, ADD, SUB
2. AND, OR, XOR, NOR
3. ANDI, ORI, XORI
4. SLT, SLTU, SLTI, SLTIU
5. SLL, SRL, SRA
6. LW, SW

**Segundo día:**

7. SLLR, SRLR, SRAR
8. LUI, ANDIH, ORIH, XORIH
9. J, JR, JAL, JALR
10. BEQ, BNE, BLT, BGT, BLE, BGE
11. SB, SH, LB, LBU, LH, LHU
12. LWX, LHX, LHUX, LBX, LBUX
13. MUL, MULH, MULHU, DIV, DIVU, REST, RESTU
