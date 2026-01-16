TRUNCATE USER_PLAYLIST, TRACK_PLAYLIST, TRACK_ARTIST, PLAYLIST, TRACK, ARTIST, GENRE, USERS RESTART IDENTITY CASCADE;

BEGIN;

INSERT INTO GENRE (label) VALUES
('No genre'), ('Rock'), ('Pop'), ('Hip-Hop'), ('Jazz'),
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

INSERT INTO TRACK (title, youtubeLink, listeningCount, durationSeconds) VALUES
('Bohemian Rhapsody', 'https://www.youtube.com/watch?v=fJ9rUzIMcZQ', 15000000, 354),
('We Will Rock You', 'https://www.youtube.com/watch?v=-tJYN-eG1zk', 8000000, 121),
('Enter Sandman', 'https://www.youtube.com/watch?v=CD-E-LDc384', 5000000, 331),
('Nothing Else Matters', 'https://www.youtube.com/watch?v=tAGnKpE4NCI', 6500000, 388),
('Get Lucky', 'https://www.youtube.com/watch?v=5NV6Rdv1a3I', 980000, 248),
('Instant Crush', 'https://www.youtube.com/watch?v=PtFMh6T4F5A', 450000, 337),
('Rolling in the Deep', 'https://www.youtube.com/watch?v=rYEDA3JcQqw', 2100000, 228),
('Someone Like You', 'https://www.youtube.com/watch?v=hLQl3WQQoQ0', 1800000, 285),
('Blinding Lights', 'https://www.youtube.com/watch?v=4NRXx6U8ABQ', 3500000, 200),
('Starboy', 'https://www.youtube.com/watch?v=34Na4j8AVgA', 2900000, 230),
('Lose Yourself', 'https://www.youtube.com/watch?v=_Yhyp-_hX2s', 4000000, 326),
('Stan', 'https://www.youtube.com/watch?v=gOMhN-hfMtY', 1200000, 384),
('HUMBLE.', 'https://www.youtube.com/watch?v=tvTRZJ-4EyI', 3100000, 177),
('Umbrella', 'https://www.youtube.com/watch?v=CvBfHwUxHIk', 5500000, 275),
('So What', 'https://www.youtube.com/watch?v=ylXk1LBvIqU', 45000, 562),
('Blue in Green', 'https://www.youtube.com/watch?v=PoPL7BExSQU', 30000, 327),
('Requiem', 'https://www.youtube.com/watch?v=Zi8vJ_lMxQI', 800000, 300),
('Inception Time', 'https://www.youtube.com/watch?v=YoHD9XEInc0', 150000, 275),
('Interstellar Main Theme', 'https://www.youtube.com/watch?v=zSWdZVtXT7E', 200000, 250),
('One', 'https://www.youtube.com/watch?v=ktvTqknDobU', 1200, 435);


INSERT INTO TRACK_ARTIST (idTrack, idArtist) VALUES
(1, 1), (2, 1), (3, 6), (4, 6), (5, 2), (5, 3),
(6, 2), (7, 8), (8, 8), (9, 9), (10, 9), (10, 2),
(11, 4), (12, 4), (13, 10), (14, 11), (15, 5),
(16, 5), (17, 7), (18, 12), (19, 12), (20, 6);

INSERT INTO PLAYLIST (name, idGenre, idOwner, visibility, vote) VALUES
('Alice Roadtrip', 2, 3, 'PUBLIC', 150),
('Bob Metal Fest', 6, 4, 'PUBLIC', 666),
('Study Session', 7, 3, 'PRIVATE', 40),
('Staff Picks', 5, 1, 'PUBLIC', 999),
('Open Community Jams', 4, 2, 'OPEN', 50),
('Team Project Focus', 5, 5, 'SHARED', 10);

INSERT INTO TRACK_PLAYLIST (idTrack, idPlaylist) VALUES
(5, 1), (9, 1), (14, 1),
(3, 2), (4, 2), (20, 2),
(15, 3), (17, 3),
(5, 4), (10, 4),
(13, 5), (1, 5), (19, 5),
(18, 6), (6, 6);

INSERT INTO USER_PLAYLIST (idUser, idPlaylist, editor) VALUES
(3, 6, TRUE),
(4, 5, TRUE);

COMMIT;
