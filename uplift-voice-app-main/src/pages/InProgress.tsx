import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import Sidebar from '@/components/layout/Sidebar';
import { Bell, Search, User, AlertTriangle, Activity } from 'lucide-react';
import ApiService, { Issue } from '@/services/ApiService';
import StatusProgression from '@/components/StatusProgression';
import { getStatusColor } from '@/utils/statusProgression';
import { getPriorityBorderColor } from '@/utils/priorityColors';

const InProgress: React.FC = () => {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchIssues();
  }, []);

  const fetchIssues = async () => {
    try {
      setLoading(true);
      const data = await ApiService.getIssues(50, 0, 'In Progress');
      setIssues(data);
    } catch (error) {
      console.error('Error fetching in progress issues:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (issueId: string, newStatus: string) => {
    try {
      await ApiService.updateIssueStatus(issueId, newStatus);
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
            <Button variant="ghost" className="p-2">
              <Bell className="w-5 h-5" />
            </Button>
            <Button variant="ghost" className="p-2">
              <User className="w-5 h-5" />
            </Button>
            <span className="bg-yellow-500 text-white px-3 py-1 rounded-full text-sm font-medium">
              Ranjan
            </span>
          </div>
        </div>

        {/* Issues Grid */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {issues.map((issue, index) => {
              const inProgressImages = [
                '/images/image 17 (1).png',
                '/images/Rectangle 25.png',
                '/images/Groups (1).png',
                '/images/image 2 (1).png',
                '/images/image 13 (1).png',
                '/images/image 13 (2).png',
                '/images/image 14 (1).png',
                '/images/image 14 (2).png'
              ];
              return (
              <Card key={issue._id} className={`bg-white border-2 ${getPriorityBorderColor(issue.priority)} hover:shadow-lg transition-shadow h-full`}>
                <CardContent className="p-4 h-full flex flex-col">
                  {/* User Header */}
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center">
                      <AlertTriangle className="w-4 h-4 text-white" />
                    </div>
                    <span className="font-medium text-gray-700">@{issue.userName || 'Albert'}</span>
                  </div>

                  {/* Issue Image */}
                  <div className="mb-3">
                    <img
                      src={issue.userUploadImages?.[0] || inProgressImages[index % inProgressImages.length]}
                      alt={issue.title}
                      className="w-full h-40 object-cover rounded-lg"
                    />
                  </div>

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
                      issueId={issue._id}
                      onStatusUpdate={(newStatus) => handleStatusUpdate(issue._id, newStatus)}
                    />
                  </div>

                  {/* Status Label and Details Button */}
                  <div className="flex items-center justify-end">
                    <Button
                      onClick={() => navigate(`/issue/${issue._id}`)}
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