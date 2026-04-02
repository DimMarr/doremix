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

INSERT INTO ARTIST (name, imageurl) VALUES
('Queen Official', 'https://yt3.googleusercontent.com/EBVYQCd4NEa7Io8bvLUxvq8HBnIUJ-BRp-cHkEUVl6u9Xj91TAADo5lh9Xzf5riI6wGIF_GAD-8=s0'),
('Daft Punk', 'https://yt3.googleusercontent.com/XPIjND5mm2nuSIJ6uQyIWLCawnIYSVm6QS0GEN_UNuPLRD5EFa6yCkYrcyLpl3TFuBo6AZynsA=s0'),
('EminemMusic', 'https://yt3.googleusercontent.com/fYB3KuH8P5jyoReOqbDRyHQJjfKsPj-BYDcJb1XANiEpo6bhCf6LXpsNxE9_fvefub9S1hCkldU=s800-c-k-c0x00ffffff-no-rj'),
('Adele', 'https://yt3.googleusercontent.com/BkJSG0gIJTKyUziqxJOdtJSjXbPNtOelrBBFjRoOaa_xcFgaptqm8hvHxbh46P4uZc4lV3f4=s0'),
('Metallica', 'https://yt3.googleusercontent.com/DW22K4fVgbvTl6Cx8uXFW9Nz_d2Bdn86npenO4pxzgH5fqAieB-nEYlX1ICnVG4zRIcvqUmrX4w=s0'),
('The Weeknd', 'https://yt3.googleusercontent.com/WHvw1ak1FcJaHeEiTmG2iN0dqEjjPxAtT_tA8ruJ3MlNr9I-RHsAur1iAenYeQN_d6LNPH2Z8Ic=s0'),
('Kendrick Lamar', 'https://yt3.googleusercontent.com/j1szYhuen1uT1D1icpjxHMFyBc0xINWK1eMtSzrB0TL5jliB7t3JB_wJ6UA9twV7VelxpKEc=s0'),
('Rihanna', 'https://yt3.googleusercontent.com/qMCGjRaKKRar82KzcIWdUoLbJ03aW2K2sEf-m4GaB7JwLshoHOZHvkxLRXsZVgpKvqCXVhKCWg=s0'),
('Miles Davis', 'https://yt3.googleusercontent.com/H4NIbxVIIA5bubjmg9LeCHefQuR-TMQikw4-CKcyIBJ4LZeyvRPn_LTlnNKHTwasbZOXE2mq=s0');

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
(2, 1),
(2, 2),
(2, 3),
(3, 1),
(4, 3),
(3, 3);

INSERT INTO TRACK (title, youtubeLink, listeningCount, durationSeconds, status) VALUES
('Bohemian Rhapsody', 'https://www.youtube.com/watch?v=fJ9rUzIMcZQ', 15000000, 354, 'ok'),
('We Will Rock You', 'https://www.youtube.com/watch?v=-tJYN-eG1zk', 8000000, 121, 'ok'),
('Enter Sandman', 'https://www.youtube.com/watch?v=CD-E-LDc384', 5000000, 331, 'ok'),
('Nothing Else Matters', 'https://www.youtube.com/watch?v=tAGnKpE4NCI', 6500000, 388, 'ok'),
('Get Lucky', 'https://www.youtube.com/watch?v=5NV6Rdv1a3I', 980000, 248, 'ok'),
('Instant Crush', 'https://www.youtube.com/watch?v=PtFMh6T4F5A', 450000, 337, 'ok'),
('Rolling in the Deep', 'https://www.youtube.com/watch?v=rYEDA3JcQqw', 2100000, 228, 'ok'),
('Someone Like You', 'https://www.youtube.com/watch?v=hLQl3WQQoQ0', 1800000, 285, 'ok'),
('Blinding Lights', 'https://www.youtube.com/watch?v=4NRXx6U8ABQ', 3500000, 200, 'ok'),
('Starboy', 'https://www.youtube.com/watch?v=34Na4j8AVgA', 2900000, 230, 'ok'),
('Lose Yourself', 'https://www.youtube.com/watch?v=7bDLIV96LD4', 4000000, 326, 'ok'),
('Stan', 'https://www.youtube.com/watch?v=gOMhN-hfMtY', 1200000, 384, 'ok'),
('HUMBLE.', 'https://www.youtube.com/watch?v=tvTRZJ-4EyI', 3100000, 177, 'ok'),
('Umbrella', 'https://www.youtube.com/watch?v=CvBfHwUxHIk', 5500000, 275, 'ok'),
('So What', 'https://www.youtube.com/watch?v=ylXk1LBvIqU', 45000, 562, 'ok'),
('Blue in Green', 'https://www.youtube.com/watch?v=PoPL7BExSQU', 30000, 327, 'ok');


INSERT INTO TRACK_ARTIST (idTrack, idArtist) VALUES
(1, 1), (2, 1),    -- Queen
(5, 2), (6, 2),    -- Daft Punk
(11, 3), (12, 3),  -- Eminem
(7, 4), (8, 4),    -- Adele
(3, 5), (4, 5),    -- Metallica
(9, 6), (10, 6),   -- The Weeknd
(13, 7),           -- Kendrick Lamar
(14, 8),          -- Rihanna
(15, 9), (16, 9); -- Miles Davis

INSERT INTO PLAYLIST (name, idGenre, idOwner, visibility, vote, coverImage) VALUES
('Top 50 Polytech', 2, 1, 'PUBLIC', 0, 'asset:playlist1.jpg'),
('Chill Lofi Study', 3, 1, 'PRIVATE', 0, 'asset:playlist2.jpg'),
('Deep Focus', 4, 1, 'PRIVATE', 0, 'asset:playlist3.jpg'),
('Focus Travail', 4, 3, 'PRIVATE', 0, NULL),
('Mega Rock Party', 1, 4, 'PRIVATE', 0, 'asset:playlist1.jpg'),
('Découvertes Semaine', 5, 2, 'PUBLIC', 0, NULL),
('Best of 2023', 2, 1, 'PUBLIC', 0, 'asset:playlist2.jpg'),
('Workout Motivation', 5, 1, 'PUBLIC', 0, 'asset:playlist3.jpg'),
('Secret Guitara', 1, 1, 'PRIVATE', 0, NULL),
('Morning Coffee', 6, 3, 'PRIVATE', 0, 'asset:playlist1.jpg'),
('Coding Session', 5, 3, 'PRIVATE', 0, NULL),
('Hard Rock Essentials', 1, 4, 'PUBLIC', 0, 'asset:playlist2.jpg'),
('Gym Playlist', 3, 4, 'PRIVATE', 0, NULL),
('Classical Masterpieces', 4, 1, 'OPEN', 0, NULL),
('Late Night Jazz', 6, 4, 'PRIVATE', 0, NULL),
('Moderation Queue', 2, 2, 'PRIVATE', 0, NULL),
('Electro Vibes', 5, 1, 'PRIVATE', 0, NULL),
('Piano Dreams', 4, 1, 'OPEN', 0, 'asset:playlist3.jpg'),
('Rap US Gold', 3, 1, 'OPEN', 0, 'asset:playlist1.jpg'),
('Indie Pop Mix', 2, 4, 'PRIVATE', 0, NULL);

INSERT INTO TRACK_PLAYLIST (idTrack, idPlaylist, nameInPlaylist, next_track_id) VALUES
(2, 1, NULL, 16),
(16, 1, 'Inception (Best OST)', 3),
(3, 1, NULL, 4),
(4, 1, NULL, 5),
(5, 1, NULL, NULL),
(4, 2, NULL, 5),
(5, 2, NULL, NULL),
(1, 3, NULL, 2),
(2, 3, 'L hymne du stade', NULL);

INSERT INTO GROUP_PLAYLIST (idGroup, idPlaylist) VALUES (3, 3);
INSERT INTO USER_PLAYLIST (idUser, idPlaylist, editor) VALUES (3, 3, TRUE);
INSERT INTO PLAYLIST_RIGHTS (idPlaylist, idRight) VALUES (1, 2);

COMMIT;
