import { Button } from '@components/generics/button';
import { AuthStore } from '@store/auth';

export function SignupPage(container: HTMLElement, authStore: AuthStore, router: any) {
  let email = '';
  let password = '';
  let username = '';
  let error = '';

  const validateEmail = (email: string): boolean => {
    return email.endsWith('@etu.umontpellier.fr') || email.endsWith('@umontpellier.fr');
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    error = '';

    if (!email || !password || !username) {
      error = 'Please fill in all fields';
      render();
      return;
    }

    if (!validateEmail(email)) {
      error = 'Email must be from @etu.umontpellier.fr or @umontpellier.fr';
      render();
      return;
    }

    if (password.length < 8) {
      error = 'Password must be at least 8 characters long';
      render();
      return;
    }

    if (username.length < 3) {
      error = 'Username must be at least 3 characters long';
      render();
      return;
    }

    try {
      await authStore.signup(email, password, username);
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
              Create your account
            </h2>
            <p class="mt-2 text-center text-sm text-gray-400">
              Or{' '}
              <a href="/login" data-link class="font-medium text-primary hover:text-primary/80">
                sign in to existing account
              </a>
            </p>
          </div>
          <form class="mt-8 space-y-6" id="signup-form">
            {error && (
              <div class="rounded-md bg-destructive/10 border border-destructive p-4">
                <p class="text-sm text-destructive">{error}</p>
              </div>
            )}
            <div class="rounded-md shadow-sm space-y-4">
              <div>
                <label for="username" class="block text-sm font-medium text-gray-300 mb-2">
                  Username
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  value={username}
                  class="appearance-none relative block w-full px-3 py-2 border border-gray-700 bg-gray-900 placeholder-gray-500 text-white rounded-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
                  placeholder="Your username"
                />
              </div>
              <div>
                <label for="email" class="block text-sm font-medium text-gray-300 mb-2">
                  University email
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
                <p class="mt-1 text-xs text-gray-500">
                  Must be @etu.umontpellier.fr or @umontpellier.fr
                </p>
              </div>
              <div>
                <label for="password" class="block text-sm font-medium text-gray-300 mb-2">
                  Password
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autocomplete="new-password"
                  required
                  value={password}
                  class="appearance-none relative block w-full px-3 py-2 border border-gray-700 bg-gray-900 placeholder-gray-500 text-white rounded-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
                  placeholder="At least 8 characters"
                />
              </div>
            </div>

            <div>
              <Button
                type="submit"
                variant="primary"
                class="w-full flex justify-center py-2 px-4"
              >
                Create account
              </Button>
            </div>
          </form>
        </div>
      </div>
    );

    // Attach event listeners
    const form = container.querySelector('#signup-form');
    if (form) {
      form.addEventListener('submit', handleSubmit);

      const usernameInput = form.querySelector('#username') as HTMLInputElement;
      const emailInput = form.querySelector('#email') as HTMLInputElement;
      const passwordInput = form.querySelector('#password') as HTMLInputElement;

      usernameInput?.addEventListener('input', (e) => {
        username = (e.target as HTMLInputElement).value;
      });

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
