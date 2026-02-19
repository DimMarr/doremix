import { cn } from '@components/index';

export interface InputProps {
  label?: string;
  placeholder?: string;
  id?: string;
  className?: string;
}

export function Input({
  label,
  placeholder,
  id,
  className,
  ...rest
}: InputProps) {
  const inputClasses = cn("grid w-full gap-1.5", className);

  const inputContent = (
    <div class={inputClasses}>
        <label
            htmlFor={id}
            class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
            {label}
        </label>
        <input
            type="text"
            id={id}
            name={id}
            placeholder={placeholder}
            class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
            {...rest}
            safe
        />
    </div>

  );

  return inputContent;
}
