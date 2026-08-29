#!/usr/bin/env python3
"""
Stage 1 -- "Noise Floor"
Generates an OOK (on-off keyed) burst carrying the flag + pointer text,
embedded in broadband noise.

Outputs:
  stage1_hackrf.cs8            -- signed 8-bit IQ for `hackrf_transfer`
  stage1_test_433.92M_2000k.cu8 -- unsigned 8-bit IQ for `rtl_433 -r` testing

Transmit with:
  hackrf_transfer -t stage1_hackrf.cs8 -f 433820000 -s 2000000 -x 20 -R
  (Tune 433.82 MHz so the +100 kHz baseband offset lands on 433.92 MHz)

Player-side decode:
  rtl_433 -A                       (live, analyze mode)
  rtl_433 -A -r stage1_test_433.92M_2000k.cu8   (from file)
"""

import numpy as np

# ---------------- parameters ----------------
FS          = 2_000_000        # sample rate (Hz) - matches hackrf_transfer -s
F_OFFSET    = 100_000          # carrier offset from center (avoid DC spike)
BIT_RATE    = 2_000            # bits/sec (500 us symbols - comfortable for rtl_433)
NOISE_SNR_DB = 40             # essentially clean packet; jamming lives on OTHER bands
REPEATS     = 12              # more repeats so a full frame is easy to catch
GAP_S       = 0.8            # longer quiet gap -> rtl_433 won't merge burst halves

PAYLOAD = b"flag{sub_ghz_still_breathes}|RECORD:16.667RPM"

# ---------------- packet build ----------------
def bytes_to_bits(data: bytes):
    return [(byte >> (7 - i)) & 1 for byte in data for i in range(8)]

def crc8(data: bytes, poly=0x31, init=0x00):
    crc = init
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ poly) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc

def manchester(bits):
    """G.E. Thomas convention (matches rtl_433 OOK_MC_ZEROBIT): 0 -> 01, 1 -> 10"""
    out = []
    for b in bits:
        out += [1, 0] if b else [0, 1]
    return out

# preamble: 4 bytes of 0xAA (nice 1010... for clock recovery, pre-Manchester)
# sync word 0x2DD4 (common in sub-GHz land, players may recognize it)
frame = bytes([0xAA] * 4) + bytes([0x2D, 0xD4]) + bytes([len(PAYLOAD)]) + PAYLOAD
frame += bytes([crc8(frame)])
chips = manchester(bytes_to_bits(frame))     # 2 chips per bit

# ---------------- waveform ----------------
sps = int(FS / (BIT_RATE * 2))               # samples per chip (Manchester doubles rate)
ook = np.repeat(np.array(chips, dtype=np.float32), sps)

# soften keying edges to limit spectral splatter (simple 5-sample ramp)
ramp = np.ones(5, dtype=np.float32) / 5
ook = np.convolve(ook, ramp, mode="same")

t = np.arange(len(ook)) / FS
burst = ook * np.exp(2j * np.pi * F_OFFSET * t).astype(np.complex64)

gap = np.zeros(int(GAP_S * FS), dtype=np.complex64)
sig = np.concatenate([np.concatenate([burst, gap]) for _ in range(REPEATS)])

# broadband noise floor across the whole capture
noise_amp = 10 ** (-NOISE_SNR_DB / 20)
noise = (np.random.randn(len(sig)) + 1j * np.random.randn(len(sig))).astype(np.complex64)
sig = sig + noise * noise_amp * 0.7071

# normalize to ~70% full scale
sig /= np.max(np.abs(sig)) * 1.4

# ---------------- file output ----------------
def write_cs8(path, iq):
    inter = np.empty(2 * len(iq), dtype=np.int8)
    inter[0::2] = np.clip(iq.real * 127, -127, 127).astype(np.int8)
    inter[1::2] = np.clip(iq.imag * 127, -127, 127).astype(np.int8)
    inter.tofile(path)

def write_cu8(path, iq):
    inter = np.empty(2 * len(iq), dtype=np.uint8)
    inter[0::2] = np.clip(iq.real * 127 + 127.5, 0, 255).astype(np.uint8)
    inter[1::2] = np.clip(iq.imag * 127 + 127.5, 0, 255).astype(np.uint8)
    inter.tofile(path)

write_cs8("stage1_hackrf.cs8", sig)
write_cu8("stage1_test_433.92M_2000k.cu8", sig)

dur = len(sig) / FS
print(f"frame: {len(frame)} bytes, {len(chips)} chips, burst {len(burst)/FS*1000:.0f} ms")
print(f"file:  {dur:.1f} s total, {REPEATS} repeats")
print(f"crc8:  0x{frame[-1]:02X}")
