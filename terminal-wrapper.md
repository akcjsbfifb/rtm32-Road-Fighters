# Wrapper para que rtm32 abra tu terminal favorita

El emulador `rtm32` abre `xterm` para la UART. Con este wrapper redirigís esa llamada a la terminal que vos quieras.

## Paso a paso

### 1. Averiguá el comando de tu terminal

| Terminal | Comando |
|----------|---------|
| Ghostty | `ghostty` |
| GNOME Terminal | `gnome-terminal` |
| Konsole (KDE) | `konsole` |
| Kitty | `kitty` |
| Alacritty | `alacritty` |
| WezTerm | `wezterm` |
| Terminator | `terminator` |
| Xfce Terminal | `xfce4-terminal` |
| LXTerminal | `lxterminal` |

Si no sabés cuál tenés, ejecutá en la terminal:

```bash
echo $TERM
```

O buscá entre los comandos disponibles:

```bash
which ghostty gnome-terminal konsole kitty alacritty wezterm 2>/dev/null
```

### 2. Crear el wrapper

```bash
mkdir -p ~/.local/bin
```

Reemplazá `ghostty` por el nombre de tu terminal:

```bash
cat > ~/.local/bin/xterm << 'EOF'
#!/bin/bash
exec ghostty "$@"
EOF
chmod +x ~/.local/bin/xterm
```

### 3. Asegurarse de que `~/.local/bin` esté en el PATH

Probá si ya está:

```bash
echo $PATH | grep -o '.local/bin'
```

Si no aparece nada, agregalo al final de tu `~/.bashrc` (o `~/.zshrc` si usás zsh):

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
exec $SHELL
```

### 4. Probar

```bash
which xterm
```

Tiene que mostrar `/home/tuusuario/.local/bin/xterm`.

### 5. Ejecutar el emulador

```bash
cd ~/Documentos/rtm32-Road-Fighters
./rtm32 -d telnet
```

Ahora debería abrirse **tu terminal** en vez de xterm.

---

## Notas

- El wrapper no se pushea al repo. Está solo en tu `~/.local/bin/`.
- Si tu terminal necesita argumentos especiales para ejecutar un comando (ej: `-e` en algunas), cambiá la línea `exec` por algo como `exec gnome-terminal -- "$@"`.
- Cada integrante del grupo tiene que hacer este paso en su máquina.
