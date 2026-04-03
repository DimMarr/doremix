import { cn } from '@components/index';

export interface AdminPanelProps {
  className?: string;
  title?: string;
  name?: string;
  content?: any;
}

export function AdminPanel({
  className,
  title,
  name,
  content
}: AdminPanelProps) {

    const baseClass = "bg-neutral-900 border border-border p-6 rounded-xl shadow-2xl flex flex-col max-h-120 flex-1 min-w-80"
    const panelClass = cn(baseClass, className);

    const panelContent = (
    <div class={panelClass}>
        <h2 class="text-xl font-semibold text-white mb-4">{title}</h2>
        <div class="h-full flex flex-col justify-between overflow-auto">
          <div id={`${name}-list`} class="space-y-2 mb-6 overflow-y-auto">
              <p class="text-muted-foreground text-sm">Loading...</p>
          </div>

          {content}
        </div>
    </div>

  );

  return panelContent;
}
