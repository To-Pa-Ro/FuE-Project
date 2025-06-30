import cv2
import numpy as np

# Kamera starten (0 = Standardkamera, bei Pi Camera ggf. anderes Setup nötig)
cap = cv2.VideoCapture(0)

# Überprüfen, ob Kamera geöffnet werden konnte
if not cap.isOpened():
    print("Fehler: Kamera konnte nicht geöffnet werden.")
    exit()

while True:
    # Einzelnes Bild (Frame) von der Kamera lesen
    ret, frame = cap.read()
    
    if not ret:
        print("Fehler beim Lesen des Bildes.")
        break

    # Bildgröße ausgeben (für Kontext)
    height, width, _ = frame.shape

    # Bild in den HSV-Farbraum konvertieren (besser für Farberkennung)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Farbgrenzen für "Rot" definieren (HSV ist zyklisch, daher 2 Bereiche)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Masken für roten Bereich erstellen
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # Bildrauschen entfernen mit Morphologie
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
    red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_DILATE, kernel)

    # Konturen im Maskenbild finden
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Über alle erkannten roten Objekte iterieren
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:  # Filter: Nur größere Objekte beachten
            # Rechteck um Objekt zeichnen
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Mittelpunkt berechnen und anzeigen
            cx = x + w // 2
            cy = y + h // 2
            cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
            cv2.putText(frame, f"Rot bei ({cx}, {cy})", (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # Koordinaten in Konsole ausgeben
            print(f"Rotes Objekt erkannt bei: X={cx}, Y={cy}")

    # Bild anzeigen (optional, wenn Desktop verfügbar)
    cv2.imshow("Rote Objekterkennung", frame)

    # Warten auf Taste 'q' zum Beenden
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kamera freigeben und Fenster schließen
cap.release()
cv2.destroyAllWindows()
