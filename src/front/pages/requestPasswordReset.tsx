import { Button, Input } from "@components/generics";
import { AlertManager } from "@utils/alertManager";
import { isValidEmail, authService } from "@utils/authentication";
import { AppRoutes } from "../router";
import logo from "@assets/images/logo.png";

export async function RequestPasswordResetPage(container) {

    const pageHtml = (
        <div class="relative h-[calc(100vh-64px)] flex-col items-center justify-center grid lg:max-w-none lg:grid-cols-2 lg:px-0 rounded-lg">
            <div class="relative hidden h-full flex-col bg-muted p-10 text-white lg:flex rounded-md animate-fade-reveal">
                <div class="absolute inset-0 bg-zinc-900 rounded-md" />
                <div class="relative z-20 flex block items-center text-lg font-medium animate-fade-right animation-delay-100">
                    <img src={logo} alt="Dorémix" class="mr-2 h-8" />
                    DoReMiX Inc
                </div>
                <div class="relative z-20 flex-1 flex flex-col justify-center mt-12 mb-8 space-y-12">
                    <div class="space-y-4">
                        <h2 class="text-3xl md:text-4xl font-bold tracking-tight leading-tight animate-fade-up animation-delay-200">
                            Forgot your password?<br/>No worries!
                        </h2>
                        <p class="text-lg text-white/80 max-w-md animate-fade-up animation-delay-300">
                            Enter your email address and we'll send you a code to reset your password.
                        </p>
                    </div>
                </div>
            </div>

            <div class="p-4 sm:p-8 h-full flex items-center justify-center animate-fade-reveal animation-delay-200">
                <div class="mx-auto flex w-full flex-col justify-center space-y-8 sm:w-[350px]">

                    <div class="relative lg:hidden z-20 flex block justify-center items-center text-lg font-medium animate-fade-right animation-delay-100">
                        <img src={logo} alt="Dorémix" class="mr-2 h-8" />
                    </div>

                    <div id="requestForm" class="flex flex-col space-y-2 text-center animate-fade-up animation-delay-300">
                        <h1 class="text-3xl font-bold tracking-tight">Reset your password</h1>
                        <p class="text-base text-muted-foreground">
                            Enter your email below to receive a reset code
                        </p>
                    </div>

                    <form id="resetRequestForm" class="flex flex-col gap-4 animate-fade-up animation-delay-500">
                        <div class="grid gap-2">
                            <Input id="email" placeholder="name@example.com" label="Email" type="email"></Input>
                        </div>
                        <Button className="w-full mt-2 transition-transform duration-200 active:scale-95">Send Reset Code</Button>
                    </form>

                    <div id="resetSuccess" class="hidden flex-col items-center space-y-6 text-center animate-fade-up">
                        <div class="flex h-20 w-20 items-center justify-center rounded-full bg-green-500/10 border-2 border-green-500/30">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-green-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M20 6 9 17l-5-5" />
                            </svg>
                        </div>
                        <div class="space-y-2">
                            <h1 class="text-2xl font-bold tracking-tight">Code sent!</h1>
                            <p class="text-sm text-muted-foreground">If you have an account with us, we've sent a password reset code to</p>
                            <p id="resetSuccessEmail" class="text-sm font-semibold text-primary"></p>
                            <p class="text-sm text-muted-foreground">Check your inbox and enter the 6-digit code.</p>
                        </div>
                        <button id="proceedToResetBtn" class="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 active:scale-95 duration-200">
                            Enter Reset Code
                        </button>
                    </div>

                    <p class="px-8 text-center text-sm text-muted-foreground animate-fade-up animation-delay-600">
                        Remember your password?{" "}
                        <a
                            href={AppRoutes.LOGIN}
                            data-link
                            class="underline underline-offset-4 hover:text-primary"
                        >
                            Back to login
                        </a>
                    </p>
                </div>
            </div>
        </div>
    );

    container.innerHTML = pageHtml;
    document.querySelector("header").innerHTML = "";
    handleRequestReset();
    handleProceedToReset();

    function handleRequestReset() {
        const form = document.getElementById('resetRequestForm');

        form.addEventListener('submit', async (e) => {
            e.preventDefault()

            const formData = new FormData(e.target as HTMLFormElement);
            const data = Object.fromEntries(formData);

            const email = data['email'].toString();

            if (!email) {
                new AlertManager().error("Please enter your email address.");
                return;
            }

            if (!isValidEmail(email)) {
                new AlertManager().error("Please enter a valid email (@umontpellier.fr or @etu.umontpellier.fr).");
                return;
            }

            try {
                await authService.requestPasswordReset(email);
                showSuccessMessage(email);
            } catch (e: any) {
                const message = e?.message || "";
                new AlertManager().error("Failed to send reset code. Please try again.");
            }
            return
        })
    }

    function handleProceedToReset() {
        const btn = document.getElementById('proceedToResetBtn');
        if (!btn) return;

        btn.addEventListener('click', () => {
            const email = document.getElementById('resetSuccessEmail')?.textContent || '';
            if (email) {
                window.location.href = `${AppRoutes.RESET_PASSWORD}?email=${encodeURIComponent(email)}`;
            }
        });
    }

    function showSuccessMessage(email: string) {
        document.getElementById("resetRequestForm").classList.add("hidden");
        document.getElementById("requestForm").classList.add("hidden");
        const successEl = document.getElementById("resetSuccess");
        document.getElementById("resetSuccessEmail").textContent = email;
        successEl.classList.remove("hidden");
        successEl.classList.add("flex");
    }
}
