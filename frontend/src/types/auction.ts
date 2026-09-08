export type LotStatus = "LIVE" | "UPCOMING" | "ENDED";

export interface Lot {
  id: string;
  lot_number: string;
  title: string;
  category: string;
  status: LotStatus;
  location: string;
  image_url: string;
  gallery_urls: string[];
  year: number;
  mileage: string;
  transmission: string;
  engine: string;
  grade: string;
  inspection_score: number;
  seller_verified: boolean;
  base_price: number;
  current_bid: number;
  minimum_increment: number;
  auction_start: string;
  auction_end: string;
  description: string;
  features: string[];
  vin: string;
  document_status: string;
}

export interface Bid {
  id: string;
  lot_id: string;
  bidder_name: string;
  bidder_type: string;
  amount: number;
  created_at: string;
  status: "VALID" | "OUTBID";
}

export interface Bidder {
  name: string;
  type: string;
}

export interface WishlistItem {
  id: string;
  bidder_name: string;
  lot_id: string;
  lot_number: string;
  title: string;
  image_url: string;
  current_bid: number;
  status: LotStatus;
  auction_end: string;
  created_at: string;
}

export interface WishlistToggleResponse {
  lot_id: string;
  liked: boolean;
}

export type BuyerType = "individual" | "company";
export type VerificationStatus = "PENDING" | "UNDER_REVIEW" | "APPROVED" | "REJECTED";

export interface BuyerRegistrationCreate {
  buyer_type: BuyerType;
  full_name: string;
  email: string;
  phone: string;
  identity_number: string;
  company_name: string;
  tax_number: string;
  address: string;
}

export interface BuyerProfile extends BuyerRegistrationCreate {
  id: string;
  verification_status: VerificationStatus;
  created_at: string;
}

export interface AdminSummary {
  total_lots: number;
  live_lots: number;
  upcoming_lots: number;
  ended_lots: number;
  total_bids: number;
  total_bid_value: number;
  pending_buyers: number;
}

export interface AdminWinner {
  lot_id: string;
  lot_number: string;
  title: string;
  status: "PENDING" | "WON" | "UNSOLD";
  bidder_name: string | null;
  winning_bid: number | null;
  auction_end: string;
}