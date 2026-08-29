# Build Checklist

| Stage | Name | Status | Flag |
|-------|------|--------|------|
| 1 | Noise Floor | ✅ built + verified | `flag{sub_ghz_still_breathes}` |
| 2 | Sounds of Earth | ✅ built + verified | `flag{through_hardship_to_the_stars}` |
| 3 | The Cover | ✅ built + verified | `flag{a_present_from_a_small_distant_world}` |
| 4 | VHF Digital | ✅ built + verified (APRS via station) | `flag{hydrogen_line_handshake}` |
| 5 | Sounds of Betelgeuse | ✅ built + verified (SSTV / Robot36) | `flag{we_are_the_signal_we_sent}` |

## Dependency chain
`S2 phrase (key)` + `S3 salt (stamp)` → `S4 decrypt` → `S4 plaintext carries S5 hints` → `S5 image`

## Recent decisions
- **S4 delivery = APRS via a dedicated station.** Players read decoded packets off
  the station display; no callsign/app needed. (ggwave and Rattlegram were
  prototyped and set aside — see challenge-04 README.)
- **S3 → S4 hint move.** The Stage-5 scan-line spec ("512 lines / 8 ms / circle")
  was removed from the Stage-3 cover and now lives in the Stage-4 decrypted reply.

- **S5 = SSTV (Robot36).** Decodable by any SSTV app, no code. Stage-4 reply
  updated to point at it ("slow-scanned...let your radio draw the lines"). A raw
  scan-line alternate exists if a harder finale is wanted.

## Global TODO
- [x] Build Stage 5 (SSTV / Robot36, verified).
- [ ] Decide "jamming" delivery: low-power dead-band recording (safer) vs. live.
- [ ] Record every transmission to WAV/IQ as remote/backup fallbacks (S1, S4 done).
- [ ] Station setup for S4: RTL-SDR + direwolf + display; optional waterfall + placard.
- [ ] Player field guide: rtl_433, a spectrogram app, CyberChef, + where the S4 station is.
- [ ] Set CTFd point values and hint ladders per challenge.
