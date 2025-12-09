-- 1. Table MUSICAL_TYPE
CREATE TABLE MUSICAL_TYPE (
    idType SERIAL PRIMARY KEY,
    label VARCHAR(255) NOT NULL
);

-- 2. Table ARTIST
CREATE TABLE ARTIST (
    idArtist SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- 3. Table TRACK
CREATE TABLE TRACK (
    idTrack SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    youtubeLink VARCHAR(2048),
    listeningCount INTEGER DEFAULT 0,
    durationSeconds INTEGER,
    addedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Table PLAYLIST
CREATE TABLE PLAYLIST (
    idPlaylist SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    idType INTEGER NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_playlist_type 
        FOREIGN KEY (idType) REFERENCES MUSICAL_TYPE(idType)
);

-- 5. Table de liaison TRACK_ARTIST
CREATE TABLE TRACK_ARTIST (
    idTrack INTEGER NOT NULL,
    idArtist INTEGER NOT NULL,
    position INTEGER,
    PRIMARY KEY (idTrack, idArtist),
    CONSTRAINT fk_trackartist_track 
        FOREIGN KEY (idTrack) REFERENCES TRACK(idTrack) 
        ON DELETE CASCADE,
    CONSTRAINT fk_trackartist_artist 
        FOREIGN KEY (idArtist) REFERENCES ARTIST(idArtist) 
        ON DELETE CASCADE
);

-- 6. Table de liaison TRACK_PLAYLIST
CREATE TABLE TRACK_PLAYLIST (
    idTrack INTEGER NOT NULL,
    idPlaylist INTEGER NOT NULL,
    position INTEGER,
    PRIMARY KEY (idTrack, idPlaylist),
    CONSTRAINT fk_trackplaylist_track 
        FOREIGN KEY (idTrack) REFERENCES TRACK(idTrack) 
        ON DELETE CASCADE,
    CONSTRAINT fk_trackplaylist_playlist 
        FOREIGN KEY (idPlaylist) REFERENCES PLAYLIST(idPlaylist) 
        ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- PARTIE SPÉCIFIQUE POSTGRESQL : GESTION DU updatedAt
-- ---------------------------------------------------------

-- A. Création de la fonction de mise à jour de la date
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updatedAt = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- B. Application du Trigger sur la table PLAYLIST
CREATE TRIGGER update_playlist_updated_at
    BEFORE UPDATE ON PLAYLIST
    FOR EACH ROW
    EXECUTE PROCEDURE update_updated_at_column();