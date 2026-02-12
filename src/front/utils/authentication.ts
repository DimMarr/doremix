import { error } from "console";
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
    /*
     * La classe AuthService contient un attribut accessToken
     * Si l'utilisateur a un accessToken, on vérifie la validité
     * Si le token est valide, on est authentifié. Sinon, si on a un cookie refreshToken, on essaie de générer un nouveau accessToken.
     * Si on a réussi à le générer, on est authentifié. Sinon, on est renvoyé vers login.
     */

    accessToken: string | null;
    constructor() {
        this.accessToken = null;
    }

    async isAuthenticated(){
        const hasRefreshToken = document.cookie.includes("refreshToken")

        // Check if accessToken is still valid
        // if yes, return true (isAuthenticated)
        // if no, set this.accessToken = null
        // try{
        //     const response = await fetch(`${API_BASE_URL}/auth/checkAccessToken`, {
        //         method: 'POST',
        //         credentials: 'same-origin'
        //     })

        //     const data = await response.json();
        //     if (data.valid == false) {
        //         this.accessToken = null;
        //     } else {
        //         return true
        //     }
        // } catch (e) {
        //     console.error('Cannot check accessToken validity', e);
        //     throw error;
        // }

        // If no accessToken, try to get a new one
        if(this.accessToken == null && hasRefreshToken){
            console.log("Calling for a new refreshAccessToken")
            await this.refreshAccessToken();
        }
        console.log("accessToken :", this.accessToken)

        return this.accessToken != null;
    }

    // Login provides a new accessToken
    async login(email, password){
        // try{
        //     const response = await fetch(`${API_BASE_URL}/auth/login`, {
        //         method: 'POST',
        //         headers: { 'Content-Type': 'application/json'},
        //         credentials: 'same-origin', // or include ?
        //         body: JSON.stringify({email, password})
        //     })

        //     const data = await response.json();
        //     this.accessToken = data.accessToken;
        // } catch (e) {
        //     console.error('Login failed', e);
        //     throw error;
        // }

        document.cookie = `refreshToken=${Math.random().toString(36).substring(2, 2 + 16)}`;
        this.accessToken = Math.random().toString(36).substring(2, 2 + 6);;
    }

    // refresh accessToken through refreshToken
    async refreshAccessToken() {
        // try {
        //     const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        //         method: 'POST',
        //         credentials: 'same-origin' // or include ?
        //     })

        //     const data = await response.json()
        //     this.accessToken = data.accessToken;
        // } catch(e) {
        //     console.error('Token refresh failed', e);
        //     throw error;
        // }

        // Trying to replicate success without backend
        if(document.cookie.includes("refreshToken")){
            this.accessToken = Math.random().toString(36).substring(2, 2 + 6);
            console.log("accessToken provided.")
            return
        }
        console.log("Do not have a refreshToken.")

    }

    async logout() {
        this.accessToken = null;
        // const response = await fetch(`${API_BASE_URL}/auth/logout`, {
        //     method: 'POST',
        //     credentials: 'same-origin' // or include ?
        // })
    }
}

export const authService = new AuthService();
