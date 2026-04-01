import { API_BASE_URL } from "@config/index";
import { AlertManager } from "@utils/alertManager";

export class UserRepository {
    async getAllUsers() {
        const response = await fetch(`${API_BASE_URL}/users`, {
          credentials: 'include'
        });

        if (!response.ok) {
          throw new Error("You don't have correct rights to list all users.");
        }
        return response.json();
      }

    async addModerator(idUser: number) {
        try {
            const response = await fetch(`${API_BASE_URL}/users/${idUser}/add-moderator`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error("Failed to add moderator.");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error adding user to moderators:", error);
            throw error;
        }
    }

    async demoteModerator(idUser: number) {
        try {
            const response = await fetch(`${API_BASE_URL}/users/${idUser}/demote-moderator`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error("Failed to demote moderator.");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error demoting user from moderators:", error);
            throw error;
        }
    }
}
