import { Button } from '@components/generics/button';
import { Text } from '@components/generics/text';
import { WifiOffIcon } from '@components/icons/wifiOffIcon';

export function NoInternetPage() {
  return (
    <div class="min-h-screen flex items-center justify-center p-4 bg-background">
      <div class="w-full max-w-md">
        {/* Empty State Container with dotted border shadcn style */}
        <div class="rounded-lg border-2 border-dashed border-neutral-700 bg-neutral-900/50 p-12 text-center space-y-6">
          {/* Icon */}
          <div class="flex justify-center">
            <div class="rounded-full bg-neutral-800 p-6">
              <WifiOffIcon className="w-16 h-16 text-neutral-400" />
            </div>
          </div>

          {/* Heading */}
          <div class="space-y-2">
            <h2 class="text-2xl font-bold tracking-tight text-white">
              No Internet Connection
            </h2>
            <Text className="text-neutral-400 text-base">
              It looks like you're offline. Please check your internet connection and try again.
            </Text>
          </div>

          {/* Retry Button */}
          <div class="pt-2">
            <Button
              variant="default"
              size="lg"
              className="w-full"
              onclick="window.location.reload()"
            >
              <span class="flex items-center gap-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="w-4 h-4"
                >
                  <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path>
                  <path d="M3 3v5h5"></path>
                  <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"></path>
                  <path d="M16 16h5v5"></path>
                </svg>
                Try Again
              </span>
            </Button>
          </div>

          {/* Additional Help Text */}
          <div class="pt-4 border-t border-neutral-800">
            <Text className="text-sm text-neutral-500">
              If the problem persists, please check your network settings
            </Text>
          </div>
        </div>
      </div>
    </div>
  );
}
