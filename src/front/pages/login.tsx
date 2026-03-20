import { Button, Input } from "@components/generics";
import { AlertManager } from "@utils/alertManager";
import { isValidEmail, isValidPassword, authService } from "@utils/authentication";

export async function LoginPage(container) {

    const pageHtml = (
        <div class="relative h-[calc(100vh-64px)] flex-col items-center justify-center grid lg:max-w-none lg:grid-cols-2 lg:px-0 rounded-lg overflow-hidden">
            <div class="relative hidden h-full flex-col bg-muted p-10 text-white lg:flex rounded-md animate-fade-reveal">
                <div class="absolute inset-0 bg-[#3838ec] rounded-md" />
                <div class="relative z-20 flex block items-center text-lg font-medium animate-fade-right animation-delay-100">
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        class="mr-2 h-6 w-6"
                    >
                        <path d="M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3" />
                    </svg>
                    DoReMiX Inc
                </div>

                <div class="relative z-20 flex-1 flex flex-col justify-center mt-12 mb-8 space-y-12">
                    <div class="space-y-4">
                        <h2 class="text-3xl md:text-4xl font-bold tracking-tight leading-tight animate-fade-up animation-delay-200">Manage your music <br/>without the noise.</h2>
                        <p class="text-lg text-white/80 max-w-md animate-fade-up animation-delay-300">A smarter way to control YouTube playlists. No clutter. No friction. Just clean, powerful control over your soundtracks.</p>
                    </div>

                    <div class="space-y-6">
                        <div class="flex items-center gap-4 animate-fade-up animation-delay-400 group hover:translate-x-2 transition-transform duration-300 cursor-default">
                            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-white/10 backdrop-blur-md border border-white/20 shadow-sm group-hover:bg-white/20 transition-colors duration-300">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-6 w-6 text-white"><path d="M9 18V5l12-2v13"></path><circle cx="6" cy="18" r="3"></circle><circle cx="18" cy="16" r="3"></circle></svg>
                            </div>
                            <div>
                                <h3 class="font-semibold text-lg text-white">Ultimate Control</h3>
                                <p class="text-sm text-white/70">Organize and curate your playlists effortlessly.</p>
                            </div>
                        </div>

                        <div class="flex items-center gap-4 animate-fade-up animation-delay-500 group hover:translate-x-2 transition-transform duration-300 cursor-default">
                            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-white/10 backdrop-blur-md border border-white/20 shadow-sm group-hover:bg-white/20 transition-colors duration-300">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-6 w-6 text-white"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                            </div>
                            <div>
                                <h3 class="font-semibold text-lg text-white">Rock-Solid Security</h3>
                                <p class="text-sm text-white/70">Zero injection vulnerabilities, maximum peace of mind.</p>
                            </div>
                        </div>

                        <div class="flex items-center gap-4 animate-fade-up animation-delay-600 group hover:translate-x-2 transition-transform duration-300 cursor-default">
                            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-white/10 backdrop-blur-md border border-white/20 shadow-sm group-hover:bg-white/20 transition-colors duration-300">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-6 w-6 text-white"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                            </div>
                            <div>
                                <h3 class="font-semibold text-lg text-white">Blazing Fast</h3>
                                <p class="text-sm text-white/70">No wasted time, just seamless performance.</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="relative z-20 mt-auto animate-fade-up animation-delay-700">
                    <blockquote class="space-y-2">
                        <p class="text-lg">
                            &ldquo;DoReMix is one of the most secure applications I have ever seen. No injection vulnerabilities — I’m impressed.&rdquo;
                        </p>
                        <footer class="text-sm">Olivier De Jonckère</footer>
                    </blockquote>
                </div>
            </div>

            <div class="p-8 h-full flex items-center justify-center animate-fade-reveal animation-delay-200">
                <div class="mx-auto flex w-full flex-col justify-center space-y-8 sm:w-[350px]">
                    <div class="flex flex-col space-y-2 text-center animate-fade-up animation-delay-300">
                        <h1 class="text-3xl font-bold tracking-tight">Login to your account</h1>
                        <p class="text-base text-muted-foreground">
                            Enter your email below to log in
                        </p>
                    </div>

                    <form id="loginForm" class="flex flex-col gap-4 animate-fade-up animation-delay-500">
                        <div class="grid gap-2">
                            <Input id="email" placeholder="name@example.com" label="Email" type="email"></Input>
                        </div>
                        <div class="grid gap-2">
                            <Input id="password" placeholder="*********" label="Password" type="password"></Input>
                            <span id="togglePasswordVisibility" class="cursor-pointer text-xs text-muted-foreground text-right w-fit ml-auto hover:text-primary transition-colors duration-200">Show password</span>
                        </div>
                        <Button className="w-full mt-2 transition-transform duration-200 active:scale-95">Sign In</Button>
                    </form>

                    <p class="px-8 text-center text-sm text-muted-foreground animate-fade-up animation-delay-600">
                        Don't have an account?{" "}
                        <a
                            href="/signup"
                            class="underline underline-offset-4 hover:text-primary"
                        >
                            Sign up
                        </a>
                    </p>
                </div>
            </div>
        </div>
    );

    container.innerHTML = pageHtml;
    document.querySelector("header").innerHTML = "";
    handleLogin();
    togglePasswordVisibility();

    function handleLogin() {
        const loginForm = document.getElementById('loginForm');

        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault()

            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);

            const email = data['email'].toString();
            const password = data['password'].toString();

            console.log(typeof (email))

            if (!email) {
                new AlertManager().error("Please enter your email address.");
                return;
            }

            if (!password) {
                new AlertManager().error("Please enter your password.");
                return;
            }

            if (!isValidEmail(email)) {
                new AlertManager().error("Please enter a valid email (@umontpellier.fr or @etu.umontpellier.fr).");
                return;
            }

            if (!isValidPassword(password)) {
                new AlertManager().error("Your password must be at least 8 characters and contains one uppercase, one lowercase, one digit and one special character.");
                return;
            }

            try {
                await authService.login(email, password);
                window.location.href = "/";
            } catch (e) {
                new AlertManager().error("Login failed. Please check your credentials.");
            }
            return

        })
    }

    function togglePasswordVisibility() {
        const btn = document.getElementById("togglePasswordVisibility")

        btn.addEventListener('click', () => {
            const passwordInput = document.getElementById("password")
            passwordInput.type == "password" ? passwordInput.type = "text" : passwordInput.type = "password"
        })
    }
}
