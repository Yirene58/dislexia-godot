export type SaveStatus = "in_progress" | "completed";

export interface SaveGame {
  id: number;
  character_id: number;
  world_id: string;
  checkpoint_id: string;
  status: SaveStatus;
  progress_data: Record<string, unknown>;
  updated_at: string | null;
}

export interface SaveGameRequest {
  world_id: string;
  checkpoint_id: string;
  status?: SaveStatus;
  progress_data?: Record<string, unknown>;
}

export interface SaveGameResponse {
  status: number;
  message: string;
  data: SaveGame | null;
}
