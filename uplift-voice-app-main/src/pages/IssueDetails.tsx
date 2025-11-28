import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Sidebar from "@/components/layout/Sidebar";
import { ArrowLeft, Upload, AlertTriangle } from "lucide-react";
import { useState, useEffect } from "react";
import ApiService, { Issue } from "@/services/ApiService";
import StatusProgression from "@/components/StatusProgression";
import { getPriorityBorderColor } from "@/utils/priorityColors";

const IssueDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [issueData, setIssueData] = useState<Issue | null>(null);
  const [matchingIssues, setMatchingIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [replyText, setReplyText] = useState("");

  const handleStatusUpdate = async (newStatus: string) => {
    if (!id || !issueData) return;
    
    try {
      await ApiService.updateIssueStatus(id, newStatus);
      // Update the local issue data
      setIssueData({...issueData, status: newStatus});
    } catch (error) {
      console.error('Error updating issue status:', error);
    }
  };

  useEffect(() => {
    const fetchIssueDetails = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        setError(null);
        const response = await ApiService.getIssueById(id);
        console.log('API Response:', response);
        
        // Handle different response structures
        const issue = response.issue || response;
        const matching = response.matching_issues || [];
        
        setIssueData(issue);
        setMatchingIssues(matching);
      } catch (error) {
        console.error('Error fetching issue details:', error);
        setError('Failed to fetch issue details');
        
        // Create mock data for testing
        const mockIssue = {
          _id: id,
          title: 'Sample Road Issue',
          description: 'Significant road crack near town center, causing traffic hazards and potential damage to vehicles.',
          location: '14, Colombo 05',
          category: 'Road crack',
          status: 'Seen',
          priority: 1,
          dateCreated: new Date().toISOString(),
          userName: 'Albert',
          userUploadImages: [
            '/images/image 2.png',
            '/images/image 7.png',
            '/images/image 10.png',
            '/images/image 11.png'
          ],
          impact: 'High'
        };
        setIssueData(mockIssue);
      } finally {
        setLoading(false);
      }
    };

    fetchIssueDetails();
  }, [id]);

  const getStatusSteps = (currentStatus: string) => {
    const allSteps = ["Seen", "Verified", "On hold", "In Progress", "Completed", "Closed"];
    const currentIndex = allSteps.indexOf(currentStatus);
    
    return allSteps.map((step, index) => ({
      label: step,
      active: step === currentStatus,
      completed: index <= currentIndex && currentStatus !== "Seen"
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <Sidebar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-lg">Loading issue details...</div>
        </div>
      </div>
    );
  }

  if (!issueData) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <Sidebar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="text-lg text-red-600 mb-4">Issue not found</div>
            <Button onClick={() => navigate('/dashboard')} className="bg-yellow-400 hover:bg-yellow-500 text-black">
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const statusSteps = getStatusSteps(issueData.status);

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />
      
      <div className="flex-1 p-6">
        <div className="max-w-4xl mx-auto">
          <div className={`bg-white rounded-lg border-2 ${getPriorityBorderColor(issueData.priority)} p-6`}>
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <Button
                variant="default"
                onClick={() => navigate('/dashboard')}
                className="bg-blue-800 hover:bg-blue-900 text-white px-4 py-2 rounded"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center">
                  <span className="text-sm font-bold">A</span>
                </div>
                <span className="font-medium">@{issueData.userName || 'Anonymous'}</span>
              </div>
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Left Column - Images */}
              <div>
                {/* Main Image */}
                <div className="mb-4">
                  {(() => {
                    // Use the same fallback image arrays as Dashboard
                    const fallbackImages = [
                      '/images/image 13.png',
                      '/images/image 13 (1).png',
                      '/images/image 13 (2).png',
                      '/images/image 14 (1).png',
                      '/images/image 14 (2).png',
                      '/images/image 15 (2).png',
                      '/images/image 16 (1).png',
                      '/images/image 17 (1).png',
                      '/images/Rectangle 25.png'
                    ];
                    const repostedFallbackImages = [
                      '/images/image 14 (3).png',
                      '/images/image 15 (1).png',
                      '/images/image 17.png',
                      '/images/image 2 (1).png',
                      '/images/Groups (1).png',
                      '/images/image 12.png'
                    ];
                    
                    // Create a consistent index based on issue ID
                    const issueIndex = id ? parseInt(id.slice(-1)) || 0 : 0;
                    const mainImage = issueData.userUploadImages?.[0] || 
                                     (issueData.status === 'Completed' ? 
                                      repostedFallbackImages[issueIndex % repostedFallbackImages.length] : 
                                      fallbackImages[issueIndex % fallbackImages.length]);
                    
                    return (
                      <img
                        src={mainImage}
                        alt="Main issue"
                        className="w-full h-64 object-cover rounded-lg"
                        onError={(e) => {
                          e.currentTarget.src = fallbackImages[0];
                        }}
                      />
                    );
                  })()}
                </div>
                
                {/* Thumbnail Images */}
                <div className="flex gap-2 overflow-x-auto">
                  {[1, 2, 3, 4].map((num, index) => {
                    const fallbackThumbs = [
                      '/images/image 13 (1).png',
                      '/images/image 14 (1).png',
                      '/images/image 15 (2).png',
                      '/images/image 16 (1).png'
                    ];
                    const img = issueData.userUploadImages?.[num] || fallbackThumbs[index];
                    return (
                      <div key={index} className="flex-shrink-0">
                        <img
                          src={img}
                          alt={`Thumbnail ${index + 1}`}
                          className="w-16 h-12 object-cover rounded cursor-pointer border border-gray-200"
                          onError={(e) => {
                            e.currentTarget.src = fallbackThumbs[index];
                          }}
                        />
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Right Column - Details */}
              <div>
                <h2 className="text-xl font-bold mb-4 text-blue-600">Details</h2>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-700 mb-4">
                    <span className="font-medium text-gray-900">Description:</span> {issueData.description || 'No description available'}
                  </p>
                  
                  <div className="space-y-3 text-sm">
                    <div className="flex">
                      <span className="font-medium text-gray-900 w-20">Location:</span>
                      <span className="text-gray-700">{issueData.location || 'Location not specified'}</span>
                    </div>
                    <div className="flex">
                      <span className="font-medium text-gray-900 w-20">Type:</span>
                      <span className="text-gray-700">{issueData.category || 'Road crack'}</span>
                    </div>
                    <div className="flex">
                      <span className="font-medium text-gray-900 w-20">Posted:</span>
                      <span className="text-gray-700">{issueData.dateCreated ? new Date(issueData.dateCreated).toLocaleDateString() : '2025-07-28'}</span>
                    </div>
                    <div className="flex">
                      <span className="font-medium text-gray-900 w-20">Impact:</span>
                      <span className={`${
                        issueData.impact === 'High' ? 'text-red-600' :
                        issueData.impact === 'Medium' ? 'text-yellow-600' : 'text-green-600'
                      }`}>
                        {issueData.impact || 'High'}
                      </span>
                    </div>
                    <div className="flex">
                      <span className="font-medium text-gray-900 w-20">Severity:</span>
                      <span className={`${
                        issueData.priority === 1 ? 'text-red-600' :
                        issueData.priority === 2 ? 'text-yellow-600' : 'text-green-600'
                      }`}>
                        {issueData.priority === 1 ? 'Critical' : issueData.priority === 2 ? 'Moderate' : 'Low'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Matching Posts */}
            <div className="mt-8">
              <h3 className="text-lg font-semibold mb-4">
                {issueData.matching_posts_count || matchingIssues.length} matching posts
              </h3>
              <div className="flex gap-3 overflow-x-auto pb-2">
                {matchingIssues.slice(0, 5).map((issue: Issue, index: number) => (
                  <div
                    key={issue.id || index}
                    className="cursor-pointer flex-shrink-0"
                    onClick={() => navigate(`/issue/${issue.id}`)}
                  >
                    <img
                      src={issue.image || '/images/941910_RS_290_290RS070691_02455_RAW_jpg.rf.610e22101c63de4e33963d619a30e220.jpg'}
                      alt={`Matching post ${index + 1}`}
                      className="w-24 h-20 object-cover rounded"
                      onError={(e) => {
                        e.currentTarget.src = 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=96&h=80&fit=crop';
                      }}
                    />
                  </div>
                ))}
                {matchingIssues.length > 5 && (
                  <div className="w-24 h-20 bg-gray-100 rounded flex items-center justify-center cursor-pointer flex-shrink-0">
                    <span className="text-blue-600 text-xs">See all</span>
                  </div>
                )}
              </div>
            </div>

            {/* Report Section */}
            <div className="mt-6 p-4 bg-yellow-50 rounded border-l-4 border-yellow-400">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
                <span className="font-semibold text-yellow-800">Report</span>
              </div>
            </div>

            {/* Reply Section */}
            <div className="mt-6 flex gap-3">
              <Button className="bg-yellow-400 hover:bg-yellow-500 text-black px-6">
                <Upload className="h-4 w-4 mr-2" />
                Upload Files
              </Button>
              <div className="flex-1 flex gap-2">
                <input
                  type="text"
                  placeholder="Type your reply..."
                  value={replyText}
                  onChange={(e) => setReplyText(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />
                <Button className="bg-yellow-400 hover:bg-yellow-500 text-black px-6">
                  Reply
                </Button>
              </div>
            </div>

            {/* Status Section */}
            <div className="mt-8 bg-gray-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-6 text-gray-800">Status</h3>
              <div className="flex justify-center">
                <StatusProgression
                  currentStatus={issueData.status || 'Seen'}
                  issueId={issueData._id || id || ''}
                  onStatusUpdate={handleStatusUpdate}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IssueDetails;