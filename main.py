import time
from machine import I2C, Pin

BUTTON_PIN = 14
LOG_FILE = "log.txt"
DS3231_I2C_ADDR = 0x68

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)


def bcd_to_dec(value):
  return (value >> 4) * 10 + (value & 0x0F)


def read_rtc_seconds():
  """Return the DS3231 time as seconds since midnight."""
  data = i2c.readfrom_mem(DS3231_I2C_ADDR, 0x00, 3)
  second = bcd_to_dec(data[0] & 0x7F)
  minute = bcd_to_dec(data[1] & 0x7F)
  raw_hour = data[2]

  if raw_hour & 0x40:
    hour = bcd_to_dec(raw_hour & 0x1F)
    if hour == 12:
      hour = 0
    if raw_hour & 0x20:
      hour += 12
  else:
    hour = bcd_to_dec(raw_hour & 0x3F)

  if second > 59 or minute > 59 or hour > 23:
    raise ValueError("DS3231 returned an invalid time")

  return hour * 3600 + minute * 60 + second


def wait_for_button_press():
  """Wait for a stable press and return the RTC time when it was detected."""
  while True:
    while button.value() == 1:
      time.sleep(0.01)

    pressed_at = read_rtc_seconds()
    time.sleep(0.03)
    if button.value() == 0:
      return pressed_at


def wait_for_button_release():
  while button.value() == 0:
    time.sleep(0.01)


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
        elapsed = (end_time - start_time) % 86400

        print("Elapsed time: {} seconds".format(elapsed))
        log_file.write("{}\n".format(elapsed))
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
