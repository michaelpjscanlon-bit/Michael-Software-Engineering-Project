# Imports relevant functions for Database creation and connection to main app 
import os
import sqlite3

# Ensures that a data directory exists so the database file can be stored in it
os.makedirs("data", exist_ok=True)

# Defines the path to the SQLite database file
DB_PATH = os.path.join("data", "nba_stats.db")

# Opens a connection to the SQLite database and creates a cursor for executing SQL
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# --- Base tables ---
# Creates players table with ID, player name, and team
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    team TEXT
);
""")

# Creates awards table to store award types (MVP, DPOY, FMVP, 6MOT)
cursor.execute("""
CREATE TABLE IF NOT EXISTS awards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
);
""")

# --- Award tables ---
# Creates the relevant table to the award with year and player_id referencing players table

# Mvp table
cursor.execute("""
CREATE TABLE IF NOT EXISTS mvp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    player_id INTEGER,
    FOREIGN KEY(player_id) REFERENCES players(id)
);
""")

# Dpoy table
cursor.execute("""
CREATE TABLE IF NOT EXISTS dpoy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    player_id INTEGER,
    FOREIGN KEY(player_id) REFERENCES players(id)
);
""")

# Fmvp table
cursor.execute("""
CREATE TABLE IF NOT EXISTS fmvp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    player_id INTEGER,
    FOREIGN KEY(player_id) REFERENCES players(id)
);
""")

# 6mot table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sixmot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    player_id INTEGER,
    FOREIGN KEY(player_id) REFERENCES players(id)
);
""")

# --- Awards Database Framework ---
# Inserts award names into awards table if they don’t already exist
cursor.execute("INSERT OR IGNORE INTO awards (name) VALUES ('MVP');")
cursor.execute("INSERT OR IGNORE INTO awards (name) VALUES ('DPOY');")
cursor.execute("INSERT OR IGNORE INTO awards (name) VALUES ('FMVP');")
cursor.execute("INSERT OR IGNORE INTO awards (name) VALUES ('6MOT');")

# --- Player Database ---
# Actually populates players table. With the values of IDs, names, and teams
# Uses INSERT OR REPLACE so rerunning script won’t create duplicates
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (1, 'Aaron McKie', 'Philadelphia 76ers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (2, 'Allen Iverson', 'Philadelphia 76ers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (3, 'Alonzo Mourning', 'Miami Heat');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (4, 'Alvin Robertson', 'San Antonio Spurs');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (5, 'Andre Iguodala', 'Golden State Warriors');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (6, 'Antawn Jamison', 'Dallas Mavericks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (7, 'Anthony Mason', 'New York Knicks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (8, 'Ben Gordon', 'Chicago Bulls');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (9, 'Ben Wallace', 'Detroit Pistons');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (10, 'Bill Russell', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (11, 'Bill Walton', 'Portland Trail Blazers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (12, 'Bob Cousy', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (13, 'Bob McAdoo', 'Buffalo Braves');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (14, 'Bob Pettit', 'St. Louis Hawks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (15, 'Bobby Jackson', 'Sacramento Kings');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (16, 'Bobby Jones', 'Philadelphia 76ers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (17, 'Chauncey Billups', 'Detroit Pistons');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (18, 'Charles Barkley', 'Phoenix Suns');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (19, 'Cedric Maxwell', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (20, 'Clifford Robinson', 'Portland Trail Blazers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (21, 'Corliss Williamson', 'Detroit Pistons');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (22, 'Darrell Armstrong', 'Orlando Magic');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (23, 'Danny Manning', 'Phoenix Suns');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (24, 'David Cowens', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (25, 'David Robinson', 'San Antonio Spurs');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (26, 'Dell Curry', 'Charlotte Hornets');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (27, 'Derrick Rose', 'Chicago Bulls');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (28, 'Dennis Johnson', 'Seattle SuperSonics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (29, 'Dennis Rodman', 'Detroit Pistons');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (30, 'Detlef Schrempf', 'Indiana Pacers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (31, 'Dikembe Mutombo', 'Denver Nuggets');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (32, 'Dirk Nowitzki', 'Dallas Mavericks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (33, 'Draymond Green', 'Golden State Warriors');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (34, 'Dwyane Wade', 'Miami Heat');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (35, 'Dwight Howard', 'Orlando Magic');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (36, 'Eddie Johnson', 'Phoenix Suns');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (37, 'Eric Gordon', 'Houston Rockets');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (38, 'Evan Mobley', 'Cleveland Cavaliers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (39, 'Gary Payton', 'Seattle SuperSonics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (40, 'Giannis Antetokounmpo', 'Milwaukee Bucks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (41, 'Hakeem Olajuwon', 'Houston Rockets');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (42, 'Isiah Thomas', 'Detroit Pistons');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (43, 'Jamal Crawford', 'LA Clippers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (44, 'James Harden', 'Houston Rockets');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (45, 'James Worthy', 'Los Angeles Lakers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (46, 'Jason Terry', 'Dallas Mavericks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (47, 'Jaren Jackson Jr.', 'Memphis Grizzlies');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (48, 'Jaylen Brown', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (49, 'Joe Dumars', 'Detroit Pistons');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (50, 'Jerry West', 'Los Angeles Lakers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (51, 'Joakim Noah', 'Chicago Bulls');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (52, 'Joel Embiid', 'Philadelphia 76ers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (53, 'John Havlicek', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (54, 'John Starks', 'New York Knicks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (55, 'Jordan Clarkson', 'Utah Jazz');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (56, 'Julius Erving', 'Philadelphia 76ers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (57, 'JR Smith', 'New York Knicks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (58, 'Kareem Abdul-Jabbar', 'Milwaukee Bucks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (59, 'Karl Malone', 'Utah Jazz');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (60, 'Kawhi Leonard', 'Toronto Raptors');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (61, 'Kevin Durant', 'Oklahoma City Thunder');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (62, 'Kevin Garnett', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (63, 'Kevin McHale', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (64, 'Kobe Bryant', 'Los Angeles Lakers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (65, 'Lamar Odom', 'Los Angeles Lakers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (66, 'Larry Bird', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (67, 'Leandro Barbosa', 'Phoenix Suns');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (68, 'LeBron James', 'Cleveland Cavaliers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (69, 'Lou Williams', 'LA Clippers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (70, 'Magic Johnson', 'Los Angeles Lakers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (71, 'Malcolm Brogdon', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (72, 'Marc Gasol', 'Memphis Grizzlies');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (73, 'Mark Eaton', 'Utah Jazz');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (74, 'Marcus Camby', 'Denver Nuggets');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (75, 'Marcus Smart', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (76, 'Manu Ginobili', 'San Antonio Spurs');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (77, 'Metta World Peace', 'Indiana Pacers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (78, 'Michael Cooper', 'Los Angeles Lakers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (79, 'Michael Jordan', 'Chicago Bulls');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (80, 'Mike Miller', 'Memphis Grizzlies');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (81, 'Montrezl Harrell', 'LA Clippers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (82, 'Moses Malone', 'Philadelphia 76ers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (83, 'Naz Reid', 'Minnesota Timberwolves');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (84, 'Nikola Jokic', 'Denver Nuggets');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (85, 'Oscar Robertson', 'Cincinnati Royals');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (86, 'Paul Pierce', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (87, 'Payton Pritchard', 'Boston Celtics');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (88, 'Ricky Pierce', 'Milwaukee Bucks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (89, 'Rodney Rogers', 'Phoenix Suns');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (90, 'Ron Artest', 'Indiana Pacers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (91, 'Roy Tarpley', 'Dallas Mavericks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (92, 'Rudy Gobert', 'Minnesota Timberwolves');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (93, 'Russell Westbrook', 'Oklahoma City Thunder');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (94, 'Shai Gilgeous-Alexander', 'Oklahoma City Thunder');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (95, 'Shaquille O’Neal', 'Los Angeles Lakers');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (96, 'Sidney Moncrief', 'Milwaukee Bucks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (97, 'Stephen Curry', 'Golden State Warriors');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (98, 'Steve Nash', 'Phoenix Suns');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (99, 'Tim Duncan', 'San Antonio Spurs');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (100, 'Toni Kukoc', 'Chicago Bulls');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (101, 'Tony Parker', 'San Antonio Spurs');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (102, 'Tyler Herro', 'Miami Heat');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (103, 'Tyson Chandler', 'New York Knicks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (104, 'Wes Unseld', 'Washington Bullets');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (105, 'Willis Reed', 'New York Knicks');")
cursor.execute("INSERT OR REPLACE INTO players (id, name, team) VALUES (106, 'Wilt Chamberlain', 'Philadelphia Warriors');")

# --- MVPs Database ---
# Populates MVP table with year and player_id values (all entries link to a player in the larger players table)
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2025, 94);")  # Shai Gilgeous-Alexander
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2024, 84);")  # Nikola Jokic
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2023, 52);")  # Joel Embiid
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2022, 84);")  # Nikola Jokic
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2021, 84);")  # Nikola Jokic
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2020, 40);")  # Giannis Antetokounmpo
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2019, 40);")  # Giannis Antetokounmpo
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2018, 44);")  # James Harden
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2017, 93);")  # Russell Westbrook
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2016, 97);")  # Stephen Curry
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2015, 97);")  # Stephen Curry
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2014, 61);")  # Kevin Durant
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2013, 68);")  # LeBron James
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2012, 68);")  # LeBron James
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2011, 27);")  # Derrick Rose
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2010, 68);")  # LeBron James
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2009, 68);")  # LeBron James
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2008, 64);")  # Kobe Bryant
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2007, 98);")  # Steve Nash
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2006, 98);")  # Steve Nash
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2005, 99);")  # Tim Duncan
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2004, 99);")  # Tim Duncan
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2003, 99);")  # Tim Duncan
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2002, 98);")  # Steve Nash
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2001, 2);")   # Allen Iverson
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (2000, 59);")  # Karl Malone
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1999, 95);")  # Shaquille O’Neal
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1997, 59);")  # Karl Malone
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1996, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1992, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1991, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1990, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1988, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1987, 70);")  # Magic Johnson
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1986, 70);")  # Magic Johnson
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1985, 70);")  # Magic Johnson
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1984, 66);")  # Larry Bird
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1983, 66);")  # Larry Bird
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1982, 66);")  # Larry Bird
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1981, 56);")  # Julius Erving
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1980, 58);")  # Kareem Abdul-Jabbar
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1979, 58);")  # Kareem Abdul-Jabbar
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1977, 58);")  # Kareem Abdul-Jabbar
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1976, 58);")  # Kareem Abdul-Jabbar
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1974, 58);")  # Kareem Abdul-Jabbar
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1971, 58);")  # Kareem Abdul-Jabbar
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1969, 104);") # Wes Unseld
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1967, 106);") # Wilt Chamberlain
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1965, 10);")  # Bill Russell
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1962, 106);") # Wilt Chamberlain
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1958, 14);")  # Bob Pettit
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1957, 10);")  # Bill Russell
cursor.execute("INSERT OR REPLACE INTO mvp (year, player_id) VALUES (1956, 14);")  # Bob Pettit

# --- DPOY Database ---
# Populates DPOY table with year and player_id values (all entries link to a player in the larger players table)
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2025, 38);")  # Evan Mobley
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2024, 92);")  # Rudy Gobert
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2023, 47);")  # Jaren Jackson Jr.
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2022, 75);")  # Marcus Smart
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2021, 92);")  # Rudy Gobert
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2020, 40);")  # Giannis Antetokounmpo
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2019, 92);")  # Rudy Gobert
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2018, 92);")  # Rudy Gobert
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2017, 33);")  # Draymond Green
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2016, 60);")  # Kawhi Leonard
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2015, 60);")  # Kawhi Leonard
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2014, 51);")  # Joakim Noah
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2013, 72);")  # Marc Gasol
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2012, 103);") # Tyson Chandler
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2011, 35);")  # Dwight Howard
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2010, 35);")  # Dwight Howard
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2009, 35);")  # Dwight Howard
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2008, 62);")  # Kevin Garnett
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2007, 74);")  # Marcus Camby
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2006, 9);")   # Ben Wallace
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2005, 9);")   # Ben Wallace
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2004, 77);")  # Metta World Peace
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2003, 9);")   # Ben Wallace
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2002, 9);")   # Ben Wallace
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2001, 31);")  # Dikembe Mutombo
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (2000, 3);")   # Alonzo Mourning
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1999, 3);")   # Alonzo Mourning
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1998, 31);")  # Dikembe Mutombo
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1997, 31);")  # Dikembe Mutombo
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1996, 39);")  # Gary Payton
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1995, 31);")  # Dikembe Mutombo
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1994, 41);")  # Hakeem Olajuwon
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1993, 41);")  # Hakeem Olajuwon
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1992, 25);")  # David Robinson
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1991, 29);")  # Dennis Rodman
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1990, 29);")  # Dennis Rodman
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1989, 73);")  # Mark Eaton
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1988, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1987, 78);")  # Michael Cooper
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1986, 4);")   # Alvin Robertson
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1985, 73);")  # Mark Eaton
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1984, 96);")  # Sidney Moncrief
cursor.execute("INSERT OR REPLACE INTO dpoy (year, player_id) VALUES (1983, 96);")  # Sidney Moncrief

# --- FMVP Database ---
# Populates FMVP table with year and player_id values (all entries link to a player in the larger players table)
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2025, 94);")  # Shai Gilgeous-Alexander
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2024, 48);")  # Jaylen Brown
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2023, 84);")  # Nikola Jokic
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2022, 97);")  # Stephen Curry
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2021, 40);")  # Giannis Antetokounmpo
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2020, 68);")  # LeBron James
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2019, 60);")  # Kawhi Leonard
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2018, 61);")  # Kevin Durant
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2017, 61);")  # Kevin Durant
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2016, 68);")  # LeBron James
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2015, 5);")   # Andre Iguodala
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2014, 60);")  # Kawhi Leonard
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2013, 68);")  # LeBron James
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2012, 68);")  # LeBron James
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2011, 32);")  # Dirk Nowitzki
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2010, 64);")  # Kobe Bryant
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2009, 64);")  # Kobe Bryant
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2008, 86);")  # Paul Pierce
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2007, 101);") # Tony Parker
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2006, 34);")  # Dwyane Wade
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2005, 99);")  # Tim Duncan
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2004, 17);")  # Chauncey Billups
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2003, 99);")  # Tim Duncan
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2002, 95);")  # Shaquille O’Neal
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2001, 2);")   # Allen Iverson
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (2000, 95);")  # Shaquille O’Neal
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1999, 99);")  # Tim Duncan
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1998, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1997, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1996, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1995, 41);")  # Hakeem Olajuwon
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1994, 41);")  # Hakeem Olajuwon
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1993, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1992, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1991, 79);")  # Michael Jordan
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1990, 42);")  # Isiah Thomas
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1989, 49);")  # Joe Dumars
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1988, 45);")  # James Worthy
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1987, 70);")  # Magic Johnson
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1986, 66);")  # Larry Bird
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1985, 58);")  # Kareem Abdul-Jabbar
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1984, 66);")  # Larry Bird
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1983, 82);")  # Moses Malone
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1982, 70);")  # Magic Johnson
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1981, 19);")  # Cedric Maxwell
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1980, 70);")  # Magic Johnson
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1973, 105);") # Willis Reed
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1972, 106);") # Wilt Chamberlain
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1971, 58);")  # Kareem Abdul-Jabbar
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1970, 105);") # Willis Reed
cursor.execute("INSERT OR REPLACE INTO fmvp (year, player_id) VALUES (1969, 50);")  # Jerry West

# --- Sixth Man of the Year Database ---
# Populates 6MOT table with year and player_id values (all entries link to a player in the larger players table)
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2025, 87);")  # Payton Pritchard
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2024, 83);")  # Naz Reid
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2023, 71);")  # Malcolm Brogdon
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2022, 102);") # Tyler Herro
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2021, 55);")  # Jordan Clarkson
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2020, 81);")  # Montrezl Harrell
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2019, 69);")  # Lou Williams
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2018, 69);")  # Lou Williams
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2017, 37);")  # Eric Gordon
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2016, 80);")  # Jamal Crawford
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2015, 80);")  # Jamal Crawford
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2014, 57);")  # JR Smith
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2013, 80);")  # Jamal Crawford
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2012, 44);")  # James Harden
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2011, 69);")  # Lou Williams
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2010, 80);")  # Jamal Crawford
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2009, 69);")  # Lou Williams
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2008, 76);")  # Manu Ginobili
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2007, 67);")  # Leandro Barbosa
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2006, 80);")  # Mike Miller
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2005, 8);")   # Ben Gordon
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2004, 6);")   # Antawn Jamison
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2003, 15);")  # Bobby Jackson
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2002, 21);")  # Corliss Williamson
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2001, 1);")   # Aaron McKie
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (2000, 22);")  # Darrell Armstrong
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1999, 89);")  # Rodney Rogers
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1998, 23);")  # Danny Manning
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1997, 54);")  # John Starks
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1996, 100);") # Toni Kukoc
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1995, 7);")   # Anthony Mason
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1994, 26);")  # Dell Curry
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1993, 20);")  # Clifford Robinson
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1992, 88);")  # Ricky Pierce
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1991, 30);")  # Detlef Schrempf
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1990, 91);")  # Roy Tarpley
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1989, 36);")  # Eddie Johnson
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1988, 63);")  # Kevin McHale
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1987, 88);")  # Ricky Pierce
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1986, 11);")  # Bill Walton
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1985, 63);")  # Kevin McHale
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1984, 63);")  # Kevin McHale
cursor.execute("INSERT OR REPLACE INTO sixmot (year, player_id) VALUES (1983, 16);")  # Bobby Jones

# Commits all changes to the databse and saves it, then closes the database connection
conn.commit()
conn.close()

print(f"Database created/updated at: {DB_PATH}")

