import { Button } from "@components/generics";
import { authService } from "@utils/authentication";
import { AppRoutes } from "../router";
import logo from "@assets/images/logo.png";
import { AlertManager } from "@utils/alertManager";

export async function VerifyEmailPage(container) {

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
                            One last step<br/>before the music
                        </h2>
                        <p class="text-lg text-white/80 max-w-md animate-fade-up animation-delay-300">
                            Verify your email address to unlock full access to your DoReMiX account.
                        </p>
                    </div>
                </div>
            </div>

            <div class="p-4 sm:p-8 h-full flex items-center justify-center animate-fade-reveal animation-delay-200">
                <div class="mx-auto flex w-full flex-col justify-center space-y-8 sm:w-[350px]">

                    <div class="relative lg:hidden z-20 flex block justify-center items-center text-lg font-medium animate-fade-right animation-delay-100">
                        <img src={logo} alt="Dorémix" class="mr-2 h-8" />
                    </div>

                    <div id="verifyStatusCard" class="flex flex-col items-center space-y-6 text-center animate-fade-up animation-delay-300">

                        {/* Loading */}
                        <div id="statusLoading" class="flex flex-col items-center space-y-4">
                            <div class="h-16 w-16 rounded-full border-4 border-muted border-t-primary animate-spin" />
                            <p class="text-base text-muted-foreground">Verifying your email…</p>
                        </div>

                        {/* Success */}
                        <div id="statusSuccess" class="hidden flex flex-col items-center space-y-4">
                            <div class="flex h-20 w-20 items-center justify-center rounded-full bg-green-500/10 border-2 border-green-500/30 animate-fade-reveal">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-green-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M20 6 9 17l-5-5" />
                                </svg>
                            </div>
                            <div class="space-y-1">
                                <h1 class="text-2xl font-bold tracking-tight">Email verified!</h1>
                                <p class="text-sm text-muted-foreground">Your account is now active. You can log in.</p>
                            </div>
                            <a href={AppRoutes.LOGIN} class="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 active:scale-95 duration-200">
                                Go to Login
                            </a>
                            <p id="countdownSuccess" class="text-sm text-muted-foreground"></p>
                        </div>


                        {/* Expired */}
                        <div id="statusExpired" class="hidden flex flex-col items-center space-y-4">
                            <div class="flex h-20 w-20 items-center justify-center rounded-full bg-amber-500/10 border-2 border-amber-500/30">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M5 22h14" /><path d="M5 2h14" />
                                    <path d="M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22" />
                                    <path d="M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2" />
                                </svg>
                            </div>
                            <div class="space-y-1">
                                <h1 class="text-2xl font-bold tracking-tight">Link expired</h1>
                                <p class="text-sm text-muted-foreground">This verification link has expired. Request a new one or go back to login.</p>
                            </div>
                            <div class="flex flex-col w-full gap-2">
                                <button id="resendEmailBtn" class="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 active:scale-95 duration-200">
                                    Resend verification email
                                </button>
                            </div>
                        </div>

                        {/* Invalid */}
                        <div id="statusInvalid" class="hidden flex flex-col items-center space-y-4">
                            <div class="flex h-20 w-20 items-center justify-center rounded-full bg-red-500/10 border-2 border-red-500/30">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <circle cx="12" cy="12" r="10" />
                                    <path d="m15 9-6 6" /><path d="m9 9 6 6" />
                                </svg>
                            </div>
                            <div class="space-y-1">
                                <h1 class="text-2xl font-bold tracking-tight">Invalid link</h1>
                                <p class="text-sm text-muted-foreground">This verification link is invalid or has already been used.</p>
                            </div>
                            <a href={AppRoutes.LOGIN} class="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 active:scale-95 duration-200">
                                Go to Login
                            </a>
                            <p id="countdownInvalid" class="text-sm text-muted-foreground"></p>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );

    container.innerHTML = pageHtml;
    document.querySelector("header").innerHTML = "";
    await handleVerification();
    handleResendEmail();

    function showStatus(status: "success" | "expired" | "invalid") {
        document.getElementById("statusLoading").classList.add("hidden");
        const id = "status" + status.charAt(0).toUpperCase() + status.slice(1);
        document.getElementById(id).classList.remove("hidden");
    }

    async function handleVerification() {
        const params = new URLSearchParams(window.location.search);
        const token = params.get("token");

        if (!token) {
            showStatus("invalid");
            startRedirectCountdown("countdownInvalid");
            return;
        }

        try {
            const result = await authService.verify_email(token);

            await new Promise(resolve => setTimeout(resolve, 1200));

            if (result === "verified" || result === "already_verified") {
                showStatus("success");
                startRedirectCountdown("countdownSuccess");
            } else if (result === "expired") {
                showStatus("expired");
            } else {
                showStatus("invalid");
                startRedirectCountdown("countdownInvalid");
            }
        } catch (e) {
            console.error(e);
            showStatus("invalid");
            startRedirectCountdown("countdownInvalid");
        }
    }

    function startRedirectCountdown(countdownId: string) {
        let seconds = 10;
        const countdownEl = document.getElementById(countdownId);
        if (!countdownEl) return;

        countdownEl.textContent = `Redirecting automatically in ${seconds}s…`;

        const interval = setInterval(() => {
            seconds--;
            countdownEl.textContent = `Redirecting automatically in ${seconds}s…`;
            if (seconds <= 0) {
                clearInterval(interval);
                window.location.href = AppRoutes.LOGIN;
            }
        }, 1000);
    }

    function handleResendEmail() {
        const btn = document.getElementById("resendEmailBtn");
        if (!btn) return;

        btn.addEventListener("click", async () => {
            const params = new URLSearchParams(window.location.search);
            const token = params.get("token");

            btn.textContent = "Sending…";
            (btn as HTMLButtonElement).disabled = true;

            try {
                await authService.resend_verification_email(token);
                new AlertManager().success("A new verification email has been sent.");
            } catch (e) {
                new AlertManager().error("Failed to resend email. Please try again.");
            } finally {
                (btn as HTMLButtonElement).disabled = false;
                btn.textContent = "Resend verification email";
            }
        });
    }
}
