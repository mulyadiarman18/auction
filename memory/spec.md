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