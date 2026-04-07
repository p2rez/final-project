from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import csv

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
    songs = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
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
                acousticness=float(row['acousticness'])
            )
            songs.append(song)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Compute a score and explanation reasons for a single song given user preferences."""
    score = 0.0
    reasons = []
    
    # Genre match: half weight for exact match
    if song['genre'] == user_prefs['genre']:
        score += 0.5
        reasons.append("genre match (+0.5)")
    else:
        reasons.append("genre mismatch")
    
    # Mood feature temporarily removed for sensitivity testing
    # if song['mood'] == user_prefs['mood']:
    #     score += 1.0
    #     reasons.append("mood match (+1.0)")
    # else:
    #     reasons.append("mood mismatch")
    reasons.append("mood ignored")
    
    # Energy score: double weight for closeness-based match
    energy_diff = abs(song['energy'] - user_prefs['energy'])
    energy_score = 1 / (1 + energy_diff)
    weighted_energy = energy_score * 2.0
    score += weighted_energy
    reasons.append(f"energy closeness (+{weighted_energy:.2f})")
    
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
        }

    scored = [
        (song, score, "; ".join(reasons))
        for song in songs
        for score, reasons in [score_song(user_prefs, _song_to_dict(song))]
    ]
    return sorted(scored, key=lambda x: x[1], reverse=True)[:k]
