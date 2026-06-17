# RTM32 — Guía de uso y Hello World

> Procesador didáctico de 32 bits. Emulador v0.5 con debugger remoto vía telnet.

---

## 1. Requisitos

- Linux
- `xterm` (terminal)
- `picocom` (comunicación serial)
- `telnet` (para conectarse al debugger)

Instalación rápida:

```bash
sudo apt install xterm picocom telnet
```

---

## 2. El emulador

El binario `./rtm32` emula el procesador. Opciones principales:

| Flag | Descripción |
|------|-------------|
| `-d telnet` | Activa debugger remoto por telnet (puerto 4444) |
| `-d console` | Debugger interactivo por terminal local |
| `-d batch` | Debugger por lotes (archivo de comandos) |
| `-l FILE` | Carga un binario en memoria |
| `-m SIZE` | Tamaño de RAM de usuario (ej: 4K, 2M) |
| `-x ADDR` | Dirección de inicio de ejecución (default 0x00000000) |
| `-p PORT` | Puerto del debugger (default 4444) |
| `-n STEPS` | Limita ejecución a N pasos |

El emulador **no tiene assembler integrado**: hay que cargar código máquina (bytes crudos) con `-l`.

---

## 3. Flujo de trabajo

```bash
# Terminal 1: lanzar el emulador con debugger telnet
./rtm32 -d telnet

# Terminal 2: conectarse al debugger
telnet localhost 4444
```

El debugger entiende estos comandos:

| Comando | Acción |
|---------|--------|
| `help` | Lista todos los comandos |
| `registers` | Muestra los 32 registros + PC + flags |
| `step` | Ejecuta una instrucción |
| `continue` | Reanuda ejecución |
| `break ADDR` | Pone breakpoint en dirección |
| `blist` / `breakpoints` | Lista breakpoints activos |
| `delete N` | Borra breakpoint N |
| `until ADDR` | Ejecuta hasta llegar a dirección |
| `examine ADDR LEN` | Vuelca memoria en hex |
| `dump ADDR LEN FILE` | Vuelca memoria a archivo |
| `load FILE` | Carga binario/snapshot en memoria |
| `set REG VAL` | Modifica un registro |
| `reset` | Resetea la CPU |
| `quit` | Sale del debugger |
| `control` | Muestra registros de control |

---

## 4. Formato de snapshot (para `load` y `-l`)

Tanto `-l FILE` como el comando `load FILE` del debugger cargan un snapshot con **header de 60 bytes**:

| Offset | Tamaño | Campo | Valor |
|--------|--------|-------|-------|
| 0 | 4 B | **magic** | `0x4742444d` (`"MDBG"` en LE) |
| 4 | 4 B | **version** | `2` (debe ser >= 2) |
| 8 | 4 B | **base_addr** | Dirección de carga |
| 12 | 4 B | **payload_size** | Tamaño del código/datos (bytes) |
| 16 | 12 B | **padding** | Ceros |
| 28 | 32 B | **mode** | String `"RTM32"` + ceros |

Después del header (byte 60 en adelante) va el payload: el código máquina crudo.

### Ejemplo mínimo (Python)

```python
header = struct.pack('<III', 0x4742444d, 2, 0)   # magic, version, base_addr
header += struct.pack('<I', len(payload))          # payload_size
header += b'\x00' * 12                             # padding [16-27]
header += b'RTM32\x00'.ljust(32, b'\x00')          # mode [28-59]
# len(header) == 60

with open('programa.bin', 'wb') as f:
    f.write(header + payload)
```

> Confirmado con `ADDI r1, r0, 42` → R[1] = 0x2A. Header armado descifrando `handle_load` del binario con `objdump`.

---

## 5. MMIO — UART en 0xFFFFFF00

La consola serial está mapeada en la dirección **`0xFFFFFF00`**:

- **Escribir** un byte en `0xFFFFFF00` → el carácter aparece en la consola.
- **Leer** un byte de `0xFFFFFF00` → devuelve el carácter tipeado (buffer circular de 16 bytes).

Esto permite E/S sin syscalls: el "Hello World" se hace escribiendo byte a byte en esa dirección.

---

## 5. Instruction Set (ISA)

### 6.1 Formato de instrucción (32 bits) ✅ CONFIRMADO

Cada instrucción ocupa exactamente 4 bytes. **El CPU es big-endian en la disposición de campos** dentro de la palabra, pero las palabras se almacenan en memoria en **little-endian** (host x86).

**I-type** (inmediatas, loads, stores, branches):
```
[31:27] opcode   (5 bits)
[26:22] rs       (5 bits)  — registro fuente
[21:17] rt       (5 bits)  — registro destino / datos
[16:0]  imm      (17 bits) — inmediato
```

Ejemplo confirmado — `ADDI r1, r0, 42`:
- opcode = `11000`, rs = `00000` (r0), rt = `00001` (r1), imm = `0...0101010` (42)
- Palabra big-endian: `11000 00000 00001 0...0101010`
- Bytes en memoria (little-endian): `0x2A 0x00 0x02 0xC0`

```
Byte 0 (LSB): 0x2A = 00101010  → imm[7:0]
Byte 1:       0x00 = 00000000  → imm[15:8] + imm[16] en bit 7 del byte 2
Byte 2:       0x02 = 00000010  → rt[2:0] + imm[16] + resto
Byte 3 (MSB): 0xC0 = 11000000  → opcode[4:0] + rs[4:2]
```

> Verificado: `printf '\x2a\x00\x02\xc0'` → cargado con snapshot → `step` → `R[1] = 0x0000002A`.

**R-type** (aritméticas, lógicas, saltos indirectos):
```
[31:27] opcode   (5 bits) = 00000
[26:22] rs       (5 bits)  — fuente 1
[21:17] rt       (5 bits)  — fuente 2
[16:12] rd       (5 bits)  — destino
[11:7]  aux      (5 bits)  — shamt / funct extendido
[6:0]   funct    (7 bits)  — operación
```

**J-type** (saltos):
```
[31:27] opcode   (5 bits) = 00010 / 00011
[26:0]  address  (27 bits) — dirección de salto (en palabras)
```

Convenciones de inmediatos:
- `SignExtImm`  = `{15{imm[16]}, imm}` — extensión de signo a 32 bits
- `ZeroExtImm`  = `{15{1'b0}, imm}` — extensión con ceros
- `ZeroCatImm`  = `{imm, 15{1'b0}}` — inmediato en parte alta
- `JumpAddr`    = `{PC+4[31:29], address, 2'b0}`
- `BranchAddr`  = `{13{imm[16]}, imm, 2'b0}`

---

### 5.2 Tabla A.1 — I-type (ordenado por opcode)

| Opcode  | Mnemo     | Operands     | Operación                              |
| ------- | --------- | ------------ | -------------------------------------- |
| `00000` | R-Type    | rs rt rd aux | Ver tabla A.2                          |
| `00010` | **J**     | address      | PC = JumpAddr                          |
| `00011` | **JAL**   | address      | R[31] = PC+4; PC = JumpAddr            |
| `00100` | **ANDI**  | rs rt imm    | R[rt] = R[rs] & ZeroExtImm             |
|         | **ANDIH** | rs rt imm    | R[rt] = R[rs] & ZeroCatImm             |
| 00101   | **ORI**   | rs rt imm    | R[rt] = R[rs] \| ZeroExtImm            |
|         | **ORIH**  | rs rt imm    | R[rt] = R[rs] \| ZeroCatImm            |
| `00100` | **XORI**  | rs rt imm    | R[rt] = R[rs] ⊕ ZeroExtImm             |
|         | **XORIH** | rs rt imm    | R[rt] = R[rs] ⊕ ZeroCatImm             |
| `01000` | **LW**    | rs rt imm    | R[rt] = M[addr] *(word)*               |
| `01001` | **SW**    | rs rt imm    | M[addr] = R[rt] *(word)*               |
| `01010` | **SH**    | rs rt imm    | M[addr] (15:0) = R[rt] (15:0) *(half)* |
| `01011` | **SB**    | rs rt imm    | M[addr] (7:0) = R[rt] (7:0) *(byte)*   |
| `01100` | **LH**    | rs rt imm    | R[rt] = sign-extend( M[addr] (15:0) )  |
| `01101` | **LHU**   | rs rt imm    | R[rt] = zero-extend( M[addr] (15:0) )  |
| `01110` | **LB**    | rs rt imm    | R[rt] = sign-extend( M[addr] (7:0) )   |
| `01111` | **LBU**   | rs rt imm    | R[rt] = zero-extend( M[addr] (7:0) )   |
| `10000` | **BEQ**   | rs rt imm    | if R[rs]==R[rt] PC=PC+4+BranchAddr     |
| `10001` | **BNE**   | rs rt imm    | if R[rs]!=R[rt] PC=PC+4+BranchAddr     |
| `10010` | **BLT**   | rs rt imm    | if R[rs]<R[rt] PC=PC+4+BranchAddr      |
| `10011` | **BGT**   | rs rt imm    | if R[rs]>R[rt] PC=PC+4+BranchAddr      |
| `10100` | **BLE**   | rs rt imm    | if R[rs]<=R[rt] PC=PC+4+BranchAddr     |
| `10101` | **BGE**   | rs rt imm    | if R[rs]>=R[rt] PC=PC+4+BranchAddr     |
| `10110` | **SLTI**  | rs rt imm    | R[rt] = (R[rs] < SignExtImm) ? 1 : 0   |
| `10111` | **SLTIU** | rs rt imm    | Igual pero sin signo                   |
| `11000` | **ADDI**  | rs rt imm    | R[rt] = R[rs] + SignExtImm             |
| `11000` | **LUI**   | rt imm       | R[rt] = ZeroCatImm                     |

> `addr = R[rs] + SignExtImm`. La distinción ANDI/ANDIH, ORI/ORIH, XORI/XORIH, ADDI/LUI se da por un campo de la codificación (probablemente imm[16]).

---

### 5.3 Tabla A.2 — R-type (ordenado por funct)

> Todos tienen opcode = `00000`, campos: `rs rt rd aux funct`

| Funct | Mnemo | Operación |
|-------|-------|-----------|
| `000000` | **SLL** | R[rd] = R[rt] << aux |
| `000001` | **SRL** | R[rd] = R[rt] >> aux (lógico) |
| `000010` | **SRA** | R[rd] = R[rt] >>> aux (aritmético) |
| `000011` | **SLLR** | R[rd] = R[rt] << R[rs][4:0] |
| `000100` | **SRLR** | R[rd] = R[rt] >> R[rs][4:0] (lógico) |
| `000101` | **SRAR** | R[rd] = R[rt] >>> R[rs][4:0] (aritm.) |
| `000110` | **CFS** | *no implementado* |
| `000111` | **CTS** | *no implementado* |
| `001000` | **AND** | R[rd] = R[rs] & R[rt] |
| `001001` | **OR** | R[rd] = R[rs] \| R[rt] |
| `001010` | **XOR** | R[rd] = R[rs] ⊕ R[rt] |
| `001011` | **NOR** | R[rd] = ¬(R[rs] \| R[rt]) |
| `001100` | **SLT** | R[rd] = (R[rs] < R[rt]) ? 1 : 0 |
| `001101` | **SLTU** | Igual pero sin signo |
| `001110` | **JR** | PC = R[rs] |
| `001111` | **JALR** | R[31] = PC+4; PC = R[rs] |
| `010000` | **LHX** | R[rt] = sign-ext( M[R[rs]+R[rd]](15:0) ) |
| `010001` | **LHUX** | R[rt] = zero-ext( M[R[rs]+R[rd]](15:0) ) |
| `010010` | **LBX** | sign-ext( M[R[rs]+R[rd]](7:0) ) |
| `010011` | **LBUX** | R[rt] = zero-ext( M[R[rs]+R[rd]](7:0) ) |
| `010100` | **LWX** | R[rt] = M[R[rs]+R[rd]] |
| `010101` | **MUL** | R[rd] = (R[rs] × R[rt])[31:0] |
| `010110` | **MULH** | R[rd] = (R[rs] × R[rt])[63:32] (c/signo) |
| `010111` | **MULHU** | R[rd] = (R[rs] × R[rt])[63:32] (s/signo) |
| `011000` | **DIV** | R[rd] = R[rs] / R[rt] |
| `011001` | **DIVU** | División sin signo |
| `011010` | **REST** | R[rd] = R[rs] % R[rt] |
| `011011` | **RESTU** | Resto sin signo |
| `011100` | **ADD** | R[rd] = R[rs] + R[rt] |
| `011101` | **SUB** | R[rd] = R[rs] − R[rt] |
| `100000` | **TRAP** | EPC = PC+4; PC = M[aux << 2] |
| `100001` | **RFT** | PC = EPC *(retorno de trap)* |

---

## 6. Estrategia para "Hello World"

El programa debe:

1. Cargar `0xFFFFFF00` en un registro (dirección de la UART)
2. Para cada carácter del mensaje `"Hello World\r\n"`:
   - Cargar el byte ASCII en otro registro
   - Ejecutar `SB` (store byte) apuntando a la UART
3. Loop infinito al final

### 6.1 Pseudo-ensamblador

```asm
; r1 = dirección UART (0xFFFFFF00)
LUI   r1, 0xFFFF      ; r1 = 0xFFFF0000
ORI   r1, r1, 0xFF00  ; r1 = 0xFFFFFF00

; Escribir 'H' (0x48)
ADDI  r2, r0, 0x48    ; r2 = 'H'
SB    r0, r2, 0       ; asumiendo modo (rs=base, rt=dato, imm=offset) — verificar encoding
; ... repetir para cada carácter ...

; Loop infinito
J     fin
```

> **Pendiente**: La codificación exacta de cada instrucción depende de confirmar con el profesor o examinar el código fuente del emulador cómo se mapean los campos `rs`, `rt`, `imm` en SB y ADDI. En particular:
> - `SB rs rt imm`: ¿M[addr] = R[rt](7:0) con addr = R[rs] + SignExtImm? Es decir, ¿rs es la base y rt el dato?
> - `ADDI rs rt imm`: R[rt] = R[rs] + SignExtImm, ¿el registro 0 es siempre cero? (como en MIPS)
>
> Esto se verifica en la primera sesión con el debugger.

### 6.2 Caracteres a enviar

```
H  e  l  l  o     W  o  r  l  d  \r \n
48 65 6C 6C 6F 20 57 6F 72 6C 64 0D 0A
```

### 6.3 Generar el binario

Una vez confirmada la codificación, se escribe un script (Python/C) que genere el `.bin` con los bytes de cada instrucción, y se carga con:

```bash
./rtm32 -d telnet -l hello.bin
```

O desde el debugger:

```
load hello.bin
continue
```

---

## 7. Traducción del mensaje del profesor

> _"Se ha publicado la primera versión estable de la máquina rtm32 en el drive. Se solicita con urgencia aprender a usarla."_

Hay que ponerse las pilas con esto ya.

> _"Es necesario tener Linux con xterm y picocom instalado. El binario funciona en cualquier lado, pero debe estar en el PATH o poner `./rtm32 -d telnet` desde el directorio donde está colocado."_

El binario `rtm32` ya lo tenemos en la carpeta. Se ejecuta con `./rtm32 -d telnet`.

> _"Adicionalmente es necesario telnet para conectarse al debugger y programar: `telnet localhost 4444`"_

Dos terminales: una corre el emulador, otra se conecta por telnet para debuggear.

> _"Si no recibo mensajes asumo que les ha ido muy bien y tienen todo andando."_

Si algo no funciona, hay que avisarle por Delmagro o WhatsApp. No quedarse callado.

> _"La RTM cuenta con una consola mediante UART mapeada en 0xFFFFFF00 (al pushear un caracter se muestra en consola, al apretar una tecla se lee del buffer circular de 16 bytes)."_

La E/S es por MMIO: escribís un byte en `0xFFFFFF00` y aparece en pantalla. Leés de ahí y obtenés la tecla presionada.

> _"Si tiene dudas sobre conceptos técnicos, usar IA para entenderlos mejor."_

Claramente nos habilita a usar herramientas como esta para entender la arquitectura.

---

## 8. Próximos pasos

1. Verificar que `./rtm32 -d telnet` levanta y que `telnet localhost 4444` conecta.
2. Usar comandos `step`, `registers`, `set`, `examine` para familiarizarse.
3. Confirmar encoding de instrucciones básicas (ADDI, SB, LUI, ORI) mediante prueba en el debugger.
4. Escribir el binario de Hello World y probarlo.
