import api from "./api";

export const membershipService = {
  getEventMembers: async (eventId: string | number) => {
    const response = await api.get(`/events/${eventId}/members`);
    return response.data;
  },

  addMemberByEmail: async (eventId: string | number, email: string) => {
    const response = await api.post(`/events/${eventId}/members`, { email });
    return response.data;
  },

  removeMember: async (eventId: string | number, userId: number) => {
    await api.delete(`/events/${eventId}/members/${userId}`);
  },
};
