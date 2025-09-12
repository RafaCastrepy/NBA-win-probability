import tkinter as tk
from tkinter import ttk

from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import franchisehistory
from nba_api.stats.static import teams
import pandas as pd
from datetime import datetime

# --- Generate seasons ---
def generate_seasons(start=1996):
    current_year = datetime.now().year
    if datetime.now().month < 8:
        current_year -= 1
    return [f"{year}-{str(year+1)[-2:]}" for year in range(start, current_year)]

all_seasons = generate_seasons()

# --- NBA teams ---
franchises = franchisehistory.FranchiseHistory().get_data_frames()[0]
franchises['START_YEAR'] = pd.to_numeric(franchises['START_YEAR'])
franchises['END_YEAR'] = pd.to_numeric(franchises['END_YEAR'])
filtered = franchises[franchises['END_YEAR'] >= 1996]
nba_teams = pd.DataFrame(teams.get_teams())
merged = filtered.merge(nba_teams, left_on="TEAM_ID", right_on="id", how="left")
team_abbrs = merged['abbreviation'].dropna().unique().tolist()
team_abbrs.sort()

# --- Tkinter setup ---
root = tk.Tk()
root.title("NBA Match Finder")
root.attributes("-fullscreen", True)

frame = tk.Frame(root)
frame.place(relx=0.5, rely=0, anchor="n")

# --- Labels and dropdowns ---
year_label = tk.Label(frame, text="Selected Year:")
year_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
year_combo_box = ttk.Combobox(frame, values=all_seasons, state="readonly")
year_combo_box.grid(row=0, column=1, padx=10, pady=5)
year_combo_box.set("Choose Year")

team1_label = tk.Label(frame, text="Team 1:")
team1_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
team1_combo_box = ttk.Combobox(frame, values=team_abbrs, state="disabled")
team1_combo_box.grid(row=1, column=1, padx=10, pady=5)
team1_combo_box.set("Choose Team 1")

team2_label = tk.Label(frame, text="Team 2:")
team2_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
team2_combo_box = ttk.Combobox(frame, values=team_abbrs, state="disabled")
team2_combo_box.grid(row=2, column=1, padx=10, pady=5)
team2_combo_box.set("Choose Team 2")

# --- Unlock dropdowns dynamically ---
def year_selected(event):
    team1_combo_box.config(state="readonly")

def team1_selected(event):
    team2_combo_box.config(state="readonly")
    year_combo_box.config(state="disabled")  # lock year after team1 selection

year_combo_box.bind("<<ComboboxSelected>>", year_selected)
team1_combo_box.bind("<<ComboboxSelected>>", team1_selected)

# Placeholders for dynamic widgets
game_dropdown = None
no_games_label = None
run_button = None

# --- Find Matches button ---
def find_matches():
    global game_dropdown, no_games_label, run_button

    # Remove old widgets if they exist
    if game_dropdown:
        game_dropdown.destroy()
    if no_games_label:
        no_games_label.destroy()
    if run_button:
        run_button.destroy()

    year = year_combo_box.get()
    team1 = team1_combo_box.get()
    team2 = team2_combo_box.get()

    if not year or not team1 or not team2:
        print("Please select Year, Team 1, and Team 2")
        return

    # Lock Team 1 now that Team 2 is selected
    team1_combo_box.config(state="disabled")

    # Fetch games
    games = leaguegamefinder.LeagueGameFinder(season_nullable=year).get_data_frames()[0]

    # Match both home and away combinations
    mask = (
        (games['MATCHUP'].str.lower() == f"{team1.lower()} vs. {team2.lower()}") |
        (games['MATCHUP'].str.lower() == f"{team1.lower()} @ {team2.lower()}") |
        (games['MATCHUP'].str.lower() == f"{team2.lower()} vs. {team1.lower()}") |
        (games['MATCHUP'].str.lower() == f"{team2.lower()} @ {team1.lower()}")
    )

    matchups = games[mask]

    if matchups.empty:
        no_games_label = tk.Label(frame, text="No games found.", font=("Arial", 12), fg="red")
        no_games_label.grid(row=5, column=0, columnspan=2, pady=10)
    else:
        game_options = [f"{row['GAME_DATE']} - {row['MATCHUP']}" for idx, row in matchups.iterrows()]
        game_dropdown = ttk.Combobox(frame, values=game_options, state="readonly")
        game_dropdown.set("Choose Game")
        game_dropdown.grid(row=5, column=0, columnspan=2, pady=10)

    # Add the "Run Program" button (no functionality yet)
    run_button = tk.Button(frame, text="Run Program", font=("Arial", 14))
    run_button.grid(row=6, column=0, columnspan=2, pady=10)

# --- Reset button ---
def reset_all():
    global game_dropdown, no_games_label, run_button

    # Clear selections
    year_combo_box.set("Choose Year")
    team1_combo_box.set("Choose Team 1")
    team2_combo_box.set("Choose Team 2")

    # Lock Team 1 and Team 2, unlock Year
    team1_combo_box.config(state="disabled")
    team2_combo_box.config(state="disabled")
    year_combo_box.config(state="readonly")

    # Remove dynamic widgets
    if game_dropdown:
        game_dropdown.destroy()
        game_dropdown = None
    if no_games_label:
        no_games_label.destroy()
        no_games_label = None
    if run_button:
        run_button.destroy()
        run_button = None

# --- Buttons ---
button_find = tk.Button(frame, text="Find Matches", command=find_matches, font=("Arial", 14))
button_find.grid(row=3, column=0, columnspan=2, pady=10)

button_reset = tk.Button(frame, text="Reset", command=reset_all, font=("Arial", 14))
button_reset.grid(row=4, column=0, columnspan=2, pady=10)

button_quit = tk.Button(frame, text="Quit (Esc)", command=root.quit, font=("Arial", 14))
button_quit.grid(row=7, column=0, columnspan=2, pady=10)

root.bind("<Escape>", lambda e: root.quit())

root.mainloop()
