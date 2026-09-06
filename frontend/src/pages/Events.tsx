import React, { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { eventService } from "../services/eventService";
import { useNavigate } from "react-router-dom";

const Events: React.FC = () => {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    const fetchEvents = async () => {
      try {
        setLoading(true);
        const data = await eventService.getEvents();
        setEvents(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to fetch events");
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, [isAuthenticated, navigate]);

  const handleCreateEvent = () => {
    navigate("/events/create");
  };

  const handleViewEvent = (eventId: string) => {
    navigate(`/events/${eventId}`);
  };

  if (!isAuthenticated) {
    return <div>Redirecting to login...</div>;
  }

  return (
    <div className="events-container">
      <h1>Events</h1>
      {user && <p>Welcome, {user.full_name}!</p>}
      {error && <div className="error-message">{error}</div>}
      <button onClick={handleCreateEvent}>Create New Event</button>
      {loading ? (
        <p>Loading events...</p>
      ) : (
        events.length === 0 ? (
          <p>No events found.</p>
        ) : (
          <div className="events-list">
            {events.map((event: any) => (
              <div key={event.id} className="event-card">
                <h3>{event.title}</h3>
                <p>{event.description}</p>
                <p>
                  <strong>Date:</strong> {new Date(event.start_time).toLocaleDateString()}
                </p>
                <button onClick={() => handleViewEvent(event.id)}>
                  View Event
                </button>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  );
};

export default Events;

