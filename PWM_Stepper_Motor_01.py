    
from time import sleep
import gpiozero

class syringe:
    def __init__(self,delay):
        self.ENE = gpiozero.DigitalOutputDevice(22)    #LED(22) # Controller Enable Bit (High to Enable / LOW to Disable).
        self.DIR = gpiozero.DigitalOutputDevice(27) # Controller Direction Bit (High for Controller default / LOW to Force a Direction Change).
        self.PUL = gpiozero.DigitalOutputDevice(17) # Stepper Drive Pulses
        self.maxbutton = gpiozero.Button(16)
        self.minbutton = gpiozero.Button(20)
        self.delay = delay       #0.0000015#0.000001   # This is actualy a delay between PUL pulses - effectively sets the mtor rotation speed.
        
    def forward(self,duration):
        self.ENE.on()
        self.DIR.off()
        print(f'DIR set to HIGH - Moving Forward at {str(self.delay)} ')
        print('Controller PUL being driven.')
        for x in range(duration): 
            buttonhigh = self.maxbutton.is_pressed
            print(buttonhigh)
            if buttonhigh:
                print('Max bewging is bereikt.')
                break
            else:
                self.PUL.on()
                sleep(self.delay)
                self.PUL.off()
                sleep(self.delay)
        self.ENE.off()    
        sleep(.5) # pause for possible change direction
        return
       
        
    def totalbackward(self):
        timeout = 0
        self.ENE.on()
        self.DIR.on()
        print('DIR set to LOW - Moving backward at ' + str(delay))
        print('Controller PUL being driven.')
        backstop = self.minbutton.is_pressed
        while backstop == False:
            if timeout < 10000: 
                self.PUL.on()
                sleep(self.delay)
                self.PUL.off()
                sleep(self.delay)
                timeout += 1
            else:
                break
        
        if backstop:
            print('Terug in achterste positie')
        self.ENE.off()    
        sleep(.5) # pause for possible change direction
        return
        
    def stepbackward(self,duration):
        self.ENE.on()
        self.DIR.on()
        print('DIR set to HIGH - Moving backwards at ' + str(self.delay))
        print('Controller PUL being driven.')
        for x in range(duration): 
            buttonhigh = self.minbutton.is_pressed
            print(buttonhigh)
            if buttonhigh:
                print('Min bewging is bereikt.')
                break
            else:
                self.PUL.on()
                sleep(self.delay)
                self.PUL.off()
                sleep(self.delay)
                
        self.ENE.off()    
        sleep(.5) # pause for possible change direction
        return
  


syr = syringe(0.000001)

#syr.forward(1000)
syr.stepbackward(12000)


