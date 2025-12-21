const API_BASE_URL = 'http://localhost:5000/api';

export interface Issue {
  _id?: string;
  id?: string;
  title: string;
  description: string;
  category: string;
  location: string;
  latitude?: number;
  longitude?: number;
  province?: string;
  district?: string;
  status: string;
  priority: number | string;
  userName: string;
  userMobile?: string;
  userUploadImages: string[];
  matchingPosts?: string[];
  dateCreated: string;
  image?: string;
  impact?: string;
  severity?: string;
  matching_posts_count?: number;
  assigned_officer_id?: number;
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
        throw new Error(data.error || data.message || `HTTP error! status: ${response.status}`);
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

  // Officer Dashboard Statistics
  static async getOfficerDashboardStats(officerId: number) {
    const response = await this.request(`/posts/dashboard/stats/${officerId}`);
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

  // Officer Issues
  static async getOfficerIssues(officerId: number, status?: string, limit = 50) {
    let endpoint = `/posts/officer/${officerId}?limit=${limit}`;
    if (status) {
      endpoint += `&status=${status}`;
    }
    const response = await this.request(endpoint);
    return response.data;
  }

  static async getRepostedIssues(officerId?: number, limit = 50, skip = 0) {
    // ✅ FIXED: Use correct endpoint and return posts array
    if (!officerId) {
      return [];
    }

    const response = await this.request(`/interactions/reposted-posts/${officerId}`);
    return response.data.posts || [];
  }

  static async getIssueById(issueId: string) {
    const response = await this.request(`/posts/${issueId}`);
    return response.data;
  }

  static async createIssue(issueData: Omit<Issue, '_id' | 'dateCreated'>) {
    const response = await this.request('/issues', {
      method: 'POST',
      body: JSON.stringify(issueData),
    });
    return response;
  }

  static async updateIssueStatus(issueId: string, status: string, officerId?: number) {
    const payload: any = { status };

    // Include officer_id if provided for cross-officer notifications
    if (officerId) {
      payload.officer_id = officerId;
    }

    const response = await this.request(`/posts/${issueId}/status`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
    return response;
  }

  static async addOfficerReply(issueId: string, officerName: string, message: string, images?: string[]) {
    const response = await this.request(`/posts/${issueId}/reply`, {
      method: 'POST',
      body: JSON.stringify({
        officer_name: officerName,
        message,
        images: images || []
      }),
    });
    return response;
  }

  static async getPostReplies(issueId: string) {
    const response = await this.request(`/posts/${issueId}/replies`);
    return response.data;
  }

  static async getRepostedPosts(officerId: number) {
    const response = await this.request(`/interactions/reposted-posts/${officerId}`);
    return response.data;
  }

  // Achievements
  static async getAchievements() {
    const response = await this.request('/achievements');
    return response.data;
  }

  static async createAchievement(achievementData: any) {
    const response = await this.request('/achievements', {
      method: 'POST',
      body: JSON.stringify(achievementData),
    });
    return response;
  }

  static async updateAchievement(id: string, achievementData: any) {
    const response = await this.request(`/achievements/${id}`, {
      method: 'PUT',
      body: JSON.stringify(achievementData),
    });
    return response;
  }
}

export default ApiService;