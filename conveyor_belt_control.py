import RPi.GPIO as GPIO
import time

from bilderkennung_v1 import detect_red_object


def switch_pin(pin):
    GPIO.output(pin, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(pin, GPIO.HIGH)

def main():
    GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
    forwards_pin = 23
    backwards_pin = 24

    GPIO.setup(forwards_pin, GPIO.OUT)
    GPIO.setup(backwards_pin, GPIO.OUT)
    
    GPIO.output(forwards_pin, GPIO.HIGH)
    GPIO.output(backwards_pin, GPIO.HIGH)

    # move belt forewards
    switch_pin(forwards_pin)
    start_time = time.time()
    # warten bis objekt erkannt
    detect_red_object()
    # warten bis Objekt komplett in Kamerabild ist (hoffentlich)
    time.sleep(0.75)
    # nochmal erkennen wo genau das Objekt jetzt ist
    area = detect_red_object()

    # weiter fahren bis was auch immer, keine Ahnung (die 2 muss noch angepasst werden)
    time.sleep(2) 
    # belt stoppen
    switch_pin(forwards_pin)
    # hier weiteren pin stuff implementieren
    time.sleep(2) # platzhalter

    end_time = time.time()
    total_belt_moving_time = end_time - start_time
    print(f"Laufband ist {total_belt_moving_time} Sekunden gelaufen")
    # move belt backwards
    switch_pin(backwards_pin)
    time.sleep(total_belt_moving_time)
    # stop belt
    switch_pin(backwards_pin)

    


if __name__ == "__main__":
    main()
