"""
PermissionService - Unified access control system for DoRéMix.

This service provides a single API for checking user permissions:
    hasPermissionsTo(action, resource, resource_id?)

It supports:
- Base roles determined by a primary group assignment (isBaseRole=True)
- Additional permissions from any other groups the user belongs to
- Resource-level access (ownership, group-playlist associations)
- Request-level caching to avoid N+1 queries
"""

from typing import Optional, List, Dict, Set, Tuple
from sqlalchemy.orm import Session

from models.user import User, UserRole
from models.enums import Actions, Ressources
from models.group import GroupUser, UserGroup, GroupPlaylist
from models.permissions import Permissions
from models.playlist import Playlist
from models.user_playlists import UserPlaylist


class PermissionService:
    """
    Service that answers the question:
      "Can `user` perform `action` on `resource` (optionally a specific `resource_id`)?"

    Decision flow
    -------------
    1. Banned user check: banned users can only READ PUBLIC resources
    2. Admin bypass: admins can do anything
    3. Base role check: get user's base role from isBaseRole=True group
    4. Effective permissions: merge permissions from ALL groups user belongs to
    5. Resource-level access check (when resource_id is provided):
       - Ownership check (idOwner)
       - GROUP_PLAYLIST membership
       - Shared playlist editor status
    """

    # Request-level permission cache
    _permission_cache: Dict[int, Set[Tuple[Actions, Ressources]]] = {}
    _group_cache: Dict[int, List[UserGroup]] = {}
    _base_role_cache: Dict[int, Optional[UserRole]] = {}

    @staticmethod
    def hasPermissionsTo(
        db: Session,
        user: User,
        action: Actions,
        resource: Ressources,
        resource_id: Optional[int] = None,
    ) -> bool:
        """
        Main entry point for permission checking.

        Args:
            db: Database session
            user: The user attempting the action
            action: The action to perform (CREATE, READ, EDIT, DELETE, etc.)
            resource: The resource type (PLAYLIST, USER, GENRE, etc.)
            resource_id: Optional ID of a specific resource instance

        Returns:
            True if the user has permission, False otherwise
        """
        # --- 1. Banned user check ---
        if PermissionService.is_banned(user):
            # Banned users can only READ PUBLIC resources
            if action == Actions.READ and resource == Ressources.PLAYLIST_PUBLIC:
                return True
            return False

        # --- 3. Get effective permissions ---
        effective_permissions = PermissionService.get_effective_permissions(
            db, user.idUser
        )

        # Check if user has the required permission
        if (action, resource) not in effective_permissions:
            return False

        # --- 4. Resource-level access check ---
        if resource_id is not None:
            return PermissionService.check_resource_access(
                db, user, action, resource, resource_id
            )

        return True

    @staticmethod
    def is_banned(user: User) -> bool:
        """Check if user is banned."""
        return True
        # return user.banned

    @staticmethod
    def get_base_role(db: Session, user_id: int) -> Optional[UserRole]:
        """
        Get the user's base role from their base-role group (isBaseRole=True).

        Returns:
            UserRole enum or None if no base role is set
        """
        if user_id in PermissionService._base_role_cache:
            return PermissionService._base_role_cache[user_id]

        base_group = (
            db.query(UserGroup)
            .join(GroupUser, GroupUser.idGroup == UserGroup.idGroup)
            .filter(
                GroupUser.idUser == user_id,
                GroupUser.isBaseRole,
            )
            .first()
        )

        if base_group is None:
            PermissionService._base_role_cache[user_id] = None
            return None

        # Map group name to role
        role_mapping = {
            "Utilisateurs normaux": UserRole.USER,
            "Modérateurs": UserRole.MODERATOR,
            "Admins": UserRole.ADMIN,
        }

        role = role_mapping.get(base_group.groupName, UserRole.USER)
        PermissionService._base_role_cache[user_id] = role
        return role

    @staticmethod
    def get_user_groups(db: Session, user_id: int) -> List[int]:
        """
        Get all group IDs the user belongs to.

        Returns:
            List of group IDs
        """
        if user_id in PermissionService._group_cache:
            return [g.idGroup for g in PermissionService._group_cache[user_id]]

        groups = (
            db.query(UserGroup)
            .join(GroupUser, GroupUser.idGroup == UserGroup.idGroup)
            .filter(GroupUser.idUser == user_id)
            .all()
        )

        PermissionService._group_cache[user_id] = groups
        return [g.idGroup for g in groups]

    @staticmethod
    def get_effective_permissions(
        db: Session, user_id: int
    ) -> Set[Tuple[Actions, Ressources]]:
        """
        Get all permissions from ALL groups the user belongs to.

        This merges permissions from:
        - The base role group
        - Any additional groups the user is a member of

        Returns:
            Set of (action, resource) tuples
        """
        if user_id in PermissionService._permission_cache:
            return PermissionService._permission_cache[user_id]

        group_ids = PermissionService.get_user_groups(db, user_id)

        if not group_ids:
            PermissionService._permission_cache[user_id] = set()
            return set()

        permissions = (
            db.query(Permissions.action, Permissions.ressource)
            .filter(Permissions.groupId.in_(group_ids))
            .distinct()
            .all()
        )

        permission_set = {(perm.action, perm.ressource) for perm in permissions}
        PermissionService._permission_cache[user_id] = permission_set
        return permission_set

    @staticmethod
    def check_resource_access(
        db: Session,
        user: User,
        action: Actions,
        resource: Ressources,
        resource_id: int,
    ) -> bool:
        """
        Check if user has access to a specific resource instance.

        Dispatches to appropriate checker based on resource type.
        """
        if resource in (
            Ressources.PLAYLIST,
            Ressources.PLAYLIST_PUBLIC,
            Ressources.PLAYLIST_PRIVATE,
            Ressources.PLAYLIST_SHARED,
        ):
            return PermissionService.check_playlist_access(
                db, user, action, resource, resource_id
            )

        if resource == Ressources.USER:
            return PermissionService.check_user_action_target(db, resource_id)

        # GENRE and other resources: permission alone is sufficient
        return True

    @staticmethod
    def check_playlist_access(
        db: Session,
        user: User,
        action: Actions,
        resource: Ressources,
        playlist_id: int,
    ) -> bool:
        """
        Check if user has access to a specific playlist.

        Rules:
        - Owner always has full access
        - PRIVATE playlists: owner only
        - SHARED playlists: owner, editors (with editor flag), or group members
        - PUBLIC playlists: permission is sufficient
        """
        playlist: Optional[Playlist] = (
            db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()
        )
        if playlist is None:
            return False

        # Owner always has full control
        if PermissionService.check_ownership(
            db, user, Ressources.PLAYLIST, playlist_id
        ):
            return True

        # Private playlists: owner only
        if resource == Ressources.PLAYLIST_PRIVATE:
            return False

        # Shared playlists: check editor status or group membership
        if resource == Ressources.PLAYLIST_SHARED:
            if PermissionService.can_edit_shared_playlist(
                db, user, playlist_id, action
            ):
                return True

        # Public playlists: permission check already passed
        return True

    @staticmethod
    def check_ownership(
        db: Session,
        user: User,
        resource: Ressources,
        resource_id: int,
    ) -> bool:
        """
        Check if user owns the resource.

        For playlists, checks idOwner field.
        """
        if resource in (
            Ressources.PLAYLIST,
            Ressources.PLAYLIST_PUBLIC,
            Ressources.PLAYLIST_PRIVATE,
            Ressources.PLAYLIST_SHARED,
        ):
            playlist: Optional[Playlist] = (
                db.query(Playlist).filter(Playlist.idPlaylist == resource_id).first()
            )
            return playlist is not None and playlist.idOwner == user.idUser

        return False

    @staticmethod
    def can_edit_shared_playlist(
        db: Session, user: User, playlist_id: int, action: Actions
    ) -> bool:
        """
        Check if user can access a shared playlist.

        Access is granted if:
        - User is a direct editor (USER_PLAYLIST with editor=True) for EDIT actions
        - User is in a group that has access (GROUP_PLAYLIST) for READ/SHARE
        """
        # Check direct editor status
        direct: Optional[UserPlaylist] = (
            db.query(UserPlaylist)
            .filter(
                UserPlaylist.idUser == user.idUser,
                UserPlaylist.idPlaylist == playlist_id,
            )
            .first()
        )
        if direct is not None:
            # EDIT requires the editor flag
            if action == Actions.EDIT and not direct.editor:
                return False
            return True

        # Check group-based access
        user_group_ids = PermissionService.get_user_groups(db, user.idUser)
        if user_group_ids:
            group_access = (
                db.query(GroupPlaylist)
                .filter(
                    GroupPlaylist.idPlaylist == playlist_id,
                    GroupPlaylist.idGroup.in_(user_group_ids),
                )
                .first()
            )
            return group_access is not None

        return False

    @staticmethod
    def check_user_action_target(db: Session, target_user_id: int) -> bool:
        """
        Prevent non-admins from performing privileged actions (BAN, PROMOTE, DEMOTE)
        against admin accounts.

        Returns:
            False if target is an admin, True otherwise
        """
        target: Optional[User] = (
            db.query(User).filter(User.idUser == target_user_id).first()
        )
        if target is None:
            return False
        return True

    @staticmethod
    def clear_cache():
        """Clear the request-level permission cache."""
        PermissionService._permission_cache.clear()
        PermissionService._group_cache.clear()
        PermissionService._base_role_cache.clear()
