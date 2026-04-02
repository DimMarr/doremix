import { API_BASE_URL } from "@config/index";
import { Genre } from "@models/genre";
import { AlertManager } from "@utils/alertManager";
import { handleHttpError } from "@utils/errorHandling";

export class GenreRepository {
    async getAll(): Promise<Genre[]> {
        try {
            const response = await fetch(`${API_BASE_URL}/genres/`, {
                credentials: "include",
            });
            if (!response.ok) {
                handleHttpError(response, "Fetch genres");
                throw new Error("Failed to fetch genres");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error fetching genres:", error);
            throw error;
        }
    }

    async create(label: string): Promise<Genre> {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/genres/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ label }),
            });

            if (!response.ok) {
                if (response.status === 409) {
                    throw new Error("Conflict");
                }
                handleHttpError(response, "Create genre");
                throw new Error("This genre already exists");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error creating genre:", error);
            throw error;
        }
    }

    async update(id: number, label: string): Promise<Genre> {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/genres/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ label }),
            });

            if (!response.ok) {
                if (response.status === 409) {
                    throw new Error("Conflict");
                }
                handleHttpError(response, "Update genre");
                throw new Error("This genre already exists");
            }
            return response.json();
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error updating genre:", error);
            throw error;
        }
    }

    async delete(id: number): Promise<void> {
        try {
            const response = await fetch(`${API_BASE_URL}/admin/genres/${id}`, {
                method: "DELETE",
                credentials: "include",
            });
            if (!response.ok) {
                handleHttpError(response, "Delete genre");
                throw new Error("Failed to delete genre");
            }
        } catch (error) {
            if (error instanceof TypeError) {
                new AlertManager().error("Network error. Check your connection.");
            }
            console.error("Error deleting genre:", error);
            throw error;
        }
    }
}
