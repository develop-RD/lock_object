import wiringpi

OUTPUT = 1

PIN_TO_PWM_0 = 2 # 7 pin
PIN_TO_PWM_1 = 3 # 8 pin

# init gpio
wiringpi.wiringPiSetup()
# activate pinMode 7 
#wiringpi.pinMode(PIN_TO_PWM_0,OUTPUT)
wiringpi.pinMode(PIN_TO_PWM_1,OUTPUT)
dl = 500
# 200 - соответствует 20 мс
#wiringpi.softPwmCreate(PIN_TO_PWM_0,0,dl)
wiringpi.softPwmCreate(PIN_TO_PWM_1,0,dl)
while True:
    for i in range(0,361):
        sig=int((i/18)+2)
        print("signal = ",sig)
#        wiringpi.softPwmWrite(PIN_TO_PWM_0,sig)
        wiringpi.softPwmWrite(PIN_TO_PWM_1,sig)
        wiringpi.delay(100)
        print(i)
    print("_________")
    wiringpi.delay(200)
#    wiringpi.softPwmStop(2)
#    wiringpi.softPwmStop(3)
#    wiringpi.delay(500)
#    wiringpi.softPwmCreate(PIN_TO_PWM_0,0,dl)
#    wiringpi.softPwmCreate(PIN_TO_PWM_1,0,dl)
