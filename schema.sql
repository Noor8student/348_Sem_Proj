DROP TABLE IF EXISTS players;

CREATE TABLE players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    team_name TEXT NOT NULL,
    ppg REAL NOT NULL,
    rpg REAL NOT NULL,
    apg REAL NOT NULL,
    bpg REAL NOT NULL,
    spg REAL NOT NULL,
    fg_pct REAL NOT NULL,
    three_pt_pct REAL NOT NULL,
    ft_pct REAL NOT NULL
);

CREATE INDEX idx_ppg ON players(ppg);
CREATE INDEX idx_team ON players(team_name);
CREATE INDEX idx_rpg ON players(rpg);
CREATE INDEX idx_apg ON players(apg);