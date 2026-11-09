import api from "./api";

export const eventService = {
  getEvents: async () => {
    const response = await api.get("/events");
    return response.data;
  },

  getEventById: async (eventId: string) => {
    const response = await api.get(`/events/${eventId}`);
    return response.data;
  },

  createEvent: async (eventData: any) => {
    const response = await api.post("/events", eventData);
    return response.data;
  },

  updateEvent: async (eventId: string, eventData: any) => {
    const response = await api.put(`/events/${eventId}`, eventData);
    return response.data;
  },

  deleteEvent: async (eventId: string) => {
    const response = await api.delete(`/events/${eventId}`);
    return response.data;
  },
};

