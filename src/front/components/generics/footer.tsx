export function Footer() {
  return (
    <footer class="bg-background rounded-md p-4 mt-12 mb-3">
      <div class="flex flex-col md:flex-row gap-6 justify-between mb-4">

        {/* --- Section Gauche --- */}
        <div class="company-section max-w-[350px]">
          <div class="font-black text-xl mb-1">Dorémix</div>
          <p class="mb-2 text-sm text-neutral-300">Your all in one solution to listen to music.</p>
          <div class="inline-flex items-center justify-center rounded-full border px-2 py-0.5 text-[10px] font-medium w-fit whitespace-nowrap shrink-0 gap-1 focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden border-transparent bg-neutral-800 text-secondary-foreground">
            <span class="w-[4px] h-[4px] rounded-[999px] bg-green-500 mr-1"></span>
            All systems operational
          </div>
        </div>

        <div class="flex flex-1 flex-col md:flex-row justify-end gap-4 md:gap-16">
          <div class="link-section flex flex-col gap-1 items-start md:items-end text-left md:text-right">
            <p class="font-bold text-sm text-white">Legal</p>
            <a href="/cgu" data-link class="text-sm text-neutral-400 hover:text-white transition-colors">
              Terms of use
            </a>
          </div>
        </div>

      </div>

      <div class="text-xs text-neutral-500 border-t border-white/10 pt-3">
        © Dorémix 2026 — DO3 Inc.
      </div>
    </footer>
  );
}
