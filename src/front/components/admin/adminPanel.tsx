export interface AdminPanelProps {
  title?: string;
  name?: string;
  content?: string;
}

export function AdminPanel({
  title,
  name,
  content
}: AdminPanelProps) {

    const panelContent = (
    <div class="bg-neutral-900 border border-border p-6 rounded-xl w-full shadow-2xl">
        <h2 class="text-xl font-semibold text-white mb-4">{title}</h2>
        <div id={`${name}-list`} class="space-y-2 mb-6 max-h-96 overflow-y-auto">
            <p class="text-muted-foreground text-sm">Loading...</p>
        </div>

        {content}
    </div>

  );

  return panelContent;
}
