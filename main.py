import time
from machine import I2C, Pin

# GPIO pins used by the five push buttons and the two status LEDs.
BUTTON_PINS = (10, 11, 12, 13, 22)
LED_PINS = (16, 17)
LOG_FILE = "log.txt"
DS3231_I2C_ADDR = 0x68

# Set up the RTC and input/output devices used by the timing game.
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
buttons = tuple(Pin(pin, Pin.IN, Pin.PULL_DOWN) for pin in BUTTON_PINS)
leds = tuple(Pin(pin, Pin.OUT) for pin in LED_PINS)
for led in leds:
  led.value(0)  # Keep the game LEDs off until a button press is detected.


def bcd_to_dec(value):
  # Convert a binary-coded decimal byte to a normal integer value.
  return (value >> 4) * 10 + (value & 0x0F)


def read_rtc_seconds():
  """Return the DS3231 time as seconds since midnight."""
  # Read the current seconds, minutes, and hour from the RTC register block.
  data = i2c.readfrom_mem(DS3231_I2C_ADDR, 0x00, 3)
  second = bcd_to_dec(data[0] & 0x7F)
  minute = bcd_to_dec(data[1] & 0x7F)
  raw_hour = data[2]

  if raw_hour & 0x40:
    # 12-hour mode: convert from 12-hour clock with AM/PM bit handling.
    hour = bcd_to_dec(raw_hour & 0x1F)
    if hour == 12:
      hour = 0
    if raw_hour & 0x20:
      hour += 12
  else:
    # 24-hour mode: strip the lower six bits and decode the hour directly.
    hour = bcd_to_dec(raw_hour & 0x3F)

  if second > 59 or minute > 59 or hour > 23:
    raise ValueError("DS3231 returned an invalid time")

  # Convert the wall-clock time to a single count of seconds since midnight.
  return hour * 3600 + minute * 60 + second


def button_pressed():
  # True when any button is actively being held down.
  return any(button.value() == 1 for button in buttons)


def set_leds(value):
  # Apply one state to every LED so a press or idle state is visually obvious.
  for led in leds:
    led.value(value)


def wait_for_button_press():
  """Wait for a stable press and return the RTC time when it was detected."""
  while True:
    while not button_pressed():
      set_leds(0)  # Show the system is waiting for the next input.
      time.sleep(0.01)

    set_leds(1)  # Light the LEDs once a press is detected.
    pressed_at = read_rtc_seconds()
    time.sleep(0.03)  # Debounce the input to ignore noisy edge transitions.
    if button_pressed():
      return pressed_at


def wait_for_button_release():
  # Hold the LEDs on while the user keeps the button pressed, then clear them.
  while button_pressed():
    set_leds(1)
    time.sleep(0.01)
  set_leds(0)


def run_game():
  print("=== Time Perception Game Started ===")
  print("Press the button to start counting 15 seconds, then press it again.")
  print("Press Ctrl+C to stop; completed trials are saved to log.txt.")

  trial_count = 0
  with open(LOG_FILE, "a") as log_file:
    try:
      while True:
        print("\nWaiting for button press to START...")
        start_time = wait_for_button_press()
        print("Timer started! Count 15 seconds in your head...")
        wait_for_button_release()

        print("Waiting for button press to STOP...")
        end_time = wait_for_button_press()
        elapsed = (end_time - start_time) % 86400  # Wrap around midnight safely.

        print("Elapsed time: {} seconds".format(elapsed))
        log_file.write("{}\n".format(elapsed))  # Save each trial result for later review.
        log_file.flush()
        trial_count += 1
        wait_for_button_release()

    except KeyboardInterrupt:
      print(
          "\nProgram terminated. {} completed trials saved to {}.".format(
              trial_count, LOG_FILE
          )
      )


if __name__ == "__main__":
  run_game()
