import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import MarketplaceHome from "@/pages/MiningHome";
import MarketplaceLotDetail from "@/pages/MiningLotDetail";
import MarketplaceDashboard from "@/pages/MarketplaceDashboardSecure";
import MarketplaceRegister from "@/pages/MarketplaceRegisterV2";
import MarketplaceAdmin from "@/pages/MarketplaceAdminV2";
import MarketplaceAdminApprovals from "@/pages/MarketplaceAdminApprovalsV3";
import MarketplaceResubmit from "@/pages/MarketplaceResubmit";
import AdminLogin from "@/pages/MITAdminLogin";
import { AdminGuard } from "@/components/admin/AdminGuard";
import type { Bidder } from "@/types/auction";

// One <Route> per page in src/pages; BrowserRouter already wraps this in main.tsx.
export default function App() {
  const [bidder, setBidder] = useState<Bidder>(() => {
    const saved = window.localStorage.getItem("lelangoto-bidder");
    return saved ? JSON.parse(saved) as Bidder : { name: "Budi Santoso", type: "Verified Bidder VIP" };
  });
  const handleBidderChange = (nextBidder: Bidder) => {
    setBidder(nextBidder);
    window.localStorage.setItem("lelangoto-bidder", JSON.stringify(nextBidder));
  };
  return (
    <Routes>
      <Route path="/" element={<MarketplaceHome bidder={bidder} onBidderChange={handleBidderChange} />} />
      <Route path="/lots/:lotId" element={<MarketplaceLotDetail bidder={bidder} onBidderChange={handleBidderChange} />} />
      <Route path="/dashboard" element={<MarketplaceDashboard bidder={bidder} onBidderChange={handleBidderChange} />} />
      <Route path="/register" element={<MarketplaceRegister bidder={bidder} onBidderChange={handleBidderChange} />} />
      <Route path="/resubmit/:buyerId" element={<MarketplaceResubmit bidder={bidder} onBidderChange={handleBidderChange} />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/admin" element={<AdminGuard>{(user) => <MarketplaceAdmin bidder={bidder} onBidderChange={handleBidderChange} adminRole={user.role} onAdminRoleChange={() => undefined} />}</AdminGuard>} />
      <Route path="/admin/approvals" element={<AdminGuard>{(user) => <MarketplaceAdminApprovals bidder={bidder} onBidderChange={handleBidderChange} adminUser={user} />}</AdminGuard>} />
    </Routes>
  );
}
