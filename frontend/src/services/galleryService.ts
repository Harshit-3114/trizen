import api from "./api";

export const galleryService = {
  listGalleries: async (eventId: string | number) => {
    const response = await api.get(`/events/${eventId}/galleries`);
    return response.data;
  },

  getGallery: async (eventId: string | number, galleryId: number) => {
    const response = await api.get(`/events/${eventId}/galleries/${galleryId}`);
    return response.data;
  },

  createGallery: async (
    eventId: string | number,
    data: { title: string; pin: string; photo_ids?: number[] }
  ) => {
    const response = await api.post(`/events/${eventId}/galleries`, data);
    return response.data;
  },

  publishGallery: async (eventId: string | number, galleryId: number) => {
    const response = await api.post(
      `/events/${eventId}/galleries/${galleryId}/publish`
    );
    return response.data;
  },

  unpublishGallery: async (eventId: string | number, galleryId: number) => {
    const response = await api.post(
      `/events/${eventId}/galleries/${galleryId}/unpublish`
    );
    return response.data;
  },

  getPublicMeta: async (slug: string) => {
    const response = await api.get(`/public/galleries/${slug}/meta`);
    return response.data;
  },

  unlockGallery: async (slug: string, pin: string) => {
    const response = await api.post(`/public/galleries/${slug}/photos`, { pin });
    return response.data;
  },
};
