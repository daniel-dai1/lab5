from machine import Pin, I2C
import time

# Initialize I2C channel 1 for the DS3231 RTC module (GPIO14 = SDA, GPIO15 = SCL)
i2c = I2C(1, sda=Pin(14), scl=Pin(15))
RTC_ADDR = 0x68  # DS3231 I2C default address

# Configure button and LED based on the expansion board layout
button = Pin(10, Pin.IN, Pin.PULL_DOWN)
led = Pin(18, Pin.OUT)


def get_rtc_seconds():
    """Reads the seconds register (0x00) from the DS3231 and converts BCD to integer."""
    data = i2c.readfrom_mem(RTC_ADDR, 0x00, 1)
    raw_byte = data[0]
    # Convert Binary Coded Decimal (BCD) to decimal integer
    tens = (raw_byte >> 4) & 0x0F
    units = raw_byte & 0x0F
    return tens * 10 + units


def run_perception_game():
    print("--- 15-Second Perception Game Started ---")
    print(
        "Press the button to start, and press it again when you think 15 seconds have passed."
    )
    print("Press Ctrl+C to safely exit and save your log file.\n")

    # Open log file in append mode to preserve previous trial history
    log_file = open("log.txt", "a")

    try:
        while True:
            # Wait for button press to start timing round
            while button.value() == 0:
                time.sleep(0.05)

            led.value(1)  # Turn on LED indicating timer start
            start_time = get_rtc_seconds()
            print("\n[Started] Counting 15 seconds...")

            # Debounce delay
            time.sleep(0.3)

            # Wait for button press to stop timing round
            while button.value() == 0:
                time.sleep(0.05)

            end_time = get_rtc_seconds()
            led.value(0)  # Turn off LED

            # Handle 60-second roll-over condition
            elapsed_time = (end_time - start_time) % 60

            print(f"[Finished] Target: 15s | Measured: {elapsed_time}s")

            # Write result to log file and flush buffer immediately to flash
            log_file.write(f"Measured_Time_Seconds: {elapsed_time}\n")
            log_file.flush()

            # Brief pause before next round
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nProgram terminated by user. Closing log file safely...")
    finally:
        log_file.close()
        print("Log file closed and saved.")


if __name__ == "__main__":
    run_perception_game()