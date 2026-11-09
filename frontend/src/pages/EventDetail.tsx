import React, { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { eventService } from "../services/eventService";
import { photoService, PhotoPage } from "../services/photoService";
import { membershipService } from "../services/membershipService";
import { galleryService } from "../services/galleryService";
import { photoUrl } from "../services/api"; import EmptyState from "../components/EmptyState";

type Tab = "photos" | "members" | "galleries";

const EventDetail: React.FC = () => {
  const { eventId } = useParams<{ eventId: string }>();
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [event, setEvent] = useState<any>(null);
  const [photos, setPhotos] = useState<PhotoPage | null>(null);
  const [page, setPage] = useState(1);
  const [selectedOnly, setSelectedOnly] = useState(false);
  const [mineOnly, setMineOnly] = useState(false);
  const [members, setMembers] = useState<any[]>([]);
  const [galleries, setGalleries] = useState<any[]>([]);
  const [tab, setTab] = useState<Tab>("photos");
  const [checked, setChecked] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [memberEmail, setMemberEmail] = useState("");
  const [galleryTitle, setGalleryTitle] = useState("");
  const [galleryPin, setGalleryPin] = useState("");

  const isEventAdmin = event && user && (event.admin_id === user.id || user.role === "admin");

  const loadPhotos = useCallback(
    async (p: number, sel: boolean, mine: boolean) => {
      const data = await photoService.getPhotosByEvent(eventId!, {
        page: p,
        page_size: 48,
        selected_only: sel,
        mine,
      });
      setPhotos(data);
    },
    [eventId]
  );

  const refreshAll = useCallback(async () => {
    const [eventData, membersData, galleriesData] = await Promise.all([
      eventService.getEventById(eventId!),
      membershipService.getEventMembers(eventId!).catch(() => []),
      galleryService.listGalleries(eventId!).catch(() => []),
    ]);
    setEvent(eventData);
    setMembers(membersData);
    setGalleries(galleriesData);
  }, [eventId]);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }
    (async () => {
      try {
        setLoading(true);
        setError(null);
        await refreshAll();
        await loadPhotos(1, false, false);
      } catch (err: any) {
        const status = err.response?.status; setError(status === 404 ? "This event does not exist, or you have not been added to it yet. Ask the event admin to invite you by email, then refresh." : err.response?.data?.detail || "Failed to load event.");
      } finally {
        setLoading(false);
      }
    })();
  }, [isAuthenticated, navigate, refreshAll, loadPhotos]);

  useEffect(() => {
    if (eventId) loadPhotos(page, selectedOnly, mineOnly).catch(() => {});
  }, [page, selectedOnly, mineOnly, eventId, loadPhotos]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    setUploading(true);
    setError(null);
    try {
      await photoService.uploadPhotos(eventId!, e.target.files);
      setNotice(`Uploaded ${e.target.files.length} photo(s).`);
      await refreshAll();
      await loadPhotos(page, selectedOnly, mineOnly);
      e.target.value = "";
    } catch (err: any) {
      setError(err.response?.data?.detail || "Photo upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const toggleCheck = (id: number) => {
    setChecked((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleSelect = async (selected: boolean) => {
    if (checked.size === 0) return;
    try {
      const res = await photoService.selectPhotos(eventId!, Array.from(checked), selected);
      setNotice(`Marked ${res.updated} photo(s) as ${selected ? "selected" : "unselected"}.`);
      setChecked(new Set());
      await refreshAll();
      await loadPhotos(page, selectedOnly, mineOnly);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Selection update failed.");
    }
  };

  const handleDeletePhoto = async (photoId: number) => {
    if (!window.confirm("Delete this photo?")) return;
    try {
      await photoService.deletePhoto(eventId!, photoId);
      await refreshAll();
      await loadPhotos(page, selectedOnly, mineOnly);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Delete failed.");
    }
  };

  const handleAddMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!memberEmail.trim()) return;
    try {
      await membershipService.addMemberByEmail(eventId!, memberEmail.trim());
      setMemberEmail("");
      setNotice("Team member added.");
      const membersData = await membershipService.getEventMembers(eventId!);
      setMembers(membersData);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not add member.");
    }
  };

  const handleRemoveMember = async (userId: number) => {
    if (!window.confirm("Remove this member?")) return;
    try {
      await membershipService.removeMember(eventId!, userId);
      setMembers((prev) => prev.filter((m) => m.id !== userId));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not remove member.");
    }
  };

  const handlePublish = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const selectedIds = (photos?.items || []).filter((p) => p.is_selected).map((p) => p.id);
      const ids = selectedIds.length > 0 ? selectedIds : Array.from(checked);
      if (ids.length === 0) {
        setError("Select at least one photo first (tick the checkboxes).");
        return;
      }
      const gallery = await galleryService.createGallery(eventId!, {
        title: galleryTitle.trim() || `${event?.name} Gallery`,
        pin: galleryPin.trim(),
        photo_ids: ids,
      });
      const published = await galleryService.publishGallery(eventId!, gallery.id);
      const link = `${window.location.origin}/gallery/${published.slug}`;
      setNotice(`Published! Share this link with the customer: ${link}  PIN: ${galleryPin.trim()}`);
      setGalleryTitle("");
      setGalleryPin("");
      setChecked(new Set());
      setGalleries(await galleryService.listGalleries(eventId!));
    } catch (err: any) {
      setError(err.response?.data?.detail || "Publish failed.");
    }
  };

  if (!isAuthenticated) return <div>Redirecting to login...</div>;
  if (loading) return <div className="page"><p>Loading event...</p></div>; if (!event) return (<div className="page event-detail"><button className="btn btn-sm" onClick={() => navigate("/events")}>Back to events</button><div className="error-message">{error || "Event not found."}</div></div>);

  return (
    <div className="page event-detail">
      <button className="btn btn-sm" onClick={() => navigate("/events")}>Back to events</button><img className="event-cover" src={`https://picsum.photos/seed/trizen-event-${event.id}/1200/440`} alt={`Cover for ${event.name}`} />
      <h2>{event.name}</h2>
      {event.description && <p>{event.description}</p>}
      <p className="muted">
        {event.total_photos} uploaded | {event.selected_photos} selected | {event.member_count} members
      </p>
      {error && <div className="error-message">{error}</div>}
      {notice && <div className="notice-message">{notice}</div>}

      <div className="tabs">
        {(["photos", "members", "galleries"] as Tab[]).map((t) => (
          <button key={t} className={tab === t ? "tab active" : "tab"} onClick={() => setTab(t)}>
            {t === "photos" ? `Photos (${event.total_photos})` : t === "members" ? `Members (${members.length})` : `Galleries (${galleries.length})`}
          </button>
        ))}
      </div>

      {tab === "photos" && (
        <>
          <div className="toolbar">
            <label className="btn">
              {uploading ? "Uploading..." : "Upload photos"}
              <input type="file" accept="image/jpeg,image/png,image/webp,image/heic,image/heif" multiple hidden onChange={handleUpload} disabled={uploading} />
            </label>
            <label><input type="checkbox" checked={selectedOnly} onChange={(e) => { setSelectedOnly(e.target.checked); setPage(1); }} /> Selected only</label>
            <label><input type="checkbox" checked={mineOnly} onChange={(e) => { setMineOnly(e.target.checked); setPage(1); }} /> My uploads</label>
            {isEventAdmin && checked.size > 0 && (
              <>
                <button className="btn btn-sm" onClick={() => handleSelect(true)}>Select ({checked.size})</button>
                <button className="btn btn-sm" onClick={() => handleSelect(false)}>Unselect</button>
              </>
            )}
          </div>
          {!photos || photos.items.length === 0 ? (
            <EmptyState title="No photos yet" hint="Upload the first batch above â€” JPEG, PNG, WebP or HEIC, up to 50 at a time." />
          ) : (
            <>
              <div className="photos-grid">
                {photos.items.map((p) => (
                  <div key={p.id} className={p.is_selected ? "photo-item selected" : "photo-item"}>
                    <img src={photoUrl(p.storage_url)} alt={p.filename} loading="lazy" />
                    <div className="photo-meta">
                      {isEventAdmin && (
                        <input type="checkbox" checked={checked.has(p.id)} onChange={() => toggleCheck(p.id)} title="Select for gallery" />
                      )}
                      <span className="muted">{p.filename}</span>
                      {p.is_selected && <span className="badge">Selected</span>}
                      <button className="btn btn-sm btn-danger" onClick={() => handleDeletePhoto(p.id)}>Delete</button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="pager">
                <button className="btn btn-sm" disabled={page <= 1} onClick={() => setPage((v) => v - 1)}>Prev</button>
                <span className="muted">Page {photos.page} of {Math.max(1, Math.ceil(photos.total / photos.page_size))} ({photos.total})</span>
                <button
                  className="btn btn-sm"
                  disabled={page * photos.page_size >= photos.total}
                  onClick={() => setPage((v) => v + 1)}
                >
                  Next
                </button>
              </div>
            </>
          )}
        </>
      )}

      {tab === "members" && (
        <div className="card">
          <h3>Team members</h3>
          {isEventAdmin ? (
            <form onSubmit={handleAddMember} className="inline-form">
              <input
                type="email"
                aria-label="Team member email" placeholder="teammate@example.com"
                value={memberEmail}
                onChange={(e) => setMemberEmail(e.target.value)}
                required
              />
              <button type="submit">Add member</button>
            </form>
          ) : (
            <p className="muted">Only the event admin can add or remove members.</p>
          )}
          {members.length === 0 ? (
            <EmptyState title="No members yet" hint="The event admin can invite teammates by email." />
          ) : (
            <ul className="members-list">
              {members.map((m: any) => (
                <li key={m.id}>
                  <span>{m.full_name || m.email} ({m.email}) - {m.role}</span>
                  {isEventAdmin && m.role !== "admin" && (
                    <button className="btn btn-sm btn-danger" onClick={() => handleRemoveMember(m.id)}>Remove</button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {tab === "galleries" && (
        <div>
          {isEventAdmin && (
            <form onSubmit={handlePublish} className="card form-card">
              <h3>Publish gallery</h3>
              <p className="muted">Uses selected photos (or ticked checkboxes). Generates a shareable link + PIN for the customer.</p>
              <input
                type="text"
                aria-label="Gallery title" placeholder="Gallery title"
                value={galleryTitle}
                onChange={(e) => setGalleryTitle(e.target.value)}
                maxLength={200}
              />
              <input
                type="text"
                inputMode="numeric"
                aria-label="Gallery PIN, 4 to 12 digits" placeholder="PIN (4-12 digits)"
                value={galleryPin}
                onChange={(e) => setGalleryPin(e.target.value)}
                required
                pattern="[0-9]{4,12}"
                title="4 to 12 digits"
              />
              <button type="submit">Create and publish</button>
            </form>
          )}
          {galleries.length === 0 ? (
            <EmptyState title="No galleries yet" hint="Select keepers, set a PIN, and publish your first customer gallery." />
          ) : (
            <div className="events-list">
              {galleries.map((g: any) => (
                <div key={g.id} className="event-card">
                  <h4>{g.title}</h4>
                  <p className="muted">{g.photo_count} photos | {g.is_published ? "Published" : "Draft"}</p>
                  {g.is_published ? (
                    <p className="share-link">{window.location.origin}/gallery/{g.slug}</p>
                  ) : (
                    isEventAdmin && (
                      <button
                        className="btn btn-sm"
                        onClick={async () => {
                          await galleryService.publishGallery(eventId!, g.id);
                          setGalleries(await galleryService.listGalleries(eventId!));
                        }}
                      >
                        Publish now
                      </button>
                    )
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EventDetail;
