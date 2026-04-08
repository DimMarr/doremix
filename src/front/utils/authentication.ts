// import { error } from "console";
import { API_BASE_URL } from "@config/index";

export function isValidPassword(password: string): boolean {
    const regex = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*_-]).{8,}$/;
    return regex.test(password)
}

export function isValidEmail(email: string): boolean {
    const regex = /^[^\s@]+@(etu\.)?umontpellier\.fr$/;
    return regex.test(email);
}

class AuthService {
    private isRefreshing = false;
    private refreshQueue: Array<(success: boolean) => void> = [];

    // Central fetch wrapper that transparently handles 401s with a single silent refresh.
    // All requests that fail while a refresh is in-flight are queued and retried once done.
    async fetchWithAuth(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
        const response = await fetch(input, { credentials: 'include', ...init });

        if (response.status !== 401) {
            return response;
        }

        // 401 received — attempt a silent refresh (only one at a time)
        if (this.isRefreshing) {
            // Another refresh is already in flight: queue this request
            await new Promise<boolean>((resolve) => {
                this.refreshQueue.push(resolve);
            }).then((success) => {
                if (!success) throw new Error('Session expired');
            });
            return fetch(input, { credentials: 'include', ...init });
        }

        this.isRefreshing = true;
        const refreshed = await this.refreshAccessToken();
        this.isRefreshing = false;

        // Notify all queued requests
        this.refreshQueue.forEach((resolve) => resolve(refreshed));
        this.refreshQueue = [];

        if (!refreshed) {
            throw new Error('Session expired');
        }

        // Retry the original request with the new access token
        return fetch(input, { credentials: 'include', ...init });
    }

    // isAuthenticated now uses fetchWithAuth against /auth/me — no dedicated check-token call needed.
    async isAuthenticated(): Promise<boolean> {
        try {
            await this.infos();
            return true;
        } catch {
            return false;
        }
    }

    // Login provides a new accessToken
    async login(email, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    "email": email,
                    "password": password
                })
            })

            const result = await response.json()

            if (!response.ok) {
                throw new Error(result.detail || "Login failed");
            }
            this.infosPromise = undefined;
        } catch (e) {
            console.log('Login failed', e);
            throw e;
        }

    }

    async register(email, password) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    "email": email,
                    "password": password
                })
            })

            const result = await response.json()

            if (!response.ok) {
                throw new Error(result.detail || "Register failed");
            }
            this.infosPromise = undefined;
        } catch (e) {
            console.log('Register failed', e);
            throw e;
        }

    }

    // refresh accessToken through refreshToken
    async refreshAccessToken() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                credentials: 'include'
            })

            if (response.status == 200) {
                this.infosPromise = undefined;
                return true;
            }
            return false;
        } catch (e) {
            console.error("Failed to refresh token:", e);
            return false;
        }
    }


    async logout() {
        await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        })
        this.infosPromise = undefined;
    }

    private infosPromise?: Promise<any>;

    async infos() {
        if (!this.infosPromise) {
            this.infosPromise = (async () => {
                const response = await this.fetchWithAuth(`${API_BASE_URL}/auth/me`, {
                    method: 'GET',
                });
                if (!response.ok) {
                    this.infosPromise = undefined;
                    throw new Error('Failed to fetch infos');
                }
                return response.json();
            })();
        }
        return this.infosPromise;
    }



    async resend_verification_email(token: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/resend-verification-email?token=${encodeURIComponent(token)}`, {
                method: 'POST',
                credentials: 'include'
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Resend failed");
            }

            return result;
        } catch (e) {
            console.error('Resend verification email failed', e);
            throw e;
        }
    }

    async verifyCode(email: string, code: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/verify-email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    email: email,
                    code: code
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Email verification failed");
            }

            return result;
        } catch (e) {
            console.error("Email code verification failed:", e);
            throw e;
        }
    }

    async resendVerificationCode(email: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/resend-verification-email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    email: email
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Resend failed");
            }

            return result;
        } catch (e) {
            console.error('Resend verification code failed', e);
            throw e;
        }
    }

    async requestPasswordReset(email: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/request-password-reset`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    email: email
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Password reset request failed");
            }

            return result;
        } catch (e) {
            console.error('Password reset request failed', e);
            throw e;
        }
    }

    async resetPassword(email: string, code: string, new_password: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    email: email,
                    code: code,
                    new_password: new_password
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Password reset failed");
            }

            return result;
        } catch (e) {
            console.error('Password reset failed', e);
            throw e;
        }
    }

    async resendPasswordResetCode(email: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/request-password-reset`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    email: email
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Resend failed");
            }

            return result;
        } catch (e) {
            console.error('Resend password reset code failed', e);
            throw e;
        }
    }
}

export const authService = new AuthService();
