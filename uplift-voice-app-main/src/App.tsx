import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/DashBoard";
import Report from "./pages/Report";
import Reports from "./pages/Reports";
import Profile from "./pages/Profile";
import MapView from "./pages/MapView";
import NotFound from "./pages/NotFound";
import Auth from "./pages/Auth";
import IssueDetails from "./pages/IssueDetails";
import Inbox from "./pages/Inbox";
import PendingIssues from "./pages/PendingIssues";
import Archived from "./pages/Archived";
import OnHold from "./pages/OnHold";
import InProgress from "./pages/InProgress";
import Completed from "./pages/Completed";
import Closed from "./pages/Closed";
import Achievements from "./pages/Achievements";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Auth />} />
          <Route path="/dashboard" element={<Index />} />
          <Route path="/issue/:id" element={<IssueDetails />} />
          <Route path="/inbox" element={<Inbox />} />
          <Route path="/pending" element={<PendingIssues />} />
          <Route path="/submit" element={<Report />} />
          <Route path="/archived" element={<Archived />} />
          <Route path="/on-hold" element={<OnHold />} />
          <Route path="/in-progress" element={<InProgress />} />
          <Route path="/completed" element={<Completed />} />
          <Route path="/closed" element={<Closed />} />
          <Route path="/achievements" element={<Achievements />} />
          <Route path="/report" element={<Report />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/map" element={<MapView />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
