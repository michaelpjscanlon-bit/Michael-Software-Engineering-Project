from flask import Flask, render_template, url_for, request, abort, redirect, session, flash
from sqlalchemy import create_engine, text
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from functools import lru_cache, wraps
import os

import csv
import sqlite3
import unicodedata

app = Flask(__name__)
app.secret_key = "nba-stats-project-secret-key"

BASE_DIR = Path(__file__).resolve().parent

AWARDS_DB = BASE_DIR / "data" / "nba_stats.db"
NBA_DB = BASE_DIR / "data" / "nba_newdb.sqlite"

AUTH_FOLDER = Path(os.environ.get("LOCALAPPDATA", BASE_DIR)) / "NBAStatsHub"
AUTH_FOLDER.mkdir(parents=True, exist_ok=True)

AUTH_DB = AUTH_FOLDER / "users.db"

PLAYER_CSV = BASE_DIR / "data" / "player_data" / "Player Per Game.csv"
TEAM_ABBREV_CSV = BASE_DIR / "data" / "player_data" / "Team Abbrev.csv"
ALL_STAR_CSV = BASE_DIR / "data" / "player_data" / "All-Star Selections.csv"
AWARD_SHARES_CSV = BASE_DIR / "data" / "player_data" / "Player Award Shares.csv"
CAREER_INFO_CSV = BASE_DIR / "data" / "player_data" / "Player Career Info.csv"
DRAFT_HISTORY_CSV = BASE_DIR / "data" / "player_data" / "Draft Pick History.csv"

PLAYER_IMAGE_FOLDER = BASE_DIR / "static" / "images" / "players"
DEFAULT_PLAYER_IMAGE = "images/players/default_player.png"

award_engine = create_engine(
    f"sqlite:///{AWARDS_DB}",
    connect_args={"check_same_thread": False}
)

nba_engine = create_engine(
    f"sqlite:///{NBA_DB}",
    connect_args={"check_same_thread": False}
)

POSITION_LABELS = {
    "PG": "Point Guard",
    "SG": "Shooting Guard",
    "SF": "Small Forward",
    "PF": "Power Forward",
    "C": "Center",
    "G": "Guard",
    "F": "Forward"
}

NBA_TEAM_ABBREVIATIONS = {
    "ATL": "Atlanta Hawks",
    "BOS": "Boston Celtics",
    "BRK": "Brooklyn Nets",
    "BKN": "Brooklyn Nets",
    "CHH": "Charlotte Hornets",
    "CHO": "Charlotte Hornets",
    "CHA": "Charlotte Hornets",
    "CHI": "Chicago Bulls",
    "CLE": "Cleveland Cavaliers",
    "DAL": "Dallas Mavericks",
    "DEN": "Denver Nuggets",
    "DET": "Detroit Pistons",
    "GSW": "Golden State Warriors",
    "HOU": "Houston Rockets",
    "IND": "Indiana Pacers",
    "LAC": "LA Clippers",
    "LAL": "Los Angeles Lakers",
    "MEM": "Memphis Grizzlies",
    "MIA": "Miami Heat",
    "MIL": "Milwaukee Bucks",
    "MIN": "Minnesota Timberwolves",
    "NOP": "New Orleans Pelicans",
    "NOH": "New Orleans Hornets",
    "NOK": "New Orleans/Oklahoma City Hornets",
    "NYK": "New York Knicks",
    "OKC": "Oklahoma City Thunder",
    "ORL": "Orlando Magic",
    "PHI": "Philadelphia 76ers",
    "PHO": "Phoenix Suns",
    "POR": "Portland Trail Blazers",
    "SAC": "Sacramento Kings",
    "SAS": "San Antonio Spurs",
    "TOR": "Toronto Raptors",
    "UTA": "Utah Jazz",
    "WAS": "Washington Wizards",

    # Historical NBA teams
    "SEA": "Seattle SuperSonics",
    "VAN": "Vancouver Grizzlies",
    "NJN": "New Jersey Nets",
    "WSB": "Washington Bullets",
    "BAL": "Baltimore Bullets",
    "CAP": "Capital Bullets",
    "CIN": "Cincinnati Royals",
    "KCK": "Kansas City Kings",
    "KCO": "Kansas City-Omaha Kings",
    "MNL": "Minneapolis Lakers",
    "SDC": "San Diego Clippers",
    "SDR": "San Diego Rockets",
    "SFW": "San Francisco Warriors",
    "PHW": "Philadelphia Warriors",
    "STL": "St. Louis Hawks",
    "SYR": "Syracuse Nationals",
    "FTW": "Fort Wayne Pistons",
    "ROC": "Rochester Royals",
    "NOJ": "New Orleans Jazz",
    "CHP": "Chicago Packers",
    "CHZ": "Chicago Zephyrs",
    "TRI": "Tri-Cities Blackhawks"
}

NBA_FULL_TEAM_NAMES = set(NBA_TEAM_ABBREVIATIONS.values())


def get_auth_connection():
    conn = sqlite3.connect(AUTH_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db():
    with get_auth_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        conn.commit()


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to access this page.")
            return redirect(url_for("login"))

        return route_function(*args, **kwargs)

    return wrapper


AUTH_DB.parent.mkdir(parents=True, exist_ok=True)
init_auth_db()

@lru_cache(maxsize=1)
def load_player_team_by_season_lookup():
    lookup = {}

    for row in load_player_per_game_rows():
        player_id = row.get("player_id", "")
        player_name = normalize_name(row.get("player"))
        season = str(row.get("season") or "")
        season_year = str(season_sort_value(season))
        team_code = row.get("team") or row.get("tm")

        if not team_code or not season:
            continue

        games = safe_int(row.get("g"))

        is_combined_team_row = (
            team_code in ["TOT", "2TM", "3TM", "4TM"] or str(team_code).endswith("TM")
        )

        rank = (
            1 if is_combined_team_row else 0,
            games
        )

        team_name = full_team_name(team_code, season)

        player_keys = []

        if player_id:
            player_keys.append(("id", player_id))

        if player_name:
            player_keys.append(("name", player_name))

        season_keys = [season]

        if season_year and season_year != "0":
            season_keys.append(season_year)

        for player_key_type, player_key_value in player_keys:
            for season_key in season_keys:
                lookup_key = (player_key_type, player_key_value, season_key)

                if lookup_key not in lookup or rank > lookup[lookup_key]["rank"]:
                    lookup[lookup_key] = {
                        "team": team_name,
                        "rank": rank
                    }

    return {
        key: value["team"]
        for key, value in lookup.items()
    }


def get_player_team_for_award_season(player_id, player_name, award_season):
    lookup = load_player_team_by_season_lookup()

    exact_season = str(award_season or "")
    season_year = str(season_sort_value(award_season))
    normalized_player_name = normalize_name(player_name)

    possible_keys = []

    if player_id:
        possible_keys.append(("id", player_id, exact_season))
        possible_keys.append(("id", player_id, season_year))

    if normalized_player_name:
        possible_keys.append(("name", normalized_player_name, exact_season))
        possible_keys.append(("name", normalized_player_name, season_year))

    for key in possible_keys:
        if key in lookup:
            return lookup[key]

    return "Unknown"

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def safe_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def safe_int_or_none(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def season_sort_value(season):
    try:
        return int(str(season)[:4])
    except (TypeError, ValueError):
        return 0


def read_csv_file(path):
    if not path.exists():
        return []

    with open(path, newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def normalize_name(name):
    text = str(name or "")
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()

    # Remove punctuation that causes database/CSV matching issues
    text = text.replace("'", "")
    text = text.replace("’", "")
    text = text.replace(".", "")
    text = text.replace("-", " ")

    return " ".join(text.split())


def image_filename_name(name):
    return normalize_name(name).replace(" ", "_")


def get_player_image_url(player_id, player_name):
    safe_image_name = image_filename_name(player_name)

    possible_filenames = [
        f"{player_id}.png",
        f"{player_id}.jpg",
        f"{safe_image_name}.png",
        f"{safe_image_name}.jpg"
    ]

    for filename in possible_filenames:
        image_path = PLAYER_IMAGE_FOLDER / filename

        if image_path.exists():
            return url_for("static", filename=f"images/players/{filename}")

    return url_for("static", filename=DEFAULT_PLAYER_IMAGE)


def full_position_name(position):
    if not position:
        return ""

    parts = str(position).split("-")
    full_parts = [POSITION_LABELS.get(part, part) for part in parts]

    return " / ".join(full_parts)


def yes_no_filter_matches(filter_value, actual_value):
    if filter_value == "yes" and not actual_value:
        return False

    if filter_value == "no" and actual_value:
        return False

    return True


def safe_number_filter(value):
    value = str(value or "").strip()[:6]

    if not value:
        return ""

    try:
        float(value)
        return value
    except ValueError:
        return ""


def height_matches(height_inches, height_filter):
    if not height_filter:
        return True

    if height_inches is None:
        return False

    if height_filter == "under_72":
        return height_inches < 72

    if height_filter == "72_76":
        return 72 <= height_inches <= 76

    if height_filter == "77_80":
        return 77 <= height_inches <= 80

    if height_filter == "81_plus":
        return height_inches >= 81

    return True


def format_height(height_inches):
    if height_inches is None:
        return "Unknown"

    feet = height_inches // 12
    inches = height_inches % 12

    return f"{feet}'{inches}\""


def weighted_average(rows, column_name):
    total_games = 0
    weighted_total = 0

    for row in rows:
        games = safe_int(row.get("g"))
        value = safe_float(row.get(column_name))

        if games > 0 and value is not None:
            total_games += games
            weighted_total += value * games

    if total_games == 0:
        return None

    return round(weighted_total / total_games, 1)


@lru_cache(maxsize=1)
def load_team_name_lookup():
    team_by_season = {}
    latest_team_name = {}

    for row in read_csv_file(TEAM_ABBREV_CSV):
        if row.get("lg") != "NBA":
            continue

        abbreviation = row.get("abbreviation", "").strip()
        team_name = row.get("team", "").strip()
        season = row.get("season", "").strip()
        season_year = season_sort_value(season)

        if not abbreviation or not team_name:
            continue

        team_by_season[(season, abbreviation)] = team_name

        if abbreviation not in latest_team_name:
            latest_team_name[abbreviation] = {
                "season_year": season_year,
                "team_name": team_name
            }
        elif season_year > latest_team_name[abbreviation]["season_year"]:
            latest_team_name[abbreviation] = {
                "season_year": season_year,
                "team_name": team_name
            }

    latest_team_name = {
        abbreviation: info["team_name"]
        for abbreviation, info in latest_team_name.items()
    }

    return team_by_season, latest_team_name


def full_team_name(team_abbreviation, season=None):
    team_abbreviation = str(team_abbreviation or "").strip()

    if team_abbreviation in ["TOT", "2TM", "3TM", "4TM"]:
        return "Multiple teams"

    team_by_season, latest_team_name = load_team_name_lookup()

    if season and (str(season), team_abbreviation) in team_by_season:
        return team_by_season[(str(season), team_abbreviation)]

    if team_abbreviation in latest_team_name:
        return latest_team_name[team_abbreviation]

    if team_abbreviation in NBA_TEAM_ABBREVIATIONS:
        return NBA_TEAM_ABBREVIATIONS[team_abbreviation]

    return team_abbreviation


@lru_cache(maxsize=1)
def load_player_per_game_rows():
    rows = []

    with open(PLAYER_CSV, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row.get("lg") != "NBA":
                continue

            if "team" not in row and "tm" in row:
                row["team"] = row["tm"]

            rows.append(row)

    return rows

@lru_cache(maxsize=1)
def get_player_profile_id_lookup():
    lookup = {}

    for row in load_player_per_game_rows():
        player_id = row.get("player_id")
        player_name = row.get("player")

        if not player_id or not player_name:
            continue

        normalized = normalize_name(player_name)

        if normalized not in lookup:
            lookup[normalized] = player_id

    return lookup


def get_award_rows(table_name, q=None):
    q = str(q or "").strip()[:50]
    player_profile_lookup = get_player_profile_id_lookup()

    sql = f"""
        SELECT {table_name}.year AS year, players.name AS name, players.team AS team
        FROM {table_name}
        JOIN players ON {table_name}.player_id = players.id
    """

    params = {}

    if q:
        sql += f" WHERE players.name LIKE :q OR CAST({table_name}.year AS TEXT) LIKE :q"
        params["q"] = f"%{q}%"

    sql += f" ORDER BY {table_name}.year DESC"

    with award_engine.connect() as conn:
        raw_rows = conn.execute(text(sql), params).fetchall()

    rows = []

    for row in raw_rows:
        data = row._mapping
        player_name = data["name"]
        profile_player_id = player_profile_lookup.get(normalize_name(player_name))

        rows.append({
            "year": data["year"],
            "name": player_name,
            "team": data["team"],
            "profile_player_id": profile_player_id
        })

    return rows

@lru_cache(maxsize=32)
def get_csv_award_rows(award_code, q=None):
    q = str(q or "").strip()[:50]
    q_normalized = normalize_name(q)

    player_profile_lookup = get_player_profile_id_lookup()

    rows = []

    for row in read_csv_file(AWARD_SHARES_CSV):
        award = str(row.get("award", "")).strip().lower()
        winner_value = str(row.get("winner", "")).strip().lower()
        winner = winner_value in ["true", "1", "yes", "y"]

        if award != award_code or not winner:
            continue

        player_name = row.get("player", "")
        player_id = row.get("player_id", "")
        year = row.get("season") or row.get("year") or ""

        if q:
            if q_normalized not in normalize_name(player_name) and q not in str(year):
                continue

        profile_player_id = player_id or player_profile_lookup.get(normalize_name(player_name))

        team = get_player_team_for_award_season(
            profile_player_id,
            player_name,
            year
        )

        rows.append({
            "year": year,
            "name": player_name,
            "team": team,
            "profile_player_id": profile_player_id
        })

    rows.sort(
        key=lambda item: season_sort_value(item["year"]),
        reverse=True
    )

    return rows

@lru_cache(maxsize=1)
def load_all_star_player_ids():
    all_star_ids = set()

    for row in read_csv_file(ALL_STAR_CSV):
        if row.get("lg") == "NBA" and row.get("player_id"):
            all_star_ids.add(row["player_id"])

    return all_star_ids


@lru_cache(maxsize=1)
def load_award_share_winners():
    award_codes = {
        "mvp": "nba mvp",
        "dpoy": "nba dpoy",
        "sixmot": "nba smoy",
        "roty": "nba roy"
    }

    winners = {
        "mvp": set(),
        "dpoy": set(),
        "sixmot": set(),
        "roty": set()
    }

    for row in read_csv_file(AWARD_SHARES_CSV):
        award = str(row.get("award", "")).strip().lower()
        player_id = row.get("player_id", "")
        winner_value = str(row.get("winner", "")).strip().lower()
        winner = winner_value in ["true", "1", "yes", "y"]

        if not player_id or not winner:
            continue

        for filter_name, award_code in award_codes.items():
            if award == award_code:
                winners[filter_name].add(player_id)

    return winners


@lru_cache(maxsize=1)
def load_existing_award_db_winners():
    winners = {
        "mvp": set(),
        "dpoy": set(),
        "fmvp": set(),
        "sixmot": set()
    }

    award_tables = {
        "mvp": "mvp",
        "dpoy": "dpoy",
        "fmvp": "fmvp",
        "sixmot": "sixmot"
    }

    try:
        with award_engine.connect() as conn:
            for award_key, table_name in award_tables.items():
                rows = conn.execute(
                    text(f"""
                        SELECT players.name
                        FROM {table_name}
                        JOIN players ON {table_name}.player_id = players.id
                    """)
                ).fetchall()

                for row in rows:
                    winners[award_key].add(normalize_name(row[0]))
    except Exception:
        pass

    return winners


@lru_cache(maxsize=1)
def load_award_years_by_player():
    award_years = {
        "MVP": {},
        "DPOY": {},
        "FMVP": {},
        "6MOT": {},
        "ROTY": {},
        "All-Star": {}
    }

    award_tables = {
        "MVP": "mvp",
        "DPOY": "dpoy",
        "FMVP": "fmvp",
        "6MOT": "sixmot"
    }

    try:
        with award_engine.connect() as conn:
            for award_name, table_name in award_tables.items():
                rows = conn.execute(
                    text(f"""
                        SELECT players.name, {table_name}.year
                        FROM {table_name}
                        JOIN players ON {table_name}.player_id = players.id
                    """)
                ).fetchall()

                for player_name, year in rows:
                    normalized = normalize_name(player_name)

                    if normalized not in award_years[award_name]:
                        award_years[award_name][normalized] = []

                    award_years[award_name][normalized].append(year)
    except Exception:
        pass

    for row in read_csv_file(AWARD_SHARES_CSV):
        award = str(row.get("award", "")).strip().lower()
        player_id = row.get("player_id")
        winner_value = str(row.get("winner", "")).strip().lower()
        winner = winner_value in ["true", "1", "yes", "y"]

        if not player_id or not winner:
            continue

        season = row.get("season") or row.get("year") or ""

        if award == "nba roy":
            if player_id not in award_years["ROTY"]:
                award_years["ROTY"][player_id] = []

            award_years["ROTY"][player_id].append(season)

    for row in read_csv_file(ALL_STAR_CSV):
        if row.get("lg") != "NBA":
            continue

        player_id = row.get("player_id")
        season = row.get("season") or row.get("year") or ""

        if not player_id:
            continue

        if player_id not in award_years["All-Star"]:
            award_years["All-Star"][player_id] = []

        award_years["All-Star"][player_id].append(season)

    return award_years


@lru_cache(maxsize=1)
def load_career_info():
    career_info = {}

    for row in read_csv_file(CAREER_INFO_CSV):
        player_id = row.get("player_id")

        if not player_id:
            continue

        career_info[player_id] = {
            "height": safe_int_or_none(row.get("ht_in_in")),
            "hof": str(row.get("hof", "")).upper() == "TRUE",
            "from": row.get("from"),
            "to": row.get("to")
        }

    return career_info


@lru_cache(maxsize=1)
def load_draft_info():
    draft_info = {}

    for row in read_csv_file(DRAFT_HISTORY_CSV):
        if row.get("lg") != "NBA":
            continue

        player_id = row.get("player_id")

        if not player_id:
            continue

        draft_info[player_id] = {
            "draft_class": row.get("season"),
            "draft_team": full_team_name(row.get("tm"), row.get("season")),
            "overall_pick": row.get("overall_pick")
        }

    return draft_info


def choose_best_rows_for_player(player_id):
    all_rows = load_player_per_game_rows()
    best_rows = {}

    for row in all_rows:
        if row.get("player_id") != player_id:
            continue

        season = row.get("season")

        if not season:
            continue

        team = row.get("team", "")
        games = safe_int(row.get("g"))
        is_combined_team_row = team in ["TOT", "2TM", "3TM", "4TM"] or team.endswith("TM")
        row_rank = (1 if is_combined_team_row else 0, games)

        if season not in best_rows or row_rank > best_rows[season]["rank"]:
            best_rows[season] = {
                "row": row,
                "rank": row_rank
            }

    selected_rows = [item["row"] for item in best_rows.values()]
    selected_rows.sort(key=lambda row: season_sort_value(row.get("season")))

    return selected_rows


def get_player_award_summary(player_id, player_name):
    award_years = load_award_years_by_player()
    normalized_name = normalize_name(player_name)
    awards = []

    for award_name in ["MVP", "DPOY", "FMVP", "6MOT"]:
        years = award_years.get(award_name, {}).get(normalized_name, [])

        if years:
            awards.append({
                "name": award_name,
                "count": len(years),
                "years": sorted(years)
            })

    roty_years = award_years.get("ROTY", {}).get(player_id, [])

    if roty_years:
        awards.append({
            "name": "ROTY",
            "count": len(roty_years),
            "years": sorted(roty_years)
        })

    all_star_years = award_years.get("All-Star", {}).get(player_id, [])

    if all_star_years:
        awards.append({
            "name": "All-Star",
            "count": len(all_star_years),
            "years": sorted(all_star_years)
        })

    return awards


def build_player_profile(player_id):
    selected_rows = choose_best_rows_for_player(player_id)

    if not selected_rows:
        return None

    latest_row = selected_rows[-1]
    first_row = selected_rows[0]
    player_name = latest_row.get("player", "Unknown Player")
    career_info = load_career_info().get(player_id, {})
    draft_info = load_draft_info().get(player_id, {})
    career_games = sum(safe_int(row.get("g")) for row in selected_rows)

    latest_stats = {
        "season": latest_row.get("season"),
        "games": safe_int(latest_row.get("g")),
        "points": safe_float(latest_row.get("pts_per_game")),
        "rebounds": safe_float(latest_row.get("trb_per_game")),
        "assists": safe_float(latest_row.get("ast_per_game")),
        "fg_percent": safe_float(latest_row.get("fg_percent")),
        "three_percent": safe_float(latest_row.get("x3p_percent")),
        "ft_percent": safe_float(latest_row.get("ft_percent")),
        "minutes": safe_float(latest_row.get("mp_per_game"))
    }

    career_stats = {
        "games": career_games,
        "points": weighted_average(selected_rows, "pts_per_game"),
        "rebounds": weighted_average(selected_rows, "trb_per_game"),
        "assists": weighted_average(selected_rows, "ast_per_game"),
        "fg_percent": weighted_average(selected_rows, "fg_percent"),
        "three_percent": weighted_average(selected_rows, "x3p_percent"),
        "ft_percent": weighted_average(selected_rows, "ft_percent"),
        "minutes": weighted_average(selected_rows, "mp_per_game")
    }

    seasons = []

    for row in selected_rows:
        seasons.append({
            "season": row.get("season"),
            "team": full_team_name(row.get("team"), row.get("season")),
            "age": row.get("age"),
            "games": row.get("g"),
            "points": row.get("pts_per_game"),
            "rebounds": row.get("trb_per_game"),
            "assists": row.get("ast_per_game"),
            "fg_percent": row.get("fg_percent"),
            "three_percent": row.get("x3p_percent"),
            "ft_percent": row.get("ft_percent"),
            "minutes": row.get("mp_per_game")
        })

    return {
        "player_id": player_id,
        "name": player_name,
        "image_url": get_player_image_url(player_id, player_name),
        "position": full_position_name(latest_row.get("pos")),
        "team": full_team_name(latest_row.get("team"), latest_row.get("season")),
        "first_season": first_row.get("season"),
        "last_season": latest_row.get("season"),
        "age": latest_row.get("age"),
        "height": format_height(career_info.get("height")),
        "hof": career_info.get("hof", False),
        "draft_class": draft_info.get("draft_class", "Unknown"),
        "draft_team": draft_info.get("draft_team", "Unknown"),
        "overall_pick": draft_info.get("overall_pick", "Unknown"),
        "awards": get_player_award_summary(player_id, player_name),
        "latest_stats": latest_stats,
        "career_stats": career_stats,
        "seasons": seasons
    }

@app.route('/players')
@login_required
def player_search_page():
    search = request.args.get("q", "").strip()[:50]
    search_normalized = normalize_name(search)

    all_rows = load_player_per_game_rows()
    player_summary = {}

    for row in all_rows:
        player_id = row.get("player_id")
        player_name = row.get("player")
        season = row.get("season")

        if not player_id or not player_name or not season:
            continue

        season_year = season_sort_value(season)

        if player_id not in player_summary:
            player_summary[player_id] = {
                "player_id": player_id,
                "name": player_name,
                "first_season": season,
                "last_season": season,
                "first_year_value": season_year,
                "last_year_value": season_year,
                "team": full_team_name(row.get("team"), season),
                "position": full_position_name(row.get("pos")),
                "age": row.get("age"),
                "image_url": get_player_image_url(player_id, player_name)
            }

        current_first = player_summary[player_id]["first_year_value"]
        current_last = player_summary[player_id]["last_year_value"]

        if season_year and (not current_first or season_year < current_first):
            player_summary[player_id]["first_season"] = season
            player_summary[player_id]["first_year_value"] = season_year

        if season_year and (not current_last or season_year > current_last):
            player_summary[player_id]["last_season"] = season
            player_summary[player_id]["last_year_value"] = season_year
            player_summary[player_id]["team"] = full_team_name(row.get("team"), season)
            player_summary[player_id]["position"] = full_position_name(row.get("pos"))
            player_summary[player_id]["age"] = row.get("age")

    player_name_options = sorted(
        info["name"]
        for info in player_summary.values()
    )

    matching_players = []

    if search_normalized:
        for info in player_summary.values():
            if search_normalized in normalize_name(info["name"]):
                matching_players.append(info)

    matching_players = sorted(
        matching_players,
        key=lambda player: player["name"]
    )[:80]

    return render_template(
        "players.html",
        search=search,
        players=matching_players,
        player_name_options=player_name_options,
        result_count=len(matching_players)
    )

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/MVP')
def mvp():
    q = request.args.get("q")

    rows = get_award_rows("mvp", q)

    image = url_for('static', filename='images/Screenshot 2025-12-05 134133.png')
    description = "This is an award given to the player who has had the most successful regular NBA season. This could be individual success, such as Russel Westbrooks 2017 season. Or potentially team success such as the most recent MVP, Shai Gilgeous-Alexander. The MVP award itself is namely dubbed the Michael Jordan Trophy. Given the historic 6 MVPs Michael Jordan won throughout his career. This list itself displays the MVP winners by year, with team and season."

    return render_template('award.html', title="MVPs of The NBA", rows=rows, image=image, description=description, q=q)

@app.route('/DPOY')
def dpoy():
    q = request.args.get("q")

    rows = get_award_rows("dpoy", q)

    image = url_for('static', filename='images/Screenshot 2025-12-05 095326.png')
    description = "Defense in the NBA is half the game! So its important to acknowledge the players that really excel at defense. Whether it’s anchoring an all time defense along with their team or holding a great singular defensive presence that gives the other team headaches. Its notably named the Hakeem Olajuwan trophy, which makes sense as players at the center position often win this a lot more frequently. This list displays the DPOY winners by year, with team and season."

    return render_template('award.html', title="DPOYs of The NBA", rows=rows, image=image, description=description, q=q)


@app.route('/FMVP')
def fmvp():
    q = request.args.get("q")

    rows = get_award_rows("fmvp", q)

    image = url_for('static', filename='images/Screenshot 2025-12-05 134833.png')
    description = "Whenever a team wins a championship, there’s normally a player who is spearheading that team to victory. This player then receives the Bill Russel trophy after the Celtics player who has won the NBA championship itself 11 times! A player on the losing team on the finals can also receive it, however it is not very common and has only happened once and was appointed to Jerry West in 1969."

    return render_template('award.html', title="FMVPs of The NBA", rows=rows, image=image, description=description, q=q)


@app.route('/6MOT')
def sixth_mot():
    q = request.args.get("q")

    rows = get_award_rows("sixmot", q)

    image = url_for('static', filename='images/Screenshot 2025-12-05 135307.png')
    description = "Obviously an NBA team doesn’t just consist of 5 players, there’s the backup bench unit as well. The Sixth Man of the Year goes to the most valuable player on the bench of a team. Essentially an MVP for the players who dont start."

    return render_template('award.html', title="6MOT of The NBA", rows=rows, image=image, description=description, q=q)

@app.route('/ROTY')
def roty():
    q = request.args.get("q")

    rows = get_csv_award_rows("nba roy", q)

    image = url_for('static', filename='images/Screenshot 2026-06-23 020917.png')

    description = (
        "The Rookie of the Year award recognises the best first-year player in an NBA season. "
        "This page displays ROTY winners using the Player Award Shares CSV dataset, with player "
        "names linked to their individual profile pages where matching player data is available."
    )

    return render_template(
        'award.html',
        title="ROTYs of The NBA",
        rows=rows,
        image=image,
        description=description,
        q=q
    )

@app.route('/graphs')
@login_required
def graphs():
    selected_team = request.args.get("team", "Los Angeles Lakers")
    compare_team = request.args.get("compare_team", "")
    selected_stat = request.args.get("stat", "avg_points")
    chart_type = request.args.get("chart_type", "line")

    if chart_type not in ["line", "bar"]:
        chart_type = "line"

    stat_options = {
        "avg_points": {"label": "Average Points Per Game", "home_expr": "g.pts_home", "away_expr": "g.pts_away", "aggregate_sql": "ROUND(AVG(CAST(stat_value AS REAL)), 1)"},
        "avg_rebounds": {"label": "Average Rebounds Per Game", "home_expr": "g.reb_home", "away_expr": "g.reb_away", "aggregate_sql": "ROUND(AVG(CAST(stat_value AS REAL)), 1)"},
        "avg_assists": {"label": "Average Assists Per Game", "home_expr": "g.ast_home", "away_expr": "g.ast_away", "aggregate_sql": "ROUND(AVG(CAST(stat_value AS REAL)), 1)"},
        "avg_blocks": {"label": "Average Blocks Per Game", "home_expr": "g.blk_home", "away_expr": "g.blk_away", "aggregate_sql": "ROUND(AVG(CAST(stat_value AS REAL)), 1)"},
        "avg_steals": {"label": "Average Steals Per Game", "home_expr": "g.stl_home", "away_expr": "g.stl_away", "aggregate_sql": "ROUND(AVG(CAST(stat_value AS REAL)), 1)"},
        "total_points": {"label": "Total Points Scored", "home_expr": "g.pts_home", "away_expr": "g.pts_away", "aggregate_sql": "ROUND(SUM(CAST(stat_value AS REAL)), 1)"},
        "total_rebounds": {"label": "Total Rebounds", "home_expr": "g.reb_home", "away_expr": "g.reb_away", "aggregate_sql": "ROUND(SUM(CAST(stat_value AS REAL)), 1)"},
        "total_assists": {"label": "Total Assists", "home_expr": "g.ast_home", "away_expr": "g.ast_away", "aggregate_sql": "ROUND(SUM(CAST(stat_value AS REAL)), 1)"},
        "total_blocks": {"label": "Total Blocks", "home_expr": "g.blk_home", "away_expr": "g.blk_away", "aggregate_sql": "ROUND(SUM(CAST(stat_value AS REAL)), 1)"},
        "total_steals": {"label": "Total Steals", "home_expr": "g.stl_home", "away_expr": "g.stl_away", "aggregate_sql": "ROUND(SUM(CAST(stat_value AS REAL)), 1)"},
        "total_turnovers": {"label": "Total Turnovers", "home_expr": "g.tov_home", "away_expr": "g.tov_away", "aggregate_sql": "ROUND(SUM(CAST(stat_value AS REAL)), 1)"},
        "total_fouls": {"label": "Total Personal Fouls", "home_expr": "g.pf_home", "away_expr": "g.pf_away", "aggregate_sql": "ROUND(SUM(CAST(stat_value AS REAL)), 1)"},
        "wins": {"label": "Total Wins", "home_expr": "CASE WHEN g.wl_home = 'W' THEN 1 ELSE 0 END", "away_expr": "CASE WHEN g.wl_away = 'W' THEN 1 ELSE 0 END", "aggregate_sql": "SUM(CAST(stat_value AS REAL))"},
        "losses": {"label": "Total Losses", "home_expr": "CASE WHEN g.wl_home = 'L' THEN 1 ELSE 0 END", "away_expr": "CASE WHEN g.wl_away = 'L' THEN 1 ELSE 0 END", "aggregate_sql": "SUM(CAST(stat_value AS REAL))"},
        "win_percentage": {"label": "Win Percentage (%)", "home_expr": "CASE WHEN g.wl_home = 'W' THEN 1 ELSE 0 END", "away_expr": "CASE WHEN g.wl_away = 'W' THEN 1 ELSE 0 END", "aggregate_sql": "ROUND(100.0 * AVG(CAST(stat_value AS REAL)), 1)"},
        "paint_points": {"label": "Average Points in the Paint", "home_expr": "os.pts_paint_home", "away_expr": "os.pts_paint_away", "aggregate_sql": "ROUND(AVG(CAST(stat_value AS REAL)), 1)"},
        "fast_break_points": {"label": "Average Fast Break Points", "home_expr": "os.pts_fb_home", "away_expr": "os.pts_fb_away", "aggregate_sql": "ROUND(AVG(CAST(stat_value AS REAL)), 1)"},
        "second_chance_points": {"label": "Average Second Chance Points", "home_expr": "os.pts_2nd_chance_home", "away_expr": "os.pts_2nd_chance_away", "aggregate_sql": "ROUND(AVG(CAST(stat_value AS REAL)), 1)"},
        "points_off_turnovers": {"label": "Average Points Off Turnovers", "home_expr": "os.pts_off_to_home", "away_expr": "os.pts_off_to_away", "aggregate_sql": "ROUND(AVG(CAST(stat_value AS REAL)), 1)"}
    }

    TEAM_COLORS = {
        "Atlanta Hawks": "#E03A3E", "Boston Celtics": "#007A33", "Brooklyn Nets": "#000000", "Charlotte Hornets": "#1D1160", "Chicago Bulls": "#CE1141", "Cleveland Cavaliers": "#860038", "Dallas Mavericks": "#00538C", "Denver Nuggets": "#0E2240", "Detroit Pistons": "#C8102E", "Golden State Warriors": "#1D428A", "Houston Rockets": "#CE1141", "Indiana Pacers": "#002D62", "LA Clippers": "#C8102E", "Los Angeles Lakers": "#552583", "Memphis Grizzlies": "#5D76A9", "Miami Heat": "#98002E", "Milwaukee Bucks": "#00471B", "Minnesota Timberwolves": "#0C2340", "New Orleans Pelicans": "#0C2340", "New York Knicks": "#006BB6", "Oklahoma City Thunder": "#007AC1", "Orlando Magic": "#0077C0", "Philadelphia 76ers": "#006BB6", "Phoenix Suns": "#1D1160", "Portland Trail Blazers": "#E03A3E", "Sacramento Kings": "#5A2D81", "San Antonio Spurs": "#C4CED4", "Toronto Raptors": "#CE1141", "Utah Jazz": "#002B5C", "Washington Wizards": "#002B5C", "Baltimore Bullets": "#002B5C", "Capital Bullets": "#002B5C", "Charlotte Bobcats": "#F26522", "Cincinnati Royals": "#5A2D81", "Kansas City Kings": "#5A2D81", "Minneapolis Lakers": "#552583", "New Jersey Nets": "#000000", "New Orleans Hornets": "#008CA8", "Philadelphia Warriors": "#1D428A", "San Diego Clippers": "#C8102E", "San Francisco Warriors": "#1D428A", "Seattle SuperSonics": "#00653A", "St. Louis Hawks": "#E03A3E", "Syracuse Nationals": "#006BB6", "Vancouver Grizzlies": "#00B2A9", "Washington Bullets": "#002B5C"
    }

    TEAM_LOGOS = {
        "Atlanta Hawks": "images/team_logos/hawks.png", "Brooklyn Nets": "images/team_logos/nets.png", "Charlotte Hornets": "images/team_logos/hornets.png", "Cleveland Cavaliers": "images/team_logos/cavaliers.png", "Dallas Mavericks": "images/team_logos/mavericks.png", "Detroit Pistons": "images/team_logos/pistons.png", "Houston Rockets": "images/team_logos/rockets.png", "Indiana Pacers": "images/team_logos/pacers.png", "LA Clippers": "images/team_logos/clippers.png", "Memphis Grizzlies": "images/team_logos/grizzlies.png", "Milwaukee Bucks": "images/team_logos/bucks.png", "Minnesota Timberwolves": "images/team_logos/timberwolves.png", "New Orleans Pelicans": "images/team_logos/pelicans.png", "Oklahoma City Thunder": "images/team_logos/thunder.png", "Orlando Magic": "images/team_logos/magic.png", "Portland Trail Blazers": "images/team_logos/trail_blazers.png", "Sacramento Kings": "images/team_logos/kings.png", "Toronto Raptors": "images/team_logos/raptors.png", "Utah Jazz": "images/team_logos/jazz.png", "Washington Wizards": "images/team_logos/wizards.png", "Los Angeles Lakers": "images/team_logos/lakers.png", "Denver Nuggets": "images/team_logos/nuggets.png", "Boston Celtics": "images/team_logos/celtics.png", "Golden State Warriors": "images/team_logos/warriors.png", "Chicago Bulls": "images/team_logos/bulls.png", "Miami Heat": "images/team_logos/heat.png", "New York Knicks": "images/team_logos/knicks.png", "Philadelphia 76ers": "images/team_logos/76ers.png", "Phoenix Suns": "images/team_logos/suns.png", "San Antonio Spurs": "images/team_logos/spurs.png"
    }

    VALID_NBA_TEAMS = [
        "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets", "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets", "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers", "LA Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat", "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks", "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns", "Portland Trail Blazers", "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors", "Utah Jazz", "Washington Wizards", "Baltimore Bullets", "Capital Bullets", "Charlotte Bobcats", "Chicago Packers", "Chicago Zephyrs", "Cincinnati Royals", "Fort Wayne Pistons", "Kansas City Kings", "Kansas City-Omaha Kings", "Minneapolis Lakers", "New Jersey Nets", "New Orleans Hornets", "New Orleans/Oklahoma City Hornets", "New Orleans Jazz", "Philadelphia Warriors", "Rochester Royals", "San Diego Clippers", "San Diego Rockets", "San Francisco Warriors", "Seattle SuperSonics", "St. Louis Hawks", "Syracuse Nationals", "Tri-Cities Blackhawks", "Vancouver Grizzlies", "Washington Bullets"
    ]

    TEAM_NAME_FIXES = {
        "goldern state warriors": "Golden State Warriors",
        "philadeplhia 76ers": "Philadelphia 76ers",
        "san antonia spurs": "San Antonio Spurs"
    }

    def get_team_logo(team_name):
        logo_path = TEAM_LOGOS.get(team_name, "images/team_logos/default.png")
        return url_for("static", filename=logo_path)

    def get_team_color(team_name):
        return TEAM_COLORS.get(team_name, "#666666")

    def clean_team_sql(column_name):
        cases = []

        for wrong_name, correct_name in TEAM_NAME_FIXES.items():
            cases.append(f"WHEN LOWER(TRIM({column_name})) = '{wrong_name}' THEN '{correct_name}'")

        return "CASE " + " ".join(cases) + f" ELSE TRIM({column_name}) END"

    if selected_stat not in stat_options:
        selected_stat = "avg_points"

    if compare_team == selected_team:
        compare_team = ""

    if selected_team not in VALID_NBA_TEAMS:
        selected_team = "Los Angeles Lakers"

    if compare_team and compare_team not in VALID_NBA_TEAMS:
        compare_team = ""

    stat = stat_options[selected_stat]
    teams = [(team, team, get_team_color(team), get_team_logo(team)) for team in VALID_NBA_TEAMS]

    selected_team_name = selected_team
    compare_team_name = compare_team if compare_team else ""
    selected_team_color = get_team_color(selected_team)
    compare_team_color = get_team_color(compare_team) if compare_team else "#666666"
    selected_team_logo = get_team_logo(selected_team)
    compare_team_logo = get_team_logo(compare_team) if compare_team else ""

    home_team_sql = clean_team_sql("g.team_name_home")
    away_team_sql = clean_team_sql("g.team_name_away")

    graph_sql = f"""
        WITH team_games AS (
            SELECT g.season_id, {home_team_sql} AS team, {stat["home_expr"]} AS stat_value
            FROM game g
            LEFT JOIN other_stats os ON g.game_id = os.game_id

            UNION ALL

            SELECT g.season_id, {away_team_sql} AS team, {stat["away_expr"]} AS stat_value
            FROM game g
            LEFT JOIN other_stats os ON g.game_id = os.game_id
        )

        SELECT
            SUBSTR(season_id, 2, 4) || '-' || printf('%02d', (CAST(SUBSTR(season_id, 2, 4) AS INTEGER) + 1) % 100) AS season_label,
            CAST(SUBSTR(season_id, 2, 4) AS INTEGER) AS start_year,
            team,
            {stat["aggregate_sql"]} AS average_value
        FROM team_games
        WHERE team IN (:team1, :team2)
        AND stat_value IS NOT NULL
        GROUP BY season_label, start_year, team
        ORDER BY start_year, team
    """

    matchup_sql = f"""
        WITH matchup_games AS (
            SELECT g.season_id, {home_team_sql} AS team, {away_team_sql} AS opponent, {stat["home_expr"]} AS stat_value
            FROM game g
            LEFT JOIN other_stats os ON g.game_id = os.game_id

            UNION ALL

            SELECT g.season_id, {away_team_sql} AS team, {home_team_sql} AS opponent, {stat["away_expr"]} AS stat_value
            FROM game g
            LEFT JOIN other_stats os ON g.game_id = os.game_id
        )

        SELECT
            SUBSTR(season_id, 2, 4) || '-' || printf('%02d', (CAST(SUBSTR(season_id, 2, 4) AS INTEGER) + 1) % 100) AS season_label,
            CAST(SUBSTR(season_id, 2, 4) AS INTEGER) AS start_year,
            team,
            {stat["aggregate_sql"]} AS matchup_value
        FROM matchup_games
        WHERE team IN (:team1, :team2)
        AND opponent IN (:team1, :team2)
        AND team != opponent
        AND stat_value IS NOT NULL
        GROUP BY season_label, start_year, team
        ORDER BY start_year, team
    """

    second_team = compare_team if compare_team else selected_team
    matchup_rows = []

    with nba_engine.connect() as conn:
        rows = conn.execute(text(graph_sql), {"team1": selected_team, "team2": second_team}).fetchall()

        if compare_team:
            matchup_rows = conn.execute(text(matchup_sql), {"team1": selected_team, "team2": compare_team}).fetchall()

    labels = []
    team_values = {}

    for season_label, start_year, team, average_value in rows:
        if season_label not in labels:
            labels.append(season_label)

        if team not in team_values:
            team_values[team] = {}

        team_values[team][season_label] = average_value

    chart_datasets = [
        {
            "label": f"{selected_team_name} — {stat['label']}",
            "data": [team_values.get(selected_team, {}).get(label) for label in labels],
            "borderColor": selected_team_color,
            "backgroundColor": selected_team_color,
            "pointBackgroundColor": selected_team_color,
            "pointBorderColor": selected_team_color,
            "borderWidth": 2,
            "tension": 0.2,
            "spanGaps": True
        }
    ]

    table_rows = []

    for label in labels:
        table_rows.append({
            "season": label,
            "team_value": team_values.get(selected_team, {}).get(label),
            "compare_value": team_values.get(compare_team, {}).get(label) if compare_team else None
        })

    if compare_team:
        chart_datasets.append(
            {
                "label": f"{compare_team_name} — {stat['label']}",
                "data": [team_values.get(compare_team, {}).get(label) for label in labels],
                "borderColor": compare_team_color,
                "backgroundColor": compare_team_color,
                "pointBackgroundColor": compare_team_color,
                "pointBorderColor": compare_team_color,
                "borderWidth": 2,
                "tension": 0.2,
                "spanGaps": True
            }
        )

    matchup_labels = []
    matchup_team_values = {}

    for season_label, start_year, team, matchup_value in matchup_rows:
        if season_label not in matchup_labels:
            matchup_labels.append(season_label)

        if team not in matchup_team_values:
            matchup_team_values[team] = {}

        matchup_team_values[team][season_label] = matchup_value

    matchup_chart_datasets = []

    if compare_team and matchup_labels:
        matchup_chart_datasets.append(
            {
                "label": f"{selected_team_name} vs {compare_team_name} — {stat['label']}",
                "data": [matchup_team_values.get(selected_team, {}).get(label) for label in matchup_labels],
                "borderColor": selected_team_color,
                "backgroundColor": selected_team_color,
                "pointBackgroundColor": selected_team_color,
                "pointBorderColor": selected_team_color,
                "borderWidth": 2,
                "tension": 0.2,
                "spanGaps": True
            }
        )

        matchup_chart_datasets.append(
            {
                "label": f"{compare_team_name} vs {selected_team_name} — {stat['label']}",
                "data": [matchup_team_values.get(compare_team, {}).get(label) for label in matchup_labels],
                "borderColor": compare_team_color,
                "backgroundColor": compare_team_color,
                "pointBackgroundColor": compare_team_color,
                "pointBorderColor": compare_team_color,
                "borderWidth": 2,
                "tension": 0.2,
                "spanGaps": True
            }
        )

    return render_template(
        "graphs.html",
        teams=teams,
        selected_team=selected_team,
        compare_team=compare_team,
        selected_stat=selected_stat,
        compare_team_name=compare_team_name,
        selected_team_name=selected_team_name,
        selected_team_color=selected_team_color,
        compare_team_color=compare_team_color,
        selected_team_logo=selected_team_logo,
        compare_team_logo=compare_team_logo,
        stat_options=stat_options,
        stat_label=stat["label"],
        labels=labels,
        chart_datasets=chart_datasets,
        matchup_labels=matchup_labels,
        matchup_chart_datasets=matchup_chart_datasets,
        chart_type=chart_type,
        table_rows=table_rows
    )

@app.route('/player-graphs')
@login_required
def player_graphs():
    selected_player_id = request.args.get("player_id", "jamesle01")
    compare_player_id = request.args.get("compare_player_id", "")
    selected_stat = request.args.get("stat", "pts_per_game")
    chart_type = request.args.get("chart_type", "line")

    player_search = request.args.get("player_search", "").strip()[:50]
    compare_player_search = request.args.get("compare_player_search", "").strip()[:50]
    selected_position = request.args.get("position", "")
    selected_player_team = request.args.get("player_team", "")
    selected_status = request.args.get("status", "")
    start_year = request.args.get("start_year", "")
    end_year = request.args.get("end_year", "")

    all_star_filter = request.args.get("all_star", "")
    mvp_filter = request.args.get("mvp", "")
    dpoy_filter = request.args.get("dpoy", "")
    sixmot_filter = request.args.get("sixmot", "")
    roty_filter = request.args.get("roty", "")
    fmvp_filter = request.args.get("fmvp", "")
    hof_filter = request.args.get("hof", "")

    career_type = request.args.get("career_type", "")
    height_filter = request.args.get("height", "")
    draft_class_filter = request.args.get("draft_class", "")

    age_min = request.args.get("age_min", "")
    age_max = request.args.get("age_max", "")

    min_ppg = safe_number_filter(request.args.get("min_ppg", ""))
    min_rpg = safe_number_filter(request.args.get("min_rpg", ""))
    min_apg = safe_number_filter(request.args.get("min_apg", ""))
    min_mpg = safe_number_filter(request.args.get("min_mpg", ""))

    valid_yes_no_values = ["", "yes", "no"]

    if selected_status not in ["", "current", "retired"]:
        selected_status = ""

    if all_star_filter not in valid_yes_no_values:
        all_star_filter = ""

    if mvp_filter not in valid_yes_no_values:
        mvp_filter = ""

    if dpoy_filter not in valid_yes_no_values:
        dpoy_filter = ""

    if sixmot_filter not in valid_yes_no_values:
        sixmot_filter = ""

    if roty_filter not in valid_yes_no_values:
        roty_filter = ""

    if fmvp_filter not in valid_yes_no_values:
        fmvp_filter = ""

    if hof_filter not in valid_yes_no_values:
        hof_filter = ""

    if career_type not in ["", "journeyman", "one_team"]:
        career_type = ""

    if height_filter not in ["", "under_72", "72_76", "77_80", "81_plus"]:
        height_filter = ""

    if start_year and not start_year.isdigit():
        start_year = ""

    if end_year and not end_year.isdigit():
        end_year = ""

    if age_min and not age_min.isdigit():
        age_min = ""

    if age_max and not age_max.isdigit():
        age_max = ""

    if chart_type not in ["line", "bar"]:
        chart_type = "line"

    player_stat_options = {
        "pts_per_game": {"label": "Points Per Game", "column": "pts_per_game", "multiplier": 1},
        "trb_per_game": {"label": "Rebounds Per Game", "column": "trb_per_game", "multiplier": 1},
        "ast_per_game": {"label": "Assists Per Game", "column": "ast_per_game", "multiplier": 1},
        "stl_per_game": {"label": "Steals Per Game", "column": "stl_per_game", "multiplier": 1},
        "blk_per_game": {"label": "Blocks Per Game", "column": "blk_per_game", "multiplier": 1},
        "tov_per_game": {"label": "Turnovers Per Game", "column": "tov_per_game", "multiplier": 1},
        "mp_per_game": {"label": "Minutes Per Game", "column": "mp_per_game", "multiplier": 1},
        "fg_percent": {"label": "Field Goal Percentage (%)", "column": "fg_percent", "multiplier": 100},
        "x3p_percent": {"label": "Three Point Percentage (%)", "column": "x3p_percent", "multiplier": 100},
        "ft_percent": {"label": "Free Throw Percentage (%)", "column": "ft_percent", "multiplier": 100}
    }

    if selected_stat not in player_stat_options:
        selected_stat = "pts_per_game"

    stat = player_stat_options[selected_stat]
    all_rows = load_player_per_game_rows()

    all_star_player_ids = load_all_star_player_ids()
    award_share_winners = load_award_share_winners()
    award_db_winners = load_existing_award_db_winners()
    career_info = load_career_info()
    draft_info = load_draft_info()

    player_summary = {}
    all_positions = set()
    all_teams = set()
    all_seasons = set()
    all_draft_classes = set()
    all_player_names = set()

    for row in all_rows:
        player_id = row.get("player_id")
        player_name = row.get("player")
        season = row.get("season")
        raw_position = row.get("pos", "").strip()
        raw_team = row.get("team", "").strip()

        if not player_id or not player_name or not season:
            continue

        season_year = season_sort_value(season)
        full_team = full_team_name(raw_team, season)

        if season_year:
            all_seasons.add(season_year)

        position_parts = str(raw_position).split("-") if raw_position else []
        full_positions = []

        for position_part in position_parts:
            position_name = POSITION_LABELS.get(position_part, position_part)
            full_positions.append(position_name)
            all_positions.add(position_name)

        is_combined_team = full_team == "Multiple teams"

        if full_team and not is_combined_team and full_team in NBA_FULL_TEAM_NAMES:
            all_teams.add(full_team)

        all_player_names.add(player_name)
        normalized_player_name = normalize_name(player_name)

        if player_id not in player_summary:
            player_summary[player_id] = {
                "player_id": player_id,
                "player": player_name,
                "normalized_player": normalized_player_name,
                "first_season": season,
                "last_season": season,
                "first_year_value": season_year,
                "last_year_value": season_year,
                "positions": set(),
                "teams": set(),
                "latest_age": None,
                "latest_team": "",
                "latest_position": "",
                "max_ppg": 0,
                "max_rpg": 0,
                "max_apg": 0,
                "max_mpg": 0
            }

        current_first = player_summary[player_id]["first_year_value"]
        current_last = player_summary[player_id]["last_year_value"]

        if season_year and (not current_first or season_year < current_first):
            player_summary[player_id]["first_season"] = season
            player_summary[player_id]["first_year_value"] = season_year

        if season_year and (not current_last or season_year > current_last):
            player_summary[player_id]["last_season"] = season
            player_summary[player_id]["last_year_value"] = season_year
            player_summary[player_id]["latest_age"] = safe_int_or_none(row.get("age"))
            player_summary[player_id]["latest_team"] = full_team
            player_summary[player_id]["latest_position"] = full_position_name(raw_position)

        for position_name in full_positions:
            player_summary[player_id]["positions"].add(position_name)

        if full_team and not is_combined_team and full_team in NBA_FULL_TEAM_NAMES:
            player_summary[player_id]["teams"].add(full_team)

        ppg = safe_float(row.get("pts_per_game")) or 0
        rpg = safe_float(row.get("trb_per_game")) or 0
        apg = safe_float(row.get("ast_per_game")) or 0
        mpg = safe_float(row.get("mp_per_game")) or 0

        player_summary[player_id]["max_ppg"] = max(player_summary[player_id]["max_ppg"], ppg)
        player_summary[player_id]["max_rpg"] = max(player_summary[player_id]["max_rpg"], rpg)
        player_summary[player_id]["max_apg"] = max(player_summary[player_id]["max_apg"], apg)
        player_summary[player_id]["max_mpg"] = max(player_summary[player_id]["max_mpg"], mpg)

    for player_id, info in player_summary.items():
        player_career_info = career_info.get(player_id, {})
        player_draft_info = draft_info.get(player_id, {})
        normalized_player_name = info["normalized_player"]

        info["team_count"] = len(info["teams"])
        info["has_all_star"] = player_id in all_star_player_ids
        info["has_mvp"] = player_id in award_share_winners["mvp"] or normalized_player_name in award_db_winners["mvp"]
        info["has_dpoy"] = player_id in award_share_winners["dpoy"] or normalized_player_name in award_db_winners["dpoy"]
        info["has_sixmot"] = player_id in award_share_winners["sixmot"] or normalized_player_name in award_db_winners["sixmot"]
        info["has_roty"] = player_id in award_share_winners["roty"]
        info["has_fmvp"] = normalized_player_name in award_db_winners["fmvp"]
        info["has_hof"] = player_career_info.get("hof", False)
        info["height"] = player_career_info.get("height")
        info["draft_class"] = player_draft_info.get("draft_class", "")

        if info["draft_class"]:
            all_draft_classes.add(info["draft_class"])

    position_options = sorted(all_positions)
    team_options = sorted(all_teams)
    season_options = sorted(all_seasons)
    draft_class_options = sorted(all_draft_classes)
    player_name_options = sorted(all_player_names)
    latest_dataset_year = max(all_seasons) if all_seasons else 0

    filtered_player_summary = []
    search_lower = normalize_name(player_search)

    for info in player_summary.values():
        first_year = info["first_year_value"]
        last_year = info["last_year_value"]

        if search_lower and search_lower not in info["normalized_player"]:
            continue

        if selected_position and selected_position not in info["positions"]:
            continue

        if selected_player_team and selected_player_team not in info["teams"]:
            continue

        if start_year and last_year < int(start_year):
            continue

        if end_year and first_year > int(end_year):
            continue

        if selected_status == "current" and last_year != latest_dataset_year:
            continue

        if selected_status == "retired" and last_year == latest_dataset_year:
            continue

        if not yes_no_filter_matches(all_star_filter, info["has_all_star"]):
            continue

        if not yes_no_filter_matches(mvp_filter, info["has_mvp"]):
            continue

        if not yes_no_filter_matches(dpoy_filter, info["has_dpoy"]):
            continue

        if not yes_no_filter_matches(sixmot_filter, info["has_sixmot"]):
            continue

        if not yes_no_filter_matches(roty_filter, info["has_roty"]):
            continue

        if not yes_no_filter_matches(fmvp_filter, info["has_fmvp"]):
            continue

        if not yes_no_filter_matches(hof_filter, info["has_hof"]):
            continue

        if career_type == "journeyman" and info["team_count"] < 4:
            continue

        if career_type == "one_team" and info["team_count"] != 1:
            continue

        if not height_matches(info["height"], height_filter):
            continue

        if draft_class_filter and info["draft_class"] != draft_class_filter:
            continue

        if age_min and (info["latest_age"] is None or info["latest_age"] < int(age_min)):
            continue

        if age_max and (info["latest_age"] is None or info["latest_age"] > int(age_max)):
            continue

        if min_ppg and info["max_ppg"] < float(min_ppg):
            continue

        if min_rpg and info["max_rpg"] < float(min_rpg):
            continue

        if min_apg and info["max_apg"] < float(min_apg):
            continue

        if min_mpg and info["max_mpg"] < float(min_mpg):
            continue

        filtered_player_summary.append(info)

    MAX_PLAYER_RESULTS = 250

    players = sorted(
        [
            (
                info["player_id"],
                info["player"],
                info["first_season"],
                info["last_season"]
            )
            for info in filtered_player_summary
        ],
        key=lambda player: player[1]
    )[:MAX_PLAYER_RESULTS]

    player_ids = [player[0] for player in players]
    all_player_ids = set(player_summary.keys())
    player_names = {info["player_id"]: info["player"] for info in player_summary.values()}

    if not player_ids:
        selected_player_id = ""
    else:
        if selected_player_id not in player_ids:
            selected_player_id = "jamesle01"

        if selected_player_id not in player_ids:
            selected_player_id = player_ids[0]

    if compare_player_id == selected_player_id:
        compare_player_id = ""

    if compare_player_id and compare_player_id not in all_player_ids:
        compare_player_id = ""

    compare_candidates = []
    compare_search_lower = normalize_name(compare_player_search)

    if compare_search_lower:
        for info in player_summary.values():
            if compare_search_lower in info["normalized_player"]:
                compare_candidates.append(
                    (
                        info["player_id"],
                        info["player"],
                        info["first_season"],
                        info["last_season"]
                    )
                )

    compare_candidates = sorted(compare_candidates, key=lambda player: player[1])[:80]

    if compare_player_id and compare_player_id in player_summary:
        selected_compare_info = player_summary[compare_player_id]
        selected_compare_tuple = (
            selected_compare_info["player_id"],
            selected_compare_info["player"],
            selected_compare_info["first_season"],
            selected_compare_info["last_season"]
        )

        if selected_compare_tuple not in compare_candidates:
            compare_candidates.insert(0, selected_compare_tuple)

    selected_player_name = player_names.get(selected_player_id, "Selected Player")
    compare_player_name = player_names.get(compare_player_id, "") if compare_player_id else ""

    selected_ids = []

    if selected_player_id:
        selected_ids.append(selected_player_id)

    if compare_player_id:
        selected_ids.append(compare_player_id)

    best_rows = {}

    for row in all_rows:
        player_id = row.get("player_id")
        season = row.get("season")

        if player_id not in selected_ids:
            continue

        if not season:
            continue

        key = (player_id, season)
        team = row.get("team", "")
        games = safe_int(row.get("g"))
        is_combined_team_row = team in ["TOT", "2TM", "3TM", "4TM"] or team.endswith("TM")
        row_rank = (1 if is_combined_team_row else 0, games)

        if key not in best_rows or row_rank > best_rows[key]["rank"]:
            best_rows[key] = {
                "row": row,
                "rank": row_rank
            }

    selected_rows = [item["row"] for item in best_rows.values()]
    selected_rows.sort(key=lambda row: (season_sort_value(row.get("season")), row.get("player_id", "")))

    labels = []
    player_values = {}
    latest_player_info = {}

    for row in selected_rows:
        player_id = row.get("player_id")
        season = row.get("season")
        season_label = str(season)
        raw_value = safe_float(row.get(stat["column"]))

        if raw_value is None:
            continue

        stat_value = round(raw_value * stat["multiplier"], 1)

        if season_label not in labels:
            labels.append(season_label)

        if player_id not in player_values:
            player_values[player_id] = {}

        player_values[player_id][season_label] = stat_value

        latest_player_info[player_id] = {
            "season": season,
            "team": full_team_name(row.get("team"), season),
            "position": full_position_name(row.get("pos")),
            "age": row.get("age"),
            "games": row.get("g"),
            "minutes": row.get("mp_per_game")
        }

    selected_player_color = "#1D428A"
    compare_player_color = "#CE1141"

    chart_datasets = [
        {
            "label": f"{selected_player_name} — {stat['label']}",
            "data": [player_values.get(selected_player_id, {}).get(label) for label in labels],
            "borderColor": selected_player_color,
            "backgroundColor": selected_player_color,
            "pointBackgroundColor": selected_player_color,
            "pointBorderColor": selected_player_color,
            "borderWidth": 2,
            "tension": 0.2,
            "spanGaps": True
        }
    ]

    if compare_player_id:
        chart_datasets.append(
            {
                "label": f"{compare_player_name} — {stat['label']}",
                "data": [player_values.get(compare_player_id, {}).get(label) for label in labels],
                "borderColor": compare_player_color,
                "backgroundColor": compare_player_color,
                "pointBackgroundColor": compare_player_color,
                "pointBorderColor": compare_player_color,
                "borderWidth": 2,
                "tension": 0.2,
                "spanGaps": True
            }
        )

    table_rows = []

    for label in labels:
        table_rows.append(
            {
                "season": label,
                "selected_value": player_values.get(selected_player_id, {}).get(label),
                "compare_value": player_values.get(compare_player_id, {}).get(label) if compare_player_id else None
            }
        )

    return render_template(
        "player_graphs.html",
        players=players,
        selected_player_id=selected_player_id,
        compare_player_id=compare_player_id,
        selected_player_name=selected_player_name,
        compare_player_name=compare_player_name,
        selected_stat=selected_stat,
        stat_options=player_stat_options,
        stat_label=stat["label"],
        labels=labels,
        chart_datasets=chart_datasets,
        chart_type=chart_type,
        table_rows=table_rows,
        selected_player_info=latest_player_info.get(selected_player_id),
        compare_player_info=latest_player_info.get(compare_player_id) if compare_player_id else None,
        selected_player_color=selected_player_color,
        compare_player_color=compare_player_color,
        player_search=player_search,
        compare_player_search=compare_player_search,
        compare_candidates=compare_candidates,
        selected_position=selected_position,
        selected_player_team=selected_player_team,
        selected_status=selected_status,
        start_year=start_year,
        end_year=end_year,
        position_options=position_options,
        team_options=team_options,
        season_options=season_options,
        draft_class_options=draft_class_options,
        player_name_options=player_name_options,
        filtered_player_count=len(filtered_player_summary),
        players_shown_count=len(players),
        all_star_filter=all_star_filter,
        mvp_filter=mvp_filter,
        dpoy_filter=dpoy_filter,
        sixmot_filter=sixmot_filter,
        roty_filter=roty_filter,
        fmvp_filter=fmvp_filter,
        hof_filter=hof_filter,
        career_type=career_type,
        height_filter=height_filter,
        draft_class_filter=draft_class_filter,
        age_min=age_min,
        age_max=age_max,
        min_ppg=min_ppg,
        min_rpg=min_rpg,
        min_apg=min_apg,
        min_mpg=min_mpg
    )


@app.route('/player/<player_id>')
@login_required
def player_profile(player_id):
    profile = build_player_profile(player_id)

    if profile is None:
        abort(404)

    return render_template("player_profile.html", profile=profile)


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()[:30]
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        try:
            with get_auth_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                conn.commit()

            flash("Account created. You can now log in.")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("That username is already taken.")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()[:30]
        password = request.form.get("password", "")

        with get_auth_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Logged in successfully.")
            return redirect(url_for("home"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(debug=True, reloader_type='stat', port=5000)
