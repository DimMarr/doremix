UPDATE playlist
SET vote = COALESCE(vote_totals.score, 0)
FROM (
    SELECT
        playlist.idplaylist,
        COALESCE(SUM(playlist_vote.value), 0) AS score
    FROM playlist
    LEFT JOIN playlist_vote
        ON playlist_vote.idplaylist = playlist.idplaylist
    GROUP BY playlist.idplaylist
) AS vote_totals
WHERE vote_totals.idplaylist = playlist.idplaylist;
