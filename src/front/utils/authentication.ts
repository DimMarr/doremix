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
        // const hasRefreshToken = document.cookie.includes("refreshToken")
        // const hasAccessToken = document.cookie.includes("accessToken")

        // if (!hasAccessToken){
        //     return false
        // }

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
            console.log(result)
            // document.cookie = `accessToken=${result.access_token}; path=/`
            // document.cookie = `refreshToken=${result.refresh_token}; path=/`
        } catch (e) {
            console.log('Login failed', e);
            throw e;
        }

    }

    // refresh accessToken through refreshToken
    async refreshAccessToken() {
        try {
            const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
                method: 'POST',
                credentials: 'include' // or include ?
            })

            return response.status == 200
        } catch (e) {
            console.error("Failed to refresh token:", e);
            return false;
        }

        // Trying to replicate success without backend
        // if(document.cookie.includes("refreshToken")){
        //     this.accessToken = Math.random().toString(36).substring(2, 2 + 6);
        //     console.log("accessToken provided.")
        //     return
        // }
        // console.log("Do not have a refreshToken.")

    }

    async logout() {
        // this.accessToken = null;
        // document.cookie = "refreshToken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/";
        const response = await fetch(`${API_BASE_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include' // or include ?
        })

    }
}

export const authService = new AuthService();
