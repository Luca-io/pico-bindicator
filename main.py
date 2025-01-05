from epdDriver import EPD_2in13_B
import utime
from time import sleep
from wifi import connect
from functions import *
import machine

# Global variables for shared resources
epd = None

# Initialize wifi connection and display on startup
def initialize():
    global epd
    connect()
    epd = EPD_2in13_B()

# Main function to update the display with collection and weather data - also draws the text on the screen
def update_display():
    global epd
    
    # Get bin collection date
    url = "LOCAL COUNCIL COLLECTION URL"
    collection_date_str = collection_date(url)
    # This bit will probably need updating depeding on the format extracted from your councils website
    day = collection_date_str.split()[0][:3]
    date = collection_date_str.split()[1]
    month = collection_date_str.split()[2][:3]

    date_image = get_date_image(date)

    # Get wind speeds
    api_key = "OPENWEATER API KEY"
    location = "YOUR LOCATION"
    warning_threshold = 30 #When the windspeed is above this speed it will show as a red warning on the display (mph)
    forecast = get_forecast(api_key, location)

    # Write text to the display
    epd.imageblack.fill(0xff)  # Clear black buffer
    epd.imagered.fill(0xff)    # Clear red buffer

    #Draw data to screen
    epd.imageblack.text('Black Bags:', 2, 20, 0x00)
    display_image(epd, date_image, 50, 50, 5, 40) # The display only has one font size, I've created a larger image of each date in numbers.py and this displays that larger number image
    epd.imageblack.text(day, 5, 35, 0x00)
    epd.imageblack.text(month, 5, 85, 0x00)

    epd.imageblack.text("Sun Wind:", 2, 115, 0x00) # Update here for the days that your collection occurs
    if forecast['sunday_9pm'] > warning_threshold:
        epd.imagered.text(str(forecast['sunday_9pm'])+"mph(!)", 10, 125, 0x00)
    else:
        epd.imageblack.text(str(forecast['sunday_9pm'])+"mph", 10, 125, 0x00)
    
    epd.imageblack.text("Mon Wind:", 2, 140, 0x00)
    if forecast['monday_9am'] > warning_threshold:
        epd.imagered.text(str(forecast['monday_9am'])+"mph(!)", 10, 150, 0x00)
    else:
        epd.imageblack.text(str(forecast['monday_9am'])+"mph", 10, 150, 0x00)
    
    epd.imageblack.text("Max Wind:", 2, 165, 0x00)
    if forecast['max_wind'] > warning_threshold:
        epd.imagered.text(str(forecast['max_wind'])+"mph(!)", 10, 175, 0x00)
    else:
        epd.imageblack.text(str(forecast['max_wind'])+"mph", 10, 175, 0x00)
        
    epd.imageblack.hline(5, 103, 94, 0x00)
        
    epd.display()  # Display the buffers

# Check if it's time to update and run the update if needed
def check_and_update():
    current_time = utime.localtime()
    weekday = current_time[6]  # 0-6, where 6 is Sunday
    hour = current_time[3]
    minute = current_time[4]
    
    should_update = False
    
    if weekday == 6:  # Sunday
        # Update at the start of every hour (when minutes = 0)
        if minute == 0:
            should_update = True
    else:  # Other days
        # Update only at 12:00
        if hour == 12 and minute == 0:
            should_update = True
            
    if should_update:
        update_display()
        # Sleep for 60 seconds to avoid multiple triggers
        utime.sleep(60)

def main():
    # Initialize on startup
    initialize()
    
    # Run initial update
    update_display()
    
    # Set up timer for periodic checking
    timer = machine.Timer(-1)
    # Check every minute (60000 ms)
    timer.init(period=60000, mode=machine.Timer.PERIODIC, callback=lambda t: check_and_update())

    # Keep the script running
    while True:
        utime.sleep(1)

if __name__ == "__main__":
    main()
