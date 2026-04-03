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

                        {/* Enter Code */}
                        <div id="statusEnterCode" class="flex flex-col items-center space-y-4 w-full">
                            <div class="space-y-2">
                                <h1 class="text-2xl font-bold tracking-tight">Verify your email</h1>
                                <p id="verifyEmailDisplay" class="text-sm text-muted-foreground"></p>
                            </div>
                            <div class="w-full space-y-3">
                                <input id="verificationCode" type="text" inputmode="numeric" placeholder="000000" maxlength="6" class="w-full px-4 py-2 rounded-md border border-input text-center text-2xl tracking-widest font-mono bg-background focus:outline-none focus:ring-2 focus:ring-primary" />
                                <button id="verifyCodeBtn" class="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 active:scale-95 duration-200">
                                    Verify Code
                                </button>
                            </div>
                            <div class="space-y-2">
                                <p class="text-xs text-muted-foreground">Didn't receive the code?</p>
                                <button id="resendCodeBtn" class="text-xs text-primary hover:underline">
                                    Resend code
                                </button>
                            </div>
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
                                <h1 class="text-2xl font-bold tracking-tight">Code expired</h1>
                                <p class="text-sm text-muted-foreground">Your verification code has expired. Request a new one.</p>
                            </div>
                            <div class="flex flex-col w-full gap-2">
                                <button id="resendExpiredCodeBtn" class="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 active:scale-95 duration-200">
                                    Resend code
                                </button>
                                <a href={AppRoutes.LOGIN} class="inline-flex h-10 w-full items-center justify-center rounded-md bg-muted px-4 py-2 text-sm font-medium text-muted-foreground shadow transition-colors hover:bg-muted/80 active:scale-95 duration-200">
                                    Back to Login
                                </a>
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

    const params = new URLSearchParams(window.location.search);
    const email = params.get("email");

    if (!email) {
        showStatus("invalid");
        startRedirectCountdown("countdownInvalid");
        return;
    }

    // Display the email
    const emailDisplay = document.getElementById("verifyEmailDisplay");
    if (emailDisplay) {
        emailDisplay.textContent = email;
    }

    handleVerifyCode(email);
    handleResendCode(email);
    handleResendExpiredCode(email);

    function showStatus(status: "success" | "expired" | "invalid" | "enter-code") {
        const statuses = ["statusEnterCode", "statusLoading", "statusSuccess", "statusExpired", "statusInvalid"];
        statuses.forEach(s => {
            const el = document.getElementById(s);
            if (el) el.classList.add("hidden");
        });

        const id = status === "enter-code" ? "statusEnterCode" : "status" + status.charAt(0).toUpperCase() + status.slice(1);
        const el = document.getElementById(id);
        if (el) el.classList.remove("hidden");
    }

    function handleVerifyCode(email: string) {
        const codeInput = document.getElementById("verificationCode") as HTMLInputElement;
        const verifyBtn = document.getElementById("verifyCodeBtn");

        if (!codeInput || !verifyBtn) return;

        verifyBtn.addEventListener("click", async () => {
            const code = codeInput.value.trim();

            if (!code || code.length !== 6 || !/^\d{6}$/.test(code)) {
                new AlertManager().error("Please enter a valid 6-digit code.");
                return;
            }

            verifyBtn.textContent = "Verifying…";
            (verifyBtn as HTMLButtonElement).disabled = true;

            try {
                const result = await authService.verifyCode(email, code);

                // Check result from backend
                if (typeof result === 'object') {
                    if (result.status === "verified" || result.status === "already_verified") {
                        // Success
                        await new Promise(resolve => setTimeout(resolve, 1200));
                        showStatus("success");
                        startRedirectCountdown("countdownSuccess");
                    } else {
                        new AlertManager().error("Verification failed. Please try again.");
                        codeInput.value = "";
                    }
                } else if (result === "verified" || result === "already_verified") {
                    // Success (fallback for old format)
                    await new Promise(resolve => setTimeout(resolve, 1200));
                    showStatus("success");
                    startRedirectCountdown("countdownSuccess");
                } else {
                    new AlertManager().error("Invalid verification code.");
                    codeInput.value = "";
                }
            } catch (e: any) {
                const message = e?.message || "";
                if (message.includes("expired")) {
                    showStatus("expired");
                    new AlertManager().warning("Your verification code has expired. Please request a new one.");
                } else if (message.includes("invalid")) {
                    new AlertManager().error("Invalid verification code.");
                    codeInput.value = "";
                } else {
                    new AlertManager().error("Verification failed. Please try again.");
                    codeInput.value = "";
                }
            } finally {
                (verifyBtn as HTMLButtonElement).disabled = false;
                verifyBtn.textContent = "Verify Code";
            }
        });

        // Allow Enter key to submit
        codeInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                verifyBtn.click();
            }
        });
    }

    function handleResendCode(email: string) {
        const resendBtn = document.getElementById("resendCodeBtn");
        if (!resendBtn) return;

        resendBtn.addEventListener("click", async () => {
            resendBtn.textContent = "Sending…";
            (resendBtn as HTMLButtonElement).disabled = true;

            try {
                await authService.resendVerificationCode(email);
                new AlertManager().success("Verification code resent to your email.");
                (document.getElementById("verificationCode") as HTMLInputElement).value = "";
            } catch (e) {
                new AlertManager().error("Failed to resend code. Please try again.");
            } finally {
                (resendBtn as HTMLButtonElement).disabled = false;
                resendBtn.textContent = "Resend code";
            }
        });
    }

    function handleResendExpiredCode(email: string) {
        const resendBtn = document.getElementById("resendExpiredCodeBtn");
        if (!resendBtn) return;

        resendBtn.addEventListener("click", async () => {
            resendBtn.textContent = "Sending…";
            (resendBtn as HTMLButtonElement).disabled = true;

            try {
                await authService.resendVerificationCode(email);
                new AlertManager().success("Verification code resent to your email.");
                // Reset to enter code state
                showStatus("enter-code");
                (document.getElementById("verificationCode") as HTMLInputElement).value = "";
            } catch (e) {
                new AlertManager().error("Failed to resend code. Please try again.");
            } finally {
                (resendBtn as HTMLButtonElement).disabled = false;
                resendBtn.textContent = "Resend code";
            }
        });
    }

    async function handleVerification() {
        // Moved to handleVerifyCode above
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
}
