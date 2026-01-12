import { Button } from '@components/generics/button';
import { AuthStore } from '@store/auth';

export function LoginPage(container: HTMLElement, authStore: AuthStore, router: any) {
  let email = '';
  let password = '';
  let error = '';

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    error = '';

    if (!email || !password) {
      error = 'Please fill in all fields';
      render();
      return;
    }

    try {
      await authStore.login(email, password);
      router.navigate('/');
    } catch (err: any) {
      error = err.message;
      render();
    }
  };

  const render = () => {
    container.innerHTML = (
      <div class="min-h-screen flex items-center justify-center bg-[#0a0a0a] px-4">
        <div class="max-w-md w-full space-y-8">
          <div>
            <h2 class="mt-6 text-center text-3xl font-extrabold text-white">
              Sign in to DoRéMix
            </h2>
            <p class="mt-2 text-center text-sm text-gray-400">
              Or{' '}
              <a href="/signup" data-link class="font-medium text-primary hover:text-primary/80">
                create a new account
              </a>
            </p>
          </div>
          <form class="mt-8 space-y-6" id="login-form">
            {error && (
              <div class="rounded-md bg-destructive/10 border border-destructive p-4">
                <p class="text-sm text-destructive">{error}</p>
              </div>
            )}
            <div class="rounded-md shadow-sm space-y-4">
              <div>
                <label for="email" class="block text-sm font-medium text-gray-300 mb-2">
                  Email address
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autocomplete="email"
                  required
                  value={email}
                  class="appearance-none relative block w-full px-3 py-2 border border-gray-700 bg-gray-900 placeholder-gray-500 text-white rounded-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
                  placeholder="you@etu.umontpellier.fr"
                />
              </div>
              <div>
                <label for="password" class="block text-sm font-medium text-gray-300 mb-2">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autocomplete="current-password"
                  required
                  value={password}
                  class="appearance-none relative block w-full px-3 py-2 border border-gray-700 bg-gray-900 placeholder-gray-500 text-white rounded-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
                  placeholder="Password"
                />
              </div>
            </div>

            <div>
              <Button
                type="submit"
                variant="primary"
                class="w-full flex justify-center py-2 px-4"
              >
                Sign in
              </Button>
            </div>
          </form>
        </div>
      </div>
    );

    // Attach event listeners
    const form = container.querySelector('#login-form');
    if (form) {
      form.addEventListener('submit', handleSubmit);

      const emailInput = form.querySelector('#email') as HTMLInputElement;
      const passwordInput = form.querySelector('#password') as HTMLInputElement;

      emailInput?.addEventListener('input', (e) => {
        email = (e.target as HTMLInputElement).value;
      });

      passwordInput?.addEventListener('input', (e) => {
        password = (e.target as HTMLInputElement).value;
      });
    }
  };

  render();
}
