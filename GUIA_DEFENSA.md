# Guía para comprender y defender la práctica

Este documento sirve para estudiar el funcionamiento real. No es una declaración de trabajo personal ni sustituye comprender el código. No atribuyas a pruebas realizadas resultados que no hayas comprobado.

## Recorrido de 5–10 minutos

1. **Objetivo y demostración (2–3 min).** Abre la aplicación y explica que la entrada es gestual y la salida visual. Haz las operaciones que indique el profesor. Ensaya también borrado, reset, decimales y división por cero.
2. **Reconocimiento (1–2 min).** MediaPipe detecta 21 puntos. El índice es el puntero. La aplicación interpreta esos puntos mediante reglas geométricas y temporales; no entrena un clasificador propio.
3. **Usabilidad (1–2 min).** Compara apuntado por permanencia y pinza; explica la barra de progreso, el bloqueo de repetición, el suavizado y la pausa. Demuestra cambiar de modo con M.
4. **Arquitectura y límites (1–2 min).** Separa interfaz, filtros de selección y cálculo. Explica precedencia, errores y límites con luz insuficiente u oclusiones.

## Sigue una pulsación por el código

`app.main()` lee un fotograma, lo refleja y lo pasa a `hands.process()`. Si hay una mano, obtiene el punto 8, suaviza su posición y busca qué botón contiene el puntero. Llama a `selector.update()` con el botón, la proporción de pinza y el reloj monotónico.

El selector devuelve `None` mientras no haya una confirmación válida. Cuando devuelve una tecla, `Calculator.press()` modifica la expresión. `render()` dibuja el nuevo estado. La cámara se libera en `finally`, incluso si ocurre un error.

## Preguntas que debes poder responder

**¿Qué parte hace MediaPipe y cuál hace la aplicación?**
MediaPipe estima puntos de la mano. El código propio decide qué tecla se está señalando, cuándo un movimiento confirma una selección, cómo evitar repeticiones y qué operación efectuar.

**¿Por qué dos modos?**
Apuntar durante un segundo exige menos coordinación fina. La pinza permite confirmar deliberadamente, pero puede resultar más difícil. Durante una prueba del usuario se observó dificultad para pulsar con pinza; se añadió permanencia y se fijó el puntero al cerrar. No equivale a un estudio de usabilidad con una muestra amplia.

**¿Cómo se evita una pulsación arbitraria?**
En permanencia se exige un segundo sobre la misma tecla y salir de ella para repetir. En pinza se exige apertura inicial, 0,20 s sobre el objetivo, cierre durante 0,10 s y reapertura antes del siguiente clic. Perder la mano reinicia el estado. No se puede garantizar que toda permanencia accidental se descarte.

**¿Qué es la histéresis aquí?**
Cerrar exige una proporción ≤ 0,35; reabrir exige ≥ 0,55. La zona intermedia evita que el ruido alrededor de un único umbral alterne continuamente entre abierto y cerrado.

**¿Por qué dividir por el ancho de la palma?**
La distancia absoluta en píxeles cambia al acercar la mano. Dividir la distancia pulgar–índice por la distancia entre los puntos 5 y 17 reduce esa dependencia. No corrige por completo la perspectiva ni una palma de canto.

**¿Por qué fijar el cursor durante la pinza?**
Al juntar los dedos se mueve la punta del índice. Si ya estaba armado el objetivo, fijarlo impide cambiar accidentalmente de tecla durante la confirmación. El objetivo vuelve a poder cambiar tras abrir.

**¿Qué se gana y qué se pierde al suavizar?**
Se reduce el temblor, a cambio de un pequeño retraso. El filtro depende del tiempo transcurrido, no de un número fijo de fotogramas, para tener un comportamiento más parecido con distintas velocidades de cámara.

**¿Por qué no usar eval como el ejemplo?**
El evaluador solo necesita cuatro operadores y números. Un analizador limitado evita interpretar código Python. `term()` resuelve multiplicaciones y divisiones antes de las sumas y restas; `Decimal` evita el artefacto binario habitual de `0.1 + 0.2`.

**¿Qué ocurre si se pierde la cámara o la mano?**
Sin mano se cancela la selección y hay que volver a apuntar. Sin fotogramas se muestra un error por terminal y se libera la cámara; no se sigue calculando con la última imagen.

**¿Qué mejoras serían razonables?**
Calibración personal de umbrales, pruebas de tiempos y errores con varios usuarios, tamaño de teclas ajustable o salida sonora opcional. Son propuestas, no funcionalidades implementadas.

## Antes de entregar

- Prueba tú mismo las cuatro operaciones, BORRAR, RESET y ambos modos.
- Explica sin leer cómo llega un punto de la mano a convertirse en una pulsación.
- Invita al profesor al repositorio privado y comprueba el acceso antes del plazo.
- Entrega el enlace o los archivos en el lugar indicado por la asignatura. Crear el repositorio en GitHub no realiza esa entrega.
- El enunciado fija el límite a las 15:00 del 9/11 y penaliza los commits posteriores: no hagas cambios en el repositorio de entrega después del plazo.
- Revisa las normas de asistencia de IA de la asignatura y declara la ayuda recibida según corresponda.
