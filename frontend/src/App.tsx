import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import MarketplaceHome from "@/pages/MarketplaceHomeV2";
import MarketplaceLotDetail from "@/pages/MarketplaceLotDetail";
import MarketplaceDashboard from "@/pages/MarketplaceDashboardV2";
import MarketplaceRegister from "@/pages/MarketplaceRegisterV2";
import MarketplaceAdmin from "@/pages/MarketplaceAdminV2";
import MarketplaceAdminApprovals from "@/pages/MarketplaceAdminApprovalsV2";
import type { AdminRole, Bidder } from "@/types/auction";

// One <Route> per page in src/pages; BrowserRouter already wraps this in main.tsx.
export default function App() {
  const [bidder, setBidder] = useState<Bidder>(() => {
    const saved = window.localStorage.getItem("lelangoto-bidder");
    return saved ? JSON.parse(saved) as Bidder : { name: "Budi Santoso", type: "Verified Bidder VIP" };
  });
  const [adminRole, setAdminRole] = useState<AdminRole>(() => (window.localStorage.getItem("lelangoto-admin-role") as AdminRole | null) ?? "super_admin");
  const handleBidderChange = (nextBidder: Bidder) => {
    setBidder(nextBidder);
    window.localStorage.setItem("lelangoto-bidder", JSON.stringify(nextBidder));
  };
  const handleAdminRoleChange = (nextRole: AdminRole) => { setAdminRole(nextRole); window.localStorage.setItem("lelangoto-admin-role", nextRole); };
  return (
    <Routes>
      <Route path="/" element={<MarketplaceHome bidder={bidder} onBidderChange={handleBidderChange} />} />
      <Route path="/lots/:lotId" element={<MarketplaceLotDetail bidder={bidder} onBidderChange={handleBidderChange} />} />
      <Route path="/dashboard" element={<MarketplaceDashboard bidder={bidder} onBidderChange={handleBidderChange} />} />
      <Route path="/register" element={<MarketplaceRegister bidder={bidder} onBidderChange={handleBidderChange} />} />
      <Route path="/admin" element={<MarketplaceAdmin bidder={bidder} onBidderChange={handleBidderChange} adminRole={adminRole} onAdminRoleChange={handleAdminRoleChange} />} />
      <Route path="/admin/approvals" element={<MarketplaceAdminApprovals bidder={bidder} onBidderChange={handleBidderChange} adminRole={adminRole} onAdminRoleChange={handleAdminRoleChange} />} />
    </Routes>
  );
}
