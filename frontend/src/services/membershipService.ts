import api from "./api";

export const membershipService = {
  getEventMembers: async (eventId: string) => {
    const response = await api.get(`/events/${eventId}/members`);
    return response.data;
  },

  addMember: async (eventId: string, userId: string, role: string = "member") => {
    const response = await api.post(`/events/${eventId}/members`, { userId, role });
    return response.data;
  },

  removeMember: async (eventId: string, userId: string) => {
    const response = await api.delete(`/events/${eventId}/members/${userId}`);
    return response.data;
  },

  updateMemberRole: async (eventId: string, userId: string, role: string) => {
    const response = await api.put(`/events/${eventId}/members/${userId}`, { role });
    return response.data;
  },
};

