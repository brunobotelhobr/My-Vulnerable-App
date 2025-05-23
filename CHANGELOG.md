# Changelog - Vulnerable Fishing Store

## Latest Security Changes

### Authentication & Authorization
- Changed token storage from localStorage to cookies for XSS challenges
- Added IDOR vulnerability in user address endpoints (/api/user/{id}/address)
- User IDs exposed in API endpoints for easier exploitation

### SQL Injection
- Added vulnerable search endpoint with multiple exploitation paths:
  - `ORDER BY` to discover number of columns
  - `UNION SELECT` to map column positions
  - Table enumeration using sqlite_master
  - Credential dumping from users table

### XSS (Cross-Site Scripting)
- Implemented stored XSS in product comments
- Updated payload to use iframe-based JavaScript execution
- Cookie-based token theft now possible

### Dependency Vulnerabilities
- Added vulnerable node-serialize@0.0.3 for RCE
- New endpoint /api/import-preferences vulnerable to deserialization attacks
- Express server running on port 3001 for serialization challenges

## Security Challenge Updates
- Added detailed solutions in challenge.html
- Included progressive exploitation steps
- Added new IDOR challenge section
- Added dependency exploitation challenge

## Known Vulnerabilities
1. Stored XSS in product comments
2. SQL Injection in product search
3. IDOR in user address endpoints
4. RCE via node-serialize
5. Token exposure in cookies

## Educational Notes
⚠️ These vulnerabilities are intentionally implemented for educational purposes.
DO NOT use these techniques on real websites or in production environments. 