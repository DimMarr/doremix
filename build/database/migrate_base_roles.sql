-- -- Migration script to assign base roles to existing users
-- -- This script should be run on existing databases to add isBaseRole flags
-- -- based on users' current idRole field.

-- -- This migration assumes:
-- -- - GROUP 1 = "Utilisateurs normaux" (USER role)
-- -- - GROUP 2 = "Modérateurs" (MODERATOR role)
-- -- - GROUP 3 = "Admins" (ADMIN role)

-- BEGIN;

-- -- First, ensure the isBaseRole column exists (it may have been added by init.sql)
-- -- This is safe to run even if the column already exists
-- DO $$
-- BEGIN
--     IF NOT EXISTS (
--         SELECT 1
--         FROM information_schema.columns
--         WHERE table_name='group_user'
--         AND column_name='isbaserole'
--     ) THEN
--         ALTER TABLE GROUP_USER ADD COLUMN isBaseRole BOOLEAN DEFAULT FALSE;
--     END IF;
-- END $$;

-- -- Update existing GROUP_USER relationships to set base roles
-- -- based on the user's idRole field

-- -- For users with idRole = 1 (USER), set their membership in group 1 as base role
-- UPDATE GROUP_USER gu
-- SET isBaseRole = TRUE
-- WHERE gu.idGroup = 1
--   AND gu.idUser IN (
--     SELECT idUser FROM USERS WHERE idRole = 1
--   );

-- -- For users with idRole = 2 (MODERATOR), set their membership in group 2 as base role
-- UPDATE GROUP_USER gu
-- SET isBaseRole = TRUE
-- WHERE gu.idGroup = 2
--   AND gu.idUser IN (
--     SELECT idUser FROM USERS WHERE idRole = 2
--   );

-- -- For users with idRole = 3 (ADMIN), set their membership in group 3 as base role
-- UPDATE GROUP_USER gu
-- SET isBaseRole = TRUE
-- WHERE gu.idGroup = 3
--   AND gu.idUser IN (
--     SELECT idUser FROM USERS WHERE idRole = 3
--   );

-- -- Ensure users who don't have their base role group are added to it
-- -- Add USER role group (1) for users with idRole=1 who aren't in it
-- INSERT INTO GROUP_USER (idUser, idGroup, isBaseRole)
-- SELECT u.idUser, 1, TRUE
-- FROM USERS u
-- WHERE u.idRole = 1
--   AND NOT EXISTS (
--     SELECT 1 FROM GROUP_USER gu
--     WHERE gu.idUser = u.idUser AND gu.idGroup = 1
--   );

-- -- Add MODERATOR role group (2) for users with idRole=2 who aren't in it
-- INSERT INTO GROUP_USER (idUser, idGroup, isBaseRole)
-- SELECT u.idUser, 2, TRUE
-- FROM USERS u
-- WHERE u.idRole = 2
--   AND NOT EXISTS (
--     SELECT 1 FROM GROUP_USER gu
--     WHERE gu.idUser = u.idUser AND gu.idGroup = 2
--   );

-- -- Add ADMIN role group (3) for users with idRole=3 who aren't in it
-- INSERT INTO GROUP_USER (idUser, idGroup, isBaseRole)
-- SELECT u.idUser, 3, TRUE
-- FROM USERS u
-- WHERE u.idRole = 3
--   AND NOT EXISTS (
--     SELECT 1 FROM GROUP_USER gu
--     WHERE gu.idUser = u.idUser AND gu.idGroup = 3
--   );

-- -- Verification: Check that each user has exactly ONE base role
-- DO $$
-- DECLARE
--     invalid_count INTEGER;
-- BEGIN
--     SELECT COUNT(DISTINCT gu.idUser)
--     INTO invalid_count
--     FROM GROUP_USER gu
--     WHERE gu.isBaseRole = TRUE
--     GROUP BY gu.idUser
--     HAVING COUNT(*) > 1;

--     IF invalid_count > 0 THEN
--         RAISE WARNING 'Found % users with multiple base roles. Please review GROUP_USER table.', invalid_count;
--     END IF;
-- END $$;

-- -- Log the migration results
-- DO $$
-- DECLARE
--     total_users INTEGER;
--     users_with_base_role INTEGER;
-- BEGIN
--     SELECT COUNT(*) INTO total_users FROM USERS;
--     SELECT COUNT(DISTINCT idUser) INTO users_with_base_role
--     FROM GROUP_USER WHERE isBaseRole = TRUE;

--     RAISE NOTICE 'Migration complete:';
--     RAISE NOTICE '  Total users: %', total_users;
--     RAISE NOTICE '  Users with base role: %', users_with_base_role;
--     RAISE NOTICE '  Users without base role: %', total_users - users_with_base_role;
-- END $$;

-- COMMIT;
