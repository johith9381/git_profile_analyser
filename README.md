# GitInsight — Developer Intelligence Platform

GitInsight analyzes any public GitHub profile and surfaces deep insights about coding behavior, personality, technology evolution, and growth trajectory — the kind of things GitHub itself never shows you.

---

## Project Overview

This is a Flask web app that fetches public GitHub data (profile + repositories) and runs custom analytics to build a developer portrait. You enter a GitHub username, hit Analyze, and get a full visual dashboard.

---

## Features

**Overview**
- Activity Score, Consistency Index, and Diversity Index at a glance
- Developer DNA Breakdown — four scored traits: Builder, Collaborator, Innovator, Consistency
- Growth Potential and Innovation Index metrics

**Activity**
- 35-day contribution heatmap based on repository push timestamps
- Developer Radar chart mapping personality traits
- Productivity pattern detection (Night Coder, Weekend Builder, Burst Developer, etc.)

**Technology**
- Technology Evolution Timeline — shows when you first used each language
- Language Ecosystem doughnut chart
- Skill Proficiency radar
- Full language distribution breakdown with progress bars

**Repositories**
- Top 6 repos ranked by a custom Impact Score formula: `(stars × 2) + (forks × 3) + open_issues`

**Patterns**
- Six unique analytic cards: Coding Rhythm, Project Depth, Developer Personality, Project Diversity, Growth Trajectory, Collaboration Style

**Insights**
- Smart text insights derived from all the above data
- Career role prediction (Frontend, Backend, Full Stack, Data Scientist, DevOps)
- Technology direction analysis based on first vs. recent language usage

---

## How It Works

1. User enters a GitHub username and clicks Analyze
2. Flask fetches the GitHub API: `/users/{username}` and `/users/{username}/repos`
3. Python functions compute all metrics from the raw data
4. Results are stored in the Flask session and the user is redirected to the dashboard
5. The dashboard renders charts (Chart.js), heatmap, and all analytics sections
6. Navigation between sections is handled with jQuery — no page reloads

---

## Unique Analytics Explained

**Developer Growth Timeline** — Repos are sorted by creation date. The first time a new language appears marks a "milestone." This reveals how a developer's stack grew year by year.

**Technology Direction** — Comparing the oldest repos (bottom of the timeline) with recent ones shows whether someone is pivoting to new languages or deepening their focus on existing ones.

**Project Diversity** — `unique_languages / total_repos × 100`. A high score means broad exploration; a low score means deep specialization.

**Coding Rhythm** — Repository push hours and weekday distribution are analyzed. If >50% of pushes happen on weekends, you're a Weekend Builder. Night pushes after midnight? Night Coder. Multiple repos created in a single month? Burst Developer.

**Project Depth** — `(average repo size / 1000) + (unique_languages × 2) + (documented_repos / total × 10)`. Maps to Beginner / Intermediate / Advanced.

**Developer DNA** — Four composite scores built from public signals:
- Builder: repo count + stars
- Collaborator: followers + forks
- Innovator: language variety + stars
- Consistency: recent activity ratio + repo volume

---

## How To Run

**Prerequisites:** Python 3.8+, pip

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Open your browser at `http://localhost:5000`

No API key needed. Uses the public GitHub API. Rate limits may apply (60 requests/hour unauthenticated). For higher limits, set a `GITHUB_TOKEN` environment variable.

---

## Project Structure

```
app.py                   — Flask routes and all analytics logic
templates/index.html     — Homepage with animated commit grid
templates/dashboard.html — Dashboard with 6 analytics sections
static/css/style.css     — All styles, animations, and keyframes
static/js/script.js      — jQuery form handling, Chart.js, dashboard logic
requirements.txt         — Python dependencies
```
