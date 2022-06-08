#!/usr/bin/python

import requests
import json
import lcddriver
import time
import socket

# ------------------------------------------------------------------------------------------------
# - VOLUMIO - 
# - print message on LCD screen HD4470
# ------------------------------------------------------------------------------------------------
# - 0.1 - 2021/11/10 - first version
# - 0.2 - 2021/11/15 - minor bug correction
# - 0.3 - 2022/01/03 - add scroll to long played song title on line 2
# ------------------------------------------------------------------------------------------------
# - E.Malosse - 
# -------------



s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))


lcd = lcddriver.lcd()			# --- Init Lcd
lcd.lcd_clear()			# --- Clear Lcd

print ("Welcome message")
print ("@" + s.getsockname()[0])

lcd.lcd_display_string(" cNuma - 2022/01", 1)
lcd.lcd_display_string("@"+ s.getsockname()[0], 2)

s.close()
time.sleep(5)

lcd.lcd_clear()

# --- Init global var ---
titleLCD_Old = ""
volume_Old = -1
statusPOld = "na"
lcdPos = 1


while True:

  try:
    response = requests.get("http://192.168.1.151:3000/api/v1/getState")
    jsonResponse = response.json()
    
    #print (jsonResponse['title'])

    statusPlayer = jsonResponse['status']

    if statusPlayer == "play":

        titleLCD = jsonResponse['title']
        titleLCD = titleLCD.encode('ascii', 'replace')

        volume = jsonResponse['volume']

        if jsonResponse['service'] == "webradio":
          L1 = "Webradio Vol=" + str(volume) + "%"
          titleLCD = jsonResponse['artist']
          titleLCD = titleLCD[:titleLCD.find(".")]
          titleLCD += " - " + jsonResponse['bitrate']
        else:
          L1 = "Spotify Vol=" + str(volume) + "%"
          titleLCD = jsonResponse['title']

        titleLCD = titleLCD.encode('ascii', 'replace')

        if (titleLCD <> titleLCD_Old) or (volume <> volume_Old):
          print (jsonResponse)
          
          lcd.lcd_clear()
          titleLCD_Old = titleLCD
          titleLCD_Len = len(titleLCD)
          titleLCD_Start = -1
          titleLCD_End   = 15
          volume_Old = volume

        print ("titleLCD_Len: " + str(titleLCD_Len))
        print ("titleLCD_Start: " + str(titleLCD_Start))
        print ("titleLCD_End: " + str(titleLCD_End))

		# --- Scrolling line 2 ---
        if titleLCD_Len > 15:
          if titleLCD_End < titleLCD_Len:
            titleLCD_Start += 1
            titleLCD_End   += 1
          elif titleLCD_Start < titleLCD_Len:
            titleLCD_Start += 1
          else:
            titleLCD_Start = 0
            titleLCD_End   = 15
            
          titleLCD = titleLCD_Old[titleLCD_Start:titleLCD_End]

        if (titleLCD_End - titleLCD_Start) < 15:
          for i in range (15 - (titleLCD_End - titleLCD_Start), 16):
            titleLCD = titleLCD + " "


        print ("Title to LCD: " + titleLCD)
        lcd.lcd_display_string(L1, 1)
        lcd.lcd_display_string(titleLCD, 2)


    else:
        if statusPOld != statusPlayer: 
         print ("Status different - MAJ status stop !")
         statusPOld = statusPlayer
         
         lcd.lcd_clear()
         lcd.lcd_display_string("    - " + statusPlayer + " -", 2)

  
  except:
    lcd.lcd_clear()
    
    if lcdPos > 2:
        lcdPos = 1
    else:
        lcdPos += 1
        
        
    lcd.lcd_display_string("Wait for Volumio", lcdPos)
    
  
  time.sleep(1)
