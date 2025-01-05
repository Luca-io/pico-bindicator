# File contains all the various functions to be used in main

import urequests
import json
import network
import time
from machine import RTC
import numbers

# Scrape the bin collection date from the local council website - this bit will probably need a complete rework to be compatible with your local councils website
def collection_date(url):
    try:
        response = urequests.get(url)
        text = response.text
        response.close()
        
        try:
            data = json.loads(text[text.find('{'):text.rfind('}') + 1])
            next_collection_date = data["Results"]["waste"].get("residualnextcollectiondate")
            if next_collection_date:
                next_collection_date = ' '.join(next_collection_date.split())
                return next_collection_date.strip()
            return "error"
        except (ValueError, KeyError):
            return "Error: Invalid JSON format"
            
    except Exception as e:
        print("Error:", e)
        return "Error"

#Gets the date of the bin collection and maps it to the appropriate image for the larger font for the display
def get_date_image(date):
    date_to_image = {
        '01': numbers.n01,
        '02': numbers.n02,
        '03': numbers.n03,
        '04': numbers.n04,
        '05': numbers.n05,
        '06': numbers.n06,
        '07': numbers.n07,
        '08': numbers.n08,
        '09': numbers.n09,
        '10': numbers.n10,
        '11': numbers.n11,
        '12': numbers.n12,
        '13': numbers.n13,
        '14': numbers.n14,
        '15': numbers.n15,
        '16': numbers.n16,
        '17': numbers.n17,
        '18': numbers.n18,
        '19': numbers.n19,
        '20': numbers.n20,
        '21': numbers.n21,
        '22': numbers.n22,
        '23': numbers.n23,
        '24': numbers.n24,
        '25': numbers.n25,
        '26': numbers.n26,
        '27': numbers.n27,
        '28': numbers.n28,
        '29': numbers.n29,
        '30': numbers.n30,
        '31': numbers.n31,
    }
    return date_to_image.get(date, None)  # Return None if the date is not found
    
# Gets the appropriate time stamps for the day before and day of bin collection - update this for your collection days
def get_next_sunday_monday_timestamps():
    rtc = RTC()
    year, month, day, weekday, hours, minutes, seconds, _ = rtc.datetime()
    
    current = time.mktime((year, month, day, hours, minutes, seconds, weekday, 0))
    
    days_until_sunday = (6 - weekday) % 7
    if days_until_sunday == 0 and hours >= 21:
        days_until_sunday = 7
        
    sunday_seconds = days_until_sunday * 86400
    sunday_9pm = current + sunday_seconds - (hours * 3600) - (minutes * 60) - seconds + (21 * 3600)
    monday_9am = sunday_9pm + 43200  # Add 12 hours (from 9 PM to 9 AM)
    
    return sunday_9pm, monday_9am

# Gets the windspeed from OpenWeather for the days provided - update variable names for your days here
def get_forecast(api_key, location):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    url = f"{base_url}?appid={api_key}&q={location}&units=imperial"
    
    try:
        sunday_target, monday_target = get_next_sunday_monday_timestamps()
        
        response = urequests.get(url)
        data = response.json()
        response.close()
        
        forecasts_in_range = []
        sunday_wind = None
        monday_wind = None
        
        for forecast in data['list']:
            forecast_time = forecast['dt']
            
            if sunday_target <= forecast_time <= monday_target:
                forecasts_in_range.append(forecast['wind']['speed'])
            
            if abs(forecast_time - sunday_target) <= 3600:
                sunday_wind = forecast['wind']['speed']
            
            if abs(forecast_time - monday_target) <= 3600:
                monday_wind = forecast['wind']['speed']
        
        max_wind = max(forecasts_in_range) if forecasts_in_range else None
        
        return {
            'sunday_9pm': sunday_wind,
            'monday_9am': monday_wind,
            'max_wind': max_wind,
            'sunday_timestamp': sunday_target,
            'monday_timestamp': monday_target
        }
        
    except Exception as e:
        print("Error:", e)
        return None
    
# Converts the byte array of an image to an actual image to be rendered on the display - has various debugging bits in it also as this bit didn't work and drove me mad for hours
def display_image(epd, byte_array, width=50, height=50, x=0, y=0, invert=True, flip_bits=False, debug=False):
    if debug:
        print(f"Array length: {len(byte_array)} bytes")
        print(f"Image dimensions: {width}x{height} pixels")
        print(f"Expected bytes per row: {width // 8 + (1 if width % 8 else 0)}")
        
    # Verify dimensions
    if x + width > epd.width or y + height > epd.height:
        raise ValueError("Image at specified position exceeds display dimensions")
    
    # Calculate bytes per row for the image
    bytes_per_row = width // 8 + (1 if width % 8 else 0)
    
    if debug:
        print(f"Actual bytes per row: {bytes_per_row}")
        print(f"Total rows: {height}")
        print(f"Required array size: {bytes_per_row * height} bytes")
    
    # Copy the byte array data into the display buffer
    for row in range(height):
        for byte in range(bytes_per_row):
            source_idx = row * bytes_per_row + byte
            
            if source_idx >= len(byte_array):
                if debug:
                    print(f"Warning: Tried to access index {source_idx} but array length is {len(byte_array)}")
                continue
                
            target_x = x + (byte * 8)
            target_y = y + row
            
            # Get the byte from our image data
            img_byte = byte_array[source_idx]
            
            if flip_bits:
                # Reverse the bits in the byte
                img_byte = int('{:08b}'.format(img_byte)[::-1], 2)
            
            # For each bit in the byte
            for bit in range(8):
                target_bit_x = target_x + bit
                
                # Skip if we're past the image width
                if target_bit_x >= x + width:
                    continue
                
                # Get the bit value
                if flip_bits:
                    bit_val = img_byte & (1 << bit)
                else:
                    bit_val = img_byte & (0x80 >> bit)
                
                # Set the pixel
                pixel_value = (0 if bit_val else 1) if invert else (1 if bit_val else 0)
                epd.imageblack.pixel(target_bit_x, target_y, pixel_value)
