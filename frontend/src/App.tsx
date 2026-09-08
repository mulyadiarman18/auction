import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import LotDetail from "@/pages/LotDetail";
import Dashboard from "@/pages/Dashboard";
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
      <Route path="/" element={<Home bidder={bidder} onBidderChange={handleBidderChange} />} />
      <Route path="/lots/:lotId" element={<LotDetail bidder={bidder} onBidderChange={handleBidderChange} />} />
      <Route path="/dashboard" element={<Dashboard bidder={bidder} onBidderChange={handleBidderChange} />} />
    </Routes>
  );
}
