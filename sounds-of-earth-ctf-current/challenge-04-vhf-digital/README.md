# Challenge 4 — VHF Digital

- **Category:** Packet / crypto
- **Difficulty:** medium–hard
- **Flag:** `flag{hydrogen_line_handshake}`
- **Needs:** Stage-2 phrase (key) + Stage-3 salt (confirmation)
- **Feeds forward:** decrypted message carries the Stage-5 pointer (SSTV finale)

## Description (CTFd)

> **The Hydrogen Line**
> On 144.390 the carrier isn't dead — it's *locked*. Something is chirping digital
> bursts stamped with a date you've seen before. Pull the packets down, put them
> back in order, and open them with the words the Record taught you. The dark is
> trying to say hello.
>
> `Flag format: flag{...}`

## Delivery — dedicated station

Players do **not** need a callsign or their own radio. A dedicated receiver
station on site does the RX and displays the decoded packets:

- **Rig:** RTL-SDR (or 2 m radio) → `direwolf` → a screen. Tune 144.390 MHz.
- **No live RF?** Loop `dist/stage4_vhf.wav` into direwolf / `atest`, or key it
  low-power under a licensed operator.
- **Players read** the decoded TNC2 lines off the station display and copy the hex.

Optional station flavor: show a live waterfall next to the text (sells "carrier
locked"), and a placard with callsign `VGR1` + the `[1977-09-05]` stamp (the
Stage-3 tie-in).

## Player path

1. Read the 4 packets off the station:
   ```
   VGR1>EARTH:[1977-09-05] 1/4 <hex>
   VGR1>EARTH:[1977-09-05] 2/4 <hex>
   VGR1>EARTH:[1977-09-05] 3/4 <hex>
   VGR1>EARTH:[1977-09-05] 4/4 <hex>
   ```
2. Concatenate the hex chunks in order (1→4).
3. **CyberChef:** `From Hex` → `XOR` with key type **UTF8 = `ADASTRAPERASPERA`**
   (the Stage-2 Morse phrase, uppercase, spaces removed).
4. Read the reply → flag + Stage-5 instructions.

Decrypted message:
> HELLO FROM THE CHILDREN OF THE OUTER DARK. WE PLAYED YOUR RECORD AND LEARNED TO
> DRAW WITH SOUND. WE KEPT THE 116TH PICTURE AND SLOW-SCANNED IT BACK TO YOU. LET
> YOUR RADIO DRAW THE LINES. `flag{hydrogen_line_handshake}`

## Files

**dist/**
- `stage4_vhf.wav` — the AFSK1200 (APRS/AX.25) audio; loop into the station

**src/**
- `gen_stage4.py` — composes the reply, XOR-encrypts, writes the packet list
- `packets.txt` — TNC2 lines for `direwolf gen_packets` (answer key)
- `plaintext.txt` — the decrypted reply (answer key)

## How it works

- **Crypto:** repeating-key **XOR**, key = `ADASTRAPERASPERA` (from Stage 2),
  emitted as hex. Trivial in CyberChef (`From Hex` → `XOR`).
- **Salt:** the Stage-3 date `1977-09-05` is stamped on every packet as
  confirmation the player has the right transmission/key (it is a label, not part
  of the key). If you'd rather make it cryptographically required, fold it into
  the key (`ADASTRAPERASPERA19770905`) — one-line change.
- **Packets:** four 1200-baud AFSK AX.25 UI frames, `VGR1>EARTH`, generated with
  `direwolf gen_packets`, verified to demodulate with `atest`.

## Build / regenerate

```
cd src
python3 gen_stage4.py                       # writes packets.txt + plaintext.txt
gen_packets -o ../dist/stage4_vhf.wav packets.txt
atest ../dist/stage4_vhf.wav                # should show 4 decoded VGR1 packets
```

Requires: Python 3, `direwolf` (`gen_packets`, `atest`).

## Design history (for reviewers)

We prototyped two alternatives before landing on station-fed APRS:
- **ggwave** (data-over-sound, phone app *Waver*, no license) — verified working,
  but capacity is 140 bytes/message so the reply had to be trimmed.
- **Rattlegram** — nice radio aesthetic, but the reference encoder's wire format
  didn't match the released app and couldn't be verified against a phone here.

The dedicated station removes the license/app friction that made us look at those,
so APRS (which looks great on a station dashboard) is the canonical build.
