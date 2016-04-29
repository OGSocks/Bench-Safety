import gpiozero
import time
import math
import readchar
import Adafruit_CharLCD as LCD

#LCD pin initializations
REFRESH_TIME = 1.0
lcd = display.lcd
lcd_rs =
lcd_en =
lcd_d4 =
lcd_d5 =
lcd_d6 =
lcd_d7 =
lcd_backlight =
#set lcd size for 16x2
lcd_columns = 16
lcd_rows = 2
# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)

userFile = "BenchUsers.txt"
trig0 = OutputDevice()
echo0= InputDevice()
trig1 = OutputDevice()
echo1 = InputDevice()
reps = 0
prev = -1
weight = 0
lastTime = time()
user_id = ""

userFlag = False
weightFlag = False

sleep(2)

def get_Users():
    users = {}
    f = open(userFile)
    for line in f:
        line = line.strip()
        line = line.split("|")
        users[line[0]] = line[1]
    return users

def get_pulse_time():
    trig.on()
    sleep(0.00001)
    trig.off()

    while echo.is_active == False:
        pulse_start = time()

    while echo.is_active == True:
        pulse_end = time()

    sleep(0.06)

    return pulse_end - pulse_start

def calculate_distance(duration):
    speed = 343
    distance = speed * duration / 2
    return distance

def calculate_velocity(d0,d1,old_d0,old_d1,last_read):
    v0 = (d0-old_d0)/(last_read-lastTime)
    v1 = (d1-old_d1)/(last_read-lastTime)
    return (v0+v1)/2
    

def read_user_average(userfile):
    with open(userfile) as ins:
    array = []
    avg_reps = 
    for line in ins:
        line.strip()
        array.append(line) # not sure if this is correct, but I want to append everything in the line to include historical user's data in array
        summation = sum(array)
        avg_reps = summation/len(array)
        
        
    
while True:
    lcd.enable_display(True)
    users = get_Users()
    while not userFlag:
        lcd.clear()
        lcd.message("Please enter your user ID: " + user_id)
        ui = readchar.readchar()
        now = time()
        while now - lastTime < REFRESH_TIME:
            sleep(.5)
            now = time()
        if ui != "\n":
            user_id += ui
        else:
            if user_id in users:
                userFlag = 1
            else:
                lcd.clear()
                lcd.message("Incorrect User ID")
                user_id = ""
    lcd.clear()
    lcd.message("Hello " + users[user_id])
    sleep(3)
    while not weightFlag:
        weight_str = ""
        lcd.clear()
        lcd.message("Please enter bar weight: " + weight)
        bi = readchar.readchar()
        now = time()
        while now - lastTime < REFRESH_TIME:
            sleep(.5)
            now = time()
        if bi != "\n" and bi.isdigit():
            weight_str += bi
        else:
            if weight_str.isdigit():
                weight = int(weight_str)
                weightFlag = 1
            else:
                lcd.clear()
                lcd.message("Incorrect char for weight")
                weight_str = ""

    duration = get_pulse_time()
    dist0_orig = calculate_distance(duration)
    print(dist0_orig)
    duration = get_pulse_time()
    dist1_orig = calculate_distance(duration)
    last_dist0 = dist0_orig
    last_dist1 = dist1_orig
    lastTime = time()
    v_last = 0
    lift_error = 0
    while True:
        duration = get_pulse_time()
        dist0 = calculate_distance(duration)
        duration = get_pulse_time()
        dist1 = calculate_distance(duration)
        now = time()
        v_now = calculate_velocity(dist0,dist1,last_dist0,last_dist1,now)
        if abs(dist0 - dist1) > .1:
            lift_bars()
            lift_error = 1
            break
        elif last_dist0 > dist0 and last_dist1 > dist1:
            
            reps += 1
