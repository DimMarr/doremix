import { Button } from "@components/generics";
import { authService, isValidPassword } from "@utils/authentication";
import { AppRoutes } from "../router";
import logo from "@assets/images/logo.png";
import { AlertManager } from "@utils/alertManager";

export async function ResetPasswordPage(container, params) {

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
                            Regain access<br/>to your account
                        </h2>
                        <p class="text-lg text-white/80 max-w-md animate-fade-up animation-delay-300">
                            Enter the 6-digit code we sent to your email and set a new password.
                        </p>
                    </div>
                </div>
            </div>

            <div class="p-4 sm:p-8 h-full flex items-center justify-center animate-fade-reveal animation-delay-200">
                <div class="mx-auto flex w-full flex-col justify-center space-y-8 sm:w-[350px]">

                    <div class="relative lg:hidden z-20 flex block justify-center items-center text-lg font-medium animate-fade-right animation-delay-100">
                        <img src={logo} alt="Dorémix" class="mr-2 h-8" />
                    </div>

                    <div id="resetStatusCard" class="flex flex-col items-center space-y-6 text-center animate-fade-up animation-delay-300">

                        {/* Enter Code & New Password */}
                        <div id="statusEnterCode" class="flex flex-col items-center space-y-4 w-full">
                            <div class="space-y-2">
                                <h1 class="text-2xl font-bold tracking-tight">Reset your password</h1>
                                <p id="resetEmailDisplay" class="text-sm text-muted-foreground"></p>
                            </div>
                            <div class="w-full space-y-3">
                                <input id="resetCode" type="text" inputmode="numeric" placeholder="000000" maxlength="6" class="w-full px-4 py-2 rounded-md border border-input text-center text-2xl tracking-widest font-mono bg-background focus:outline-none focus:ring-2 focus:ring-primary" />
                                <div class="space-y-1">
                                    <input id="newPassword" type="password" placeholder="New password" class="w-full px-4 py-2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-primary" />
                                    <span id="toggleNewPasswordVisibility" class="cursor-pointer text-xs text-muted-foreground text-right w-fit ml-auto hover:text-primary transition-colors duration-200">Show password</span>
                                </div>
                                <button id="resetPasswordBtn" class="inline-flex h-10 w-full items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 active:scale-95 duration-200">
                                    Reset Password
                                </button>
                            </div>
                            <div class="flex flex-col w-full gap-2">
                                <a href={AppRoutes.LOGIN} data-link class="inline-flex h-10 w-full items-center justify-center rounded-md bg-muted px-4 py-2 text-sm font-medium text-muted-foreground shadow transition-colors hover:bg-muted/80 active:scale-95 duration-200">
                                    Back to Login
                                </a>
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
                                <h1 class="text-2xl font-bold tracking-tight">Password reset!</h1>
                                <p class="text-sm text-muted-foreground">Your password has been reset successfully. You can now log in.</p>
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
                                <p class="text-sm text-muted-foreground">Your reset code has expired. Request a new one.</p>
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
                                <h1 class="text-2xl font-bold tracking-tight">Invalid code</h1>
                                <p class="text-sm text-muted-foreground">This reset code is invalid or has already been used.</p>
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

    const urlParams = new URLSearchParams(window.location.search);
    const email = urlParams.get("email");

    if (!email) {
        showStatus("invalid");
        startRedirectCountdown("countdownInvalid");
        return;
    }

    // Display the email
    const emailDisplay = document.getElementById("resetEmailDisplay");
    if (emailDisplay) {
        emailDisplay.textContent = email;
    }

    handleResetPassword(email);
    toggleNewPasswordVisibility();

    function showStatus(status: "success" | "expired" | "invalid" | "enter-code") {
        const statuses = ["statusEnterCode", "statusSuccess", "statusExpired", "statusInvalid"];
        statuses.forEach(s => {
            const el = document.getElementById(s);
            if (el) el.classList.add("hidden");
        });

        const id = status === "enter-code" ? "statusEnterCode" : "status" + status.charAt(0).toUpperCase() + status.slice(1);
        const el = document.getElementById(id);
        if (el) el.classList.remove("hidden");
    }

    function handleResetPassword(email: string) {
        const codeInput = document.getElementById("resetCode") as HTMLInputElement;
        const passwordInput = document.getElementById("newPassword") as HTMLInputElement;
        const resetBtn = document.getElementById("resetPasswordBtn");

        if (!codeInput || !passwordInput || !resetBtn) return;

        resetBtn.addEventListener("click", async () => {
            const code = codeInput.value.trim();
            const newPassword = passwordInput.value;

            if (!code || code.length !== 6 || !/^\d{6}$/.test(code)) {
                new AlertManager().error("Please enter a valid 6-digit code.");
                return;
            }

            if (!newPassword) {
                new AlertManager().error("Please enter a new password.");
                return;
            }

            if (!isValidPassword(newPassword)) {
                new AlertManager().error("Your password must be at least 8 characters and contains one uppercase, one lowercase, one digit and one special character.");
                return;
            }

            resetBtn.textContent = "Resetting…";
            (resetBtn as HTMLButtonElement).disabled = true;

            try {
                const result = await authService.resetPassword(email, code, newPassword);

                if (result.status === "reset") {
                    await new Promise(resolve => setTimeout(resolve, 1200));
                    showStatus("success");
                    startRedirectCountdown("countdownSuccess");
                } else {
                    new AlertManager().error("Password reset failed. Please try again.");
                    codeInput.value = "";
                }
            } catch (e: any) {
                const message = e?.message || "";
                if (message.includes("expired")) {
                    showStatus("expired");
                    new AlertManager().warning("Your reset code has expired. Please request a new one.");
                } else if (message.includes("invalid")) {
                    new AlertManager().error("Invalid reset code.");
                    codeInput.value = "";
                } else {
                    new AlertManager().error("Password reset failed. Please try again.");
                    codeInput.value = "";
                }
            } finally {
                (resetBtn as HTMLButtonElement).disabled = false;
                resetBtn.textContent = "Reset Password";
            }
        });

        // Allow Enter key to submit
        passwordInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                resetBtn.click();
            }
        });
    }

    function toggleNewPasswordVisibility() {
        const btn = document.getElementById("toggleNewPasswordVisibility")

        if (!btn) {
            return;
        }

        btn.addEventListener('click', () => {
            const passwordInput = document.getElementById("newPassword") as HTMLInputElement;

            if (!passwordInput) {
                return;
            }

            passwordInput.type == "password" ? passwordInput.type = "text" : passwordInput.type = "password"
        })
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
