import time
from machine import I2C, Pin, SPI
from mfrc522 import MFRC522

### Settings for output ###
led = Pin(25, Pin.OUT) # in-built LED
buzzer = Pin(15 , Pin.OUT) # sound buzzer Pin15 to positive on buzzer
relay = Pin(16, Pin.OUT) # relay for door strike

### Settings for button ###
button = Pin(15, Pin.IN, Pin.PULL_DOWN)

### Settings for Keypad ###
KEY_UP   = const(0)
KEY_DOWN = const(1)
keys = [['1', '2', '3', 'A'], ['4', '5', '6', 'B'], ['7', '8', '9', 'C'], ['*', '0', '#', 'D']]
# Pin names for Pico
rows = [10,11,12,13]
cols = [18,19,20,21]
# set pins for rows as outputs
row_pins = [Pin(pin_name, mode=Pin.OUT) for pin_name in rows]
# set pins for cols as inputs
col_pins = [Pin(pin_name, mode=Pin.IN, pull=Pin.PULL_DOWN) for pin_name in cols]

pincode1 = 5544
pincode2 = 3322

def init():
    for row in range(0,4):
        for col in range(0,4):
            row_pins[row].low()

def scan(row, col):
    """ scan the keypad """

    # set the current column to high
    row_pins[row].high()
    key = None

    # check for keypressed events
    if col_pins[col].value() == KEY_DOWN:
        key = KEY_DOWN
    if col_pins[col].value() == KEY_UP:
        key = KEY_UP
    row_pins[row].low()

    # return the key state
    return key

### Settings for RFID Board ###
true = Pin(15, Pin.OUT) # not using
false = Pin(14, Pin.OUT) # not using
sck = Pin(6, Pin.OUT)
mosi = Pin(7, Pin.OUT)
miso = Pin(4, Pin.OUT)
sda = Pin(5, Pin.OUT)
rst = Pin(22, Pin.OUT)
spi = SPI(0, baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
card1 = "0003053784"
card2 = "0x88043cb3"
card3 = ""
card4 = ""
card5 = ""
card6 = ""

### General functions
def grant_access(method):
    print("Access Granted:", method)
    led.value(1)
    #buzzer.value(1)
    relay.low()
    time.sleep(3)
    led.value(0)
    #buzzer.value(0)
    relay.high()
    time.sleep(3)
    

# Initialize - set all the keypad columns to low
init()
relay.high()

print("starting access control")
pin_code = []
incorrect_passcode_attempts = 0
time_since_last_attempt = 0
incorrect_delay = 0
while True:
    ### Exit button
    if button.value():
        grant_access("Exit button pushed")

    ### Keypad ###
        
    # First we check if the keypad is locked from multiple attempts
    current_time = time.time() # get current timestamp
    if incorrect_passcode_attempts > 0: # check for incorrect password attempts
        time_since_last_attempt = current_time - delay_timer
        
    if time_since_last_attempt >= incorrect_delay: # activate keypad if not within delay period
        for row in range(4):
            for col in range(4):
                key = scan(row, col)
                if key == KEY_DOWN:
                    print("Key Pressed", keys[row][col])
                    buzzer.value(1)
                    time.sleep(0.1)
                    buzzer.value(0)
                    pin_code.append(keys[row][col])
                    if len(pin_code) == 4:
                        pin4 = pin_code[0]+pin_code[1]+pin_code[2]+pin_code[3]
                        if pin4 == str(pincode1) or pin4 == str(pincode2):
                            pin_success = "Access Granted: Correct Pin Entered: " + pin4
                            grant_access(pin_success)
                            pin_code = []
                        
                        else:
                            print("Access Denied: Incorrect pin entered:", pin4)
                            pin_code = []
                            time.sleep(0.2)
                            buzzer.value(1)
                            time.sleep(0.2)
                            buzzer.value(0)
                            time.sleep(0.2)
                            buzzer.value(1)
                            time.sleep(0.2)
                            buzzer.value(0)
                            time.sleep(0.2)
                            buzzer.value(1)
                            time.sleep(0.2)
                            buzzer.value(0)
                            
                            delay_timer = time.time()
                            incorrect_passcode_attempts += 1
                            print("Incorrect password attempts: {}".format(incorrect_passcode_attempts))
                            incorrect_delay = incorrect_passcode_attempts ** 2
                            print("Keypad locked for {} seconds".format(incorrect_delay))                    


    ### RFID
    rdr = MFRC522(spi, sda, rst)
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
        (stat, raw_uid) = rdr.anticoll()
        if stat == rdr.OK:
            uid = ("0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
            #print(uid)
            if uid == card1:
                true.value(1)
                time.sleep(1)
                true.value(0)
                time.sleep(1)
            elif uid == card2:
                rfid_success_message = "Access Granted: RFID Scan Successful - Card 2 -  {}".format(uid)
                grant_access(rfid_success_message)
                incorrect_passcode_attempts = 0 # in-case keypad is locked, reset
                incorrect_delay = 0 
            else:
                print("Access Denied: Invalid RFID card swiped: {}".format(uid))
                time.sleep(3)
