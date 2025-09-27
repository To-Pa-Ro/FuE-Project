import RPi.GPIO as GPIO
import time

from bilderkennung_v1 import ImageRecognition



forwards_pin = 23
backwards_pin = 24
    
data_pin1 = 25
data_pin2 = 8
data_pin3 = 7


def move_conveyor_belt(direction):
	global forwards_pin, backwards_pin
	if direction == 's':
		GPIO.output(forwards_pin, GPIO.HIGH)
		GPIO.output(backwards_pin, GPIO.HIGH)
		print("stop")
	elif direction == 'f':
		GPIO.output(forwards_pin, GPIO.LOW)
		GPIO.output(backwards_pin, GPIO.HIGH)
		print("forwards")
	elif direction == 'b':
		GPIO.output(forwards_pin, GPIO.HIGH)
		GPIO.output(backwards_pin, GPIO.LOW)
		print("backwards")
	else:
		raise Exception("Unkown conveyor belt direction")

def move_kuka(area):
	global data_pin1, data_pin2, data_pin3
	if area[1] == 0:
		GPIO.output(data_pin1, GPIO.LOW)
		GPIO.output(data_pin2, GPIO.HIGH)
		GPIO.output(data_pin3, GPIO.HIGH)
	elif area[1] == 1:
		GPIO.output(data_pin1, GPIO.HIGH)
		GPIO.output(data_pin2, GPIO.LOW)
		GPIO.output(data_pin3, GPIO.HIGH)
	elif area[1] == 2:
		GPIO.output(data_pin1, GPIO.LOW)
		GPIO.output(data_pin2, GPIO.LOW)
		GPIO.output(data_pin3, GPIO.HIGH)
	elif area[1] == 3:
		GPIO.output(data_pin1, GPIO.HIGH)
		GPIO.output(data_pin2, GPIO.HIGH)
		GPIO.output(data_pin3, GPIO.LOW)
	elif area[1] == 4:
		GPIO.output(data_pin1, GPIO.LOW)
		GPIO.output(data_pin2, GPIO.HIGH)
		GPIO.output(data_pin3, GPIO.LOW)
	elif area[1] == 5:
		GPIO.output(data_pin1, GPIO.HIGH)
		GPIO.output(data_pin2, GPIO.LOW)
		GPIO.output(data_pin3, GPIO.LOW)
	elif area[1] == 6:
		GPIO.output(data_pin1, GPIO.LOW)
		GPIO.output(data_pin2, GPIO.LOW)
		GPIO.output(data_pin3, GPIO.LOW)
	else:
		raise Exception("Unknown area")

def stop_kuka():
	GPIO.output(data_pin1, GPIO.HIGH)
	GPIO.output(data_pin2, GPIO.HIGH)
	GPIO.output(data_pin3, GPIO.HIGH)
	
	
def main():
    global forwards_pin, backwards_pin, data_pin1, data_pin2, data_pin3
    GPIO.setmode(GPIO.BCM) # Use BCM pin numbering

    GPIO.setup(forwards_pin, GPIO.OUT)
    GPIO.setup(backwards_pin, GPIO.OUT)
    GPIO.setup(data_pin1, GPIO.OUT)
    GPIO.setup(data_pin2, GPIO.OUT)
    GPIO.setup(data_pin3, GPIO.OUT)
    
    move_conveyor_belt('s')
    stop_kuka()

    imageRecognition = ImageRecognition()
    imageRecognition.start()

    # move belt forewards
    move_conveyor_belt('f')
    start_time = time.time()
    # warten bis objekt erkannt
    area = []
    middle = (imageRecognition.bottom_right_corner[0] - imageRecognition.top_left_corner[0]) / 2 + imageRecognition.top_left_corner[0]
    while area == []:
        area = imageRecognition.find_area_by_x_range(middle-15, middle+15)
    
    print(f"erkannt: {area}")

    # belt stoppen
    move_conveyor_belt('s')
    end_time = time.time()
    # hier weiteren pin stuff implementieren
    move_kuka(area)
    print("sende signal")
    time.sleep(10) # warten bis program gestartet ist
    stop_kuka()
    time.sleep(6)

    total_belt_moving_time = end_time - start_time
    print(f"Laufband ist {total_belt_moving_time} Sekunden gelaufen")
    # move belt backwards
    move_conveyor_belt('b')
    time.sleep(total_belt_moving_time)
    # stop belt
    move_conveyor_belt('s')
    print("finish")
    imageRecognition.stop()


if __name__ == "__main__":
    main()
