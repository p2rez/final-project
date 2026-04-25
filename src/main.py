"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import logging
import os
import random
from recommender import load_songs, recommend_songs

# Gemini AI insight — requires GEMINI_API_KEY env var; skipped gracefully if missing
try:
    from google import genai as _genai
    _gemini_key = os.environ.get("GEMINI_API_KEY", "")
    _gemini_client = _genai.Client(api_key=_gemini_key) if _gemini_key else None
except ImportError:
    _gemini_client = None


def get_ai_insight(user_prefs: dict, title: str, artist: str, genre: str, mood: str, energy: float) -> str:
    """Call Gemini to generate a one-sentence personal insight for a recommendation."""
    if _gemini_client is None:
        return ""
    prompt = (
        f"A music listener who enjoys {user_prefs['genre']} music, "
        f"a {user_prefs['mood']} mood, and energy level {user_prefs['energy']:.2f} "
        f"was recommended '{title}' by {artist} "
        f"(genre: {genre}, mood: {mood}, energy: {energy:.2f}). "
        "In one sentence, explain in a friendly tone why this song might resonate with them."
    )
    try:
        response = _gemini_client.models.generate_content(
            model="gemini-2.5-flash-lite", contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        # Log API failures without crashing the recommendation loop
        logging.warning("Gemini API call failed: %s", e)
        return ""

# Log application-level warnings to the same file as recommender.py
logging.basicConfig(
    filename="data/recommender.log",
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# File used to persist the generation count across runs
COUNTER_FILE = "data/generation_count.txt"


def get_and_increment_count() -> int:
    """Read the current generation count, increment it, save it, and return the new value."""
    count = 0
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            raw = f.read().strip()
            # Guardrail: reset to 0 if the counter file contains non-numeric content
            try:
                count = int(raw)
            except ValueError:
                # Log corruption so it is recorded even if the terminal output is missed
                logging.warning("Counter file corrupted (value: '%s'), resetting to 0.", raw)
                print(f"Warning: counter file was corrupted ('{raw}'), resetting to 0.")
                count = 0
    count += 1
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(count))
    return count

# GUARDRAIL: Seed from OS entropy to guarantee a different sequence every run
random.seed(os.urandom(16))


def random_user_prefs(songs: list) -> dict:
    genres = list({s['genre'] if isinstance(s, dict) else s.genre for s in songs})
    moods = list({s['mood'] if isinstance(s, dict) else s.mood for s in songs})
    energy = round(random.uniform(0.2, 1.0), 2)
    return {"genre": random.choice(genres), "mood": random.choice(moods), "energy": energy}


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Guardrail: stop early if no songs loaded to avoid crashes downstream
    if not songs:
        logging.error("No songs loaded from CSV — aborting generation.")
        print("Error: no songs were loaded. Check that data/songs.csv exists and is not empty.")
        return

    # Increment and display the persistent generation counter
    generation = get_and_increment_count()
    print(f"Generation #{generation}")

    # Profile is randomized each run so recommendations vary
    user_prefs = random_user_prefs(songs)
    print(f"User profile this run: genre={user_prefs['genre']}, mood={user_prefs['mood']}, energy={user_prefs['energy']}")

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        song, score, explanation = rec
        reasons = explanation.split("; ")
        if isinstance(song, dict):
            title = song['title']
            artist = song['artist']
        else:
            title = song.title
            artist = song.artist
        # Display artist bio from CSV alongside song details
        bio = song.get('bio', '') if isinstance(song, dict) else song.bio
        genre = song.get('genre', '') if isinstance(song, dict) else song.genre
        mood = song.get('mood', '') if isinstance(song, dict) else song.mood
        energy = song.get('energy', 0.0) if isinstance(song, dict) else song.energy
        print(f"🎵 {title} by {artist}")
        print(f"   Score: {score:.2f}")
        if bio:
            print(f"   About the artist: {bio}")
        print("   Reasons:")
        for reason in reasons:
            print(f"     - {reason}")
        # AI-generated insight explaining why this song fits the listener
        insight = get_ai_insight(user_prefs, title, artist, genre, mood, energy)
        if insight:
            print(f"   Why you might like this: {insight}")
        print()


if __name__ == "__main__":
    # Loop so the user can generate again without re-running the program
    while True:
        main()
        try:
            again = input("Would you like to generate again? (yes/no): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            # Guardrail: handle Ctrl+C or piped input gracefully
            print("\nExiting.")
            break
        if again not in ("yes", "y"):
            # Read the final count to display before exiting
            final_count = 0
            if os.path.exists(COUNTER_FILE):
                with open(COUNTER_FILE, 'r') as f:
                    final_count = int(f.read().strip() or 0)
            print(f"\nThanks for using the recommender! Total generations this session: {final_count}")
            break
