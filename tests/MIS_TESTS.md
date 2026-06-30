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


### Instrucciones
- ORI r1, r2, 8

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 10: XORI

### Descripción


### Instrucciones
- XORI r1, r2, 0xF

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 11: SLT

### Descripción


### Instrucciones
- SLT r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 12: SLTU

### Descripción


### Instrucciones
- SLTU r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 13: SLTI

### Descripción


### Instrucciones
- SLTI r1, r2, 10

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 14: SLTIU

### Descripción


### Instrucciones
- SLTIU r1, r2, 1

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 15: SLL

### Descripción


### Instrucciones
- SLL r1, r2, 4

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 16: SRL

### Descripción


### Instrucciones
- SRL r1, r2, 4

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 17: SRA

### Descripción


### Instrucciones
- SRA r1, r2, 4

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 18: SLLR

### Descripción


### Instrucciones
- SLLR r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 19: SRLR

### Descripción


### Instrucciones
- SRLR r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 20: SRAR

### Descripción


### Instrucciones
- SRAR r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 21: LW

### Descripción


### Instrucciones
- LW r1, r2, 0

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 22: SW

### Descripción


### Instrucciones
- SW r1, r2, 0

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 23: J

### Descripción


### Instrucciones
- J 4

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 24: JR

### Descripción


### Instrucciones
- JR r31

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 25: JAL

### Descripción


### Instrucciones
- JAL 4

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 26: JALR

### Descripción


### Instrucciones
- JALR r4

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 27: LUI

### Descripción


### Instrucciones
- LUI r1, 0x1234

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 28: ANDIH

### Descripción


### Instrucciones
- ANDIH r1, r2, 0x1234

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 29: ORIH

### Descripción


### Instrucciones
- ORIH r1, r2, 0x5678

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 30: XORIH

### Descripción


### Instrucciones
- XORIH r1, r2, 0x9ABC

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 31: BEQ

### Descripción


### Instrucciones
- BEQ r1, r2, 1

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 32: BNE

### Descripción


### Instrucciones
- BNE r1, r2, 1

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 33: BLT

### Descripción


### Instrucciones
- BLT r1, r2, 1

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 34: BGT

### Descripción


### Instrucciones
- BGT r1, r2, 1

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 35: BLE

### Descripción


### Instrucciones
- BLE r1, r2, 1

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 36: BGE

### Descripción


### Instrucciones
- BGE r1, r2, 1

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 37: SH

### Descripción


### Instrucciones
- SH r1, r2, 0

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 38: SB

### Descripción


### Instrucciones
- SB r1, r2, 0

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 39: LH

### Descripción


### Instrucciones
- LH r1, r2, 0

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 40: LHU

### Descripción


### Instrucciones
- LHU r1, r2, 0

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 41: LB

### Descripción


### Instrucciones
- LB r1, r2, 0

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 42: LBU

### Descripción


### Instrucciones
- LBU r1, r2, 0

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 43: LWX

### Descripción


### Instrucciones
- LWX r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 44: LHX

### Descripción


### Instrucciones
- LHX r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 45: LHUX

### Descripción


### Instrucciones
- LHUX r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 46: LBX

### Descripción


### Instrucciones
- LBX r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 47: LBUX

### Descripción


### Instrucciones
- LBUX r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 48: MUL

### Descripción


### Instrucciones
- MUL r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 49: MULH

### Descripción


### Instrucciones
- MULH r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 50: MULHU

### Descripción


### Instrucciones
- MULHU r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 51: DIV

### Descripción


### Instrucciones
- DIV r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 52: DIVU

### Descripción


### Instrucciones
- DIVU r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 53: REST

### Descripción


### Instrucciones
- REST r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones



---

## Caso 54: RESTU

### Descripción


### Instrucciones
- RESTU r1, r2, r3

### Precondiciones
- 
- 
- 

### Code


### Postcondiciones
- 
- 

### Conclusiones


