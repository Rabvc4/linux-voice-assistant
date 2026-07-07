import logging
import struct

import usb.core
import usb.util

_LOGGER = logging.getLogger(__name__)

VID = 0x2886
PID = 0x001A
TIMEOUT_MS = 100000

LED_RESID = 20
LED_EFFECT = 12
LED_BRIGHTNESS = 13
LED_SPEED = 15
LED_COLOR = 16

CTRL_OUT = usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE


class LEDController:
    def __init__(self) -> None:
        self.dev = usb.core.find(idVendor=VID, idProduct=PID)

        if self.dev is None:
            raise RuntimeError("ReSpeaker XVF3800 not found on USB")

        _LOGGER.info("ReSpeaker XVF3800 LED controller initialized")

        # Start in a known safe state.
        self.idle()

    def _write_uint8(self, cmdid: int, value: int) -> None:
        self.dev.ctrl_transfer(
            CTRL_OUT,
            0,
            cmdid,
            LED_RESID,
            int(value).to_bytes(1, byteorder="little"),
            TIMEOUT_MS,
        )

    def _write_uint32(self, cmdid: int, value: int) -> None:
        self.dev.ctrl_transfer(
            CTRL_OUT,
            0,
            cmdid,
            LED_RESID,
            struct.pack("<I", int(value)),
            TIMEOUT_MS,
        )

    def _set_effect(self, effect: int) -> None:
        self._write_uint8(LED_EFFECT, effect)

    def _set_brightness(self, brightness: int) -> None:
        self._write_uint8(LED_BRIGHTNESS, brightness)

    def _set_speed(self, speed: int) -> None:
        self._write_uint8(LED_SPEED, speed)

    def _set_color(self, color: int) -> None:
        # Color format: 0xRRGGBB
        self._write_uint32(LED_COLOR, color)

    def off(self) -> None:
        self._set_effect(0)

    def idle(self) -> None:
        self.off()

    def listening(self) -> None:
        self._set_color(0x0088FF)
        self._set_brightness(128)
        self._set_effect(3)

    def thinking(self) -> None:
        self._set_color(0xFF8800)
        self._set_brightness(180)
        self._set_speed(1)
        self._set_effect(1)

    def speaking(self) -> None:
        self._set_color(0x00FF88)
        self._set_brightness(160)
        self._set_effect(3)

    def doa(self) -> None:
        self._set_effect(4)
