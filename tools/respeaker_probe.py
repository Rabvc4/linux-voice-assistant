#!/usr/bin/env python3

import sys

try:
    import usb.core
    import usb.util
except ImportError:
    print("ERROR: PyUSB is not installed.")
    print("Try: apt update && apt install -y python3-usb")
    sys.exit(1)


VID = 0x2886
PID = 0x001A


def safe_get_string(dev, index):
    if not index:
        return None

    try:
        return usb.util.get_string(dev, index)
    except Exception as err:
        return f"<unreadable: {err}>"


def interface_class_name(class_code):
    return {
        0x01: "Audio",
        0x03: "HID",
        0xFE: "Application Specific",
        0xFF: "Vendor Specific",
    }.get(class_code, f"Unknown ({class_code:#04x})")


def main():
    print("Searching for ReSpeaker XVF3800...")
    dev = usb.core.find(idVendor=VID, idProduct=PID)

    if dev is None:
        print(f"NOT FOUND: {VID:04x}:{PID:04x}")
        sys.exit(2)

    print("FOUND")
    print(f"USB ID: {dev.idVendor:04x}:{dev.idProduct:04x}")
    print(f"Bus: {dev.bus}")
    print(f"Address: {dev.address}")
    print(f"Manufacturer: {safe_get_string(dev, dev.iManufacturer)}")
    print(f"Product: {safe_get_string(dev, dev.iProduct)}")
    print(f"Serial: {safe_get_string(dev, dev.iSerialNumber)}")
    print(f"Configurations: {dev.bNumConfigurations}")
    print()

    vendor_interfaces = []
    hid_interfaces = []

    for cfg in dev:
        print(f"Configuration {cfg.bConfigurationValue}")
        print(f"  Interfaces: {cfg.bNumInterfaces}")

        for intf in cfg:
            class_name = interface_class_name(intf.bInterfaceClass)

            print()
            print(f"  Interface {intf.bInterfaceNumber}")
            print(f"    Alt setting: {intf.bAlternateSetting}")
            print(f"    Class: {intf.bInterfaceClass:#04x} ({class_name})")
            print(f"    Subclass: {intf.bInterfaceSubClass:#04x}")
            print(f"    Protocol: {intf.bInterfaceProtocol:#04x}")
            print(f"    Endpoints: {intf.bNumEndpoints}")

            if intf.bInterfaceClass == 0xFF:
                vendor_interfaces.append(intf.bInterfaceNumber)

            if intf.bInterfaceClass == 0x03:
                hid_interfaces.append(intf.bInterfaceNumber)

            for ep in intf:
                direction = "IN" if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN else "OUT"
                transfer_type = usb.util.endpoint_type(ep.bmAttributes)

                print(f"      Endpoint: {ep.bEndpointAddress:#04x} {direction}")
                print(f"        Max packet size: {ep.wMaxPacketSize}")
                print(f"        Transfer type: {transfer_type}")

    print()
    print("Summary:")
    print(f"  Vendor-specific interfaces: {vendor_interfaces or 'none'}")
    print(f"  HID interfaces: {hid_interfaces or 'none'}")

    if vendor_interfaces:
        print()
        print("Recommendation:")
        print("  Use PyUSB/vendor control path for ReSpeaker control commands.")
        print("  Do not integrate with satellite.py until a standalone LED command test works.")

    if hid_interfaces:
        print()
        print("Note:")
        print("  HID exists, but that does not prove LED control uses HID.")
        print("  For this device, the vendor-specific interface is still the safer control target.")


if __name__ == "__main__":
    main()
