import { create } from "zustand";

// Define the shape of the user object
interface User {
  id: string;
  email: string;
  full_name: string | null;
  profile_type: "admin" | "basic" | "premium" | "enterprise";
  is_active: boolean;
}

// Define the shape of the store's state
interface AuthState {
  accessToken: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (userData: User) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null, // This is no longer used on the client, but kept for structure
  user: null,
  isAuthenticated: false,

  login: (userData: User) =>
    set({
      user: userData,
      isAuthenticated: true,
    }),

  logout: () =>
    set({
      user: null,
      isAuthenticated: false,
    }),
}));