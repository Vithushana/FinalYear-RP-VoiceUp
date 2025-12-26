import Sidebar from "@/components/layout/Sidebar";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Award, CheckCircle2, Clock, TrendingUp, Loader2, Mail, Phone, Calendar, Briefcase, Shield } from "lucide-react";
import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import ApiService from "@/services/ApiService";
import { getUserData } from "@/utils/authUtils";

const OfficerProfile = () => {
    const [stats, setStats] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    // Get user data safely
    const userData = getUserData() || {
        username: "Officer",
        email: "officer@voiceup.gov",
        mobile: "",
        position: "",
        created_at: new Date().toISOString()
    };

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const data = await ApiService.getDashboardStats();
            setStats(data);
        } catch (error) {
            console.error("Error fetching stats:", error);
        } finally {
            setLoading(false);
        }
    };

    // Get initials from name
    const getInitials = (name: string) => {
        if (!name || name === "Officer") return "OF";
        return name
            .split(" ")
            .map((word) => word[0])
            .join("")
            .toUpperCase()
            .slice(0, 2);
    };

    // Format date
    const formatDate = (dateString: string) => {
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        } catch {
            return "Recently";
        }
    };

    if (loading) {
        return (
            <div className="flex min-h-screen bg-gray-50">
                <Sidebar />
                <div className="flex-1 flex items-center justify-center">
                    <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
                </div>
            </div>
        );
    }

    const totalIssues = stats?.total_issues || 0;
    const resolved = stats?.completed || 0;
    const inProgress = stats?.in_progress || 0;
    const verified = stats?.verified || 0;
    const achievements = stats?.achievements || 0;

    return (
        <div className="flex min-h-screen bg-gray-50">
            <Sidebar />

            <div className="flex-1">
                {/* Header */}
                <div className="bg-white border-b px-8 py-4 flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-800">Officer Profile</h1>
                        <p className="text-sm text-gray-500">View and manage your profile</p>
                    </div>
                    <Link to="/dashboard">
                        <Button variant="outline">Back to Dashboard</Button>
                    </Link>
                </div>

                {/* Main Content */}
                <div className="p-8">
                    <div className="max-w-5xl mx-auto space-y-6">
                        {/* Profile Header Card */}
                        <Card>
                            <CardContent className="pt-6">
                                <div className="flex items-center gap-6">
                                    <Avatar className="h-24 w-24 bg-blue-600 text-white text-3xl font-bold">
                                        <AvatarFallback className="bg-blue-600 text-white text-3xl">
                                            {getInitials(userData.username || userData.name)}
                                        </AvatarFallback>
                                    </Avatar>
                                    <div className="flex-1">
                                        <h2 className="text-2xl font-bold mb-3">{userData.username || userData.name || "Officer"}</h2>
                                        <div className="grid grid-cols-2 gap-3">
                                            <div className="flex items-center gap-2 text-gray-600">
                                                <Mail className="h-4 w-4 flex-shrink-0" />
                                                <span className="text-sm">{userData.email}</span>
                                            </div>
                                            {(userData.mobile || userData.phone) && (
                                                <div className="flex items-center gap-2 text-gray-600">
                                                    <Phone className="h-4 w-4 flex-shrink-0" />
                                                    <span className="text-sm">{userData.mobile || userData.phone}</span>
                                                </div>
                                            )}
                                            {userData.position && (
                                                <div className="flex items-center gap-2 text-gray-600">
                                                    <Briefcase className="h-4 w-4 flex-shrink-0" />
                                                    <span className="text-sm">{userData.position}</span>
                                                </div>
                                            )}
                                            <div className="flex items-center gap-2 text-gray-600">
                                                <Calendar className="h-4 w-4 flex-shrink-0" />
                                                <span className="text-sm">Member since {formatDate(userData.created_at)}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="text-center">
                                        <div className="flex items-center gap-2 text-yellow-600 mb-1">
                                            <Award className="h-5 w-5" />
                                            <span className="text-2xl font-bold">{achievements}</span>
                                        </div>
                                        <p className="text-sm text-gray-500">Achievements</p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Stats Grid */}
                        <div className="grid grid-cols-4 gap-4">
                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-center">
                                        <div className="text-3xl font-bold text-gray-800 mb-1">
                                            {totalIssues}
                                        </div>
                                        <p className="text-sm text-gray-500">Total Issues</p>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-center">
                                        <div className="flex items-center justify-center gap-2 mb-1">
                                            <CheckCircle2 className="h-5 w-5 text-green-600" />
                                            <div className="text-3xl font-bold text-green-600">
                                                {resolved}
                                            </div>
                                        </div>
                                        <p className="text-sm text-gray-500">Completed</p>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-center">
                                        <div className="flex items-center justify-center gap-2 mb-1">
                                            <Clock className="h-5 w-5 text-blue-600" />
                                            <div className="text-3xl font-bold text-blue-600">
                                                {inProgress}
                                            </div>
                                        </div>
                                        <p className="text-sm text-gray-500">In Progress</p>
                                    </div>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardContent className="pt-6">
                                    <div className="text-center">
                                        <div className="flex items-center justify-center gap-2 mb-1">
                                            <TrendingUp className="h-5 w-5 text-purple-600" />
                                            <div className="text-3xl font-bold text-purple-600">
                                                {verified}
                                            </div>
                                        </div>
                                        <p className="text-sm text-gray-500">Verified</p>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Performance Summary */}
                        <Card>
                            <CardContent className="pt-6">
                                <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                    <Award className="h-5 w-5 text-yellow-600" />
                                    Performance Summary
                                </h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                                        <p className="text-sm text-gray-600 mb-1">Resolution Rate</p>
                                        <p className="text-2xl font-bold text-green-600">
                                            {totalIssues > 0 ? Math.round((resolved / totalIssues) * 100) : 0}%
                                        </p>
                                    </div>
                                    <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                                        <p className="text-sm text-gray-600 mb-1">Verification Rate</p>
                                        <p className="text-2xl font-bold text-blue-600">
                                            {totalIssues > 0 ? Math.round((verified / totalIssues) * 100) : 0}%
                                        </p>
                                    </div>
                                    <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                                        <p className="text-sm text-gray-600 mb-1">Active Cases</p>
                                        <p className="text-2xl font-bold text-purple-600">{inProgress}</p>
                                    </div>
                                    <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                                        <p className="text-sm text-gray-600 mb-1">Achievements Earned</p>
                                        <p className="text-2xl font-bold text-yellow-600">{achievements}</p>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default OfficerProfile;
