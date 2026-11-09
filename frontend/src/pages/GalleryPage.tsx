import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { galleryService } from "../services/galleryService";
import { photoUrl } from "../services/api";

const GalleryPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [meta, setMeta] = useState<any>(null);
  const [pin, setPin] = useState("");
  const [photos, setPhotos] = useState<any[]>([]);
  const [title, setTitle] = useState("");
  const [eventName, setEventName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [unlocking, setUnlocking] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const m = await galleryService.getPublicMeta(slug!);
        setMeta(m);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Gallery not found or not published yet.");
      } finally {
        setLoading(false);
      }
    };
    if (slug) load();
  }, [slug]);

  const handleUnlock = async (e: React.FormEvent) => {
    e.preventDefault();
    setUnlocking(true);
    setError(null);
    try {
      const data = await galleryService.unlockGallery(slug!, pin);
      setPhotos(data.photos);
      setTitle(data.title);
      setEventName(data.event_name);
    } catch (err: any) {
      const status = err.response?.status;
      setError(
        status === 401
          ? "Incorrect PIN. Please check the PIN shared with you and try again."
          : status === 429
          ? "Too many attempts. Please wait a few minutes and try again."
          : err.response?.data?.detail || "Could not open gallery."
      );
    } finally {
      setUnlocking(false);
    }
  };

  if (loading) return <div className="page"><p>Loading gallery...</p></div>;

  return (
    <div className="page gallery-public">
      {photos.length === 0 ? (
        <div className="card form-card">
          <img className="event-cover" src={`https://picsum.photos/seed/trizen-gallery-${slug}/1200/440`} alt="Gallery cover" /><h2>{meta ? meta.title : "Customer gallery"}</h2>
          {meta && <p className="muted">{meta.event_name} | {meta.photo_count} photos</p>}
          {error && <div className="error-message">{error}</div>}
          <p>Enter the PIN shared with you to view the photos. No account needed.</p>
          <form onSubmit={handleUnlock}>
            <input
              type="password"
              inputMode="numeric"
              aria-label="Gallery access PIN" placeholder="Access PIN"
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              required
              minLength={4}
              maxLength={12}
            />
            <button type="submit" disabled={unlocking || !pin}>
              {unlocking ? "Checking..." : "View photos"}
            </button>
          </form>
        </div>
      ) : (
        <>
          <h2>{title}</h2>
          {eventName && <p className="muted">{eventName} | {photos.length} photos</p>}
          <div className="photos-grid">
            {photos.map((p: any) => (
              <div key={p.id} className="photo-item">
                <img src={photoUrl(p.storage_url)} alt={p.filename} loading="lazy" />
                <p className="muted">{p.filename}</p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default GalleryPage;
