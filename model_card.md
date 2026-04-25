# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder generates personalized song recommendations for a single user session. Each run, it creates a randomized listener profile (genre preference, mood, and energy level) and returns the five songs from the catalog that best match that profile, along with a score breakdown and an AI-generated explanation for each pick.

The system is designed for classroom exploration of how content-based recommender systems work. It assumes the user wants to understand the reasoning behind each recommendation, not just receive a list. It is not intended for production use — the user profile is randomly generated rather than collected from a real person, and the catalog is small and fictional.

---

## 3. How the Model Works

Every song in the catalog has three attributes: genre, mood, and energy level (a number between 0 and 1). The user profile also has those three attributes. VibeFinder compares them directly.

For each song, it checks three things:
- Does the genre match? If yes, the song gets +1.0 points.
- Does the mood match? If yes, the song gets +1.0 points.
- How close is the energy level? The closer it is to the user's energy, the closer to +1.0 it scores. A perfect match is +1.0; a song at the opposite end of the energy scale scores close to 0.

The maximum score is 3.0 (perfect match on all three). Songs are ranked highest to lowest and the top five are returned.

A Gemini AI model then reads the user profile and each song's attributes and writes one sentence explaining why that song might appeal to the listener. This layer adds natural language on top of the numeric scoring, making the results easier to interpret.

From the original project: mood scoring had been silently disabled and energy was weighted at +2.0 while genre was only +0.5, causing energy to dominate results. Both were fixed — mood was restored and all three factors were equalized at +1.0 each.

---

## 4. Data

The catalog contains 60 songs across eight genres: pop, rock, lofi, jazz, ambient, synthwave, classical, and hip-hop. Each song has a genre label, a mood label (happy, sad, focused, moody, intense, relaxed, melancholic, or energetic), an energy value, tempo, valence, danceability, and acousticness. Every song also includes a two-sentence fictional artist biography.

No real songs or real artists are used. The dataset was written specifically for this project to ensure coverage across genre and mood combinations. Some genres (lofi, ambient, synthwave) have fewer songs than others, which means users with those preferences will see the same artists recommended repeatedly. Complex or niche musical tastes — subgenre nuance, cultural context, or listener history — are not represented.

---

## 5. Strengths

The system works well when the user profile aligns cleanly with a well-represented genre. A pop/happy profile or a lofi/focused profile consistently surfaces appropriate songs with high scores, and the score breakdown makes the reasoning transparent and easy to verify. Equal weighting across genre, mood, and energy means no single factor can override the other two, which keeps results balanced. The Gemini insight layer adds a conversational explanation that makes the output feel more like a recommendation and less like a spreadsheet.

---

## 6. Limitations and Bias

Genre and mood matching is all-or-nothing. A jazz fan gets zero genre credit for a blues song, and a user who wants "calm sad" music gets the same mood score as one who wants "intense sad." The energy scoring is continuous but the other two factors are binary, which creates a ceiling effect for users whose preferences fall between categories.

The catalog skews toward certain genres. Users with synthwave or classical preferences will see the same small pool of artists in nearly every run. The `likes_acoustic` field is part of the user profile data structure but is never used in scoring — acoustic preference is silently ignored.

Because the user profile is randomized rather than collected, the system never actually personalizes to anyone. It simulates personalization across the space of possible profiles, but a real user running it multiple times will get different profiles each time rather than consistent recommendations.

---

## 7. Evaluation

Testing covered five user profile types: pop/happy/high energy, lofi/focused/low energy, ambient/moody/very low energy, synthwave/intense/medium energy, and rock/moody/medium-low energy. For each profile, the top five results were checked to confirm that genre and mood matches appeared first and that energy scores decreased correctly down the list.

The most important test was `test_mood_is_not_ignored`, added after discovering that mood scoring had been completely disabled in the original codebase. The system produced plausible-looking results without mood — nothing crashed and scores were non-zero — which made the bug invisible until the source was read carefully. That regression test now fails immediately if mood is ever disabled again.

Fifteen automated tests cover all three scoring factors, the equal-weight enforcement, result ordering, bio loading from CSV, the empty catalog guardrail, and the missing file error. All 15 pass.

---

## 8. Future Work

The most impactful improvement would be partial genre credit — a jazz fan getting some score for blues, or a pop fan getting partial credit for indie pop, rather than a hard zero for any non-exact match. Second would be wiring in the `likes_acoustic` field that is already collected but unused.

Diversity filtering would prevent the same artist from occupying multiple slots in the top five, which currently happens frequently with small genres. A real user profile collected over multiple sessions — rather than re-randomized each run — would make the personalization genuine rather than simulated. The Gemini insight prompt could also be enriched with song valence and danceability data that is currently loaded but not passed to the model.

---

## 9. Personal Reflection

Building this recommender made it clear how much a scoring formula shapes what users see and what they never see. Changing a single weight completely reshuffled results — the same 60 songs told a completely different story depending on how the factors were balanced. The most surprising discovery was that mood had been silently disabled in the original code and the system still appeared to work. Scores were non-zero, results looked plausible, and nothing warned me. That moment changed how I think about testing: checking that a function returns something is not the same as checking that it does what it is supposed to do.

Adding the Gemini layer at the end was a different kind of lesson. The numeric scoring tells you *that* a song fits; the AI explanation tells you *why* in a way a person can actually read and respond to. The combination — transparent rule-based scoring plus generative natural language — felt more honest than either alone. Real recommendation systems rarely show you their math. Seeing both at once made the gap between "algorithmically correct" and "actually useful to a person" much more visible.
