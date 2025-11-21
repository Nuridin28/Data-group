# Fix: Date Parsing Error in Analytics Endpoints

## Issue
The `/analytics/revenue` endpoint (and other analytics endpoints) was failing with error:
```
"Unknown datetime string format, unable to parse: string, at position 0"
```

This occurred when testing in Swagger UI where the example value "string" was being sent as the actual date value.

## Root Cause
In `services/data_service.py`, the `get_dataframe()` method was calling `pd.to_datetime()` directly on filter values without validation, causing it to try parsing the literal string "string" as a date.

## Solution Implemented

### 1. Added `_parse_date_filter()` helper method
- Safely parses date strings with validation
- Returns `None` for invalid/placeholder values ("string", "none", "null", empty)
- Uses `errors='coerce'` to handle parsing failures gracefully
- Located in `services/data_service.py`

### 2. Updated `get_dataframe()` method
- Now uses `_parse_date_filter()` for date validation
- Only applies date filters if parsing succeeds
- Also added validation for other filter fields (region, city, etc.) to ignore "string" placeholders

### 3. Enhanced schema examples
- Updated `AnalyticsRequest` and `PredictionRequest` in `models/schemas.py`
- Added `examples` parameter to show proper date format (YYYY-MM-DD)
- Helps users understand the expected format in Swagger UI

## Testing
✅ String placeholders are now ignored
✅ Valid dates (YYYY-MM-DD) work correctly
✅ Empty/null values are handled
✅ Invalid date formats return None gracefully
✅ All filter types (date, region, city, etc.) validate input

## Usage Examples

**Before (would fail):**
```json
{
  "start_date": "string",
  "end_date": "string"
}
```

**After (works correctly):**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

Or simply omit the fields or use `null`:
```json
{
  "start_date": null
}
```

## Files Modified
- `services/data_service.py` - Added date parsing validation
- `models/schemas.py` - Added examples to schemas

