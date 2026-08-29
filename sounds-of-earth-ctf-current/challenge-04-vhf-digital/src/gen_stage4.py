#!/usr/bin/env python3
"""
Stage 4 — "VHF Digital"  (encryption + packet layout)

Key   : the Stage-2 Morse phrase, spaces removed, lowercased -> 'adastraperaspera'
Salt  : the Stage-3 launch date 1977-09-05, stamped on each packet as confirmation
Cipher: repeating-key XOR, emitted as hex (trivial in CyberChef: From Hex -> XOR)

Writes:
  packets.txt      -- TNC2 lines for `direwolf gen_packets`
  plaintext.txt    -- the answer-key reply (keep private)
"""

KEY = "ADASTRAPERASPERA"   # from Stage 2 Morse (uppercase, spaces removed)
SALT = "1977-09-05"               # from Stage 3  (Voyager 1 launch)

PLAINTEXT = (
    "HELLO FROM THE CHILDREN OF THE OUTER DARK. "
    "WE PLAYED YOUR RECORD AND LEARNED TO DRAW WITH SOUND. "
    "WE KEPT THE 116TH PICTURE AND SLOW-SCANNED IT BACK TO YOU. "
    "LET YOUR RADIO DRAW THE LINES. flag{hydrogen_line_handshake}"
)

def xor_hex(text, key):
    kb = key.encode()
    return "".join("%02x" % (b ^ kb[i % len(kb)])
                   for i, b in enumerate(text.encode()))

def chunk(s, n):
    return [s[i:i+n] for i in range(0, len(s), n)]

def main():
    ct = xor_hex(PLAINTEXT, KEY)
    parts = chunk(ct, 120)                     # keep each packet comfortably short
    total = len(parts)

    lines = []
    for i, part in enumerate(parts, 1):
        # TNC2 monitor format: SRC>DEST:info
        # salt stamp + sequence + ciphertext chunk
        info = f":EARTH    :[{SALT}] {i}/{total} {part}"
        lines.append(f"VGR1>EARTH::{info}")

    # simpler, clean APRS-ish message lines (no addressee padding quirks)
    lines = [f"VGR1>EARTH:[{SALT}] {i}/{total} {part}"
             for i, part in enumerate(parts, 1)]

    with open("packets.txt", "w") as f:
        f.write("\n".join(lines) + "\n")
    with open("plaintext.txt", "w") as f:
        f.write(PLAINTEXT + "\n")

    print(f"plaintext : {len(PLAINTEXT)} chars")
    print(f"ciphertext: {len(ct)} hex chars -> {total} packets")
    print(f"key       : {KEY}")
    print("packets.txt written:")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
