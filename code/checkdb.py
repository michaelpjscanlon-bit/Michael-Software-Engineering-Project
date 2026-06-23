#NOTE: THIS IS JUST A DIAGNOSTICS CHECKER, NOT A RELEVANT PART OF THE WORKING APP 

# Imports SQLAlchemy engine creator
from sqlalchemy import create_engine

# Connects to SQLite database file with threading option disabled
engine = create_engine('sqlite:////home/myproject/data/nba_stats.db', connect_args={"check_same_thread": False})

# Defines database filename for local checks
db = "nba_stats.db"

# Prints current working directory (cwd) to confirm where script is running
print("cwd:", os.getcwd())

# Checks if database file exists in cwd
print("exists:", os.path.exists(db))

# Opens direct SQLite connection to the database file
conn = sqlite3.connect(db)
cur = conn.cursor()

# Lists all tables currently in the database
cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("tables:", cur.fetchall())

# Tries to count rows in players table then prints error if table missing
try:
    cur.execute("SELECT COUNT(*) FROM players;")
    print("players count:", cur.fetchone()[0])
except Exception as e:
    print("players error:", e)

# Tries to query MVP table joined with players and shows 5 most recent rows
try:
    cur.execute("""
    SELECT mvp.year, players.name, players.team
    FROM mvp
    JOIN players ON mvp.player_id = players.id
    ORDER BY mvp.year DESC
    LIMIT 5;
    """)
    print("sample mvp rows:", cur.fetchall())
except Exception as e:
    print("mvp join error:", e)

# Shell command to show current working directory in terminal
pwd

# Another shell command to print first 40 lines of app.py to verify create_engine line
sed -n '1,120p' /path/to/your/app.py | sed -n '1,40p'
# Alternative: open app.py in an editor

# Closes SQLite connection cleanly
conn.close()

