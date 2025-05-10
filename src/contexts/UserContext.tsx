import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: string;
  // Add more user properties as needed in the future
}

interface UserContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  isLoading: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load user from localStorage on mount
    const storedUser = localStorage.getItem('aphrodite_user');
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
      } catch (e) {
        console.error('Failed to parse stored user:', e);
        localStorage.removeItem('aphrodite_user');
      }
    } else {
      // For now, set a default user with ID '1' if no user is stored
      // This maintains backward compatibility
      const defaultUser = { id: '1' };
      setUser(defaultUser);
      localStorage.setItem('aphrodite_user', JSON.stringify(defaultUser));
    }
    setIsLoading(false);
  }, []);

  const handleSetUser = (newUser: User | null) => {
    setUser(newUser);
    if (newUser) {
      localStorage.setItem('aphrodite_user', JSON.stringify(newUser));
    } else {
      localStorage.removeItem('aphrodite_user');
    }
  };

  return (
    <UserContext.Provider value={{ user, setUser: handleSetUser, isLoading }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
