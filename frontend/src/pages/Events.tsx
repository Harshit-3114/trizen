import React, { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { eventService } from "../services/eventService"; import EmptyState from "../components/EmptyState";
import { useNavigate } from "react-router-dom";

interface EventItem {
  id: number;
  name: string;
  description: string;
  admin_id: number;
  created_at: string;
  total_photos: number;
  selected_photos: number;
  member_count: number;
}

const Events: React.FC = () => {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const fetchEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await eventService.getEvents();
      setEvents(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to fetch events");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    fetchEvents();
  }, [isAuthenticated, navigate]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    setCreating(true);
    try {
      const created = await eventService.createEvent({ name: name.trim(), description: description.trim() });
      setName("");
      setDescription("");
      setEvents((prev) => [{ ...created, total_photos: 0, selected_photos: 0, member_count: 0 }, ...prev]);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create event");
    } finally {
      setCreating(false);
    }
  };

  if (!isAuthenticated) {
    return <div>Redirecting to login...</div>;
  }

  return (
    <div className="events-container">
      <div className="kicker">Studio</div>
      <h1>Events</h1>
      {user && <p className="muted">Signed in as {user.full_name || user.email} ({user.role})</p>}
      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleCreate} className="card form-card">
        <h3>Create event</h3>
        <input
          type="text"
          aria-label="Event name"
          placeholder="Event name (e.g. Arjun and Priya Wedding)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          maxLength={200}
        />
        <textarea
          aria-label="Event description"
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={2}
          maxLength={2000}
        />
        <button type="submit" disabled={creating || !name.trim()}>
          {creating ? "Creating..." : "Create event"}
        </button>
      </form>

      {loading ? (
        <p>Loading events...</p>
      ) : events.length === 0 ? (
        <EmptyState title="No events yet" hint="Create one above, or ask an admin to add you as a team member." />
      ) : (
        <div className="events-list">
          {events.map((event) => (
            <div key={event.id} className="event-card">
              <img
                className="cover"
                src={`https://picsum.photos/seed/trizen-event-${event.id}/600/300`}
                alt={`Cover for ${event.name}`}
                loading="lazy"
              />
              <div className="event-body">
                <h3>{event.name}</h3>
                {event.description && <p>{event.description}</p>}
                <p className="muted">
                  {event.total_photos} uploaded | {event.selected_photos} selected | {event.member_count} members
                </p>
                <button onClick={() => navigate(`/events/${event.id}`)}>Open event</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Events;
