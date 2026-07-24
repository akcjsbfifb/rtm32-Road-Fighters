# Manual de Usuario - RTM32 Computer v1.0

Total pages: 79

---

## Page 1

Arquitectura y Especificaciones
Sistema RTM32
Manual del Usuario y Especificación de
Arquitectura
Diseñado para alta velocidad de ejecución y modularidad.
Alejandro Rodriguez Costello

---

## Page 2

Universidad Nacional de Rosario
Instituto Politécnico Superior
Cátedra de Arquitectura de Computadoras
Documento: Manual de Usuario y Datos Técnicos
Versión: 0.1.5-RC (lista para futuras expansiones)
Fecha: 27 de mayo de 2026
Contacto: acrod@ips.edu.ar
Licencia y Derechos de Autor
© 2026 Alejandro Rodriguez Costello.
Este documento se publica bajo la licencia Creative Commons
Atribución-NoComercial-CompartirIgual 4.0 Internacional (CC BY-NC-SA 4.0).
Para ver una copia de esta licencia, visite http://creativecommons.org/licenses/by-nc-sa/4.0/.
i

---

## Page 3

Parte I
Arquitectura del Sistema RTM32
1

---

## Page 4

1. Introducción
1.1. Generalidades
LaaplicaciónRTM32esunemuladordelaarquitecturaRISCde32bitsTM32optimizada
nativamentemediantetécnicasdeenlazadodirectoestático(DirectThreadedCode)einlining
agresivo de memoria para priorizar la velocidad de ejecución.
Este manual proporciona el modelo de programación a nivel de sistema y de uso para
aplicación. El propósito principal de esta documentación es guiar a los desarrolladores en la
escritura de software a nivel ensamblador (assembly), la construcción de boot ROMs y la
posibilidad de portar un compilador de un lenguaje de alto nivel (HLL) como Oberon. Este
texto establece las convenciones de software, manejo de la memoria y los requisitos para la
utilización de registros.
El alcance de este documento se limita estrictamente a la interfaz arquitectónica visible
por software y no profundiza en la mecánica interna del emulador. En su lugar, cubre los
límites estructurales del conjunto de instrucciones, los 32 registros de propósito general y
7 de propósito especial, la jerarquía de memoria y los mecanismos formales de manejo de
excepciones e interrupciones por hardware.
El emulador equilibra claridad educativa con una ejecución veloz diseñada para tener
rendimiento en la ejecución de sistemas operativos, aplicaciones de consola y emulación de
videojuegos, en lugar de una simulación precisa de ciclo (cycle-accurate physical simulation).
Componentescomplejosdehardwarecomolaunidaddemanejodememoria(MMU)paginada
seomitenenfavorderegionesdememoriaplanasalineadas.Losestadosinternossecondensan
enrepresentacionesdirectasmedianteflags,resultandoenunmodelodeejecuciónsimplificado
y fácil de entender para programadores de compiladores y estudiantes de computación por
igual.
Esta arquitectura del emulador está diseñada para ejecutar un stack de software especia-
lizado. El despliegue inicial se centra en el diseño de boot ROMs monolíticas de bajo nivel
para configurar el sistema (first stage) y posibilitar la carga y ejecución de un bloque de
código en almacenamiento externo (boot loader) para que se encargue de cargar el resto del
sistema (second stage). Uno de los objetivos a largo plazo es portar completamente el entorno
del sistema operativo Oberon y su lenguaje compilador orientado a objectos, adaptando el
concepto de estación de trabajo a una estructura de aplicación de consola liviana y de alto
rendimiento.
1.2. Arquitectura del emulador
La arquitectura RTM32 se compone de tres software de aplicación llamados: RTM32, el
emulador de la máquina, RTM32AS el compilador cruzado (cross compiler) del lenguaje en-
samblador de la arquitectura TM32 y una utilidad llamada RTM32FMT para administrar los
dispositivos de masa. La máquina está compuesta por una CPU, un manejador de interrup-
ciones, un bus de 32 bits unificado, como se observa en la figura 1.1 , RAM, ROM y distintos
periféricos optativos.
2

---

## Page 5

Capítulo 1. Introducción Manual de Usuario RTM32
Interrupt IRQ0
CPU
Controller ...
STX4
LAPIC IRQ15
32-Bit Unifying System Bus
User Space (RAM) Kernel MMIO Peripherals
Base: 0x00000000 Space Base: 0xFFFFF000
Limit: < Privilege Bound (RAM) (Dynamic Table)
Figura 1.1: 32-Bit Unifying System Bus Architecture.
Su configuración se realiza a través de un archivo descriptivo y switchs opcionales que se
pueden desplegar en la línea de comando como se describe en el Capítulo 2.
Para avanzar en el desarrollo de aplicaciones se dispone del compiladorRTM32AS descripto
enelCapítulo9.1,quegeneracódigoobjectoejecutableenelemulador.Dichoobjetosepuede
cargar desde la inicialización o desde el modo depurador (debug) descripto en el Capítulo 10.
La utilidad RTM32FMT nos permite crear un archivo en el host que represente una unidad
de almacenamiento como un disco, formatearlo y editar su contenido en forma offline para
anexarlo al controlador de dispositivo correspondiente durante la inicialización (disc attach).
El modelo de programación cambia entre dos posibles estados con diferentes privilegios
(priviledge states):
Modo Kernel: o privilegiado (priviledge), con acceso completo al ISA y a la memoria
mapeada disponible.
Modo User: restringido a ciertas instrucciones y regiones de la memoria mediante
excepciones (traps).
La representación de datos en todos los buses, espacios de memoria y regiones de acceso
a los dispositivos es estrictamente Little-Endian.
1.3. Procesador (STX4)
El procesador central del sistema RTM32 es el STX4, un procesador RISC de propósito
generalde32bitsqueimplementalaarquitecturadeconjuntodeinstrucciones(ISA)RTM32.
Elprocesadorejecutaunúnicoflujodeinstruccionessobreunespaciodedireccionesunificado
de 32 bits, compartido por el código ejecutable, los datos y los dispositivos de entrada/salida
mapeados en memoria (MMIO).
El STX4 es un procesador de un solo núcleo (single-core) con ejecución en orden (in-
order) y emisión simple (single-issue). Las instrucciones se obtienen, decodifican y ejecutan
secuencialmente, proporcionando un comportamiento arquitectónico determinista adecuado
para programación de sistemas, desarrollo de compiladores y fines educativos.
1.3. Procesador (STX4) 3

---

## Page 6

Capítulo 1. Introducción Manual de Usuario RTM32
La arquitectura sigue el modelo clásico load/store, en el cual todas las operaciones arit-
méticasylógicasserealizanexclusivamentesobreregistros,mientrasqueelaccesoamemoria
se efectúa únicamente mediante instrucciones explícitas de carga y almacenamiento.
El estado arquitectónico visible por software está compuesto por treinta y dos registros
de propósito general, cinco registros de propósito especial, el estado de privilegio actual y la
información de control necesaria para soportar excepciones, interrupciones y transferencias
de control. Estos elementos se describen en detalle en los capítulos siguientes.
La arquitectura no define cachés de instrucciones ni de datos visibles para el software.
Todas las operaciones de memoria se realizan sobre un único espacio de direcciones unificado,
independientemente de la implementación interna del emulador.
Las instrucciones son de ancho fijo (32 bits), estrictamente alineadas a límites de 4 bytes,
y se cargan (fetch) secuencialmente mediante el Program Counter (pc).
1.4. Memoria principal
El procesador STX4 opera sobre un espacio de direcciones lineal de 32 bits, proporcio-
nando un total de 232 bytes (4 GiB) de espacio direccionable. Este espacio constituye una
vista arquitectónica uniforme utilizada para acceder tanto a memoria como a dispositivos de
entrada/salida mapeados en memoria (MMIO).
La cantidad de memoria física instalada no está determinada por la arquitectura. Tanto
la capacidad de la memoria RAM como la de la memoria ROM son parámetros configurables
del emulador y pueden variar entre distintas configuraciones del sistema sin modificar el ISA
ni el modelo de programación.
La memoria RAM se divide lógicamente en dos regiones independientes: una región des-
tinada al espacio de usuario (User Space) y otra destinada al espacio privilegiado (Kernel
Space). Ambas regiones poseen rangos de direcciones distintos dentro del espacio de direccio-
nes de 32 bits y pueden configurarse de manera independiente durante la inicialización del
sistema.
La memoria ROM contiene el código de inicialización del sistema y la tabla de vectores
utilizada durante el proceso de arranque, las excepciones y las interrupciones. Su contenido
se carga al iniciar el emulador y permanece inmutable durante toda la ejecución del sistema,
ya que la arquitectura no define mecanismos para su reprogramación mediante software.
Las regiones del espacio de direcciones que no contienen memoria ni dispositivos registra-
dos se consideran direcciones no mapeadas. Cualquier acceso a dichas regiones produce una
excepción arquitectónica de acceso inválido, cuyo comportamiento se describe en el capítulo
dedicado al manejo de excepciones.
1.4.1. Segmentación del espacio de memoria
El subsistema de memoria maneja la decodificación de direcciones dividiendo su espacio
en dos grandes regiones basadas en el valor del más significativo (bit 31). A la dirección
límite 0x80000000 se la conoce como límite privilegiado (Privilege Boundary). Este límite
está cableado y no se puede cambiar. Las regiones son:
UserSpace(0x00000000a0x7FFFFFFF):Accesibleuniversalmenteporambosmodosde
ejecución: Kernel Mode y User Mode. Las direcciones dentro de este segmento mapean
1.4. Memoria principal 4

---

## Page 7

Capítulo 1. Introducción Manual de Usuario RTM32
directamente a la RAM física volátil del sistema disponible.
Kernel Space (0x80000000 a 0xFFFFFFFF): El acceso está estrictamente limitado a la
ejecución en Kernel mode. Cualquier intento de un programa dentro de este espacio de
direcciones en User mode o de emitir una instrucción load o store que acceda dentro de
este rango dispara inmediatamente al procesador a un trap de excepción. Esta región
a su vez se subdivide en:
• Kernel RAM Mapping: región de la RAM mapeada a partir del inicio del Kernel
Space y que se extiende hasta el comienzo de la ROM.
• BootROMMapping:ElCold Boot Vectordelsistemaresideenlapartesuperior
del kernel space en 0xF0000000.
• Memory-Mapped I/O (MMIO): La comunicación con hardware depende entera-
mente de bloques periféricos independientes registrados dinámicamente en el bus
del sistema. Los registros de control de hardware por defecto se agrupan dentro
del bloque superior comenzando en 0xFFFFF000.
Por simplicidad, las reglas de alineación de datos se aplican estrictamente. No hay soporte
por hardware para accesos desalineados (unaligned access).
Alineaciónestrictade16bits:Lasoperacionesconhalfwords(lh,lhx,lhu,lhux,sh)re-
quierenqueladireccióndememoriadestinoseamúltiplode2(elbitmenossignificativo
debe ser 0).
Alineación estricta de 32 bits: Las operaciones con words (lw, lwx, lh) y los fetch de
instrucciones mediante el pc requieren direcciones múltiplo de 4 (los dos bits menos
significativos deben ser 00).
Enforcement de alineación: Cualquier operación de lectura o escritura no alineada viola
el cumplimiento arquitectónico, detiene el flujo actual de ejecuón y dispara un trap de
hardware ALIGNMENT_FAULT de forma inmediata.
Precisión extendida: La ejecución aritmética opera nativamente sobre registros de 32
bits. La precisión extendida de 64 bits se asigna exclusivamente, y es modificada por,
las operaciones de multiplicación (mul, mulh, mulhu) y división (div, divu, rem, remu)
de hardware de enteros.
1.4.2. Controlador de interrupciones
El sistema RTM32 incorpora un controlador local de interrupciones denominado LAPIC
(Little Advanced Programmable Interrupt Controller),unaimplementacióndelaarquitectura
de controlador de interrupciones IIC (Intermediate Interrupt Controller).
El controlador local de interrupciones LAPIC es el componente responsable de arbitrar
todas las solicitudes de interrupción por hardware generadas por los dispositivos del sistema
y presentarlas al procesador STX4 mediante una interfaz de interrupción única.
El controlador admite hasta dieciséis líneas físicas de interrupción (IRQ0–IRQ15), cada
una configurable de manera independiente. Para cada canal es posible definir el modo de
disparo, la polaridad de la señal, el nivel de prioridad, el vector de interrupción asociado y
su estado de habilitación.
Cuando múltiples solicitudes se encuentran pendientes simultáneamente, el LAPIC re-
suelve automáticamente cuál debe ser atendida utilizando un mecanismo de arbitraje por
1.4. Memoria principal 5

---

## Page 8

Capítulo 1. Introducción Manual de Usuario RTM32
prioridad implementado completamente en hardware. El controlador también mantiene el
estado de las interrupciones actualmente activas, permitiendo la ejecución anidada de rutinas
de servicio cuando una solicitud de mayor prioridad interrumpe a otra de menor prioridad.
El LAPIC forma parte del espacio de dispositivos mapeados en memoria (MMIO), desde
dondeelsoftwarepuedeconfigurarsuscanalesycontrolarelciclodevidadelasinterrupciones
mediante un conjunto reducido de registros de control. La descripción completa de la interfaz
deprogramaciónydelmodelodeejecuciónsedesarrollaenelcapítulodedicadoalsubsistema
de interrupciones.
Las excepciones arquitectónicas generadas por la CPU, como instrucciones inválidas, ac-
cesos desalineados o violaciones de memoria, no atraviesan el controlador de interrupciones.
Estas condiciones son detectadas directamente por el procesador y despachadas mediante la
tabla de vectores de excepción correspondiente.
1.4.3. Notación general
Los valores hexadecimales se designan explícitamente usando el prefijo estándar 0x (ej.,
0xF0000000).
Los valores binarios se prefijan con 0b (ej., 0b01010).
Los registros se representan usando el token $ acompañado de su índice físico o alias
de aplicación (ej., $0 o $z).
1.4. Memoria principal 6

---

## Page 9

2. Configuración del Emulador
El emulador RTM32 soporta dos mecanismos de configuración complementarios:
1. Archivo de configuración (TOML)
2. Argumentos de línea de comandos
El archivo de configuración por defecto, rtm32.toml, es opcional. Cuando está presente,
se carga automáticamente desde el directorio de trabajo del emulador. El archivo de con-
figuración puede definir cualquier opción que también esté disponible como argumento de
línea de comandos, así como ajustes adicionales del emulador y del hardware virtual que no
se pueden especificar desde la línea de comandos. Estos ajustes específicos de hardware se
describen en una sección dedicada de este documento.
Los argumentos de línea de comandos siempre tienen precedencia sobre los valores definidos
en el archivo de configuración. Esto incluye la opción utilizada para especificar un archivo
de configuración alternativo, lo que permite reemplazar el archivo rtm32.toml por defecto
al inicio. Si no se especifica una opción de configuración a través de ninguno de los dos
mecanismos, el emulador utiliza su valor por defecto predefinido. Las opciones que requieren
una entrada explícita del usuario se validan durante el inicio, y los valores de configuración
inválidos dan como resultado un error de inicialización.
2.1. Orden de búsqueda de la configuración
Alinicio,elemuladorlocalizaelarchivodeconfiguracióndeacuerdoconelsiguienteorden
de búsqueda.
Prioridad Ubicación Descripción
1 Archivodeconfiguraciónespecifica- Utiliza el archivo de configuración solicitado
do por –config <file> explícitamente.
2 ./rtm32.toml Utiliza el archivo de configuración por defecto
ubicado en el directorio de trabajo actual.
3 Valores por defecto integrados Se utilizan cuando no se encuentra ningún ar-
chivo de configuración.
El archivo de configuración por defecto es opcional. Su ausencia no se considera un error, y
el emulador continúa la inicialización utilizando sus valores por defecto integrados.
@ NOTA
El soporte nativo para la Especificación de Directorio Base XDG está planificado para
una futura versión. La implementación actual busca intencionalmente solo en el di-
rectorio de trabajo actual para simplificar la distribución y la ejecución en entornos
educativos.
7

---

## Page 10

Capítulo 2. Configuración del Emulador Manual de Usuario RTM32
2.2. Precedencia de configuración
Cuando una opción de configuración está definida por múltiples fuentes, el emulador
resuelve el valor final de acuerdo con las siguientes reglas de precedencia, ordenadas por
orden de prioridad donde la primera es las más alta y la última la más baja.
1. Argumentos de línea de comandos
2. Archivo de configuración
3. Valores por defecto integrados
En consecuencia, cada opción de línea de comandos sobrescribe el valor correspondiente defi-
nido en el archivo de configuración. Esto incluye la opción –config, que permite seleccionar
un archivo de configuración alternativo antes de que se procese cualquier otro valor de con-
figuración. Si una opción de configuración se omite tanto de la línea de comandos como del
archivo de configuración, el emulador utiliza automáticamente su valor por defecto predefini-
do. Los valores de configuración se validan durante la inicialización. Los valores inválidos o
inconsistentes impiden que el emulador se inicie y se informan como errores de configuración.
2.3. Argumentos de línea de comandos
Los argumentos de línea de comandos proporcionan un mecanismo conveniente para so-
brescribir la configuración del emulador al inicio sin modificar el archivo de configuración.
Cada opción de línea de comandos está disponible tanto en una forma larga (–config) como
abreviada (-c). A menos que se indique lo contrario, ambas formas son funcionalmente equi-
valentes y pueden utilizarse indistintamente. Los argumentos de línea de comandos siempre
tienen precedencia sobre los valores definidos en el archivo de configuración. Cuando una
opción se especifica varias veces, la última aparición determina el valor efectivo. La mayoría
delasopcionessiguenunasintaxiscomúndiseñadaparaproporcionarunainterfazdeusuario
consistente en todo el emulador.
Sintaxis Descripción
–switch=LIST[,OPTION...] Formato general del argumento.
LIST Unoomásvalorespredefinidosaceptadosporelargumento.Depen-
diendo de la opción, se puede especificar un solo valor o múltiples
valores separados por comas.
OPTION Parámetro opcional expresado como un par key=value que modi-
fica el comportamiento de los valores seleccionados. Los múltiples
parámetros se separan por comas.
Ejemplos:
−−log=console
−−log=console,file
−−log=console,file,level=warning,color=false
Cuando un argumento soporta múltiples valores, estos se especifican como una lista separada
por comas. El orden de los valores no es significativo. Los parámetros opcionales siempre
siguen a la lista de valores y se expresan como pares key=value. Las siguientes secciones des-
criben cada argumento de línea de comandos, sus valores aceptados, parámetros opcionales,
comportamiento por defecto y su forma abreviada correspondiente.
2.2. Precedencia de configuración 8

---

## Page 11

Capítulo 2. Configuración del Emulador Manual de Usuario RTM32
2.3.1. –debug, -d
Habilita el debugger del emulador y selecciona la interfaz de comunicación utilizada para
interactuar con la sesión de depuración. El debugger está deshabilitado por defecto y debe
habilitarse explícitamente al inicio.
Gramática
−−debug=MODE[,OPTION...]
Elemento Descripción
MODE Selecciona la interfaz del debugger.
OPTION Parámetros de configuración opcionales para la interfaz seleccionada.
Modos
Modo Descripción
console Inicia el debugger interactivo utilizando los flujos estándar de entrada y salida.
telnet Inicia el debugger como un servidor Telnet y espera la conexión de un cliente remoto.
Opciones
Las siguientes opciones se aplican al modo telnet.
Opción Descripción Por defecto
port=<n> Puerto TCP utilizado por el servidor Telnet. 4444
Comportamiento por defecto
Eldebuggerestádeshabilitadoamenosqueseespecifiqueexplícitamentelaopción–debug.
Elemuladorrequiereunafuentedeejecuciónalinicio.Estapuedeproporcionarsehabilitando
el debugger, cargando una imagen de ROM o cargando una imagen de RAM. Al cargar una
imagen, se utilizan las direcciones de carga y ejecución embebidas a menos que se sobrescri-
ban explícitamente mediante las opciones de línea de comandos correspondientes. Si no se
especifica ninguna fuente de ejecución, el emulador finaliza con un error de configuración.
Ejemplos
−−debug=console
Inicia el debugger interactivo utilizando la terminal.
−−debug=telnet
Inicia el debugger de Telnet en el puerto por defecto (4444).
−−debug=telnet,port=4444
Inicia el debugger de Telnet utilizando el puerto TCP especificado.
2.3. Argumentos de línea de comandos 9

---

## Page 12

Capítulo 2. Configuración del Emulador Manual de Usuario RTM32
2.3.2. –load, -l
Cargaunaimagenbinariaenlamemoriadelemuladorantesdelaejecución.Pordefecto,la
imagensecargaenladirecciónespecificadaporsuformatodearchivo.Sepuedeproporcionar
una dirección opcional para sobrescribir la dirección de carga embebida y reubicar la imagen
en cualquier dirección válida y correctamente alineada dentro del espacio de direcciones del
emulador.
Gramática
−−load=FILE[,OPTION...]
Elemento Descripción
FILE Ruta a la imagen binaria que se va a cargar.
OPTION Parámetros opcionales que modifican el comportamiento de carga.
Opciones
Opción Descripción Por defecto
address=<addr> Sobrescribe ladirección decarga dela Dirección embebida en la imagen
imagen.
Comportamiento por defecto
La imagen se carga antes de que el emulador comience la ejecución. Cuando no se especifica
ninguna dirección de carga, se utiliza la dirección embebida en la imagen. Si se proporciona
una sobrescritura, la imagen se reubica en la dirección especificada. La dirección específica
debe hacer referencia a una ubicación válida y correctamente alineada dentro del espacio de
direccionesdelemulador.Lasdireccionesinválidasseinformancomoerroresdeconfiguración.
Ejemplos
−−load=test.bin
Carga la imagen utilizando la dirección embebida en el archivo.
−−load=test.bin,address=0x2000
Carga la imagen en la dirección 0x2000, sobrescribiendo la dirección embebida en el archivo.
2.3.3. –log, -g
Configura el subsistema de logs del emulador. Se pueden habilitar uno o más destinos de
log simultáneamente. Todos los mensajes de log generados se envían a los destinos seleccio-
nados utilizando el mismo nivel de log y opciones de formato.
2.3. Argumentos de línea de comandos 10

---

## Page 13

Capítulo 2. Configuración del Emulador Manual de Usuario RTM32
Gramática
−−log=DESTINATION[,OPTION...]
Elemento Descripción
DESTINATION Uno o más destinos de log. Los múltiples valores se separan por comas.
OPTION Parámetros opcionales que controlan el comportamiento de los logs.
Destinos
Destino Descripción
display Escribe los mensajes de log en la salida estándar.
file Escribe los mensajes de log en un archivo de log.
Opciones
Opción Descripción Por defecto
file=<path> Rutadelarchivodelogdesalida.Requerido —
cuando se selecciona el destino file.
level=debug|info|warning|error Nivel mínimo de severidad a registrar. info
color=true|false Habilitaodeshabilitalassecuenciasdecolor true
ANSI para la salida de la terminal.
Los destinos seleccionados comparten el mismo nivel de log y opciones de formato.
Comportamiento por defecto
El registro de logs está deshabilitado a menos que se especifique explícitamente la opción
–log. Cuando se seleccionan múltiples destinos, cada mensaje de log se envía a cada uno de
los destinos seleccionados.
Ejemplos
−−log=file,file=emu.log,level=debug
Escribe todos los mensajes de log con severidad debug o superior en el archivo emu.log.
−−log=display,level=warning,color=false
MuestralosmensajesdelogconseveridadwarningosuperiorenlaterminalsincoloresANSI.
−−log=display,file,file=emu.log,level=info
Escribe el mismo flujo de log simultáneamente en la terminal y en emu.log.
2.3. Argumentos de línea de comandos 11

---

## Page 14

Capítulo 2. Configuración del Emulador Manual de Usuario RTM32
2.3.4. –exec, -e
Establece la dirección de ejecución inicial de la CPU virtual. Por defecto, la ejecución
comienza en el punto de entrada definido por la imagen cargada. Se puede proporcionar una
dirección de ejecución explícita para sobrescribir el punto de entrada embebido y comenzar
la ejecución desde cualquier dirección válida y correctamente alineada dentro del espacio de
direcciones del emulador.
Gramática
−−exec=ADDRESS[,OPTION...]
Elemento Descripción
ADDRESS Dirección de ejecución inicial.
OPTION Parámetros opcionales que controlan el comportamiento de la ejecución.
Opciones
Opción Descripción Por defecto
steps=<n> Cantidad máxima de instrucciones a ejecutar antes de devolver el Ilimitado
control.
Comportamiento por defecto
Cuando no se especifica la opción –exec, el emulador comienza la ejecución en el punto
de entrada definido por la imagen cargada. Si se identifica una dirección de ejecución, esta
sobrescribe el punto de entrada de la imagen. La dirección específica debe hacer referencia a
unaubicaciónválidaycorrectamentealineadadentrodelespaciodedireccionesdelemulador.
Las direcciones inválidas se informan como errores de configuración.
Ejemplos
−−exec=0x1000
Inicia la ejecución en la dirección 0x1000.
−−exec=0x1000,steps=100
Inicia la ejecución en la dirección 0x1000 y ejecuta como máximo 100 instrucciones antes de
devolver el control.
2.3.5. –rom, -r
Carga una imagen de ROM en el emulador antes de la secuencia de reset del procesador.
La imagen de ROM contiene toda la información requerida por el emulador, incluyendo la
tabla de vectores de interrupción y el punto de entrada de reset. Su ubicación dentro del
espacio de direcciones del emulador está fijada por la arquitectura del sistema y no se puede
sobrescribir.
2.3. Argumentos de línea de comandos 12

---

## Page 15

Capítulo 2. Configuración del Emulador Manual de Usuario RTM32
Gramática
−−rom=FILE
Elemento Descripción
FILE Ruta a la imagen de ROM.
Comportamiento por defecto
No se carga ninguna imagen de ROM a menos que se especifique explícitamente la opción
–rom. Cuando está presente, la imagen de ROM se mapea en la región de ROM antes de que
comience la secuencia de reset del procesador. El procesador luego realiza su inicialización
de reset normal y comienza la ejecución desde el vector de reset contenido en la imagen de
ROM. La dirección de ejecución inicial puede ser sobrescrita por la opción –exec para fines
de desarrollo y depuración.
Ejemplos
−−rom=boot.bin
Carga la imagen de ROM boot.bin antes de iniciar el emulador.
2.3.6. –kernel, -k
Especifica el tamaño de la región de memoria del kernel. La región de memoria del kernel
estávinculadaalespaciodedireccionesdelkernelyestádisponibleparasoftwareprivilegiado.
Gramática
−−kernel=SIZE
Elemento Descripción
SIZE Tamaño de la región de memoria del kernel. Los sufijos soportados son K, M y G.
Comportamiento por defecto
Noseasignamemoriadelkernelamenosqueseespecifiqueexplícitamentelaopción–kernel.
El tamaño especificado debe estar alineado por página (4 KiB) y no debe exceder los 2 MiB.
Las restricciones de arquitectura adicionales se describen en la sección Mapa de memoria.
Ejemplos
−−kernel=64K
Asigna una región de memoria del kernel de 64 KiB.
2.3. Argumentos de línea de comandos 13

---

## Page 16

Capítulo 2. Configuración del Emulador Manual de Usuario RTM32
2.3.7. –memory, -m
Especificaeltamañodelaregióndememoriadeusuario.Laregióndememoriadeusuario
estávinculadaalespaciodedireccionesdeusuarioyproporcionalaRAMprincipaldisponible
para las aplicaciones de usuario.
Gramática
−−memory=SIZE
Elemento Descripción
SIZE Tamaño de la región de memoria de usuario. Los sufijos soportados son K, M y G.
Comportamiento por defecto
Si se omite la opción, se asigna una región de memoria de usuario de 4 KiB. El tamaño espe-
cificadodebeestaralineadoporpágina(4KiB)ynodebeexcederlos2MiB.Lasrestricciones
de arquitectura adicionales se describen en la sección Mapa de memoria.
Ejemplos
−−memory=256K
Asigna una región de memoria de usuario de 256 KiB.
2.3.8. –config, -c
Especificaelarchivodeconfiguraciónquesecargarádurantelainicializacióndelemulador.
ElarchivodeconfiguracióndebecontenerunasintaxisTOMLválida.Laextensióndelnombre
de archivo no es significativa.
Gramática
−−config=FILE
Elemento Descripción
FILE Ruta al archivo de configuración.
Comportamiento por defecto
Si no se especifica la opción –config, el emulador busca rtm32.toml en el directorio de
trabajo actual. Si el archivo de configuración especificado no se puede abrir o contiene una
sintaxis TOML inválida, el emulador finaliza con un error de configuración.
2.3. Argumentos de línea de comandos 14

---

## Page 17

Capítulo 2. Configuración del Emulador Manual de Usuario RTM32
Ejemplos
−−config=board.cfg
Carga la configuración desde board.cfg. Aunque el archivo utiliza una extensión .cfg, su
contenido debe cumplir con la especificación TOML.
2.3. Argumentos de línea de comandos 15

---

## Page 18

Parte II
Arquitectura del procesador STX4
16

---

## Page 19

3. El procesador STX4
3.1. Modelo de Ejecución
LaarquitecturaTM32estádiseñadabajounparadigmadetipoRISC(Reduced Instruction
Set Computer) con una longitud de palabra de 32 bits. Desde la perspectiva del programa-
dor y del usuario del emulador, el procesador se comporta bajo un modelo de ejecución
secuencial y de ciclo único (single-cycle).
Estoimplicaquecadainstrucciónsebusca,decodifica,ejecutayretirademaneraatómica
antes de comenzar el procesamiento de la siguiente instrucción. La semántica de ejecución
garantiza que el estado de la máquina se actualiza de forma síncrona al final de cada ciclo
de instrucción, eliminando complejidades visibles al software tales como riesgos de datos
(data hazards), riesgos de control (control hazards) o la necesidad de ranuras de retardo de
salto (branch delay slots). La codificación de las instrucciones se clasifica en tres formatos
principales R, I y J detallados en el Capítulo 6.
El procesador denominado STX4 es una implementación de la arquitectura TM32.
3.2. Estado Arquitectónico
El estado arquitectónico representa el conjunto mínimo de elementos de almacenamiento
(registros y memoria) que definen unívocamente la situación del sistema en un instante de
tiempo dado. En el procesador STX4, este estado está constituido por:
1. Banco de Registros de Propósito General (GPR): Un conjunto de registros de
32 bits de ancho encargados de almacenar operandos y resultados intermedios.
2. Program Counter (PC): Registro de 32 bits que apunta a la dirección de memoria
de la instrucción en curso.
3. Banco de Registros de Funciones Especiales (SFR): Un espacio de almacena-
miento interno destinado a la configuración, el control y la gestión de excepciones y
estado del procesador.
4. Memoria Principal (M): Un espacio físico direccionable por bytes donde residen las
instrucciones y los datos del sistema.
3.3. Banco de Registros
La arquitectura RISC ortogonal TM32 de 32 bits cuenta con un banco de 32 registros de
propósito general (GPR) para el usuario numerados de 0 a 31 como se observa en la tabla 3.1
donde se exhibe la designación mnemotécnica (mnemonic) usada por el ensamblador (colum-
na ABI) y el propósito o convención que deberá seguir el programador y/o la herramienta de
desarrollo que haga uso de los mismos.
El registro cero ($zero o $0) siempre contiene el valor 0. Está cableado en el hardware,
así que no se puede modificar, aunque puede usarse como destino en cualquier instrucción.
17

---

## Page 20

Capítulo 3. El procesador STX4 Manual de Usuario RTM32
Reg. ABI Convención
$0 $zero Cableado a cero1
$1 $ra Dirección de retorno
$2,$3 $k0,$k1 Reservados
$4,...,$7 $lr0,...,$lr3 Registros de enlace
$8,...,$13 $a0,...,$a5 Argumentos de función
$14,...,$19 $t0,...,$t5 Temporarios
$20,...,$27 $s0,...,$s7 Almacenablesl
$28 $fp Puntero de marco
$29 $gp Puntero global
$30 $sp Puntero de pila
$31 $at Ensamblador
Tabla 3.1: Uso y convención de los registros RTM32
El registro $at (assembler temporary) es muy utilizado por el compilador de assembly para
almacenar valores temporales que se utilizan dentro de pseudo-instrucciones. No se preserva
entre function calls.
Losregistros$a0,...,$a5(argument)seusanparapasarargumentosafunciones.Sielnúmero
de argumentos es mayor se debe utilizar la pila. No se preservan entre function calls al igual
que los registros temporales $t0,...,$t5 (temporaries) que son usados por el compilador o
por el programador de assembly para almacenar valores intermedios. Los registros $a0 y $a1
tienen como alias $v0 y $v1 y se pueden usar para retornar valores desde funciones. No se
preservan entre llamadas (function calls). Normalmente solo se usa el primero pero es posible
retornar valores de 64 bits mediante el uso del segundo para contener los cuatro bytes más
significativos. Los registros $s0,...,$s7 (Saved Temporary) se usan para almacenar valores
de mayor duración y sí se preservan entre function calls.
Los registros de enlazado $lr0,...,$lr3 (link register) requieren una especial mención.
Pueden ser utilizados por la instrucción JALX para almacenar múltiples retornos en aplicacio-
nes como corrutinas. No se preservan y por lo tanto pueden ser reutilizados cuando no están
en uso.
Los registros $k0,$k1 están reservados para uso del kernel del sistema operativo. Pueden
cambiar de forma impredecible en cualquier momento porque son utilizados por los interrupt
handlers.
Los registros de puntero (pointer registers) son una familia de registros que contiene
direcciones de memoria, a lo que se les asigna funciones muy particulares. Todos ellos se
preservan entre function calls y no todos son de uso obligatorio, por lo que pueden cumplir
una función secundaria con otro alias. Por ejempo $fp tiene como alias $s8 y $gp alias $s9.
Es importante enteder que mientras se los use como otros registros no podrán ser punteros y
viceversa.
A continuación detallamos la función asignada a cada uno de ellos:
Puntero global $gp (Global Pointer): normalmente guarda un puntero al área de datos
globales (para que pueda accederse usando memory offset addressing).
Punterodepila $sp(Stack Pointer):seusaparaalmacenarladirecciónadondeapunta
la pila actualmente.
3.3. Banco de Registros 18

---

## Page 21

Capítulo 3. El procesador STX4 Manual de Usuario RTM32
Puntero de marco $fp (Frame Pointer): se usa para almacenar la dirección base del
marco de pila (Stack Frame).
Dirección de retorno $ra (Return Address): almacena la dirección de retorno (la ubica-
cióndelprogramaalaqueunafuncióndebevolver).Estepunteroesusadocomúnmente
para las instrucciones JAL y JALR.
TodoslosregistrosmencionadossonutilizadosregularmenteenlaCPUyaccesibleatraves
de las instrucciones pero hay otros registros como el contador de programa $pc (program
counter)queesmanipuladoexclusivamenteporlaCPUeindirectamenteporlasinstrucciones
de cambio de flujo.
3.4. Registros de Funciones Especiales
LosregistrosdefuncionesespecialesSFR(special function registers)permiteninspeccionar
o setear distintas condiciones del la CPU y se acceden en forma indirecta mediante instruc-
ciones específicas como CFS y CTS. La CPU STX4 tiene 7 registros especiales que detallamos
a continuación:
Palabra de estado del programa $psw (Program Status Word): almacena el estado de
ejecución del procesador, incluyendo las banderas aritméticas, el nivel de privilegio y el
estado global de las interrupciones.
Registro de causa de la excepción $ecr (Exception Cause Register): contiene el código
que identifica la excepción o interrupción que provocó la transferencia de control al
manejador correspondiente.
Contador de programa de la excepción $epc (Exception Program Counter): almace-
na la dirección de la instrucción cuya ejecución fue interrumpida por la excepción o
interrupción, permitiendo reanudar la ejecución cuando corresponda.
Registro de estado de la excepción $esr (Exception Status Register): almacena el valor
del $psw al momento en que se produce una excepción o interrupción, permitiendo
restaurar su valor cuando corresponda.
Dirección virtual incorrecta $bva (Bad Virtual Address): almacena la dirección virtual
que originó una excepción de acceso a memoria.
Registro base vectorizado $vbr (Vector Base Register): contiene la dirección base de
la tabla de vectores de excepción e interrupción. Cuando se resetea el procesador este
registro se carga con el valor 0xF0000000
Registro de identificación de la CPU $pir (Processor Identification Register): contiene
un conjunto de bits que identifican el procesador, su familia y si posee características
especiales. Está cableado de fábrica y su valor no puede alterarse.
3.4.1. El PSW
Este registro está compuesto por un conjunto de bits detallado en la figura 3.1 que repre-
sentanelestadodelprocesador.Losquepermitenescrituradeterminanciertasconfiguraciones
posibles como la habilitación de interrupciones o la ejecución de traps en modo privilegiado.
A continuación se detalla el comportamiento y la función semántica de cada uno de los bits
de control y banderas de condición que conforman el registro $psw:
3.4. Registros de Funciones Especiales 19

---

## Page 22

Capítulo 3. El procesador STX4 Manual de Usuario RTM32
31 7 6 5 4 3 2 1 0
unused T M I N O C Z
Figura 3.1: Formato del registro PSW
Bit Nombre Descripción y Funcionamiento
M Modo de Ejecución Determina el nivel de privilegio actual del procesador.
• 1: Modo Kernel (Privilegiado). Permite la ejecución
de todas las instrucciones del ISA, incluyendo aquellas de
control de sistema, manipulación de registros de control y
acceso irrestricto al mapa de memoria.
• 0: Modo Usuario (No Privilegiado). Restringe las
operacionessensiblesdemáquina.Cualquierintentodeeje-
cutarinstruccionesdecontrolenestemodogatilladeforma
automática un trap por violación de privilegios.
I Habilitación de Interrupciones Control global sobre la aceptación de peticiones de inte-
rrupción de hardware externas (enmascarables).
• 1: Habilitadas. El procesador responderá y derivará el
control al manejador de interrupciones correspondiente al
recibir una petición.
• 0: Deshabilitadas. Las interrupciones externas quedan
bloqueadas temporalmente en el hardware del procesador.
T Habilitación de Traps Controla la captura de excepciones generadas por software
o errores de ejecución interna cuando el sistema opera en
el nivel de mayor privilegio.
• 1: Habilitado. Permite que se generen y capturen traps
de manera de forma controlada y segura incluso cuando el
procesador se encuentra ejecutando en Modo Kernel.
• 0: Deshabilitado.
Z Bandera de Cero Indica si el resultado de la última operación en la ALU fue
idénticamente nulo. Se evalúa en 1 si el resultado es cero;
de lo contrario, se limpia a 0.
N Bandera de Negativo Refleja el bit más significativo (bit de signo) del resultado
de la última operación aritmética. Se establece en 1 si el
resultado es negativo; de lo contrario, toma el valor 0.
C Bandera de Acarreo Se establece en 1 si se produce un acarreo de salida (carry-
out) o un préstamo (borrow) más allá del bit más signi-
ficativo en operaciones aritméticas de suma o resta; de lo
contrario, se limpia a 0.
O Bandera de Desbordamiento Se activa en 1 si ocurre un desbordamiento aritmético en
operacionesconsignobajolarepresentacióndecomplemen-
to a dos (por ejemplo, cuando la suma de dos valores de
igual signo produce un resultado con signo opuesto); de lo
contrario, permanece en 0.
Tabla 3.2: Descripción detallada de los bits del registro PSW
3.5. Modelo de Privilegios
El procesador STX4 implementa un modelo de seguridad dual basado en dos niveles de
ejecución jerárquicos gobernados por el bit M del registro de estado $psw: el Modo Kernel
(privilegiado, M=1) y el Modo Usuario (no privilegiado, M=0).
Toda transición hacia un entorno seguro de ejecución se gestiona a través de excepciones
de software controladas mediante la instrucción TRAP, la cual almacena la dirección de re-
torno en el registro $epc aplicando un desfase fijo de 4 bytes sobre el program counter actual
3.5. Modelo de Privilegios 20

---

## Page 23

Capítulo 3. El procesador STX4 Manual de Usuario RTM32
(EPC = PC+4) y desvía el flujo del programa hacia el vector de servicio correspondiente
en la dirección de memoria apuntada por la expresión $vbr+(param≪2). El retorno desde
el contexto privilegiado hacia el hilo de ejecución original se efectúa de forma atómica me-
diante la instrucción RFT, la cual restaura el contador de programa desde el registro $epc
restableciendo además los contextos de estado guardados en $esr hacia el $psw.
3.5.1. Estado de Reset
La activación de la señal física de reset fuerza al procesador a un estado inicial predecible
e inmune a condiciones de carrera de software. El estado arquitectónico del procesador tras
un evento de reset (Cold Start) se establece de la siguiente manera:
1. Program Counter (PC): El contador de programa es forzado a inicializarse en la
direccióndememoriafísica0xF0000000(definidacomoelvectordeiniciodelamáquina
o Vector 0), lugar donde debe residir el firmware o cargador de arranque primario del
sistema.
2. Registro de Estado ($psw): Se inicializa con los bits de control configurados para
permitir la inicialización segura del software de sistema:
El bit M se establece en 1 (Modo Kernel), otorgando acceso privilegiado completo
al hardware.
El bit I se establece en 0 (Interrupciones deshabilitadas), previniendo la interfe-
rencia de periféricos externos antes de que se configuren las tablas de vectores.
El bit T se establece en 1 (Traps habilitados), permitiendo capturar excepciones
de software generadas de forma síncrona en el arranque.
3. Banco de Registros de Propósito General: Todos los registros del banco (R[0] a
R[31]) son borrados de manera síncrona por hardware, garantizando un estado inicial
limpio con valor 0x00000000 para todos ellos al comenzar la ejecución.
4. Registro Base Vectorizado ($vbr): Se inicializa cargando por defecto el valor de
dirección 0xF0000000, alineando el espacio inicial de excepciones con el segmento de
memoria de arranque.
3.6. Tipos de Datos
La arquitectura RTM32 es una máquina orientada a palabras de 32 bits que opera funda-
mentalmente sobre enteros y direcciones de memoria. A continuación, se detallan los tipos de
datos fundamentales soportados por el hardware, su representación binaria y el tratamiento
que el procesador aplica a los operandos inmediatos y las direcciones de memoria.
3.6.1. Tipos de Datos Fundamentales y Tamaños
El procesador define tres tamaños de datos básicos para la manipulación de información
en registros y memoria:
3.6. Tipos de Datos 21

---

## Page 24

Capítulo 3. El procesador STX4 Manual de Usuario RTM32
Palabra (Word): El tipo de dato nativo de la arquitectura, con un ancho de 32 bits (4
bytes). Los registros de propósito general (R[0] a R[31]) y las operaciones de la ALU
operan de manera nativa en este formato.
Media Palabra (Half-word): Datos con un ancho de 16 bits (2 bytes). Utilizado
principalmente en transferencias de memoria estructuradas y operaciones de empaque-
tado.
Byte: La unidad mínima de direccionamiento de la memoria, con un ancho de 8 bits
(1 byte).
3.6.2. Representación de Enteros e Interpretación
Los tipos de datos numéricos se interpretan bajo dos esquemas de codificación binaria
dependiendo de la instrucción ejecutada (por ejemplo, diferencias entre BLT y BLTU, o SLTI
y SLTIU):
Representación Sin Signo (Unsigned)
Un entero sin signo de n bits permite representar valores en el rango [0,2n−1]. Para una
palabra completa de 32 bits, el rango corresponde a [0,4294967295]. Su valor decimal se
evalúa mediante la sumatoria estándar de pesos binarios:
n−1
U(X)= ∑ x ⋅2i
i
i=0
Representación Con Signo (Signed)
Los enteros con signo se representan exclusivamente mediante el formato de comple-
mento a dos. El bit más significativo (x ) actúa como bit de signo. El rango de valores
n−1
representables para una palabra de 32 bits bajo este esquema es [−231,231−1], equivalente a
[−2147483648,2147483647]. El valor decimal se calcula como:
n−2
S(X)=−x ⋅2n−1+ ∑ x ⋅2i
n−1 i
i=0
Las instrucciones de carga de memoria (LH, LHU, LB, LBU) realizan la transferencia desde
la memoria hacia un registro destino aplicando extensión de signo (añadiendo copias de x
15
o x en los bits más significativos del registro de 32 bits) o extensión de cero, de acuerdo con
7
la semántica del mnemónico.
3.6.3. Valores Inmediatos y Extensión de Tipo
Las instrucciones de formato I codifican operandos inmediatos dentro de la propia ins-
trucción. Para adaptar estos valores al ancho nativo de la ALU (32 bits), el procesador imple-
mentadosoperadoresmatemáticosdeextensióndenotadoscomoE (y,z)ydeconcatenación
x
C (y,z):
x
1. Extensión de Signo o Cero (E (y,z)):Extiendeunvalory dexbitshastacompletar
x
los 32 bits utilizando un bit de relleno z ∈{S,0,1}.
3.6. Tipos de Datos 22

---

## Page 25

Capítulo 3. El procesador STX4 Manual de Usuario RTM32
Extensión con Signo (E (y,S)): Los 32−x bits más significativos del operando
x
final se rellenan con el bit de signo del inmediato original (bit y ). Se utiliza
x−1
en instrucciones aritméticas con signo como ADDI o desplazamientos de memoria
como LW.
Extensión con Cero (E (y,0)): Los bits restantes se rellenan con 0. Utilizado
x
en operaciones lógicas como ANDI u ORI.
2. Concatenación de Bits (C (y,z)): Utilizada para construir constantes en la parte
x
alta de un registro (instrucciones tipo LCI, ANDH, ORH, XORH). Concatena los x bits del
inmediato y en los bits más significativos de la palabra, preservando o modificando los
bits menos significativos provenientes del registro fuente z.
3.6.4. Representación de Direcciones de Memoria
La arquitectura RTM32 utiliza un espacio de direccionamiento plano y lineal de 32 bits, lo
que permite un límite teórico de acceso a memoria de 4 GiB (232 bytes).
Direcciones Relativas al PC (RA ): Los saltos condicionales e incondicionales cal-
x
culan su destino de forma relativa al registro PC. El procesador opera en direcciona-
mientoporpalabrasde32bitsparainstrucciones,calculandoladireccióndestinocomo:
RA (y)=PC+4+E (4y,S)
x x
Multiplicar el inmediato por 4 desplaza implícitamente el operando 2 bits a la izquier-
da, optimizando el rango de salto bajo la premisa de que las instrucciones siempre se
encuentran alineadas a palabra en memoria.
Direcciones Absolutas (AA ): Saltos indirectos calculados como base más despla-
x
zamiento:
AA (rs,imm)=R[rs]+E (4imm,S)
x x
Dirección Efectiva de Datos (EA y EAX):Paraaccesosdelectura/escrituraame-
moria de datos, ladirección efectiva de transferencia se determinamediante la suma del
registro base y el inmediato extendido con signo (EA=R[rs]+E (imm,S)) o mediante
17
la suma indexada de dos registros en instrucciones de tipo indexado (EAX(rs,rd) =
R[rs]+R[rd]).
3.6.5. Concepto de Desbordamiento (Overflow)
El desbordamiento aritmético ocurre exclusivamente en operaciones con signo cuando el
resultado matemático de una operación excede el rango de representación del formato de
complemento a dos de 32 bits (rango [−231,231−1]).
El procesador detecta esta condición mediante hardware dedicado en la ALU y actualiza
de manera síncrona la bandera de desbordamiento O (Overflow) en el registro de estado
$psw. Conceptualmente, para una operación de suma Z =X+Y, la bandera O se activa si y
solo si:
Se suman dos operandos con signo positivo (x =0,y =0) y el resultado tiene signo
31 31
negativo (z =1).
31
3.6. Tipos de Datos 23

---

## Page 26

Capítulo 3. El procesador STX4 Manual de Usuario RTM32
Se suman dos operandos con signo negativo (x =1,y =1) y el resultado tiene signo
31 31
positivo (z =0).
31
En operaciones sin signo, las condiciones de rebase de rango se registran únicamente a través
delabanderadeacarreoC(Carry),evitandoalterarlabanderadedesbordamientoaritmético
con signo.
3.6. Tipos de Datos 24

---

## Page 27

Parte III
Arquitectura del Set de
Instrucciones
25

---

## Page 28

4. Notación
4.1. Convenciones generales
A lo largo de este manual las instrucciones de RTM32 se describen mediante un lengua-
je matemático formal. Las funciones, operadores y convenciones definidas en este capítulo
forman parte de la especificación arquitectónica del ISA y se utilizarán en los capítulos pos-
teriores sin volver a redefinirse.
Salvo que se indique explícitamente lo contrario, todos los registros y operandos poseen
el tamaño nativo de la arquitectura (32 bits). Las constantes inmediatas se representan uti-
lizando el número de bits definido por el formato de instrucción correspondiente.
. ATENCIÓN
Lasfuncionesdefinidasenestecapítulonorepresentaninstruccionesdelaarquitectura
ni operaciones realizadas por el compilador. Constituyen una notación matemática
utilizada para describir de manera precisa el comportamiento de cada instrucción del
ISA.
4.2. Operaciones sobre bits
Algunas instrucciones operan únicamente sobre una parte del contenido de un registro
o de un operando. Para describir estas operaciones la arquitectura utiliza la notación de
selección de campos de bits.
4.2.1. Selección de bits
La expresión
x
[m∶n]
indica el subconjunto de bits comprendidos entre las posiciones m y n, siendo m≥n y m
el bit más significativo del rango. Los bits se numeran desde cero, correspondiendo el bit 0 al
bit menos significativo.
Por ejempl si x=0x12345678 entonces x =0x5678 y x =0x1234.
[15∶0] [31∶16]
4.2.2. Concatenación binaria
El operador
x∣∣y
representa la concatenación de dos secuencias binarias, donde los bits de x forman la
partemássignificativadelresultadoylosbitsdey lapartemenossignificativa.Esteoperador
constituye la base de la función de concatenación C() a definir.
26

---

## Page 29

Capítulo 4. Notación Manual de Usuario RTM32
Por ejemplo,
0x1234∣∣0xABCD=0x1234ABCD
4.3. Espacios de almacenamiento
Las siguientes expresiones identifican los distintos espacios de almacenamiento utilizados
por la arquitectura.
R[x] Registro de propósito general con índice x.
S[x] Registro especial con índice x.
M[x] Contenido de memoria ubicado en la dirección x.
PC Contador de programa.
EPC Contador de programa almacenado durante una excepción.
$0 Registro constante cuyo valor es siempre cero.
Cuando una expresión utiliza índices (selección de bits) como en el ejemplo,
R[5]
[15∶0]
representa los dieciséis bits menos significativos del registro R[5].
4.4. Transformación de operandos
Las instrucciones de RTM32 utilizan distintas funciones para adaptar el tamaño de ope-
randos inmediatos antes de participar en operaciones aritméticas, lógicas o en el cálculo de
direcciones.
Estas funciones reciben como entrada un operando de x bits y producen un resultado del
tamaño de palabra de la arquitectura.
4.4.1. Extensión de operandos
La función general de extensión se define como
E (y,z) (4.1)
x
donde
x representa el tamaño original del operando.
y representa el valor a extender.
z especifica el mecanismo de extensión.
El parámetro
z ∈{S,0,1}
selecciona uno de los tres mecanismos de extensión definidos por la arquitectura.
4.3. Espacios de almacenamiento 27

---

## Page 30

Capítulo 4. Notación Manual de Usuario RTM32
Extensión con signo
La extensión con signo conserva el valor numérico de un operando representado en com-
plemento a dos.
Formalmente,
E (y,S)=b ...b b ...b (4.2)
x x−1 x−1 x−1 0
·„„„„„„„„„„„„„„„„„„„„„„„„„‚„„„„„„„„„„„„„„„„„„„„„„„„„„¶
32−x
donde b representa el bit de signo del operando original.
x−1
En consecuencia,
si el bit de signo vale 0, la extensión completa con ceros;
si el bit de signo vale 1, la extensión completa con unos.
La extensión con signo preserva el valor aritmético del operando al cambiar su tamaño
de representación. Este mecanismo se utiliza para constantes inmediatas con signo, despla-
zamientos relativos y cargas de datos con signo.
Ejemplo 1
E (0x2A,S)=0x0000002A
8
Como el bit de signo vale cero, los bits superiores se completan con ceros.
Ejemplo 2
E (0xF4,S)=0xFFFFFFF4
8
En este caso el operando representa el valor decimal −12, por lo que los bits superiores se
completan con unos.
Extensión con ceros
La extensión con ceros copia el operando original completando los bits superiores con
ceros.
E (y,0)=00...0 b ...b (4.3)
x x−1 0
·„„„„„„„‚„„„„„„„¶
32−x
Este mecanismo interpreta el operando como un valor sin signo. La extensión con ceros
se emplea principalmente en operaciones lógicas y en las instrucciones que manipulan datos
sin signo.
Por ejemplo,
E (0xABCD,0)=0x0000ABCD
16
Extensión con unos
La extensión con unos completa los bits superiores utilizando el valor uno.
E (y,1)=11...1 b ...b (4.4)
x x−1 0
·„„„„„„„‚„„„„„„„¶
32−x
4.4. Transformación de operandos 28

---

## Page 31

Capítulo 4. Notación Manual de Usuario RTM32
Este mecanismo se utiliza principalmente para construir máscaras donde los bits más
significativos deben permanecer activos.
. ATENCIÓN
La extensión con unos no preserva el valor numérico del operando. Su finalidad es fa-
cilitar la construcción de máscaras binarias empleadas por determinadas instrucciones
lógicas de la arquitectura.
Por ejemplo,
E (0x1234,1)=0xFFFF1234
16
4.4.2. Concatenación
Algunas instrucciones requieren construir un nuevo operando combinando dos valores
distintos. Para ello la arquitectura define la función de concatenación
C (y,z) (4.5)
x
que concatena los x bits de y como parte más significativa con los x bits menos significa-
tivos de z.
Formalmente,
C (y,z)=y ∣∣z
x [x−1∶0] [x−1∶0]
donde el operador ∣∣ representa la concatenación de secuencias binarias.
@ NOTA
Lafuncióndeconcatenaciónpermiteconstruirconstantesde32bitsmedianteunaúni-
ca instrucción, reutilizando parte del contenido previo de un registro. Este mecanismo
es utilizado por las instrucciones LCI, ANDH, ORH y XORH.
Ejemplo Si
R[$t0]=0x56789ABC
entonces
C (0x1234,R[$t0])=0x12349ABC
16
ya que los dieciséis bits superiores provienen del operando inmediato, mientras que los
dieciséis bits inferiores conservan el contenido original del registro.
Constantes ubicadas en la mitad superior Con frecuencia resulta conveniente repre-
sentarconstantesde32bitscuyovalorinmediatoocupalamitadsuperiordelapalabraycuya
mitad inferior está formada por un valor constante. Para simplificar la notación se definen
las siguientes funciones auxiliares:
4.4. Transformación de operandos 29

---

## Page 32

Capítulo 4. Notación Manual de Usuario RTM32
H (imm,0)≡C (imm,$0)
16 16
H (imm,1)≡C (imm,¬$0)
16 16
donde $0 representa el registro constante con valor 0x00000000 y ¬$0 denota concep-
tualmente un registro con valor 0xFFFFFFFF. Estas funciones son únicamente alias de la
operación de concatenación y se utilizan para expresar de forma más clara las operaciones
lógicas inmediatas sobre la mitad superior del registro.
4.5. Interpretación de operandos
Salvo que se indique explícitamente lo contrario, todos los operandos de la arquitectura
se interpretan como enteros representados en complemento a dos.
Paraaquellasinstruccionesquerequiereninterpretarunoperandocomounvalorsinsigno
se utiliza la función
U(x) (4.6)
la cual indica que el operando debe considerarse como un entero positivo representado
mediante aritmética modular de 32 bits.
@ NOTA
La función U() modifica únicamente la interpretación matemática del operando. No
altera el patrón binario almacenado en el registro.
Por ejemplo,
0xFFFFFFFF=−1
cuando se interpreta como entero con signo, mientras que
U(0xFFFFFFFF)=4294967295
cuando se interpreta como entero sin signo.
Esta notación se emplea principalmente en las instrucciones de comparación, multiplica-
ción y división sin signo.
4.6. Cálculo de direcciones
Las instrucciones que acceden a memoria o modifican el flujo de ejecución obtienen la
dirección de destino mediante funciones arquitectónicas especializadas. Estas funciones for-
man parte de la especificación formal del ISA y serán utilizadas en la descripción de todas
las instrucciones correspondientes.
4.5. Interpretación de operandos 30

---

## Page 33

Capítulo 4. Notación Manual de Usuario RTM32
4.6.1. Dirección efectiva
Las instrucciones de acceso a memoria con desplazamiento inmediato utilizan la función
EA(rs,imm)=R[rs]+E (imm,S) (4.7)
17
donde R[rs] proporciona la dirección base y el operando inmediato representa un des-
plazamiento relativo expresado en bytes.
Por ejemplo. si
R[$sp]=0x1000
entonces
EA($sp,8)=0x1008.
4.6.2. Dirección efectiva extendida
Las instrucciones de acceso a memoria del formato R utilizan dos registros para calcular
la dirección efectiva.
La función correspondiente se define como
EAX(rs,rd)=R[rs]+R[rd] (4.8)
Estemecanismoeliminalanecesidaddeutilizarunoperandoinmediatoypermiteindexar
estructuras de datos utilizando registros.
Por ejemplo, si
R[$s0]=0x1000
y
R[$t0]=0x0010
entonces
EAX($s0,$t0)=0x1010.
4.6.3. Dirección relativa al contador de programa
Las instrucciones de salto relativo utilizan la función
RA (imm)=PC+4+E (4⋅imm,S) (4.9)
x x
donde el subíndice x indica el tamaño efectivo del operando inmediato empleado por la
instrucción correspondiente.
El desplazamiento inmediato se expresa en palabras y posteriormente se convierte a bytes
multiplicándolo por cuatro.
4.6. Cálculo de direcciones 31

---

## Page 34

Capítulo 4. Notación Manual de Usuario RTM32
@ NOTA
La referencia utilizada por la función RA() corresponde siempre a la dirección de la
siguiente instrucción (PC+4), independientemente del tipo de salto.
4.6.4. Dirección absoluta relativa a un registro
Las instrucciones de salto indirecto utilizan la función
AA (rs,imm)=R[rs]+E (4⋅imm,S) (4.10)
x x
donde el desplazamiento inmediato también se expresa en palabras y se convierte a bytes
antes de realizar la suma.
A diferencia de la función RA(), la dirección base no proviene del contador de programa
sino del contenido de un registro de propósito general.
4.6.5. Entrada de la tabla de vectores
La arquitectura define la función
TV(param)=param≪2 (4.11)
que calcula el desplazamiento correspondiente a una entrada param dentro de la tabla
de vectores de excepción. Cada entrada ocupa una palabra de memoria (4 bytes), razón por
la cual el índice se multiplica por cuatro mediante un desplazamiento de dos bits hacia la
izquierda.
Por ejemplo, si param=5 entonces
TV(5)=20=0x14.
@ NOTA
LafunciónTV()calculaúnicamenteeldesplazamientodeunaentradadentrodelatabla
de vectores. La dirección base de dicha tabla es proporcionada por la implementación
de la arquitectura o por el sistema operativo.
4.7. Nomenclatura de operandos inmediatos
Las instrucciones de RTM32 emplean operandos inmediatos de distintos tamaños, depen-
diendo del formato de instrucción y de la operación realizada. Para simplificar la descripción
de la ISA, este manual utiliza una convención de nombres donde el identificador del ope-
rando refleja directamente la cantidad relativa de bits disponibles para representar el valor
inmediato. La Tabla 4.1 resume la nomenclatura empleada a lo largo del manual.
La longitud efectiva de cada operando depende del formato de instrucción en el que
aparece y se encuentra determinada por la codificación binaria del ISA. Por este motivo, los
4.7. Nomenclatura de operandos inmediatos 32

---

## Page 35

Capítulo 4. Notación Manual de Usuario RTM32
Notación Significado Relativo Tamaño
elimm Extra Long Immediate Mayor 25 bits
vlimm Very Long Immediate 24 bits
llimm Long Long Immediate 20 bits
limm Long Immediate 19 bits
imm Immediate 17 bits
simm Short Immediate Menor 16 bits
Tabla 4.1: Jerarquía de operandos inmediatos
nombres anteriores constituyen una nomenclatura relativa y no representan un número fijo
de bits.
Esta convención permite describir el comportamiento de las instrucciones de forma in-
dependiente de la distribución concreta de campos dentro de cada formato de instrucción,
manteniendo una notación uniforme en toda la especificación arquitectónica.
@ NOTA
Los prefijos utilizados siguen una jerarquía estrictamente decreciente:
vlimm>llimm>limm>imm>simm
dondecadaniveldisponedeuncampoinmediatomenoroigualqueelanterior.Lacan-
tidad exacta de bits de cada operando se define en el capítulo dedicado a los formatos
de instrucción.
4.7. Nomenclatura de operandos inmediatos 33

---

## Page 36

5. Modos de Direccionamiento
5.1. Consideraciones generales
Los modos de direccionamiento definen la forma en que una instrucción obtiene la ubica-
ción de sus operandos. Dependiendo de la operación, éstos pueden encontrarse en registros de
propósito general, formar parte de la propia instrucción o calcularse dinámicamente a partir
de uno o más registros del procesador.
En RTM32 el modo de direccionamiento no se codifica mediante un campo específico
dentro de la instrucción. En su lugar, queda determinado de manera implícita por el opcode
yporelformatodeinstrucciónutilizado. Esteenfoquesimplificaelprocesodedecodificación,
reduce la complejidad del hardware de control y permite mantener un formato de instrucción
uniforme de 32 bits para toda la arquitectura.
La arquitectura define cinco modos fundamentales de direccionamiento:
Direccionamiento mediante registros.
Direccionamiento inmediato.
Direccionamiento indexado.
Direccionamiento relativo al contador de programa.
Direccionamiento indirecto.
Cada uno de ellos responde a necesidades diferentes y ha sido diseñado para optimizar
las operaciones más frecuentes realizadas por el procesador.
5.2. Direccionamiento mediante registros
El direccionamiento mediante registros (Register Addressing) utiliza como operandos el
contenido de los registros de propósito general. En este modo la instrucción únicamente
codifica los índices de los registros involucrados; los datos propiamente dichos nunca forman
parte de la palabra de instrucción.
Las instrucciones de formato R emplean este mecanismo para la mayoría de las operacio-
nes aritméticas, lógicas, desplazamientos, comparaciones, multiplicación, división y acceso a
registros especiales.
Generalmente los campos rs y rt identifican los registros fuente, mientras que rd selec-
ciona el registro destino. Algunas familias reinterpretan parcialmente estos campos, aunque
el principio de funcionamiento permanece inalterado.
Al encontrarse todos los operandos disponibles dentro del banco de registros, este modo
evita accesos adicionales a memoria y constituye el mecanismo de direccionamiento de menor
latencia de la arquitectura.
ADD $t0,$t1,$t2
AND $s0,$s1,$s2
SLTU $a0,$a1,$a2
MUL $v0,$v1,$t0
34

---

## Page 37

Capítulo 5. Modos de Direccionamiento Manual de Usuario RTM32
El direccionamiento mediante registros constituye el mecanismo preferido para el proce-
samiento intensivo de datos. Los compiladores intentan mantener las variables más utilizadas
en registros para minimizar los accesos a memoria y mejorar el rendimiento del programa.
5.3. Direccionamiento inmediato
En el direccionamiento inmediato (Immediate Addressing) uno de los operandos se en-
cuentra codificado directamente dentro de la instrucción. De este modo la CPU dispone
inmediatamente del valor constante sin necesidad de realizar accesos adicionales a memoria.
Dependiendo de la instrucción, la constante inmediata puede representar un valor aritmé-
tico, una máscara lógica, un desplazamiento o una parte de una constante de mayor tamaño.
Antes de participar en la operación correspondiente, el operando inmediato se transforma
utilizandolasfuncionesdefinidasenlasección4.4.Segúnlainstrucción,laarquitecturapuede
aplicar extensión con signo, extensión con ceros, extensión con unos o concatenación.
Este modo de direccionamiento es utilizado por todas las instrucciones de operación in-
mediata del formato I.
ADDI $t0,$t1,−4
ANDI $s0,$s0,0x00FF
ORI $a0,$a0,0x10
LCI $t2,$t2,0x1234
@ NOTA
LastransformacionesdeoperandosinmediatossedescribenmediantelasfuncionesE()
y C(), definidas en las secciones 4.4.1 y 4.4.2 respectivamente. Estas funciones forman
partedelaespecificaciónformaldelaarquitecturaysereferenciaránalolargodetodo
el manual.
5.4. Direccionamiento indexado
El direccionamiento indexado (Base+Offset Addressing) constituye el mecanismo utiliza-
doportodaslasinstruccionesdeaccesoamemoriadelformatoI.Enestemodolainstrucción
especifica un registro base y un desplazamiento inmediato a partir del cual la CPU obtiene
la dirección del operando.
Durante la ejecución la dirección efectiva se calcula aplicando la función EA(), definida en
la sección 4.6.1. Como el desplazamiento inmediato se representa en complemento a dos, el
accesopuederealizarsetantohaciadireccionessuperiorescomoinferioresrespectodelregistro
base.
Estemecanismoresultaespecialmenteadecuadoparaaccederavariableslocales,registros
de activación, estructuras de datos, arreglos y pilas, permitiendo recorrer regiones completas
de memoria modificando únicamente el valor del registro base. Todas las instrucciones de
carga y almacenamiento utilizan este modo de direccionamiento.
LW $t0,8($sp)
SW $t1,−4($sp)
LH $a0,2($s0)
5.3. Direccionamiento inmediato 35

---

## Page 38

Capítulo 5. Modos de Direccionamiento Manual de Usuario RTM32
LBU $v0,0($a1)
SB $t2,15($fp)
. ATENCIÓN
El cálculo de la dirección efectiva no garantiza que el resultado satisfaga las restric-
ciones de alineación requeridas por la instrucción. Cuando una operación accede a
palabras o medias palabras, la dirección obtenida mediante EA() deberá encontrarse
correctamente alineada. En caso contrario la CPU genera una excepción de alineación.
5.5. Direccionamiento relativo al contador de programa
El direccionamiento relativo al contador de programa (PC-Relative Addressing) se utiliza
para las instrucciones de transferencia de control cuyo destino depende de la posición actual
del programa.
En este modo la instrucción codifica únicamente un desplazamiento relativo. Durante la
ejecución la CPU calcula la dirección de destino mediante la función RA(), definida en la
sección 4.6.1, utilizando como referencia la dirección de la siguiente instrucción (PC+4).
Este mecanismo permite generar código independiente de la posición de carga (Position
Independent Code), ya que el destino del salto depende únicamente del valor actual del con-
tador de programa y no de direcciones absolutas.
LasinstruccionesdesaltocondicionaldelformatoIylasinstruccionesdesaltodelformato
J utilizan este modo de direccionamiento.
BEQ $t0,$t1,label
BNE $a0,$zero,loop
J init
JAL function
@ NOTA
La utilización de desplazamientos relativos facilita la relocación del código ejecutable
y reduce el tamaño de los operandos necesarios para representar direcciones de salto.
5.6. Direccionamiento indirecto
El direccionamiento indirecto (Register-Relative Addressing) obtiene la dirección de des-
tinoapartirdelcontenidodeunregistrobaseyundesplazamientoinmediato.Adiferenciadel
direccionamiento relativo al contador de programa, la referencia utilizada durante el cálculo
proviene del contenido de un registro de propósito general.
La dirección de destino se obtiene mediante la función AA(), definida en la sección 4.6.4.
Este mecanismo permite realizar transferencias dinámicas de control cuya dirección única-
mente puede conocerse durante la ejecución del programa.
Las instrucciones JR, JALR y JALRX utilizan este modo de direccionamiento.
JR $t0,8
5.5. Direccionamiento relativo al contador de programa 36

---

## Page 39

Capítulo 5. Modos de Direccionamiento Manual de Usuario RTM32
JALR $s0,−2
JALRX $lr1,handler
Las variantes con enlace almacenan previamente la dirección de retorno en el registro co-
rrespondienteantesdeefectuarlatransferenciadecontrol,permitiendoimplementarllamadas
a procedimientos y retornos posteriores.
@ NOTA
El direccionamiento indirecto resulta fundamental para implementar llamadas me-
diante punteros a función, tablas de despacho, máquinas virtuales, intérpretes y otras
estructuras donde el destino del salto no puede conocerse durante la compilación.
5.7. Resumen
LaTabla5.1resumelosmodosdedireccionamientosoportadosporlaarquitecturaRTM32
y las familias de instrucciones que los emplean.
Modo Referencia Instrucciones
Mediante registros Banco de registros Formato R
Inmediato Constante codificada Operaciones inmediatas
Indexado Registro base + desplazamiento Cargas y almacenamientos
Relativo al PC PC + desplazamiento Branch, J, JAL, JALX
Indirecto Registro base + desplazamiento JR, JALR, JALRX
Tabla 5.1: Resumen de los modos de direccionamiento de RTM32
5.7. Resumen 37

---

## Page 40

6. Formatos de Instrucción
6.1. Consideraciones Generales
Lasinstruccionesconstandeunanchofijode32bitsysedecodificanmediantecamposbit
a bit estructurados en cuatro tipos llamados: R, I y J. Todas las instrucciones comparten el
mismocampollamadoopcode(códigodeoperación)formadoporloscincobitsmássignifica-
tivos (bits 31 a 27). El valor del opcodeidentificaal tipo de instrucción comosemuestraen la
tablaB.1.Notodoslosopcodessonválidos.Losvaloresdeopcodenoasignadosseconsideran
codificaciones reservadas. Su ejecución genera una excepción de instrucción inválida. Durante
ladescripcióndelosformatos,losbitssenumerandesdeelbit0(menossignificativo)hastael
bit31(mássignificativo).Lasfigurasrepresentanlasinstruccionesconelbitmássignificativo
a la izquierda.
Para simplificar la descripción de las instrucciones se utilizará la notación definida en el
capítulo Notación que se resume en la tabla A.1.
6.2. Formato R-Type
El formato tipo R (register) que se muestra en la figura 6.1 se utiliza principalmente
para operaciones aritméticas, lógicas, desplazamientos, multiplicación, división y operaciones
especiales del sistema.
31 27 26 22 21 17 16 12 11 7 6 5 0
opcode rs rt rd param x func
Figura 6.1: Formato tipo R
Cómo todas comparten el mismo opcode, la CPU las diferencia por el campo func o función
(function) que se encuentra en los 6 bits menos significativos (bit 0 al 5). En la tabla B.2 se
provee una lista de las instrucciones tipo R y sus valores de función asociados.
Loscamposrs,rty rdespecificanregistros(deallíelnombredetipoR),haciendoreferencia
al primer operando fuente (source register) , al segundo operando fuente (temporal register)
y a el registro destino (destination register). El bit 6 identificado como x está reservado y
debe contener 01.
6.2.1. Campo param
El campo param (bits 12 a 8) es un campo paramétrico (parameter field) de propósito
múltiple de 5 bits cuyo significado depende de la instrucción. Según la instrucción, puede
representar un desplazamiento inmediato, un índice de registro especial o un índice dentro
de la tabla de vectores de excepción. Sus usos se especifican a continuación:
Desplazamientos inmediatos (SLL, SRL, SRA): param contiene la cantidad de bits a des-
plazar (0–31).
1Todocamporeservadodeberáescribirseconceroydeberáignorarsedurantelalectura,salvoqueseindique
explícitamente lo contrario.
38

---

## Page 41

Capítulo 6. Formatos de Instrucción Manual de Usuario RTM32
Acceso a registros especiales (CFS, CTS): param contiene el índice del registro especial.
Manejo de excepciones (TRAP): param contiene el índice de la entrada correspondiente
dentro de la tabla de vectores de excepción.
Cuando una instrucción no utiliza el campo param, este deberá codificarse con el valor
cero para garantizar la compatibilidad con futuras extensiones de la arquitectura.
Ejemplo 1:
SRL $t0,$t1,5
opcode = 00000
rs = 00000
rt = 01111 ($t1)
rd = 01110 ($t0)
param = 00101
func = 000001
En esta instrucción param representa el desplazamiento inmediato.
Ejemplo 2:
SRLR $t0,$t1,$t2
opcode = 00000
rs = 10000 ($t2)
rt = 01111 ($t1)
rd = 01110 ($t0)
param = 00000
func = 000100
En esta instrucción el campo param debe codificarse con el valor cero y no participa en la
operación. La cantidad de bits a desplazar se obtiene de los cinco bits menos significativos
de R[rs].
6.3. Formato I-Type
El formato I (immediate)2 dispone de los campos opcode, rs, rt e imm como se muestra
en la figura 6.2. En este formato el campo opcode identifica la instrucción.
31 27 26 22 21 17 16 0
opcode rs rt imm
Figura 6.2: Formato tipo I
Enlamayoríadelasinstruccionesloscamposrsyrtcodificanregistrosdepropósitogeneral,
mientras que imm contiene una constante inmediata de 17 bits cuyo significado depende de la
instrucción. Según la operación puede representar:
un desplazamiento para direccionamiento indexado;
un desplazamiento relativo para instrucciones de salto condicional;
un desplazamiento relativo a un registro para instrucciones de enlazado indirecto;
2El nombre proviene del hecho de que la instrucción incorpora un operando inmediato codificado dentro
de la propia instrucción.
6.3. Formato I-Type 39

---

## Page 42

Capítulo 6. Formatos de Instrucción Manual de Usuario RTM32
una constante inmediata para operaciones aritméticas o lógicas.
Algunas familias de instrucciones reinterpretan parte del campo rt para extender el código
de operación o ampliar el tamaño del operando inmediato. Esta técnica permite conservar el
ancho fijo de 32 bits sin introducir nuevos formatos de instrucción. Los casos particulares se
describen en las secciones correspondientes.
6.3.1. Direccionamiento indexado
El direccionamiento indexado es el mecanismo utilizado por las instrucciones de acceso a
memoria para obtener la dirección del operando. En este modo la instrucción no codifica una
dirección absoluta, sino un registro base R[rs] y un desplazamiento inmediato imm a partir
de los cuales la CPU calcula la dirección efectiva mediante la función EA(), definida en la
Sección 4.6.1.
Todas las instrucciones de acceso a memoria del formato I emplean este mecanismo an-
tes de realizar la lectura o escritura correspondiente, incluyendo accesos de palabra, media
palabra y byte.
Ejemplo 1:
LW $t0, 8($sp)
opcode = 01000
rs = 11110 ($sp)
rt = 01110 ($t0)
imm = 0 0000 0000 0000 1000 (8)
Dado R[$sp] = 0x1000, aplicando la ecuación (4.7) tenemos que EA = 0x1008 por lo que
R[$t0] = M[0x1008]. El contenido de la posición de memoria 0x1008 se copia en el registro
$t0.
Ejemplo 2:
SW $t1, −4($sp)
opcode = 01001
rs = 11110 ($sp)
rt = 01111 ($t1)
imm = 1 1111 1111 1111 1100 (−4)
Aplicando un razonamiento similar EA = 0x0FFC por lo que M[0x0FFC] = R[$t1]. El conte-
nido del registro $t1 se copia en la posición de memoria 0x0FFC.
. ATENCIÓN
La función EA() calcula únicamente la dirección efectiva. Corresponde a cada ins-
trucción verificar que dicha dirección satisfaga los requisitos de alineación establecidos
por la arquitectura. Las instrucciones que operan sobre palabras requieren direccio-
nes múltiplo de cuatro, mientras que las que operan sobre medias palabras requieren
direcciones múltiplo de dos. Cuando una instrucción que exige alineación utiliza una
dirección no válida, la CPU genera la excepción correspondiente.
Como el desplazamiento se representa en complemento a dos, es posible acceder a posi-
ciones ubicadas antes o después de la dirección base sin modificar previamente el contenido
6.3. Formato I-Type 40

---

## Page 43

Capítulo 6. Formatos de Instrucción Manual de Usuario RTM32
del registro.
El formato I también también se utiliza para las instrucciones de salto condicional. En
ese caso, el operando inmediato deja de representar un desplazamiento sobre una dirección
base y pasa a expresar un desplazamiento relativo al contador de programa.
6.3.2. Saltos condicionales
Las instrucciones de salto condicional (branch) modifican el flujo normal de ejecución
únicamente cuando se cumple una condición lógica. En caso contrario, la ejecución continúa
con la siguiente instrucción. De ser verdadera entonces la CPU realiza el salto cambiando el
valordelPCaunonuevodefinidoporRA()segúnlasección4.6.3.Comoimmestárepresentado
encomplementoadoscon17bits,elalcancedelsaltoesaproximadamente±216 instrucciones,
equivalente a ±218 bytes (≈ 256 Ki instrucciones o ≈1 MiB de código).
Ejemplo 1:
BEQ $t0, $t1, 6
opcode = 10000
rs = 01110 ($t0)
rt = 01111 ($t1)
imm = 0000 0000 0000 0110 (6)
Supongamos que la instrucción se encuentra en la dirección PC = 0x00001000. Si R[$t0] ==
R[$t1], aplicando la ecuación correspondiente se obtiene:
RA=0x1000+4+(6×4)=0x101C
Laejecucióncontinúaentoncesenladirección 0x101C.Encasocontrario,lacondiciónresulta
falsa y la CPU continúa normalmente con la siguiente instrucción ubicada en 0x1004.
Ejemplo 2:
BNE $t0, $zero, −3
opcode = 10001
rs = 01110 ($t0)
rt = 00000 ($zero)
imm = 1111 1111 1111 1101 (−3)
Supongamos nuevamente que la instrucción se encuentra en PC = 0x00001000. Si R[$t0] !=
0, el desplazamiento negativo permite regresar a una instrucción anterior:
RA=0x1000+4+(−3×4)=0x0FF8
Este tipo de desplazamiento es muy utilizado para implementar bucles (loops), ya que
permite volver a ejecutar un bloque de instrucciones sin utilizar direcciones absolutas.
6.3.3. Operaciones inmediatas
Las instrucciones de operación inmediata utilizan el campo imm como un operando cons-
tanteincorporadoenlapropiainstrucción,evitandolanecesidaddecargarpreviamentedicho
valor en un registro.
6.3. Formato I-Type 41

---

## Page 44

Capítulo 6. Formatos de Instrucción Manual de Usuario RTM32
EnRTM32estegrupoestáformadoporlasinstruccionesADDI,SLTIySLTIU.Entodoslos
casos el operando inmediato ocupa 17 bits y se interpreta como un número en complemento a
dos. Antes de utilizarse es extendido al tamaño de palabra mediante la función E (imm,S)
17
definida en la sección 4.4.1. De este modo pueden representarse constantes positivas y nega-
tivas dentro del rango permitido por el campo inmediato.
La instrucción ADDI realiza la suma del contenido de un registro con una constante inme-
diata.
Ejemplo:
ADDI $t0, $t1, −4
opcode = 00100
rs = 01111 ($t1)
rt = 01110 ($t0)
h = 0
imm = 1111 1111 1111 1100 (−4)
EloperandoinmediatoseextiendeconsignomedianteE (simm,S)yposteriormentesesuma
17
al contenido del registro $t1. El resultado se almacena en $t0.
LasinstruccionesSLTIySLTIUrealizanunacomparaciónentreelcontenidodeunregistro
y una constante inmediata. Si la condición resulta verdadera almacenan el valor 1 en el
registro destino; en caso contrario almacenan 0. Todos los operadores relacionales realizan
comparaciones con signo, salvo cuando alguno de sus operandos aparece envuelto por la
función U(), que fuerza una interpretación sin signo.
Ejemplo:
SLTI $t0, $a0, 10
opcode = 10110
rs = 01000 ($a0)
rt = 01110 ($t0)
imm = 00000000000001010 (10)
El operando inmediato se extiende con signo hasta el tamaño de palabra y se compara con
el contenido del registro $a0. Si $a0 es menor que 10, la instrucción almacena el valor 1 en
$t0; en caso contrario almacena 0.
6.3.4. Operaciones inmediatas extendidas
Algunas instrucciones de operación inmediata no requieren un desplazamiento de 17 bits.
En consecuencia, el bit más significativo del operando inmediato se reutiliza como extensión
del código de operación, reduciendo el tamaño de la constante a 16 bits y duplicando el
número de instrucciones disponibles dentro de esta familia.
31 27 26 22 21 17 16 15 0
opcode rs rt h simm
Figura 6.3: Reinterpretación del formato I para las operaciones inmediatas extendidas
Las instrucciones de esta familia comparten el mismo formato básico de las operaciones
inmediatas convencionales. Sin embargo, el bit más significativo del campo imm, denominado
6.3. Formato I-Type 42

---

## Page 45

Capítulo 6. Formatos de Instrucción Manual de Usuario RTM32
h, deja de formar parte del operando inmediato y pasa a integrarse al código de operación.
El operando resultante, denominado simm, queda constituido únicamente por los 16 bits
restantes.
Cadavalordelcampoopcodeidentificaunafamiliadedosinstrucciones.Elbithselecciona
laoperaciónconcreta,duplicandoelespaciodecodificacióndisponiblesinmodificarelformato
de la instrucción.
Las instrucciones ANDI, ANI, ORI y XORI utilizan simm como una constante inmediata que,
es extendida mediante E (simm,z) definida en la sección 4.4.1 donde el parámetro z indica
16
el tipo de extensión requerido por la instrucción (signo, cero o uno).
Por otra parte, las instrucciones LCI, ANH, ORH y XORH interpretan simm como la mitad
más significativa de una constante de 32 bits. En estos casos la constante completa se obtiene
mediante la función C (simm,z) definida en la sección 4.4.2 donde el parámetro z indica el
16
registroaconcatenarrequeridoporlainstrucción(R[rs]o$0),permitiendoconstruirmáscaras
y constantes de 32 bits mediante una única instrucción.
Ejemplo 1:
ANDI $t0, $t1, 0xFF
opcode = 00100
rs = 01111 ($t1)
rt = 01110 ($t0)
h = 0
imm = 0000 0000 1111 1100 (−4)
El operando inmediato se extiende con ceros mediante E (simm,0) y posteriormente se
16
realiza la operación AND bit a bit con el contenido del registro $t1. El resultado se almacena
en $t0. Si $t1 contiene el valor 0x45003211 el resultado de $t0 = 0x00000011.
Ejemplo 2:
LCI $t0, $t0, 0x1234
opcode = 00100
rs = 01110 ($t0)
rt = 01110 ($t0)
h = 1
imm = 0001 0010 0011 0100
Laconstanteinmediataseconcatenaconlos16bitsmenossignificativosde$t0,obteniéndose:
R[$t0]=C (0x1234,R[$t0])
16
Como resultado, los 16 bits más significativos del registro pasan a contener el valor 0x1234,
mientras que los 16 bits menos significativos conservan su contenido original.
Este mecanismo constituye otro ejemplo de reutilización jerárquica de la codificación de
instrucciones. Al reducir el tamaño del operando inmediato en un bit es posible duplicar
el número de instrucciones disponibles dentro de la familia de operaciones inmediatas sin
introducir un nuevo formato de instrucción.
6.3. Formato I-Type 43

---

## Page 46

Capítulo 6. Formatos de Instrucción Manual de Usuario RTM32
6.3.5. Saltos indirectos
En la mayoría de las instrucciones de formato I, los campos rs, rt e imm representan dos
registros y un operando inmediato. Sin embargo, algunas familias de instrucciones reutilizan
parte de los bits del campo rt para extender el código de operación. En estas instrucciones el
campo rt deja de codificar un registro de propósito general y pasa a formar parte del proceso
de decodificación, permitiendo definir variantes de una misma operación sin introducir un
nuevo formato de instrucción.
Las instrucciones JR, JALR y JALRX utilizan este mecanismo. Todas ellas comparten el mismo
opcode y se diferencian mediante los bits almacenados en el campo rt. Al mismo tiempo, los
bits restantes de dicho campo permiten seleccionar el registro de enlace en la variante JALRX.
La figura 6.4 muestra la reinterpretación de los campos.
31 27 26 22 21 20 19 17 16 0
opcode rs so ll imm
Figura 6.4: Reinterpretación del formato I para JR/JALR
Los dos bits más significativos del campo rt constituyen un subcódigo de operación (so) que
identifica la variante de la instrucción, mientras que los tres bits menos significativos (ll) se
utilizan para extender la constante imm formando la constante inmediata llimm de 20 bits de
longitud.
Todas las instrucciones de esta familia realizan un salto hacia una dirección calculada
a partir de un registro base y un desplazamiento inmediato. A diferencia de los saltos con-
dicionales, donde el desplazamiento es relativo al contador de programa, en este caso el
desplazamiento es relativo al contenido del registro rs y la dirección de destino se obtiene
mediante la función AA (R[rs],llimm) definida en la sección 4.6.4.
22
La instrucción JR (so = b00) realiza el salto sin conservar la dirección de retorno. Por
el contrario, JALR (so = b01) almacena previamente el valor PC + 4 en el registro de enlace
$ra. Finalmente, JALRX generaliza este comportamiento permitiendo seleccionar uno de los
cuatro registros de enlace ($lr0..$lr3) mediante dos bits específicos (lr) dentro del campo
rt codificados como se muestra en la figura 6.5.
31 27 26 22 21 20 19 18 17 16 0
opcode rs 1 1r l imm
Figura 6.5: Reinterpretación del formato I para JALRX
Notar que ahora imm se extiende a 19 bits limm y la dirección de destino se obtiene
mediante AA (R[rs],limm) que solo difiere en el tamaño de la constante inmediata que es
21
menor. Esta capacidad resulta útil cuando existen múltiples contextos de llamada o cuando
el software necesita mantener varios enlaces activos simultáneamente.
Ejemplo 1:
JR $t0, 8
opcode = 00010
rs = 01110 ($t0)
rt = 00 000
imm = 0 0000 0000 0000 1000
6.3. Formato I-Type 44

---

## Page 47

Capítulo 6. Formatos de Instrucción Manual de Usuario RTM32
llimm = 000 0 0000 0000 0000 1000 (8)
Si R[$t0] = 0x2000, aplicando la ecuación (4.10) se obtiene:
AA=0x2000+(8×4)=0x2020
La CPU transfiere el control a la dirección 0x2020 sin modificar ningún registro de enlace.
Ejemplo 2:
JALR $s0, −2
opcode = 00010
rs = 10000 ($s0)
rt = 01 111
imm = 1 1111 1111 1111 1110
llimm = 111 1 1111 1111 1111 1110 (−2)
Si R[$s0] = 0x4000 y la instrucción se encuentra en PC = 0x1000, entonces:
AA=0x4000+(−2×4)=0x3FF8
Antes de efectuar el salto se almacena 0x1004 en el registro $ra. Posteriormente la ejecución
continúa en la dirección 0x3FF8.
Ejemplo 3:
JALRX $t1, 12
opcode = 00010
rs = 01111 ($t1)
rt = 1 01 00
imm = 0 0000 0000 0000 1100
limm = 00 0 0000 0000 0000 1100 (12)
En este ejemplo el bit más significativo de rt, con valor 1 identifica la instrucción JALRX, los
dos bits que le siguen (01) seleccionan el registro de enlace correspondiente y los restantes
forman parte de la constante slimm. El valor PC + 4 se almacena en $lr1 y la ejecución
continúa en la dirección calculada mediante la ecuación (4.10).
Este mecanismo constituye un ejemplo de reutilización jerárquica de la codificación de
instrucciones. Un mismo opcode identifica una familia de operaciones relacionadas, mientras
que parte de un campo originalmente destinado a operandos se reutiliza como extensión del
código de operación y otra parte para extender constantes. De este modo la arquitectura
incrementa el número de instrucciones disponibles sin aumentar el tamaño de la palabra de
instrucción ni introducir nuevos formatos de codificación.
6.4. Formato J-Type
El formato J (jump) está destinado a las instrucciones de transferencia incondicional de
controlmediantedireccionamientorelativoalcontadordeprograma(PC).Disponeúnicamente
de los campos opcode y jump, como se muestra en la figura 6.6. En este formato el campo
6.4. Formato J-Type 45

---

## Page 48

Capítulo 6. Formatos de Instrucción Manual de Usuario RTM32
opcode identifica la familia de instrucciones, mientras que el resto de la palabra se destina a
codificar el desplazamiento del salto.
31 27 26 0
opcode jump
Figura 6.6: Formato tipo J
En su forma básica el campo jump representa un desplazamiento relativo al contador de
programa. Sin embargo, al igual que ocurre en otras familias de instrucciones de RTM32,
algunas instrucciones reinterpretan una parte de este campo para extender el código de ope-
ración o seleccionar operandos adicionales. Esta técnica permite incrementar el número de
instrucciones disponibles manteniendo un tamaño fijo de 32 bits.
6.4.1. Saltos relativos
A diferencia de las instrucciones de salto indirecto, donde el destino se calcula a partir de
unregistrobase,estasinstruccionesdesaltoincondicionalutilizanundesplazamientorelativo
al contador de programa (PC). La dirección de salto depende únicamente del valor actual del
PC y del operando inmediato.
Las instrucciones J y JAL reutilizan los dos bits más significativos del campo jump pa-
ra extender el código de operación, mientras que los veinticinco bits restantes forman un
operando inmediato denominado vlimm que se utiliza para obtener la dirección de destino
RA (elimm) usando la ecuación 4.9.
27
31 27 26 25 24 0
opcode so elimm
Figura 6.7: Reinterpretación del formato J para J/JAL
La reinterpretación del formato se muestra en la figura 6.7. El subcódigo de operación
(so) distingue ambas variantes:
so = b00: instrucción J.
so = b01: instrucción JAL.
La instrucción J transfiere el control a la dirección calculada sin almacenar una dirección
de retorno. Por el contrario, JAL guarda previamente el valor PC+4 en el registro $ra antes
de efectuar el salto.
La instrucción JALX constituye una extensión de esta familia. Para incorporar la selec-
ción del registro de enlace consume un bit adicional del operando inmediato, reduciendo su
longitud efectiva. La reinterpretación del formato se muestra en la figura 6.8.
31 27 2266 25 24 23 0
opcode 1 lr vlimm
Figura 6.8: Reinterpretación del formato J para JALX
En este caso el bit más significativo del campo jump identifica la subfamilia JALX, mientras
que los dos bits siguientes seleccionan uno de los cuatro registros de enlace ($lr0..$lr3).
Los veinticuatro bits restantes forman la constante inmediata limm utilizados para obtener
6.4. Formato J-Type 46

---

## Page 49

Capítulo 6. Formatos de Instrucción Manual de Usuario RTM32
la dirección de destino mediante RA (vlimm). La reducción de un bit en el tamaño del
26
operando inmediato permite disponer de cuatro registros de enlace sin modificar el formato
base de la instrucción.
Ejemplo 1:
J 32
opcode = 00001
jump = 00 0000000000000000000100000
so = 00
elimm = 0 0000 0000 0000 0000 0010 0000 (32)
Suponiendo que la instrucción se encuentra en PC = 0x00001000, se obtiene:
RA=0x1000+4+(32×4)=0x1084
La ejecución continúa en la dirección 0x1084.
Ejemplo 2:
JAL −8
opcode = 00001
jump = 01 1111111111111111111111000
so = 01
elimm = 1 1111 1111 1111 1111 1111 1000 (−8)
Si la instrucción se encuentra en PC = 0x00001000, la CPU almacena previamente 0x1004
en el registro $ra y transfiere el control a la dirección calculada mediante la ecuación (4.9).
Ejemplo 3:
JALX $lr2, 12
opcode = 00001
jump = 1 10 000000000000000000001100
lr = 10
vlimm = 0000 0000 0000 0000 0000 1100 (12)
En este ejemplo el bit más significativo identifica la instrucción JALX, los dos bits siguientes
seleccionan el registro de enlace $lr2 y los restantes forman parte de la constante inmediata
limm. Antes del salto se almacena PC+4 en el registro de enlace seleccionado y la ejecución
continúa en la dirección calculada mediante la ecuación (4.9).
6.4. Formato J-Type 47

---

## Page 50

7. Instrucciones del Procesador STX4
7.1. Instrucciones aritméticas
Las instrucciones aritméticas realizan operaciones enteras sobre el contenido de los regis-
tros de propósito general. Dependiendo de la instrucción, los operandos pueden provenir de
dos registros o de un registro y un valor inmediato codificado dentro de la propia instrucción.
Esta familia está formada por tres instrucciones: ADD, SUB y ADDI. Las dos primeras
pertenecen al formato R, mientras que ADDI utiliza el formato I.
Cuandounainstrucciónempleaunoperandoinmediato,ésteseinterpretacomounentero
con signo de 16 bits y se extiende al tamaño nativo del procesador mediante el operador
E (imm,S) definido previamente.
16
Todas las instrucciones de esta familia actualizan las banderas de estado Z, N, O y C.
Estas indican, respectivamente, si el resultado es nulo, negativo, produjo desbordamiento
aritmético o generó un acarreo (en una suma) o un préstamo (en una resta). El desborda-
miento aritmético no genera una excepción y únicamente modifica el estado de la bandera
correspondiente.
7.1.1. ADD y SUB
Las instrucciones ADD y SUB realizan operaciones aritméticas entre dos registros de pro-
pósito general y almacenan el resultado en un tercer registro. Constituyen las operaciones
básicas para implementar cálculos enteros, actualización de contadores, manipulación de di-
recciones y, en general, cualquier expresión aritmética que involucre operandos almacenados
en registros.
Ambas instrucciones poseen el mismo formato y difieren únicamente en la operación
realizada por la ALU.
Instrucción Operación
ADD R[rd]=R[rs]+R[rt]
SUB R[rd]=R[rs]−R[rt]
Los operandos son interpretados como valores enteros contenidos en los registros fuente
rs y rt. El resultado se almacena en el registro destino indicado por el campo rd.
Sintaxis y ejemplos
add $t3, $t1, $t2
sub $t4, $t4, $t3
Si inicialmente t1 = 25, t2 = 17, t4 = 120 la ejecución produce t3 = 42 y t4 = 78. Al
finalizar cada instrucción se actualizan las banderas Z, N, O y C de acuerdo con el resultado
obtenido.
48

---

## Page 51

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
7.1.2. ADDI
La instrucción ADDI realiza la suma entre un registro y un operando inmediato con signo.
Seutilizaprincipalmenteparaincrementarodecrementarcontadores,ajustarpunteros,calcu-
lar desplazamientos y operar con constantes pequeñas sin necesidad de cargarlas previamente
en un registro.
Su comportamiento está definido por la siguiente operación:
R[rt]=R[rs]+E (imm,S)
17
El inmediato se interpreta como un entero con signo de 17 bits y se extiende al tamaño
nativo del procesador antes de efectuar la suma.
Sintaxis y ejemplos
addi $t2, $t2, −4
addi $t3, $zero, 100
Enelprimerejemplo,siinicialmentet2=100,luegodelaejecuciónt2=96.Enelsegundo
ejemplo, el registro t3 recibe el valor inmediato extendido a 32 bits (100).
Al igual que el resto de las instrucciones aritméticas, ADDI actualiza las banderas Z, N, O
y C y el desbordamiento aritmético no produce una excepción.
7.1.3. Actualización de banderas
Las instrucciones ADD, SUB y ADDI actualizan las banderas Z, N, O y C de acuerdo con el
resultado de la operación aritmética. La bandera Z se activa cuando el resultado obtenido es
cero, mientras que la bandera N refleja el bit más significativo del resultado, indicando una
interpretación negativa en complemento a dos. Las banderas C y O representan condiciones
diferentes. La bandera C indica un acarreo fuera del tamaño del operando en una suma o un
préstamoenunaresta,porloqueestáasociadaalainterpretaciónsinsignodelosvalores.En
cambio, la bandera O indica que el resultado no puede representarse correctamente utilizando
complemento a dos, por lo que está asociada a la interpretación con signo.
La siguiente suma de dos operandos de 32 bits:
0xFFFFFFFF+1=0x00000000
produce Z = 1, C = 1 y O = 0. El acarreo indica que la suma excedió el rango de repre-
sentación sin signo, pero no existe desbordamiento con signo porque el resultado equivalente
es cero (-1 + 1).
En cambio:
0x7FFFFFFF+1=0x80000000
produce Z = 0, C = 0 y O = 1. En este caso el resultado no puede representarse como un
entero positivo con signo, por lo que se activa la bandera de desbordamiento.
En las operaciones de resta, la bandera C indica que la operación generó un préstamo
(borrow) fuera del bit más significativo del operando. Se activa cuando el minuendo es menor
que el sustraendo bajo una interpretación sin signo.
7.1. Instrucciones aritméticas 49

---

## Page 52

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
Por ejemplo, considerando operandos de 32 bits:
3−5=0xFFFFFFFE
Laoperaciónrequiereunpréstamo,porloqueC=1.Elresultadoalmacenadocorresponde
a la representación en complemento a dos de −2, pero la bandera C refleja únicamente la
condición de préstamo de la operación sin signo.
@ NOTA
Esta definición permite utilizar la bandera C para operaciones aritméticas sin signo,
mientras que la bandera O permite detectar condiciones de desbordamiento en aritmé-
tica con signo.
La separación entre las banderas C y O permite implementar decisiones aritméticas más
complejas. Mientras que C permite evaluar condiciones sobre valores sin signo, O permite
detectar resultados inválidos en aritmética con signo. Las instrucciones de consulta de estado
permiten utilizar estas condiciones directamente desde un programa.
Por ejemplo, para determinar si un valor sin signo contenido en $1 es menor que otro
contenido en $2, puede realizarse la resta $1−$2 y consultar posteriormente la bandera C. De
estaforma,lamismaoperaciónaritméticautilizadaparaobtenerunresultadopuedeproducir
información adicional sobre la relación entre los operandos.
7.2. Instrucciones lógicas
Las instrucciones lógicas realizan operaciones booleanas bit a bit sobre el contenido de los
registros de propósito general. Estas operaciones permiten manipular máscaras, seleccionar
campos individuales dentro de una palabra, combinar valores y modificar grupos de bits
mediante operaciones simples.
Las operaciones lógicas pueden utilizar dos operandos almacenados en registros o un
registro junto con un operando inmediato codificado en la instrucción. Las instrucciones con
operandos inmediatos utilizan diferentes formas de extensión según el tipo de operación,
permitiendo trabajar tanto con máscaras de bits inferiores como con valores ubicados en la
mitad superior del registro.
Las instrucciones lógicas actualizan las banderas de estado Z y N. La bandera Z se acti-
va cuando el resultado obtenido es cero, mientras que N refleja el bit más significativo del
resultado. Las banderas O y C no son modificadas por estas instrucciones.
La familia está formada por las instrucciones AND, OR, XOR, NOR, ANDI, ANI, ORI, XORI,
ANH, ORH y XORH.
7.2.1. Operaciones lógicas entre registros
Las instrucciones AND, OR, XOR y NOR realizan operaciones lógicas bit a bit entre dos
registros fuente y almacenan el resultado en un registro destino.
TodasestasinstruccionesutilizanelformatoRysediferencianúnicamenteenlaoperación
lógica aplicada por la ALU.
7.2. Instrucciones lógicas 50

---

## Page 53

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
Instrucción Operación
AND R[rd]=R[rs]&R[rt]
OR R[rd]=R[rs]∣R[rt]
XOR R[rd]=R[rs]⊕R[rt]
NOR R[rd]=¬(R[rs]∣R[rt])
Estasinstruccionessonutilizadashabitualmenteparaimplementarmáscaras,combinación
de campos, inversión de bits y operaciones booleanas generales.
Sintaxis y ejemplos
and $t0, $t1, $t2
or $t3, $t1, $t2
xor $t4, $t1, $t2
nor $t5, $t1, $t2
Si t1 = 0xFF00FF00 y t2 = 0x0F0F0F0F entonces para la instrucción AND t0 = 0x0F000F00.
7.2.2. Diseño de las operaciones lógicas inmediatas
RTM32 distingue dos familias de operaciones lógicas inmediatas:
ANDI, junto con ORI y XORI, utilizan la semántica clásica de las arquitecturas RISC,
dondeeloperandoinmediatorepresentaunaconstanteextendidaaltamañodepalabra.
ANI, junto con ORI, XORI, ANH, ORH y XORH, interpretan el operando inmediato como
un modificador de media palabra, preservando automáticamente la mitad opuesta del
registro.
Las instrucciones ORI y XORI pertenecen simultáneamente a ambas familias debido a que
la extensión con ceros conserva naturalmente la mitad superior del registro al aplicar las ope-
raciones OR y XOR. En cambio, la operación AND requiere dos instrucciones diferenciadas
(ANDI y ANI) porque las extensiones con ceros y con unos producen semánticas distintas.
Justificación del diseño Las instrucciones ORI y XORI pertenecen simultáneamente a
ambasfamilias.Enestasoperacioneslaextensióndelinmediatoconcerospermiterepresentar
una constante de palabra completa y, al mismo tiempo, preservar automáticamente la mitad
superior del registro debido a las propiedades del álgebra booleana:
x∨0=x
x⊕0=x
Por el contrario, la operación AND no posee esta propiedad. La extensión con ceros
produce una máscara de palabra completa, mientras que la extensión con unos preserva
automáticamente la mitad superior del registro:
x∧0=0
7.2. Instrucciones lógicas 51

---

## Page 54

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
x∧1=x
Por este motivo RTM32 define dos instrucciones distintas para la operación AND in-
mediata: ANDI, orientada al uso de máscaras completas siguiendo la semántica clásica de
las arquitecturas RISC, y ANI, orientada a la modificación selectiva de la mitad inferior del
registro preservando automáticamente la mitad superior.
7.2.3. Operaciones lógicas inmediatas
LasinstruccionesANDI,ANI,ORIyXORIrealizanoperacioneslógicasentreunregistroyun
valor inmediato de 16 bits. El valor inmediato es extendido al tamaño nativo del procesador
antes de efectuar la operación. La extensión utilizada depende de la instrucción.
Instrucción Operación
ANDI R[rt]=R[rs]&E (imm,0)
16
ANI R[rt]=R[rs]&E (imm,1)
16
ORI R[rt]=R[rs]∣E (imm,0)
16
XORI R[rt]=R[rs]⊕E (imm,0)
16
La extensión utilizada por ANI, ORI y XORI garantiza que únicamente se modifiquen los
16 bits menos significativos del registro, preservando el contenido de la mitad superior.
Sintaxis y ejemplos
ani $t0, $t1, 0xFF00
ori $t2, $t3, 0x5678
xori $t4, $t5, 0xFFFF
Por ejemplo si t3 = 0x12340000 entonces la instrucción ORI t2 = 0x12345678.
La instrucción ANDI extiende el valor inmediato con ceros, sin preservar los valores de los
bits más significativos de la operación. Permite crear máscaras de palabra completa. Esta
semántica coincide con la utilizada por numerosas arquitecturas RISC modernas y facilita la
generación eficiente de código por parte de los compiladores.
andi $t0, $t1, 0xFF
En el ejemplo de la instrucción anterior la máscara 0xFF se extiende al valor 0x000000FF,
permitiendo enmascaras los 8 bits menos significativos de $t1.
7.2.4. Operaciones lógicas inmediatas en la parte alta
Las instrucciones ANH, ORH y XORH constituyen la versión sobre la mitad superior de
las operaciones lógicas inmediatas orientadas a campos. Permiten modificar únicamente los
16 bits más significativos del registro, preservando la mitad inferior. La operación se realiza
utilizando una constante de 32 bits cuyo valor inmediato ocupa la mitad superior de la
palabra. La mitad inferior se completa automáticamente con unos o ceros según la operación
lógica aplicada.
7.2. Instrucciones lógicas 52

---

## Page 55

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
Instrucción Operación
ANH R[rt]=R[rs]&H (imm,1)
16
ORH R[rt]=R[rs]∣H (imm,0)
16
XORH R[rt]=R[rs]⊕H (imm,0)
16
Laconcatenaciónutilizaraporestasinstruccionesgarantizaqueúnicamentesemodifiquen
los 16 bits más significativos del registro, preservando el contenido de la mitad inferior.
Estas instrucciones permiten modificar directamente la mitad superior de un registro sin
utilizar desplazamientos adicionales.
7.3. Construcción de constantes
LainstrucciónLCIpermiteconstruirvaloresde32bitsmediantelacombinacióndeunope-
rando inmediato de 16 bits con la mitad inferior de un registro fuente. Esta operación resulta
especialmente útil para generar constantes, direcciones y valores que no pueden representarse
mediante un único valor inmediato de 16 bits. A diferencia del resto de las instrucciones
con operandos inmediatos, LCI no realiza una extensión del valor inmediato. En su lugar,
utiliza el operador de concatenación C () definido previamente para formar el resultado. La
16
instrucción LCI no modifica las banderas de estado.
7.3.1. LCI
La operación realizada por la instrucción está definida por:
R[rt]=C (imm,R[rs])
16
Los 16 bits del operando inmediato constituyen la mitad más significativa del resultado,
mientras que los 16 bits menos significativos se obtienen del registro fuente.
Sintaxis y ejemplos
lci $t0, $zero, 0x1234
Dado que zero está cableado a 0 la ejecución produce que t0 = 0x12340000.
La instrucción LCI puede combinarse con instrucciones lógicas inmediatas para construir
constantes completas de 32 bits. Por ejemplo el siguiente código carga en t0 = 0x12345678.
lci $t0, $zero, 0x1234
ori $t0, $t0, 0x5678
También es posible construir la misma constante en el orden inverso obteniéndose nueva-
mente en t0 = 0x12345678
ori $t0, $zero, 0x5678
lci $t0, $t0, 0x1234
Esta propiedad proporciona flexibilidad para la generación y reorganización de secuencias
de instrucciones que construyen constantes de 32 bits.
7.3. Construcción de constantes 53

---

## Page 56

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
7.4. Instrucciones de desplazamiento
Las instrucciones de desplazamiento permiten desplazar o rotar los bits contenidos en
un registro de propósito general. Dependiendo de la instrucción, la cantidad de posiciones a
desplazar puede especificarse mediante un parámetro inmediato de 5 bits o tomarse de los
cinco bits menos significativos de un registro.
Esta familia está formada por ocho instrucciones. Las instrucciones SLL, SRL, SRA y RLL
utilizan un desplazamiento inmediato, mientras que SLLR, SRLR, SRAR y RLLR obtienen el
desplazamiento desde un registro.
En las variantes controladas por registro únicamente se consideran los cinco bits menos
significativos del registro fuente (rs), por lo que el desplazamiento efectivo pertenece al
intervalo comprendido entre 0 y 31 posiciones.
Las instrucciones de esta familia no modifican las banderas de estado.
7.4.1. Desplazamientos lógicos
Las instrucciones SLL y SRL realizan desplazamientos lógicos hacia la izquierda y hacia la
derecha, respectivamente. En ambos casos, las posiciones vacantes son completadas con ceros
y los bits desplazados fuera del registro son descartados.
Instrucción Operación
SLL R[rd]=R[rt]≪param
SRL R[rd]=R[rt]≫param
Matemáticamente, realizar un desplazamiento lógico a la izquierda de un valor X por n
posiciones es estrictamente equivalente a una multiplicación entera por una potencia de dos,
truncada a la capacidad del registro:
Y =X ⋅2n (m´od 232) (7.1)
MSB(31) LSB(0)
Bits del registro original
Bits perdidos
Bits del registro desplazados 0
Desplazamiento a la izquierda Inyección de ceros
Figura 7.1: Desplazamiento lógico hacia la izquierda (SLL).
Losdesplazamientoslógicosaladerechaseutilizannormalmenteparaoperarconnúmeros
enteros“sinsigno”(unsignedintegerdivision).Desplazarunnúmerosinsignohacialaderecha
n posiciones equivale a una división entera:
X
Y =⌊ ⌋ (7.2)
2n
Las figuras 7.1 y 7.2 muestra el funcionamiento de los desplazamientos lógicos.
7.4. Instrucciones de desplazamiento 54

---

## Page 57

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
MSB(31) LSB(0)
Bits del registro original
Bits perdidos
0 Bits del registro desplazados
Inyección de ceros Desplazamiento a la derecha
Figura 7.2: Desplazamiento lógico hacia la derecha (SRL).
Sintaxis y ejemplos
sll $t0, $t1, 4
srl $t2, $t0, 8
Si inicialmente t1 = 0x12345678 la ejecución produce t0 = 0x23456780 y posteriormente
t2 = 0x00234567
7.4.2. Desplazamiento aritmético
La instrucción SRA realiza un desplazamiento hacia la derecha preservando el signo del
operando.Lasposicionesvacantessecompletanreplicandoelbitmássignificativodelregistro.
R[rd]=R[rt]⋙param
La Figura 7.3 ilustra el comportamiento del desplazamiento aritmético.
MSB(31) LSB(0)
S Bits del registro original
Bits perdidos
S S Bits del registro desplazados
Inyección del signo Desplazamiento a la derecha
Figura 7.3: Desplazamiento aritmético hacia la derecha (SRA).
Sintaxis y ejemplos
sra $t0, $t1, 3
Si inicialmente t1 = 0xFFFFFF80 la ejecución produce t0 = 0xFFFFFFF0.
7.4.3. Rotación
La instrucción RLC realiza una rotación circular hacia la izquierda. A diferencia de un
desplazamientológico,losbitsqueabandonanelextremomássignificativodelregistrovuelven
a introducirse por el extremo menos significativo, por lo que no se pierde información.
R[rd]=R[rt]≪ ↷ param
La Figura 7.4 muestra el funcionamiento de esta operación.
7.4. Instrucciones de desplazamiento 55

---

## Page 58

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
MSB(31) LSB(0)
Bits del registro original
Bits del registro desplazados
Desplazamiento a la izquierda
Figura 7.4: Rotación circular hacia la izquierda (RLC).
Sintaxis y ejemplos
rlc $t0, $t1, 8
Si inicialmente t1 = 0x12345678 la ejecución produce t0 = 0x34567812.
7.4.4. Variantes controladas por registro
Las instrucciones SLLR, SRLR, SRAR y RLCR realizan las mismas operaciones que sus va-
riantes con desplazamiento inmediato. La diferencia consiste en que la cantidad de posiciones
a desplazar se obtiene de los cinco bits menos significativos del registro rs.
Instrucción Operación
SLLR R[rd]=R[rt]≪R[rs]
[4∶0]
SRLR R[rd]=R[rt]≫R[rs]
[4∶0]
SRAR R[rd]=R[rt]⋙R[rs]
[4∶0]
RLCR R[rd]=R[rt]≪ ↷ R[rs]
[4∶0]
Sintaxis y ejemplos
sllr $t0, $a0, $t1
rlcr $t2, $a0, $t1
Si inicialmente a0 = 8 y t1 = 0x02000001 la primera instrucción desplaza el contenido de
t1 ocho posiciones hacia la izquierda, mientras que la segunda realiza una rotación circular
a la izquierda de la misma magnitud quedando t2 = 0x00000012.
@ NOTA
Laarquitecturaimplementaúnicamentelarotacióncircularhacialaizquierdamedian-
te las instrucciones RLC y RLCR. Esta decisión simplifica el conjunto de instrucciones
sin reducir su capacidad funcional, ya que una rotación hacia la derecha puede ob-
tenerse mediante una rotación hacia la izquierda de 32−n posiciones. De esta forma
se evita incorporar instrucciones redundantes manteniendo la simetría del conjunto de
operaciones de desplazamiento.
7.5. Instrucciones de comparación
Las instrucciones de comparación permiten evaluar la relación de orden entre dos operan-
dosyalmacenarelresultadodirectamenteenunregistrodepropósitogeneral.Adiferenciade
7.5. Instrucciones de comparación 56

---

## Page 59

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
lasinstruccionesaritméticas,estasinstruccionesnoproducenunresultadonuméricoderivado
de los operandos, sino un valor booleano representado mediante un entero.
Esta familia está formada por cuatro instrucciones. SLT y SLTU comparan el contenido de
dos registros, mientras que SLTI y SLTIU comparan un registro con un operando inmediato.
El resultado de la comparación siempre es un valor entero. Si la condición evaluada es
verdadera, el registro destino recibe el valor 1; en caso contrario recibe el valor 0.
Las instrucciones de esta familia no modifican las banderas de estado.
7.5.1. Comparación entre registros
Las instrucciones SLT y SLTU comparan el contenido de dos registros de propósito general
y almacenan el resultado de la comparación en un tercer registro.
La diferencia entre ambas instrucciones radica en la interpretación de los operandos.
SLT realiza una comparación con signo utilizando la representación en complemento a dos,
mientras que SLTU interpreta ambos operandos como enteros sin signo mediante el operador
U() definido previamente.
Instrucción Operación
SLT R[rd]=(R[rs]<R[rt]) ? 1∶0
SLTU R[rd]=(U(R[rs])<U(R[rt])) ? 1∶0
Sintaxis y ejemplos
slt $t0, $a0, $a1
sltu $t1, $a2, $a3
Si inicialmente a0 = -8 y a1 = 5 la primera comparación produce t0 = 1 ya que −8 < 5.
En cambio, SLTU interpreta ambos operandos como enteros sin signo, por lo que resulta
adecuada para comparar direcciones de memoria, tamaños, índices y otros valores que no
poseen interpretación con signo.
7.5.2. Comparación con operandos inmediatos
Las instrucciones SLTI y SLTIU realizan la comparación entre un registro y un operando
inmediato codificado dentro de la instrucción. En SLTI el operando inmediato se interpreta
como un entero con signo y se extiende mediante el operador E (imm,S), mientras que
17
SLTIU realiza una extensión con ceros utilizando E (imm,0) para efectuar una comparación
17
sin signo.
Instrucción Operación
SLTI R[rt]=(R[rs]<E (imm,S)) ? 1∶0
17
SLTIU R[rt]=(U(R[rs])<U(E (imm,0))) ? 1∶0
17
Sintaxis y ejemplos
slti $t0, $s0, 100
sltiu $t1, $s1, 1024
7.5. Instrucciones de comparación 57

---

## Page 60

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
Si inicialmente s0 = 75 la ejecución produce t0 = 1 ya que 75<100.
La instrucción SLTIU resulta especialmente útil para verificar si un valor sin signo perte-
nece a un determinado rango o es inferior a un límite constante.
7.5.3. Resultados booleanos
El resultado producido por las instrucciones de comparación constituye un valor booleano
almacenado en un registro de propósito general. A diferencia de las arquitecturas que repre-
sentanelresultadodeunacomparaciónexclusivamentemediantebanderasdeestado,RTM32
permite utilizar directamente dicho valor como un operando más dentro del programa.
El resultado de una comparación puede almacenarse en memoria, transferirse como argu-
mento de una función, combinarse mediante instrucciones lógicas o emplearse posteriormente
para controlar el flujo de ejecución.
Por ejemplo:
slt $t0, $a0, $a1
beq $t0, $zero, mayor_igual
Enestecaso,lainstrucciónSLTgeneraelvalorbooleanocorrespondientealacomparación,
mientras que la instrucción de salto, que se verá más adelante, utiliza dicho resultado para
decidir el flujo de ejecución.
7.6. Instrucciones de acceso a memoria
Lasinstruccionesdeaccesoamemoriapermitentransferirdatosentrelamemoriaprincipal
y los registros de propósito general. En RTM32 todas las operaciones de carga y almacena-
miento se realizan exclusivamente mediante este conjunto de instrucciones; las operaciones
aritméticas y lógicas nunca operan directamente sobre memoria.
La arquitectura implementa un modelo Load/Store, donde las instrucciones de carga co-
piandatosdesdememoriahaciaunregistro,mientrasquelasinstruccionesdealmacenamiento
realizan la operación inversa.
RTM32 soporta accesos de palabra (32 bits), media palabra (16 bits) y byte (8 bits),
incluyendo variantes con y sin extensión de signo. Además, proporciona dos mecanismos para
calcular la dirección efectiva:
Direccionamiento indexado mediante un registro base y un desplazamiento inmediato
(EA()).
Direccionamiento indexado mediante dos registros (EAX()).
Las instrucciones de carga actualizan las banderas de estado Z y N de acuerdo con el
valor cargado en el registro destino. Las instrucciones de almacenamiento no modifican las
banderas del procesador.
La familia está formada por las instrucciones LW, LWX, SW, LH, LHU, LHX, LHUX, SH, LB, LBU,
LBX, LBUX y SB.
7.6. Instrucciones de acceso a memoria 58

---

## Page 61

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
7.6.1. Carga y almacenamiento de palabras
Las instrucciones de palabra transfieren un valor completo de 32 bits entre la memoria y
un registro de propósito general.
Instrucción Operación
LW R[rt]=M[EA(rs,imm)]
LWX R[rt]=M[EAX(rs,rd)]
SW M[EA(rs,imm)]=R[rt]
Las instrucciones LW y SW utilizan direccionamiento indexado con desplazamiento inme-
diato, mientras que LWX calcula la dirección efectiva utilizando dos registros.
Sintaxis y ejemplos
lw $t0,8($sp)
lwx $t1,$s0,$a0
sw $t2,−4($fp)
7.6.2. Carga y almacenamiento de medias palabras
Las instrucciones de media palabra permiten acceder a datos de 16 bits.
Lasvariantesdecargasediferencianúnicamenteporelmecanismoutilizadoparaextender
el dato leído hasta el tamaño nativo del procesador.
Instrucción Operación
LH R[rt]=E (M[EA(rs,imm)],S)
16
LHU R[rt]=E (M[EA(rs,imm)],0)
16
LHX R[rt]=E (M[EAX(rs,rd)],S)
16
LHUX R[rt]=E (M[EAX(rs,rd)],0)
16
SH M[EA(rs,imm)]=R[rt]
[15∶0]
Las instrucciones LH y LHX realizan extensión con signo, mientras que LHU y LHUX rea-
lizan extensión con ceros. La instrucción SH almacena únicamente los dieciséis bits menos
significativos del registro fuente.
Sintaxis y ejemplos
lh $t0,2($sp)
lhu $t1,4($sp)
lhx $t2,$s0,$a0
lhux $t3,$s1,$a1
sh $t4,6($sp)
7.6. Instrucciones de acceso a memoria 59

---

## Page 62

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
7.6.3. Carga y almacenamiento de bytes
Las instrucciones de byte permiten acceder individualmente a cada uno de los bytes
almacenados en memoria.
Al igual que en las instrucciones de media palabra, las variantes de carga se diferencian
únicamente por el tipo de extensión aplicado al dato leído.
Instrucción Operación
LB R[rt]=E (M[EA(rs,imm)],S)
8
LBU R[rt]=E (M[EA(rs,imm)],0)
8
LBX R[rt]=E (M[EAX(rs,rd)],S)
8
LBUX R[rt]=E (M[EAX(rs,rd)],0)
8
SB M[EA(rs,imm)]=R[rt]
[7∶0]
Las instrucciones LB y LBX preservan el signo del byte leído, mientras que LBU y LBUX
completanlosbitssuperioresconceros.LainstrucciónSBalmacenaúnicamenteelbytemenos
significativo del registro fuente.
Sintaxis y ejemplos
lb $a0,0($s0)
lbu $a1,1($s0)
lbx $v0,$s1,$t0
lbux $v1,$s2,$t1
sb $t2,3($sp)
. ATENCIÓN
Las instrucciones que operan sobre palabras requieren que la dirección efectiva se
encuentre alineada a cuatro bytes, mientras que las instrucciones de media palabra
requieren alineación a dos bytes. Las instrucciones de acceso a bytes no poseen restric-
ciones de alineación. Cuando una instrucción utiliza una dirección que no satisface los
requisitos de alineación establecidos por la arquitectura, la CPU genera la excepción
correspondiente.
7.7. Instrucciones de transferencia del control
Las instrucciones de transferencia del control modifican el valor del contador de programa
(PC),permitiendoalterarlasecuencianormaldeejecución.Estafamiliaimplementatantosal-
tos condicionales como incondicionales, llamadas a procedimientos y transferencias indirectas
de control.
RTM32 utiliza dos mecanismos para calcular la dirección de destino:
Direccionamiento relativo al contador de programa mediante la función RA().
Direccionamiento relativo a un registro base mediante la función AA().
7.7. Instrucciones de transferencia del control 60

---

## Page 63

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
Las instrucciones de salto no modifican las banderas de estado del procesador.
La familia está formada por las instrucciones BEQ, BNE, BLT, BGE, BLTU, BGEU, J, JAL,
JALX, JR, JALR y JALRX.
7.7.1. Saltos condicionales
Las instrucciones de salto condicional comparan dos registros y modifican el contador de
programa únicamente cuando la condición evaluada resulta verdadera. El destino del salto
se calcula mediante la función RA(), utilizando un desplazamiento relativo al contador de
programa.
Instrucción Condición
BEQ R[rs]=R[rt]
BNE R[rs]≠R[rt]
BLT R[rs]<R[rt]
BGE R[rs]≥R[rt]
BLTU U(R[rs])<U(R[rt])
BGEU U(R[rs])≥U(R[rt])
LascomparacionesBLTy BGEinterpretanambosoperandoscomoenterosconsigno,mien-
tras que BLTU y BGEU realizan la comparación sobre valores sin signo.
Simetría de las comparaciones
RTM32 implementa únicamente las comparaciones “menor que” y “mayor o igual que”,
tanto para enteros con signo como sin signo.
Esta decisión reduce el número de instrucciones necesarias sin disminuir la capacidad
expresiva de la arquitectura. Las relaciones restantes pueden obtenerse invirtiendo el orden
de los operandos o utilizando la condición complementaria.
Por ejemplo,
A>B
es equivalente a
B <A
mientras que
A≤B
es equivalente a
B ≥A.
Deestaformalaarquitecturamantieneunconjuntodecomparacionesmínimoysimétrico,
simplificando el decodificador y reduciendo el espacio de codificación requerido por la ISA.
7.7. Instrucciones de transferencia del control 61

---

## Page 64

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
Sintaxis y ejemplos
beq $t0,$t1,label
bne $a0,$zero,error
blt $s0,$s1,loop
bge $sp,$fp,exit
bltu $t0,$t1,unsigned_cmp
bgeu $t2,$t3,unsigned_end
7.7.2. Saltos relativos incondicionales
Las instrucciones de salto relativo modifican el contador de programa sin realizar compa-
raciones previas. El destino se calcula mediante la función RA().
Instrucción Operación
J R[0]=PC+4; PC =RA(limm)
JAL R[1]=PC+4; PC =RA(limm)
JALX R[lrx]=PC+4; PC =RA(llimm)
La instrucción J realiza un salto incondicional sin conservar la dirección de retorno.
Las instrucciones JAL y JALX almacenan previamente la dirección de la siguiente instruc-
ción en un registro de enlace antes de efectuar el salto. Mientras JAL utiliza el registro de
enlace predeterminado, JALX permite seleccionar cualquiera de los registros de enlace defini-
dos por la arquitectura.
Sintaxis y ejemplos
j loop
jal printf
jalx $lr2,handler
7.7.3. Saltos indirectos incondicionales
Lasinstruccionesdesaltoindirectocalculaneldestinoapartirdelcontenidodeunregistro
base y un desplazamiento inmediato mediante la función AA().
Instrucción Operación
JR R[0]=PC+4; PC =AA(rs,imm)
JALR R[1]=PC+4; PC =AA(rs,imm)
JALRX R[lrx]=PC+4; PC =AA(rs,llimm)
Este mecanismo resulta apropiado para implementar llamadas indirectas, despacho me-
diante tablas de funciones, punteros a funciones y otras formas de transferencia dinámica del
control.
Al igual que en los saltos relativos, las variantes con enlace almacenan la dirección de
retorno antes de actualizar el contador de programa.
7.7. Instrucciones de transferencia del control 62

---

## Page 65

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
Sintaxis y ejemplos
jr $t0,0
jalr $s0,8
jalrx $lr3,$gp,−4
@ NOTA
Todaslasinstruccionesdetransferenciadelcontrolutilizandireccionesrelativas,yasea
respectodelcontadordeprograma(RA())odeunregistrobase(AA()).Laarquitectura
no incorpora instrucciones que codifiquen direcciones absolutas dentro de la propia
instrucción.
7.8. Instrucciones de sistema
Lasinstruccionesdesistemapermiteninteractuarconrecursosinternosdelprocesadorque
noformanpartedelconjuntoderegistrosdepropósitogeneral.Estasinstruccionesseutilizan
para acceder al estado de la CPU, modificar registros especiales y realizar la transición entre
los modos de ejecución de usuario y supervisor.
A diferencia del resto de las instrucciones de la arquitectura, las instrucciones de siste-
ma operan sobre recursos privilegiados cuyo acceso puede estar restringido por el modo de
ejecución actual del procesador.
La familia está formada por las instrucciones CFS, CTS, TRAP y RFT.
7.8.1. Acceso a registros especiales
Las instrucciones CFS (Copy From Special) y CTS (Copy To Special) permiten transferir
información entre los registros de propósito general y los registros especiales del procesador.
Ambas instrucciones utilizan el formato R. El campo param identifica el registro especial
involucrado en la operación.
Instrucción Operación
CFS R[rs]=S[param]
CTS S[param]=R[rs]
Estas instrucciones constituyen el mecanismo general utilizado por la arquitectura para
leer y modificar el estado interno del procesador. La descripción de cada registro especial y
de sus privilegios de acceso se presenta en el capítulo correspondiente.
Sintaxis y ejemplos
cfs $t0,PSW
cts $t1,EPC
7.8. Instrucciones de sistema 63

---

## Page 66

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
7.8.2. Generación de excepciones
LainstrucciónTRAPprovocaunaexcepciónsoftwarequetransfiereelcontrolalmanejador
de excepciones correspondiente (normalmente el sistema operativo).
Antes de modificar el flujo de ejecución, la CPU almacena la dirección de la siguiente
instrucción en el registro especial EPC y guarda el modo de ejecución actual en el registro
ESR. A continuación, conmuta al modo supervisor y obtiene la dirección del manejador co-
rrespondiente mediante la función TV() y transfiere el control a dicha rutina.
Instrucción Operación
TRAP EPC =PC+4;
ESR=PSW;
PSW.MODE =Supervisor;
PSW.IE =0;
PSW.TE =0;
PC =M[TV(param)]
El operando inmediato selecciona una entrada de la tabla de vectores, por lo que una
instrucción TRAP puede invocar cualquier manejador definido por la arquitectura. De esta
forma, las excepciones software y las interrupciones hardware comparten una única tabla de
vectores, diferenciándose únicamente por la entrada utilizada.
La ejecución de TRAP deshabilita automáticamente la aceptación de interrupciones y de
nuevas excepciones software. El manejador puede rehabilitarlas modificando el registro PSW
mediante las instrucciones CFS y CTS.
Durante esta operación el procesador abandona el modo usuario y continúa la ejecución
en modo supervisor, permitiendo que el núcleo del sistema operativo o el correspondiente
manejador atienda la excepción o el servicio solicitado.
La instrucción puede ejecutarse siempre desde modo usuario. Cuando el procesador ya
se encuentra ejecutando en modo supervisor, la ejecución de TRAP requiere que el bit TE
(Supervisor Trap Enable) del registro PSW se encuentre habilitado. Esta restricción evita
excepciones software recursivas no deseadas. En ambos casos la CPU preserva el modo de
ejecución previo para que pueda ser restaurado posteriormente por la instrucción RFT.
Sintaxis y ejemplos
trap 5
7.8.3. Retorno de excepción
La instrucción RFT (Return From Trap) finaliza la ejecución del manejador de excepción
y restaura el contexto de ejecución previamente almacenado por la CPU.
Instrucción Operación
RFT PSW =ESR;
PC =EPC
7.8. Instrucciones de sistema 64

---

## Page 67

Capítulo 7. Instrucciones del Procesador STX4 Manual de Usuario RTM32
Durante su ejecución, la CPU restaura el modo de ejecución almacenado en el registro
ESR y recupera el valor del contador de programa desde EPC. Como consecuencia, la ejecución
continúa exactamente en la instrucción siguiente a la que originó la excepción.
La instrucción RFT constituye el único mecanismo arquitectónico para abandonar el modo
supervisor y retornar al contexto previamente interrumpido.
Sintaxis y ejemplos
rft
@ NOTA
La arquitectura utiliza una tabla de vectores unificada para excepciones e interrupcio-
nes.LasexcepcionessoftwaregeneradasmedianteTRAPyloseventoshardwareutilizan
el mismo mecanismo de despacho, diferenciándose únicamente por la entrada de la ta-
bla de vectores seleccionada.
7.9. Pseudoinstrucciones
El ensamblador de referencia ofrece pseudoinstrucciones INC y DEC para simplificar ope-
raciones aritméticas frecuentes. Estas no forman parte del conjunto de instrucciones de la
arquitectura, sino que son traducidas automáticamente a una o más instrucciones reales du-
rante el ensamblado. Su sintaxis se encuentra documentada en la tabla 7.1.
Familia Pseudo Expansión Operación
Artimética inc r addi r, r, 1 R[r]=R[r]+1
dec r addi r, r, -1 R[r]=R[r]−1
inc r, i addi r, r, i R[r]=R[r]+i
dec r, i addi r, r, -i R[r]=R[r]−i
neg r sub r, $zero, r R[r]=0−R[r]
neg r, s sub r, $zero, s R[r]=0−R[s]
Lógica not r nor r, $zero, r R[r]=¬(0∣R[r])
not r, s nor r, $zero, s R[r]=¬(0∣R[s])
clr r xor r, r, r R[r]=R[r]⊕R[r]
cpy r, s or r, $zero, s R[r]=0∣R[s]
lui r, i lci r, $zero, i R[r]=C (i,0)
16
nop sll $zero, $zero, 0
li r, i ori r, $zero, i R[r]=0∣i
Tabla 7.1: Expansión de pseudoinstrucciones simples.
El uso de estas pseudoinstrucciones mejora la legibilidad del código fuente, aunque todas
ellas son equivalentes a una instrucción ADDI
7.9. Pseudoinstrucciones 65

---

## Page 68

Parte IV
Operación del Sistema
66

---

## Page 69

8. Excepciones
PRONTO ...
67

---

## Page 70

Parte V
Dispositivos y Entrada/Salida
68

---

## Page 71

9. Entrada/Salida
PRONTO ...
69

---

## Page 72

Parte VI
Interface de Software
70

---

## Page 73

Manual de Usuario RTM32
9.1. Compilador RTM32AS
PRONTO ...
9.1. Compilador RTM32AS 71

---

## Page 74

Parte VII
Verificación y Debugging
72

---

## Page 75

10. Interfaz del Depurador (Modo Debug)
10.1. Activación del Entorno Interactivo
Elemuladorarrancapordefectoenmododirectodealtavelocidad.Parainiciarlaconsola
interactiva de depuración comandada por terminal, utilice los modificadores de lanzamiento:
./rtm32_emu −d
# O alternativamente:
./rtm32_emu −−debug
10.2. Diccionario de Comandos Aceptados
La consola de comandos responde al prompt RTM32> mediante una interfaz síncrona. Los
comandos implementados son los siguientes:
10.2.1. Comando G (Ejecución Continua o Limitada)
Sintaxis: G x [n]
EstableceelPCenladirecciónhexadecimalxeinicialaejecución.Siseespecificaelparámetro
opcional n, la CPU procesará exactamente n instrucciones antes de pausarse y devolver el
control al depurador. Si se omite n, corre de forma indefinida hasta el final o una instrucción
de detención.
10.2.2. Comando D R (Vuelco de Registros)
Sintaxis: D R[x]
Si se ejecuta de forma aislada como D R, vuelca por pantalla el contenido actual de los 32
registros y el contador de programa (PC). Si se indica un índice específico (ej. D R5), imprime
el valor único del registro seleccionado.
10.2.3. Comando D M (Vuelco de Memoria)
Sintaxis: D Mx [n]
Muestra el contenido hexadecimal de la palabra en la dirección x. Si se proporciona n, realiza
un volcado en ráfaga consecutiva de n direcciones de memoria.
10.2.4. Comando W (Escritura en Memoria)
Sintaxis: W x v
Escribe de forma forzada el valor hexadecimal v en la dirección de memoria especificada por
x.
10.2.5. Comandos S y L (Gestión de Estados e Instantáneas)
Sintaxis: S filename / L filename
Permiten serializar y deserializar de forma directa el bloque binario completo de la estruc-
tura de datos CPU (incluyendo registros, estado de periféricos seriales y el bloque completo
73

---

## Page 76

Capítulo 10. Interfaz del Depurador (Modo Debug) Manual de Usuario RTM32
de memoria RAM) hacia o desde el archivo local indicado por filename, garantizando la
persistencia completa de las sesiones de depuración.
10.2. Diccionario de Comandos Aceptados 74

---

## Page 77

A. Notation
Notación Descripción
R[x] Registro de propósito general con índice x.
S[x] Registro especial con índice x.
M[x] Contenido de la posición de memoria ubicada en la direc-
ción x.
PC Contador de programa.
EPC Contador de programa almacenado durante una excep-
ción.
x Selección del campo de bits comprendido entre las posi-
[m∶n]
ciones m y n.
x∥y Concatenación de las secuencias binarias x e y.
E (y,z) Extensión de un operando de x bits mediante el mecanis-
x
mo z ∈{S,0,1}.
C (y,z) Concatenación de los x bits de y con los x bits menos
x
significativos de z.
U(x) Interpretación de x como entero sin signo.
EA(rs,imm) Dirección efectiva para accesos a memoria con desplaza-
miento inmediato.
EAX(rs,rd) Dirección efectiva calculada a partir de dos registros.
RA (imm) Dirección relativa al contador de programa.
x
AA (rs,imm) Dirección de salto relativa a un registro base.
x
TV(param) Desplazamientocorrespondienteaunaentradadelatabla
de vectores.
Tabla A.1: Resumen de la notación utilizada en la especificación de RTM32
75

---

## Page 78

B. Instruction Set Reference
Opcode T Mnemo Operands Operation
00000 R see table B.2
00001/00 J J vlimm R[0] = PC + 4; PC = RA (limm) (1)
27
00001/01 J JAL vlimm R[1] = PC + 4; PC = RA (limm)
27
00001/1ix J JALX limm R[1ix] = PC + 4; PC = RA (llimm)
26
00010/00 I JR rs llimm R[0] = PC + 4; PC = AA (rs,limm) (2)
22
00010/01 I JALR rs llimm R[1] = PC + 4; PC = AA (rs,limm)
22
00010/1ix I JALRX rs slimm R[1ix] = PC + 4; PC = AA (rs,llimm)
21
00011 I ADDI rs rt simm R[rt] = R[rs] + E (simm,S) (3)
17
00100/0 I ANDI rs rt simm R[rt] = R[rs] & E (simm,0)
16
00100/1 I LCI rs rt simm R[rt] = C (simm, R[rs]) (4)
16
00101/0 I ANI rs rt simm R[rt] = R[rs] & E (simm,1)
16
00101/0 I ANH rs rt simm R[rt] = R[rs] & C (simm,R[rs])
16
00110/0 I ORI rs rt simm R[rt] = R[rs] ∣ E (simm,0)
16
00110/1 I ORH rs rt simm R[rt] = R[rs] ∣ C (simm,$0)
16
00111/0 I XORI rs rt simm R[rt] = R[rs] ⊕ E (simm,0)
16
00111/1 I XORH rs rt simm R[rt] = R[rs] ⊕ C (simm,$0)
16
01000 I LW rs rt imm R[rt] = M[EA(rs, imm)] (5)
01001 I SW rs rt imm M[EA(rs, imm)] = R[rt]
01010 I SH rs rt imm M[EA(rs, imm)] = R[rt]
[15∶0]
01011 I SB rs rt imm M[EA(rs, imm)] = R[rt]
[7∶0]
01100 I LH rs rt imm R[rt]= E (M[EA(rs, imm)],S)
16
01101 I LHU rs rt imm R[rt]= E (M[EA(rs, imm)],0)
16
01110 I LB rs rt imm R[rt]= E (M[EA(rs, imm)],S)
8
01111 I LBU rs rt imm R[rt]= E (M[EA(rs, imm)],0)
8
10000 I BEQ rs rt imm if (R[rs] == R[rt]) PC = RA (imm)
19
10001 I BNE rs rt imm if (R[rs] != R[rt]) PC = RA (imm)
19
10010 I BLT rs rt imm if (R[rs] < R[rt]) PC = RA (imm) (6)
19
10011 I BGE rs rt imm if (R[rs] >= R[rt]) PC = RA (imm)
19
10100 I BLTU rs rt imm if (U(R[rs]) < U(R[rt])) PC = RA (imm)
19
10101 I BGEU rs rt imm if (U(R[rs]) >= U(R[rt])) PC = RA (imm)
19
10110 I SLTI rs rt imm R[rt] = (R[rs] < E (imm,S)) ? 1 : 0
17
10111 I SLTIU rs rt imm R[rt] = (U(R[rs]) < U(E (imm,0))) ? 1 : 0
17
Tabla B.1: RTM32 Instruction Set sorted by opcode
(1) RA (y) = PC + 4 + E (4y,S) calcula la dirección en palabras relativa al PC actual.
x x
(2) AA (rs,imm) = R[rs] + E (4imm,S) calcula la dirección absoluta en palabras relativa a
x x
R[rs].
(3) E (y,z) extiende los x bits de y con z ∈S,0,1 (signo, cero o uno).
x
(4) C (y,z) concatena los x bits de y como parte más significativa con los x bits menos
x
significativos de z.
(5) EA(rs,imm) = R[rs] + E (imm,S) calcula la dirección efectiva.
17
(6) U(x) = (unsigned)x valor no signado. Salvo que se indique explícitamente lo contrario,
todoslosoperadoresrelacionales(<,<=,>,>=)realizancomparacionesconsigno.Paraefectuar
comparacionessinsignodebeutilizarselanotaciónU(x)sobrelosoperandoscorrespondientes.
76

---

## Page 79

Apéndice B. Instruction Set Reference Manual de Usuario RTM32
Func Mnemo Operands Operation
000000 SLL rt rd param R[rd] = R[rt] ≪ param
↷
000001 RLC rt rd param R[rd] = R[rt] ≪ param
000010 SRL rt rd param R[rd] = R[rt] ≫ param
000011 SRA rt rd param R[rd] = R[rt] ⋙ param
000100 SLLR rs rt rd R[rd] = R[rt] ≪ R[rs]
[4∶0]
↷
000101 RLCR rs rt rd R[rd] = R[rt] ≪ R[rs]
[4∶0]
000110 SRLR rs rt rd R[rd] = R[rt] ≫ R[rs]
[4∶0]
000111 SRAR rs rt rd R[rd] = R[rt] ⋙ R[rs]
[4∶0]
001000 AND rs rt rd R[rd] = R[rs] & R[rt]
001001 OR rs rt rd R[rd] = R[rs] ∣ R[rt]
001010 XOR rs rt rd R[rd] = R[rs] ⊕ R[rt]
001011 NOR rs rt rd R[rd] = ¬ (R[rs] ∣ R[rt])
001100 ADD rs rt rd R[rd] = R[rs] + R[rt]
001101 SUB rs rt rd R[rd] = R[rs] − R[rt]
001110 SLT rs rt rd R[rd] = (R[rs] < R[rt]) ? 1 : 0
001111 SLTU rs rt rd R[rd] = (U(R[rs]) < U(R[rt])) ? 1 : 0
010000 LHX rs rt rd R[rt] = E (M[EAX(rs,rd)],S) (7)
16
010001 LHUX rs rt rd R[rt] = E (M[EAX(rs,rd)],0)
16
010010 LBX rs rt rd R[rt] = E (M[EAX(rs,rd)],S)
8
010011 LBUX rs rt rd R[rt] = E (M[EAX(rs,rd)],0)
8
010100 LWX rs rt rd R[rt] = M[EAX(rs,rd)]
010101 SWX rs rt rd M[EAX(rs,rd)] = R[rt]
010110 SHX rs rt rd M[EAX(rs,rd)] = R[rt]
[15∶0]
010111 SBX rs rt rd M[EAX(rs,rd)] = R[rt]
[7∶0]
011000 MUL rs rt rd R[rd] = {R[rs] × R[rt]}
[31∶0]
011001 MULH rs rt rd R[rd] = {R[rs] × R[rt]}
[63∶32]
011010 MULHU rs rt rd R[rd] = {U(R[rs]) × U(R[rt])}
[63∶32]
011011 MULHSU rs rt rd R[rd] = {R[rs] × U(R[rt])}
[63∶32]
011100 DIV rs rt rd R[rd] = R[rs] / R[rt]
011101 DIVU rs rt rd R[rd] = U(R[rs]) / U(R[rt])
011110 REST rs rt rd R[rd] = R[rs]% R[rt]
011111 RESTU rs rt rd R[rd] = U(R[rs])% U(R[rt])
100000 CFS rs param R[rs] = S[param]
100001 CTS rs param S[param] = R[rs]
100010 TRAP param EPC = PC + 4; PC = M[TV(param)] (8)
100011 RFT PC = EPC
Tabla B.2: R-type instructions sorted by func
(7) EAX(rs,rd) = R[rs] + R[rd] calcula la dirección efectiva extendida por otro registro EAX
(8) TV(param) = param ≪ 2
77

---

