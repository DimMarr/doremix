from typing import Optional

from sqlalchemy.orm import Session

from models.enums import Actions, Ressources
from models.permissions import Permissions
from models.user import User, UserRole
from models.group import GroupUser, GroupPlaylist
from models.playlist import Playlist
from models.user_playlists import UserPlaylist


class AccessControlService:
    """
    Service that answers the question:
      "Can `user` perform `action` on `resource` (optionally a specific `resource_id`)?"

    Decision flow
    -------------
    1. Admins bypass every check — they can do anything.
    2. Group-permission check: the user must belong to at least one USER_GROUP whose
       PERMISSIONS row matches (action, resource).
    3. Resource-level ownership check (only when resource_id is provided):
       - PLAYLIST_PRIVATE  → only the owner may act on it.
       - PLAYLIST_SHARED   → owner, direct USER_PLAYLIST members (editors only for EDIT),
                             or members of a GROUP_PLAYLIST group.
       - PLAYLIST / PLAYLIST_PUBLIC → no extra ownership constraint.
       - USER              → the target user must not be an admin
                             (moderators cannot act on admins).
    """

    @staticmethod
    def can(
        db: Session,
        user: User,
        action: Actions,
        resource: Ressources,
        resource_id: Optional[int] = None,
    ) -> bool:
        # --- 1. Admin bypass ---
        if user.role == UserRole.ADMIN:
            return True

        # --- 2. Group-permission check ---
        if not AccessControlService._has_group_permission(
            db, user.idUser, action, resource
        ):
            return False

        # --- 3. Ownership / access constraint (requires a concrete resource) ---
        if resource_id is not None:
            return AccessControlService._check_resource_access(
                db, user, action, resource, resource_id
            )

        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _has_group_permission(
        db: Session,
        user_id: int,
        action: Actions,
        resource: Ressources,
    ) -> bool:
        """Return True if the user belongs to any group that holds (action, resource)."""
        result = (
            db.query(Permissions)
            .join(GroupUser, GroupUser.idGroup == Permissions.groupId)
            .filter(
                GroupUser.idUser == user_id,
                Permissions.action == action,
                Permissions.ressource == resource,
            )
            .first()
        )
        return result is not None

    @staticmethod
    def _check_resource_access(
        db: Session,
        user: User,
        action: Actions,
        resource: Ressources,
        resource_id: int,
    ) -> bool:
        """Dispatch to the appropriate ownership/access checker."""
        if resource in (
            Ressources.PLAYLIST,
            Ressources.PLAYLIST_PUBLIC,
            Ressources.PLAYLIST_PRIVATE,
            Ressources.PLAYLIST_SHARED,
        ):
            return AccessControlService._check_playlist_access(
                db, user, action, resource, resource_id
            )

        if resource == Ressources.USER:
            return AccessControlService._check_user_action_target(db, resource_id)

        # GENRE and other resources: permission alone is sufficient
        return True

    @staticmethod
    def _check_playlist_access(
        db: Session,
        user: User,
        action: Actions,
        resource: Ressources,
        playlist_id: int,
    ) -> bool:
        playlist: Optional[Playlist] = (
            db.query(Playlist).filter(Playlist.idPlaylist == playlist_id).first()
        )
        if playlist is None:
            return False

        # The owner always has full control over their own playlist
        if playlist.idOwner == user.idUser:
            return True

        # Private playlists: owner only
        if resource == Ressources.PLAYLIST_PRIVATE:
            return False

        # Shared playlists: direct membership or group membership
        if resource == Ressources.PLAYLIST_SHARED:
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

            # Group-based access (read/share only — not edit)
            user_group_ids = db.query(GroupUser.idGroup).filter(
                GroupUser.idUser == user.idUser
            )
            group_access = (
                db.query(GroupPlaylist)
                .filter(
                    GroupPlaylist.idPlaylist == playlist_id,
                    GroupPlaylist.idGroup.in_(user_group_ids),
                )
                .first()
            )
            return group_access is not None

        # PLAYLIST / PLAYLIST_PUBLIC: group permission alone is enough
        return True

    @staticmethod
    def _check_user_action_target(db: Session, target_user_id: int) -> bool:
        """
        Prevent non-admins from performing privileged actions (BAN, PROMOTE, DEMOTE)
        against admin accounts.
        """
        target: Optional[User] = (
            db.query(User).filter(User.idUser == target_user_id).first()
        )
        if target is None:
            return False
        return target.role != UserRole.ADMIN
