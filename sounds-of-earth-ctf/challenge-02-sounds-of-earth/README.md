# Challenge 2 — Sounds of Earth

- **Category:** Audio / Morse
- **Difficulty:** easy–medium
- **Flag:** `flag{through_hardship_to_the_stars}`
- **Feeds forward:** the Morse phrase **AD ASTRA PER ASPERA** → XOR key for Stage 4 (`ADASTRAPERASPERA`)

## Description (CTFd)

> **Sounds of Earth**
> We taught the Record our music and flung it into the dark. Forty-nine years
> later something sends it back — but turn the dial now and you won't find a
> single song. Every station on the FM band carries the same thing: a voice from
> somewhere cold, drowning in static and worse. Find where it's broadcasting.
> Then listen closely — it's spelling something out in a language older than radio.
>
> `Flag format: flag{...}`

The description steers players to **FM** (the songs are gone; every station is the
same signal) and hints at Morse ("a language older than radio").

## Delivery

`dist/alien_signal.wav` — a 30 s dark, irradiated-radio drone. Play it on a
clear FM frequency (low-power transmitter) so players find it by tuning, or hand
it out as a file. Energy is kept 300 Hz–6 kHz so it survives a speaker→phone-mic
path.

## Player path

1. The audio sounds like noise/static. Open a **spectrogram** view (Spectroid /
   SpectrumView on a phone, or Audacity → Spectrogram).
2. A steady **600 Hz** line carries Morse (there's a fainter echo at 1200 Hz).
3. Decode the Morse → **AD ASTRA PER ASPERA**.
4. Translate the Latin → *"through hardship to the stars"* → flag.

The phrase itself is the Stage-4 key; the flag is its meaning.

## Files

**dist/**
- `alien_signal.wav` — the transmission (Morse buried under the bed)

**src/**
- `gen_stage2.py` — synth generator (all knobs documented at the top)
- `verify_morse.py` — bandpass/envelope decoder that recovers the Morse (proof)
- `spectrogram.png` — reference spectrogram (answer key)

## How it works

- **Bed:** brown-noise static, AM crackle, Geiger-burst clicks, drifting
  heterodyne whistles, a low dissonant drone, radiation surges, signal-fade
  dropouts, then waveshaping/bitcrush and a dark spectral tilt.
- **Morse:** 600 Hz tone at ~14 wpm, dashes stretched 1.15× ("learned, not human").
- **Readability tricks:** the bed has a real **bandstop slot** carved at 520–690 Hz,
  and a **sidechain duck** dips the bed a few dB under the Morse so radiation
  bursts can't bury a symbol. Verified to decode clean both direct and through a
  simulated mic path.

## Build / regenerate

```
cd src && python3 gen_stage2.py        # writes ../dist/alien_signal.wav
python3 verify_morse.py                 # should print AD ASTRA PER ASPERA
```

Tuning (top of `gen_stage2.py`): `DOT` (speed), morse level (`0.22`), duck depth
(`0.4`), bandstop width, and the `static` weights for more/less grit. Change the
RNG seed (`1977`) for a different arrangement of bursts/whistles.

Requires: Python 3 + numpy + scipy.
