# Re: Sounds of Earth — CTF

A five-stage radio/audio/crypto CTF built around the Voyager Golden Record.
Players chase a reply signal down through poisoned airwaves, decoding sound,
images, Morse, and packets — each stage handing forward a key the next one needs.

> ⚠️ **This repo contains spoilers.** Every challenge folder has a `src/` with
> generators, answer keys, and full solutions, and this README lists all flags.
> It is for the **build/review team only** — do not hand it to players. Players
> get the files in each challenge's `dist/` folder plus the CTFd description.

---

## Story

August 2026. Forty-nine years after Voyager 1 left Earth, the Deep Space
Network hears a reply on 1420 MHz — the hydrogen line etched on the Record's
own cover. The header reads **`Re: Sounds of Earth / From: Sounds of Betelgeuse`**.

Whatever answered listened to the Record and learned from it — and it assumes
we still remember what we sent. The key to the reply is on the Record itself.
The signal has also poisoned the airwaves: FM, aircraft, and VHF are walls of
noise. Only sub-GHz still breathes.

## The stage chain

Each stage produces something the next stage consumes:

```
 S1 Noise Floor ──► pointer: "listen to the Record"
 S2 Sounds of Earth ──► phrase AD ASTRA PER ASPERA  ─────────────┐ (key)
 S3 The Cover ──► salt 1977-09-05  ──────────────────────────────┤ (stamp)
 S4 VHF Digital ── decrypt with key+salt ──► flag + Stage-5 hints ┘
 S5 Sounds of Betelgeuse ──► the 116th picture: the reply is a mirror
```

## Challenges & flags

| # | Name | Category | Delivery | Flag |
|---|------|----------|----------|------|
| 1 | Noise Floor | RF / SDR | 433.92 MHz OOK (HackRF) | `flag{sub_ghz_still_breathes}` |
| 2 | Sounds of Earth | Audio / Morse | FM audio / file | `flag{through_hardship_to_the_stars}` |
| 3 | The Cover | Stego / spectrogram | audio file | `flag{a_present_from_a_small_distant_world}` |
| 4 | VHF Digital | Packet / crypto | 144.39 MHz APRS via station | `flag{hydrogen_line_handshake}` |
| 5 | Sounds of Betelgeuse | Forensics (finale) | *planned* | `flag{we_are_the_signal_we_sent}` |

Stages 1–4 are built and verified. Stage 5 is specified but not yet built —
see its README.

## Repo layout

```
sounds-of-earth-ctf/
├── README.md            <- you are here
├── CHECKLIST.md         <- build status + global TODO
└── challenge-0X-name/
    ├── README.md        <- description, solution, flag, build notes
    ├── dist/            <- PLAYER-FACING files only
    └── src/             <- generators, answer keys, solutions (spoilers)
```

## Tooling (host side)

Most stages are built/verified with Python 3 + `numpy`/`scipy`/`matplotlib`/`Pillow`.
Per-stage extras:

- **S1:** `rtl_433`, `hackrf` tools (HackRF transmit), an RTL-SDR to test.
- **S2/S3:** just Python for build; players use a phone spectrogram app.
- **S4:** `direwolf` (`gen_packets`, `atest`) to make/verify the AFSK audio.

Player-side tools are listed in each challenge README (rtl_433, CyberChef,
a spectrogram app, and the station display for S4).

## ⚠️ RF & safety notes

- Transmitting on 433 MHz ISM (S1) and 2 m / 144.39 MHz (S4) has legal limits.
  Keep power low, use a shielded/controlled space, and key 2 m only under a
  licensed operator. Every stage ships a **recorded file** so the whole CTF can
  run with zero live RF if needed.
- Do **not** actually jam FM/aviation bands to create the "poisoned airwaves"
  effect. Use a canned "dead-band" recording or a low-power source into a dummy
  load / shielded enclosure.

## Regenerating artifacts

Every challenge's `src/gen_*.py` rebuilds its files deterministically (fixed RNG
seeds where relevant). See each README's "Build / regenerate" section.
