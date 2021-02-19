"""
This file contains the main function, which will
continually read data from sensors, filter it,
update the flight state, move the servo, and 
write output.
"""

FAKE_DATA = True
fake_path = 'fake_data/Success.csv'

# Import modules
import sensors
import data_filter
import state
import controller
import servo
import scribe
from data_manager import Data_Manager

# Configuration
# active_sensors = ['IMU', 'Accelerometer', 'Altimeter']
active_sensors = ['Accelerometer', 'Altimeter']
manager = Data_Manager(active_sensors)

# Initialize modules
if FAKE_DATA:
    import sensors_spoof as sensors
    sensors.initialize_sensors(fake_path, manager)
else:
    import sensors
    sensors.initialize_sensors(manager)
data_filter.initialize_filter(manager)
state.initialize_state(manager)
scribe.initialize_file(manager)
servo.initialize_servo()
controller.initialize(manager)


def main():
    while True:
        # Attempt to execute
        #try:
        # Read data
        sensors.read_sensors(manager)

        # Filter data
        data_filter.filter_data(manager)

        # Update flight state
        curr_state = state.state_transition(manager)

        # PID
        extension = controller.step(manager)
        servo_angle = controller.get_angle(manager)

        # Servo
        servo.rotate(servo_angle)

        # Log output
        scribe.write_row(manager)

        # Handle error
        #except:
        #    print('We regret to inform you that your code has a tumor')

# Python stuff to make code more clean
if __name__ == '__main__':
    main()
    servo.clean_servo()
