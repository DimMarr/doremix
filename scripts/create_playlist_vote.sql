CREATE TABLE IF NOT EXISTS playlist_vote (
    iduser INTEGER NOT NULL REFERENCES users(iduser) ON DELETE CASCADE,
    idplaylist INTEGER NOT NULL REFERENCES playlist(idplaylist) ON DELETE CASCADE,
    value SMALLINT NOT NULL CHECK (value IN (-1, 1)),
    PRIMARY KEY (iduser, idplaylist)
);
