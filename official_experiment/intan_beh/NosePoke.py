# NosePoke is a class that controls the physical nose poke device in the rig. Input variable light = GPIO pin for
# controlling LED in the nosepoke (1 = on, 0 = off). Input variable beam = GPIO pin receiving input from IR
# beam-break sensor inside nose poke device (1 = uncrossed, 0 = crossed)
class NosePoke:
    def __init__(self, light, beam):
        self.exit = None
        self.light = light
        self.beam = beam
        self.endtime = time.time() + 1200  # endtime is a class-wide condition to help the program exit when the task
        # is over. Usually this variable is changed when a behavioral task program is initiated
        GPIO.setup(self.light, GPIO.OUT)
        GPIO.setup(self.beam, GPIO.IN) 

    def shutdown(self):
        print("blink shutdown")
        self.exit.set()

    def flash_on(self):  # turn the light on
        GPIO.output(self.light, 0)

    def flash_off(self):  # turn the light off
        GPIO.output(self.light, 1)

    def flash(self, hz, run):  # bink on and of at frequency hz (LED has physical limit of 3.9)
        print("flashing "+str(self.light)+" start")
        while time.time() < self.endtime:
            if run.value == 1:
                GPIO.output(self.light, 1)
            if run.value == 1:
                time.sleep(2 / hz)            # try to consolidate 
                GPIO.output(self.light, 0)    # test
            if run.value == 1:
                time.sleep(2 / hz)
            if run.value == 0:
                GPIO.output(self.light, 0)
            if run.value == 2:
                GPIO.output(self.light, 1)
        print("flashing "+str(self.light)+" start")

    def is_crossed(self):  # report if beam is crossed
        return GPIO.input(self.beam) == 1
          
    def keep_out(self, wait):  # report when the animal has stayed out of the nosepoke for duration of [wait] seconds
        print("keep out start")
        start = time.time()
        while True and time.time() < self.endtime:
            if self.is_crossed():
                start = time.time()
            elif time.time() - start > wait:
                break
        print("keep out end")

    def kill(self):  # kind of useless method
        GPIO.output(self.light, 0)
