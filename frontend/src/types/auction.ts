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
  auction_code: string;
  unit_number: string;
  hull_number: string;
  registration_code: string;
  brand: string;
  model_type: string;
  operating_hours: string;
  seller_name: string;
  pool_location: string;
  document_completeness: string[];
  session_id: string | null;
  unit_status: "DRAFT" | "VERIFIED" | "READY" | "IN_AUCTION" | "SOLD" | "UNSOLD" | "HANDED_OVER" | "WITHDRAWN";
  inspection_status: "UNSCHEDULED" | "SCHEDULED" | "IN_PROGRESS" | "COMPLETED" | "REJECTED";
  reserve_price: number;
}

export interface Bid {
  id: string;
  lot_id: string;
  bidder_name: string;
  bidder_type: string;
  amount: number;
  created_at: string;
  status: "VALID" | "OUTBID";
  bidder_code: string;
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
export type AdminRole = "super_admin" | "reviewer" | "finance" | "inspector";
export type InternalRole = AdminRole;

export interface BuyerDocument {
  id: string;
  document_type: "identity_document" | "company_document";
  file_name: string;
  content_type: string;
  size_bytes: number;
  storage_id: string;
  uploaded_at: string;
}

export interface DepositDocument {
  id: string;
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
  resubmission_required: boolean;
  membership_status: "INACTIVE" | "ACTIVE";
  deposit_status: "NOT_SUBMITTED" | "PENDING" | "CONFIRMED" | "REJECTED";
  deposit_amount: number;
  deposit_document: DepositDocument | null;
  deposit_reviewed_at: string | null;
  deposit_reviewed_by: string | null;
  deposit_review_reason: string | null;
  buyer_code: string;
  membership_fee: number;
  membership_payment_status: "NOT_SUBMITTED" | "PENDING" | "CONFIRMED" | "REJECTED";
  membership_document: DepositDocument | null;
  membership_expires_at: string | null;
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
  admin_role: InternalRole;
  old_status: string;
  new_status: string;
  reason: string;
  created_at: string;
}

export interface AdminUser {
  id: string;
  username: string;
  name: string;
  role: InternalRole;
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

export type SessionStatus = "DRAFT" | "PUBLISHED" | "LIVE" | "CLOSED";

export interface AuctionSession {
  id: string;
  code: string;
  title: string;
  start_at: string;
  end_at: string;
  publication_at: string;
  status: SessionStatus;
  lot_ids: string[];
  created_at: string;
}

export interface BidAccessStatus {
  bidder_name: string;
  buyer_id: string | null;
  verification_status: string;
  membership_status: string;
  deposit_status: string;
  deposit_amount: number;
  eligible: boolean;
  reasons: string[];
}

export interface DepositReviewItem {
  buyer_id: string;
  bidder_name: string;
  email: string;
  amount: number;
  status: string;
  document_file_name: string;
  submitted_at: string;
}

export interface VendorDocument {
  id: string;
  document_type: "LEGALITY" | "PKS";
  file_name: string;
  content_type: string;
  size_bytes: number;
  storage_id: string;
  uploaded_at: string;
}

export interface VendorProfile {
  id: string;
  company_name: string;
  tax_number: string;
  address: string;
  pic_name: string;
  email: string;
  phone: string;
  legality_status: "INCOMPLETE" | "PENDING" | "APPROVED" | "REJECTED";
  pks_status: "NOT_UPLOADED" | "UNDER_REVIEW" | "ACTIVE" | "EXPIRED";
  documents: VendorDocument[];
  created_at: string;
  seller_code: string;
  admin_fee_percent: number;
  contract_number: string;
  contract_start: string | null;
  contract_end: string | null;
  pool_address: string;
  pool_pic: string;
  settlement_terms: string;
}

export interface VendorUnitCreate {
  unit_name: string;
  category: string;
  brand: string;
  model_type: string;
  year: number;
  unit_number: string;
  hull_number: string;
  operating_hours: string;
  pool_location: string;
  proposed_price: number;
}

export interface VendorUnitSubmission extends VendorUnitCreate {
  id: string;
  vendor_id: string;
  status: "DRAFT" | "SUBMITTED" | "APPROVED" | "REJECTED" | "LOTTED";
  settlement_status: "NONE" | "PENDING" | "INVOICED" | "PAID";
  winning_bid: number | null;
  created_at: string;
}

export interface VendorSettlement {
  unit_submission_id: string;
  unit_name: string;
  status: string;
  settlement_status: string;
  winning_bid: number | null;
  admin_fee_percent: number;
  admin_fee_amount: number;
  net_settlement: number;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  buyer_id: string;
  bidder_name: string;
  lot_id: string;
  lot_title: string;
  hammer_price: number;
  deposit_deduction: number;
  buyer_admin_fee: number;
  tax_amount: number;
  total_due: number;
  due_at: string;
  status: "PENDING_PAYMENT" | "PAYMENT_REVIEW" | "PAID" | "OVERDUE" | "CANCELLED";
  payment_document: DepositDocument | null;
  created_at: string;
}

export interface InspectionRecord {
  id: string;
  lot_id: string;
  inspector_name: string;
  planned_at: string;
  status: "UNSCHEDULED" | "SCHEDULED" | "IN_PROGRESS" | "COMPLETED" | "REJECTED";
  component_scores: Record<string, number>;
  notes: string;
  total_score: number | null;
  suggested_grade: "A" | "B" | "C" | "D" | null;
  completed_at: string | null;
  photos: Array<{ slot: string; file_name: string; uploaded_by: string; uploaded_at: string }>;
}