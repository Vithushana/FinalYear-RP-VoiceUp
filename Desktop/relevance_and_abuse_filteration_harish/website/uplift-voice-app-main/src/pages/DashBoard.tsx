import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Sidebar from "@/components/layout/Sidebar";
import { Search, User } from "lucide-react";
import { NotificationBell } from '@/components/NotificationBell';
import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import ApiService from "@/services/ApiService";
import { getPriorityBorderColor } from "@/utils/priorityColors";
import { getInitials } from "@/utils/userUtils";
import { getUserData } from "@/utils/authUtils";
import type { Issue } from "@/services/ApiService";

const Index = () => {
  const [stats, setStats] = useState([
    { title: "Unseen Issues", value: "0", color: "text-red-600", path: "/inbox" },
    { title: "Seen", value: "0", color: "text-blue-600", path: "/seen" },
    { title: "Verified", value: "0", color: "text-green-600", path: "/verified" },
    { title: "Hold", value: "0", color: "text-yellow-600", path: "/on-hold" },
    { title: "In Progress", value: "0", color: "text-orange-600", path: "/in-progress" },
    { title: "Achievements", value: "0", color: "text-purple-600", path: "/achievements" },
  ]);
  const [issues, setIssues] = useState([]);
  const [repostedIssues, setRepostedIssues] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Helper function to format image URL
      const formatImageUrl = (image: string) => {
        if (!image) return '';
        // If it's already a base64 image or full URL, return as is
        if (image.startsWith('data:image') || image.startsWith('http')) {
          return image;
        }
        // Otherwise, it's a filename - prepend the backend URL
        return `http://localhost:5000/uploads/${image}`;
      };

      // Helper to format images array
      const formatIssueImages = (issue: any) => {
        if (issue.images && Array.isArray(issue.images)) {
          return {
            ...issue,
            images: issue.images.map((img: string) => formatImageUrl(img))
          };
        }
        return issue;
      };

      // Get officer ID safely
      const user = getUserData();
      const officerId = user?.id;

      if (officerId) {
        // Fetch officer-specific stats
        const statsData = await ApiService.getOfficerDashboardStats(officerId);

        if (statsData && statsData.stats) {
          const stats = statsData.stats;
          setStats([
            { title: "Unseen Issues", value: (stats.unseen || 0).toString(), color: "text-red-600", path: "/inbox" },
            { title: "Seen", value: (stats.seen || 0).toString(), color: "text-blue-600", path: "/seen" },
            { title: "Verified", value: (stats.verified || 0).toString(), color: "text-green-600", path: "/verified" },
            { title: "Hold", value: (stats.hold || 0).toString(), color: "text-yellow-600", path: "/on-hold" },
            { title: "In Progress", value: (stats.in_progress || 0).toString(), color: "text-orange-600", path: "/in-progress" },
            { title: "Achievements", value: (stats.achievements || 0).toString(), color: "text-purple-600", path: "/achievements" },
          ]);

          // Set recent posts from officer's assigned issues with formatted images
          if (statsData.recent_posts) {
            setIssues(statsData.recent_posts.map(formatIssueImages));
          }
        }
      }

      // Fetch reposted issues with formatted images
      const repostedData = await ApiService.getRepostedIssues(officerId, 4);
      setRepostedIssues(repostedData ? repostedData.map(formatIssueImages) : []);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setIssues([]);
      setRepostedIssues([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        <header className="bg-white border-b px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-80 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex items-center gap-4">
            <NotificationBell />
            <Link to="/officer-profile">
              <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-bold cursor-pointer hover:bg-blue-700 transition-colors">
                {getInitials(getUserData()?.username || 'User')}
              </span>
            </Link>
          </div>
        </header>

        <main className="flex-1 p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-lg">Loading dashboard data...</div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-3 gap-6 mb-8">
                {stats.map((stat, index) => (
                  <Link key={index} to={stat.path}>
                    <Card className="p-6 text-center hover:shadow-lg transition-shadow cursor-pointer">
                      <CardContent className="p-0">
                        <h3 className="text-sm font-medium text-gray-600 mb-2">{stat.title}</h3>
                        <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>

              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Road Issues For Your Consideration</h2>
                <div className="grid grid-cols-3 gap-6 mb-4">
                  {issues.map((issue) => (
                    <Link key={issue.id || issue._id} to={`/issue/${issue.id || issue._id}`}>
                      <Card className={`overflow-hidden hover:shadow-lg transition-shadow cursor-pointer border-2 ${getPriorityBorderColor(issue.priority)}`}>
                        <CardContent className="p-4">
                          {/* User Profile */}
                          <div className="flex items-center gap-2 mb-3">
                            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                              <span className="text-xs font-bold text-white">{getInitials(issue.username || 'User')}</span>
                            </div>
                            <div className="flex-1">
                              <p className="text-sm font-semibold text-gray-800">{issue.username || 'Anonymous'}</p>
                              <p className="text-xs text-gray-500">{issue.status}</p>
                            </div>
                          </div>

                          <div className="w-full h-32 bg-gray-200 rounded mb-3 overflow-hidden">
                            <img
                              src={issue.images && issue.images.length > 0 ? issue.images[0] : '/images/image 13.png'}
                              alt="Road Issue"
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                e.currentTarget.src = '/images/image 13.png';
                              }}
                            />
                          </div>

                          <p className="text-sm text-gray-600 mb-3 line-clamp-3">{issue.description}</p>
                          <div className="text-xs text-gray-500 mb-2">{issue.location}</div>
                          <div className="text-xs text-gray-500 mb-3">{issue.time}</div>
                          <Button className="w-full bg-yellow-400 hover:bg-yellow-500 text-black text-sm py-1">
                            Details
                          </Button>
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>
                <div className="text-center">
                  <Link to="/inbox">
                    <Button className="bg-yellow-400 hover:bg-yellow-500 text-black px-8">
                      See all road issues
                    </Button>
                  </Link>
                </div>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-4">Reposted Posts For Your Consideration</h2>
                <div className="grid grid-cols-3 gap-6 mb-4">
                  {repostedIssues.map((issue) => (
                    <Link key={issue._id || issue.id} to={`/issue/${issue._id || issue.id}`}>
                      <Card className={`overflow-hidden hover:shadow-lg transition-shadow cursor-pointer border-2 ${getPriorityBorderColor(issue.priority)}`}>
                        <CardContent className="p-4">
                          {/* User Profile */}
                          <div className="flex items-center gap-2 mb-3">
                            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                              <span className="text-xs font-bold text-white">{getInitials(issue.username || 'User')}</span>
                            </div>
                            <div className="flex-1">
                              <p className="text-sm font-semibold text-gray-800">{issue.username || 'Anonymous'}</p>
                              <p className="text-xs text-gray-500">{issue.status}</p>
                            </div>
                          </div>

                          <div className="w-full h-32 bg-gray-200 rounded mb-3 overflow-hidden">
                            <img
                              src={issue.images && issue.images.length > 0 ? issue.images[0] : '/images/image 13.png'}
                              alt="Road Issue"
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                e.currentTarget.src = '/images/image 13.png';
                              }}
                            />
                          </div>

                          <p className="text-sm text-gray-600 mb-3 line-clamp-3">{issue.description}</p>
                          <div className="text-xs text-gray-500 mb-2">{issue.location}</div>
                          <div className="text-xs text-gray-500 mb-3">{issue.time}</div>
                          <Button className="w-full bg-yellow-400 hover:bg-yellow-500 text-black text-sm py-1">
                            Details
                          </Button>
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>
                <div className="text-center">
                  <Link to="/reposted">
                    <Button className="bg-yellow-400 hover:bg-yellow-500 text-black px-8">
                      See all reposted issues
                    </Button>
                  </Link>
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default Index;
