from src.recommender import Song, UserProfile, Recommender, score_song, load_songs


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_song(**overrides) -> Song:
    """Return a base Song with any field overridden for targeted tests."""
    defaults = dict(
        id=1, title="Test Track", artist="Test Artist",
        genre="pop", mood="happy", energy=0.8,
        tempo_bpm=120, valence=0.9, danceability=0.8,
        acousticness=0.2, bio="A test artist bio."
    )
    defaults.update(overrides)
    return Song(**defaults)


def make_recommender(*songs) -> Recommender:
    return Recommender(list(songs))


def song_to_dict(song: Song) -> dict:
    return {
        "genre": song.genre, "mood": song.mood, "energy": song.energy,
        "id": song.id, "title": song.title, "artist": song.artist,
        "tempo_bpm": song.tempo_bpm, "valence": song.valence,
        "danceability": song.danceability, "acousticness": song.acousticness,
        "bio": song.bio,
    }


# ── Score: genre ──────────────────────────────────────────────────────────────

def test_genre_match_adds_one_point():
    """Exact genre match must contribute exactly +1.0."""
    prefs = {"genre": "pop", "mood": "chill", "energy": 0.5}
    song = song_to_dict(make_song(genre="pop", mood="sad", energy=0.5))
    score, reasons = score_song(prefs, song)
    assert "genre match (+1.0)" in reasons


def test_genre_mismatch_adds_no_points():
    """Genre mismatch must not contribute any genre points."""
    prefs = {"genre": "jazz", "mood": "chill", "energy": 0.5}
    song = song_to_dict(make_song(genre="rock", mood="chill", energy=0.5))
    score, reasons = score_song(prefs, song)
    assert "genre mismatch" in reasons
    assert not any("genre match" in r for r in reasons)


# ── Score: mood ───────────────────────────────────────────────────────────────

def test_mood_match_adds_one_point():
    """Mood match must contribute exactly +1.0 — verifies mood is not disabled."""
    prefs = {"genre": "rock", "mood": "intense", "energy": 0.5}
    song = song_to_dict(make_song(genre="lofi", mood="intense", energy=0.5))
    score, reasons = score_song(prefs, song)
    assert "mood match (+1.0)" in reasons


def test_mood_mismatch_adds_no_points():
    """Mood mismatch must not contribute any mood points."""
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.5}
    song = song_to_dict(make_song(genre="pop", mood="sad", energy=0.5))
    score, reasons = score_song(prefs, song)
    assert "mood mismatch" in reasons
    assert not any("mood match" in r for r in reasons)


def test_mood_is_not_ignored():
    """Regression: mood was previously disabled. Two songs identical except mood
    must score differently when the profile mood matches only one of them."""
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    happy = song_to_dict(make_song(mood="happy"))
    sad   = song_to_dict(make_song(mood="sad"))
    score_happy, _ = score_song(prefs, happy)
    score_sad,   _ = score_song(prefs, sad)
    assert score_happy > score_sad, "Mood match should raise the score"


# ── Score: energy ─────────────────────────────────────────────────────────────

def test_perfect_energy_match_scores_near_one():
    """Zero energy difference must yield an energy score of exactly 1.0."""
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.7}
    song = song_to_dict(make_song(energy=0.7))
    score, reasons = score_song(prefs, song)
    assert any("energy closeness (+1.00)" in r for r in reasons)


def test_energy_score_decreases_with_distance():
    """A song with closer energy must outscore one with farther energy."""
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    close = song_to_dict(make_song(energy=0.85))
    far   = song_to_dict(make_song(energy=0.4))
    score_close, _ = score_song(prefs, close)
    score_far,   _ = score_song(prefs, far)
    assert score_close > score_far


def test_energy_max_weight_equals_one():
    """Energy must never contribute more than 1.0 (capped to match genre/mood)."""
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.5}
    song = song_to_dict(make_song(energy=0.5))
    score, _ = score_song(prefs, song)
    # Max possible score = 1.0 (genre) + 1.0 (mood) + 1.0 (energy) = 3.0
    assert score <= 3.0


# ── Score: equal weights ──────────────────────────────────────────────────────

def test_all_three_factors_equal_weight():
    """Genre, mood, and energy must each contribute at most 1.0 — no factor dominates."""
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    # Perfect match on all three
    perfect = song_to_dict(make_song(genre="pop", mood="happy", energy=0.8))
    score_perfect, _ = score_song(prefs, perfect)
    assert abs(score_perfect - 3.0) < 0.01

    # Genre + mood match, energy far off
    partial = song_to_dict(make_song(genre="pop", mood="happy", energy=0.0))
    score_partial, _ = score_song(prefs, partial)
    # Should be roughly 2.0 + small energy contribution, never reach 3.0
    assert score_partial < score_perfect


# ── Recommender class ─────────────────────────────────────────────────────────

def test_recommend_returns_correct_count():
    """recommend() must return exactly k songs."""
    songs = [make_song(id=i, title=f"Song {i}") for i in range(10)]
    rec = Recommender(songs)
    user = UserProfile("pop", "happy", 0.8, False)
    assert len(rec.recommend(user, k=3)) == 3
    assert len(rec.recommend(user, k=1)) == 1


def test_recommend_sorts_by_score():
    """Best-matching song must appear first in results."""
    best  = make_song(id=1, genre="pop", mood="happy", energy=0.8)
    worst = make_song(id=2, genre="lofi", mood="sad",   energy=0.1)
    rec   = make_recommender(worst, best)
    user  = UserProfile("pop", "happy", 0.8, False)
    results = rec.recommend(user, k=2)
    assert results[0].id == best.id


def test_explain_recommendation_is_non_empty():
    """explain_recommendation() must return a non-empty string."""
    rec  = make_recommender(make_song())
    user = UserProfile("pop", "happy", 0.8, False)
    explanation = rec.explain_recommendation(user, rec.songs[0])
    assert isinstance(explanation, str) and explanation.strip()


# ── Bio integration ───────────────────────────────────────────────────────────

def test_song_bio_is_loaded():
    """Songs loaded from the real CSV must carry a non-empty bio field."""
    songs = load_songs("data/songs.csv")
    for song in songs:
        assert hasattr(song, "bio"), "Song is missing bio attribute"
        assert isinstance(song.bio, str)
    # At least some songs should have a bio
    assert any(s.bio for s in songs), "No songs have a bio — check the CSV"


# ── Guardrail: empty catalog ──────────────────────────────────────────────────

def test_recommender_handles_empty_song_list():
    """Recommender must not crash when the song list is empty."""
    rec  = Recommender([])
    user = UserProfile("pop", "happy", 0.8, False)
    results = rec.recommend(user, k=5)
    assert results == []


# ── Guardrail: missing CSV ────────────────────────────────────────────────────

def test_load_songs_raises_on_missing_file():
    """load_songs must raise FileNotFoundError for a non-existent path."""
    import pytest
    with pytest.raises(FileNotFoundError):
        load_songs("data/does_not_exist.csv")
