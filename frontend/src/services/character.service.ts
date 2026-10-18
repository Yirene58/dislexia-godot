import { api } from "./api";

import type {
  Character,
  CharacterListResponse,
  CharacterDetailResponse,
  CreateCharacterRequest,
} from "../types/character.types";

export const characterService = {
  async getAll(token: string): Promise<Character[]> {
    const response = await api.get<CharacterListResponse>(
      "/characters",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data.data;
  },

  async create(
    token: string,
    data: CreateCharacterRequest
  ): Promise<Character> {
    const response = await api.post<CharacterDetailResponse>(
      "/characters",
      data,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    return response.data.data;
  },

  async getById(
    token: string,
    characterId: number
  ): Promise<Character> {
    const response = await api.get<CharacterDetailResponse>(
      `/characters/${characterId}`,
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
      `/characters/${characterId}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
  },
};
