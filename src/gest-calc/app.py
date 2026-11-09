"""Interfaz OpenCV y captura de gestos con MediaPipe Hands."""
import argparse
import os
import time
from dataclasses import dataclass

import cv2
import mediapipe as mp
import numpy as np

from calculator import Calculator
from gestures import PinchSelector, pinch_ratio

WIDTH, HEIGHT = 1280, 720
WINDOW = "Calculadora gestual"
FONT = cv2.FONT_HERSHEY_SIMPLEX


@dataclass
class Button:
    value: str
    x: int
    y: int
    width: int
    height: int

    def contains(self, point):
        return (point is not None and self.x <= point[0] < self.x + self.width
                and self.y <= point[1] < self.y + self.height)


def make_buttons():
    buttons = [Button("C", 824, 212, 206, 66), Button("<", 1042, 212, 206, 66)]
    for row, values in enumerate(("789/", "456*", "123-", "0.=+")):
        for col, value in enumerate(values):
            buttons.append(Button(value, 824 + col * 109, 290 + row * 83, 97, 71))
    return buttons


def text(image, value, point, scale=.6, color=(235, 240, 245), thickness=1):
    cv2.putText(image, value, point, FONT, scale, color, thickness, cv2.LINE_AA)


def render(frame, calculator, buttons, selector, pointer=None, hover=None,
           flash=None, fps=0, ratio=None, paused=False):
    image = cv2.resize(frame, (WIDTH, HEIGHT))
    cv2.rectangle(image, (800, 0), (WIDTH, HEIGHT), (29, 25, 22), -1)
    cv2.rectangle(image, (0, 0), (799, 94), (29, 25, 22), -1)
    text(image, "CALCULADORA GESTUAL", (26, 38), .85, thickness=2)
    text(image, "1. Apunta   2. Junta pulgar e indice   3. Separa", (26, 73), .57)
    text(image, "OPERACION", (824, 36), .5, (173, 184, 194))
    cv2.rectangle(image, (824, 51), (1248, 195), (47, 43, 38), -1)
    previous = calculator.previous
    if len(previous) > 35:
        previous = "..." + previous[-32:]
    text(image, previous, (838, 78), .48, (173, 184, 194))
    expression = calculator.expression or "0"
    if len(expression) > 28:
        for index in range(3):
            text(image, expression[index * 28:(index + 1) * 28], (838, 112 + index * 28), .65)
    else:
        scale = 1.1
        while cv2.getTextSize(expression, FONT, scale, 2)[0][0] > 395:
            scale -= .05
        text(image, expression, (838, 144), scale, thickness=2)
    for button in buttons:
        color = (69, 61, 53)
        if button.value in "+-*/=":
            color = (109, 78, 32)
        if button.value in "C<":
            color = (68, 54, 90)
        if button.value == hover:
            color = (139, 113, 53)
        if button.value == flash:
            color = (85, 151, 43)
        cv2.rectangle(image, (button.x, button.y),
                      (button.x + button.width, button.y + button.height), color, -1)
        label = {"C": "RESET", "<": "BORRAR"}.get(button.value, button.value)
        scale = .65 if len(label) > 1 else 1.0
        size = cv2.getTextSize(label, FONT, scale, 2)[0]
        text(image, label, (button.x + (button.width - size[0]) // 2,
                           button.y + (button.height + size[1]) // 2), scale, thickness=2)
        if button.value == hover:
            cv2.rectangle(image, (button.x, button.y),
                          (button.x + button.width, button.y + button.height), (180, 231, 255), 2)
            cv2.rectangle(image, (button.x, button.y + button.height - 5),
                          (button.x + int(button.width * selector.progress), button.y + button.height),
                          (180, 231, 255), -1)
    cv2.rectangle(image, (0, 620), (799, HEIGHT), (29, 25, 22), -1)
    status = "PAUSA: pulsa espacio para continuar" if paused else selector.status
    text(image, status, (26, 652), .65, (180, 231, 255))
    text(image, "ESPACIO: pausa    Q / ESC: salir", (26, 686), .55)
    text(image, f"{fps:.0f} FPS", (686, 686), .5)
    if ratio is not None:
        text(image, f"Pinza: {ratio:.2f}", (26, 602), .5)
    if calculator.error:
        text(image, calculator.error, (824, 646), .45, (137, 167, 255))
    else:
        text(image, "Prioridad: * y / antes que + y -", (824, 646), .46, (173, 184, 194))
    text(image, "Mantener cerrado no repite la pulsacion", (824, 682), .43, (173, 184, 194))
    if pointer is not None and not paused:
        cv2.circle(image, pointer, 10, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.circle(image, pointer, 10, (180, 231, 255), 2, cv2.LINE_AA)
    return image


def open_camera(index):
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(index)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(index)
    return cap


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0, help="Indice de webcam (0 por defecto)")
    parser.add_argument("--close", type=float, default=.35, help="Umbral de cierre normalizado")
    parser.add_argument("--release", type=float, default=.55, help="Umbral de apertura normalizado")
    parser.add_argument("--preview", metavar="PNG", help="Guarda una vista sin abrir la camara")
    args = parser.parse_args()
    try:
        selector = PinchSelector(close=args.close, release=args.release)
    except ValueError as error:
        parser.error(str(error))
    calculator, buttons = Calculator(), make_buttons()
    if args.preview:
        calculator.expression = "12+3*4"
        image = render(np.full((HEIGHT, WIDTH, 3), (71, 63, 56), dtype=np.uint8),
                       calculator, buttons, selector, hover="4", fps=30)
        if not cv2.imwrite(args.preview, image):
            raise SystemExit("No se pudo guardar la vista")
        return
    cap = open_camera(args.camera)
    if not cap.isOpened():
        cap.release()
        raise SystemExit("No se puede abrir la camara. Prueba --camera 1 y revisa los permisos.")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    pointer, flash, flash_until = None, None, 0
    last_time, fps, paused = time.monotonic(), 0, False
    hands_api = mp.solutions.hands
    try:
        cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW, WIDTH, HEIGHT)
        with hands_api.Hands(max_num_hands=1, model_complexity=0,
                             min_detection_confidence=.7, min_tracking_confidence=.7) as hands:
            while True:
                ok, frame = cap.read()
                if not ok:
                    raise SystemExit("Se perdio la imagen de la camara. Revisa la conexion.")
                now = time.monotonic()
                elapsed = max(now - last_time, .001)
                fps = .9 * fps + .1 / elapsed
                last_time = now
                frame = cv2.resize(cv2.flip(frame, 1), (WIDTH, HEIGHT))
                ratio, hover = None, None
                if not paused:
                    rgb = cv2.cvtColor(cv2.resize(frame, (640, 360)), cv2.COLOR_BGR2RGB)
                    rgb.flags.writeable = False
                    result = hands.process(rgb)
                    if result.multi_hand_landmarks:
                        landmarks = result.multi_hand_landmarks[0]
                        target = (int(landmarks.landmark[8].x * WIDTH),
                                  int(landmarks.landmark[8].y * HEIGHT))
                        if pointer is None:
                            pointer = target
                        else:
                            alpha = 1 - np.exp(-min(elapsed, .2) / .045)
                            pointer = tuple(int(a + alpha * (b - a)) for a, b in zip(pointer, target))
                        ratio = pinch_ratio(landmarks.landmark, WIDTH, HEIGHT)
                        hover = next((b.value for b in buttons if b.contains(pointer)), None)
                        mp.solutions.drawing_utils.draw_landmarks(frame, landmarks, hands_api.HAND_CONNECTIONS)
                    else:
                        pointer = None
                    selected = selector.update(hover, ratio, now)
                    if selected:
                        calculator.press(selected)
                        flash, flash_until = selected, now + .3
                image = render(frame, calculator, buttons, selector, pointer, hover,
                               flash if now < flash_until else None, fps, ratio, paused)
                cv2.imshow(WINDOW, image)
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord("q")) or cv2.getWindowProperty(WINDOW, cv2.WND_PROP_VISIBLE) < 1:
                    break
                if key == ord(" "):
                    paused = not paused
                    selector.reset()
                    pointer = None
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
