// contexts/AuthContext.tsx
'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';
import { User } from '@/lib/types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, full_name?: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // Check if user is logged in on mount
  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    try {
      const token = api.getToken();
      if (token) {
        const currentUser = await api.getCurrentUser();
        setUser(currentUser);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      api.clearToken();
    } finally {
      setLoading(false);
    }
  }

  async function login(email: string, password: string) {
    try {
      await api.login(email, password);
      const currentUser = await api.getCurrentUser();
      setUser(currentUser);
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  async function register(email: string, password: string, full_name?: string) {
    try {
      await api.register(email, password, full_name);
      // Auto-login after registration
      await login(email, password);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  function logout() {
    api.logout();
    setUser(null);
    router.push('/login');
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
