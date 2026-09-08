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
export type VerificationStatus = "INCOMPLETE" | "PENDING" | "UNDER_REVIEW" | "APPROVED" | "REJECTED";
export type AdminRole = "super_admin" | "reviewer";

export interface BuyerDocument {
  id: string;
  document_type: "identity_document" | "company_document";
  file_name: string;
  content_type: string;
  size_bytes: number;
  storage_id: string;
  uploaded_at: string;
}

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
  screening_status: "INCOMPLETE" | "READY";
  screening_issues: string[];
  documents: BuyerDocument[];
  created_at: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
  review_reason: string | null;
}

export interface BuyerVerificationUpdate {
  verification_status: "APPROVED" | "REJECTED";
  admin_name: string;
  reason: string;
}

export interface BuyerStatusResponse {
  found: boolean;
  profile: BuyerProfile | null;
}

export interface AdminAuditLog {
  id: string;
  entity_type: "BUYER";
  entity_id: string;
  entity_name: string;
  action: "APPROVE" | "REJECT";
  admin_name: string;
  admin_role: AdminRole;
  old_status: string;
  new_status: string;
  reason: string;
  created_at: string;
}

export interface AdminUser {
  id: string;
  username: string;
  name: string;
  role: AdminRole;
  is_active: boolean;
}

export interface AdminSessionResponse {
  user: AdminUser;
  expires_at: string;
}

export interface BuyerResubmissionUpdate {
  full_name: string;
  email: string;
  phone: string;
  identity_number: string;
  company_name: string;
  tax_number: string;
  address: string;
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