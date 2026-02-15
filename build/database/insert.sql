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

INSERT INTO USERS (username, email, password, idRole, banned) VALUES
('SuperAdmin', 'admin@umontpellier.fr', 'root123', 3, FALSE),
('ModoSarah', 'sarah@etu.umontpellier.fr', 'modoPass', 2, FALSE),
('AliceEtudiante', 'alice@etu.umontpellier.fr', 'passA', 1, FALSE),
('BobRocker', 'bob@etu.umontpellier.fr', 'passB', 1, FALSE),
('Charlie', 'charlie@etu.umontpellier.frm', 'passC', 1, FALSE),
('DaveHacker', 'dave@evil.com', 'hack', 1, TRUE);

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
('Top 50 Polytech', 2, 1, 'PUBLIC', 999, 'https://static.vecteezy.com/vite/assets/photo-masthead-375-BoK_p8LG.webp'),
('Chill Lofi Study', 3, 1, 'PRIVATE', 150, 'https://images.unsplash.com/photo-1516280440614-37939bbacd81?q=80&w=1000&auto=format&fit=crop'),
('Deep Focus', 4, 1, 'PRIVATE', 85, 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?q=80&w=1000&auto=format&fit=crop'),
('Focus Travail', 4, 3, 'PRIVATE', 0, NULL),
('Mega Rock Party', 1, 4, 'PRIVATE', 50, 'https://img.freepik.com/photos-gratuite/homme-du-courage-passe-travers-ecart-entre-colline-idee-concept-entreprise_1323-262.jpg?semt=ais_user_personalization&w=740&q=80'),
('Découvertes Semaine', 5, 2, 'PUBLIC', 12, NULL),
('Best of 2023', 2, 1, 'PUBLIC', 500, 'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?q=80&w=1000&auto=format&fit=crop'),
('Workout Motivation', 5, 1, 'PUBLIC', 320, 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?q=80&w=1000&auto=format&fit=crop'),
('Secret Guitara', 1, 1, 'PRIVATE', 10, NULL),
('Morning Coffee', 6, 3, 'PRIVATE', 45, 'https://images.unsplash.com/photo-1511920170033-f8396924c348?q=80&w=1000&auto=format&fit=crop'),
('Coding Session', 5, 3, 'PRIVATE', 100, NULL),
('Hard Rock Essentials', 1, 4, 'PUBLIC', 666, 'https://images.unsplash.com/photo-1498038432885-c6f3f1b912ee?q=80&w=1000&auto=format&fit=crop'),
('Gym Playlist', 3, 4, 'PRIVATE', 88, NULL),
('Classical Masterpieces', 4, 5, 'OPEN', 200, NULL),
('Late Night Jazz', 6, 5, 'PRIVATE', 30, NULL),
('Moderation Queue', 2, 2, 'PRIVATE', 0, NULL),
('Electro Vibes', 5, 1, 'PRIVATE', 210, NULL),
('Piano Dreams', 4, 3, 'OPEN', 150, 'https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?q=80&w=1000&auto=format&fit=crop'),
('Rap US Gold', 3, 4, 'OPEN', 420, 'https://images.unsplash.com/photo-1581368135153-a506cf13b1e1?q=80&w=1000&auto=format&fit=crop'),
('Indie Pop Mix', 2, 5, 'PRIVATE', 75, NULL);

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
