from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.environ.get("DIL_SECRET_KEY", "dev-secret-key")


def login_required():
    return True


@app.route("/login", methods=["GET", "POST"])
def login():
    return redirect(url_for("analyzer"))


@app.route("/", methods=["GET"])
def analyzer():
    return render_template("index.html")


def fetch_github_profile(username):
    u = f"https://api.github.com/users/{username}"
    r = requests.get(u, timeout=10)
    if r.status_code == 404:
        return None
    if r.status_code != 200:
        return None
    return r.json()


def fetch_github_repos(username):
    u = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
    r = requests.get(u, timeout=15)
    if r.status_code == 404:
        return None
    if r.status_code != 200:
        return None
    return r.json()


def compute_activity_score(profile, repos):
    followers = profile.get("followers", 0)
    repo_count = len(repos)
    total_stars = sum([repo.get("stargazers_count", 0) for repo in repos])
    return followers + repo_count + total_stars


def language_stats(repos):
    counts = {}
    for repo in repos:
        lang = repo.get("language")
        if not lang:
            continue
        counts[lang] = counts.get(lang, 0) + 1
    total = sum(counts.values()) or 1
    percentages = {k: round((v / total) * 100, 2) for k, v in counts.items()}
    return counts, percentages


def technology_evolution(repos):
    # Sort repos by creation date
    sorted_repos = sorted(
        [r for r in repos if r.get("created_at") and r.get("language")],
        key=lambda x: x["created_at"]
    )
    timeline = []
    seen_langs = set()
    for r in sorted_repos:
        lang = r.get("language")
        if lang and lang not in seen_langs:
            date_str = r["created_at"].split("T")[0]
            year = date_str.split("-")[0]
            timeline.append({"year": year, "language": lang, "repo": r.get("name")})
            seen_langs.add(lang)
    return timeline[:5]  # Limit to 5 key milestones


def developer_metrics(profile, repos):
    repo_count = len(repos)
    if repo_count == 0:
        return {
            "impact_score": 0,
            "diversity_index": 0,
            "consistency_score": 0,
            "complexity_level": "Beginner",
            "collaboration_level": "Solo Developer",
            "personality": "Explorer"
        }

    # Impact Score = (stars * 2) + (forks * 3) + (open issues)
    total_stars = sum([r.get("stargazers_count", 0) for r in repos])
    total_forks = sum([r.get("forks_count", 0) for r in repos])
    total_issues = sum([r.get("open_issues_count", 0) for r in repos])
    impact_score = (total_stars * 2) + (total_forks * 3) + total_issues

    # Diversity Index = unique_languages / total_repositories
    counts, _ = language_stats(repos)
    unique_languages = len(counts)
    diversity_index = round((unique_languages / repo_count) * 100, 1)

    # Consistency Score (0-100)
    recent_cutoff = datetime.utcnow() - timedelta(days=90)
    recent_updates = 0
    for r in repos:
        pushed = r.get("pushed_at")
        if pushed:
            dt = datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ")
            if dt >= recent_cutoff:
                recent_updates += 1
    consistency_score = min(100, round((recent_updates / max(1, repo_count)) * 100 + (repo_count / 10 * 5)))

    # Complexity Indicator
    avg_size = sum([r.get("size", 0) for r in repos]) / repo_count
    has_readme_count = sum([1 for r in repos if r.get("description")]) # Proxy for README presence
    complexity_val = (avg_size / 1000) + (unique_languages * 2) + (has_readme_count / repo_count * 10)
    if complexity_val > 50:
        complexity_level = "Advanced"
    elif complexity_val > 20:
        complexity_level = "Intermediate"
    else:
        complexity_level = "Beginner"

    # Collaboration Indicator
    total_watchers = sum([r.get("watchers_count", 0) for r in repos])
    collab_val = total_forks + total_issues + total_watchers
    if collab_val > 100:
        collaboration_level = "Open Source Contributor"
    elif collab_val > 20:
        collaboration_level = "Collaborative Developer"
    else:
        collaboration_level = "Solo Developer"

    # Personality Model
    # Explorer (many languages), Specialist (dominant language), Maintainer (many repos with steady updates),
    # Experimenter (many small repos), Architect (few but complex repos)
    top_lang_pct = 0
    if counts:
        top_lang_count = max(counts.values())
        top_lang_pct = (top_lang_count / repo_count) * 100

    if unique_languages > 5 and diversity_index > 50:
        personality = "Explorer"
    elif top_lang_pct > 70:
        personality = "Specialist"
    elif recent_updates > 5 and repo_count > 15:
        personality = "Maintainer"
    elif avg_size < 500 and repo_count > 10:
        personality = "Experimenter"
    else:
        personality = "Architect"

    return {
        "impact_score": impact_score,
        "diversity_index": diversity_index,
        "consistency_score": consistency_score,
        "complexity_level": complexity_level,
        "collaboration_level": collaboration_level,
        "personality": personality
    }


def developer_dna(profile, repos, metrics):
    followers = profile.get("followers", 0)
    repo_count = len(repos)
    total_stars = sum([repo.get("stargazers_count", 0) for repo in repos])
    total_forks = sum([repo.get("forks_count", 0) for repo in repos])
    counts, _ = language_stats(repos)
    unique_languages = len(counts)

    builder = min(100, repo_count * 2 + total_stars * 0.5)
    collaborator = min(100, followers * 1 + total_forks * 2)
    innovator = min(100, unique_languages * 8 + total_stars * 0.2)
    consistency = metrics["consistency_score"]

    return {
        "Builder": round(builder),
        "Collaborator": round(collaborator),
        "Innovator": round(innovator),
        "Consistency": round(consistency),
    }


def career_role(counts):
    if not counts:
        return "Full Stack Developer"
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    top_langs = [l for l, _ in top[:3]]
    langs_set = set([l.lower() for l in top_langs])
    if ("javascript" in langs_set or "typescript" in langs_set) and ("html" in langs_set or "css" in langs_set):
        return "Frontend Developer"
    if ("python" in langs_set and ("r" in langs_set or "jupyter notebook" in langs_set)) or "r" in langs_set:
        return "Data Scientist"
    if ("go" in langs_set or "rust" in langs_set) and ("shell" in langs_set or "dockerfile" in langs_set or "yaml" in langs_set):
        return "DevOps Engineer"
    if ("javascript" in langs_set or "typescript" in langs_set) and ("python" in langs_set or "java" in langs_set or "c#" in langs_set):
        return "Full Stack Developer"
    if "go" in langs_set or "rust" in langs_set or "java" in langs_set or "c#" in langs_set or "php" in langs_set:
        return "Backend Developer"
    return "Full Stack Developer"


def productivity_pattern(repos):
    hours = []
    days = []
    created_months = []
    for repo in repos:
        pushed = repo.get("pushed_at")
        created = repo.get("created_at")
        if pushed:
            try:
                dt = datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ")
                hours.append(dt.hour)
                days.append(dt.weekday())
            except Exception:
                pass
        if created:
            try:
                cdt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%SZ")
                created_months.append(cdt.strftime("%Y-%m"))
            except Exception:
                pass
    if not hours and not created_months:
        return "Consistent Contributor"
    night = sum(1 for h in hours if h < 5)
    morning = sum(1 for h in hours if 5 <= h < 12)
    weekend = sum(1 for d in days if d >= 5)
    total = max(len(hours), 1)
    month_bursts = 0
    if created_months:
        from collections import Counter
        cnt = Counter(created_months)
        month_bursts = max(cnt.values()) if cnt else 0
    if month_bursts >= 5:
        return "Burst Developer"
    if weekend / total >= 0.5:
        return "Weekend Builder"
    if night / total >= 0.4:
        return "Night Coder"
    if morning / total >= 0.4:
        return "Morning Coder"
    return "Consistent Contributor"


def contribution_heatmap(repos):
    today = datetime.utcnow().date()
    start = today - timedelta(days=34)
    day_counts = {}
    for repo in repos:
        pushed = repo.get("pushed_at")
        if not pushed:
            continue
        try:
            dt = datetime.strptime(pushed, "%Y-%m-%dT%H:%M:%SZ").date()
            if dt >= start:
                day_counts[dt] = day_counts.get(dt, 0) + 1
        except Exception:
            continue
    grid = []
    for i in range(35):
        d = start + timedelta(days=i)
        grid.append(day_counts.get(d, 0))
    if grid:
        mx = max(grid)
        mx = mx if mx > 0 else 1
        grid = [round((v / mx) * 4) for v in grid]
    return grid


def popularity_meter(profile, repos):
    followers = profile.get("followers", 0)
    total_stars = sum([repo.get("stargazers_count", 0) for repo in repos])
    score = followers + total_stars
    level = "Low Popularity"
    if score >= 100:
        level = "High Popularity"
    elif score >= 20:
        level = "Medium Popularity"
    return {"score": score, "level": level}


def innovation_index(repos):
    counts, _ = language_stats(repos)
    unique_languages = len(counts)
    repo_count = len(repos)
    return unique_languages * repo_count


def growth_potential(profile, repos):
    followers = profile.get("followers", 0)
    repo_count = len(repos)
    stars = sum([r.get("stargazers_count", 0) for r in repos])
    score = followers * 0.5 + repo_count * 1.0 + stars * 0.5
    level = "Beginner Developer"
    if score >= 80:
        level = "Advanced Developer"
    elif score >= 30:
        level = "Growing Developer"
    return {"score": round(score), "level": level}


def personality_type(dna, counts):
    innovator = dna.get("Innovator", 0)
    builder = dna.get("Builder", 0)
    collaborator = dna.get("Collaborator", 0)
    consistency = dna.get("Consistency", 0)
    if innovator >= 70 and builder >= 60 and len(counts) >= 5:
        return "Experimental Hacker"
    if builder >= 70 and consistency >= 60:
        return "Project Builder"
    if collaborator >= 70:
        return "Community Leader"
    return "Open Source Explorer"


@app.route("/analyze", methods=["POST"])
def analyze():
    username = request.form.get("github_username", "").strip()
    if not username:
        return jsonify({"success": False, "error": "Please enter a username"}), 400
    profile = fetch_github_profile(username)
    repos = fetch_github_repos(username)
    if profile is None or repos is None:
        return jsonify({"success": False, "error": "GitHub user not found"}), 404

    counts, percentages = language_stats(repos)
    metrics = developer_metrics(profile, repos)
    evolution = technology_evolution(repos)
    dna = developer_dna(profile, repos, metrics)
    role = career_role(counts)
    
    activity = compute_activity_score(profile, repos)
    skill_radar_labels = list(counts.keys())
    skill_radar_values = [counts[k] for k in skill_radar_labels]

    # Use custom Impact Score for top repos
    for r in repos:
        r["impact_score"] = (r.get("stargazers_count", 0) * 2) + (r.get("forks_count", 0) * 3) + r.get("open_issues_count", 0)
    
    top_repos = sorted(repos, key=lambda r: r.get("impact_score", 0), reverse=True)[:6]
    prod_pattern = productivity_pattern(repos)
    heatmap = contribution_heatmap(repos)
    innovation = innovation_index(repos)
    growth = growth_potential(profile, repos)

    insights = []
    if counts:
        most_active_lang = max(counts.items(), key=lambda x: x[1])[0]
        insights.append(f"Strong focus on {most_active_lang} projects.")
        insights.append(f"Most productive language: {most_active_lang}.")
    
    if evolution:
        latest_lang = evolution[-1]["language"]
        insights.append(f"Recent activity shows growing interest in {latest_lang}.")
    
    if metrics["personality"] == "Experimenter":
        insights.append("Developer prefers building small experimental repositories.")
    elif metrics["personality"] == "Specialist":
        insights.append(f"Deep expertise in {most_active_lang or 'their primary language'}.")
    
    if metrics["collaboration_level"] == "Open Source Contributor":
        insights.append("Highly collaborative with significant open-source contributions.")

    data = {
        "profile": {
            "avatar_url": profile.get("avatar_url"),
            "username": profile.get("login"),
            "name": profile.get("name"),
            "bio": profile.get("bio"),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
            "public_repos": profile.get("public_repos", 0),
            "location": profile.get("location", "N/A"),
            "company": profile.get("company", "N/A"),
        },
        "activity_score": activity,
        "dna": dna,
        "career_role": role,
        "skill_radar": {"labels": skill_radar_labels, "values": skill_radar_values},
        "top_repos": [
            {
                "name": r.get("name"),
                "description": r.get("description"),
                "stars": r.get("stargazers_count", 0),
                "language": r.get("language"),
                "html_url": r.get("html_url"),
                "impact_score": r.get("impact_score"),
                "forks": r.get("forks_count", 0),
            }
            for r in top_repos
        ],
        "productivity_pattern": prod_pattern,
        "heatmap": heatmap,
        "innovation_index": innovation,
        "metrics": metrics,
        "evolution": evolution,
        "language_distribution": percentages,
        "growth_potential": growth,
        "insights": insights,
    }

    session["analysis"] = data
    return jsonify({"success": True, "redirect": url_for("dashboard")})


@app.route("/dashboard", methods=["GET"])
def dashboard():
    data = session.get("analysis")
    if not data:
        return redirect(url_for("analyzer"))
    return render_template("dashboard.html", data=data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
