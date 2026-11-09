# Calculadora basada en gestos

Práctica 3 de Sistemas Interactivos Inteligentes. Calculadora controlada con una mano captada por webcam, construida a partir del material proporcionado en la asignatura.

## Entorno

- Sistema empleado para desarrollo y comprobaciones: **Windows**.
- Python **3.12** (comprobado con 3.12.16).
- MediaPipe **0.10.21**, OpenCV contrib **4.11.0.86** y NumPy **1.26.4**: se mantienen las versiones del material docente.
- `requirements.txt`: dependencias directas. `requirements-lock.txt`: versiones completas del entorno comprobado en Windows, para reproducirlo con mayor exactitud.

## Ejecutar en Windows o macOS con uv

Instalar [uv desde su documentación oficial](https://docs.astral.sh/uv/getting-started/installation/). Abrir una terminal en la carpeta del proyecto:

```sh
uv venv --python 3.12
uv pip install -r requirements.txt
uv run python src/gest-calc/webcam_test.py
uv run python src/gest-calc/sample_main.py
```

En Windows también se puede hacer doble clic en `INICIAR.cmd`: usa el entorno existente o, si falta y uv está instalado, lo prepara. En macOS debe concederse acceso a la cámara al programa desde el que se ejecute.

Para reproducir las dependencias completas comprobadas en Windows, sustituir la instalación por `uv pip install -r requirements-lock.txt`. Este archivo no implica que se haya probado macOS o Linux.

Otra cámara:

```sh
uv run python src/gest-calc/sample_main.py --camera 1
```

## Ejecutar en Linux

Se conservan el Dockerfile y las recetas del material docente (requieren Docker y una sesión gráfica compatible con X11):

```sh
make build
make camtest
make run
# Otra cámara:
make run CAM=/dev/video2
```

También se pueden utilizar los comandos de uv anteriores. Docker no se ha probado en este equipo Windows; para Windows se emplea uv como indica el enunciado.

## Interacción

La imagen se muestra en espejo. Mover la punta del índice mueve el círculo de selección. Se detecta una sola mano; se recomienda buena luz, mantener la mano entera visible y evitar que otra persona introduzca una mano en la imagen.

**Modo apuntar (predeterminado):** situar el círculo sobre una tecla y mantenerlo durante un segundo. La barra muestra el tiempo de confirmación y la tecla se ilumina al pulsar. Para escribir dos veces la misma tecla, salir de ella y volver. Pasar rápidamente por encima no la activa.

**Modo pinza (tecla M):** con pulgar e índice separados, apuntar a una tecla durante 0,20 s hasta completar la barra. Juntar sus puntas durante al menos 0,10 s para confirmar y separarlas antes de otra pulsación. El puntero se fija al empezar a cerrar para que el movimiento del índice no cambie la tecla elegida.

| Control | Acción |
| --- | --- |
| `M` | Cambiar entre apuntar y pinza |
| Espacio | Pausar o reanudar la selección |
| `Q` o Esc | Salir y liberar la cámara |
| `RESET` | Vaciar operación, resultado e historial visible |
| `BORRAR` | Eliminar el último carácter |
| `=` | Evaluar la operación |

Las operaciones se introducen mediante gestos, sin atajos de teclado para los números. Se admiten suma, resta, multiplicación, división, decimales y operandos negativos como `5*-2`. Se respeta la prioridad de multiplicación/división: `2+3*4 = 14`. Tras un resultado, una cifra empieza una operación nueva; un operador continúa desde el resultado. Los errores conservan la expresión para poder corregirla.

Para iniciar directamente en modo pinza o ajustar sus umbrales:

```sh
uv run python src/gest-calc/sample_main.py --mode pinch
uv run python src/gest-calc/sample_main.py --mode pinch --close 0.40 --release 0.65
```

`close` debe ser positivo y menor que `release`. Son proporciones respecto a la anchura de la palma, no distancias en centímetros. Los valores predeterminados son 0,35 y 0,55.

## Organización y decisiones

- `sample_main.py`: conserva el punto de entrada del material docente.
- `app.py`: cámara, MediaPipe, suavizado del puntero y dibujo de la interfaz.
- `gestures.py`: filtros temporales de apuntado y pinza; no necesita cámara para probarse.
- `calculator.py`: edición y evaluación de expresiones; no utiliza `eval`.
- `webcam_test.py`: diagnóstico independiente de la webcam.
- `tests/`: pruebas automáticas de cálculo y selección.

MediaPipe proporciona 21 puntos de la mano. Se usa el 8 para apuntar y los puntos 4 y 8 para la pinza. La distancia 5–17 sirve de referencia de tamaño. Las distancias se calculan en píxeles para respetar la relación de aspecto. Una palma menor de 15 píxeles se rechaza por inestabilidad.

La pinza utiliza dos umbrales (histéresis) y un bloqueo hasta volver a abrir. Perder la mano reinicia el filtro. El modo apuntar reduce la exigencia de coordinación fina y añade un segundo de permanencia para distinguir apuntados de movimientos de paso. La barra y los mensajes hacen visible el estado; no se depende solo del color.

El puntero aplica un filtro exponencial con constante de tiempo de 45 ms: reduce temblor a cambio de un pequeño retraso. La inferencia utiliza una imagen de 640 × 360 y un modelo ligero. La interfaz mantiene coordenadas de 1280 × 720 aunque se cambie el tamaño de la ventana.

El evaluador reconoce únicamente números y cuatro operadores, con precedencia explícita. Usa `Decimal` con 16 cifras significativas; las divisiones periódicas se redondean. La entrada y el resultado se limitan a 60 caracteres. No se admiten paréntesis, potencias ni notación científica.

## Pruebas

```sh
uv run python -m unittest discover -s tests -v
```

Se han comprobado las operaciones, prioridad, errores, edición, bloqueo de repeticiones, cambios de objetivo, pérdida de seguimiento y permanencia. También se han procesado 20 fotogramas de la webcam 0 con MediaPipe en el equipo Windows. Estas comprobaciones no sustituyen una prueba manual de todos los gestos en las condiciones de la defensa.

Recorrido manual recomendado: `2+3=5`, `9-12=-3`, `6*7=42`, `8/4=2`, `0.1+0.2=0.3`, `1/0` (error), corregir con BORRAR, RESET y escribir `11` saliendo de la tecla entre pulsaciones. Probar pausa, retirar la mano y ambos modos.

## Limitaciones y solución de problemas

- Si no abre la cámara: cerrar aplicaciones que la estén usando, comprobar permisos del sistema y probar `--camera 1`.
- Si cuesta apuntar: mejorar la luz, alejar ligeramente la mano para que quepa entera y usar el modo apuntar. La cámara no debe estar tapada.
- El modo apuntar puede activar una tecla si se permanece sobre ella sin intención. Espacio pausa la interacción. En modo pinza la confirmación es más explícita, pero exige mayor coordinación.
- La oclusión, luz deficiente, cambios de mano y orientación de canto pueden empeorar el seguimiento. La normalización no elimina todos estos efectos.
- Se muestran mensajes sin tildes en la ventana por la limitación de la fuente incorporada en OpenCV.
- Las imágenes se procesan localmente: la aplicación no graba vídeo ni lo envía a ningún servidor.

## Procedencia

El primer commit conserva el material entregado por el profesor. El desarrollo posterior se realizó con asistencia de IA para implementación, pruebas y documentación. El historial registra los cambios reales; no se han modificado sus fechas. El uso de esta asistencia debe ajustarse a las normas de la asignatura.

Referencias: [MediaPipe Hands](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/hands.md), [uv](https://docs.astral.sh/uv/).
