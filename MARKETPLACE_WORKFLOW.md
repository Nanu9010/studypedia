# StudyPedia Marketplace Workflow (Short Architecture)

## 1) Architecture Overview

StudyPedia marketplace follows a standard Django layered flow:

- **Presentation layer (templates)**:
  - Marketplace listing: `ecommerce/templates/ecommerce/marketplace.html`
  - Cart + checkout UI: `ecommerce/templates/ecommerce/cart.html`, `ecommerce/templates/ecommerce/checkout.html`
  - User library/download UI: `accounts/templates/accounts/profile.html`

- **Application layer (views/controllers)**:
  - `marketplace()` shows featured Notes/Papers + stats
  - `add_to_cart()`, `cart_view()`, `checkout()` handle buy flow
  - `payment_callback()` confirms Razorpay payments
  - `download_item()` validates ownership and serves file

- **Domain/data layer (models)**:
  - Content: `Note`, `Paper` (price, credits, pdf_file, is_active)
  - Commerce: `Cart`, `CartItem`, `Order`, `OrderItem`, `Coupon`, `PurchaseRequest`, `DownloadLog`
  - User: `User` with `credits`

- **Payment layer**:
  - **Credits**: immediate success if enough user credits
  - **Razorpay**: create order, verify signature in callback, mark paid

## 2) High-Level Diagram

```mermaid
flowchart LR
    U[Student User]
    M[Marketplace UI]
    V[Ecommerce Views]
    DB[(DB Models)]
    RP[Razorpay]
    P[Profile Library]

    U --> M
    M --> V
    V --> DB
    V --> RP
    RP --> V
    V --> DB
    DB --> P
    U --> P
```

## 3) Buy + Download Workflow

```mermaid
sequenceDiagram
    participant User
    participant Market as Marketplace
    participant Ecom as Ecommerce Views
    participant DB as DB
    participant Razor as Razorpay
    participant Profile as Profile/Library

    User->>Market: Open marketplace
    Market->>Ecom: marketplace()
    Ecom->>DB: Load active Note/Paper + stats
    DB-->>Market: Featured items

    User->>Ecom: add_to_cart(item, type)
    Ecom->>DB: Create/get Cart + CartItem
    User->>Ecom: checkout(payment_method)
    Ecom->>DB: Create Order + OrderItem + PurchaseRequest(pending)

    alt Payment = Credits
        Ecom->>DB: Deduct user credits
        Ecom->>DB: Mark order/purchase paid
    else Payment = Razorpay
        Ecom->>Razor: Create Razorpay order
        Razor-->>User: Payment popup
        User->>Ecom: payment_callback(signature data)
        Ecom->>Razor: Verify signature
        Ecom->>DB: Mark order/purchase paid
    end

    User->>Profile: Open library
    Profile->>DB: Fetch purchases
    User->>Ecom: download_item()
    Ecom->>DB: Validate paid ownership + log download
    Ecom-->>User: Redirect to file URL
```

## 4) Current Important Notes

- Purchase access is controlled by paid records (`OrderItem` / `PurchaseRequest`).
- Download is allowed only for paid users and writes a `DownloadLog`.
- Coupons are session based and applied during checkout.
- Admin commerce dashboard exists for order/coupon monitoring (`adminapp`).
