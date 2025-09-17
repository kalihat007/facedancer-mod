#!/usr/bin/env python3
#
# facedancer-switch-flip-endpoint.py

from facedancer import FacedancerUSBApp
from facedancer.USBConfiguration import USBConfiguration
from facedancer.USBInterface import USBInterface
from facedancer.USBEndpoint import USBEndpoint
from facedancer.USBProxy import USBProxyDevice, USBProxyFilter
from facedancer.filters.standard import USBProxySetupFilters
from facedancer.filters.logging import USBProxyPrettyPrintFilter


class SwitchControllerWorkWithFacedancer21Filter(USBProxyFilter):
    """
    The Switch controller uses EP1 as an IN endpoint, and EP2 as an OUT
    endpoint. This works great with newer FaceDancer boards, but doesn't
    work with the older Facedancer21, whose MAXUSB chip only supports using
    EP1 as OUT and EP2 as IN.

    This filter rewrites the Switch's configuration descriptors to switch
    EP1 and EP2, and then reroutes all packets accordingly, so this example
    can work on the Facedancer21.
    """

    GET_DESCRIPTOR_REQUEST = 6
    DESCRIPTOR_CONFIGURATION = 0x02

    def filter_control_in(self, req, data, stalled):

        if stalled:
            return req, data, stalled

        # If this is a read of a descriptor, see if we'll have to interpose.
        if req.request == self.GET_DESCRIPTOR_REQUEST:

            # Get the descriptor type and index.
            descriptor_type  = req.value >> 8
            descriptor_index = req.value & 0xFF

            # If this is the configuration descriptor, modify the endpoint descritors
            # to switch EP1 and EP2.
            if descriptor_type == self.DESCRIPTOR_CONFIGURATION and req.length >= 32:
                configuration = USBConfiguration.from_binary_descriptor(data)

                # Swap EP2 and EP1.
                ep2, ep1 = configuration.interfaces[0].endpoints
                ep1.number = 2
                ep2.number = 1
                configuration.interfaces[0].endpoints = [ep1, ep2]

                # And replace our data with the modified descriptor.
                data = configuration.get_descriptor()

        return req, data, stalled


    def filter_in_token(self, ep_num):
        """
        Redirect IN requests on EP2 (FaceDancer) to EP1 (real device), compensating 
        for our flip.
        """
        return 1 if ep_num == 2 else ep_num


    def filter_out(self, ep_num, data):
        """
        Redirect OUT requests on EP1 (FaceDancer) to EP2 (real device), compensating
        for our flip.
        """

        if ep_num == 1:
            ep_num = 2

        return ep_num, data



class SwitchControllerInvertXFilter(USBProxyFilter):
    """
    Sample filter that inverts the X axis on a switch controller.
    Demonstrates how dead simple this is. :)
    """

    # Joystick up:   b'\x00\x00\x0f\x80\xff\x80\x80\x00'
    # Joystick down: b'\x00\x00\x0f\x80\x00\x80\x80\x00'

    def filter_in(self, ep_num, data):

        # Invert the X axis...
        try:
            data[3] = 0xff - data[3]
        except:
            pass

        return ep_num, data



def main():

    # Create a new proxy/MITM connection for the Switch Wired Pro Controller.
    u = FacedancerUSBApp(verbose=1)
    d = USBProxyDevice(u, idVendor=0x0f0d, idProduct=0x00c1, verbose=2)

    # Apply our filter before the standard filters so we impact configuration
    # of the target device.
    d.add_filter(SwitchControllerWorkWithFacedancer21Filter())

    d.add_filter(USBProxySetupFilters(d, verbose=2))

    d.add_filter(SwitchControllerInvertXFilter())
    d.add_filter(USBProxyPrettyPrintFilter(verbose=5))

    d.connect()

    try:
        d.run()
    # SIGINT raises KeyboardInterrupt
    except KeyboardInterrupt:
        d.disconnect()

if __name__ == "__main__":
    main()
