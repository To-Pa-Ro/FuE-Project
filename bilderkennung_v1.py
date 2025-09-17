import cv2
import math
import threading
import time
import numpy as np



class ImageRecognition:

    def __init__(self):
        # Kamera starten (0 = Standardkamera, bei Pi Camera ggf. anderes Setup nötig)
        self.cap = cv2.VideoCapture(0)

        # MJPEG einstellen
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # Definitionen der Erkennungsbereiche
        self.top_left_corner = np.array([100, 50])
        self.bottom_right_corner = np.array([540, 430])
        self.horizontal_areas = 1
        self.vertical_areas = 8
        self.horizontal_area_size = int((self.bottom_right_corner[0] - self.top_left_corner[0]) / self.horizontal_areas)
        self.vertical_area_size = int((self.bottom_right_corner[1] - self.top_left_corner[1]) / self.vertical_areas)

        # Variable to store positions of detected red objects
        self.red_object_positions = []
        self.running = False

        # Start the frame processing in a separate thread
        self.thread = threading.Thread(target=self.detect_red_object)
        self.thread.start()
    
    def in_detectionbox(self, x, y):
        return x > self.top_left_corner[0] and x < self.bottom_right_corner[0] and y > self.top_left_corner[1] and y < self.bottom_right_corner[1] 

    def coordinates_to_area(self, x, y):
        area_x = math.floor((x - self.top_left_corner[0]) / self.horizontal_area_size)
        area_y = math.floor((y - self.top_left_corner[1]) / self.vertical_area_size)
        return np.array([area_x, area_y])

    def find_area_by_x_range(self, x_min, x_max):
        for position in self.red_object_positions:
            x, y, area = position
            if x_min <= x <= x_max:
                return area  # Return the area if x is within the specified range
        return []  # Return None if no area is found

    def detect_red_object(self):
        # Überprüfen, ob Kamera geöffnet werden konnte
        if not self.cap.isOpened():
            print("Fehler: Kamera konnte nicht geöffnet werden.")
            exit()

        while True:
            if not self.running:
                time.sleep(0.5)
                continue
            self.red_object_positions = []
            # Einzelnes Bild (Frame) von der Kamera lesen
            ret, frame = self.cap.read()
            
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
                contour_area = cv2.contourArea(cnt)
                if contour_area > 500:  # Filter: Nur größere Objekte beachten
                    # Rechteck um Objekt zeichnen
                    x, y, w, h = cv2.boundingRect(cnt)
                    
                    # Mittelpunkt berechnen und anzeigen
                    cx = x + w // 2
                    cy = y + h // 2
                    if self.in_detectionbox(cx,cy):
                        area = self.coordinates_to_area(cx, cy)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)
                        cv2.putText(frame, f"Rot bei ({cx}, {cy}), Bereich: {area}", (x, y - 10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

                        # Koordinaten in Konsole ausgeben
                        # print(f"Rotes Objekt erkannt bei: X={cx}, Y={cy} in Bereich: {area}")
                        
                        #cap.release()
                        #cv2.destroyAllWindows()
                        self.red_object_positions.append((cx, cy, area))
                        

            # Graphischje ausgabe detection frame
            cv2.rectangle(frame, self.top_left_corner, self.bottom_right_corner, (0, 255, 0), 2)
            
            # unterteilung des detection frames in horizontale bereiche
            for i in range(1, self.horizontal_areas):
                cv2.line(frame, (self.top_left_corner[0] + self.horizontal_area_size*i, self.top_left_corner[1]), (self.top_left_corner[0] + self.horizontal_area_size*i, self.bottom_right_corner[1]), (255, 0, 0), 2)
            
            # unterteilung des detection frames in vertikale bereiche
            for i in range(1, self.vertical_areas):
                cv2.line(frame, (self.top_left_corner[0], self.top_left_corner[1] + self.vertical_area_size*i), (self.bottom_right_corner[0], self.top_left_corner[1] + self.vertical_area_size*i), (255, 0, 0), 2)

            # Bild anzeigen (optional, wenn Desktop verfügbar)
            cv2.imshow("Rote Objekterkennung", frame)

            # Warten auf Taste 'q' zum Beenden
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    def start(self):
        self.running = True
    
    def stop(self):
        self.running= False
        self.thread.join()
        self.cap.release()
        cv2.destroyAllWindows()



