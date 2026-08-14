i2c = board.I2C()
try:
    icm = adafruit_icm20x.ICM20948(i2c, address=0x69)
except ValueError:
    icm = adafruit_icm20x.ICM20948(i2c, address=0x68)

icm.accelerometer_range = adafruit_icm20x.AccelRange.RANGE_16G
icm.gyro_range = adafruit_icm20x.GyroRange.RANGE_500_DPS
icm.accelerometer_data_rate_divisor = 0
icm.gyro_data_rate_divisor = 0

ax, ay, az = icm.acceleration
g0 = (ax*ax + ay*ay + az*az) ** 0.5 / G
print(f"IMU ok, resting |a| = {g0:.3f} g   (want ~1.000)")
if not 0.9 < g0 < 1.1:
    print("  WARNING: not ~1 g - check config before trusting drop data.")
