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

            if (response.status == 200) {
                return true
            }
        } catch {
            const refresh = await this.refreshAccessToken()
            console.log(`refresh: ${refresh}`)
            if (refresh) {
                return true
            }
            return false
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
                throw new Error(result.message || "Login failed");
            }
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
        } catch (e) {
            console.log('Register failed', e);
            throw e;
        }

    }

    // refresh accessToken through refreshToken
    async refreshAccessToken() {
        const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            credentials: 'include'
        })

        return response.status == 200
    }

    async logout() {
        const response = await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        })

    }

    async iduser() {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            method: 'GET',
            credentials: 'include'
        })

        const result = response.json()
        return result
    }
}

export const authService = new AuthService();
