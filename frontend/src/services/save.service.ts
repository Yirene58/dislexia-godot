import { api } from "./api";

import type {
  SaveGame,
  SaveGameRequest,
  SaveGameResponse,
} from "../types/save.types";

export const saveService = {
  async get(
    token: string,
    characterId: number
  ): Promise<SaveGame | null> {
    const response = await api.get<SaveGameResponse>(
      `/characters/${characterId}/save`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data.data;
  },

  async save(
    token: string,
    characterId: number,
    data: SaveGameRequest
  ): Promise<SaveGame | null> {
    const response = await api.put<SaveGameResponse>(
      `/characters/${characterId}/save`,
      data,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data.data;
  },

  async delete(
    token: string,
    characterId: number
  ): Promise<void> {
    await api.delete(
      `/characters/${characterId}/save`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  },
};
