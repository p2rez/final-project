# Music Recommender Simulation

## Live Demo

[Watch the live demo on Loom](https://www.loom.com/share/2e58a6813dcb4564b106c3b913d08699)

---

## Original Project

This project originates from the **Music Recommender Simulation** built across Modules 1–3. The original goal was to represent songs and a user taste profile as structured data, then design a content-based scoring algorithm that turns that data into ranked recommendations. It demonstrated how real-world AI recommenders work by making the scoring logic transparent and explainable, returning not just results but the reasons behind each one.

---

## Title and Summary

**Music Recommender Simulation** is a command-line application that generates personalized song recommendations based on a randomized user profile. It matters because it makes the mechanics of recommendation algorithms visible — every result comes with a score breakdown explaining exactly why a song was suggested, which mirrors how systems like Spotify or YouTube work under the hood, but without the black box. A Gemini AI integration adds a natural-language "Why you might like this" insight for each recommendation, generated live by a large language model.

---

## Architecture Overview

The system is built around five core components that pass data through a linear pipeline:

1. **Data Store** (`songs.csv`) — 60 songs with genre, mood, energy, and a fictional 2-sentence artist biography.
2. **Loader** (`load_songs`) — reads and validates the CSV, skipping any malformed rows with a warning rather than crashing.
3. **Profile Generator** (`random_user_prefs`) — picks a random genre, mood, and energy level each run, seeded from OS entropy to guarantee uniqueness.
4. **Scorer + Recommender** (`score_song`, `recommend_songs`) — scores every song against the profile using three equally weighted factors (genre, mood, energy), then returns the top 5.
5. **Gemini AI Insight** (`get_ai_insight`) — calls the Gemini API to generate a one-sentence natural-language explanation of why each top song fits the listener's profile.

A **human checkpoint** sits at the end of each run: the user reviews the results and decides whether to generate again. A persistent counter file tracks how many generations have occurred across all sessions.

```
songs.csv ──► load_songs ──► [Song objects]
                                    │
OS entropy ──► random seed          │
                   │                ▼
                   └──► random_user_prefs ──► {genre, mood, energy}
                                                     │
                                                     ▼
                                            score_song (per song)
                                                     │
                                                     ▼
                                           sorted top-5 results
                                                     │
                                    ┌────────────────┘
                                    ▼
                             get_ai_insight
                          (Gemini API per song)
                                    │
                                    ▼
                         ┌───────────────────────┐
                         │   Human Reviews       │
                         │   Run again? yes/no   │
                         └───────────────────────┘
                                    │
                         generation_count.txt
                         (incremented each run)
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd final-project
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate      # Mac / Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Gemini API key

The app uses the Gemini API to generate a personalized insight for each recommendation. Get a free key at [aistudio.google.com](https://aistudio.google.com), then set it in your terminal:

```bash
export GEMINI_API_KEY=your_key_here
```

If the key is missing, the app runs normally but skips the AI insight lines.

### 5. Run the application

```bash
cd final-project
python3 src/main.py
```

### 5. Run the tests

```bash
pytest
```

---

## Sample Interactions

### Example 1 — Pop / Happy Profile

```
Generation #1
User profile this run: genre=pop, mood=happy, energy=0.87

Top recommendations:

🎵 Bounce Back by Max Pulse
   Score: 2.94
   About the artist: Max Pulse is a high-energy pop producer and DJ from Miami
   whose tracks are engineered to push listeners to their limits. He has produced
   anthems for major fitness brands and international sporting events.
   Reasons:
     - genre match (+1.0)
     - mood match (+1.0)
     - energy closeness (+0.94)
   Why you might like this: This high-energy pop track perfectly matches your
   upbeat mood and love of pop, making it an ideal pick-me-up for your playlist.

🎵 Sunrise City by Neon Echo
   Score: 2.93
   About the artist: Neon Echo is a Los Angeles-based electronic duo known for
   blending retro synthwave textures with modern pop energy. They rose to
   prominence in 2019 after their debut EP went viral on underground music blogs.
   Reasons:
     - genre match (+1.0)
     - mood match (+1.0)
     - energy closeness (+0.93)
   Why you might like this: With its bright, driving energy and happy pop sound,
   Sunrise City should feel like a natural fit for your current vibe.

Would you like to generate again? (yes/no):
```

---

### Example 2 — Lofi / Focused Profile

```
Generation #2
User profile this run: genre=lofi, mood=focused, energy=0.41

Top recommendations:

🎵 Focus Flow by LoRoom
   Score: 2.99
   About the artist: LoRoom is a solo bedroom producer from Portland whose hazy,
   tape-warped beats have become a staple of late-night study playlists worldwide.
   He crafts every track using a single vintage sampler and a worn-out cassette deck.
   Reasons:
     - genre match (+1.0)
     - mood match (+1.0)
     - energy closeness (+0.99)
   Why you might like this: This lofi track is basically built for your focused
   headspace — low energy, calm mood, and a hazy texture perfect for deep work.

🎵 Deep Focus by LoRoom
   Score: 2.97
   About the artist: LoRoom is a solo bedroom producer from Portland whose hazy,
   tape-warped beats have become a staple of late-night study playlists worldwide.
   He crafts every track using a single vintage sampler and a worn-out cassette deck.
   Reasons:
     - genre match (+1.0)
     - mood match (+1.0)
     - energy closeness (+0.97)
   Why you might like this: Another strong match — similar tempo and that same
   focused, unhurried feel that pairs well with your current energy level.

Would you like to generate again? (yes/no):
```

---

### Example 3 — Ambient / Moody Profile, User Exits

```
Generation #3
User profile this run: genre=ambient, mood=moody, energy=0.19

Top recommendations:

🎵 Void Walker by Orbit Bloom
   Score: 2.99
   About the artist: Orbit Bloom is an ambient composer and sound designer based
   in Reykjavik who creates vast, meditative soundscapes inspired by astronomy
   and deep space. Her music has been featured in planetarium shows and science
   documentaries across Europe.
   Reasons:
     - genre match (+1.0)
     - mood match (+1.0)
     - energy closeness (+0.99)

Would you like to generate again? (yes/no): no

Thanks for using the recommender! Total generations this session: 3
```

---

## Design Decisions

### Content-based filtering over collaborative filtering
The system scores each song directly against the user profile rather than comparing users to each other. This keeps the logic transparent and explainable — every score has a clear reason — which was the primary goal of the project.

### Equal weights for genre, mood, and energy
Each factor contributes a maximum of +1.0 to the score. An earlier version weighted energy at +2.0 and genre at +0.5, which caused energy to dominate and made genre and mood feel irrelevant. Equalizing the weights means no single factor can override the others.

### Randomized user profile instead of a fixed one
The original project used a hardcoded `{"genre": "pop", "mood": "happy", "energy": 0.8}` for every run, producing identical results every time. Randomizing the profile using OS entropy makes each run genuinely different and exercises more of the dataset.

### Persistent generation counter
A flat text file (`generation_count.txt`) was chosen over a database because the only data that needs to survive between runs is a single integer. It is simple, human-readable, and requires no additional dependencies.

### Artist bios stored in the CSV
Rather than making live API calls to Wikipedia (which would fail since all artists are fictional), bios were written once and stored directly in the CSV alongside the song data. This keeps the system fully self-contained and offline-capable.

### Gemini AI for natural-language insights
After scoring, each top result is passed to the Gemini API (`gemini-2.5-flash-lite`) with a prompt describing the user profile and song attributes. The model returns a single friendly sentence explaining why that song fits the listener. The call is wrapped in a try/except so a quota error or missing key never crashes the program — it simply omits the insight line. This keeps the AI feature additive rather than load-bearing.

### Trade-offs
- The scoring formula is simple and interpretable but cannot capture nuance. Two songs with identical genre, mood, and energy score identically even if they sound nothing alike.
- Genre and mood matching is all-or-nothing. A jazz fan gets no partial credit for a blues song.
- The `likes_acoustic` field in `UserProfile` is defined but not yet wired into scoring.

---

## Testing Summary

The system uses **three layers of reliability verification**: automated unit tests, structured logging, and manual integration review.

### Automated Tests — 15 tests, all passing

Run with:
```bash
python3 -m pytest tests/ -v
```

```
tests/test_recommender.py::test_genre_match_adds_one_point         PASSED
tests/test_recommender.py::test_genre_mismatch_adds_no_points      PASSED
tests/test_recommender.py::test_mood_match_adds_one_point          PASSED
tests/test_recommender.py::test_mood_mismatch_adds_no_points       PASSED
tests/test_recommender.py::test_mood_is_not_ignored                PASSED
tests/test_recommender.py::test_perfect_energy_match_scores_near_one PASSED
tests/test_recommender.py::test_energy_score_decreases_with_distance PASSED
tests/test_recommender.py::test_energy_max_weight_equals_one       PASSED
tests/test_recommender.py::test_all_three_factors_equal_weight     PASSED
tests/test_recommender.py::test_recommend_returns_correct_count    PASSED
tests/test_recommender.py::test_recommend_sorts_by_score           PASSED
tests/test_recommender.py::test_explain_recommendation_is_non_empty PASSED
tests/test_recommender.py::test_song_bio_is_loaded                 PASSED
tests/test_recommender.py::test_recommender_handles_empty_song_list PASSED
tests/test_recommender.py::test_load_songs_raises_on_missing_file  PASSED

15 passed in 0.02s
```

Tests cover: scoring weights for each factor, the mood regression (previously disabled), equal weighting enforcement, result ordering, bio loading from CSV, empty catalog safety, and missing file guardrail.

### Logging

All warnings and errors are written to `data/recommender.log` with timestamps so failures are recorded even if the terminal output is missed. Logged events include: corrupted counter file, bad CSV rows skipped during load, and empty song catalog on startup.

### What worked
- Scoring logic behaved correctly. Rebalancing weights had an immediate and measurable effect on results.
- The run-again loop and generation counter held up across multiple sessions without drift.

### What didn't work initially
- Mood scoring was silently disabled in the original codebase — caught only by reading the source, not by any existing test. The new `test_mood_is_not_ignored` regression test now prevents this from happening again.
- `_song_to_dict` was stripping the `bio` field during conversion — caught during manual integration review.
- The counter guardrail only handled empty strings, not corrupt non-numeric content like `"abc"` — fixed and now logged.

### What was learned
- Silent failures are harder to catch than crashes. Tests that only check return types won't surface a disabled feature.
- Logging alongside print statements means problems leave a trail even when no one is watching the terminal.

---

## Responsible AI Reflection

### Limitations and Biases

The system has several built-in limitations worth acknowledging. Genre and mood matching is all-or-nothing — a jazz fan gets zero credit for a blues song, and a user who wants "calm sad" music might get loud intense tracks if their energy level happens to match. The catalog of 60 songs is small and skewed toward certain genres, meaning some profiles will almost always surface the same artists. The `likes_acoustic` field is collected from the user profile but never used in scoring, so acoustic preference is silently ignored. Perhaps most importantly, the user profile is randomly generated rather than collected from a real person — which means the system is never actually personalizing to anyone. It is simulating personalization, not delivering it.

### Potential for Misuse

A music recommender seems low-stakes, but the same design patterns used here appear in higher-risk systems. The core risk is that a simple scoring formula can be manipulated: if someone could inject songs into the catalog with artificially inflated scores, those songs would surface in every recommendation regardless of actual fit. In a real system this could be used to promote content unfairly. Prevention would require input validation on the catalog, rate limiting on any submission mechanism, and auditing which songs appear most frequently across diverse user profiles to detect gaming. For this project, the CSV is the only data source and is not user-editable at runtime, which limits that surface area — but it is worth naming.

### What Surprised Me During Testing

The most surprising finding was that mood scoring had been completely disabled in the original codebase and the system still appeared to work correctly. Results looked reasonable, scores were non-zero, and nothing crashed. There was no visible sign that an entire feature was missing. This was only caught by reading the source code carefully — none of the original two tests checked whether mood affected the score at all. It reinforced that a system can seem reliable while silently ignoring user input. The regression test `test_mood_is_not_ignored` was added specifically because of this discovery.

### Collaboration with AI During This Project

AI assistance was used throughout this project to write and refine code, add guardrails, expand the test suite, and draft documentation.

**One instance where the AI gave a helpful suggestion:** When asked about adding artist bios, the AI immediately flagged that all artists in the dataset were fictional and that a Wikipedia API call would return nothing — before writing any code. That saved time that would have been spent building an integration that could never work, and led to the better solution of storing bios directly in the CSV.

**One instance where the suggestion was flawed:** When the logging configuration was added to both `main.py` and `recommender.py`, the AI placed two separate `logging.basicConfig()` calls in each file. In Python, `basicConfig` is a no-op after the first call, meaning the second configuration silently does nothing. The log file still works because both modules share the same logging system, but the duplicated setup is misleading — it implies each file configures logging independently when only the first call has any effect. The correct approach would be to configure logging once in a shared entry point. This is a subtle Python behavior that the AI did not flag.

### Reflection

Building this recommender made it clear how much a scoring formula shapes what users see — and what they don't. Changing a single weight completely reshuffled results, which showed how the same data can tell very different stories depending on the designer's choices. The most surprising moment was discovering that mood had been silently disabled: the system appeared to work, produced plausible-looking results, and gave no indication that an entire feature was missing.

This mirrors a real risk in AI systems. A model can look functional on the surface while ignoring an entire category of user preference. Real systems like Spotify or YouTube face the same tradeoffs at massive scale, and the consequences of getting them wrong — showing someone the wrong kind of content repeatedly — are much larger. Human judgment still matters when deciding which features to weight and whose preferences count. A model that optimizes for one group's taste can quietly fail everyone else, even if it is technically correct by its own scoring rules.
