
export function createFooter(): HTMLElement {
    const footer = document.createElement('footer');
    footer.innerHTML = `
    <div class="bg-[#161616] rounded-md p-6 mt-[400px] mb-3">
      <div class='flex flex-col md:flex-row gap-10 justify-between mb-6'>
        <div class='company-section max-w-[300px]'>
          <div class='font-black text-2xl mb-1'>
            Dorémix
          </div>
          <p class="mb-1">
            Your all in one solution to listen to music.
          </p>
          <div class="inline-flex items-center justify-center rounded-full border px-2 py-0.5 text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden border-transparent bg-[#262626] text-secondary-foreground [a&]:hover:bg-[#262626]/90">
          <span class="w-[4px] h-[4px] rounded-[999px] bg-green-500 mr-1"></span>
            All systems operationals
          </div>
        </div>
        <div class="flex flex-1 justify-between flex-col md:flex-row md:justify-end gap-5 md:gap-[120px]">
          <div class="link-section flex flex-col gap-2">
            <p class="font-bold">Navigation</p>
            <p>Landing page</p>
            <p>Authentication</p>
            <p>Terms of service</p>
          </div>
          <div class="link-section flex flex-col gap-2">
            <p class="font-bold">Ressources</p>
            <p>Terms</p>
            <p>Cookie preference</p>
          </div>
        </div>
      </div>
      <div>
        © Dorémix 2025 — DO3 Inc.
      </div>
    </div>
    `;


    return footer;
}
