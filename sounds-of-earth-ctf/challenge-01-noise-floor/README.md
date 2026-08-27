# Challenge 1 — Noise Floor

- **Category:** RF / SDR
- **Difficulty:** easy (entry stage)
- **Flag:** `flag{sub_ghz_still_breathes}`
- **Feeds forward:** pointer `RECORD:16.667RPM` → tells players to listen to the Record (Stage 2)

## Description (CTFd)

> **Noise Floor**
> The airwaves are poisoned — turn any dial and you get a wall of hiss. But the
> jamming never reached all the way down. Somewhere in the sub-GHz band, one
> honest channel is still breathing. Point your dish, load the receiver card,
> and read what's coming through.
>
> `Flag format: flag{...}`

Hand players the **poster** (`dist/signal_problems_poster.html`) — it carries the
frequency-chart clue (433.92 MHz is the one "SIGNAL READABLE" row) and the exact
config usage.

## Delivery

An OOK / Manchester burst transmitted at **433.92 MHz** from a HackRF:

```
hackrf_transfer -t src/stage1_hackrf.cs8 -f 433820000 -s 2000000 -x 30 -R
```

(The signal sits at a +100 kHz baseband offset, so tuning the HackRF to
433.82 MHz lands it on 433.92 MHz, clear of the DC spike. `-R` loops forever.)

For a hardware-free run, hand players `dist/stage1_test_433.92M_2000k.cu8` and let
them decode it with `-r`.

## Player path

1. Poster says: tune 433.92 MHz, sample rate 250k, use `voyager.conf`.
2. Run one command:
   ```
   rtl_433 -c voyager.conf
   ```
   (or against the capture: `rtl_433 -c voyager.conf -r stage1_test_433.92M_2000k.cu8`)
3. Copy the hex from the `data` field into **CyberChef → From Hex**.
4. Read: `flag{sub_ghz_still_breathes}|RECORD:16.667RPM`.

## Files

**dist/ (player-facing)**
- `voyager.conf` — one-command rtl_433 decoder config (freq + rate + flex decoder)
- `signal_problems_poster.html` — in-universe ad poster (clue + instructions)
- `stage1_test_433.92M_2000k.cu8` — recorded capture (hardware-free fallback)

**src/ (author)**
- `gen_stage1.py` — generates the frame + both IQ files (edit payload/noise here)
- `stage1_hackrf.cs8` — transmit file for `hackrf_transfer`
- `solve_stage1.py` — CRC-gated reference solver (pipe `rtl_433 ... -F json` into it)

## How it works

A custom Manchester/OOK frame: `AA×4` preamble, `0x2DD4` sync, length byte,
ASCII payload, CRC-8. The `voyager.conf` flex decoder aligns on the sync word
(`preamble=2dd42d`) and prints the payload as hex. The CRC byte happens to land
on `$` (0x24), so `From Hex` yields a clean readable string.

Design note: the packet is transmitted **clean** (noise floor comes from the room
and the story's "jamming" lives on *other* bands). At low SNR the flex decoder can
emit junk lines, but the real one is always the `len:368` line starting `666c61…`
(`flag{`). `solve_stage1.py` is a CRC-gated solver if you want zero false positives.

## Build / regenerate

```
cd src && python3 gen_stage1.py
# writes stage1_hackrf.cs8 (transmit) + stage1_test_*.cu8 (test/fallback)
```

Requires: `rtl_433` (v22+), Python 3 + numpy. Verify with:
```
rtl_433 -c ../dist/voyager.conf -r ../dist/stage1_test_433.92M_2000k.cu8
```
