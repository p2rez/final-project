# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

### Algorithm Recipe

Our music recommender uses a content-based filtering approach that scores songs based on how well they match a user's taste profile. Each song receives points across two criteria:

**Genre Match (0.5 points max):**
- **Genre Match**: +0.5 points if the song's genre exactly matches the user's favorite genre
- No partial credit for near-genre matches

**Energy Similarity (up to ~2.0 points):**
- Score is computed as `1 / (1 + |song_energy - target_energy|) × 2.0`
- A perfect match (0.0 difference) yields the maximum of 2.0 points
- Score decreases continuously as the energy difference grows
- No hard cutoff — every song gets some energy score

**Note:** Mood scoring is currently disabled for sensitivity testing. Songs are ranked primarily by energy closeness, with genre acting as a tiebreaker.

**Maximum Score**: ~2.5 points (genre match + perfect energy) | **Minimum Score**: ~0 points

### Data Flow Process

1. **Input**: User provides preferences (favorite_genre, favorite_mood, target_energy, likes_acoustic)
2. **Processing**: System loads songs from CSV and scores each song using the algorithm above
3. **Output**: Returns top K recommendations (default K=5) sorted by score, with explanations

### Potential Biases and Limitations

**Genre Over-Prioritization**: The system heavily weights genre matches (+2.0 points) compared to mood (+1.0 point), which may cause it to recommend songs that match the user's favorite genre but ignore excellent songs that perfectly match their preferred mood.

**Energy Similarity Threshold**: The current 0.4 energy difference cutoff means songs with energy levels outside this range get zero similarity points, potentially excluding songs that could still be enjoyable despite moderate energy differences.

**Limited Feature Set**: The system only considers basic audio features and categorical preferences, missing important factors like tempo preferences, lyrical content, or cultural context that real music recommenders consider.

**Small Catalog Impact**: With a limited song database, the system may not have enough variety to properly test edge cases or demonstrate the algorithm's effectiveness across different user types.

### Example Output

Here's a screenshot of the terminal output showing recommendations for a user profile preferring "pop" genre, "happy" mood, and energy level 0.8:

![Terminal recommendation screenshot](./screenshot-recommendation.png)

This output demonstrates how the system explains its recommendations with transparent scoring breakdowns.

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

- **Changed genre weight from 2.0 to 0.5**: Reducing the genre weight made energy the dominant factor. Songs with very close energy to the target ranked first even when the genre didn't match, which produced surprising but sometimes reasonable results.
- **Disabled mood scoring**: Removing the mood bonus (+1.0) to test sensitivity revealed that the system still ranked genre-matching songs near the top due to energy being a strong signal. However, it exposed a real weakness — two songs with identical genre and energy can't be distinguished by mood at all.
- **Tested adversarial profiles** (see `run_profiles.py`): Profiles with conflicting preferences (e.g., `favorite_mood='sad'` but `target_energy=0.9`) caused the system to recommend intense high-energy tracks regardless of mood. A user who wants calm sad music would get completely wrong results.
- **Tried a profile with a non-existent genre** (`classical` with `ecstatic` mood): No songs matched genre, so all results were ranked by energy alone — the system silently falls back without warning the user.

---

## Limitations and Risks

- It only works on a tiny 18-song catalog, so results repeat and variety is limited
- It does not understand lyrics, language, cultural context, or tempo preferences
- Mood scoring is currently disabled, so two users with opposite moods but the same energy target get identical recommendations
- Genre matching is all-or-nothing — a "jazz" fan gets no credit for liking a "blues" song
- The acoustic preference field in `UserProfile` is collected but never used in scoring

---

## Reflection

[**Model Card**](model_card.md)

Building this recommender made it clear how much a scoring formula shapes what users see — and what they don't. Changing a single weight (like dropping genre from 2.0 to 0.5) completely reshuffled results, which showed how the same data can tell very different "stories" depending on the designer's choices. The most surprising moment was running adversarial profiles: a user who prefers sad, low-energy music still received high-energy pop tracks because the energy signal dominated everything else.

This made me think about real systems like Spotify or YouTube. Their algorithms face the same tradeoffs at massive scale — and the consequences of getting them wrong (showing someone the wrong kind of content repeatedly) are much larger. Human judgment still matters when deciding *which* features to weight and *whose* preferences count. A model that optimizes for one group's taste can be unfair to users with different backgrounds or listening habits, even if it's technically "correct" by its own scoring rules.


