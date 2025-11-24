# Review API Documentation for Mobile App

## Overview
This document describes all the Review APIs that the mobile app needs to interact with.

---

## 1. Get Product Reviews
**GET** `/api/v1/reviews/product/{product_id}/`

Returns all approved reviews for a specific product in the format requested by the mobile app.

### Response Format:
```json
{
  "rating": {
    "productID": "1",
    "businessID": "1",
    "expTime": "2025-12-21T18:00:00Z",
    "rates": [
      {
        "title": "Review by username",
        "description": "Great product!",
        "value": "5"
      },
      {
        "title": "Review by another_user",
        "description": "Good quality",
        "value": "4"
      }
    ]
  }
}
```

### Fields:
- `productID`: Product ID (string)
- `businessID`: Business ID (string)
- `expTime`: Expiration time (ISO format, 30 days from now)
- `rates`: Array of review objects
  - `title`: Review title (string)
  - `description`: Review comment/description (string)
  - `value`: Star rating as string (1-5)

### Example:
```bash
GET https://mywebsite.osc-fr1.scalingo.io/api/v1/reviews/product/1/
```

---

## 2. Create Product Review
**POST** `/api/v1/reviews/create/`

Creates a new review for a product.

### Request Body:
```json
{
  "userId": "1",  // or "phone" (e.g., "05340382335")
  "productId": "1",
  "rateNumber": "5",  // Optional, use star-value instead
  "star-value": "5",  // Star rating (1-5)
  "time": "2025-11-21T18:00:00Z",  // Optional timestamp
  "description": "Great product!"  // Optional review text
}
```

### Response (Success):
```json
{
  "message": "Review created successfully",
  "review_id": 123
}
```

### Response (Update - if review exists):
```json
{
  "message": "Review updated successfully",
  "review_id": 123
}
```

### Fields:
- `userId` or `phone`: User ID or phone number (required)
- `productId`: Product ID (required)
- `star-value` or `rateNumber`: Star rating 1-5 (required)
- `time`: Optional timestamp (ISO format)
- `description`: Optional review text

### Example:
```bash
POST https://mywebsite.osc-fr1.scalingo.io/api/v1/reviews/create/
Content-Type: application/json

{
  "userId": "1",
  "productId": "1",
  "star-value": "5",
  "description": "Excellent product!"
}
```

---

## 3. Delete Product Review
**DELETE** `/api/v1/reviews/delete/`

Deletes a review for a product.

### Request Body:
```json
{
  "userId": "1",  // or "phone"
  "productId": "1"
}
```

### Response (Success):
```json
{
  "message": "Review deleted successfully"
}
```

### Response (Error):
```json
{
  "error": "Review not found"
}
```

### Fields:
- `userId` or `phone`: User ID or phone number (required)
- `productId`: Product ID (required)

### Example:
```bash
DELETE https://mywebsite.osc-fr1.scalingo.io/api/v1/reviews/delete/
Content-Type: application/json

{
  "userId": "1",
  "productId": "1"
}
```

---

## 4. Get All Product Reviews for a Business
**GET** `/api/v1/reviews/business/{business_id}/products/`

Returns all product reviews for all products in a specific business/store.

### Response Format:
```json
[
  {
    "productID": "1",
    "businessID": "1",
    "productName": "Burger",
    "rates": [
      {
        "title": "Review by username",
        "description": "Great burger!",
        "value": "5"
      }
    ]
  },
  {
    "productID": "2",
    "businessID": "1",
    "productName": "Pizza",
    "rates": [
      {
        "title": "Review by another_user",
        "description": "Delicious!",
        "value": "4"
      }
    ]
  }
]
```

### Fields:
- Array of product review objects:
  - `productID`: Product ID (string)
  - `businessID`: Business ID (string)
  - `productName`: Product name (string)
  - `rates`: Array of review objects (same format as above)

### Example:
```bash
GET https://mywebsite.osc-fr1.scalingo.io/api/v1/reviews/business/1/products/
```

---

## Error Responses

All APIs may return the following error responses:

### 400 Bad Request:
```json
{
  "error": "Error message here"
}
```

### 404 Not Found:
```json
{
  "error": "Product not found"
}
```

### 401 Unauthorized:
```json
{
  "error": "User authentication required"
}
```

---

## Notes

1. **Authentication**: 
   - `userId` can be a user ID (integer) or phone number (string)
   - If `userId` is a phone number, the system will try to find the user by business phone
   - For anonymous users, authentication may be required for some operations

2. **Review Status**:
   - New reviews are created with status `PENDING` and require moderation
   - Only `APPROVED` reviews are returned in GET requests
   - Reviews can be updated by the same user

3. **Rating Values**:
   - Star rating must be between 1 and 5
   - Can be sent as `star-value` or `rateNumber` in POST request
   - Returned as string in GET responses

4. **Time Format**:
   - Use ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`
   - Example: `2025-11-21T18:00:00Z`

---

## Complete API List

1. **GET** `/api/v1/reviews/product/{product_id}/` - Get reviews for a product
2. **POST** `/api/v1/reviews/create/` - Create a new review
3. **DELETE** `/api/v1/reviews/delete/` - Delete a review
4. **GET** `/api/v1/reviews/business/{business_id}/products/` - Get all product reviews for a business

---

## Testing

You can test these APIs using:
- Postman
- curl
- Your mobile app

Example curl commands:

```bash
# Get product reviews
curl https://mywebsite.osc-fr1.scalingo.io/api/v1/reviews/product/1/

# Create review
curl -X POST https://mywebsite.osc-fr1.scalingo.io/api/v1/reviews/create/ \
  -H "Content-Type: application/json" \
  -d '{"userId": "1", "productId": "1", "star-value": "5", "description": "Great!"}'

# Delete review
curl -X DELETE https://mywebsite.osc-fr1.scalingo.io/api/v1/reviews/delete/ \
  -H "Content-Type: application/json" \
  -d '{"userId": "1", "productId": "1"}'

# Get business product reviews
curl https://mywebsite.osc-fr1.scalingo.io/api/v1/reviews/business/1/products/
```



