# LelangOto MVP Spec

## Product
Responsive online vehicle auction marketplace for visitors and bidder participants. The MVP focuses on browsing lots, viewing lot detail, and placing simulated bids persisted in MongoDB. The active UI uses a familiar light marketplace layout with white surfaces and green primary actions.

## Data model
- `lots`: vehicle metadata, auction status/times, pricing, increment, inspection, image, and location.
- `bids`: lot id, bidder name/type, amount, timestamp, and validity status.

## Key flows
1. Visitor opens the editorial home/catalog, filters or searches lots, and opens a lot detail page.
2. Demo bidder persona is selected in the header; no real authentication or payment is used.
3. Bidder chooses a quick increment or enters a custom amount at least current bid plus the lot increment; the API stores the bid and updates the lot current bid.
4. Dashboard shows the selected bidder's bid history and summary.

## Roles and auth
The MVP has visitor and bidder personas only. Authentication is intentionally mocked by a local demo persona selector; there are no admin credentials, payment integrations, or third-party services.

## Seed data
Six demo lots are written by `backend/seed.py`: live Porsche 911 GT3 RS and Audi R8, upcoming Impala, Mercedes 280SL, Koenigsegg, and an ended Dodge Challenger.

## Added marketplace features
- Catalog filters support minimum/maximum current bid (in millions), location, category, status, and ending/price sort options.
- Wishlist items are persisted in MongoDB per demo bidder persona via `/api/wishlists`; toggling a lot shows a local toast reminder.
- `/register` collects individual/company bidder data and displays a `PENDING` verification state after submission. This is a demo flow without document upload or external auth.
- `/admin` is an intentionally open demo console for lot status/schedule changes, summary metrics, and computed winner/unsold outcomes.
- `/admin/approvals` lists `PENDING` bidder registrations and lets the demo admin persist `APPROVED` or `REJECTED` status decisions.
- Registration now requires identity details plus a real PDF/JPG/PNG upload (and a company document for company accounts). Files are stored in Mongo GridFS; auto screening keeps incomplete submissions out of the review queue.
- Demo admin roles are `super_admin` (inventory, schedule, outcomes, approvals) and `reviewer` (approvals only). Backend routes enforce the selected role, though authentication itself remains mocked.
- Rejections require a reason. Every approval decision stores reviewer identity, timestamp, previous/new status, and reason in `admin_audit_logs`.
- Bidder dashboard resolves the selected persona's latest registration and shows an `INCOMPLETE`, `PENDING`, `APPROVED`, or `REJECTED` status alert.
- Admin routes now require a Mongo-backed HTTP-only session created by `/api/admin/auth/login`; role comes from the authenticated account, not a client selector.
- Rejected bidders can open `/resubmit/{buyerId}` from the dashboard, correct their data, upload a replacement identity document, and return to `PENDING` after screening.
- Reviewer document links open PDF/JPG/PNG inside an authenticated modal preview rather than downloading immediately.