import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (token) {
        localStorage.setItem('token', token);
        // Decode token or fetch user profile? 
        // For now just assume auth if token exists. 
        // Ideally we fetch /api/v1/accounts/me to get user info
        fetchUser();
    } else {
        localStorage.removeItem('token');
        setUser(null);
    }
  }, [token]);

  const fetchUser = async () => {
      try {
          const response = await fetch('http://localhost:8000/api/v1/accounts/me', {
              headers: { 'Authorization': `Bearer ${token}` }
          });
          if (response.ok) {
              const data = await response.json();
              setUser(data);
          } else {
              // Token invalid
              logout();
          }
      } catch (e) {
          console.error("Failed to fetch user", e);
      }
  };

  const login = (newToken) => {
    setToken(newToken);
  };

  const logout = () => {
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
