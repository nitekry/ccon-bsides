#!/usr/bin/env python3
"""
Stage 1 solver / TX health monitor.

Pipe rtl_433 JSON into it. It ignores the flood of noise fragments and
prints the flag only when a CRC-valid frame arrives.

Live over the air:
  rtl_433 -f 433.92M -s 250k \
    -X 'n=voyager,m=OOK_MC_ZEROBIT,s=250,l=0,r=2000' -F json \
    | python3 solve_stage1.py

From a recorded file:
  rtl_433 -r capture.cu8 \
    -X 'n=voyager,m=OOK_MC_ZEROBIT,s=250,l=0,r=2000' -F json \
    | python3 solve_stage1.py
"""
import sys, json

SYNC = "0010110111010100"          # 0x2DD4, bit string

def crc8(data, poly=0x31, init=0x00):
    crc = init
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ poly) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc

def try_extract(hexstr):
    """Return payload string if a CRC-valid frame is found, else None."""
    try:
        bits = bin(int(hexstr, 16))[2:].zfill(len(hexstr) * 4)
    except ValueError:
        return None
    for polarity in (bits, "".join("1" if c == "0" else "0" for c in bits)):
        i = polarity.find(SYNC)
        if i < 0:
            continue
        rest = polarity[i + 16:]
        if len(rest) < 8:
            continue
        ln = int(rest[:8], 2)
        need = 8 + ln * 8 + 8          # len byte + payload + crc
        if len(rest) < need:
            continue
        payload = bytes(int(rest[8 + j*8 : 16 + j*8], 2) for j in range(ln))
        got_crc = int(rest[8 + ln*8 : 16 + ln*8], 2)
        frame = bytes([0xAA]*4) + bytes([0x2D, 0xD4, ln]) + payload
        if crc8(frame) == got_crc:
            try:
                return payload.decode()
            except UnicodeDecodeError:
                return None
    return None

def main():
    seen = 0
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        for row in d.get("rows", [{}]) or [{}]:
            hexstr = row.get("data") or d.get("data") or ""
            if not hexstr:
                continue
            seen += 1
            payload = try_extract(hexstr)
            if payload:
                print("\n[+] CRC-VALID FRAME")
                if "|" in payload:
                    flag, ptr = payload.split("|", 1)
                    print(f"    flag    : {flag}")
                    print(f"    pointer : {ptr}")
                else:
                    print(f"    payload : {payload}")
                print(f"    (rejected {seen-1} noise fragments before this)")
                return
    print(f"[-] no valid frame; checked {seen} candidates", file=sys.stderr)

if __name__ == "__main__":
    main()
