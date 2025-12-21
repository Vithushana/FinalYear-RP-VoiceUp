import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Sidebar from "@/components/layout/Sidebar";
import { ArrowLeft, Upload, X } from "lucide-react";
import { useState, useEffect, useRef } from "react";
import ApiService from "@/services/ApiService";
import { getInitials } from "@/utils/userUtils";
import { getUserData } from "@/utils/authUtils";

interface Issue {
  _id?: string;
  id?: number;
  title: string;
  description: string;
  location: string;
  category?: string;
  issue_type?: string;
  status: string;
  priority?: string | number;
  dateCreated?: string;
  created_at?: string;
  userName?: string;
  username?: string;
  reporter_name?: string;
  userUploadImages?: string[];
  images?: string[];
  impact?: string;
  severity?: string;
}

const IssueDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [issue, setIssue] = useState<Issue | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [replyMessage, setReplyMessage] = useState('');
  const [replyImages, setReplyImages] = useState<string[]>([]);
  const [submittingReply, setSubmittingReply] = useState(false);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [pendingStatus, setPendingStatus] = useState<string | null>(null);
  const [replies, setReplies] = useState<any[]>([]);
  const [userReposts, setUserReposts] = useState<any[]>([]);

  const statusOrder = ['seen', 'verified', 'hold', 'in_progress', 'completed', 'closed'];
  const statusLabels: Record<string, string> = {
    seen: 'Seen',
    verified: 'Verified',
    hold: 'On Hold',
    in_progress: 'In Progress',
    completed: 'Completed',
    closed: 'Closed'
  };

  useEffect(() => {
    fetchIssueDetails();
    fetchReplies();
    fetchUserReposts();
  }, [id]);

  const formatImageUrl = (image: string) => {
    if (!image) return '';
    // If it's already a base64 image or full URL, return as is
    if (image.startsWith('data:image') || image.startsWith('http')) {
      return image;
    }
    // Otherwise, it's a filename - prepend the backend URL
    return `http://localhost:5000/uploads/${image}`;
  };

  const fetchReplies = async () => {
    if (!id) return;
    try {
      const response = await ApiService.getPostReplies(id);
      const formattedReplies = (response.replies || []).map((reply: any) => ({
        ...reply,
        image: formatImageUrl(reply.image)
      }));
      setReplies(formattedReplies);
    } catch (error) {
      console.error('Error fetching replies:', error);
    }
  };

  const fetchUserReposts = async () => {
    if (!id) return;
    try {
      // Get current officer's info to filter by region (safe access)
      const user = getUserData();
      const officerRegion = user?.officer_region;
      const officerProvince = user?.officer_province;
      const officerDistrict = user?.officer_district;

      const response = await fetch(`http://localhost:5000/api/interactions/comments/${id}`);
      const data = await response.json();
      if (data.success) {
        // Filter for user reposts (is_repost = true and has image)
        let reposts = (data.data.comments || []).filter((comment: any) => 
          comment.is_repost === true && comment.image
        );
        
        // Further filter by officer's region if available
        // (only show reposts from posts in officer's jurisdiction)
        if (officerRegion && officerProvince && officerDistrict) {
          const issueResponse = await ApiService.getIssueById(id);
          const issueData = issueResponse.issue || issueResponse;
          // Only show reposts if this issue is in officer's region
          if (issueData.region === officerRegion && 
              issueData.province === officerProvince && 
              issueData.district === officerDistrict) {
            // Format image URLs
            const formattedReposts = reposts.map((repost: any) => ({
              ...repost,
              image: formatImageUrl(repost.image)
            }));
            setUserReposts(formattedReposts);
          } else {
            setUserReposts([]); // Not in officer's region
          }
        } else {
          // No region info, show all (fallback)
          const formattedReposts = reposts.map((repost: any) => ({
            ...repost,
            image: formatImageUrl(repost.image)
          }));
          setUserReposts(formattedReposts);
        }
      }
    } catch (error) {
      console.error('Error fetching user reposts:', error);
    }
  };

  const fetchIssueDetails = async () => {
    if (!id) return;

    try {
      setLoading(true);
      setError(null);
      const response = await ApiService.getIssueById(id);

      const rawIssue = response.issue || response;
      const mappedIssue: Issue = {
        _id: rawIssue.id || rawIssue._id,
        id: rawIssue.id,
        title: rawIssue.title,
        description: rawIssue.description,
        location: rawIssue.location,
        category: rawIssue.issue_type || rawIssue.type || rawIssue.category,
        status: rawIssue.status,
        priority: rawIssue.priority || 2,
        dateCreated: rawIssue.created_at || rawIssue.dateCreated,
        userName: rawIssue.username || rawIssue.reporter_name || 'Anonymous',
        userUploadImages: (rawIssue.images || []).map((img: string) => formatImageUrl(img)),
        impact: rawIssue.impact || 'High',
        severity: rawIssue.severity || 'Moderate'
      };

      setIssue(mappedIssue);
    } catch (error) {
      console.error('Error fetching issue details:', error);
      setError('Failed to fetch issue details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusClick = (newStatus: string) => {
    setPendingStatus(newStatus);
    setShowConfirmDialog(true);
  };

  const confirmStatusChange = async () => {
    if (!id || !pendingStatus) return;

    try {
      setUpdatingStatus(true);
      const user = getUserData();
      const officerId = user?.id;
      if (!officerId) {
        alert('User data not found. Please log in again.');
        return;
      }
      await ApiService.updateIssueStatus(id, pendingStatus, officerId);
      setShowConfirmDialog(false);
      fetchIssueDetails();
    } catch (error) {
      console.error('Error updating status:', error);
      alert('Failed to update status');
    } finally {
      setUpdatingStatus(false);
      setPendingStatus(null);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    Array.from(files).forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setReplyImages(prev => [...prev, reader.result as string]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (index: number) => {
    setReplyImages(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmitReply = async () => {
    if (!replyMessage.trim() && replyImages.length === 0) {
      alert('Please enter a message or upload at least one image');
      return;
    }
    if (!id) return;

    try {
      setSubmittingReply(true);
      const user = getUserData();
      const officerName = user?.username || 'Officer';

      await ApiService.addOfficerReply(id, officerName, replyMessage, replyImages);
      setReplyMessage('');
      setReplyImages([]);
      alert('Reply submitted successfully!');
      fetchIssueDetails();
      fetchReplies(); // Refresh replies list
      fetchUserReposts(); // Refresh user reposts
    } catch (error) {
      console.error('Error submitting reply:', error);
      alert('Failed to submit reply');
    } finally {
      setSubmittingReply(false);
    }
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

  if (error || !issue) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <Sidebar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-lg text-red-600">{error || 'Issue not found'}</div>
        </div>
      </div>
    );
  }

  const currentStatusIndex = statusOrder.indexOf(issue.status);

  return (
    <div className="min-h-screen bg-gray-100 flex">
      <Sidebar />

      <div className="flex-1 p-8">
        {/* Main Card Container */}
        <div className="max-w-3xl mx-auto">
          <Card className="border-2 border-red-500 rounded-lg shadow-lg bg-white">
            <CardContent className="p-6">
              {/* Header with Back Button and User */}
              <div className="flex items-center justify-between mb-6">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate(-1)}
                  className="flex items-center gap-2 bg-blue-900 text-white hover:bg-blue-800 px-4 py-2 rounded"
                >
                  <ArrowLeft className="h-4 w-4" />
                  Back
                </Button>

                {/* User Profile */}
                <div className="flex items-center gap-2">
                  <div className="w-10 h-10 bg-yellow-400 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-black">{getInitials(issue.userName || 'User')}</span>
                  </div>
                  <span className="font-semibold text-gray-800">@{issue.userName}</span>
                </div>
              </div>

              {/* Main Image */}
              <div className="mb-4">
                {issue.userUploadImages && issue.userUploadImages.length > 0 ? (
                  <img
                    src={issue.userUploadImages[0]}
                    alt="Main issue"
                    className="w-full h-64 object-cover rounded-lg"
                  />
                ) : (
                  <div className="w-full h-64 bg-gray-200 rounded-lg flex items-center justify-center">
                    <span className="text-gray-500">No image available</span>
                  </div>
                )}
              </div>

              {/* Thumbnail Images */}
              {issue.userUploadImages && issue.userUploadImages.length > 1 && (
                <div className="flex gap-2 mb-6">
                  {issue.userUploadImages.slice(1, 5).map((img, index) => (
                    <div key={index} className="flex-shrink-0">
                      <img
                        src={img}
                        alt={`Thumbnail ${index + 1}`}
                        className="w-20 h-16 object-cover rounded border-2 border-gray-300"
                      />
                    </div>
                  ))}
                </div>
              )}

              {/* Details Section */}
              <div className="mb-6">
                <h2 className="text-lg font-bold mb-3 text-gray-900">Details</h2>
                <div className="bg-gray-100 p-4 rounded-lg space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">Description: </span>
                    <span className="text-gray-800">{issue.description || 'Significant crack on main road near town center, causing bumps and potential hazards.'}</span>
                  </div>
                  <ul className="space-y-1 ml-4">
                    <li className="text-gray-800">
                      <span className="font-medium">Location:</span> {issue.location}
                    </li>
                    <li className="text-gray-800">
                      <span className="font-medium">Type:</span> {issue.category || 'Road crack'}
                    </li>
                    <li className="text-gray-800">
                      <span className="font-medium">Posted:</span> {issue.dateCreated ? new Date(issue.dateCreated).toLocaleDateString() : '2025-07-28'}
                    </li>
                    <li className="text-gray-800">
                      <span className="font-medium">Impact:</span> None
                    </li>
                    <li className="text-gray-800">
                      <span className="font-medium">Severity:</span> None
                    </li>
                  </ul>
                </div>
              </div>

              {/* Report / Reply Section */}
              <div className="mb-6 border-t pt-4">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold text-white">△</span>
                  </div>
                  <h3 className="text-base font-bold text-blue-900">Report / Reply</h3>
                </div>

                <div className="space-y-3">
                  {/* Image Previews */}
                  {replyImages.length > 0 && (
                    <div className="flex flex-wrap gap-2 p-2 bg-gray-50 rounded-lg">
                      {replyImages.map((img, index) => (
                        <div key={index} className="relative">
                          <img src={img} alt={`Preview ${index}`} className="w-20 h-20 object-cover rounded border-2 border-gray-300" />
                          <button
                            onClick={() => removeImage(index)}
                            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs hover:bg-red-600 shadow"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Upload Button, Text Input, and Reply Button in One Row */}
                  <div className="flex items-center gap-2">
                    {/* Upload Files Button */}
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/*"
                      multiple
                      className="hidden"
                      onChange={handleImageUpload}
                    />
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold px-4 py-2 rounded flex items-center gap-2 whitespace-nowrap"
                    >
                      <Upload className="w-4 h-4" />
                      Upload Files
                    </button>

                    {/* Text Input */}
                    <input
                      type="text"
                      className="flex-1 px-4 py-2 border border-gray-300 rounded focus:outline-none focus:border-yellow-400 text-gray-900"
                      placeholder="Type your reply.."
                      value={replyMessage}
                      onChange={(e) => setReplyMessage(e.target.value)}
                    />

                    {/* Reply Button */}
                    <button
                      onClick={handleSubmitReply}
                      disabled={submittingReply || (!replyMessage.trim() && replyImages.length === 0)}
                      className="bg-yellow-400 hover:bg-yellow-500 disabled:bg-gray-300 disabled:cursor-not-allowed text-black font-semibold px-6 py-2 rounded whitespace-nowrap"
                    >
                      {submittingReply ? 'Sending...' : 'Reply'}
                    </button>
                  </div>
                </div>
              </div>

              {/* Status Section */}
              <div>
                <h3 className="font-bold mb-4 text-gray-900">Status</h3>

                {/* Status Progression */}
                <div className="flex items-center justify-between mb-4 px-4">
                  {statusOrder.map((status, index) => {
                    const isCompleted = index <= currentStatusIndex;
                    return (
                      <div key={status} className="flex flex-col items-center relative" style={{ flex: 1 }}>
                        <button
                          onClick={() => handleStatusClick(status)}
                          disabled={updatingStatus}
                          className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all z-10 ${isCompleted
                            ? 'bg-green-500 border-green-500'
                            : 'bg-gray-300 border-gray-400 hover:border-yellow-400'
                            } ${updatingStatus ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`}
                        >
                          {isCompleted && (
                            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </button>
                        <span className="text-xs mt-1 text-center text-gray-600 whitespace-nowrap">{statusLabels[status]}</span>

                        {/* Connecting Line */}
                        {index < statusOrder.length - 1 && (
                          <div
                            className={`absolute top-5 h-0.5 ${index < currentStatusIndex ? 'bg-green-500' : 'bg-gray-300'
                              }`}
                            style={{
                              left: '50%',
                              width: 'calc(100% - 20px)',
                              zIndex: 0
                            }}
                          />
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Current Status Display */}
                <div className="text-center text-sm">
                  <span className="text-gray-600">Status: </span>
                  <span className="font-semibold text-gray-900">{statusLabels[issue.status] || issue.status}</span>
                </div>
              </div>

              {/* User Reposts Section */}
              {userReposts.length > 0 && (
                <div className="mt-6">
                  <h3 className="font-bold mb-4 text-gray-900">User Reposts ({userReposts.length})</h3>
                  <div className="space-y-3">
                    {userReposts.map((repost, index) => (
                      <div key={index} className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 bg-orange-500 rounded-full flex items-center justify-center flex-shrink-0">
                            <span className="text-sm font-bold text-white">{getInitials(repost.username || 'User')}</span>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-orange-900">{repost.username}</span>
                              <span className="text-xs bg-orange-500 text-white px-2 py-0.5 rounded">REPOST</span>
                            </div>
                            <p className="text-gray-800 text-sm mb-2">{repost.text}</p>
                            {repost.image && (
                              <img
                                src={repost.image}
                                alt="User repost"
                                className="w-full max-w-md h-48 object-cover rounded-lg border-2 border-orange-300 mt-2"
                              />
                            )}
                            <span className="text-xs text-gray-500 mt-2 block">
                              {new Date(repost.created_at).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Your Replies Section */}
              {replies.length > 0 && (
                <div className="mt-6">
                  <h3 className="font-bold mb-4 text-gray-900">Your Replies ({replies.length})</h3>
                  <div className="space-y-3">
                    {replies.map((reply, index) => (
                      <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                            <span className="text-sm font-bold text-white">{getInitials(reply.officer_name || 'Officer')}</span>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-blue-900">{reply.officer_name}</span>
                              <span className="text-xs bg-blue-500 text-white px-2 py-0.5 rounded">OFFICER</span>
                            </div>
                            <p className="text-gray-800 text-sm mb-2">{reply.message}</p>
                            {reply.image && (
                              <img
                                src={reply.image}
                                alt="Officer reply"
                                className="w-full max-w-md h-48 object-cover rounded-lg border-2 border-blue-300 mt-2"
                              />
                            )}
                            <span className="text-xs text-gray-500 mt-2 block">
                              {new Date(reply.created_at).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Confirmation Dialog */}
      {showConfirmDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
            <h3 className="text-lg font-bold mb-4 text-gray-900">Confirm Status Change</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to change the status to <span className="font-semibold text-gray-900">{pendingStatus && statusLabels[pendingStatus]}</span>?
            </p>
            <div className="flex gap-3">
              <Button
                onClick={() => setShowConfirmDialog(false)}
                variant="outline"
                className="flex-1 border-gray-300"
                disabled={updatingStatus}
              >
                Cancel
              </Button>
              <Button
                onClick={confirmStatusChange}
                className="flex-1 bg-yellow-400 hover:bg-yellow-500 text-black font-semibold"
                disabled={updatingStatus}
              >
                {updatingStatus ? 'Updating...' : 'Confirm'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IssueDetails;