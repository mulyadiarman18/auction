import { useQuery } from "@tanstack/react-query";
import { RefreshCw } from "lucide-react";
import { Link } from "react-router-dom";
import MarketplaceDashboardV2 from "@/pages/MarketplaceDashboardV2";
import { apiGet } from "@/lib/api";
import type { Bidder, BuyerStatusResponse } from "@/types/auction";

interface MarketplaceDashboardSecureProps { bidder: Bidder; onBidderChange: (bidder: Bidder) => void }

export default function MarketplaceDashboardSecure(props: MarketplaceDashboardSecureProps) {
  const query = useQuery({ queryKey: ["buyer-status", props.bidder.name], queryFn: () => apiGet<BuyerStatusResponse>(`/buyers/status/by-name?full_name=${encodeURIComponent(props.bidder.name)}`), retry: false });
  const profile = query.data?.profile;
  return <div className="relative"><MarketplaceDashboardV2 {...props} />{profile && (profile.verification_status === "REJECTED" || profile.verification_status === "INCOMPLETE") && <Link data-testid="dashboard-resubmission-link" to={`/resubmit/${profile.id}`} className="fixed bottom-6 right-6 z-30 inline-flex items-center gap-2 rounded-full bg-[#03AC0E] px-5 py-3 text-sm font-bold text-white shadow-xl shadow-green-900/20 transition hover:-translate-y-0.5 hover:bg-[#02930c]"><RefreshCw size={16} /> Perbaiki pengajuan</Link>}</div>;
}