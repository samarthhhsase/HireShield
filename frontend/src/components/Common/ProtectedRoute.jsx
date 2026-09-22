import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { getStoredToken, getStoredUser } from '../../api/auth';

/**
 * Route guard that ensures only authenticated analysts with valid tokens
 * can access protected intelligence workspaces.
 */
export default function ProtectedRoute({ children }) {
  const location = useLocation();
  const token = getStoredToken();
  const user = getStoredUser();

  const isAuthenticated = Boolean(token || (user && user.isLocalSession));

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children ? children : null;
}
