import api from "./api";

export interface PhotoItem {
  id: number;
  event_id: number;
  uploaded_by: number;
  filename: string;
  storage_url: string;
  content_type: string;
  file_size: number;
  is_selected: boolean;
  created_at: string;
}

export interface PhotoPage {
  items: PhotoItem[];
  total: number;
  page: number;
  page_size: number;
}

export const photoService = {
  uploadPhotos: async (eventId: string | number, files: FileList | File[]) => {
    const formData = new FormData();
    Array.from(files).forEach((f) => formData.append("files", f));
    const response = await api.post(`/events/${eventId}/photos`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data as PhotoItem[];
  },

  getPhotosByEvent: async (
    eventId: string | number,
    opts: { page?: number; page_size?: number; selected_only?: boolean; mine?: boolean } = {}
  ) => {
    const response = await api.get(`/events/${eventId}/photos`, {
      params: {
        page: opts.page ?? 1,
        page_size: opts.page_size ?? 48,
        selected_only: opts.selected_only ?? false,
        mine: opts.mine ?? false,
      },
    });
    return response.data as PhotoPage;
  },

  selectPhotos: async (eventId: string | number, photo_ids: number[], selected: boolean) => {
    const response = await api.patch(`/events/${eventId}/photos/select`, {
      photo_ids,
      selected,
    });
    return response.data;
  },

  deletePhoto: async (eventId: string | number, photoId: number) => {
    await api.delete(`/events/${eventId}/photos/${photoId}`);
  },
};
