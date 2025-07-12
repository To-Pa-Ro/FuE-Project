import cv2
import numpy as np

# Kamera starten
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# Kamera öffnen prüfen
if not cap.isOpened():
    print("Fehler: Kamera konnte nicht geöffnet werden.")
    exit()

# ==========================================
# NEU: Vier Punkte für das ROI-Polygon definieren
# ==========================================
# ➤ Diese Koordinaten kannst du manuell anpassen
roi_points = np.array([
    [100, 100],
    [540, 100],
    [540, 380],
    [100, 380]
], dtype=np.int32)

# Maske erzeugen anhand der definierten Punkte
def create_roi_mask(frame_shape, points):
    mask = np.zeros(frame_shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [points], 255)
    return mask

# Haupt-Loop
while True:
    ret, frame = cap.read()
    if not ret:
        print("Fehler beim Lesen des Bildes.")
        break

    # ==========================================
    # NEU: Maske für das Bild erstellen
    # ==========================================
    roi_mask = create_roi_mask(frame.shape, roi_points)

    # Kopie des output Frames damit in der Anzeige das originalbild ohne maskierung gezeigt werden kann
    output_frame = frame.copy()

    # Alles außerhalb des Polygons wird geschwärzt
    masked_frame = cv2.bitwise_and(frame, frame, mask=roi_mask)

    # Kontur der ROI-Zone einzeichnen (optional zur Visualisierung)
    cv2.polylines(output_frame, [roi_points], isClosed=True, color=(0, 255, 0), thickness=2)

    # ==========================================
    # Farberkennung nur innerhalb des maskierten Bereichs
    # ==========================================
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # Rauschentfernung
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_DILATE, kernel)

    # Konturen nur im ROI suchen
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(masked_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cx = x + w // 2
            cy = y + h // 2
            cv2.circle(masked_frame, (cx, cy), 5, (255, 0, 0), -1)
            cv2.putText(masked_frame, f"Rot bei ({cx}, {cy})", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            print(f"Rotes Objekt erkannt bei: X={cx}, Y={cy}")

    # Bild anzeigen
    cv2.imshow("Rote Objekterkennung im ROI", output_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
