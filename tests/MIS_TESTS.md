# Testing de instrucciones RTM32

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
s [0x0] 0xC0820005

11000 opcode
00010 $2
00001 $1
0,0000,0000,0000,0101 (imm 5 en 17 bits.)

1100, 0000, 1000, 0010, 0000, 0000, 0000,0101
C          0          8      2          0       0         0      5

### Postcondiciones
- R[ 1]: 0x0000000A   R[ 2]: 0x00000005
- 5 + 5 = 10 = 0xA

### Conclusiones
addi funciona correctamente, le suma el valor en imm al primer registro y lo guarda en el segundo


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
AND con inmediato

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
OR inmediato (zero-extend)

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
Si r1=0xF0 → XORI opcode 00110 confirmado. Si r1=0x0F → comparte opcode con ANDI (00100).


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

### Postcondiciones
R 1: 0x00000008   R 2: 0x00000080   R 3: 0x00000004
0x80 >> 4 = 8

### Conclusiones
SRLR correcto.


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

## Caso 21: LW

### Descripción
Load Word: R[rt] = M[R[rs] + SignExtImm]

### Instrucciones
- LW r1, r2, 0

### Precondiciones
set pc 0
s [0x1000] 0xDEADBEEF
s r2 0x1000

### Code
s [0x0] 0x40820000

01000 opcode (LW = 0x08)
00010 $2 (base)
00001 $1 (destino)
0,0000,0000,0000,0000 (offset 0)

0100, 0000, 1000, 0010, 0000, 0000, 0000, 0000
   4        0        8        2        0        0       0        0

### Postcondiciones
R 1: 0xDEADBEEF   R 2: 0x00001000
M[0x1000 + 0] = 0xDEADBEEF

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
s r2 0x1000

### Code
s [0x0] 0x48820000

01001 opcode (SW = 0x09)
00010 $2 (base)
00001 $1 (dato a guardar)
0,0000,0000,0000,0000 (offset 0)

0100, 1000, 1000, 0010, 0000, 0000, 0000, 0000
   4        8        8        2        0       0        0        0

### Postcondiciones
x xw 0x1000 1 → muestra 0xCAFEBABE

### Conclusiones
SW guarda 4 bytes en M[0x1000]. Verificar con: x xw 0x1000 1


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
000,0000,0000,0000,0000,0000,0000,0100 (address 4)

0001, 1000, 0000, 0000, 0000, 0000, 0000, 0100
   1        8        0        0        0        0       0        4

### Postcondiciones
PC = 0x00000010   R 31: 0x00000004

### Conclusiones
JAL: salta a 0x10 y guarda retorno (0x04) en $31.


---

## Caso 26: JALR

### Descripción
Jump And Link Register: R[31] = PC+4; PC = R[rs]

### Instrucciones
- JALR r4

### Precondiciones
set pc 0
s r4 0x100

### Code
s [0x0] 0x0100000F

00000 opcode (R-type)
00100 rs ($4)
00000 rt
00000 rd
00000 aux
0001111 funct (JALR = 0x0F)

0000, 0001, 0000, 0000, 0000, 0000, 0000, 1111
   0        1        0        0        0        0       0        F

### Postcondiciones
PC = 0x00000100   R 31: 0x00000004

### Conclusiones
JALR: PC = R[4] = 0x100, $31 = retorno (0x04).


---

## Caso 27: LUI

### Descripción
Load Upper Immediate: R[rt] = {imm[15:0], 16'b0}. Opcode 11000 (mismo que ADDI),
se distingue con rs=0 + imm[16]=1.

### Instrucciones
- LUI r1, 0x1234

### Precondiciones
set pc 0

### Code
s [0x0] 0xC0031234

11000 opcode (mismo que ADDI = 0x18)
00000 rs ($0: señal de LUI)
00001 rt ($1)
1,0001,0010,0011,0100 (imm[16]=1, imm[15:0]=0x1234)

1100, 0000, 0000, 0011, 0001, 0010, 0011, 0100
   C        0         0       3        1        2        3        4

### Postcondiciones
R 1: 0x12340000

### Conclusiones
LUI carga 0x1234 en parte alta. Si r1 = 0x00001234 → imm fue a baja (bug).
Si r1 = 0xFFFFFFFF → se sign-extendió. Si r1 = 0x12340000 → OK.


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

00110 opcode (XORI asumido = 0x06)
00010 $2
00001 $1
1,1001,1010,1011,1100 (imm[16]=1, imm[15:0]=0x9ABC)

0011, 0000, 1000, 0011, 1001, 1010, 1011, 1100
   3        0        8       3        9        A        B        C

### Postcondiciones
R 1: 0x9ABC0000   R 2: 0x00000000
0 ^ 0x9ABC0000 = 0x9ABC0000

### Conclusiones
XORIH: confirma opcode 00110 si funciona con imm[16]=1. Si r1=0 → XORI no usa opcode 00110.


---

## Caso 31: BEQ

### Descripción
Branch if Equal. Estrategia: BEQ en 0x0, ADD r4,r5,r6 en 0x8. Si tomado → PC=8, r4=30. Si no → PC=4, r4=0.

### Instrucciones
- BEQ r1, r2, 1

### Precondiciones (caso TOMADO: r1=5, r2=5)
set pc 0
s [0x8] 0x014C401C
s r1 5
s r2 5
s r5 10
s r6 20

### Precondiciones (caso NO TOMADO: r1=5, r2=99)
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
BEQ: r1==r2 → salta a 0x8. r1!=r2 → sigue a 0x4.


---

## Caso 32: BNE

### Descripción
Branch if Not Equal

### Instrucciones
- BNE r1, r2, 1

### Precondiciones (TOMADO: r1=5, r2=99) (NO TOMADO: r1=5, r2=5)
set pc 0
s [0x8] 0x014C401C
s r5 10
s r6 20
[setear r1,r2 según caso]

### Code
s [0x0] 0x88440001

10001 opcode (BNE = 0x11)
00001 $1
00010 $2
0,0000,0000,0000,0001 (imm=1)

1000, 1000, 0100, 0100, 0000, 0000, 0000, 0001
   8        8        4        4        0       0        0        1

### Postcondiciones
TOMADO:     PC=0x08, r4=30  (r1!=r2 → true)
NO TOMADO:  PC=0x04, r4=0   (r1==r2 → false)

### Conclusiones
BNE: r1!=r2 → salta. r1==r2 → no salta.


---

## Caso 33: BLT

### Descripción
Branch if Less Than (signed)

### Instrucciones
- BLT r1, r2, 1

### Precondiciones (TOMADO: r1=5, r2=10) (NO TOMADO: r1=10, r2=5)
set pc 0
s [0x8] 0x014C401C
s r5 10
s r6 20
[setear r1,r2 según caso]

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

### Precondiciones (TOMADO: r1=10, r2=5) (NO TOMADO: r1=5, r2=10)
set pc 0
s [0x8] 0x014C401C
s r5 10
s r6 20
[setear r1,r2 según caso]

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

### Precondiciones (TOMADO: r1=5, r2=5) (NO TOMADO: r1=10, r2=5)
set pc 0
s [0x8] 0x014C401C
s r5 10
s r6 20
[setear r1,r2 según caso]

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

### Precondiciones (TOMADO: r1=10, r2=5) (NO TOMADO: r1=5, r2=10)
set pc 0
s [0x8] 0x014C401C
s r5 10
s r6 20
[setear r1,r2 según caso]

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

## Caso 37: SH

### Descripción
Store Halfword: M[addr](15:0) = R[rt](15:0)

### Instrucciones
- SH r1, r2, 0

### Precondiciones
set pc 0
s r1 0x1234ABCD
s r2 0x1000

### Code
s [0x0] 0x50820000

01010 opcode (SH = 0x0A)
00010 $2 (base)
00001 $1 (dato, solo halfword baja)
0,0000,0000,0000,0000 (offset 0)

0101, 0000, 1000, 0010, 0000, 0000, 0000, 0000
   5        0        8        2       0        0        0        0

### Postcondiciones
x xw 0x1000 1 → halfword baja = 0xABCD

### Conclusiones
SH guarda 16 bits bajos de $1. Verificar con: x xw 0x1000 1


---

## Caso 38: SB

### Descripción
Store Byte: M[addr](7:0) = R[rt](7:0)

### Instrucciones
- SB r1, r2, 0

### Precondiciones
set pc 0
s r1 0x41
s r2 0x1000

### Code
s [0x0] 0x58820000

01011 opcode (SB = 0x0B)
00010 $2 (base)
00001 $1 (dato)
0,0000,0000,0000,0000 (offset 0)

0101, 1000, 1000, 0010, 0000, 0000, 0000, 0000
   5        8        8        2       0        0        0        0

### Postcondiciones
x xb 0x1000 4 → primer byte = 0x41 ('A')

### Conclusiones
SB guarda 1 byte. Verificar con: x xb 0x1000 4


---

## Caso 39: LH

### Descripción
Load Halfword con sign-extend

### Instrucciones
- LH r1, r2, 0

### Precondiciones
set pc 0
s [0x1000] 0x00008000
s r2 0x1000

### Code
s [0x0] 0x60820000

01100 opcode (LH = 0x0C)
00010 $2
00001 $1
0,0000,0000,0000,0000

0110, 0000, 1000, 0010, 0000, 0000, 0000, 0000
   6        0        8        2        0        0        0        0

### Postcondiciones
R 1: 0xFFFF8000   R 2: 0x00001000
Halfword 0x8000 → sign-extend → 0xFFFF8000

### Conclusiones
LH extiende signo: 0x8000 → 0xFFFF8000 (bit 15=1 → bits altos en 1).


---

## Caso 40: LHU

### Descripción
Load Halfword Unsigned (zero-extend)

### Instrucciones
- LHU r1, r2, 0

### Precondiciones
set pc 0
s [0x1000] 0x00008000
s r2 0x1000

### Code
s [0x0] 0x68820000

01101 opcode (LHU = 0x0D)
00010 $2
00001 $1
0,0000,0000,0000,0000

0110, 1000, 1000, 0010, 0000, 0000, 0000, 0000
   6        8        8        2       0        0        0        0

### Postcondiciones
R 1: 0x00008000   R 2: 0x00001000
0x8000 → zero-extend → 0x00008000

### Conclusiones
LHU: zero-extend, bits altos = 0.


---

## Caso 41: LB

### Descripción
Load Byte con sign-extend

### Instrucciones
- LB r1, r2, 0

### Precondiciones
set pc 0
s [0x1000] 0x00000080
s r2 0x1000

### Code
s [0x0] 0x70820000

01110 opcode (LB = 0x0E)
00010 $2
00001 $1
0,0000,0000,0000,0000

0111, 0000, 1000, 0010, 0000, 0000, 0000, 0000
   7        0        8        2        0        0        0        0

### Postcondiciones
R 1: 0xFFFFFF80   R 2: 0x00001000
Byte 0x80 → sign-extend → 0xFFFFFF80

### Conclusiones
LB: 0x80 es negativo → extiende con 1s. Resultado: 0xFFFFFF80.


---

## Caso 42: LBU

### Descripción
Load Byte Unsigned (zero-extend)

### Instrucciones
- LBU r1, r2, 0

### Precondiciones
set pc 0
s [0x1000] 0x00000080
s r2 0x1000

### Code
s [0x0] 0x78820000

01111 opcode (LBU = 0x0F)
00010 $2
00001 $1
0,0000,0000,0000,0000

0111, 1000, 1000, 0010, 0000, 0000, 0000, 0000
   7        8        8        2       0        0        0        0

### Postcondiciones
R 1: 0x00000080   R 2: 0x00001000
Byte 0x80 → zero-extend → 0x00000080

### Conclusiones
LBU: zero-extend, bits altos = 0. Resultado: 0x00000080.


---

## Caso 43: LWX

### Descripción
Load Word Indexed: R[rt] = M[R[rs] + R[rd]]. ATENCIÓN: en indexed loads, rt es destino y rd es offset.

### Instrucciones
- LWX r1, r2, r3

### Precondiciones
set pc 0
s [0x1050] 0xBEEFFACE
s r2 0x1000
s r3 0x50

### Code
s [0x0] 0x00823014

00000 opcode
00010 $2 (rs: base)
00001 $1 (rt: destino)
00011 $3 (rd: offset)
00000 aux
0010100 funct (LWX = 0x14)

0000, 0000, 1000, 0010, 0011, 0000, 0001, 0100
   0        0        8        2        3        0       1        4

### Postcondiciones
R 1: 0xBEEFFACE   R 2: 0x00001000   R 3: 0x00000050
M[0x1000 + 0x50] = M[0x1050] = 0xBEEFFACE

### Conclusiones
LWX: dirección = R[rs] + R[rd] (base + offset en registros).


---

## Caso 44: LHX

### Descripción
Load Halfword Indexed con sign-extend

### Instrucciones
- LHX r1, r2, r3

### Precondiciones
set pc 0
s [0x1050] 0x00008000
s r2 0x1000
s r3 0x50

### Code
s [0x0] 0x00823010

00000 opcode
00010 $2 (rs)
00001 $1 (rt)
00011 $3 (rd)
00000 aux
0010000 funct (LHX = 0x10)

0000, 0000, 1000, 0010, 0011, 0000, 0001, 0000
   0        0        8        2        3        0       1        0

### Postcondiciones
R 1: 0xFFFF8000
M[0x1050](15:0) = 0x8000 → sign-extend → 0xFFFF8000

### Conclusiones
LHX: halfword indexado con sign-extend. Dirección = R[rs] + R[rd].


---

## Caso 45: LHUX

### Descripción
Load Halfword Indexed Unsigned

### Instrucciones
- LHUX r1, r2, r3

### Precondiciones
set pc 0
s [0x1050] 0x00008000
s r2 0x1000
s r3 0x50

### Code
s [0x0] 0x00823011

00000 opcode
00010 $2 (rs)
00001 $1 (rt)
00011 $3 (rd)
00000 aux
0010001 funct (LHUX = 0x11)

0000, 0000, 1000, 0010, 0011, 0000, 0001, 0001
   0        0        8        2        3        0       1        1

### Postcondiciones
R 1: 0x00008000
0x8000 → zero-extend → 0x00008000

### Conclusiones
LHUX: halfword indexado sin extender signo.


---

## Caso 46: LBX

### Descripción
Load Byte Indexed con sign-extend

### Instrucciones
- LBX r1, r2, r3

### Precondiciones
set pc 0
s [0x1050] 0x00000080
s r2 0x1000
s r3 0x50

### Code
s [0x0] 0x00823012

00000 opcode
00010 $2 (rs)
00001 $1 (rt)
00011 $3 (rd)
00000 aux
0010010 funct (LBX = 0x12)

0000, 0000, 1000, 0010, 0011, 0000, 0001, 0010
   0        0        8        2        3        0       1        2

### Postcondiciones
R 1: 0xFFFFFF80
Byte 0x80 → sign-extend → 0xFFFFFF80

### Conclusiones
LBX: byte indexado con sign-extend.


---

## Caso 47: LBUX

### Descripción
Load Byte Indexed Unsigned

### Instrucciones
- LBUX r1, r2, r3

### Precondiciones
set pc 0
s [0x1050] 0x00000080
s r2 0x1000
s r3 0x50

### Code
s [0x0] 0x00823013

00000 opcode
00010 $2 (rs)
00001 $1 (rt)
00011 $3 (rd)
00000 aux
0010011 funct (LBUX = 0x13)

0000, 0000, 1000, 0010, 0011, 0000, 0001, 0011
   0        0        8        2        3        0       1        3

### Postcondiciones
R 1: 0x00000080
Byte 0x80 → zero-extend → 0x00000080

### Conclusiones
LBUX: byte indexado, bits altos = 0.


---

## Caso 48: MUL

### Descripción
Multiplicación: devuelve 32 bits bajos del producto 64-bit.

### Instrucciones
- MUL r1, r2, r3

### Precondiciones
set pc 0
s r2 6
s r3 7

### Code
s [0x0] 0x00861015

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0010101 funct (MUL = 0x15)

0000, 0000, 1000, 0110, 0001, 0000, 0001, 0101
   0        0        8        6        1        0       1        5

### Postcondiciones
R 1: 0x0000002A   R 2: 0x00000006   R 3: 0x00000007
6 × 7 = 42 = 0x2A

### Conclusiones
MUL: 6 × 7 = 42, devuelve parte baja del producto.


---

## Caso 49: MULH

### Descripción
Multiply High (signed): 32 bits altos del producto 64-bit.

### Instrucciones
- MULH r1, r2, r3

### Precondiciones
set pc 0
s r2 0x10000000
s r3 0x10

### Code
s [0x0] 0x00861016

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0010110 funct (MULH = 0x16)

0000, 0000, 1000, 0110, 0001, 0000, 0001, 0110
   0        0        8        6        1        0       1        6

### Postcondiciones
R 1: 0x00000001
0x10000000 × 0x10 = 0x100000000 → high 32 = 1

### Conclusiones
MULH: 0x10000000 × 16 = 0x100000000, upper 32 = 1.


---

## Caso 50: MULHU

### Descripción
Multiply High Unsigned

### Instrucciones
- MULHU r1, r2, r3

### Precondiciones
set pc 0
s r2 0x10000000
s r3 0x10

### Code
s [0x0] 0x00861017

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0010111 funct (MULHU = 0x17)

0000, 0000, 1000, 0110, 0001, 0000, 0001, 0111
   0        0        8        6        1        0       1        7

### Postcondiciones
R 1: 0x00000001
0x10000000 × 0x10 unsigned → high = 1

### Conclusiones
MULHU: mismo resultado que MULH (operandos positivos = misma parte alta).


---

## Caso 51: DIV

### Descripción
División signed: R[rd] = R[rs] / R[rt]

### Instrucciones
- DIV r1, r2, r3

### Precondiciones
set pc 0
s r2 20
s r3 6

### Code
s [0x0] 0x00861018

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0011000 funct (DIV = 0x18)

0000, 0000, 1000, 0110, 0001, 0000, 0001, 1000
   0        0        8        6        1        0       1        8

### Postcondiciones
R 1: 0x00000003   R 2: 0x00000014   R 3: 0x00000006
20 / 6 = 3 (truncado)

### Conclusiones
DIV signed: 20 / 6 = 3.


---

## Caso 52: DIVU

### Descripción
División Unsigned

### Instrucciones
- DIVU r1, r2, r3

### Precondiciones
set pc 0
s r2 20
s r3 6

### Code
s [0x0] 0x00861019

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0011001 funct (DIVU = 0x19)

0000, 0000, 1000, 0110, 0001, 0000, 0001, 1001
   0        0        8        6        1        0       1        9

### Postcondiciones
R 1: 0x00000003
20 / 6 unsigned = 3

### Conclusiones
DIVU: 20 / 6 = 3 sin signo.


---

## Caso 53: REST

### Descripción
Resto signed: R[rd] = R[rs] % R[rt]

### Instrucciones
- REST r1, r2, r3

### Precondiciones
set pc 0
s r2 20
s r3 6

### Code
s [0x0] 0x0086101A

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0011010 funct (REST = 0x1A)

0000, 0000, 1000, 0110, 0001, 0000, 0001, 1010
   0        0        8        6        1        0       1        A

### Postcondiciones
R 1: 0x00000002
20 % 6 = 2

### Conclusiones
REST: 20 mod 6 = 2.


---

## Caso 54: RESTU

### Descripción
Resto Unsigned

### Instrucciones
- RESTU r1, r2, r3

### Precondiciones
set pc 0
s r2 20
s r3 6

### Code
s [0x0] 0x0086101B

00000 opcode
00010 $2
00011 $3
00001 $1
00000 aux
0011011 funct (RESTU = 0x1B)

0000, 0000, 1000, 0110, 0001, 0000, 0001, 1011
   0        0        8        6        1        0       1        B

### Postcondiciones
R 1: 0x00000002
20 % 6 unsigned = 2

### Conclusiones
RESTU: 20 mod 6 = 2 sin signo.
