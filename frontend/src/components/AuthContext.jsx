import { createContext, useState, useEffect } from "react";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  // Verifică dacă utilizatorul este logat la încărcarea aplicației
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        const parsedUser = JSON.parse(storedUser);
        // Handle both old format {status, rol, user} and new format {user object}
        const userData = parsedUser.user || parsedUser;
        setUser(userData);
      }
    } catch (error) {
      console.error("Error loading user from localStorage:", error);
      localStorage.removeItem("user"); // Clear corrupted data
    }
  }, []);

  const login = (userData) => {
    try {
      if (!userData || !userData.nume || !userData.rol) {
        console.error("Invalid user data:", userData);
        return;
      }
      setUser(userData);
      localStorage.setItem("user", JSON.stringify(userData));
    } catch (error) {
      console.error("Error saving user to localStorage:", error);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("user");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}