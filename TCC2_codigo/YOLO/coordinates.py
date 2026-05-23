import cv2

points = []

def mouse_callback(event, x, y, flags, param):

    if event == cv2.EVENT_LBUTTONDOWN:

        points.append((x, y))

        print(f"Ponto adicionado: ({x}, {y})")

cap = cv2.VideoCapture("TCC2Teste3.mp4")

cv2.namedWindow("Video")
cv2.setMouseCallback("Video", mouse_callback)

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Desenha os pontos
    for point in points:

        cv2.circle(frame, point, 5, (0, 0, 255), -1)

        cv2.putText(
            frame,
            str(point),
            (point[0] + 10, point[1]),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )

    cv2.imshow("Video", frame)

    key = cv2.waitKey(1)

    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()