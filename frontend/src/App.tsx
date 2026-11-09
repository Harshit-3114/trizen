import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Landing from "./pages/Landing";
import Events from "./pages/Events";
import EventDetail from "./pages/EventDetail";
import GalleryPage from "./pages/GalleryPage"; import Logo from "./components/Logo";
import "./App.css";

function ProtectedRoute({ children }: { children: JSX.Element }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function NavBar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const handleLogout = () => {
    logout();
    navigate("/login");
  };
  return (
    <nav className="navbar">
      <Link to="/" className="brand"><Logo size={30} /></Link>
      <div className="nav-links">
        {isAuthenticated ? (
          <>
            <Link to="/events">Events</Link>
            <span className="nav-user">{user?.full_name || user?.email} ({user?.role})</span>
            <button onClick={handleLogout} className="btn btn-sm">Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <NavBar />
          <main className="main">
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/gallery/:slug" element={<GalleryPage />} />
              <Route path="/events" element={<ProtectedRoute><Events /></ProtectedRoute>} />
              <Route path="/events/:eventId" element={<ProtectedRoute><EventDetail /></ProtectedRoute>} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main><footer className="footer"><div className="footer-inner"><Logo size={26} variant="light" /><p className="muted">Shoot. Curate. Dazzle. PIN-protected galleries for event teams.</p><p className="muted">Trizen Photos — crafted for the TrizenAI internship challenge.</p></div></footer>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
