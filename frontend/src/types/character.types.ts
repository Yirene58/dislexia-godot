export type CharacterClass =
  | "warrior"
  | "mage"
  | "archer";

export interface Character {
  id: number;
  name: string;
  character_class: CharacterClass;
  level: number;
  experience: number;
}

export interface CreateCharacterRequest {
  name: string;
  character_class: CharacterClass;
}

export interface CharacterListResponse {
  status: number;
  message: string;
  data: Character[];
}

export interface CharacterDetailResponse {
  data: Character;
}
