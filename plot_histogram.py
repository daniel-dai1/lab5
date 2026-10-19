import matplotlib.pyplot as plt


def read_times(log_path="log.txt"):
  times = []
  try:
    with open(log_path, "r") as log_file:
      for line_number, line in enumerate(log_file, start=1):
        value = line.strip()
        if not value:
          continue
        if value.startswith("Measured_Time_Seconds:"):
          value = value.partition(":")[2].strip()
        try:
          times.append(float(value))
        except ValueError as error:
          raise ValueError(
              "Invalid time on line {} of {}".format(line_number, log_path)
          ) from error
  except FileNotFoundError:
    raise SystemExit(
        "{} not found. Make sure it is in the same directory.".format(log_path)
    )

  if not times:
    raise SystemExit("No data found in {}.".format(log_path))
  return times


def main():
  times = read_times()

  plt.figure(figsize=(8, 5))
  plt.hist(times, bins=10, edgecolor="black", alpha=0.7)
  plt.axvline(
      15.0, color="red", linestyle="dashed", linewidth=1.5, label="Target (15s)"
  )

  plt.xlabel("Time Taken to Count 15 Seconds (seconds)")
  plt.ylabel("Frequency (Number of Trials)")
  plt.title("Time Perception Accuracy Histogram")
  plt.legend()
  plt.grid(True, linestyle=":", alpha=0.6)

  plt.savefig("histogram.png", dpi=300)
  print("Histogram saved as histogram.png")
  plt.show()


if __name__ == "__main__":
  main()