import { Link, useLocation, useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  Home,
  Inbox,
  Text,
  FileText,
  Upload,
  Archive,
  MapPin,
  BarChart3,
  CheckCircle2,
  Clock,
  XCircle,
  LogOut
} from "lucide-react";
import { clearAuthData } from "@/utils/authUtils";

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    { icon: Home, label: "Dashboard", path: "/dashboard", active: true },
    { icon: Inbox, label: "Inbox", path: "/inbox" },
    { icon: Text, label: "Text Complaint", path: "/text-complaint" },
    { icon: FileText, label: "Seen", path: "/seen" },
    { icon: CheckCircle2, label: "Verified", path: "/verified" },
    { icon: MapPin, label: "Hold", path: "/on-hold" },
    { icon: BarChart3, label: "In Progress", path: "/in-progress" },
    { icon: CheckCircle2, label: "Completed", path: "/completed" },
    { icon: Clock, label: "Closed", path: "/closed" },
    { icon: Archive, label: "Reposted", path: "/reposted" },
    { icon: XCircle, label: "Achievements", path: "/achievements" },
  ];

  const handleLogout = () => {
    // Clear all authentication data using safe utility
    clearAuthData();

    console.log("🚪 Logged out successfully");

    // Redirect to login page
    navigate("/");
  };

  return (
    <div className="w-64 bg-[#1e3a8a] text-white min-h-screen flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-blue-600">
        <h1 className="text-xl font-bold">Voice Up</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4">
        {menuItems.map((item, index) => (
          <Link
            key={index}
            to={item.path}
            className={cn(
              "flex items-center gap-3 px-6 py-3 text-sm hover:bg-blue-700 transition-colors",
              (location.pathname === item.path || (item.path === "/dashboard" && location.pathname === "/"))
                ? "bg-yellow-500 text-black font-medium"
                : "text-white"
            )}
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </Link>
        ))}
      </nav>

      {/* Logout Button */}
      <div className="border-t border-blue-600">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-6 py-3 text-sm hover:bg-red-600 transition-colors w-full text-left text-white"
        >
          <LogOut className="h-4 w-4" />
          Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;