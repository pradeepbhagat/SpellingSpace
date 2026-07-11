"""
Pre-generate natural neural-voice audio clips for Spelling Space.

Uses Microsoft Edge neural voices (free, no API key) via edge-tts so every
device plays the same warm, human-sounding voice - no reliance on the tablet's
robotic built-in voice. Re-run any time to refresh the clips.

    python generate_audio.py
"""
import asyncio
import os
import edge_tts

VOICE = "en-US-JennyNeural"   # warm, clear American voice
OUT = os.path.join(os.path.dirname(__file__), "audio")

# Letter NAMES (spelled phonetically so the neural voice says the letter name,
# e.g. "bee" for b) - matches how letters are said in school dictation.
LETTER_NAMES = {
    "a": "ay", "b": "bee", "c": "see", "d": "dee", "e": "ee", "f": "eff",
    "g": "gee", "h": "aitch", "i": "eye", "j": "jay", "k": "kay", "l": "el",
    "m": "em", "n": "en", "o": "oh", "p": "pee", "q": "cue", "r": "ar",
    "s": "ess", "t": "tee", "u": "you", "v": "vee", "w": "double you",
    "x": "ex", "y": "why", "z": "zee",
}

# Class words already covered (kept in sync with CLASS_WORDS in index.html).
WORDS = [
    "and", "good", "this", "very", "class", "fire", "field", "trip", "with",
    "monkey", "right", "next", "said", "them", "there", "tried", "snacks",
    "table", "today", "yellow",
    # extra common early words so more parent-added words are covered
    "cat", "dog", "sun", "run", "big", "the", "was", "you", "for", "are",
    "she", "his", "her", "boy", "girl", "play", "jump", "book", "tree", "star",
]

# Fixed phrases (slug -> spoken text). Dynamic sentences are composed at runtime
# by playing a phrase clip and then a letter/word clip.
PHRASES = {
    "hi": "Hi! I will read your words.",
    "learn": "Hello! Let's learn to spell.",
    "addwords": "Let's add your words first. Ask a grown up.",
    "which_letter": "Listen! Which letter is this?",
    "this_one": "This one!",
    "perfect": "Perfect! You did it!",
    "welldone": "Well done!",
    "blastoff": "Amazing! You finished all your words! Blast off!",
    "listen_watch": "Listen and watch.",
    "try_again": "Let's try again together.",
    "great_job": "Great job!",
    # ----- Space rescue mission narration -----
    "mission_start": "Captain! Space Command needs you. Little star friends are lost in space. Spell each word to bring them safely home. Are you ready? Let's blast off!",
    "mission_next": "Here comes a lost star. Listen closely!",
    "write_now": "Now write the letters with your finger!",
    "next_letter": "Now the next letter.",
    "rescued": "You rescued a star friend! Great work, Captain!",
    "mission_done": "Mission complete! You brought every star friend home. You are a spelling hero!",
    "trace_good": "Beautiful writing!",
    "trace_on": "Trace right on top of the letter.",
    "keep_going": "Keep going, you can do it!",
    # ----- Stage action guidance (so a non-reader knows what to do) -----
    "do_listen": "Step one, Captain! Listen closely and watch each letter light up.",
    "do_tap": "Catch the letters! Tap each glowing letter, in order, from the start.",
    "do_build": "Beam the letters home! Slide each one into its box to build the word.",
}


def load_words():
    """Words to voice: essentials below + optional words.txt dictionary."""
    words = set(WORDS)
    path = os.path.join(os.path.dirname(__file__), "words.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                w = "".join(ch for ch in line.strip().lower() if ch.isalpha())
                if 1 <= len(w) <= 12:
                    words.add(w)
    return sorted(words)


async def gen(text, path, rate="-8%"):
    if os.path.exists(path):        # idempotent: skip clips we already have
        return
    await edge_tts.Communicate(text, VOICE, rate=rate).save(path)
    print("  ", os.path.basename(path), text)


async def main():
    os.makedirs(OUT, exist_ok=True)
    all_words = load_words()
    print("Letters:")
    for l, name in LETTER_NAMES.items():
        await gen(name, os.path.join(OUT, f"letter_{l}.mp3"), rate="-12%")
    print(f"Words ({len(all_words)}):")
    for w in all_words:
        await gen(w, os.path.join(OUT, f"word_{w}.mp3"), rate="-6%")
    print("Phrases:")
    for slug, text in PHRASES.items():
        await gen(text, os.path.join(OUT, f"phrase_{slug}.mp3"), rate="-2%")

    # Emit a JS manifest (array of clip keys) for the app to know what exists.
    keys = ([f"letter_{l}" for l in LETTER_NAMES]
            + [f"word_{w}" for w in all_words]
            + [f"phrase_{s}" for s in PHRASES])
    manifest = "window.AUDIO_CLIPS=" + str(keys).replace("'", '"') + ";\n"
    with open(os.path.join(OUT, "manifest.js"), "w", encoding="utf-8") as f:
        f.write(manifest)
    print(f"\nDone. {len(keys)} clips + manifest.js")


if __name__ == "__main__":
    asyncio.run(main())
