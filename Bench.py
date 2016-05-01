import gpiozero
import time
import math
import readchar
import Adafruit_CharLCD as LCD

#LCD pin initializations
REFRESH_TIME = 1.0
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

#Range finder inits
trig0 = OutputDevice()
echo0= InputDevice()
trig1 = OutputDevice()
echo1 = InputDevice()

#Other inits
led = LED()
bar_up = 0
userFile = "BenchUsers.txt"
reps = 0
prev = -1
weight = 0
lastTime = time()
user_id = ""
end_screen = []
end_page = 0

userFlag = False
weightFlag = False

sleep(2)

def get_Users():
    users = {}
    f = open(userFile)
    for line in f:
        line = line.strip()
        line = line.split("|")
        line[1] = line[1].split(",")
        users[line[0]] = line[1]
    f.close()
    return users
    
def update_file():
    users[user_id][-1] = reps
    users[user_id][-2] = weight
    f = open(userFile, "w")
    for user in users.keys:
        f.write(user + "|" + users[user][0] + "," + users[user][1] + "," + users[user][2])
    f.close()

def get_pulse_time0():
    trig0.on()
    sleep(0.00001)
    trig0.off()

    while echo0.is_active == False:
        pulse_start = time()

    while echo0.is_active == True:
        pulse_end = time()

    sleep(0.06)

    return pulse_end - pulse_start

def get_pulse_time1():
    trig1.on()
    sleep(0.00001)
    trig1.off()

    while echo1.is_active == False:
        pulse_start = time()

    while echo1.is_active == True:
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

def calculate_acceleration(v0, v1, now):
    return (v1-v0)/(now-lastTime)

def read_user_average(userfile):
    with open(userfile) as ins:
    array = []
    avg_reps = 
    for line in ins:
        line.strip()
        array.append(line) # not sure if this is correct, but I want to append everything in the line to include historical user's data in array
        summation = sum(array)
        avg_reps = summation/len(array)

def lift_bars():
    led.on()
    bar_up = 1

def lower_bars():
    led.off()
    bar_up = 0

def end_screen_init():
    end_screen[0] = "A:last page \n D:next page"
    end_screen[1] = "ENTER: lower bars and exit"
    end_screen[2] = "Completed " + reps + " reps at " + weight + " lbs"
    end_screen[3] = "Completed " + users[user_id][-1] + " reps at " + users[user_id][-2] + " lbs"
    
def screen_back():
    if end_page == 0:
        end_page = 2
    else:
        end_page--

def screen_forward()
    if end_page == 2:
        end_page = 0
    else:
        end_page++

def display_end():
    lcd.clear()
    if end_page == 2:
        lcd.message("Current session results")
        sleep(1)
        lcd.clear()
    elif end_page == 3:
        lcd.message("Last session results")
        sleep(1)
        lcd.clear()
    lcd.message(end_screen[end_page])
    
def cleanup():
    bar_up = 0
    reps = 0
    prev = -1
    weight = 0
    user_id = ""
    end_page = 0
    userFlag = False
    weightFlag = False
    
while True:
    lcd.enable_display(True)
    users = get_Users()
    while not userFlag:
        lcd.clear()
        lcd.message("Please enter your user ID: " + user_id)
        ui = readchar.readkey()
        now = time()
        while now - lastTime < REFRESH_TIME:
            sleep(.5)
            now = time()
        if ui != readchar.keys.ENTER:
            user_id += ui
        else:
            if user_id in users:
                userFlag = 1
            else:
                lcd.clear()
                lcd.message("Incorrect User ID")
                user_id = ""
    lcd.clear()
    lcd.message("Hello " + users[user_id][0])
    sleep(3)
    while not weightFlag:
        weight_str = ""
        lcd.clear()
        lcd.message("Please enter bar weight: " + weight)
        bi = readchar.readkey()
        now = time()
        while now - lastTime < REFRESH_TIME:
            sleep(.5)
            now = time()
        if bi != readchar.key.ENTER and bi.isdigit():
            weight_str += bi
        else:
            if weight_str.isdigit():
                weight = int(weight_str)
                weightFlag = 1
            else:
                lcd.clear()
                lcd.message("Incorrect char for weight")
                weight_str = ""

    duration = get_pulse_time0()
    dist0_orig = calculate_distance(duration)
    print(dist0_orig)
    duration = get_pulse_time1()
    dist1_orig = calculate_distance(duration)
    last_dist0 = dist0_orig
    last_dist1 = dist1_orig
    lastTime = time()
    v_last = 0
    lift_error = 0
    direction = 0 # 1 for up, 0 for down
    stuck = 0
    while True:
        sleep(.05)
        duration = get_pulse_time0()
        dist0 = calculate_distance(duration)
        duration = get_pulse_time1()
        dist1 = calculate_distance(duration)
        now = time()
        v_now = calculate_velocity(dist0,dist1,last_dist0,last_dist1,now)
        accel = calculate_acceleration(v_last, v_now, now)
        lastTime = now
        if accel <= -9:
            lift_bars()
            lift_error = 2
            break
        if abs(dist0 - dist1) > .2:
            lift_bars()
            lift_error = 1
            break
        elif last_dist0 > dist0 and last_dist1 > dist1:
            stuck = 0
            if direction == 1:
                reps++
            direction = 0
        elif last_dist0 < dist0 and last_dist1 < dist1:
            stuck = 0
            direction = 1
        elif abs(dist0-last_dist0) < .1 and abs(dist1-last_dist1) < .1:
            if stuck:
                lift_bars()
                lift_error = 3
                break
            stuck = 1
    while bar_up:
        end_screen_init()
        lcd.clear()
        lcd.message("Completed " + reps + " reps!")
        sleep(2)
        ei = readchar.readkey()
        while True:
            display_end()
            ei = readchar.readkey()
            now = time()
            while now - lastTime < REFRESH_TIME:
                sleep(.5)
                now = time()
            if ei == "a":
                screen_back()
            elif ei == "d":
                screen_forward()
            elif ei == readchar.keys.ENTER:
                lower_bars()
                break
    update_file()
    cleanup()
