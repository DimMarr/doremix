import { API_BASE_URL } from "@config/index";
import { handleHttpError } from "@utils/errorHandling";
import { authService } from "@utils/authentication";

export interface Group {
    idGroup: number;
    groupName: string;
}

export interface GroupMember {
    idUser: number;
    username: string;
    email: string;
}

export interface GroupWithUsers extends Group {
    users: GroupMember[];
}

export class GroupRepository {
    async getAllGroups(): Promise<Group[]> {
        const response = await authService.fetchWithAuth(`${API_BASE_URL}/groups/`, {
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

    async adminGetAllGroups(): Promise<GroupWithUsers[]> {
        const response = await authService.fetchWithAuth(`${API_BASE_URL}/admin/groups/`, {
            method: "GET",
            credentials: "include",
        });

        if (!response.ok) {
            handleHttpError(response, "Fetch groups");
            throw new Error("Failed to fetch groups");
        }

        return response.json();
    }

    async adminCreateGroup(groupName: string): Promise<Group> {
        const response = await authService.fetchWithAuth(`${API_BASE_URL}/admin/groups/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ groupName }),
        });

        if (!response.ok) {
            if (response.status === 409) {
                throw new Error("Conflict");
            }
            handleHttpError(response, "Create group");
            throw new Error("Failed to create group");
        }

        return response.json();
    }

    async adminDeleteGroup(groupId: number): Promise<void> {
        const response = await authService.fetchWithAuth(`${API_BASE_URL}/admin/groups/${groupId}`, {
            method: "DELETE",
            credentials: "include",
        });

        if (!response.ok) {
            handleHttpError(response, "Delete group");
            throw new Error("Failed to delete group");
        }
    }

    async adminAddUser(groupId: number, userId: number): Promise<void> {
        const response = await authService.fetchWithAuth(
            `${API_BASE_URL}/admin/groups/${groupId}/users/${userId}`,
            {
                method: "POST",
                credentials: "include",
            }
        );

        if (!response.ok) {
            if (response.status === 409) {
                throw new Error("Conflict");
            }
            handleHttpError(response, "Add user to group");
            throw new Error("Failed to add user");
        }
    }

    async adminRemoveUser(groupId: number, userId: number): Promise<void> {
        const response = await authService.fetchWithAuth(
            `${API_BASE_URL}/admin/groups/${groupId}/users/${userId}`,
            {
                method: "DELETE",
                credentials: "include",
            }
        );

        if (!response.ok) {
            handleHttpError(response, "Remove user from group");
            throw new Error("Failed to remove user");
        }
    }
}
