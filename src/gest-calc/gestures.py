"""Filtro temporal de pinza. No depende de MediaPipe: se prueba sin cámara."""

from math import hypot


def pinch_ratio(landmarks, width, height):
    """Distancia pulgar-índice dividida por anchura de palma, en píxeles."""
    def distance(a, b):
        return hypot((landmarks[a].x - landmarks[b].x) * width,
                     (landmarks[a].y - landmarks[b].y) * height)
    palm = distance(5, 17)
    return distance(4, 8) / palm if palm >= 15 else None


class PinchSelector:
    def __init__(self, close=0.35, release=0.55, hover_time=0.20, hold_time=0.10):
        if not 0 < close < release or min(hover_time, hold_time) <= 0:
            raise ValueError("Umbrales de pinza no validos")
        self.close = close
        self.release = release
        self.hover_time = hover_time
        self.hold_time = hold_time
        self.reset()

    def reset(self):
        self.target = None
        self.since = None
        self.pinch_since = None
        self.armed = False
        self.locked = True
        self.progress = 0.0
        self.status = "Muestra la mano y abre la pinza"

    def update(self, target, ratio, now):
        if ratio is None:
            self.reset()
            return None
        if ratio >= self.release:
            self.locked = False
            self.pinch_since = None
            if target is None or target != self.target:
                self.target, self.since, self.armed = target, now, False
            self.progress = min(1.0, (now - self.since) / self.hover_time) if target else 0
            self.armed = bool(target and self.progress >= 1)
            self.status = "Junta pulgar e indice" if self.armed else "Apunta a una tecla"
            return None
        if self.locked:
            self.status = "Abre la pinza para continuar"
            return None
        if target != self.target or target is None:
            self.armed = False
            self.progress = 0
        if ratio <= self.close:
            if not self.armed:
                self.locked = True
                self.status = "Abre la pinza y apunta primero"
                return None
            if self.pinch_since is None:
                self.pinch_since = now
            self.status = "Confirmando..."
            if now - self.pinch_since >= self.hold_time:
                selected = self.target
                self.locked, self.armed = True, False
                self.target, self.since, self.progress = None, None, 0
                self.status = "Pulsado. Abre la pinza"
                return selected
        else:
            self.pinch_since = None
        return None
