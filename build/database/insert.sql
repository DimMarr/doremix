TRUNCATE
    USER_PLAYLIST, TRACK_PLAYLIST, TRACK_ARTIST, PLAYLIST_RIGHTS, ROLE_RIGHTS,
    GROUP_USER, GROUP_PLAYLIST, PLAYLIST, TRACK, ARTIST, GENRE,
    USERS, USER_GROUP, RIGHTS, ROLE
RESTART IDENTITY CASCADE;

BEGIN;

INSERT INTO ROLE (roleName) VALUES
('USER'),
('MODERATOR'),
('ADMIN');

INSERT INTO RIGHTS (rightName) VALUES
('CREATE'),
('READ'),
('EDIT'),
('DELETE'),
('BAN_USER');


INSERT INTO ROLE_RIGHTS (idRole, idRight) VALUES
(3, 1), (3, 2), (3, 3), (3, 4), (3, 5);

INSERT INTO ROLE_RIGHTS (idRole, idRight) VALUES
(2, 2), (2, 4), (2, 5);

INSERT INTO ROLE_RIGHTS (idRole, idRight) VALUES
(1, 1), (1, 2), (1, 3);

INSERT INTO GENRE (label) VALUES
('Rock'), ('Pop'), ('Hip-Hop'), ('Classique'), ('Electro'), ('Jazz');

INSERT INTO ARTIST (name) VALUES
('Queen'), ('Daft Punk'), ('Eminem'), ('Mozart'), ('Adele'), ('Hans Zimmer');

INSERT INTO USER_GROUP (groupName) VALUES
('Les Etudiants'),
('Staff Admin'),
('Fans de Rock');

INSERT INTO USERS (username, email, password, idRole, isverified) VALUES
('SuperAdmin', 'admin@umontpellier.fr', '$2b$12$xnS.JxXR0Rij1Cw/60901Of0vVcowP8t1C5.TVB4ZGGjaS5XeUCSK', 3, TRUE),
('ModoSarah', 'sarah@etu.umontpellier.fr', '$2b$12$MfGljJQRrXEFoIXXniPzFueRzeO.wSwElO8U1uRqmq.f15VHw7kIK', 2, TRUE),
('AliceEtudiante', 'alice@etu.umontpellier.fr', '$2b$12$j538y6ALuA4i/ZN.N/xxjObHVeb5NnB9HNYIZo4tKfNfvEAIMzoJu', 1, TRUE),
('Charlie', 'charlie@umontpellier.fr', '$2b$12$fnRwsmyffcI00XeKK15W/.2/lsUvSN/7PThyDCbyboWuIkczRA5Ha', 1, FALSE);

INSERT INTO GROUP_USER (idUser, idGroup) VALUES
(1, 2),
(3, 1),
(4, 3),
(3, 3);

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
('Interstellar Main Theme', 'https://www.youtube.com/watch?v=zSWdZVtXT7E', 200000, 250);


INSERT INTO TRACK_ARTIST (idTrack, idArtist) VALUES
(1, 1), (6, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 6);

INSERT INTO PLAYLIST (name, idGenre, idOwner, visibility, vote, coverImage) VALUES
('Top 50 Polytech', 2, 1, 'PUBLIC', 999, 'asset:playlist1.jpg'),
('Chill Lofi Study', 3, 1, 'PRIVATE', 150, 'asset:playlist2.jpg'),
('Deep Focus', 4, 1, 'PRIVATE', 85, 'asset:playlist3.jpg'),
('Focus Travail', 4, 3, 'PRIVATE', 0, NULL),
('Mega Rock Party', 1, 4, 'PRIVATE', 50, 'asset:playlist1.jpg'),
('Découvertes Semaine', 5, 2, 'PUBLIC', 12, NULL),
('Best of 2023', 2, 1, 'PUBLIC', 500, 'asset:playlist2.jpg'),
('Workout Motivation', 5, 1, 'PUBLIC', 320, 'asset:playlist3.jpg'),
('Secret Guitara', 1, 1, 'PRIVATE', 10, NULL),
('Morning Coffee', 6, 3, 'PRIVATE', 45, 'asset:playlist1.jpg'),
('Coding Session', 5, 3, 'PRIVATE', 100, NULL),
('Hard Rock Essentials', 1, 4, 'PUBLIC', 666, 'asset:playlist2.jpg'),
('Gym Playlist', 3, 4, 'PRIVATE', 88, NULL),
('Classical Masterpieces', 4, 1, 'OPEN', 200, NULL),
('Late Night Jazz', 6, 4, 'PRIVATE', 30, NULL),
('Moderation Queue', 2, 2, 'PRIVATE', 0, NULL),
('Electro Vibes', 5, 1, 'PRIVATE', 210, NULL),
('Piano Dreams', 4, 1, 'OPEN', 150, 'asset:playlist3.jpg'),
('Rap US Gold', 3, 1, 'OPEN', 420, 'asset:playlist1.jpg'),
('Indie Pop Mix', 2, 4, 'PRIVATE', 75, NULL);

INSERT INTO TRACK_PLAYLIST (idTrack, idPlaylist, nameInPlaylist) VALUES
(2, 1, NULL),
(18, 1, 'Inception (Best OST)'),
(4, 2, NULL),
(5, 2, NULL),
(1, 3, NULL),
(2, 3, 'L hymne du stade');

INSERT INTO GROUP_PLAYLIST (idGroup, idPlaylist) VALUES (3, 3);
INSERT INTO USER_PLAYLIST (idUser, idPlaylist, editor) VALUES (3, 3, TRUE);
INSERT INTO PLAYLIST_RIGHTS (idPlaylist, idRight) VALUES (1, 2);

COMMIT;
