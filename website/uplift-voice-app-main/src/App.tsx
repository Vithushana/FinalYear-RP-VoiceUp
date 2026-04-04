import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/DashBoard";
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
import Seen from "./pages/Seen";
import Verified from "./pages/Verified";
import Reposted from "./pages/Reposted";
import OfficerProfile from "./pages/OfficerProfile";
import ProtectedRoute from "./components/ProtectedRoute";
import TextComplaints from "./pages/TextComplaints";
import Compl from "./pages/ComplaintDetails_SA/ComplaintDetails_sa";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Auth />} />
          <Route path="/dashboard" element={<ProtectedRoute><Index /></ProtectedRoute>} />
          <Route path="/issue/:id" element={<ProtectedRoute><IssueDetails /></ProtectedRoute>} />
          <Route path="/inbox" element={<ProtectedRoute><Inbox /></ProtectedRoute>} />
          <Route path="/text-complaint" element={<ProtectedRoute><TextComplaints /></ProtectedRoute>} />
          <Route path="/complaint/:id" element={<ProtectedRoute><Compl /></ProtectedRoute>} />
          <Route path="/seen" element={<ProtectedRoute><Seen /></ProtectedRoute>} />
          <Route path="/verified" element={<ProtectedRoute><Verified /></ProtectedRoute>} />
          <Route path="/pending" element={<ProtectedRoute><PendingIssues /></ProtectedRoute>} />
          <Route path="/archived" element={<ProtectedRoute><Archived /></ProtectedRoute>} />
          <Route path="/on-hold" element={<ProtectedRoute><OnHold /></ProtectedRoute>} />
          <Route path="/in-progress" element={<ProtectedRoute><InProgress /></ProtectedRoute>} />
          <Route path="/completed" element={<ProtectedRoute><Completed /></ProtectedRoute>} />
          <Route path="/closed" element={<ProtectedRoute><Closed /></ProtectedRoute>} />
          <Route path="/reposted" element={<ProtectedRoute><Reposted /></ProtectedRoute>} />
          <Route path="/achievements" element={<ProtectedRoute><Achievements /></ProtectedRoute>} />
          <Route path="/officer-profile" element={<ProtectedRoute><OfficerProfile /></ProtectedRoute>} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;