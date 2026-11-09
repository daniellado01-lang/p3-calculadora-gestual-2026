"""Diagnóstico de cámara independiente del reconocimiento de gestos."""
import argparse
import os
import cv2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--camera', type=int, default=0)
    args = parser.parse_args()
    cap = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW) if os.name == 'nt' else cv2.VideoCapture(args.camera)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(args.camera)
    try:
        if not cap.isOpened():
            raise SystemExit('No se puede abrir la camara. Revisa permisos o prueba --camera 1.')
        print('Camara abierta. Pulsa Q o Esc para cerrar.')
        while True:
            ok, frame = cap.read()
            if not ok:
                raise SystemExit('No se puede leer la imagen de la camara.')
            cv2.imshow('Webcam', cv2.flip(frame, 1))
            if cv2.waitKey(1) & 0xFF in (27, ord('q')):
                break
            if cv2.getWindowProperty('Webcam', cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
