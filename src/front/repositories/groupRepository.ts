import { API_BASE_URL } from "@config/index";

export interface Group {
    idGroup: number;
    groupName: string;
}

export class GroupRepository {
    async getAllGroups(): Promise<Group[]> {
        const response = await fetch(`${API_BASE_URL}/groups/`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }
}
