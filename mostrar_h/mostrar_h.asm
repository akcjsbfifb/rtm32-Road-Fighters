; mostrar_h.asm — solo imprime 'h' en la UART

ADDI r1, r0, -256     ; r1 = 0xFFFFFF00 (UART)
ADDI r2, r0, 'h'      ; r2 = 'h'
SB    r1, r2, 0        ; M[r1+0] = 'h' → aparece en el xterm
J 0                    ; loop infinito
