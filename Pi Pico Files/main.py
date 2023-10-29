from machine import Pin, I2C, SPI
from time import sleep

from pico_i2c_lcd import I2cLcd
from SSD1306 import SSD1306_I2C
from urtc import DS3231

import sdcard
import uos

i2c=I2C(0,sda=Pin(0),scl=Pin(1),freq=400000)
power=I2C(1,scl=Pin(3),sda=Pin(2),freq=100000)
addr=power.scan()[0]

#print(hex(i2c.scan()[0]))
lcd=I2cLcd(i2c,0x27,2,16)
oled=SSD1306_I2C(128,64,i2c)
rtc=DS3231(i2c)

cs = machine.Pin(13, machine.Pin.OUT)
spi = machine.SPI(1,baudrate=1000000,polarity=0,phase=0,bits=8,firstbit=machine.SPI.MSB,sck=machine.Pin(10),mosi=machine.Pin(11),miso=machine.Pin(12))
sd=sdcard.SDCard(spi,cs)
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")

total_power=0.00
hour_power=0.00
minute_power=0.00

temp_hour=[]
temp_count=0
for i in range(0,120):
       temp_hour.append(0)

def save_total_pow():                                                         #TO SAVE TOTAL_POWER DATA TO TOTAL_POWER FILE
    (year,month,date,day,hour,minute,second,p1)=rtc.datetime()
    
    global total_power
    temp=str(total_power)
    with open("/sd/Total_Power.txt", "w") as file:
        file.write(temp+"\r\n")
        file.close()

def save_hour_pow():                                                          #TO SAVE HOUR_POWER DATA TO HOUR_POWER FILE
    (year,month,date,day,hour,minute,second,p1)=rtc.datetime()
    
    global hour_power
    temp=str(hour_power)
    with open("/sd/Hour_Power.txt", "a") as file:
        file.write(str(hour)+":00"+":00"+" "+temp+"\r\n")
        file.close()
    hour_power=0.00

def save_minute_pow():                                                        #TO SAVE MINUTE_POWER DATA TO MINUTE_POWER FILE
    (year,month,date,day,hour,minute,second,p1)=rtc.datetime()
    
    global minute_power
    temp=str(minute_power)
    with open("/sd/Minute_Power.txt", "a") as file:
        file.write(str(hour)+":"+str(minute)+":00"+" "+temp+"\r\n")
        file.close()
    minute_power=0.00
    
def read_arduino():                                                           #TO GET DATA FROM ARDUINO
    second_data=0.00
    a= power.readfrom(addr,5)
    b=(a[4]*100+a[3]*10+a[2]+((a[1]*10+a[0])/100))
    second_data = second_data + float(b)
    return second_data
    
def calc_minute():                                                            #TO CALCULATE MINUTE DATA
    global minute_power,temp_hour,temp_count
    
    temp_minute=0.00
    count=0
  
    (year,month,date,day,hour,minute,second,p1)=rtc.datetime()
    
    while True:
        temp_minute=temp_minute + read_arduino()
        count = count + 1
        sleep(1)
        (year,month,date,day,hour,minute,second,p1)=rtc.datetime()
        
        if int(str(second)) == 58:
            break
          
    minute_power = temp_minute/count
    print(minute_power)           #debug only
    save_minute_pow()
    count=0
    
    temp_hour[temp_count]=minute_power
    temp_count = temp_count + 1
    
    (year,month,date,day,hour,minute,second,p1)=rtc.datetime()
    if(int(str(hour))) == 59:
        if(int(str(second))) > 57:
            calc_hour()
    
def calc_hour():                                                              #TO CALCULATE HOUR DATA
    global temp_hour,temp_count,total_power
    temp=0.00
    
    for x in range(0,temp_count):
        temp = temp + temp_hour[x]
        
    hour_power = temp/temp_count
    print(hour_power)               #debug only
    save_hour_pow()
    
    total_power = total_power + hour_power
    save_total_pow()
    
    temp_count=0

def print_lcd():                                                              #TO PRINT ON LCD
    global total_power
    lcd.clear()
    print(total_power)
    lcd.putstr(str(int(total_power)))
    
def print_oled():                                                             #TO PRINT ON OLED
    oled.fill(0)
    oled.text("Link Status:Ok",0,0)
    oled.show()
    
def read_file():                                                              #TO READ BACK TOTAL POWER AFTER POWER CUTS
    global total_power
    with open("/sd/Total_Power.txt", "r") as file:
        data = file.read()
        x=float(data)
        print(x)
        total_power = x
        file.close()



read_file()

while True:
    
    calc_minute()
    print_lcd()
    print_oled()








