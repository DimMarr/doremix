TRUNCATE USER_PLAYLIST, TRACK_PLAYLIST, TRACK_ARTIST, PLAYLIST, TRACK, ARTIST, GENRE, USERS RESTART IDENTITY CASCADE;

BEGIN;

INSERT INTO GENRE (label) VALUES 
('Rock'), ('Pop'), ('Hip-Hop'), ('Jazz'), 
('Electro'), ('Metal'), ('Classical'), ('Reggae');

INSERT INTO ARTIST (name) VALUES 
('Queen'), ('Daft Punk'), ('Pharrell Williams'), ('Eminem'), 
('Miles Davis'), ('Metallica'), ('Mozart'), ('Adele'), 
('The Weeknd'), ('Kendrick Lamar'), ('Rihanna'), ('Hans Zimmer');

INSERT INTO USERS (username, email, password, role, banned) VALUES 
('AdminSys', 'admin@platform.com', 'admin123', 'ADMIN', FALSE),
('ModSarah', 'sarah@modo.com', 'secureMod', 'MODERATOR', FALSE),
('AliceMusic', 'alice@gmail.com', 'passA', 'USER', FALSE),
('BobRocker', 'bob@yahoo.com', 'passB', 'USER', FALSE),
('CharliePro', 'charlie@pro.com', 'passC', 'USER', FALSE),
('DaveBanned', 'dave@bad.com', 'passD', 'USER', TRUE);

INSERT INTO TRACK (title, listeningCount, durationSeconds) VALUES 
('Bohemian Rhapsody', 15000000, 354),
('We Will Rock You', 8000000, 121),
('Enter Sandman', 5000000, 331),
('Nothing Else Matters', 6500000, 388),
('Get Lucky', 980000, 248),
('Instant Crush', 450000, 337),
('Rolling in the Deep', 2100000, 228),
('Someone Like You', 1800000, 285),
('Blinding Lights', 3500000, 200),
('Starboy', 2900000, 230),
('Lose Yourself', 4000000, 326),
('Stan', 1200000, 384),
('HUMBLE.', 3100000, 177),
('Umbrella', 5500000, 275),
('So What', 45000, 562),
('Blue in Green', 30000, 327),
('Requiem', 800000, 300),
('Inception Time', 150000, 275),
('Interstellar Main Theme', 200000, 250),
('One', 1200, 435);

INSERT INTO TRACK_ARTIST (idTrack, idArtist, position) VALUES 
(1, 1, 1), (2, 1, 1), (3, 6, 1), (4, 6, 1), (5, 2, 1), (5, 3, 2), 
(6, 2, 1), (7, 8, 1), (8, 8, 1), (9, 9, 1), (10, 9, 1), (10, 2, 2), 
(11, 4, 1), (12, 4, 1), (13, 10, 1), (14, 11, 1), (15, 5, 1), 
(16, 5, 1), (17, 7, 1), (18, 12, 1), (19, 12, 1), (20, 6, 1);

INSERT INTO PLAYLIST (name, idGenre, idOwner, visibility, vote) VALUES 
('Alice Roadtrip', 2, 3, 'PUBLIC', 150),
('Bob Metal Fest', 6, 4, 'PUBLIC', 666),
('Study Session', 7, 3, 'PRIVATE', 40),
('Staff Picks', 5, 1, 'PUBLIC', 999),
('Open Community Jams', 4, 2, 'OPEN', 50),
('Team Project Focus', 5, 5, 'SHARED', 10);

INSERT INTO TRACK_PLAYLIST (idTrack, idPlaylist, position) VALUES 
(5, 1, 1), (9, 1, 2), (14, 1, 3),
(3, 2, 1), (4, 2, 2), (20, 2, 3),
(15, 3, 1), (17, 3, 2),
(5, 4, 1), (10, 4, 2),
(13, 5, 1), (1, 5, 2), (19, 5, 3),
(18, 6, 1), (6, 6, 2);

INSERT INTO USER_PLAYLIST (idUser, idPlaylist, editor) VALUES 
(3, 6, TRUE),
(4, 5, TRUE);

COMMIT;