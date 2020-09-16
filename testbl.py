from evdev import InputDevice, categorize, ecodes

#creates object 'gamepad' to store the data
#you can call it whatever you like
gamepad0 = InputDevice('/dev/input/event4')
gamepad1 = InputDevice('/dev/input/event5')
gamepad2 = InputDevice('/dev/input/event6')
gamepad3 = InputDevice('/dev/input/event7')
gamepad4 = InputDevice('/dev/input/event8')
#prints out device info at start
print(gamepad0)
print(gamepad1)
print(gamepad2)
print(gamepad3)
print(gamepad4)
#evdev takes care of polling the controller in a loop
for event in gamepad4.read_loop():
    print(event.code, event.value)
