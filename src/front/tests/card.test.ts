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

import { Card, buildCardsFromPlaylists, initCardsElements } from "../components/generics/card";
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

describe("initCardsElements — IntersectionObserver lazy loading", () => {
  it("sets img src when card intersects viewport", () => {
    const container = document.createElement("div");
    container.innerHTML = `
      <a data-playlist-card="1" data-playlist-id="1" data-has-cover="1" href="/playlist/1">
        <div>
          <div data-skeleton class="animate-pulse"></div>
          <img data-src="http://example.com/cover.jpg" class="opacity-0" />
        </div>
      </a>
    `;
    document.body.appendChild(container);

    const playlist = new Playlist({
      idPlaylist: 1,
      name: "Test",
      image: "http://example.com/cover.jpg",
      visibility: Visibility.public,
      tracks: [],
    });

    let observerCallback: IntersectionObserverCallback;
    const mockObserver = {
      observe: vi.fn(),
      disconnect: vi.fn(),
      unobserve: vi.fn(),
    };
    vi.stubGlobal(
      "IntersectionObserver",
      vi.fn(function (cb: IntersectionObserverCallback) {
        observerCallback = cb;
        return mockObserver;
      })
    );

    initCardsElements(container, [playlist]);

    const imgEl = container.querySelector("img") as HTMLImageElement;
    observerCallback!(
      [{ isIntersecting: true, target: container.querySelector("[data-playlist-card]")! } as any],
      mockObserver as any
    );

    expect(imgEl.src).toContain("http://example.com/cover.jpg");
    expect(mockObserver.unobserve).toHaveBeenCalled();

    document.body.removeChild(container);
  });

  it("hides skeleton and shows image on load", () => {
    const container = document.createElement("div");
    container.innerHTML = `
      <a data-playlist-card="1" data-playlist-id="2" data-has-cover="1" href="/playlist/2">
        <div>
          <div data-skeleton></div>
          <img data-src="http://example.com/cover2.jpg" class="opacity-0" />
        </div>
      </a>
    `;
    document.body.appendChild(container);

    const playlist = new Playlist({
      idPlaylist: 2,
      name: "Test2",
      image: "http://example.com/cover2.jpg",
      visibility: Visibility.public,
      tracks: [],
    });

    let observerCallback: IntersectionObserverCallback;
    const mockObserver = { observe: vi.fn(), disconnect: vi.fn(), unobserve: vi.fn() };
    vi.stubGlobal(
      "IntersectionObserver",
      vi.fn(function (cb: IntersectionObserverCallback) { observerCallback = cb; return mockObserver; })
    );

    initCardsElements(container, [playlist]);

    observerCallback!(
      [{ isIntersecting: true, target: container.querySelector("[data-playlist-card]")! } as any],
      mockObserver as any
    );

    const imgEl = container.querySelector("img") as HTMLImageElement;
    const skeleton = container.querySelector("[data-skeleton]") as HTMLElement;

    imgEl.dispatchEvent(new Event("load"));

    expect(skeleton.style.display).toBe("none");
    expect(imgEl.classList.contains("opacity-0")).toBe(false);
    expect(imgEl.classList.contains("opacity-100")).toBe(true);

    document.body.removeChild(container);
  });

  it("hides skeleton and shows SVG placeholder on image error", () => {
    const container = document.createElement("div");
    container.innerHTML = `
      <a data-playlist-card="1" data-playlist-id="3" data-has-cover="1" href="/playlist/3">
        <div>
          <div data-skeleton></div>
          <img data-src="http://broken.com/cover.jpg" class="opacity-0" />
        </div>
      </a>
    `;
    document.body.appendChild(container);

    const playlist = new Playlist({
      idPlaylist: 3,
      name: "Broken",
      image: "http://broken.com/cover.jpg",
      visibility: Visibility.public,
      tracks: [],
    });

    let observerCallback: IntersectionObserverCallback;
    const mockObserver = { observe: vi.fn(), disconnect: vi.fn(), unobserve: vi.fn() };
    vi.stubGlobal(
      "IntersectionObserver",
      vi.fn(function (cb: IntersectionObserverCallback) { observerCallback = cb; return mockObserver; })
    );

    initCardsElements(container, [playlist]);

    observerCallback!(
      [{ isIntersecting: true, target: container.querySelector("[data-playlist-card]")! } as any],
      mockObserver as any
    );

    const imgEl = container.querySelector("img") as HTMLImageElement;
    const skeleton = container.querySelector("[data-skeleton]") as HTMLElement;

    imgEl.dispatchEvent(new Event("error"));

    expect(skeleton.style.display).toBe("none");
    expect(imgEl.style.display).toBe("none");

    const svgPlaceholder = container.querySelector("[data-cover-fallback]");
    expect(svgPlaceholder).not.toBeNull();

    document.body.removeChild(container);
  });

  it("does not attach observer to cards without data-has-cover", async () => {
    const container = document.createElement("div");
    container.innerHTML = `
      <a data-playlist-card="1" data-playlist-id="4" href="/playlist/4">
        <svg></svg>
      </a>
    `;
    document.body.appendChild(container);

    const playlist = new Playlist({
      idPlaylist: 4,
      name: "No Cover",
      image: undefined,
      visibility: Visibility.public,
      tracks: [],
    });

    const mockObserver = { observe: vi.fn(), disconnect: vi.fn(), unobserve: vi.fn() };
    vi.stubGlobal("IntersectionObserver", vi.fn(function () { return mockObserver; }));

    initCardsElements(container, [playlist]);

    expect(mockObserver.observe).not.toHaveBeenCalled();

    document.body.removeChild(container);
  });
});
