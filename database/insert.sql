-- ============================================================
-- FICHIER 2 : JEU DE DONNÉES (SEEDING)
-- ============================================================

-- Nettoyage des données existantes (pour éviter les doublons si relancé)
TRUNCATE USER_PLAYLIST, TRACK_PLAYLIST, TRACK_ARTIST, PLAYLIST, TRACK, ARTIST, GENRE, "USER" RESTART IDENTITY CASCADE;

BEGIN;

-- 1. GENRES (8 entrées)
INSERT INTO GENRE (label) VALUES 
('Rock'), ('Pop'), ('Hip-Hop'), ('Jazz'), 
('Electro'), ('Metal'), ('Classical'), ('Reggae');

-- 2. ARTISTS (12 entrées)
INSERT INTO ARTIST (name) VALUES 
('Queen'),              -- 1
('Daft Punk'),          -- 2
('Pharrell Williams'),  -- 3
('Eminem'),             -- 4
('Miles Davis'),        -- 5
('Metallica'),          -- 6
('Mozart'),             -- 7
('Adele'),              -- 8
('The Weeknd'),         -- 9
('Kendrick Lamar'),     -- 10
('Rihanna'),            -- 11
('Hans Zimmer');        -- 12

-- 3. USERS (5 entrées)
INSERT INTO "USER" (username, email, password, role, disabled) VALUES 
('AdminSys', 'admin@platform.com', 'admin123', 'ADMIN', FALSE),   -- 1
('AliceMusic', 'alice@gmail.com', 'passA', 'USER', FALSE),        -- 2 (Active creator)
('BobRocker', 'bob@yahoo.com', 'passB', 'USER', FALSE),           -- 3 (Rock fan)
('CharliePro', 'charlie@pro.com', 'passC', 'USER', FALSE),        -- 4 (Editor)
('DaveBanned', 'dave@bad.com', 'passD', 'USER', TRUE);            -- 5 (Banned user)

-- 4. TRACKS (20 entrées variées)
INSERT INTO TRACK (title, listeningCount, durationSeconds) VALUES 
-- Rock / Metal
('Bohemian Rhapsody', 15000000, 354),     -- 1
('We Will Rock You', 8000000, 121),       -- 2
('Enter Sandman', 5000000, 331),          -- 3
('Nothing Else Matters', 6500000, 388),   -- 4
-- Pop / Electro
('Get Lucky', 980000, 248),               -- 5
('Instant Crush', 450000, 337),           -- 6
('Rolling in the Deep', 2100000, 228),    -- 7
('Someone Like You', 1800000, 285),       -- 8
('Blinding Lights', 3500000, 200),        -- 9
('Starboy', 2900000, 230),                -- 10
-- Hip-Hop
('Lose Yourself', 4000000, 326),          -- 11
('Stan', 1200000, 384),                   -- 12
('HUMBLE.', 3100000, 177),                -- 13
('Umbrella', 5500000, 275),               -- 14
-- Jazz / Classical / BO
('So What', 45000, 562),                  -- 15
('Blue in Green', 30000, 327),            -- 16
('Requiem', 800000, 300),                 -- 17
('Inception Time', 150000, 275),          -- 18
('Interstellar Main Theme', 200000, 250), -- 19
('One', 1200, 435);                       -- 20

-- 5. TRACK_ARTIST (Qui chante quoi ? Gestion des Duos)
INSERT INTO TRACK_ARTIST (idTrack, idArtist, position) VALUES 
(1, 1, 1), (2, 1, 1), -- Queen
(3, 6, 1), (4, 6, 1), -- Metallica
(5, 2, 1), (5, 3, 2), -- Get Lucky: Daft Punk (1) & Pharrell (2)
(6, 2, 1),            -- Instant Crush: Daft Punk
(7, 8, 1), (8, 8, 1), -- Adele
(9, 9, 1),            -- The Weeknd
(10, 9, 1), (10, 2, 2), -- Starboy: The Weeknd ft Daft Punk
(11, 4, 1), (12, 4, 1), -- Eminem
(13, 10, 1),            -- Kendrick
(14, 11, 1),            -- Rihanna
(15, 5, 1), (16, 5, 1), -- Miles Davis
(17, 7, 1),             -- Mozart
(18, 12, 1), (19, 12, 1), -- Hans Zimmer
(20, 6, 1);             -- One: Metallica

-- 6. PLAYLISTS
INSERT INTO PLAYLIST (name, idGenre, idOwner, visibility, vote) VALUES 
('Alice Roadtrip', 2, 2, 'PUBLIC', 150),       -- ID 1 (Pop, by Alice)
('Bob Metal Fest', 6, 3, 'PUBLIC', 666),       -- ID 2 (Metal, by Bob)
('Study Session', 7, 2, 'PUBLIC', 40),         -- ID 3 (Classical, by Alice)
('Private Gym', 3, 2, 'PRIVATE', 0),           -- ID 4 (HipHop, by Alice)
('Electro Party', 5, 1, 'PUBLIC', 999),        -- ID 5 (Electro, by Admin)
('Sad Vibes', 2, 3, 'PRIVATE', 5);             -- ID 6 (Pop, by Bob)

-- 7. TRACK_PLAYLIST (Remplissage des playlists)
INSERT INTO TRACK_PLAYLIST (idTrack, idPlaylist, position) VALUES 
-- Alice Roadtrip (Pop/Mix)
(5, 1, 1), (9, 1, 2), (14, 1, 3), (1, 1, 4),
-- Bob Metal Fest (Metal)
(3, 2, 1), (4, 2, 2), (20, 2, 3), (2, 2, 4),
-- Study Session (Calm)
(15, 3, 1), (16, 3, 2), (17, 3, 3), (19, 3, 4),
-- Private Gym (HipHop/Dynamique)
(11, 4, 1), (13, 4, 2), (9, 4, 3),
-- Electro Party (Daft Punk & Weeknd)
(5, 5, 1), (6, 5, 2), (10, 5, 3),
-- Sad Vibes
(8, 6, 1), (12, 6, 2), (4, 6, 3);

-- 8. USER_PLAYLIST (Collaboration / Éditeurs)
-- CharliePro aide Alice sur sa playlist "Roadtrip"
INSERT INTO USER_PLAYLIST (idUser, idPlaylist, editor) VALUES (4, 1, TRUE);
-- BobRocker est fan (spectateur) de la playlist "Electro Party" de l'Admin
INSERT INTO USER_PLAYLIST (idUser, idPlaylist, editor) VALUES (3, 5, FALSE);

COMMIT;