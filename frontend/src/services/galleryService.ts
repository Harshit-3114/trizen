import api from "./api";

export const galleryService = {
  getGalleryByEvent: async (eventId: string) => {
    const response = await api.get(`/events/${eventId}/gallery`);
    return response.data;
  },

  verifyPin: async (eventId: string, pin: string) => {
    const response = await api.post(`/events/${eventId}/gallery/verify-pin`, { pin });
    return response.data;
  },
};

