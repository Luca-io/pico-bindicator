# pico-bindicator
A black bag collection date and wind speed notifier running on the RPi Pico with an ePaper display

**DISCLAIMER: I have ZERO electronics experience and a very basic understanding of coding. Everything here is probably horribly coded and there are probably many improvements to be made.**

![The bindictor](https://i.imgur.com/ffHfOLI.jpeg)

## Hardware Needed

- Raspberry Pi Pico 2 W (The original Pico probably works fine too)
- Pico Header Pins
- ePaper display (I've used the 2.13" WaveShare display)
- Some sort of power (can be powered via USB or I have opted for a battery pack for the Pico)

## Pre-Prerequisites

1. Solder the header pins to your Pico - pretty self explanitory
Once soldered you can plug the Pico into the ePaper display board (might be different if you are using a different ePaper display model)

2. Sign up for an OpenWeather API key - it's free for basic usage
https://openweathermap.org/api

3. Install MicroPython onto your Pico
https://www.raspberrypi.com/documentation/microcontrollers/micropython.html

4. Get some sort of IDE to code in and get your files onto the Pico
I used Thonny - https://thonny.org/

5. Get the display "drivers" for your ePaper display
I got my WaveShare ones from https://github.com/waveshareteam/Pico_ePaper_Code/tree/main/python

## Guide

### Setup
1. Connect Pico to your computer
2. Open your IDE, in my case Thonny
3. Transfer all the python files in this git to your Pico
4. Transfer the display driver file to your Pico

### Functions.py
1. You'll probably have to re-write the 'collection_date' function as this is currently setup to scrape my councils website. Your local council's website probably has a different format so it will have to reflect that.
2. Update 'get_next_sunday_monday_timestamps' to be for the dates before and on the collection date in your location
3. Update 'get_forecast' to be for the dates before and on the collection date in your location

### Wifi.py
1. Add your wifi networks name and password - yes storing this in plaintext is terrible security

### Main.py
1. Update the first line to import the drivers for your specific ePaper display model
2. Update the url in 'update_display' for your local council's bin collection page - line 22
3. Update your OpenWeather API key - line 31
4. Update your location - line 32
5. NOTE: If you are using a different display driver the epd commands in 'update_display' may also need updating
6. Update the the text to be displayed on line 45 onwards to be for your collection days as well as updating the variable names if you changed them in functions.py
7. Optional: change the update days and intervals in 'check and update'
