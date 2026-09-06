import React, { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { eventService } from "../services/eventService";
import { photoService } from "../services/photoService";
import { membershipService } from "../services/membershipService";
import { galleryService } from "../services/galleryService";
import { useNavigate, useParams } from "react-router-dom";

const EventDetail: React.FC = () => {
  const [event, setEvent] = useState<any>(null);
  const [photos, setPhotos] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { user, isAuthenticated } = useAuth();
  const { eventId } = useParams<{ eventId: string }>();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    const fetchEventData = async () => {
      try {
        setLoading(true);
        const [eventData, photosData, membersData] = await Promise.all([
          eventService.getEventById(eventId!),
          photoService.getPhotosByEvent(eventId!),
          membershipService.getEventMembers(eventId!),
        ]);
        setEvent(eventData);
        setPhotos(photosData);
        setMembers(membersData);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to fetch event data");
      } finally {
        setLoading(false);
      }
    };

    fetchEventData();
  }, [isAuthenticated, navigate, eventId]);

  const handleAddPhoto = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      try {
        await photoService.uploadPhoto(eventId!, e.target.files[0]);
        // Refresh photos after upload
        const photosData = await photoService.getPhotosByEvent(eventId!);
        setPhotos(photosData);
        e.target.value = ""; // Reset file input
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to upload photo");
      }
    }
  };

  const handleAddMember = () => {
    // In a real app, this would open a modal or form to add a member
    alert("Add member functionality would go here");
  };

  if (!isAuthenticated) {
    return <div>Redirecting to login...</div>;
  }

  if (!event) {
    return <div>Loading event...</div>;
  }

  return (
    <div className="event-detail-container">
      <h1>{event.title}</h1>
      <p>{event.description}</p>
      <p>
        <strong>Start Time:</strong> {new Date(event.start_time).toLocaleString()}
      </p>
      <p>
        <strong>End Time:</strong> {new Date(event.end_time).toLocaleString()}
      </p>
      {error && <div className="error-message">{error}</div>}
      
      <div className="event-tabs">
        <button>Photos ({photos.length})</button>
        <button>Members ({members.length})</button>
        <button>Gallery</button>
      </div>
      
      <div className="tab-content">
        {/* Photos Tab */}
        <div>
          <h2>Photos</h2>
          <input type="file" accept="image/*" onChange={handleAddPhoto} />
          {photos.length > 0 ? (
            <div className="photos-grid">
              {photos.map((photo: any) => (
                <div key={photo.id} className="photo-item">
                  <img 
                    src={`${import.meta.env.VITE_API_URL}/uploads/${photo.filename}`} 
                    alt={photo.description || "Photo"}
                  />
                  <p>{photo.description || ""}</p>
                </div>
              ))}
            </div>
          ) : (
            <p>No photos uploaded yet.</p>
          )}
        </div>
        
        {/* Members Tab */}
        <div>
          <h2>Members</h2>
          <button onClick={handleAddMember}>Add Member</button>
          {members.length > 0 ? (
            <ul className="members-list">
              {members.map((member: any) => (
                <li key={member.id}>
                  {member.full_name} ({member.role})
                </li>
              ))}
            </ul>
          ) : (
            <p>No members yet.</p>
          )}
        </div>
        
        {/* Gallery Tab */}
        <div>
          <h2>Gallery</h2>
          {/* Gallery functionality would go here */}
          <p>Gallery view with PIN protection</p>
        </div>
      </div>
    </div>
  );
};

export default EventDetail;

