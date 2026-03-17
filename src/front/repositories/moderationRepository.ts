import { API_BASE_URL } from "@config/index";
import { AlertManager } from "@utils/alertManager";
import { handleHttpError } from "@utils/errorHandling";

export interface ModerationUser {
    idUser: number;
    email: string;
    username: string;
    role: "USER" | "MODERATOR" | "ADMIN";
    banned: boolean;
}

interface BanUserResponse {
    idUser: number;
    banned: boolean;
    detail: string;
}

export class ModerationRepository {
    async getBanCandidates(): Promise<ModerationUser[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/moderation/ban-candidates`, {
                credentials: "include",
            });
            if (!response.ok) {
                handleHttpError(response, "Fetch ban candidates");
                throw new Error("Failed to fetch ban candidates");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error fetching ban candidates:", error);
            throw error;
        }
    }

    async getUnbanCandidates(): Promise<ModerationUser[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/moderation/unban-candidates`, {
                credentials: "include",
            });
            if (!response.ok) {
                handleHttpError(response, "Fetch unban candidates");
                throw new Error("Failed to fetch unban candidates");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error fetching unban candidates:", error);
            throw error;
        }
    }

    async banUser(idUser: number): Promise<BanUserResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/moderation/users/${idUser}/ban`, {
                method: "POST",
                credentials: "include",
            });
            if (!response.ok) {
                handleHttpError(response, "Ban user");
                throw new Error("Failed to ban user");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error banning user:", error);
            throw error;
        }
    }

    async unbanUser(idUser: number): Promise<BanUserResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/moderation/users/${idUser}/unban`, {
                method: "POST",
                credentials: "include",
            });
            if (!response.ok) {
                handleHttpError(response, "Unban user");
                throw new Error("Failed to unban user");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error unbanning user:", error);
            throw error;
        }
    }
}
