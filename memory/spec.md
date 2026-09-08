# MIT Auction MVP Spec

## Product
Responsive MPI/MIT unit-disposal auction platform for visitors, bidder members, reviewers, and administrators. The active UI retains the familiar marketplace layout while using an industrial yellow, charcoal, and white identity under the product name **MIT Auction**.

## Data model
- `lots`: mining equipment identity (unit/hull/registration codes, brand/model, operating hours), auction status/times, pricing, increment, inspection, vendor, documents, image, and pool location.
- `bids`: lot id, bidder name/type, amount, timestamp, and validity status.

## Key flows
1. Visitor opens the mining-equipment catalog, filters or searches units, and opens a lot detail page.
2. Demo bidder persona is selected in the header; no real authentication or payment is used.
3. Bidder chooses a quick increment or enters a custom amount at least current bid plus the lot increment; the API stores the bid and updates the lot current bid.
4. Dashboard shows the selected bidder's bid history and summary.

## Roles and auth
The public bidder identity remains a local demo persona. Admin authentication is real and session-backed with `super_admin` and `reviewer` roles. Payment, membership fee, and deposit confirmation remain outside the current implemented slice.

## Seed data
Six mining-equipment lots are written by `backend/seed.py`: Komatsu excavator and dump truck, Caterpillar motor grader and wheel loader, Komatsu dozer, and Volvo articulated hauler across Indonesian mining pools.

## Added marketplace features
- Catalog filters support minimum/maximum current bid (in millions), location, category, status, and ending/price sort options.
- Wishlist items are persisted in MongoDB per demo bidder persona via `/api/wishlists`; toggling a lot shows a local toast reminder.
- `/register` collects individual/company bidder data and uploads required identity/legal documents before reaching `PENDING`.
- `/admin` is protected by HTTP-only sessions and exposes role-appropriate controls for lot status/schedule changes, summary metrics, and computed winner/unsold outcomes.
- `/admin/approvals` lists `PENDING` bidder registrations and lets the demo admin persist `APPROVED` or `REJECTED` status decisions.
- Registration now requires identity details plus a real PDF/JPG/PNG upload (and a company document for company accounts). Files are stored in Mongo GridFS; auto screening keeps incomplete submissions out of the review queue.
- Admin roles are `super_admin` (inventory, schedule, outcomes, approvals) and `reviewer` (approvals only). Backend dependencies enforce the authenticated role.
- Rejections require a reason. Every approval decision stores reviewer identity, timestamp, previous/new status, and reason in `admin_audit_logs`.
- Bidder dashboard resolves the selected persona's latest registration and shows an `INCOMPLETE`, `PENDING`, `APPROVED`, or `REJECTED` status alert.
- Admin routes now require a Mongo-backed HTTP-only session created by `/api/admin/auth/login`; role comes from the authenticated account, not a client selector.
- Rejected bidders can open `/resubmit/{buyerId}` from the dashboard, correct their data, upload a replacement identity document, and return to `PENDING` after screening.
- Reviewer document links open PDF/JPG/PNG inside an authenticated modal preview rather than downloading immediately.