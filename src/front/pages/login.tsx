import { Button, Input } from "@components/generics";
import { AlertManager } from "@utils/alertManager";
import { isValidEmail, isValidPassword, authService } from "@utils/authentication";

export async function LoginPage(container) {

    const pageHtml = (
        <div class="container relative min-h-screen flex-col items-center justify-center grid lg:max-w-none lg:grid-cols-2 lg:px-0">
            <div class="relative hidden h-full flex-col bg-muted p-10 text-white lg:flex">
                <div class="absolute inset-0 bg-zinc-900" />
                <div class="relative z-20 flex block items-center text-lg font-medium">
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
                <div class="relative z-20 mt-auto">
                    <blockquote class="space-y-2">
                        <p class="text-lg">
                            &ldquo;DoReMix is one of the most secure applications I have ever seen. No injection vulnerabilities — I’m impressed.&rdquo;
                        </p>
                        <footer class="text-sm">Olivier De Jonckère</footer>
                    </blockquote>
                </div>
            </div>

            <div class="p-8 h-full flex items-center justify-center">
                <div class="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-[350px]">
                    <div class="flex flex-col space-y-2 text-center">
                        <h1 class="text-2xl font-semibold tracking-tight">Login to your account</h1>
                        <p class="text-sm text-muted-foreground">
                            Enter your email below to log in
                        </p>
                    </div>

                    <form id="loginForm" class="flex flex-col gap-4">
                        <div class="grid gap-2">
                            <Input id="email" placeholder="name@example.com" label="Email" type="email"></Input>
                        </div>
                        <div class="grid gap-2">
                            <Input id="password" placeholder="*********" label="Password" type="password"></Input>
                            <span id="togglePasswordVisibility" class="cursor-pointer text-xs text-muted-foreground text-right w-fit ml-auto hover:text-primary">Show password</span>
                        </div>
                        <Button className="w-full mt-2">Sign In</Button>
                    </form>

                    <p class="px-8 text-center text-sm text-muted-foreground">
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
