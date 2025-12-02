import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { 
  Home, 
  Inbox, 
  FileText, 
  Upload, 
  Archive, 
  MapPin, 
  BarChart3, 
  CheckCircle2, 
  Clock, 
  XCircle 
} from "lucide-react";

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { icon: Home, label: "Dashboard", path: "/dashboard", active: true },
    { icon: Inbox, label: "Inbox", path: "/inbox" },
    { icon: FileText, label: "Pending Issues", path: "/pending" },
    { icon: Upload, label: "Submit", path: "/submit" },
    { icon: Archive, label: "Archived", path: "/archived" },
    { icon: MapPin, label: "On Hold", path: "/on-hold" },
    { icon: BarChart3, label: "In progress", path: "/in-progress" },
    { icon: CheckCircle2, label: "Completed", path: "/completed" },
    { icon: Clock, label: "Closed", path: "/closed" },
    { icon: XCircle, label: "Achievements", path: "/achievements" },
  ];

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
    </div>
  );
};

export default Sidebar;