"""
This file contains all of the code used to read
data from sensors.

Sensors Used:
ADXL345 - Accelerometer
MPL3115A2 - Altimeter
MPU9250/6500 - IMU
"""

# Import libraries
import time
import board
import busio
import adafruit_adxl34x
import adafruit_mpl3115a2
import FaBo9Axis_MPU9250
import logging
import data_manager
from data_manager import Data_Manager

# Parameters
ALTITUDE_STEPS = 100

# Global variables
i2c = busio.I2C(board.SCL, board.SDA)

accelerometer = None
altimeter = None
imu = None



# Initialization functions
def initialize_accelerometer(manager: Data_Manager) -> bool:
    """
    Author: Nick Crnkovich
    This function initializes the accelerometer.
    Input: None
    Output: boolean, True if initialized correctly,
    false if initialized incorrectly
    """
    logging.info("Initializing accelerometer")
    global accelerometer
    
    accelerometer = adafruit_adxl34x.ADXL345(i2c)
    accelerometer.range = adafruit_adxl34x.Range.RANGE_16_G
    accelerometer.data_rate = adafruit_adxl34x.DataRate.RATE_100_HZ

    manager.add_data(data_manager.Tuple_Data('adxl_acceleration'))

    return True

def initialize_altimeter(manager: Data_Manager) -> bool:
    """
    Author:
    This function initializes the altimeter.
    Input: None
    Output: boolean, True if initialized correctly,
    false if initialized incorrectly
    """
    logging.info("Initializing altimeter")
    global altimeter

    altimeter = adafruit_mpl3115a2.MPL3115A2(i2c)
    altimeter._ctrl_reg1 = adafruit_mpl3115a2._MPL3115A2_CTRL_REG1_OS1 | adafruit_mpl3115a2._MPL3115A2_CTRL_REG1_ALT

    pressure_sum = 0
    for _ in range(ALTITUDE_STEPS):
        pressure_sum += altimeter.pressure
    altimeter.sealevel_pressure = int(pressure_sum / ALTITUDE_STEPS)

    manager.add_data(data_manager.Scalar_Data('mpl_altitude'))
    
    return True

def initialize_imu(manager: Data_Manager) -> bool:
    """
    Author:
    This function initializes the IMU.
    Input: None
    Output: boolean, True if initialized correctly,
    false if initialized incorrectly
    """
    logging.info("Initializing IMU")
    global imu

    imu = FaBo9Axis_MPU9250.MPU9250()
    imu.configMPU9250(FaBo9Axis_MPU9250.GFS_2000, FaBo9Axis_MPU9250.AFS_16G)

    manager.add_data(data_manager.Tuple_Data('mpu_acceleration'))
    manager.add_data(data_manager.Tuple_Data('mpu_gyroscope'))
    manager.add_data(data_manager.Tuple_Data('mpu_magnetometer'))

    return True

def initialize_timer(manager: Data_Manager) -> bool:
    """
    Initializes time data
    """
    logging.info("Initializing timer...")
    manager.add_data(data_manager.Scalar_Data('time'))

    return True

def initialize_sensors(manager: Data_Manager) -> bool:
    """
    This function initializes all the sensors
    Note: call other functions in the design
    """
    logging.info("Initializing sensors...")

    # Initialize active sensors
    result = initialize_timer(manager)
    for sensor in manager.active_sensors:
        if sensor == 'IMU':
            result = result and initialize_imu(manager)
        elif sensor == 'Accelerometer':
            result = result and initialize_accelerometer(manager)
        elif sensor == 'Altimeter':
            result = result and initialize_altimeter(manager)

    return result


# Reading Functions
def read_accelerometer(manager: Data_Manager):
    """
    Author:
    This function reads values from the accelerometer
    Input: None
    Output: Ordered tuple containing the x, y, and z
    acceleration
    """
    try:
        acceleration = accelerometer.acceleration
    except:
        acceleration = [0,0,0]
    manager.update_field('adxl_acceleration', acceleration)

def read_altimeter(manager: Data_Manager):
    """
    Author:
    This function reads values from the altimeter
    Input: None
    Output: Current height of the rocket
    """
    try:
        altitude = altimeter.altitude
    except:
        altitude = 0
    manager.update_field('mpl_altitude', altitude)

def read_imu(manager: Data_Manager):
    """
    Author:
    This function reads values from the IMU
    Input: None
    Output: Dict containing any relevant sensor
    output from the IMU (minimum orientation and 
    acceleration)
    """
    try:
        accel = imu.readAccel()
    except:
        accel = (0,0,0)
    try:
        magnet_val = imu.readGyro()
    except:
        magnet_val = (0,0,0)
    try:
        gyro_val = imu.readMagnet()
    except:
        gyro_val = (0,0,0)

    manager.update_dict_field('mpu_acceleration', accel)
    manager.update_dict_field('mpu_magnetometer', magnet_val)
    manager.update_dict_field('mpu_gyroscope', gyro_val)

def read_time(manager: Data_Manager):
    """
    Returns the current time
    """
    current_time = time.time()
    manager.update_field('time', current_time)


def read_sensors(manager: Data_Manager):
    """
    Author:
    This function reads relevant values from every
    sensor.
    """

    read_time(manager)
    for sensor in manager.active_sensors:
        if sensor == 'IMU':
            read_imu(manager)
        elif sensor == 'Accelerometer':
            read_accelerometer(manager)
        elif sensor == 'Altimeter':
            read_altimeter(manager)