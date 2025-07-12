import cv2
import numpy as np

# Kamera starten
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

if not cap.isOpened():
    print("Fehler: Kamera konnte nicht geöffnet werden.")
    exit()

# ➕ NEU: Vier Punkte definieren (ROI – Region of Interest)
roi_points = np.array([
    [100, 100],
    [540, 100],
    [540, 380],
    [100, 380]
], dtype=np.int32)

# ➕ NEU: Hilfsfunktion zur Maskenerstellung
def create_roi_mask(shape, points):
    mask = np.zeros(shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [points], 255)
    return mask

while True:
    ret, frame = cap.read()
    if not ret:
        print("Fehler beim Lesen des Bildes.")
        break

    # ➕ NEU: Maske mit Polygon erzeugen
    roi_mask = create_roi_mask(frame.shape, roi_points)

    # 🔁 GEÄNDERT: Das Originalbild bleibt erhalten und wird verwendet
    output_frame = frame.copy()

    # ➕ NEU: ROI-Bereich im Bild einzeichnen (nur Umriss, kein Schwärzen)
    cv2.polylines(output_frame, [roi_points], isClosed=True, color=(0, 255, 0), thickness=2)

    # 🔁 GEÄNDERT: HSV-Bild vom Original, nicht von einem geschwärzten Bild
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Farbgrenzen für "Rot"
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # 🔁 GEÄNDERT: Begrenze die Farberkennungsmaske auf den ROI
    red_mask = cv2.bitwise_and(red_mask, red_mask, mask=roi_mask)

    # Rauschentfernung
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_DILATE, kernel)

    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            # 🔁 GEÄNDERT: Zeichnen erfolgt auf dem Originalbild (nicht maskiert)
            cv2.rectangle(output_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cx = x + w // 2
            cy = y + h // 2
            cv2.circle(output_frame, (cx, cy), 5, (255, 0, 0), -1)
            cv2.putText(output_frame, f"Rot bei ({cx}, {cy})", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            print(f"Rotes Objekt erkannt bei: X={cx}, Y={cy}")

    # 🔁 GEÄNDERT: Zeige das vollständige Bild inkl. Erkennung
    cv2.imshow("Rote Objekterkennung im vollständigen Bild", output_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kamera freigeben
cap.release()
cv2.destroyAllWindows()
