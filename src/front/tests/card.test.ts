import { describe, it, expect, vi } from "vitest";

vi.mock("../components/index", () => ({
  cn: (...classes: string[]) => classes.filter(Boolean).join(" "),
  getCardClasses: () => "card",
}));

vi.mock("../layouts/mainLayout", () => ({
  trackPlayerInstance: {
    playlist: { idPlaylist: -1 },
    setPlaylist: () => {},
    playTrack: () => {},
  },
}));

vi.mock("../utils/alertManager", () => ({
  AlertManager: class {
    error() {}
  },
}));

vi.mock("../repositories/index", () => ({
  PlaylistRepository: class {
    getTracks() { return Promise.resolve([]); }
  },
}));

vi.mock("../models/playlist", () => ({
  default: class Playlist {
    idPlaylist: number;
    name: string;
    image?: string;
    visibility: string;
    tracks: any[];

    constructor(data: any) {
      this.idPlaylist = data.idPlaylist;
      this.name = data.name;
      this.image = data.image;
      this.visibility = data.visibility;
      this.tracks = data.tracks;
    }
  },
  Visibility: { private: "private", public: "public", open: "open" },
}));

import { Card, buildCardsFromPlaylists } from "../components/generics/card";
import Playlist, { Visibility } from "../models/playlist";

describe("Card — lazy loading structure", () => {
  it("renders img with data-src and no src when image is provided", async () => {
    const html = await Card({ title: "My Playlist", image: "http://example.com/cover.jpg" });
    expect(html).toContain('data-src="http://example.com/cover.jpg"');
    expect(html).not.toMatch(/<img[^>]+(?<!\bdata-)src="http:\/\/example\.com\/cover\.jpg"/);
    expect(html).toContain('opacity-0');
  });

  it("renders skeleton div when image is provided", async () => {
    const html = await Card({ title: "My Playlist", image: "http://example.com/cover.jpg" });
    expect(html).toContain("data-skeleton");
  });

  it("renders SVG placeholder and no skeleton when image is undefined", async () => {
    const html = await Card({ title: "No Cover" });
    expect(html).not.toContain("data-skeleton");
    expect(html).toContain("<svg");
  });
});

describe("buildCardsFromPlaylists — data-has-cover", () => {
  it("adds data-has-cover='1' when playlist has an image", () => {
    const playlist = new Playlist({
      idPlaylist: 1,
      name: "With Cover",
      image: "http://example.com/cover.jpg",
      visibility: Visibility.public,
      tracks: [],
    });
    const html = buildCardsFromPlaylists([playlist]);
    expect(html).toContain('data-has-cover="1"');
  });

  it("does not add data-has-cover when playlist has no image", () => {
    const playlist = new Playlist({
      idPlaylist: 2,
      name: "No Cover",
      image: undefined,
      visibility: Visibility.public,
      tracks: [],
    });
    const html = buildCardsFromPlaylists([playlist]);
    expect(html).not.toContain('data-has-cover');
  });
});
