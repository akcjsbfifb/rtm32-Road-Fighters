# RTM32 — Emulador de procesador didáctico

## Requisitos

```bash
sudo pacman -S xterm telnet picocom
```

## Arranque rápido 

| Terminal | Comando | Qué hace |
|----------|---------|----------|
| 1 | `./rtm32 -d telnet` | Emulador + xterm de UART |
| 2 | `telnet localhost 4444` | Debugger (step, registers, load...) |
| 3 | Tu editor | Escribir .asm, ensamblar |

## Utilidades

```bash
pkill xterm   # cerrar terminales abiertas por el emulador
```

# Testing de instrucciones RTM32

Por Martin Moloeznik y Nicolas Paz Reyes

---

## Caso 1:

### Descripción
Testeando ADD
### Instrucciones
- ADD r1, r2, r3
### Precondiciones
set pc 0
s r2 5
s r3 7

### Code
s [0x0] 0x0086101C 
00000 opcode 
00010 $2
00011 $3
00001 $1
000000 aux
funct 011100  (add)
    ,       ,        ,        ,       ,        ,        ,    
00000 00010 00011 00001 00000 0011100
0        0       8         6      1       0       1      C 
### Postcondiciones
R 1: 0x0000000C   R 2: 0x00000005   R 3: 0x00000007
5 + 7 = 12 = 0xC
### Conclusiones
ADD funciona correctamente, suma $2 + $3 y guarda en $1.


---

## Caso 2: ADDi

### Descripción

### Instrucciones
- ADDi r1, r2, 5
### Precondiciones
- set pc 0
- set r2, 5

### Code
s [0x0] 0x08820005

00001 opcode
00010 $2
00001 $1
0,0000,0000,0000,0101 (imm 5 en 17 bits.)

0000,1000,1000,0010,0000,0000,0000,0101
   0       8        8        2      0        0       0       5
### Postcondiciones
- R[ 1]: 0x0000000A   R[ 2]: 0x00000005

### Conclusiones
En nueva version funciona con opcode 00001.


---

## Caso 3: 
### Descripción
SUB

### Instrucciones
- SUB r1, r2, r3

### Precondiciones
- set pc 0
- set r2 10
- set r3 3

### Code
 s [0x0] 0x0086101D

00000 opcode
00010 r2
00011 r3
00001 r1
000000 aux
0011101 sub (0x1D)
0000, 0000, 1000, 0110, 0001, 0000, 0001,1101
   0         0        8        6       1        0         1       D
### Postcondiciones
R 1: 0x00000007   R  2: 0x0000000A   R 3 : 0x00000003
### Conclusiones
SUB resto correctamente R2 - R3 y lo guardo en R1. 

--- 
## Caso 3.1: 
### Descripción
SUB a valores negativos
### Instrucciones
- SUB r1, r2, r3

### Precondiciones
- set pc 0
- set r2 10
- set r3 14

### Code
 s [0x0] 0x0086101D
### Postcondiciones
R 1: 0xFFFFFFFC   R 2: 0x0000000A   R 3: 0x0000000E
10 - 14 = -4
00000100 = 4
11111011
11111100 = -4 = 0xFC
### Conclusiones
SUB resto correctamente R2 - R3 y lo guardo en R1 como negativo en complemento a 2

---

## Caso 4: AND

### Descripción
AND bit a bit entre registros

### Instrucciones
- AND r1, r2, r3

### Precondiciones
- set pc 0
- s r2 0xff
- s r3 0x0f

### Code
s [0x0] 0x00861008

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0001000 and (0x08)

0000, 0000, 1000, 0110, 0001, 0000, 0000, 1000
   0       0         8        6        1        0       0        8

### Postcondiciones
R 1: 0x0000000F   R 2: 0x000000FF   R 3: 0x0000000F
0xFF & 0x0F = 0x0F
  11111111 & 00001111 = 00001111 = 0x0F

### Conclusiones
AND funciona correctamente, $1 = $2 & $3.



---

## Caso 5: OR

### Descripción
OR bit a bit entre registros

### Instrucciones
- OR r1, r2, r3

### Precondiciones
- set pc 0
- s r2 0xF0
- s r3 0x0F

### Code
s [0x0] 0x00861009

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0001001 or (0x09)

0000, 0000, 1000, 0110, 0001, 0000, 0000, 1001
   0         0        8       6        1        0        0       9

### Postcondiciones
R 1: 0x000000FF   R 2: 0x000000F0   R 3: 0x0000000F
0xF0 | 0x0F = 0xFF
  11110000 | 00001111 = 11111111 = 0xFF

### Conclusiones
OR funciona correctamente, $1 = $2 | $3.



---

## Caso 6: XOR

### Descripción
XOR bit a bit entre registros

### Instrucciones
- XOR r1, r2, r3

### Precondiciones
- set pc 0
- s r2 0xFF
- s r3 0x0F

### Code
s [0x0] 0x0086100A

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0001010 xor (0x0A)

0000, 0000, 1000, 0110, 0001, 0000, 0000, 1010
   0        0        8        6        1        0       0         A

### Postcondiciones
R 1: 0x000000F0   R 2: 0x000000FF   R 3: 0x0000000F
0xFF ^ 0x0F = 0xF0
  11111111 `xor` 00001111 =  11110000 = 0xF0

### Conclusiones
XOR funciona correctamente, $1 = $2 ^ $3.

---

## Caso 7: NOR

### Descripción
NOR bit a bit entre registros (~(r2 | r3))

### Instrucciones
- NOR r1, r2, r3

### Precondiciones
- set pc 0
- s r2 0xF0
- s r3 0x00

### Code
s [0x0] 0x0086100B

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0001011 nor (0x0B)

0000, 0000, 1000, 0110, 0001, 0000, 0000, 1011
   0        0        8        6        1        0        0       B

### Postcondiciones
R 1: 0xFFFFFF0F   R 2: 0x000000F0   R 3: 0x00000000
~(0xF0 | 0x00) = ~0xF0 = 0xFFFFFF0F
  000000F0 | 00000000 = 000000F0 → ~ = FFFFFFF0F

### Conclusiones
NOR funciona correctamente. El resultado muestra todos los bits altos en 1 por la negación.



---

## Caso 8: ANDI

### Descripción
AND inmediato

### Instrucciones
- ANDI r1, r2, 0xF

### Precondiciones
- set pc 0
- s r2 0xFF

### Code
s [0x0] 0x2082000F

00100 opcode (ANDI)
00010 $2
00001 $1
0,0000,0000,0000,1111 (imm 0xF en 17 bits, imm[16]=0 → normal)

0010, 0000, 1000, 0010, 0000, 0000, 0000, 1111
   2        0         8         2       0        0        0       F

### Postcondiciones
R 1: 0x0000000F   R 2: 0x000000FF
0xFF & 0xF = 0x0F

### Conclusiones
ANDI funciona. El inmediato se extiende con ceros (zero-extend), no con signo.




---
## Caso 9: ORI

### Descripción
OR inmediato 

### Instrucciones
- ORI r1, r2, 8

### Precondiciones
set pc 0
s r2 0xF0

### Code
s [0x0] 0x28820008

00101 opcode (ORI)
00010 $2
00001 $1
0,0000,0000,0000,1000 (imm 8 en 17 bits)

0010, 1000, 1000, 0010, 0000, 0000, 0000, 1000
   2        8       8        2        0       0        0        8

### Postcondiciones
R 1: 0x000000F8   R 2: 0x000000F0
0xF0 | 0x0008 = 0xF8
  
  11110000 | 00001000 = 11111000

### Conclusiones
0xF0 | 8 = 0xF8. ORI usa zero-extend del inmediato.

hasta aca probado por marto en terminal

---

## Caso 10: XORI

### Descripción
XOR inmediato. 
XORI=00110.

### Instrucciones
- XORI r1, r2, 0xF

### Precondiciones
set pc 0
s r2 0xFF

### Code
s [0x0] 0x3082000F

00110 opcode (XORI asumido = 0x06)
00010 $2
00001 $1
0,0000,0000,0000,1111 (imm 0xF)

0011, 0000, 1000, 0010, 0000, 0000, 0000, 1111
   3       0        8        2        0        0        0        F

### Postcondiciones
R 1: 0x000000F0   R 2: 0x000000FF
0xFF ^ 0xF = 0xF0

### Conclusiones
funciona correctamente con la v2 del manual.


---

## Caso 11: SLT

### Descripción
Set Less Than (signed). r1 = (r2 < r3) ? 1 : 0

### Instrucciones
- SLT r1, r2, r3

### Precondiciones
set pc 0
s r2 5
s r3 10

### Code
s [0x0] 0x0086100C

00000 opcode (R-type)
00010 $2
00011 $3
00001 $1
00000 aux
0001100 funct (SLT = 0x0C)

0000, 0000, 1000, 0110, 0001, 0000, 0000, 1100
   0        0        8       6        1        0       0         C

### Postcondiciones
R 1: 0x00000001   R 2: 0x00000005   R 3: 0x0000000A
5 < 10 → true → 1

### Conclusiones
SLT compara signed. 5 < 10 → r1 = 1.


---

## Caso 12: SLTU

### Descripción
Set Less Than Unsigned. 0xFFFFFFFF NO es < 1 sin signo.

### Instrucciones
- SLTU r1, r2, r3

### Precondiciones
set pc 0
s r2 -1
s r3 1

### Code
s [0x0] 0x0086100D

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0001101 funct (SLTU = 0x0D)

0000, 0000, 1000, 0110, 0001, 0000, 0000, 1101
   0        0        8       6        1        0       0         D

### Postcondiciones
R 1: 0x00000000   R 2: 0xFFFFFFFF   R 3: 0x00000001
Unsigned: 0xFFFFFFFF > 1 → false → 0

### Conclusiones
SLTU sin signo: 0xFFFFFFFF no es < 1 → r1 = 0.


---

## Caso 12b: SLTU (caso contrario)

### Descripción
Set Less Than Unsigned — caso donde SÍ da true. 1 < 5 sin signo.

### Instrucciones
- SLTU r1, r2, r3

### Precondiciones
set pc 0
s r2 1
s r3 5

### Code
s [0x0] 0x0086100D

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0001101 funct (SLTU = 0x0D)

0000, 0000, 1000, 0110, 0001, 0000, 0000, 1101
   0        0        8       6        1        0       0         D

### Postcondiciones
R 1: 0x00000001   R 2: 0x00000001   R 3: 0x00000005
Unsigned: 1 < 5 → true → 1

### Conclusiones
SLTU sin signo: 1 < 5 → r1 = 1, confirma que SLTU funciona para el caso true.


---

## Caso 13: SLTI

### Descripción
Set Less Than Immediate (signed). Inmediato se sign-extiende.

### Instrucciones
- SLTI r1, r2, 10

### Precondiciones
set pc 0
s r2 5

### Code
s [0x0] 0xB082000A

10110 opcode (SLTI = 0x16)
00010 $2
00001 $1
0,0000,0000,0000,1010 (imm 10)

1011, 0000, 1000, 0010, 0000, 0000, 0000, 1010
   B        0        8        2        0        0       0         A

### Postcondiciones
R 1: 0x00000001   R 2: 0x00000005
5 < 10 → true → 1

### Conclusiones
SLTI: 5 < 10 signado → r1 = 1.


---

## Caso 13b: SLTI (caso contrario)

### Descripción
Set Less Than Immediate — caso donde SÍ da false. 15 < 10 signado → false.

### Instrucciones
- SLTI r1, r2, 10

### Precondiciones
set pc 0
s r2 15

### Code
s [0x0] 0xB082000A

10110 opcode (SLTI = 0x16)
00010 $2
00001 $1
0,0000,0000,0000,1010 (imm 10)

1011, 0000, 1000, 0010, 0000, 0000, 0000, 1010
   B        0        8        2        0        0       0         A

### Postcondiciones
R 1: 0x00000000   R 2: 0x0000000F
15 < 10 signed → false → 0

### Conclusiones
SLTI: 15 no es < 10 signado → r1 = 0. Confirma que SLTI funciona para el caso false.


---

## Caso 14: SLTIU

### Descripción
Set Less Than Immediate Unsigned

### Instrucciones
- SLTIU r1, r2, 1

### Precondiciones
set pc 0
s r2 -1

### Code
s [0x0] 0xB8820001

10111 opcode (SLTIU = 0x17)
00010 $2
00001 $1
0,0000,0000,0000,0001 (imm 1)

1011, 1000, 1000, 0010, 0000, 0000, 0000, 0001
   B        8        8        2        0       0        0        1

### Postcondiciones
R 1: 0x00000000   R 2: 0xFFFFFFFF
Unsigned: 0xFFFFFFFF < 1 → false → 0

### Conclusiones
SLTIU: 0xFFFFFFFF no es < 1 sin signo. Inmediato zero-extend.


---

## Caso 14b: SLTIU (caso contrario)

### Descripción
Set Less Than Immediate Unsigned — caso donde SÍ da true. 3 < 10 sin signo.

### Instrucciones
- SLTIU r1, r2, 10

### Precondiciones
set pc 0
s r2 3

### Code
s [0x0] 0xB882000A

10111 opcode (SLTIU = 0x17)
00010 $2
00001 $1
0,0000,0000,0000,1010 (imm 10)

1011, 1000, 1000, 0010, 0000, 0000, 0000, 1010
   B        8        8        2        0       0        0        A

### Postcondiciones
R 1: 0x00000001   R 2: 0x00000003
Unsigned: 3 < 10 → true → 1

### Conclusiones
SLTIU: 3 < 10 sin signo → r1 = 1. Confirma que SLTIU funciona para el caso true.


---

## Caso 15: SLL

### Descripción
Shift Left Logical inmediato. aux = shift amount.

### Instrucciones
- SLL r1, r2, 4

### Precondiciones
set pc 0
s r2 3

### Code
s [0x0] 0x00041200

00000 opcode (R-type)
00000 rs (no usado)
00010 $2 (rt: fuente)
00001 $1 (rd: destino)
00100 aux (4: shift amount)
0000000 funct (SLL = 0x00)

0000, 0000, 0000, 0100, 0001, 0010, 0000, 0000
   0        0        0        4        1        2       0        0

### Postcondiciones
R 1: 0x00000030   R 2: 0x00000003
3 << 4 = 48 = 0x30

### Conclusiones
SLL: 3 << 4 = 48 correcto.


---

## Caso 15b: SLL (variante con otro valor)

### Descripción
Shift Left Logical — mismo shift de 4, distinto operando. 7 << 4.

### Instrucciones
- SLL r1, r2, 4

### Precondiciones
set pc 0
s r2 7

### Code
s [0x0] 0x00041200

00000 opcode (R-type)
00000 rs (no usado)
00010 $2 (rt: fuente)
00001 $1 (rd: destino)
00100 aux (4: shift amount)
0000000 funct (SLL = 0x00)

0000, 0000, 0000, 0100, 0001, 0010, 0000, 0000
   0        0        0        4        1        2       0        0

### Postcondiciones
R 1: 0x00000070   R 2: 0x00000007
7 << 4 = 112 = 0x70

### Conclusiones
SLL: 7 << 4 = 112 correcto. Confirma SLL con otro operando.


---

## Caso 16: SRL

### Descripción
Shift Right Logical inmediato

### Instrucciones
- SRL r1, r2, 4

### Precondiciones
set pc 0
s r2 0x80

### Code
s [0x0] 0x00041201

00000 opcode
00000 rs
00010 $2 (rt)
00001 $1 (rd)
00100 aux (4)
0000001 funct (SRL = 0x01)

0000, 0000, 0000, 0100, 0001, 0010, 0000, 0001
   0        0        0        4        1        2       0        1

### Postcondiciones
R 1: 0x00000008   R 2: 0x00000080
0x80 >> 4 = 8

### Conclusiones
SRL: 0x80 >> 4 = 8 correcto.


---

## Caso 16b: SRL (variante con otro valor)

### Descripción
Shift Right Logical — mismo shift de 4, distinto operando. 0xFF >> 4.

### Instrucciones
- SRL r1, r2, 4

### Precondiciones
set pc 0
s r2 0xFF

### Code
s [0x0] 0x00041201

00000 opcode
00000 rs
00010 $2 (rt)
00001 $1 (rd)
00100 aux (4)
0000001 funct (SRL = 0x01)

0000, 0000, 0000, 0100, 0001, 0010, 0000, 0001
   0        0        0        4        1        2       0        1

### Postcondiciones
R 1: 0x0000000F   R 2: 0x000000FF
0xFF >> 4 = 15 = 0x0F

### Conclusiones
SRL: 0xFF >> 4 = 15 correcto. Confirma SRL con otro operando.


---

## Caso 17: SRA

### Descripción
Shift Right Arithmetic. Preserva signo.

### Instrucciones
- SRA r1, r2, 4

### Precondiciones
set pc 0
s r2 0x80000000

### Code
s [0x0] 0x00041202

00000 opcode
00000 rs
00010 $2 (rt)
00001 $1 (rd)
00100 aux (4)
0000010 funct (SRA = 0x02)

0000, 0000, 0000, 0100, 0001, 0010, 0000, 0010
   0        0        0        4        1        2       0        2

### Postcondiciones
R 1: 0xF8000000   R 2: 0x80000000
0x80000000 >>> 4 = 0xF8000000

### Conclusiones
SRA con signo: 0x80000000 >> 4 = 0xF8000000 (bits altos en 1).


---

## Caso 17b: SRA (variante con valor positivo)

### Descripción
Shift Right Arithmetic con número positivo — rellena con 0s porque bit 31=0.

### Instrucciones
- SRA r1, r2, 4

### Precondiciones
set pc 0
s r2 0x40000000

### Code
s [0x0] 0x00041202

00000 opcode
00000 rs
00010 $2 (rt)
00001 $1 (rd)
00100 aux (4)
0000010 funct (SRA = 0x02)

0000, 0000, 0000, 0100, 0001, 0010, 0000, 0010
   0        0        0        4        1        2       0        2

### Postcondiciones
R 1: 0x04000000   R 2: 0x40000000
0x40000000 (positivo) >>> 4 = 0x04000000 (bits altos en 0)

### Conclusiones
SRA con valor positivo: rellena con 0s correctamente. Contraste con 0x80000000 que rellena con 1s.


---

## Caso 18: SLLR

### Descripción
Shift Left Logical Register. Shift amount de R[rs][4:0].

### Instrucciones
- SLLR r1, r2, r3
(rs=$3 contiene shift amount, rt=$2 fuente, rd=$1 destino)

### Precondiciones
set pc 0
s r3 4
s r2 3

### Code
s [0x0] 0x00C41003

00000 opcode
00011 $3 (rs: shift amount)
00010 $2 (rt: fuente)
00001 $1 (rd: destino)
00000 aux
0000011 funct (SLLR = 0x03)

0000, 0000, 1100, 0100, 0001, 0000, 0000, 0011
   0        0        C        4        1        0       0        3

### Postcondiciones
R 1: 0x00000030   R 2: 0x00000003   R 3: 0x00000004
3 << 4 = 48

### Conclusiones
SLLR: shift amount desde $3, correcto.


---

## Caso 18b: SLLR (variante con otro shift)

### Descripción
Shift Left Logical Register — 5 << 2 = 20, shift amount desde $3.

### Instrucciones
- SLLR r1, r2, r3

### Precondiciones
set pc 0
s r2 5
s r3 2

### Code
s [0x0] 0x00C41003

00000 opcode
00011 $3 (rs: shift amount)
00010 $2 (rt: fuente)
00001 $1 (rd: destino)
00000 aux
0000011 funct (SLLR = 0x03)

0000, 0000, 1100, 0100, 0001, 0000, 0000, 0011
   0        0        C        4        1        0       0        3

### Postcondiciones
R 1: 0x00000014   R 2: 0x00000005   R 3: 0x00000002
5 << 2 = 20 = 0x14

### Conclusiones
SLLR: 5 << 2 = 20 correcto. Confirma SLLR con otro shift amount.


---

## Caso 19: SRLR

### Descripción
Shift Right Logical Register

### Instrucciones
- SRLR r1, r2, r3

### Precondiciones
set pc 0
s r3 4
s r2 0x80

### Code
s [0x0] 0x00C41004

00000 opcode
00011 $3 (rs)
00010 $2 (rt)
00001 $1 (rd)
00000 aux
0000100 funct (SRLR = 0x04)

0000, 0000, 1100, 0100, 0001, 0000, 0000, 0100
   0        0        C        4        1        0       0        4
3
### Postcondiciones
R 1: 0x00000008   R 2: 0x00000080   R 3: 0x00000004
0x80 >> 4 = 8

### Conclusiones
SRLR correcto.


---

## Caso 19b: SRLR (variante con otro valor)

### Descripción
Shift Right Logical Register — 0xFF >> 4 = 15, shift amount desde $3.

### Instrucciones
- SRLR r1, r2, r3

### Precondiciones
set pc 0
s r2 0xFF
s r3 4

### Code
s [0x0] 0x00C41004

00000 opcode
00011 $3 (rs)
00010 $2 (rt)
00001 $1 (rd)
00000 aux
0000100 funct (SRLR = 0x04)

0000, 0000, 1100, 0100, 0001, 0000, 0000, 0100
   0        0        C        4        1        0       0        4

### Postcondiciones
R 1: 0x0000000F   R 2: 0x000000FF   R 3: 0x00000004
0xFF >> 4 = 15

### Conclusiones
SRLR: 0xFF >> 4 = 15 correcto. Confirma SRLR con otro operando.


---

## Caso 20: SRAR

### Descripción
Shift Right Arithmetic Register

### Instrucciones
- SRAR r1, r2, r3

### Precondiciones
set pc 0
s r2 0x80000000
s r3 4

### Code
s [0x0] 0x00C41005

00000 opcode
00011 $3 (rs)
00010 $2 (rt)
00001 $1 (rd)
00000 aux
0000101 funct (SRAR = 0x05)

0000, 0000, 1100, 0100, 0001, 0000, 0000, 0101
   0        0        C        4        1        0       0        5


### Postcondiciones
R 1: 0xF8000000   R 2: 0x80000000   R 3: 0x00000004
0x80000000 >>> 4 = 0xF8000000

### Conclusiones
SRAR preserva signo correctamente.


---

## Caso 20b: SRAR (variante con valor positivo)

### Descripción
Shift Right Arithmetic Register con número positivo — rellena con 0s porque bit 31=0.

### Instrucciones
- SRAR r1, r2, r3

### Precondiciones
set pc 0
s r2 0x40000000
s r3 4

### Code
s [0x0] 0x00C41005

00000 opcode
00011 $3 (rs)
00010 $2 (rt)
00001 $1 (rd)
00000 aux
0000101 funct (SRAR = 0x05)

0000, 0000, 1100, 0100, 0001, 0000, 0000, 0101
   0        0        C        4        1        0       0        5

### Postcondiciones
R 1: 0x04000000   R 2: 0x40000000   R 3: 0x00000004
0x40000000 (positivo) >>> 4 = 0x04000000 (bits altos en 0)

### Conclusiones
SRAR con valor positivo: rellena con 0s correctamente. Contraste con 0x80000000 que rellena con 1s.

Hasta Aca nico martes a la noche

---

## Caso 21: LW

### Descripción
Load Word: R[rt] = M[R[rs] + SignExtImm]

### Instrucciones
- LW r1, r2, 0

### Precondiciones
set pc 0
s [0x50] 0xDDDDDDDD
s r2 0x50

### Code
s [0x0] 0x40820000

01000 opcode (LW = 0x08)
00010 $2 (base)
00001 $1 (destino)
0,0000,0000,0000,0000 (offset 0)

0100, 0000, 1000, 0010, 0000, 0000, 0000, 0000
   4        0        8        2        0        0       0        0

### Postcondiciones
R 1: 0xDDDDDDDD   R 2: 0x00000050
M[0x50 + 0] = 0xDDDDDDDD

### Conclusiones
LW carga 4 bytes de memoria correctamente.


---

## Caso 22: SW

### Descripción
Store Word: M[R[rs] + SignExtImm] = R[rt]

### Instrucciones
- SW r1, r2, 0

### Precondiciones
set pc 0
s r1 0xCAFEBABE
s r2 0x50

### Code
s [0x0] 0x48820000

01001 opcode (SW = 0x09)
00010 $2 (base)
00001 $1 (dato a guardar)
0,0000,0000,0000,0000 (offset 0)

0100, 1000, 1000, 0010, 0000, 0000, 0000, 0000
   4        8        8        2        0       0        0        0

### Postcondiciones
x xw 0x50  → muestra 0xCCCCCCCC

### Conclusiones
SW guarda 4 bytes en M[0x50]. Verificar con: x xw 0x50


---

## Caso 23: J

### Descripción
Jump: PC = {PC+4[31:29], address, 2'b0}

### Instrucciones
- J 4

### Precondiciones
set pc 0

### Code
s [0x0] 0x10000004

00010 opcode (J = 0x02)
000,0000,0000,0000,0000,0000,0000,0100 (address 4, 27 bits)

JumpAddr = {000, 4, 00} = 0x00000010

0001, 0000, 0000, 0000, 0000, 0000, 0000, 0100
   1        0        0        0        0        0       0        4

### Postcondiciones
PC = 0x00000010

### Conclusiones
J 4 desde 0x0 → PC = 0x10.


---

## Caso 24: JR

### Descripción
Jump Register: PC = R[rs]
se utilizaria para "volver de una subrutina" entonces vuelvo a la direccion que dejo jal o jalr en el registro 31 que es la $ra Dirección de retorno 

### Instrucciones
- JR r31

### Precondiciones
set pc 0
s r31 0x100

### Code
s [0x0] 0x07C0000E

00000 opcode (R-type)
11111 rs ($31)
00000 rt
00000 rd
00000 aux
0001110 funct (JR = 0x0E)

0000, 0111, 1100, 0000, 0000, 0000, 0000, 1110
   0        7        C        0        0        0       0        E

### Postcondiciones
PC = 0x00000100

### Conclusiones
JR: PC = R[31] = 0x100.


---

## Caso 25: JAL

### Descripción
Jump And Link: R[31] = PC+4; PC = JumpAddr

### Instrucciones
- JAL 4

### Precondiciones
set pc 0

### Code
s [0x0] 0x18000004

00011 opcode (JAL = 0x03)
000,0000,0000,0000,0000,0000,0010,0000 (address 4)

0001, 1000, 0000, 0000, 0000, 0000, 0010, 0000
   1        8        0        0        0        0       2        0

### Postcondiciones
PC = 0x00000080   R 31: 0x00000004

### Conclusiones
JAL: salta a 0x80 y guarda retorno (0x04) en $31.


---

## Caso 26: JALR

### Descripción
Jump And Link Register: R[rd] = PC+4; PC = R[rs]. El link va a rd.

### Instrucciones
- JALR r4, r31

### Precondiciones
set pc 0
s r4 0x100

### Code
s [0x0] 0x0101F00F

00000 opcode (R-type)
00100 rs ($4, destino del salto)
00000 rt (no usado)
11111 rd ($31, donde guarda retorno)
00000 aux
0001111 funct (JALR = 0x0F)

0000, 0001, 0000, 0001, 1111, 0000, 0000, 1111
   0        1        0        1        F        0        0        F

### Postcondiciones
PC = 0x00000100   R 31: 0x00000004

### Conclusiones
JALR: PC = R[4] = 0x100, R[31] = PC+4 = 0x04. El link se escribe en rd.


---

## Caso 27: LUI

### Descripción
Pone un número de 16 bits en la mitad de arriba de un registro y deja la mitad de abajo en ceros.
No importa el bit h (como si en andi ori xori) , siempre los pone en los 16 de la parte alta.
### Instrucciones
- LUI r1, 0x1234

### Precondiciones
set pc 0

### Code
s [0x0] 0x38031234

00111 opcode (LUI = 0x07)
00000 rs (no usado)
00001 rt ($1)
1,0001,0010,0011,0100 (h=1, imm=0x1234)

0011, 1000, 0000, 0011, 0001, 0010, 0011, 0100
   3        8        0        3        1        2        3        4

### Postcondiciones
R 1: 0x12340000

### Conclusiones
LUI carga 0x1234 en parte alta: {0x1234, 16'b0} = 0x12340000. OK.

Pregunta: 
lui carga en parte alta
ori hace lo mismo en parte baja
orih para que existe? o para que existe lui?

---

## Caso 28: ANDIH

### Descripción
AND inmediato HIGH. imm[16]=1 activa ZeroCatImm = {imm[15:0], 16'b0}.

### Instrucciones
- ANDIH r1, r2, 0x1234

### Precondiciones
set pc 0
s r2 0xFFFFFFFF

### Code
s [0x0] 0x20831234

00100 opcode (mismo que ANDI)
00010 $2
00001 $1
1,0001,0010,0011,0100 (imm[16]=1 → high)

0010, 0000, 1000, 0011, 0001, 0010, 0011, 0100
   2        0        8       3        1        2        3        4

### Postcondiciones
R 1: 0x12340000   R 2: 0xFFFFFFFF
0xFFFFFFFF & 0x12340000 = 0x12340000

### Conclusiones
ANDIH: AND con inmediato en parte alta (0x12340000).


---

## Caso 29: ORIH

### Descripción
OR inmediato HIGH

### Instrucciones
- ORIH r1, r2, 0x5678

### Precondiciones
set pc 0
s r2 0

### Code
s [0x0] 0x28835678

00101 opcode (mismo que ORI)
00010 $2
00001 $1
1,0101,0110,0111,1000 (imm[16]=1, imm[15:0]=0x5678)

0010, 1000, 1000, 0011, 0101, 0110, 0111, 1000
   2        8        8       3        5        6        7        8

### Postcondiciones
R 1: 0x56780000   R 2: 0x00000000
0 | 0x56780000 = 0x56780000

### Conclusiones
ORIH: inmediato va a parte alta, OR con 0 da ese valor.


---

## Caso 30: XORIH

### Descripción
XOR inmediato HIGH

### Instrucciones
- XORIH r1, r2, 0x9ABC

### Precondiciones
set pc 0
s r2 0

### Code
s [0x0] 0x30839ABC

00110  opcode (XORI asumido = 0x06)
00010 $2
00001 $1
1,1001,1010,1011,1100 (imm[16]=1, imm[15:0]=0x9ABC)

0011, 0000, 1000, 0011, 1001, 1010, 1011, 1100
   3        0        8       3        9        A        B        C

### Postcondiciones
R 1: 0x9ABC0000   R 2: 0x00000000
0 ^ 0x9ABC0000 = 0x9ABC0000

### Conclusiones
XORIH: confirma opcode 00110 si funciona con imm[16]=1.


---

## Caso 31: BEQ (Branch if Equal)

### Descripción
Branch if Equal. Estrategia: BEQ en 0x0, ADD r4,r5,r6 en 0x8.
Si tomado → PC=0x8, ejecuta ADD → r4=30. Si no tomado → PC=0x4, r4=0.

### Instrucciones
- BEQ r1, r2, 1

### Precondiciones (TOMADO: r1=5, r2=5)
set pc 0
s [0x8] 0x014C401C
s r1 5
s r2 5
s r5 10
s r6 20

### Precondiciones (NO TOMADO: r1=5, r2=99)
set pc 0
s [0x8] 0x014C401C
s r1 5
s r2 99
s r5 10
s r6 20

### Code
s [0x0] 0x80440001

10000 opcode (BEQ = 0x10)
00001 $1 (rs)
00010 $2 (rt)
0,0000,0000,0000,0001 (imm=1 → BranchAddr=4 → PC=0+4+4=8)

1000, 0000, 0100, 0100, 0000, 0000, 0000, 0001
   8        0        4        4        0       0        0        1

### Postcondiciones
TOMADO:     PC=0x00000008, r4=0x0000001E (30)
NO TOMADO:  PC=0x00000004, r4=0x00000000

### Conclusiones
BEQ funciona: r1 = r2 → salta a 0x8 y ejecuta ADD. r1!=r2 → no salta, sigue a 0x4.
Probado 2026-07-02, binario rtm32 v3.


---

## Caso 32: BNE (Branch if Not Equal)

### Descripción
Branch if Not Equal. Misma estrategia: BNE en 0x0, ADD r4,r5,r6 en 0x8.

### Instrucciones
- BNE r1, r2, 1

### Precondiciones (TOMADO: r1=5, r2=99)
set pc 0
s [0x8] 0x014C401C
s r1 5
s r2 99
s r5 10
s r6 20

### Precondiciones (NO TOMADO: r1=5, r2=5)
set pc 0
s [0x8] 0x014C401C
s r1 5
s r2 5
s r5 10
s r6 20

### Code
s [0x0] 0x88440001

10001 opcode (BNE = 0x11)
00001 $1 (rs)
00010 $2 (rt)
0,0000,0000,0000,0001 (imm=1)

1000, 1000, 0100, 0100, 0000, 0000, 0000, 0001
   8        8        4        4        0       0        0        1

### Postcondiciones
TOMADO:     PC=0x00000008, r4=0x0000001E (30)
NO TOMADO:  PC=0x00000004, r4=0x00000000

### Conclusiones
✅ BNE funciona: r1!=r2 → salta. r1 = r2 → no salta.
Probado 2026-07-02, binario rtm32 v3.

---

## Caso 33: BLT

### Descripción
Branch if Less Than (signed)

### Instrucciones
- BLT r1, r2, 1

### Precondiciones (TOMADO: r1=5, r2=10)

set pc 0
s [0x8] 0x014C401C
s r1 5
s r2 10
s r5 10
s r6 20

### Precondiciones NO TOMADO: r1 = 10 y r2 = 5

set pc 0
s [0x8] 0x014C401C
s r1 10
s r2 5
s r5 10
s r6 20
### Code
s [0x0] 0x90440001

10010 opcode (BLT = 0x12)
00001 $1
00010 $2
0,0000,0000,0000,0001

1001, 0000, 0100, 0100, 0000, 0000, 0000, 0001
   9        0        4        4        0       0        0        1

### Postcondiciones
TOMADO:     PC=0x08, r4=30  (5<10 signed → true)
NO TOMADO:  PC=0x04, r4=0   (10<5 signed → false)

### Conclusiones
BLT compara signed: 5 < 10 → salta, 10 < 5 → no salta.

---

## Caso 34: BGT

### Descripción
Branch if Greater Than (signed)

### Instrucciones
- BGT r1, r2, 1

### Precondiciones (TOMADO: r1=10, r2=5)
set pc 0
s [0x8] 0x014C401C
s r1 10
s r2 5
s r5 10
s r6 20

### Precondiciones (NO TOMADO: r1=5, r2=10)
set pc 0
s [0x8] 0x014C401C
s r1 5
s r2 10
s r5 10
s r6 20
### Code
s [0x0] 0x98440001

10011 opcode (BGT = 0x13)
00001 $1
00010 $2
0,0000,0000,0000,0001

1001, 1000, 0100, 0100, 0000, 0000, 0000, 0001
   9        8        4        4       0        0        0        1

### Postcondiciones
TOMADO:     PC=0x08, r4=30  (10>5 signed → true)
NO TOMADO:  PC=0x04, r4=0   (5>10 signed → false)

### Conclusiones
BGT: 10 > 5 signed → salta. 5 > 10 → no salta.

---

## Caso 35: BLE

### Descripción
Branch if Less or Equal (signed)

### Instrucciones
- BLE r1, r2, 1

### Precondiciones (TOMADO: r1=5, r2=5)
set pc 0
s [0x8] 0x014C401C
s r1 5
s r2 5
s r5 10
s r6 20

### Precondiciones (NO TOMADO: r1=10, r2=5)
set pc 0
s [0x8] 0x014C401C
s r1 10
s r2 5
s r5 10
s r6 20
### Code
s [0x0] 0xA0440001

10100 opcode (BLE = 0x14)
00001 $1
00010 $2
0,0000,0000,0000,0001

1010, 0000, 0100, 0100, 0000, 0000, 0000, 0001
   A        0        4        4        0       0        0        1

### Postcondiciones
TOMADO:     PC=0x08, r4=30  (5<=5 → true)
NO TOMADO:  PC=0x04, r4=0   (10<=5 → false)

### Conclusiones
BLE: 5 <= 5 → salta. 10 <= 5 → no salta.

---

## Caso 36: BGE

### Descripción
Branch if Greater or Equal (signed)

### Instrucciones
- BGE r1, r2, 1

### Precondiciones (TOMADO: r1=10, r2=5)
set pc 0
s [0x8] 0x014C401C
s r1 10
s r2 5
s r5 10
s r6 20

### Precondiciones (NO TOMADO: r1=5, r2=10)
set pc 0
s [0x8] 0x014C401C
s r1 5
s r2 10
s r5 10
s r6 20
### Code
s [0x0] 0xA8440001

10101 opcode (BGE = 0x15)
00001 $1
00010 $2
0,0000,0000,0000,0001

1010, 1000, 0100, 0100, 0000, 0000, 0000, 0001
   A        8        4        4        0       0        0        1

### Postcondiciones
TOMADO:     PC=0x08, r4=30  (10>=5 → true)
NO TOMADO:  PC=0x04, r4=0   (5>=10 → false)

### Conclusiones
BGE: 10 >= 5 → salta. 5 >= 10 → no salta.


---

## Caso 40: LHU (Load Halfword Unsigned) — Bug encontrado y corregido en v3

### Descripción
Load Halfword Unsigned: carga 16 bits de memoria y hace zero-extend a 32 bits.
En versiones anteriores ejecutaba como LB (Load Byte).
Corregido por Profesor en rtm32 v3 (2026-07-02)

### Instrucciones
- LHU r1, r2, 0

### Precondiciones
set pc 0
s r2 0x50
s [0x50] 0x0000BBBB

### Code
s [0x0] 0x68820000

01101 opcode (LHU = 0x0D)
00010 $2
00001 $1
0,0000,0000,0000,0000 (imm 0)

0110, 1000, 1000, 0010, 0000, 0000, 0000, 0000
   6        8        8        2       0        0        0        0

### Postcondiciones
R 1: 0x0000BBBB   R 2: 0x00000050
M[0x50](15:0) = 0xBBBB → zero-extend → 0x0000BBBB

### Conclusiones
ARREGLADO en v3. LHU carga 2 bytes (halfword) y hace zero-extend: 0xBBBB → 0x0000BBBB.
Antes devolvía 0xFFFFFFBB (sign-extend de 1 byte, comportamiento de LB).
Probado 2026-07-02 con binario rtm32 v3.