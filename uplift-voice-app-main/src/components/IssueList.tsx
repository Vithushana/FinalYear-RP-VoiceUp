import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import Sidebar from '@/components/layout/Sidebar';
import { Bell, Search, User } from 'lucide-react';
import { Link } from 'react-router-dom';
import ApiService, { Issue } from '@/services/ApiService';

interface IssueListProps {
  title: string;
  status?: string;
  showStats?: boolean;
}

const IssueList: React.FC<IssueListProps> = ({ title, status, showStats = false }) => {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [stats, setStats] = useState({
    pending_issues: 0,
    reported_issues: 0,
    verified: 0,
    on_hold: 0,
    in_progress: 0,
    achievements: 0,
  });
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      if (showStats) {
        const statsData = await ApiService.getDashboardStats();
        setStats(statsData);
      }

      let issuesData;
      if (status === 'inbox') {
        // Inbox: unseen and seen issues (not verified)
        issuesData = await ApiService.getIssues(50, 0, 'Seen');
      } else if (status === 'pending') {
        // Pending: verified but not yet processed
        issuesData = await ApiService.getIssues(50, 0, 'Verified');
      } else if (status) {
        // Specific status
        issuesData = await ApiService.getIssues(50, 0, status);
      } else {
        // All issues
        issuesData = await ApiService.getIssues(50);
      }
      
      setIssues(issuesData);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  }, [status, showStats]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <Sidebar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-lg">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold">{title}</h1>
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search issues..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <Button variant="ghost" size="icon">
                <Bell className="h-5 w-5" />
              </Button>
              <Button variant="ghost" className="flex items-center gap-2">
                <User className="h-4 w-4" />
                Owner
              </Button>
            </div>
          </div>
        </header>

        <main className="flex-1 p-6">
          {showStats && (
            <div className="grid grid-cols-3 gap-6 mb-8">
              <Card className="p-6 text-center">
                <CardContent className="p-0">
                  <h3 className="text-sm font-medium text-gray-600 mb-2">Pending Issues</h3>
                  <div className="text-3xl font-bold text-blue-600">{stats.pending_issues}</div>
                </CardContent>
              </Card>
              <Card className="p-6 text-center">
                <CardContent className="p-0">
                  <h3 className="text-sm font-medium text-gray-600 mb-2">Reported Issues</h3>
                  <div className="text-3xl font-bold text-blue-600">{stats.reported_issues}</div>
                </CardContent>
              </Card>
              <Card className="p-6 text-center">
                <CardContent className="p-0">
                  <h3 className="text-sm font-medium text-gray-600 mb-2">Verified</h3>
                  <div className="text-3xl font-bold text-green-600">{stats.verified}</div>
                </CardContent>
              </Card>
            </div>
          )}

          {issues.length === 0 ? (
            <div className="text-center text-gray-500 mt-12">
              <p>No issues found for this status</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {issues.map((issue: Issue) => (
                <Link key={issue._id} to={`/issue/${issue._id}`}>
                  <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center">
                          <span className="text-xs font-bold">!</span>
                        </div>
                        <span className="text-sm font-medium text-gray-600">{issue.status}</span>
                      </div>
                      
                      {issue.userUploadImages?.length > 0 ? (
                        <div className="w-full h-32 bg-gray-200 rounded mb-3 flex items-center justify-center">
                          <img 
                            src={issue.userUploadImages[0]} 
                            alt="Issue"
                            className="w-full h-full object-cover rounded"
                            onError={(e) => {
                              e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxyZWN0IHg9IjEyNSIgeT0iODUiIHdpZHRoPSI1MCIgaGVpZ2h0PSIzMCIgZmlsbD0iIzlDQTNBRiIvPgo8L3N2Zz4K';
                            }}
                          />
                        </div>
                      ) : (
                        <div className="w-full h-32 bg-gray-200 rounded mb-3 flex items-center justify-center text-gray-500">
                          <span className="text-lg font-medium">{issue.title}</span>
                        </div>
                      )}
                      
                      <p className="text-sm text-gray-600 mb-3 line-clamp-3">{issue.description}</p>
                      <div className="text-xs text-gray-500 mb-2">{issue.location}</div>
                      <div className="text-xs text-gray-500 mb-3">{new Date(issue.dateCreated).toLocaleDateString()}</div>
                      <Button className="w-full bg-yellow-400 hover:bg-yellow-500 text-black text-sm py-1">
                        Details
                      </Button>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default IssueList;