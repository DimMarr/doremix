from typing import cast

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.playlist import Playlist
from models.playlist_vote import PlaylistVote


class VoteRepository:
    @staticmethod
    def _get_insert_statement(db: AsyncSession):
        dialect_name = db.get_bind().dialect.name
        if dialect_name == "postgresql":
            return pg_insert(PlaylistVote)
        if dialect_name == "sqlite":
            return sqlite_insert(PlaylistVote)
        raise RuntimeError(f"Unsupported SQL dialect for vote upsert: {dialect_name}")

    @staticmethod
    async def upsert_vote(
        db: AsyncSession, iduser: int, idplaylist: int, value: int
    ) -> tuple[int, int | None]:
        if value == 0:
            existing_vote = await db.get(
                PlaylistVote, {"idUser": iduser, "idPlaylist": idplaylist}
            )
            if existing_vote:
                await db.delete(existing_vote)
        else:
            insert_stmt = VoteRepository._get_insert_statement(db).values(
                idUser=iduser,
                idPlaylist=idplaylist,
                value=value,
            )
            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=["iduser", "idplaylist"],
                set_={"value": value},
            )
            await db.execute(upsert_stmt)

        await db.flush()
        aggregate_score = (
            select(func.coalesce(func.sum(PlaylistVote.value), 0))
            .where(PlaylistVote.idPlaylist == idplaylist)
            .scalar_subquery()
        )
        await db.execute(
            update(Playlist)
            .where(Playlist.idPlaylist == idplaylist)
            .values(vote=aggregate_score)
        )
        await db.commit()

        score_result = await db.execute(
            select(Playlist.vote).where(Playlist.idPlaylist == idplaylist)
        )
        score = score_result.scalar_one_or_none() or 0
        user_vote = await VoteRepository.get_user_vote(db, iduser, idplaylist)
        return score, user_vote

    @staticmethod
    async def get_user_vote(
        db: AsyncSession, iduser: int, idplaylist: int
    ) -> int | None:
        result = await db.execute(
            select(PlaylistVote.value).where(
                PlaylistVote.idUser == iduser,
                PlaylistVote.idPlaylist == idplaylist,
            )
        )
        return cast(int | None, result.scalar_one_or_none())
