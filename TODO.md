# NCLEX CSS Separation TODO

## Status: ✅ Step 1 Complete | 🔄 In Progress

### 1. ✅ Create CSS Directory Structure & Files
   - ✅ static/css/base.css (from base.html)
   - ✅ pages/static/pages/css/home.css (from pages/home.html)
   - ✅ exam_sessions/static/exam_sessions/css/take_exam.css (from take_exam.html)
   - ✅ game/static/game/css/play_game.css (from play_game.html)
   - ✅ gamification/static/gamification/css/badges.css (from badges.html) *(minor linter fix pending)*

### 2. ✅ Update base.html
   - ✅ Extract & link static/css/base.css
   - ✅ Remove inline <style>

### 3. ✅ Update App Templates
   - ✅ pages/templates/pages/home.html → link pages/css/home.css
   - ✅ exam_sessions/templates/exam_sessions/take_exam.html → link exam_sessions/css/take_exam.css
   - ✅ game/templates/game/play_game.html → link game/css/play_game.css
   - ✅ gamification/templates/gamification/badges.html → link gamification/css/badges.css

### 4. ✅ Collect Static & Test
   - ✅ python manage.py collectstatic --noinput (0 new, 316 unmodified)
   - [ ] python manage.py collectstatic --noinput
   - [ ] Test: runserver, verify pages (home, exam, game, badges)
   - [ ] Check F12: no 404 CSS, styles intact

### 5. [ ] Complete
   - [ ] attempt_completion
