# mostrar_h — ADDI y SB para imprimir 'h' por UART

## Las dos instrucciones que usamos

### ADDI — Add Immediate

```
ADDI rt, rs, imm
R[rt] = R[rs] + SignExtImm
```

Suma un inmediato con signo a `rs` y guarda en `rt`.

`SignExtImm` extiende el bit 16 del inmediato (17 bits) a 32 bits:

| imm (17b) | bit 16 | SignExtImm (32b) | Ejemplo |
|-----------|--------|-------------------|---------|
| 42 | 0 | `0x0000002A` | positivo, sin cambio |
| −256 | 1 | `0xFFFFFF00` | negativo, replica 1s arriba |

**Truco:** `ADDI r1, r0, -256` mete `0xFFFFFF00` en r1 sin necesidad de LUI+ORI.

### SB — Store Byte

```
SB base, dato, offset
M[ R[base] + SignExtImm ](7:0) = R[dato](7:0)
```

Escribe el byte bajo de `dato` en la dirección `R[base] + offset`.

Para la UART (0xFFFFFF00):

```
SB r1, r2, 0    →   M[0xFFFFFF00 + 0] = byte bajo de r2
```

El emulador tiene la UART mapeada en `0xFFFFFF00`. Escribir un byte ahí = mostrarlo en el xterm.

---

## El programa (mostrar_h.asm)

```asm
ADDI r1, r0, -256     ; r1 = 0xFFFFFF00  (dirección UART)
ADDI r2, r0, 'h'      ; r2 = 0x68        (carácter 'h')
SB    r1, r2, 0        ; M[r1+0] = r2(7:0) → 'h' en pantalla
J 0                    ; loop infinito
```

Paso a paso en el debugger:

```
load mostrar_h.bin     # carga en 0x00000000
step                   # ADDI → r1 = 0xFFFFFF00  (registers para ver)
step                   # ADDI → r2 = 0x68
step                   # SB   → 'h' aparece en el xterm de la UART
```

> `r0` siempre vale `0`. Es el "zero register" (como en MIPS).

---

## Ver el binario en hex

En vez de abrir el `.bin` con nvim (se ve basura), usá:

```bash
# Formato más legible: offset + bytes + ASCII
hexdump -C mostrar_h.bin

# O con od
od -A x -t x1z mostrar_h.bin
```

El header (60 bytes):

```
00000000  4d 44 42 47  → magic "MDBG"
00000004  02 00 00 00  → version 2
00000008  00 00 00 00  → base addr 0
0000000c  10 00 00 00  → payload size 16 bytes
00000010              → padding (12 bytes de ceros)
0000001c  52 54 4d 33  → "RTM32" (mode string)
...
```

El payload (instrucciones, desde byte 60 = 0x3C):

```
0000003c  00 ff 03 c0  → ADDI r1, r0, -256    (word 0xC003FF00)
00000040  68 00 04 c0  → ADDI r2, r0, 0x68    (word 0xC0040068)
00000044  00 00 44 58  → SB   r1, r2, 0       (word 0x58440000)
00000048  00 00 00 10  → J    0               (word 0x10000000)
```

### Cómo leer una instrucción de sus bytes

Tomá los 4 bytes `00 ff 03 c0`. El CPU los lee como la palabra `0xC003FF00` (little-endian):

```
0xC003FF00 en binario:
1100 0000 0000 0011 1111 1111 0000 0000

[31:27] 11000  → opcode = ADDI
[26:22] 00000  → rs = r0
[21:17] 00001  → rt = r1
[16:0]  1 1111 1111 0000 0000 → imm bit 16=1, negativo: -(2^17 - 0x1FF00) = -256
```

---

## Script para codificar a mano

```python
import struct

def i(opcode, rs, rt, imm):
    """I-type a 4 bytes LE"""
    w = (opcode << 27) | (rs << 22) | (rt << 17) | (imm & 0x1FFFF)
    return struct.pack('<I', w)

# ADDI r1, r0, -256
i(0x18, 0, 1, 0x1FF00).hex(' ')   # → '00 ff 03 c0'

# ADDI r2, r0, 'h'
i(0x18, 0, 2, 0x68).hex(' ')      # → '68 00 04 c0'

# SB r1, r2, 0
i(0x0B, 1, 2, 0).hex(' ')         # → '00 00 44 58'
```
