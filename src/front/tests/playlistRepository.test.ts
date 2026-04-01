import { describe, it, expect, vi, beforeEach } from "vitest";

// Stub fetch globally
const mockFetch = vi.fn();
vi.stubGlobal("fetch", mockFetch);

describe("PlaylistRepository.getAll", () => {
  beforeEach(() => {
    mockFetch.mockReset();
  });

  it("sets image to undefined when coverImage is null", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => [
        {
          idPlaylist: 1,
          name: "Test",
          coverImage: null,
          visibility: "public",
          vote: 0,
          userVote: null,
          genre: null,
        },
      ],
    });

    const { PlaylistRepository } = await import("../repositories/playlistRepository");
    const repo = new PlaylistRepository();
    const playlists = await repo.getAll();

    expect(playlists[0].image).toBeUndefined();
  });

  it("resolves image URL when coverImage is a path", async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => [
        {
          idPlaylist: 2,
          name: "With Cover",
          coverImage: "abc123.jpg",
          visibility: "public",
          vote: 0,
          userVote: null,
          genre: null,
        },
      ],
    });

    const { PlaylistRepository } = await import("../repositories/playlistRepository");
    const repo = new PlaylistRepository();
    const playlists = await repo.getAll();

    expect(playlists[0].image).toContain("abc123.jpg");
  });
});
