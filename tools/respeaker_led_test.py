#!/usr/bin/env python3

import argparse
import struct
import sys
import time

import usb.core
import usb.util


VID = 0x2886
PID = 0x001A
TIMEOUT_MS = 100000

# Official XVF3800 command IDs
LED_RESID = 20
LED_EFFECT = 12
LED_BRIGHTNESS = 13
LED_SPEED = 15
LED_COLOR = 16

CTRL_OUT = usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE


def find_device():
    dev = usb.core.find(idVendor=VID, idProduct=PID)

    if dev is None:
        raise RuntimeError("ReSpeaker XVF3800 not found")

    return dev


def write_uint8(dev, cmdid: int, value: int):
    payload = int(value).to_bytes(1, byteorder="little")

    dev.ctrl_transfer(
        CTRL_OUT,
        0,
        cmdid,
        LED_RESID,
        payload,
        TIMEOUT_MS,
    )


def write_uint32(dev, cmdid: int, value: int):
    payload = struct.pack("<I", int(value))

    dev.ctrl_transfer(
        CTRL_OUT,
        0,
        cmdid,
        LED_RESID,
        payload,
        TIMEOUT_MS,
    )


def set_effect(dev, effect: int):
    # 0=off, 1=breath, 2=rainbow, 3=single color, 4=DoA, 5=ring
    write_uint8(dev, LED_EFFECT, effect)


def set_brightness(dev, brightness: int):
    write_uint8(dev, LED_BRIGHTNESS, brightness)


def set_speed(dev, speed: int):
    write_uint8(dev, LED_SPEED, speed)


def set_color(dev, color: int):
    # Color format is 0xRRGGBB
    write_uint32(dev, LED_COLOR, color)


def main():
    parser = argparse.ArgumentParser(description="Test ReSpeaker XVF3800 LED control")
    parser.add_argument(
        "mode",
        choices=["off", "breath", "rainbow", "solid", "doa"],
        help="LED mode to test",
    )
    parser.add_argument("--color", default="0x0088ff", help="RGB color as 0xRRGGBB")
    parser.add_argument("--brightness", type=int, default=128)
    parser.add_argument("--speed", type=int, default=1)

    args = parser.parse_args()

    dev = find_device()

    color = int(args.color, 0)

    print(f"Found ReSpeaker XVF3800: {dev}")
    print(f"Setting mode: {args.mode}")

    if args.mode == "off":
        set_effect(dev, 0)

    elif args.mode == "breath":
        set_color(dev, color)
        set_speed(dev, args.speed)
        set_brightness(dev, args.brightness)
        set_effect(dev, 1)

    elif args.mode == "rainbow":
        set_speed(dev, args.speed)
        set_brightness(dev, args.brightness)
        set_effect(dev, 2)

    elif args.mode == "solid":
        set_color(dev, color)
        set_effect(dev, 3)

    elif args.mode == "doa":
        set_effect(dev, 4)

    print("Command sent.")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)
