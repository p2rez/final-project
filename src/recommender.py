from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv
import logging
import os

# Log warnings and errors to a file so failures are recorded, not just printed
logging.basicConfig(
    filename="data/recommender.log",
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Added to store fictional artist biography for display in results
    bio: str = ""

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # Convert UserProfile to dict for scoring
        user_prefs = {
            'genre': user.favorite_genre,
            'mood': user.favorite_mood,
            'energy': user.target_energy
        }
        # Score all songs
        scored = []
        for song in self.songs:
            song_dict = {
                'id': song.id,
                'title': song.title,
                'artist': song.artist,
                'genre': song.genre,
                'mood': song.mood,
                'energy': song.energy,
                'tempo_bpm': song.tempo_bpm,
                'valence': song.valence,
                'danceability': song.danceability,
                'acousticness': song.acousticness
            }
            score, reasons = score_song(user_prefs, song_dict)
            scored.append((song, score, reasons))
        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_prefs = {
            'genre': user.favorite_genre,
            'mood': user.favorite_mood,
            'energy': user.target_energy
        }
        song_dict = {
            'id': song.id,
            'title': song.title,
            'artist': song.artist,
            'genre': song.genre,
            'mood': song.mood,
            'energy': song.energy,
            'tempo_bpm': song.tempo_bpm,
            'valence': song.valence,
            'danceability': song.danceability,
            'acousticness': song.acousticness
        }
        _, reasons = score_song(user_prefs, song_dict)
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Song]:
    """Load songs from a CSV file and return them as Song objects."""
    # Guardrail: catch missing CSV file with a clear error message
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Songs file not found: '{csv_path}'. Make sure the data folder is present.")

    songs = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            # Guardrail: skip rows with bad numeric values instead of crashing the entire load
            try:
                song = Song(
                    id=int(row['id']),
                    title=row['title'],
                    artist=row['artist'],
                    genre=row['genre'],
                    mood=row['mood'],
                    energy=float(row['energy']),
                    tempo_bpm=float(row['tempo_bpm']),
                    valence=float(row['valence']),
                    danceability=float(row['danceability']),
                    acousticness=float(row['acousticness']),
                    # Load artist bio added to CSV for recommendation display
                    bio=row.get('bio', '')
                )
                songs.append(song)
            except (ValueError, KeyError) as e:
                # Log bad rows to file instead of only printing to terminal
                logging.warning("Skipping row %d due to bad data: %s", i, e)
                print(f"Warning: skipping row {i} due to bad data ({e})")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Compute a score and explanation reasons for a single song given user preferences."""
    score = 0.0
    reasons = []
    
    # Rebalanced: genre, mood, and energy each contribute equally (max +1.0)
    if song['genre'] == user_prefs['genre']:
        score += 1.0
        reasons.append("genre match (+1.0)")
    else:
        reasons.append("genre mismatch")

    # Restored mood matching — was previously disabled for sensitivity testing
    if song['mood'] == user_prefs['mood']:
        score += 1.0
        reasons.append("mood match (+1.0)")
    else:
        reasons.append("mood mismatch")

    # Energy score: capped at 1.0 to match genre and mood weight
    energy_diff = abs(song['energy'] - user_prefs['energy'])
    energy_score = 1 / (1 + energy_diff)
    score += energy_score
    reasons.append(f"energy closeness (+{energy_score:.2f})")
    
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Return the top-k recommended songs sorted by score with explanation reasons."""
    def _song_to_dict(song_item):
        if isinstance(song_item, dict):
            return song_item
        return {
            'id': song_item.id,
            'title': song_item.title,
            'artist': song_item.artist,
            'genre': song_item.genre,
            'mood': song_item.mood,
            'energy': song_item.energy,
            'tempo_bpm': song_item.tempo_bpm,
            'valence': song_item.valence,
            'danceability': song_item.danceability,
            'acousticness': song_item.acousticness,
            # Include bio so it is available when displaying results in main.py
            'bio': song_item.bio,
        }

    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, _song_to_dict(song))]
    ]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
