#!/usr/bin/env python3
#
# Simplest possible example of using the FaceDancer host API.

import sys
import time

from facedancer import FacedancerUSBHostApp

# Enumerate and configure the attached device.
u = FacedancerUSBHostApp(verbose=3)

# Give the user a clear message (with a timeout) if no downstream device is present.
WAIT_TIMEOUT_SECONDS = 10
CHECK_INTERVAL_SECONDS = 0.5

if not u.device_is_connected():
    print(f"Waiting up to {WAIT_TIMEOUT_SECONDS}s for a downstream USB device...")
    start_time = time.time()
    print("\tPort power:", "On" if u.port_is_powered() else "Off")
    print("\tInitial line state:", u.current_line_state(as_string=True))

    while not u.device_is_connected():
        if time.time() - start_time > WAIT_TIMEOUT_SECONDS:
            print("Timed out waiting for a device. Ensure your target is connected to the GreatFET host port.")
            print("\tLast seen line state:", u.current_line_state(as_string=True))
            sys.exit(1)

        # Issue a reset to encourage newly-connected devices to enumerate.
        u.bus_reset()
        time.sleep(CHECK_INTERVAL_SECONDS)

u.initialize_device(assign_address=1, apply_configuration=1)

# At this point, we can perform whatever communications we need to to use the target device.
# Usually, this is accomplished using the send_on_endpoint and read_from_endpoint functions
# for non-control requests, and the control_request_in and control_request out functions
# for control requests.

# Print the device state.
print("Device initialized: ")
print("\tDevice is: {}".format("Connected" if u.device_is_connected() else "Disconnected"))
print("\tDevice speed: {}".format(u.current_device_speed(as_string=True)))
print("\tPort is: {}".format("Enabled" if u.port_is_enabled() else "Disabled"))
print("\tPort power is: {}".format("On" if (u.port_is_powered()) else "Off"))
print("\tLine state: {}".format(u.current_line_state(as_string=True)))

# Print information about the attached device...
print("Attached device: {}".format(u.get_device_descriptor()))

# .. and its configuration.
configuration = u.get_configuration_descriptor()
print("Using first configuration: {}".format(configuration))

for interface in configuration.interfaces:
    print("\t - {}".format(interface))

    for endpoint in interface.endpoints:
        print("\t\t - {}".format(endpoint))
