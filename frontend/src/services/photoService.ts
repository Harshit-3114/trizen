import api from "./api";

export const photoService = {
  uploadPhoto: async (eventId: string, file: File, description: string = "") => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("description", description);
    
    const response = await api.post(`/events/${eventId}/photos`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  getPhotosByEvent: async (eventId: string) => {
    const response = await api.get(`/events/${eventId}/photos`);
    return response.data;
  },

  deletePhoto: async (photoId: string) => {
    const response = await api.delete(`/photos/${photoId}`);
    return response.data;
  },
};

