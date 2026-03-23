import sqlite3
import json
from datetime import datetime

DATABASE_NAME = "profiles.db"

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            impact_score INTEGER,
            diversity_index REAL,
            consistency_score INTEGER,
            personality TEXT,
            career_role TEXT,
            innovation_index INTEGER,
            top_language TEXT,
            raw_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_analysis(username, data):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    # Extract key metrics for structured SQL queries
    metrics = data.get("metrics", {})
    percentages = data.get("language_distribution", {})
    top_lang = max(percentages.items(), key=lambda x: x[1])[0] if percentages else "N/A"
    
    c.execute('''
        INSERT INTO analyses (
            username, impact_score, diversity_index, consistency_score, 
            personality, career_role, innovation_index, top_language, raw_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        username,
        metrics.get("impact_score", 0),
        metrics.get("diversity_index", 0.0),
        metrics.get("consistency_score", 0),
        metrics.get("personality", "Unknown"),
        data.get("career_role", "Unknown"),
        data.get("innovation_index", 0),
        top_lang,
        json.dumps(data)
    ))
    conn.commit()
    conn.close()

def get_sql_insights(username):
    """
    The 'SQL Oracle' - Performs novel comparative analytics using pure SQL window functions
    to provide insights not possible with simple Python aggregations.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get total count
    c.execute("SELECT COUNT(*) FROM analyses")
    total_users = c.fetchone()[0]
    
    if total_users <= 1:
        return {
            "rank_percentile": 100,
            "comparison_text": "You are the first to be analyzed in this session!",
            "global_avg_impact": 0,
            "rare_language_status": "N/A"
        }

    # Complex SQL Query: Global Rank Percentile & Comparison
    # Using Subqueries and Aggregations to find the user's relative standing
    query = '''
        WITH GlobalStats AS (
            SELECT 
                AVG(impact_score) as avg_impact,
                AVG(innovation_index) as avg_innovation,
                (SELECT COUNT(*) FROM analyses WHERE impact_score > (SELECT impact_score FROM analyses WHERE username = ? ORDER BY created_at DESC LIMIT 1)) as higher_ranked
            FROM analyses
        ),
        UserStats AS (
            SELECT impact_score, top_language
            FROM analyses 
            WHERE username = ? 
            ORDER BY created_at DESC LIMIT 1
        )
        SELECT 
            gs.avg_impact,
            gs.avg_innovation,
            gs.higher_ranked,
            us.impact_score,
            us.top_language,
            (SELECT COUNT(*) FROM analyses WHERE top_language = us.top_language) as lang_popularity
        FROM GlobalStats gs, UserStats us
    '''
    
    c.execute(query, (username, username))
    row = c.fetchone()
    
    if not row:
        return None
        
    rank_percentile = round(((total_users - row['higher_ranked']) / total_users) * 100, 1)
    
    # Rare Language Check: Is your top language rare in the database?
    lang_popularity_pct = (row['lang_popularity'] / total_users) * 100
    rare_status = "Rare Specialist" if lang_popularity_pct < 20 else "Mainstream Developer"
    
    comparison_text = f"Your impact score is {round(row['impact_score'] - row['avg_impact'], 1)} points {'above' if row['impact_score'] >= row['avg_impact'] else 'below'} the global average."
    
    conn.close()
    
    return {
        "rank_percentile": rank_percentile,
        "comparison_text": comparison_text,
        "global_avg_impact": round(row['avg_impact'], 1),
        "rare_language_status": rare_status,
        "total_analyzed": total_users
    }
