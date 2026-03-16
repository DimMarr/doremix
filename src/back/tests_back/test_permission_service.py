"""
Unit tests for PermissionService

Tests cover:
- Base role resolution
- Permission aggregation from multiple groups
- Ownership checks
- Banned user restrictions
- Admin bypass
- Resource-level access (playlists, users)
- Shared playlist editor logic
"""

import pytest
from sqlalchemy.orm import Session
from models.user import User, UserRole
from models.group import UserGroup, GroupUser, GroupPlaylist
from models.permissions import Permissions
from models.playlist import Playlist
from models.user_playlists import UserPlaylist
from models.enums import Actions, Ressources, PlaylistVisibility
from models.genre import Genre
from services.permission_service import PermissionService


@pytest.fixture
def setup_groups(db: Session):
    """Create the three main user groups"""
    groups = [
        UserGroup(groupName="Utilisateurs normaux"),
        UserGroup(groupName="Modérateurs"),
        UserGroup(groupName="Admins"),
    ]
    db.add_all(groups)
    db.commit()
    for group in groups:
        db.refresh(group)
    return groups


@pytest.fixture
def normal_user(db: Session, setup_groups):
    """Create a normal user with base role"""
    user = User(
        username="normaluser",
        email="normal@test.com",
        password="hashed_password",
        idRole=1,
        banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Assign to Utilisateurs normaux group as base role
    group_user = GroupUser(idUser=user.idUser, idGroup=1, isBaseRole=True)
    db.add(group_user)
    db.commit()

    return user


@pytest.fixture
def moderator_user(db: Session, setup_groups):
    """Create a moderator user with base role"""
    user = User(
        username="moderator",
        email="mod@test.com",
        password="hashed_password",
        idRole=2,
        banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Assign to Modérateurs group as base role
    group_user = GroupUser(idUser=user.idUser, idGroup=2, isBaseRole=True)
    db.add(group_user)
    db.commit()

    return user


@pytest.fixture
def admin_user(db: Session, setup_groups):
    """Create an admin user with base role"""
    user = User(
        username="admin",
        email="admin@test.com",
        password="hashed_password",
        idRole=3,
        banned=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Assign to Admins group as base role
    group_user = GroupUser(idUser=user.idUser, idGroup=3, isBaseRole=True)
    db.add(group_user)
    db.commit()

    return user


@pytest.fixture
def banned_user(db: Session, setup_groups):
    """Create a banned user"""
    user = User(
        username="banneduser",
        email="banned@test.com",
        password="hashed_password",
        idRole=1,
        banned=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Assign to Utilisateurs normaux group as base role
    group_user = GroupUser(idUser=user.idUser, idGroup=1, isBaseRole=True)
    db.add(group_user)
    db.commit()

    return user


@pytest.fixture
def setup_permissions(db: Session):
    """Create basic permissions for groups"""
    permissions = [
        # Normal users
        Permissions(action=Actions.CREATE, ressource=Ressources.PLAYLIST, groupId=1),
        Permissions(
            action=Actions.READ, ressource=Ressources.PLAYLIST_PUBLIC, groupId=1
        ),
        Permissions(action=Actions.EDIT, ressource=Ressources.PLAYLIST, groupId=1),
        # Moderators
        Permissions(action=Actions.CREATE, ressource=Ressources.PLAYLIST, groupId=2),
        Permissions(
            action=Actions.READ, ressource=Ressources.PLAYLIST_PUBLIC, groupId=2
        ),
        Permissions(action=Actions.BAN, ressource=Ressources.USER, groupId=2),
        # Admins
        Permissions(action=Actions.CREATE, ressource=Ressources.PLAYLIST, groupId=3),
        Permissions(action=Actions.DELETE, ressource=Ressources.PLAYLIST, groupId=3),
        Permissions(action=Actions.BAN, ressource=Ressources.USER, groupId=3),
    ]
    db.add_all(permissions)
    db.commit()


@pytest.fixture
def sample_genre(db: Session):
    """Create a test genre"""
    genre = Genre(label="Rock")
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


class TestBaseRoleResolution:
    """Test base role resolution from groups"""

    def test_get_base_role_normal_user(self, db: Session, normal_user, setup_groups):
        """Normal user should have USER base role"""
        PermissionService.clear_cache()
        role = PermissionService.get_base_role(db, normal_user.idUser)
        assert role == UserRole.USER

    def test_get_base_role_moderator(self, db: Session, moderator_user, setup_groups):
        """Moderator should have MODERATOR base role"""
        PermissionService.clear_cache()
        role = PermissionService.get_base_role(db, moderator_user.idUser)
        assert role == UserRole.MODERATOR

    def test_get_base_role_admin(self, db: Session, admin_user, setup_groups):
        """Admin should have ADMIN base role"""
        PermissionService.clear_cache()
        role = PermissionService.get_base_role(db, admin_user.idUser)
        assert role == UserRole.ADMIN

    def test_get_base_role_no_group(self, db: Session):
        """User without base role group should return None"""
        PermissionService.clear_cache()
        user = User(
            username="nogroup",
            email="nogroup@test.com",
            password="hashed_password",
            idRole=1,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        role = PermissionService.get_base_role(db, user.idUser)
        assert role is None


class TestPermissionAggregation:
    """Test permission aggregation from multiple groups"""

    def test_single_group_permissions(
        self, db: Session, normal_user, setup_permissions
    ):
        """User should get permissions from their base group"""
        PermissionService.clear_cache()
        permissions = PermissionService.get_effective_permissions(
            db, normal_user.idUser
        )

        assert (Actions.CREATE, Ressources.PLAYLIST) in permissions
        assert (Actions.READ, Ressources.PLAYLIST_PUBLIC) in permissions
        assert (Actions.BAN, Ressources.USER) not in permissions

    def test_multiple_group_permissions(
        self, db: Session, normal_user, setup_groups, setup_permissions
    ):
        """User should get merged permissions from all groups"""
        PermissionService.clear_cache()

        # Add user to moderator group (not as base role)
        group_user = GroupUser(idUser=normal_user.idUser, idGroup=2, isBaseRole=False)
        db.add(group_user)
        db.commit()

        PermissionService.clear_cache()
        permissions = PermissionService.get_effective_permissions(
            db, normal_user.idUser
        )

        # Should have permissions from both groups
        assert (Actions.CREATE, Ressources.PLAYLIST) in permissions
        assert (Actions.READ, Ressources.PLAYLIST_PUBLIC) in permissions
        assert (Actions.BAN, Ressources.USER) in permissions


class TestAdminBypass:
    """Test admin bypass logic"""

    def test_admin_bypass_all_permissions(
        self, db: Session, admin_user, setup_permissions
    ):
        """Admin should bypass all permission checks"""
        PermissionService.clear_cache()

        # Admin should be able to do anything, even without specific permissions
        assert PermissionService.hasPermissionsTo(
            db, admin_user, Actions.DELETE, Ressources.PLAYLIST
        )
        assert PermissionService.hasPermissionsTo(
            db, admin_user, Actions.BAN, Ressources.USER
        )
        # Even actions not in PERMISSIONS table
        assert PermissionService.hasPermissionsTo(
            db, admin_user, Actions.PROMOTE, Ressources.USER
        )


class TestBannedUsers:
    """Test banned user restrictions"""

    def test_banned_user_denied_most_actions(
        self, db: Session, banned_user, setup_permissions
    ):
        """Banned users should be denied most actions"""
        PermissionService.clear_cache()

        assert not PermissionService.hasPermissionsTo(
            db, banned_user, Actions.CREATE, Ressources.PLAYLIST
        )
        assert not PermissionService.hasPermissionsTo(
            db, banned_user, Actions.EDIT, Ressources.PLAYLIST
        )

    def test_banned_user_can_read_public(
        self, db: Session, banned_user, setup_permissions
    ):
        """Banned users should still be able to read public resources"""
        PermissionService.clear_cache()

        assert PermissionService.hasPermissionsTo(
            db, banned_user, Actions.READ, Ressources.PLAYLIST_PUBLIC
        )


class TestPlaylistOwnership:
    """Test playlist ownership checks"""

    def test_owner_has_full_access(
        self, db: Session, normal_user, sample_genre, setup_permissions
    ):
        """Playlist owner should have full access"""
        PermissionService.clear_cache()

        playlist = Playlist(
            name="My Playlist",
            idOwner=normal_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.PUBLIC,
        )
        db.add(playlist)
        db.commit()
        db.refresh(playlist)

        # Owner can edit their own playlist
        assert PermissionService.hasPermissionsTo(
            db, normal_user, Actions.EDIT, Ressources.PLAYLIST, playlist.idPlaylist
        )

    def test_non_owner_private_playlist(
        self, db: Session, normal_user, moderator_user, sample_genre, setup_permissions
    ):
        """Non-owner should not access private playlist"""
        PermissionService.clear_cache()

        playlist = Playlist(
            name="Private Playlist",
            idOwner=normal_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.PRIVATE,
        )
        db.add(playlist)
        db.commit()
        db.refresh(playlist)

        # Even moderator with permissions can't access private playlist they don't own
        assert not PermissionService.hasPermissionsTo(
            db,
            moderator_user,
            Actions.EDIT,
            Ressources.PLAYLIST_PRIVATE,
            playlist.idPlaylist,
        )


class TestSharedPlaylistAccess:
    """Test shared playlist editor logic"""

    def test_editor_can_edit_shared_playlist(
        self, db: Session, normal_user, moderator_user, sample_genre, setup_permissions
    ):
        """User with editor flag should be able to edit shared playlist"""
        PermissionService.clear_cache()

        # Create shared playlist owned by normal_user
        playlist = Playlist(
            name="Shared Playlist",
            idOwner=normal_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.OPEN,
        )
        db.add(playlist)
        db.commit()
        db.refresh(playlist)

        # Add moderator as editor
        user_playlist = UserPlaylist(
            idUser=moderator_user.idUser,
            idPlaylist=playlist.idPlaylist,
            editor=True,
        )
        db.add(user_playlist)
        db.commit()

        # Moderator should be able to edit
        assert PermissionService.hasPermissionsTo(
            db,
            moderator_user,
            Actions.EDIT,
            Ressources.PLAYLIST_SHARED,
            playlist.idPlaylist,
        )

    def test_non_editor_cannot_edit_shared_playlist(
        self, db: Session, normal_user, moderator_user, sample_genre, setup_permissions
    ):
        """User without editor flag should not be able to edit shared playlist"""
        PermissionService.clear_cache()

        # Create shared playlist owned by normal_user
        playlist = Playlist(
            name="Shared Playlist",
            idOwner=normal_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.OPEN,
        )
        db.add(playlist)
        db.commit()
        db.refresh(playlist)

        # Add moderator as non-editor
        user_playlist = UserPlaylist(
            idUser=moderator_user.idUser,
            idPlaylist=playlist.idPlaylist,
            editor=False,
        )
        db.add(user_playlist)
        db.commit()

        # Moderator should not be able to edit
        assert not PermissionService.hasPermissionsTo(
            db,
            moderator_user,
            Actions.EDIT,
            Ressources.PLAYLIST_SHARED,
            playlist.idPlaylist,
        )


class TestGroupPlaylistAccess:
    """Test group-based playlist access"""

    def test_group_member_can_access_group_playlist(
        self,
        db: Session,
        normal_user,
        moderator_user,
        sample_genre,
        setup_groups,
        setup_permissions,
    ):
        """User in group should be able to access group playlist"""
        PermissionService.clear_cache()

        # Create playlist owned by moderator
        playlist = Playlist(
            name="Group Playlist",
            idOwner=moderator_user.idUser,
            idGenre=sample_genre.idGenre,
            visibility=PlaylistVisibility.OPEN,
        )
        db.add(playlist)
        db.commit()
        db.refresh(playlist)

        # Associate playlist with group 1 (Utilisateurs normaux)
        group_playlist = GroupPlaylist(idGroup=1, idPlaylist=playlist.idPlaylist)
        db.add(group_playlist)
        db.commit()

        # Normal user (in group 1) should be able to access
        assert PermissionService.hasPermissionsTo(
            db,
            normal_user,
            Actions.READ,
            Ressources.PLAYLIST_SHARED,
            playlist.idPlaylist,
        )


class TestUserActionTarget:
    """Test user action target restrictions"""

    def test_cannot_ban_admin(
        self, db: Session, moderator_user, admin_user, setup_permissions
    ):
        """Moderator should not be able to ban admin"""
        PermissionService.clear_cache()

        # Moderator has BAN permission
        assert not PermissionService.hasPermissionsTo(
            db, moderator_user, Actions.BAN, Ressources.USER, admin_user.idUser
        )

    def test_can_ban_normal_user(
        self, db: Session, moderator_user, normal_user, setup_permissions
    ):
        """Moderator should be able to ban normal user"""
        PermissionService.clear_cache()

        assert PermissionService.hasPermissionsTo(
            db, moderator_user, Actions.BAN, Ressources.USER, normal_user.idUser
        )


class TestCaching:
    """Test permission caching functionality"""

    def test_cache_is_used(self, db: Session, normal_user, setup_permissions):
        """Verify that cache reduces database queries"""
        PermissionService.clear_cache()

        # First call should populate cache
        perms1 = PermissionService.get_effective_permissions(db, normal_user.idUser)

        # Second call should use cache (same result)
        perms2 = PermissionService.get_effective_permissions(db, normal_user.idUser)

        assert perms1 == perms2

    def test_cache_clear(self, db: Session, normal_user, setup_permissions):
        """Verify cache can be cleared"""
        PermissionService.clear_cache()

        # Populate cache
        PermissionService.get_effective_permissions(db, normal_user.idUser)

        # Clear cache
        PermissionService.clear_cache()

        # Cache should be empty
        assert len(PermissionService._permission_cache) == 0
        assert len(PermissionService._group_cache) == 0
        assert len(PermissionService._base_role_cache) == 0
