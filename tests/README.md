# Tests de verificación del ISA

Cada `.bin` prueba un grupo de instrucciones. Cargá con `load`, hacé `step` paso a paso, y verificá registros con `registers`.

## Cómo ejecutar un test

```bash
# Terminal 1
./rtm32 -d telnet

# Terminal 2
telnet localhost 4444
load tests/test_rtype_arith.bin
step        # ejecutá N veces
registers   # compará con lo esperado
```

## Lista de tests

| Test | Instrucciones | Qué verifica |
|------|---------------|--------------|
| `test_rtype_arith` | ADD, SUB, AND, OR, XOR, NOR, SLT, SLTU | Formato R-type, tabla de funct |
| `test_rtype_shifts` | SLL, SRL, SRA, SLLR, SRLR, SRAR | Shifts inmediatos y variables |
| `test_itype_alu` | ANDI, ORI, XORI | Opcodes correctos (PDF ambiguo) |
| `test_itype_high` | ANDIH, ORIH, XORIH | Codificación high (imm[16]=1) |
| `test_lui` | LUI | ¿ADDI con imm[16]=1 y rs=0? |
| `test_branches` | BEQ, BNE, BLT, BGT, BLE, BGE | Saltos condicionales |
| `test_jr_jalr` | JR, JALR | Saltos por registro |
| `test_slti` | SLTI, SLTIU | Set-less-than inmediato |
| `test_indexed` | LWX | Load indexado (base+offset en reg) |
| `test_mul_div` | MUL, MULH, MULHU, DIV, DIVU, REST, RESTU | Multiplicación y división |
| `test_j_jal` | JAL | Salto con link (verifica r31) |

## Resultados esperados

Ejecutá `python3 gen_tests.py` para ver el detalle de cada test con valores exactos esperados paso a paso.
