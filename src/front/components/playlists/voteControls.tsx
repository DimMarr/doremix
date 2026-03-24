import { PlaylistRepository, type VoteResponse } from "@repositories/playlistRepository";

export type VoteValue = -1 | 0 | 1;

interface VoteControlsProps {
  initialScore: number;
  initialUserVote: number | null;
}

interface VoteControlsOptions extends VoteControlsProps {
  playlistId: number;
  onSync?: (state: VoteResponse) => void;
}

function getNextVote(currentVote: number | null, direction: Exclude<VoteValue, 0>): VoteValue {
  return currentVote === direction ? 0 : direction;
}

function applyOptimisticVote(score: number, currentVote: number | null, nextVote: VoteValue) {
  return {
    score: score - (currentVote ?? 0) + nextVote,
    userVote: nextVote === 0 ? null : nextVote,
  };
}

function getButtonClass(active: boolean, direction: "up" | "down") {
  const baseClass = "flex h-10 w-10 items-center justify-center rounded-full border transition-colors";
  if (direction === "up") {
    return `${baseClass} ${active ? "border-emerald-400 bg-emerald-500/20 text-emerald-300" : "border-white/10 hover:bg-white/10 text-white/70"}`;
  }
  return `${baseClass} ${active ? "border-rose-400 bg-rose-500/20 text-rose-300" : "border-white/10 hover:bg-white/10 text-white/70"}`;
}

export function VoteControls({ initialScore, initialUserVote }: VoteControlsProps) {
  return (
    <div class="flex items-center gap-3">
      <button
        type="button"
        data-vote-direction="1"
        class={getButtonClass(initialUserVote === 1, "up")}
        aria-pressed={initialUserVote === 1 ? "true" : "false"}
        title="Upvote playlist"
      >
        ▲
      </button>
      <span data-vote-score class="min-w-10 text-center text-sm font-semibold text-white">
        {initialScore}
      </span>
      <button
        type="button"
        data-vote-direction="-1"
        class={getButtonClass(initialUserVote === -1, "down")}
        aria-pressed={initialUserVote === -1 ? "true" : "false"}
        title="Downvote playlist"
      >
        ▼
      </button>
    </div>
  );
}

export function initVoteControls(container: HTMLElement, options: VoteControlsOptions) {
  const repo = new PlaylistRepository();
  let score = options.initialScore;
  let userVote = options.initialUserVote;
  let isPending = false;

  const render = () => {
    container.innerHTML = VoteControls({
      initialScore: score,
      initialUserVote: userVote,
    }) as unknown as string;
  };

  render();

  container.onclick = async (event: MouseEvent) => {
    const target = event.target as HTMLElement;
    const button = target.closest("[data-vote-direction]") as HTMLElement | null;
    if (!button || isPending) return;

    const direction = Number(button.getAttribute("data-vote-direction")) as Exclude<VoteValue, 0>;
    const nextVote = getNextVote(userVote, direction);
    const previousState = { score, userVote };
    const optimisticState = applyOptimisticVote(score, userVote, nextVote);

    score = optimisticState.score;
    userVote = optimisticState.userVote;
    isPending = true;
    render();

    try {
      const response = await repo.castVote(options.playlistId, nextVote);
      score = response.score;
      userVote = response.userVote;
      options.onSync?.(response);
      render();
    } catch (error) {
      console.error("Failed to cast vote", error);
      score = previousState.score;
      userVote = previousState.userVote;
      render();
    } finally {
      isPending = false;
    }
  };
}
