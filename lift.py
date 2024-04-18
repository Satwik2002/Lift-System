from gpiozero import LED
from time import sleep
import random

floorLeds = [LED(17), LED(27), LED(22), LED(23)]
upLed = LED(24) # for engage up
downLed = LED(25) # for engage down
liftDoor = LED(19)
motorLed = LED(16)
emergencyStop = LED(6)
i = 0
current_floor_light = True

# Define BDD table and control memory
BDD_Table = [
    {'N_type': 'x', 'N_index': 1, 'successor0': 2, 'successor1': 1},
    {'N_type': 'a', 'N_index': 1, 'successor0': None, 'successor1': 5},
    {'N_type': 'x', 'N_index': 2, 'successor0': 4, 'successor1': 3},
    {'N_type': 'a', 'N_index': 2, 'successor0': None, 'successor1': 12},
    {'N_type': 'a', 'N_index': 0, 'successor0': None, 'successor1': 0},
    {'N_type': 'x', 'N_index': 3, 'successor0': 6, 'successor1': 7},
    {'N_type': 'a', 'N_index': 1, 'successor0': None, 'successor1': 5},
    {'N_type': 'x', 'N_index': 5, 'successor0': 9, 'successor1': 8},
    {'N_type': 'a', 'N_index': 5, 'successor0': None, 'successor1': 23},
    {'N_type': 'x', 'N_index': 6, 'successor0': 11, 'successor1': 10},
    {'N_type': 'a', 'N_index': 3, 'successor0': None, 'successor1': 21},
    {'N_type': 'a', 'N_index': 4, 'successor0': None, 'successor1': 22},
    {'N_type': 'x', 'N_index': 3, 'successor0': 13, 'successor1': 14},
    {'N_type': 'a', 'N_index': 2, 'successor0': None, 'successor1': 12},
    {'N_type': 'x', 'N_index': 4, 'successor0': 15, 'successor1': 16},
    {'N_type': 'a', 'N_index': 5, 'successor0': None, 'successor1': 23},
    {'N_type': 'x', 'N_index': 5, 'successor0': 18, 'successor1': 17},
    {'N_type': 'a', 'N_index': 5, 'successor0': None, 'successor1': 23},
    {'N_type': 'x', 'N_index': 6, 'successor0': 20, 'successor1': 19},
    {'N_type': 'a', 'N_index': 3, 'successor0': None, 'successor1': 21},
    {'N_type': 'a', 'N_index': 4, 'successor0': None, 'successor1': 22},
    {'N_type': 'a', 'N_index': 6, 'successor0': None, 'successor1': 24},
    {'N_type': 'a', 'N_index': 6, 'successor0': None, 'successor1': 24},
    {'N_type': 'a', 'N_index': 0, 'successor0': None, 'successor1': 0},
    {'N_type': 'x', 'N_index': 7, 'successor0': 26, 'successor1': 25},
    {'N_type': 'a', 'N_index': 8, 'successor0': None, 'successor1': 30},
    {'N_type': 'x', 'N_index': 5, 'successor0': 27, 'successor1': 28},
    {'N_type': 'a', 'N_index': 6, 'successor0': None, 'successor1': 24},
    {'N_type': 'a', 'N_index': 7, 'successor0': None, 'successor1': 29},
    {'N_type': 'a', 'N_index': 5, 'successor0': None, 'successor1': 23},
    {'N_type': 'x', 'N_index': 8, 'successor0': 31, 'successor1': 32},
    {'N_type': 'a', 'N_index': 8, 'successor0': None, 'successor1': 30},
    {'N_type': 'a', 'N_index': 5, 'successor0': None, 'successor1': 23},
]

control_memory = [
    {'imm_transition': False, 'control': 'y0'},
    {'imm_transition': False, 'control': 'y1'},
    {'imm_transition': False, 'control': 'y1'},
    {'imm_transition': True, 'control': 'y2'},
    {'imm_transition': True, 'control': 'y3'},
    {'imm_transition': True, 'control': 'y4'},
    {'imm_transition': False, 'control': 'y5'},
    {'imm_transition': True, 'control': 'y6'},
    {'imm_transition': False, 'control': 'y7'}
]


current_floor = 0
target_floor = 0
upDirection = False
downDirection = False


# x is boolean array of size 8
# x = [lift_request, destn_request, doors_closed, person_inside, same_floor, current<target, emergency_sensor, safety_recovered]
x = [0, 0, 0, 0, 0, 0, 0, 0]

def take_inputs():
    global current_floor, target_floor, x
    print("Inside take_inputs")
    print("Lift requested from floor? (1, 0)")
    x[0] = int(input())
    if x[0] == 0:
        print("Destination requested from floor? (1, 0)")
        x[1] = int(input())

    if x[0] == 1 or x[1] == 1:
        print("Input target floor (0, 3): ")
        target_floor = int(input())
        
        x[4] = int(current_floor == target_floor)
        x[5] = int(current_floor < target_floor)
        if x[1]==1:
            print("Is there a person inside? (1, 0)")
            x[3] = int(input())



def close_doors():
    print("Inside close_doors")
    # blink both current_floor LED door and lift door LED at same time
    global current_floor, x
    floorLeds[current_floor].blink(on_time=0.5, off_time=0.5, n=3)
    liftDoor.blink(on_time=0.5, off_time=0.5, n=3)
    sleep(3.5)
    liftDoor.off()
    x[2] = 1
    return

def up_actuator():
    global upDirection
    print("Inside up_actuator")
    upLed.on()
    upDirection = True
    return

def down_actuator():
    global downDirection
    print("Inside down_actuator")
    downLed.on()
    downDirection = True
    return

def open_door():
    print("Inside open_door")
    global current_floor, x
    # blink both current_floor LED door and lift door LED at same time
    floorLeds[current_floor].blink(on_time=0.5, off_time=0.5, n=3)
    liftDoor.blink(on_time=0.5, off_time=0.5, n=3)
    sleep(3.5)
    floorLeds[current_floor].on()
    liftDoor.on()
    x[2] = 0
    x[0] = 0
    x[1] = 0

def start_motor():
    print("Inside start_motor")
    global current_floor, target_floor, upDirection, downDirection, x, current_floor_light
    motorLed.on()
    if current_floor_light:
        current_floor_light = False
        sleep(0.5)
    else:
        current_floor = current_floor + 1 if upDirection else current_floor - 1
    floorLeds[current_floor].on()
    sleep(1)
    floorLeds[current_floor].off()

    if current_floor==target_floor:
        x[4] = 1
    return

def stop_motor():
    print("Inside stop_motor")
    global upDirection, downDirection, current_floor_light
    if upDirection:
        upLed.off()
        upDirection = False
    if downDirection:
        downLed.off()
        downDirection = False
    motorLed.off()
    current_floor_light = True
    return

def brake():
    print("Inside brake")
    
    global current_floor, upDirection, downDirection, x,current_floor_light
    if upDirection:
        upLed.off()
        upDirection = False
    if downDirection:
        downLed.off()
        downDirection = False
    motorLed.off()

    emergencyStop.on()
    print("Safety recovered ? (1, 0)")
    x[7] = int(input())
    if x[7] == 1:
        emergencyStop.off()
        x[6] = 0
        current_floor = 0
        current_floor_light =True
    return



def execute_control_action(action):
    if action == 'y0':
        take_inputs()
    elif action == 'y1':
        close_doors()
    elif action == 'y2':
        up_actuator()
    elif action == 'y3':
        down_actuator()
    elif action == 'y4':
        open_door()
    elif action == 'y5':
        start_motor()
    elif action == 'y6':
        stop_motor()
    elif action == 'y7':
        brake()
    else:
        print("Invalid control action")



# Main function for SLC driver
def SLC_Driver():
    global i
    state = 0
    while not (state and not control_memory[BDD_Table[i]['N_index']]['imm_transition']):
        sleep(0.5)
        # Random choice but 1 having higher probability for x[6]
        temp = random.randint(0,1000)
        if temp>900:
           x[6]=1
        else:
           x[6]=0
        print("BDD_Table_Index : ", i, " Sensor Values : ", x)
        index = BDD_Table[i]['N_index']
        if BDD_Table[i]['N_type'] == 'x':
            if x[index-1] == 0:
                i = BDD_Table[i]['successor0']
            else:
                i = BDD_Table[i]['successor1']
        elif BDD_Table[i]['N_type'] == 'a':
            state = 1
            if control_memory[index]['control'] is not None:
                execute_control_action(control_memory[index]['control'])
            i = BDD_Table[i]['successor1']


# Call the SLC driver
while True:
    SLC_Driver()



