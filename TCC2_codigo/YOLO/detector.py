# @misc{lin2015microsoft,
#       title={Microsoft COCO: Common Objects in Context},
#       author={Tsung-Yi Lin and Michael Maire and Serge Belongie and Lubomir Bourdev and Ross Girshick and James Hays and Pietro Perona and Deva Ramanan and C. Lawrence Zitnick and Piotr Dollár},
#       year={2015},
#       eprint={1405.0312},
#       archivePrefix={arXiv},
#       primaryClass={cs.CV}
# }

# ============================================
# IMPORTS
# ============================================

import cv2
import numpy as np
from ultralytics import YOLO
from shapely.geometry import Polygon
import tkinter as tk
import serial
import time

# ============================================
# RESOLUÇÃO MONITOR
# ============================================

root = tk.Tk()
root.withdraw()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# ============================================
# MODELO YOLO
# ============================================

model = YOLO("yolov8n.pt")

# ============================================
# SERIAL ESP32
# ============================================

esp32 = serial.Serial("COM3", 115200)
time.sleep(2)

esp32.write(b'R\n')

print("RESET ENVIADO")

# ============================================
# CONTROLE DE ENVIO
# ============================================

ultimo_envio = 0
gap = 0.25
ultimo_estado = ""

# ============================================
# VÍDEOS
# ============================================

videopathA = "TCC2VideoVazio.mp4"
videopathB = "TCC2VideoCarro.mp4"

videoA = "n"
videoB = "n"

capA = cv2.VideoCapture(videopathA)
capB = cv2.VideoCapture(videopathB)

# ============================================
# CLASSES VEÍCULOS
# ============================================

vehicle_classes = [2, 3, 5, 7]

# ============================================
# THRESHOLDS
# ============================================

confianca = 0.2
percentagemROI = 0.2

# ============================================
# ROI
# ============================================

if videoA == "s":
    roi_array_B = np.array([
        [1188, 1069],
        [11, 984],
        [1284, 403],
        [1385, 417]
    ], np.int32)
else:
    roi_array_A = np.array([ 
        [1130, 384], 
        [1215, 415], 
        [1060, 1072], 
        [47, 1039] 
    ], np.int32)

if videoB == "s":
    roi_array_B = np.array([
        [1188, 1069],
        [11, 984],
        [1284, 403],
        [1385, 417]
    ], np.int32)
else:
    roi_array_B = np.array([ 
        [1130, 384], 
        [1215, 415], 
        [1060, 1072], 
        [47, 1039] 
    ], np.int32)

roi_points_A = roi_array_A.reshape((-1, 1, 2))
roi_polygon_A = Polygon(roi_array_A)

roi_points_B = roi_array_B.reshape((-1, 1, 2))
roi_polygon_B = Polygon(roi_array_B)

# ============================================
# JANELAS
# ============================================

cv2.namedWindow("Via A", cv2.WINDOW_NORMAL)
cv2.namedWindow("Via B", cv2.WINDOW_NORMAL)

# ============================================
# FUNÇÃO DETECÇÃO
# ============================================

def detectar_veiculos(frame, roi_points, roi_polygon):

    veiculos = 0

    frame_original = frame.copy()

    # DESENHO ROI
    cv2.polylines(
        frame_original,
        [roi_points],
        isClosed=True,
        color=(0, 255, 255),
        thickness=2
    )

    # DETECÇÃO
    results = model(frame_original)

    for result in results:

        for box in result.boxes:

            # FILTRO CLASSE
            cls = int(box.cls[0])

            if cls in vehicle_classes:

                # FILTRO CONFIANÇA
                confidence = float(box.conf[0])

                if confidence < confianca:
                    continue

                # MAPEAMENTO BOUNDING BOX
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                bbox_polygon = Polygon([
                    (x1, y1),
                    (x2, y1),
                    (x2, y2),
                    (x1, y2)
                ])

                # CÁLCULO INTERSEÇÃO
                intersection_area = roi_polygon.intersection(
                    bbox_polygon
                ).area

                bbox_area = bbox_polygon.area

                if bbox_area == 0:
                    continue

                percentage_inside = (
                    intersection_area / bbox_area
                )

                # EFEITOS VISUAIS
                if percentage_inside >= percentagemROI:

                    veiculos += 1

                    label = model.names[cls]

                    cv2.rectangle(
                        frame_original,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                    text = (
                        f"{label} "
                        f"{confidence:.2f}"
                    )

                    cv2.putText(
                        frame_original,
                        text,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )

                    center_x = int((x1 + x2) / 2)
                    center_y = int((y1 + y2) / 2)

                    cv2.circle(
                        frame_original,
                        (center_x, center_y),
                        5,
                        (0, 0, 255),
                        -1
                    )

    return frame_original, veiculos

# ============================================
# LOOP PRINCIPAL
# ============================================

while True:

    retA, frameA = capA.read()
    retB, frameB = capB.read()

    if not retA or not retB:
        break

    # DETECÇÃO VIA A

    frameA, contadorA = detectar_veiculos(
        frameA,
        roi_points_A,
        roi_polygon_A
    )

    # DETECÇÃO VIA B

    frameB, contadorB = detectar_veiculos(
        frameB,
        roi_points_B,
        roi_polygon_B
    )

    # DECISÃO

    estado_atual = "A"

    if contadorB > contadorA:
        estado_atual = "B"

    # ENVIO SERIAL

    agora = time.time()

    if (agora - ultimo_envio) >= gap:
        print(f"SINAL ENVIADO: {estado_atual}")

        esp32.write(
            (estado_atual + "\n").encode()
        )

        ultimo_estado = estado_atual

        ultimo_envio = agora

    cv2.putText(
        frameA,
        f"Via A: {contadorA} veiculos",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        3
    )

    cv2.putText(
        frameB,
        f"Via B: {contadorB} veiculos",
        (50, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        3
    )

    cv2.putText(
        frameA,
        f"SINAL: {estado_atual}",
        (50, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        3
    )

    # RESIZE VIA A

    heightA, widthA = frameA.shape[:2]

    scaleA = min(
        (screen_width * 0.45) / widthA,
        (screen_height * 0.85) / heightA
    )

    frameA = cv2.resize(
        frameA,
        (
            int(widthA * scaleA),
            int(heightA * scaleA)
        )
    )

    # RESIZE VIA B

    heightB, widthB = frameB.shape[:2]

    scaleB = min(
        (screen_width * 0.45) / widthB,
        (screen_height * 0.85) / heightB
    )

    frameB = cv2.resize(
        frameB,
        (
            int(widthB * scaleB),
            int(heightB * scaleB)
        )
    )

    cv2.imshow("Via A", frameA)
    cv2.imshow("Via B", frameB)

    key = cv2.waitKey(1)

    if key == 27:
        break

capA.release()
capB.release()

cv2.destroyAllWindows()