; hello.asm — "Hello World\r\n" para RTM32
;
; Igual que mostrar_h.asm pero con los 12 caracteres completos.
; Misma técnica: ADDI con negativo para UART, ADDI+SB por cada char.

ADDI r1, r0, -256     ; r1 = 0xFFFFFF00 (UART)

ADDI r2, r0, 'H'      ; H
SB    r1, r2, 0

ADDI r2, r0, 'e'      ; e
SB    r1, r2, 0

ADDI r2, r0, 'l'      ; l
SB    r1, r2, 0

ADDI r2, r0, 'l'      ; l
SB    r1, r2, 0

ADDI r2, r0, 'o'      ; o
SB    r1, r2, 0

ADDI r2, r0, 0x20    ; espacio (no usar ' ', el parser lo rompe)
SB    r1, r2, 0

ADDI r2, r0, 'W'      ; W
SB    r1, r2, 0

ADDI r2, r0, 'o'      ; o
SB    r1, r2, 0

ADDI r2, r0, 'r'      ; r
SB    r1, r2, 0

ADDI r2, r0, 'l'      ; l
SB    r1, r2, 0

ADDI r2, r0, 'd'      ; d
SB    r1, r2, 0

ADDI r2, r0, '\r'     ; carriage return
SB    r1, r2, 0

ADDI r2, r0, '\n'     ; newline
SB    r1, r2, 0

J 27                   ; loop infinito sobre sí mismo (no reimprime)
