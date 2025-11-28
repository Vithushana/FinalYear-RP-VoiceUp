const API_BASE_URL = 'http://localhost:5000/api';

export interface Issue {
  _id: string;
  title: string;
  description: string;
  category: string;
  location: string;
  status: string;
  priority: string;
  userName: string;
  userMobile: string;
  userUploadImages: string[];
  matchingPosts: string[];
  dateCreated: string;
  achievement?: {
    governmentOfficialName: string;
    designation: string;
    meetingDate: string;
    issueStatus: string;
    actionTaken: string;
    documentPath?: string;
  };
}

class ApiService {
  static async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }
      
      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Dashboard Statistics
  static async getDashboardStats() {
    const response = await this.request('/stats');
    return response.data;
  }

  // Issues
  static async getIssues(limit = 50, skip = 0, status?: string) {
    const params = new URLSearchParams({
      limit: limit.toString(),
      skip: skip.toString(),
    });
    
    if (status) {
      params.append('status', status);
    }

    const response = await this.request(`/issues?${params}`);
    return response.data;
  }

  static async getRepostedIssues(limit = 50, skip = 0) {
    const params = new URLSearchParams({
      limit: limit.toString(),
      skip: skip.toString(),
    });

    const response = await this.request(`/issues/reposted?${params}`);
    return response.data;
  }

  static async getIssueById(issueId: string) {
    const response = await this.request(`/issues/${issueId}`);
    return response.data;
  }

  static async createIssue(issueData: Omit<Issue, '_id' | 'dateCreated'>) {
    const response = await this.request('/issues', {
      method: 'POST',
      body: JSON.stringify(issueData),
    });
    return response;
  }

  static async updateIssueStatus(issueId: string, status: string) {
    const response = await this.request(`/issues/${issueId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
    return response;
  }

  static async searchIssues(query: string) {
    const params = new URLSearchParams({ q: query });
    const response = await this.request(`/issues/search?${params}`);
    return response.data;
  }

  // Authentication (if needed later)
  static async login(email: string, password: string) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return response;
  }

  static async signup(userData: { email: string; password: string; name?: string }) {
    const response = await this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    return response;
  }

  static async updateAchievement(issueId: string, achievement: Issue['achievement']) {
    const response = await this.request(`/issues/${issueId}/achievement`, {
      method: 'PUT',
      body: JSON.stringify({ achievement }),
    });
    return response.data;
  }
}

export default ApiService;