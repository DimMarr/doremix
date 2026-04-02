// import { error } from "console";
import { API_BASE_URL } from "@config/index";

export function isValidPassword(password: string): boolean {
    const regex = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$/;
    return regex.test(password)
}

export function isValidEmail(email: string): boolean {
    const regex = /^[^\s@]+@(etu\.)?umontpellier\.fr$/;
    return regex.test(email);
}

class AuthService {
    async isAuthenticated() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/check-token`, {
                method: 'POST',
                credentials: 'include'
            })

            if (response.status === 200) {
                return true
            }
        } catch (e) {
            console.error("Network error during token check:", e);
        }

        const refresh = await this.refreshAccessToken()
        console.log(`refresh: ${refresh}`)
        if (refresh) {
            return true
        }
        return false
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
                throw new Error(result.message || "Login failed");
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
                throw new Error(result.message || "Register failed");
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
        const response = await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        })
        this.infosPromise = undefined;
    }

    private infosPromise?: Promise<any>;

    async infos() {
        if (!this.infosPromise) {
            this.infosPromise = (async () => {
                const response = await fetch(`${API_BASE_URL}/auth/me`, {
                    method: 'GET',
                    credentials: 'include'
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

    async verify_email(token: string) {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/verify-email?token=${encodeURIComponent(token)}`, {
                method: 'GET',
                credentials: 'include'
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || "Email verification failed");
            }

            return result;

        } catch (e) {
            console.error("Email validation failed:", e);
            throw e;
        }
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
}

export const authService = new AuthService();
