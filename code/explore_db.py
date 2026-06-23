import sqlite3

conn = sqlite3.connect("data/nba_newdb.sqlite")
cursor = conn.cursor()

cursor.execute("""
WITH team_games AS (
    SELECT 
        season_id,
        team_abbreviation_home AS team,
        pts_home AS points,
        reb_home AS rebounds,
        ast_home AS assists
    FROM game

    UNION ALL

    SELECT 
        season_id,
        team_abbreviation_away AS team,
        pts_away AS points,
        reb_away AS rebounds,
        ast_away AS assists
    FROM game
)

SELECT 
    season_id,
    team,
    COUNT(*) AS games_played,
    ROUND(AVG(points), 1) AS avg_points,
    ROUND(AVG(rebounds), 1) AS avg_rebounds,
    ROUND(AVG(assists), 1) AS avg_assists
FROM team_games
WHERE team = 'LAL'
GROUP BY season_id, team
ORDER BY season_id;
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

cursor.execute("""
WITH team_games AS (
    SELECT 
        season_id,
        team_abbreviation_home AS team,
        pts_home AS points
    FROM game

    UNION ALL

    SELECT 
        season_id,
        team_abbreviation_away AS team,
        pts_away AS points
    FROM game
)

SELECT 
    season_id,
    team,
    ROUND(AVG(points), 1) AS avg_points
FROM team_games
WHERE team IN ('LAL', 'GSW')
GROUP BY season_id, team
ORDER BY season_id, team;
""")

rows = cursor.fetchall()

for row in rows:
    print(row)



conn.close()
