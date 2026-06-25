# RTM32 — Emulador de procesador didáctico

Emulador de un CPU RISC de 32 bits con debugger remoto vía telnet y UART por MMIO.

## Requisitos

```bash
sudo pacman -S xterm telnet picocom
```

## Arranque rápido (3 terminales)

| Terminal | Comando | Qué hace |
|----------|---------|----------|
| 1 | `./rtm32 -d telnet` | Emulador + xterm de UART |
| 2 | `telnet localhost 4444` | Debugger (step, registers, load...) |
| 3 | Tu editor | Escribir .asm, ensamblar |

```bash
# Terminal 2 — comandos básicos del debugger
load hello_world/hello.bin    # carga programa
step                          # ejecuta 1 instrucción
registers                     # ve los 32 registros
continue                      # ejecuta sin parar
examine 0x00000000            # ve memoria en hex
```

## Guías (leer en este orden)

| # | Archivo | Contenido |
|---|---------|-----------|
| 1 | [`RTM32-guia.md`](RTM32-guia.md) | ISA completa, setup, comandos debugger |
| 2 | [`mostrar_h/explicacion_mostrar_h.md`](mostrar_h/explicacion_mostrar_h.md) | Cómo funciona ADDI y SB, ver binario en hex |

## Herramienta principal: `asm.py`

Ensamblador/desensamblador para RTM32.

```bash
# Ver ayuda (todos los opcodes soportados)
python3 asm.py

# Ensamblar
python3 asm.py hello_world/hello.asm

# Desensamblar un .bin
python3 asm.py --dis hello_world/hello.bin

# Ensamblar con nombre de salida personalizado
python3 asm.py mi_programa.asm mi_programa.bin
```

### Sintaxis .asm

```asm
; comentario
ADDI r1, r0, -256     ; r1 = 0xFFFFFF00
ADDI r2, r0, 'H'      ; caracteres entre comillas
ADDI r2, r0, 0x20     ; hex para espacio (no usar ' ')
SB    r1, r2, 0        ; store byte en UART
J 27                   ; salto absoluto (en palabras)
```

Soporta 24 opcodes I-type y J-type (ver `python3 asm.py`). R-type no implementado aún.

## Ejemplos

| Carpeta | Programa | Descripción |
|---------|----------|-------------|
| [`mostrar_h/`](mostrar_h/) | `mostrar_h.bin` | Imprime solo 'h' (3 instrucciones) |
| [`hello_world/`](hello_world/) | `hello.bin` | Imprime "Hello World\r\n" (28 instrucciones) |

## Ver binarios en hex

```bash
# payload solo (sin header), 4 bytes por línea = 1 instrucción
od -A x -t x1 -w4 -j60 hello_world/hello.bin

# lo mismo pero con decodificación
python3 asm.py --dis hello_world/hello.bin
```

## Utilidades

```bash
pkill xterm   # cerrar terminales abiertas por el emulador
```
