#!/usr/bin/env python3
"""Decode a GMW3110 §9 DTC from a 4-byte (or longer) GMLAN frame payload.

Algorithm transcribed from mattiasclaesson/Trionic's
TrionicCANLib/Trionic8.cs:GetDtcDescription (lines 4635-4678).

A DTC frame on the GMLAN single-frame reply address ($054X / $05E8)
looks like:

    81 D1 D2 D3 STATUS [00 00 00]

Where:
    D1: byte 1 — letter + first 3 digits packed
    D2: byte 2 — last 2 digits (hex nibbles)
    D3: byte 3 — failure-type sub-byte (sometimes 00 for older ECMs)
    STATUS: GMW3110 §9.3 status bitfield

DTC text encoding (per Trionic):
    letter      = (D1 >> 6) & 0x03  → 0=P, 1=C, 2=B, 3=U
    digit_2     = (D1 >> 4) & 0x03  → 0-3 decimal
    digit_3     = D1 & 0x0F         → 0-F hex
    digit_4     = (D2 >> 4) & 0x0F  → 0-F hex
    digit_5     = D2 & 0x0F         → 0-F hex
    sub_type    = D3                → printed as 2-digit hex suffix

Status bits (per Trionic comments, line 4669-4676):
    bit 7  warningIndicatorRequestedState   (MIL request)
    bit 6  currentDTCSincePowerUp
    bit 5  testNotPassedSinceCurrentPowerUp
    bit 4  historyDTC                       (stored in EEPROM)
    bit 3  testFailedSinceDTCCleared
    bit 2  testNotPassedSinceDTCCleared
    bit 1  currentDTC                       (active right now)
    bit 0  DTCSupportedByCalibration

Usage:
    python3 decode_gmw3110_dtc.py "B8 32 45 13"
    python3 decode_gmw3110_dtc.py --hex B83245
    cat dtc_list.txt | python3 decode_gmw3110_dtc.py --stdin
"""
from __future__ import annotations

import argparse
import sys
from typing import NamedTuple

LETTERS = "PCBU"

STATUS_BITS = [
    (0x80, "warningIndicatorRequestedState"),
    (0x40, "currentDTCSincePowerUp"),
    (0x20, "testNotPassedSinceCurrentPowerUp"),
    (0x10, "historyDTC"),
    (0x08, "testFailedSinceDTCCleared"),
    (0x04, "testNotPassedSinceDTCCleared"),
    (0x02, "currentDTC"),
    (0x01, "DTCSupportedByCalibration"),
]


class DTC(NamedTuple):
    code: str           # e.g. "P0420-00"
    status: int         # raw status byte
    status_flags: list[str]


def decode(d1: int, d2: int, d3: int, status: int = 0) -> DTC:
    letter = LETTERS[(d1 >> 6) & 0x03]
    digit_2 = (d1 >> 4) & 0x03
    digit_3 = d1 & 0x0F
    digit_4 = (d2 >> 4) & 0x0F
    digit_5 = d2 & 0x0F
    code = f"{letter}{digit_2}{digit_3:X}{digit_4:X}{digit_5:X}-{d3:02X}"
    flags = [name for bit, name in STATUS_BITS if status & bit]
    return DTC(code=code, status=status, status_flags=flags)


def parse_hex_input(s: str) -> list[int]:
    """Accept either '04 20 00 25' or '04200025'."""
    s = s.strip().replace(",", " ")
    if " " in s:
        return [int(x, 16) for x in s.split() if x]
    return [int(s[i:i + 2], 16) for i in range(0, len(s), 2)]


def decode_one(hex_str: str) -> str:
    bytes_ = parse_hex_input(hex_str)
    if len(bytes_) < 3:
        return f"{hex_str}: too short (need at least 3 bytes)"
    d1, d2, d3 = bytes_[0], bytes_[1], bytes_[2]
    status = bytes_[3] if len(bytes_) >= 4 else 0
    dtc = decode(d1, d2, d3, status)
    flags_str = " | ".join(dtc.status_flags) if dtc.status_flags else "(none)"
    return f"{hex_str:>16}  →  {dtc.code:<10}  status=0x{dtc.status:02X}  {flags_str}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dtc", nargs="?", help="DTC bytes, e.g. 'B8 32 45 13'")
    ap.add_argument("--stdin", action="store_true",
                    help="Read DTC bytes from stdin, one per line")
    args = ap.parse_args()

    if args.stdin:
        for line in sys.stdin:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            print(decode_one(line))
    elif args.dtc:
        print(decode_one(args.dtc))
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
