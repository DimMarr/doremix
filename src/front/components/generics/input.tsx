import { cn } from '@components/index';

export interface InputProps {
  label?: string;
  placeholder?: string;
  id?: string;
  className?: string;
  type?: string
}

export function Input({
  label,
  placeholder,
  id,
  className,
  type = "text",
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
        {type == "checkbox" ?
          <label class="relative inline-flex items-center cursor-pointer">
              <input
                  type="checkbox"
                  id={id}
                  name={id}
                  class="sr-only peer"
                  {...rest}
              />
              <div class="w-11 h-6 bg-input rounded-full peer peer-checked:bg-primary peer-focus-visible:ring-1 peer-focus-visible:ring-ring transition-colors peer-disabled:cursor-not-allowed peer-disabled:opacity-50" />
              <div class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm transition-transform peer-checked:translate-x-5" />
          </label> :
          <input
              type={type}
              id={id}
              name={id}
              placeholder={placeholder}
              class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              {...rest}
              safe
          />
        }

    </div>

  );

  return inputContent;
}
