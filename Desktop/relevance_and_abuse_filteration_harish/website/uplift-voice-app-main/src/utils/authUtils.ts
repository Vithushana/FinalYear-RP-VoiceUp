/**
 * Utility functions for authentication and user data management
 */

export interface UserData {
  id?: number;
  username?: string;
  email?: string;
  mobile?: string;
  phone?: string;
  name?: string;
  position?: string;
  officer_region?: string;
  officer_province?: string;
  officer_district?: string;
  officer_title?: string;
  created_at?: string;
  is_officer?: boolean;
}

/**
 * Safely get user data from localStorage with error handling
 * @returns UserData object or null if not available
 */
export function getUserData(): UserData | null {
  try {
    const storedUser = localStorage.getItem('user');
    if (!storedUser) {
      return null;
    }
    const parsed = JSON.parse(storedUser);
    // Validate that it's an object
    if (typeof parsed !== 'object' || parsed === null) {
      console.error('Invalid user data format in localStorage');
      return null;
    }
    return parsed as UserData;
  } catch (error) {
    console.error('Error parsing user data from localStorage:', error);
    return null;
  }
}

/**
 * Safely get auth token from localStorage
 * @returns token string or null if not available
 */
export function getAuthToken(): string | null {
  try {
    return localStorage.getItem('auth_token');
  } catch (error) {
    console.error('Error accessing auth_token from localStorage:', error);
    return null;
  }
}

/**
 * Get officer ID from user data (safely)
 * @returns officer ID or null
 */
export function getOfficerId(): number | null {
  const userData = getUserData();
  return userData?.id ?? null;
}

/**
 * Check if current user is an officer
 * @returns boolean
 */
export function isOfficer(): boolean {
  const userData = getUserData();
  return userData?.is_officer === true;
}

/**
 * Get user's display name (username or name)
 * @returns display name or 'User'
 */
export function getUserDisplayName(): string {
  const userData = getUserData();
  return userData?.username || userData?.name || 'User';
}

/**
 * Clear all auth data from localStorage
 */
export function clearAuthData(): void {
  try {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
  } catch (error) {
    console.error('Error clearing auth data:', error);
  }
}

/**
 * Save user data to localStorage safely
 * @param userData - User data object to save
 */
export function saveUserData(userData: UserData): void {
  try {
    localStorage.setItem('user', JSON.stringify(userData));
  } catch (error) {
    console.error('Error saving user data to localStorage:', error);
  }
}

/**
 * Save auth token to localStorage safely
 * @param token - Auth token string
 */
export function saveAuthToken(token: string): void {
  try {
    localStorage.setItem('auth_token', token);
  } catch (error) {
    console.error('Error saving auth token to localStorage:', error);
  }
}
