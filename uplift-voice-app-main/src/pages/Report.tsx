import { ReportForm } from "@/components/report/ReportForm";
import Sidebar from "@/components/layout/Sidebar";
import { Button } from "@/components/ui/button";
import { Bell, User } from "lucide-react";

const Report = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />
      
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">Submit a Reply to a Report</h1>
            <div className="flex items-center gap-3">
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
        </header>

        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <p className="text-lg text-gray-600">
                Help improve your community by reporting road and infrastructure issues
              </p>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <ReportForm />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Report;
