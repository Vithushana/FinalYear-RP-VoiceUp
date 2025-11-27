import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Sidebar from "@/components/layout/Sidebar";
import { Bell, Search, User } from "lucide-react";
import { Link } from "react-router-dom";
import { useState, useEffect } from "react";
import ApiService from "@/services/ApiService";
import { getPriorityBorderColor } from "@/utils/priorityColors";

const Index = () => {
  const [stats, setStats] = useState([
    { title: "Pending Issues", value: "0", color: "text-blue-600" },
    { title: "Reported Issues", value: "0", color: "text-blue-600" },
    { title: "Verified", value: "0", color: "text-green-600" },
    { title: "On hold", value: "0", color: "text-yellow-600" },
    { title: "In Progress", value: "0", color: "text-orange-600" },
    { title: "Achievements", value: "0", color: "text-purple-600" },
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
      
      // Fetch stats
      const statsData = await ApiService.getDashboardStats();
      setStats([
        { title: "Pending Issues", value: statsData.pending_issues.toString(), color: "text-blue-600" },
        { title: "Reported Issues", value: statsData.reported_issues.toString(), color: "text-blue-600" },
        { title: "Verified", value: statsData.verified.toString(), color: "text-green-600" },
        { title: "On hold", value: statsData.on_hold.toString(), color: "text-yellow-600" },
        { title: "In Progress", value: statsData.in_progress.toString(), color: "text-orange-600" },
        { title: "Achievements", value: statsData.achievements.toString(), color: "text-purple-600" },
      ]);

      // Fetch regular issues
      const issuesData = await ApiService.getIssues(6);
      setIssues(issuesData);

      // Fetch reposted issues
      const repostedData = await ApiService.getRepostedIssues(4);
      setRepostedIssues(repostedData);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
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
            <Button variant="ghost" size="sm">
              <Bell className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm">
              <User className="h-4 w-4" />
              Owner
            </Button>
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
                  <Card key={index} className="p-6 text-center">
                    <CardContent className="p-0">
                      <h3 className="text-sm font-medium text-gray-600 mb-2">{stat.title}</h3>
                      <div className={`text-3xl font-bold ${stat.color}`}>{stat.value}</div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <div className="mb-8">
                <h2 className="text-xl font-semibold mb-4">Road Issues For Your Consideration</h2>
                <div className="grid grid-cols-3 gap-6 mb-4">
                  {issues.map((issue) => (
                    <Link key={issue._id} to={`/issue/${issue._id}`}>
                      <Card className={`overflow-hidden hover:shadow-lg transition-shadow cursor-pointer border-2 ${getPriorityBorderColor(issue.priority)}`}>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-2 mb-3">
                            <div className="w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center">
                              <span className="text-xs font-bold">!</span>
                            </div>
                            <span className="text-sm font-medium text-gray-600">{issue.status}</span>
                          </div>
                          
                          <div className="w-full h-32 bg-gray-200 rounded mb-3 overflow-hidden">
                            <img 
                              src={issue.image}
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
                  <Button className="bg-yellow-400 hover:bg-yellow-500 text-black px-8">
                    See all road issues
                  </Button>
                </div>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-4">Reposted post For Your Consideration,</h2>
                <div className="grid grid-cols-3 gap-6 mb-4">
                  {repostedIssues.map((issue) => (
                    <Link key={issue._id} to={`/issue/${issue._id}`}>
                      <Card className={`overflow-hidden hover:shadow-lg transition-shadow cursor-pointer border-2 ${getPriorityBorderColor(issue.priority)}`}>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-2 mb-3">
                            <div className="w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center">
                              <span className="text-xs font-bold">!</span>
                            </div>
                            <span className="text-sm font-medium text-gray-600">{issue.status}</span>
                          </div>
                          
                          <div className="w-full h-32 bg-gray-200 rounded mb-3 overflow-hidden">
                            <img 
                              src={issue.image}
                              alt="Road Issue"
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                e.currentTarget.src = '/images/image 17.png';
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
                  <Button className="bg-yellow-400 hover:bg-yellow-500 text-black px-8">
                    See all reposted issues
                  </Button>
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
