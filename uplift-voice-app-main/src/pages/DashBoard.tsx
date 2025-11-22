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
      ]); // Closing parenthesis for setStats array

      // Fetch regular issues
      const issuesData = await ApiService.getIssues(6); // Get 6 issues for the grid
      setIssues(issuesData);

      // Fetch reposted issues
      const repostedData = await ApiService.getRepostedIssues(4); // Get 4 reposted issues
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
              {(() => {
                // Create road issue mock data with only road-related content
                const roadIssues = [
                  {
                    id: '1',
                    _id: '1',
                    status: 'Verified',
                    description: 'Significant crack in sidewalk verified by inspection team, awaiting repair scheduling.',
                    location: 'Business District, 7th Street',
                    time: '2 hours ago',
                    priority: 2,
                    image: '/images/image 13.png'
                  },
                  {
                    id: '2', 
                    _id: '2',
                    status: 'On hold',
                    description: 'Ongoing noise complaint has been resolved through legal channels and case is closed.',
                    location: 'Residential Area, Block 12',
                    time: '2 hours ago',
                    priority: 3,
                    image: '/images/image 13 (1).png'
                  },
                  {
                    id: '3',
                    _id: '3', 
                    status: 'On Hold',
                    description: 'Multiple parking meters not accepting payment. Waiting for parts delivery to complete repairs.',
                    location: 'Downtown Shopping District',
                    time: '2 hours ago',
                    priority: 2,
                    image: '/images/image 13 (2).png'
                  },
                  {
                    id: '4',
                    _id: '4',
                    status: 'In Progress', 
                    description: 'Road surface repair currently underway. Expected completion by end of week.',
                    location: 'Main Street, Block 8',
                    time: '3 hours ago',
                    priority: 1,
                    image: '/images/image 14 (1).png'
                  },
                  {
                    id: '5',
                    _id: '5',
                    status: 'Completed',
                    description: 'Pothole repair has been completed successfully. Road surface restored to safe condition.',
                    location: 'Highway 21, Mile Marker 15',
                    time: '4 hours ago', 
                    priority: 1,
                    image: '/images/image 14 (2).png'
                  },
                  {
                    id: '6',
                    _id: '6',
                    status: 'Seen',
                    description: 'New report of damaged road markings affecting traffic flow during rush hours.',
                    location: 'Central Avenue Intersection',
                    time: '5 hours ago',
                    priority: 2,
                    image: '/images/image 15 (2).png'
                  }
                ];

                return roadIssues.map((issue, index) => (
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
                ));
              })()}
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
              {(() => {
                // Create reposted road issue mock data
                const repostedRoadIssues = [
                  {
                    id: '7',
                    _id: '7',
                    status: 'Verified',
                    description: 'The stop sign at the intersection of Pine and Cedar was knocked down during the storm last week. This intersection is very dangerous without proper signage.',
                    location: 'Pine St & Cedar Ave Intersection',
                    time: '11 days ago',
                    priority: 1,
                    image: '/images/image 16 (1).png'
                  },
                  {
                    id: '8',
                    _id: '8',
                    status: 'Completed',
                    description: 'The traffic light at the main intersection is stuck on red in all directions. This is causing major traffic congestion during rush hours.',
                    location: 'Main St & Broadway Intersection',
                    time: '11 days ago',
                    priority: 1,
                    image: '/images/image 17 (1).png'
                  },
                  {
                    id: '9',
                    _id: '9',
                    status: 'Seen',
                    description: 'The public trash bin near the bus stop has been overflowing for days. It\'s attracting pests and creating an unsanitary condition.',
                    location: 'Bus Stop, Oak Street',
                    time: '21 days ago',
                    priority: 2,
                    image: '/images/Rectangle 25.png'
                  },
                  {
                    id: '10',
                    _id: '10',
                    status: 'Completed',
                    description: 'Multiple deep potholes have formed on this busy road section, causing damage to vehicles and creating safety hazards.',
                    location: 'Main St & Broadway Intersection',
                    time: '11 days ago',
                    priority: 1,
                    image: '/images/Groups (1).png'
                  }
                ];

                return repostedRoadIssues.map((issue, index) => (
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
                ));
              })()}
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
