# Challenge 5 — Sounds of Betelgeuse  (finale · NOT YET BUILT)

- **Category:** Forensics (image reconstruction)
- **Difficulty:** hard
- **Flag (planned):** `flag{we_are_the_signal_we_sent}`
- **Needs:** the Stage-4 decrypted hints (512 lines / 8 ms each / a circle proves timing)

> Status: **specified, not implemented.** This README is the spec so the team can
> review the plan before we build it.

## Concept

The reply's final payload is the **116th picture** — encoded the way the Record's
own 115 images were (analog scan lines). Decoding it reveals the punchline of the
whole CTF: the "alien" reply is a **mirror of us** — the final image is the
receiving dish/antenna, timestamped 2026.

## Planned delivery

The Stage-4 plaintext already says: *"WE KEPT THE 116TH PICTURE … 512 LINES, 8 MS
EACH, TOP TO BOTTOM. A CIRCLE PROVES YOUR TIMING."* Stage 5 provides the encoded
image as an audio blob (a final transmission or a file linked from Stage 4).

## Planned player path

1. From Stage 4: the image is drawn in scan lines — 512 lines, ~8 ms each,
   top-to-bottom, with a **calibration circle** first to confirm timing.
2. Reconstruct the image from the audio using those specs (or an open-source
   Golden Record image decoder).
3. A correctly-timed decode shows a circle, then the final photo → flag.

## Build plan

- Write the encoder by **inverting the Golden Record image spec**: grayscale →
  512 columns, each column = one scan line (amplitude-modulated over ~8 ms), sync
  pulse per line, calibration circle as the first frame.
- Final image: the venue's dish/antenna with the flag overlaid, timestamped 2026.
- Verify with a matching decoder (prove the circle + image reconstruct at the
  stated timing) before shipping.

## Open questions for the team

- Deliver the Stage-5 audio as a **file** (linked from Stage 4) or a **final
  on-air transmission**?
- How forgiving should the timing be? (Tighter = harder; the calibration circle
  is the safety net.)
- Do we want the flag *in* the image (OCR-able) or spelled by a visual element?
