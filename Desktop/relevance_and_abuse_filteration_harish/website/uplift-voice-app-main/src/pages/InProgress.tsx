import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import Sidebar from '@/components/layout/Sidebar';
import { Search, User, AlertTriangle, Activity } from 'lucide-react';
import { NotificationBell } from '@/components/NotificationBell';
import ApiService, { Issue } from '@/services/ApiService';
import StatusProgression from '@/components/StatusProgression';
import { getStatusColor } from '@/utils/statusProgression';
import { getPriorityBorderColor } from '@/utils/priorityColors';
import { getInitials } from '@/utils/userUtils';
import { getUserData } from '@/utils/authUtils';

const InProgress: React.FC = () => {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchIssues();
  }, []);

  const formatImageUrl = (image: string) => {
    if (!image) return '';
    if (image.startsWith('data:image') || image.startsWith('http')) {
      return image;
    }
    return `http://localhost:5000/uploads/${image}`;
  };

  const fetchIssues = async () => {
    try {
      setLoading(true);
      const user = getUserData();
      const officerId = user?.id;

      if (officerId) {
        const data = await ApiService.getOfficerIssues(officerId, 'in_progress', 50);
        const formattedIssues = (data.posts || []).map((issue: any) => ({
          ...issue,
          images: (issue.images || []).map((img: string) => formatImageUrl(img))
        }));
        setIssues(formattedIssues);
      }
    } catch (error) {
      console.error('Error fetching in progress issues:', error);
      setIssues([]);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (issueId: string, newStatus: string) => {
    try {
      const user = getUserData();
      const officerId = user?.id;
      await ApiService.updateIssueStatus(issueId, newStatus, officerId);
      // Refresh the issues list after status update
      fetchIssues();
    } catch (error) {
      console.error('Error updating issue status:', error);
    }
  };

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

      <div className="flex-1">
        {/* Header */}
        <div className="bg-white border-b p-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-800">In Progress</h1>

          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <NotificationBell />
            <Link to="/officer-profile">
              <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-bold cursor-pointer hover:bg-blue-700 transition-colors">
                {getInitials(getUserData()?.username || 'User')}
              </span>
            </Link>
          </div>
        </div>

        {/* Issues Grid */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {issues.map((issue) => {
              return (
                <Card key={issue.id || issue._id} className={`bg-white border-2 ${getPriorityBorderColor(issue.priority)} hover:shadow-lg transition-shadow h-full`}>
                  <CardContent className="p-4 h-full flex flex-col">
                    {/* User Profile */}
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                        <span className="text-xs font-bold text-white">{(issue.username || issue.reporter_name || 'User').substring(0, 2).toUpperCase()}</span>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-semibold text-gray-800">{issue.username || issue.reporter_name || 'Anonymous'}</p>
                        <p className="text-xs text-gray-500">{issue.status}</p>
                      </div>
                    </div>

                    {/* Issue Image */}
                    {issue.images && issue.images.length > 0 && (
                      <div className="mb-3">
                        <img
                          src={issue.images[0]}
                          alt={issue.title}
                          className="w-full h-40 object-cover rounded-lg"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                          }}
                        />
                      </div>
                    )}

                    {/* Issue Description */}
                    <div className="mb-4 flex-grow">
                      <p className="text-sm text-gray-600 mb-2 line-clamp-3">
                        {issue.description}
                      </p>
                      <div className="text-xs text-gray-500 space-y-1">
                        <div><span className="font-medium">Type:</span> {issue.category}</div>
                        <div><span className="font-medium">Location:</span> {issue.location}</div>
                        <div><span className="font-medium">Posted:</span> {new Date(issue.dateCreated).toLocaleDateString()}</div>
                      </div>
                    </div>

                    {/* Status Progression with Next Button */}
                    <div className="mb-3 mt-auto">
                      <StatusProgression
                        currentStatus={issue.status}
                        issueId={issue.id || issue._id}
                        onStatusUpdate={(newStatus) => handleStatusUpdate(issue.id || issue._id, newStatus)}
                      />
                    </div>

                    {/* Status Label and Details Button */}
                    <div className="flex items-center justify-end">
                      <Button
                        onClick={() => navigate(`/issue/${issue.id || issue._id}`)}
                        className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-1 text-sm rounded-md"
                      >
                        details
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {issues.length === 0 && (
            <div className="text-center py-12">
              <div className="text-gray-500 text-lg">No issues in progress found</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InProgress;