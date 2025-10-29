# 🧪 Threat Intelligence Testing Guide

## Quick Start

### 1. Backend Setup
```bash
cd backend

# Run migrations
python manage.py migrate threat_intelligence

# Create superuser (if needed)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies (if needed)
npm install

# Start dev server
npm run dev
```

### 3. Access the Application
Open browser: `http://localhost:5173/threat-intelligence`

---

## 🎯 Testing Checklist

### **Threats Tab**

#### Create Threat ✅
1. Click **"Add Threat"** button
2. Fill in the form:
   - Title: "Test Phishing Campaign"
   - Description: "Malicious emails targeting employees with fake login pages from IP 192.168.1.100"
   - Type: Cyber Security
   - Severity: High
   - Source: "Email Security Gateway"
   - Tags: phishing, social-engineering
3. ✅ **Check "Analyze with AI after creation"**
4. Click **"Create Threat"**
5. ✅ Verify: Toast notification appears
6. ✅ Verify: Threat appears in list
7. ✅ Verify: AI analysis runs automatically

#### View Threat Details ✅
1. Click **"View Details"** on any threat
2. **Details Tab:**
   - ✅ Verify all threat info displays
   - ✅ Click different status buttons
   - ✅ Verify status updates
3. **AI Analysis Tab:**
   - ✅ Click "AI Analyze" button
   - ✅ Verify confidence score appears
   - ✅ Verify analysis results show (severity, attack vectors, recommendations)
4. **Indicators Tab:**
   - ✅ Click "Extract Now" button
   - ✅ Verify IOCs are extracted (IP: 192.168.1.100 should be detected)
   - ✅ Verify indicator cards show type, confidence, value
5. **Risk Assessment Tab:**
   - ✅ Click "Generate Now" button
   - ✅ Verify risk assessment is created
   - ✅ Check Risk Assessments tab for new entry

#### Delete Threat ✅
1. Click **trash icon** on a threat
2. ✅ Verify confirmation dialog appears
3. Click OK
4. ✅ Verify threat is removed
5. ✅ Verify statistics update

---

### **Alerts Tab**

#### Create Alert ✅
1. Click **"Create Alert"** button
2. Fill in the form:
   - Title: "Unauthorized Access Attempt"
   - Description: "Failed login attempts detected from unknown location"
   - Type: Unauthorized Access
   - Severity: High
   - Source: "Access Control System"
3. Click **"Create Alert"**
4. ✅ Verify alert appears in list

#### Acknowledge Alert ✅
1. Find an alert with status "new"
2. Click **"Acknowledge"** button
3. ✅ Verify status changes to "acknowledged"
4. ✅ Verify button disappears after acknowledgment

#### Delete Alert ✅
1. Click **trash icon** on an alert
2. ✅ Verify confirmation dialog
3. Click OK
4. ✅ Verify alert is removed

---

### **Risk Assessments Tab**

#### View Assessments ✅
1. Navigate to Risk Assessments tab
2. ✅ Verify assessments generated from threats appear
3. ✅ Verify badges show:
   - Risk level (red)
   - Likelihood (orange)
   - Impact (yellow)
4. ✅ Verify vulnerability analysis displays

---

### **Threat Indicators Tab**

#### View and Search Indicators ✅
1. Navigate to Indicators tab
2. ✅ Verify extracted IOCs appear
3. **Test Search:**
   - Type an IP address in search box
   - ✅ Verify filtering works
   - Clear search
   - ✅ Verify all indicators return
4. ✅ Verify each indicator shows:
   - Type (IP, domain, email, etc.)
   - Confidence level
   - Occurrence count
   - Last seen date

---

### **Watchlist Tab**

#### View Watchlist Entries ✅
1. Navigate to Watchlist tab
2. ✅ Verify entries display (if any exist)
3. ✅ Verify each entry shows:
   - Subject name
   - Risk level badge
   - Watchlist type badge
   - Detection count
   - Last detected date

---

## 🤖 AI Features Testing

### Test 1: AI Threat Analysis
**Steps:**
1. Create threat with detailed description
2. Enable "Analyze with AI" checkbox
3. Submit

**Expected Results:**
- ✅ Threat created successfully
- ✅ AI analysis runs automatically
- ✅ Toast shows "AI analysis complete!"
- ✅ View Details → AI Analysis tab shows results
- ✅ Confidence score is displayed
- ✅ Attack vectors are identified
- ✅ Recommendations are provided

### Test 2: Manual AI Analysis
**Steps:**
1. Open existing threat details
2. Click "AI Analyze" button

**Expected Results:**
- ✅ Loading indicator appears
- ✅ AI processes the threat
- ✅ Results populate in AI Analysis tab
- ✅ Toast notification confirms completion

### Test 3: Risk Assessment Generation
**Steps:**
1. Open threat details
2. Go to Risk Assessment tab
3. Click "Generate Now"

**Expected Results:**
- ✅ AI generates comprehensive assessment
- ✅ Toast shows success message
- ✅ Assessment appears in Risk Assessments tab
- ✅ Contains: risk level, likelihood, impact, mitigation strategies

### Test 4: Indicator Extraction
**Steps:**
1. Create threat with IOCs in description (IPs, domains, emails)
2. Open threat details
3. Go to Indicators tab
4. Click "Extract Now"

**Expected Results:**
- ✅ AI extracts all IOCs from description
- ✅ Each indicator has type, value, confidence
- ✅ Indicators appear in Threat Indicators tab
- ✅ Can be searched and filtered

---

## 📊 Statistics Testing

### Dashboard Statistics ✅
1. Create a threat → ✅ Threat count increases
2. Create an alert → ✅ Alert count increases
3. Generate risk assessment → ✅ Assessment count increases
4. Extract indicators → ✅ Indicator count increases
5. Delete items → ✅ Counts decrease accordingly

---

## 🎨 UI/UX Testing

### Visual Elements ✅
- ✅ Color-coded severity badges (critical=red, high=orange, etc.)
- ✅ Status badges with appropriate colors
- ✅ Icons display correctly
- ✅ Hover effects work
- ✅ Loading states show during API calls
- ✅ Empty states display when no data

### Dark Mode ✅
1. Toggle dark mode in settings
2. ✅ Verify all modals render correctly
3. ✅ Verify tabs are readable
4. ✅ Verify cards have proper contrast

### Responsive Design ✅
1. Resize browser window
2. ✅ Verify layout adapts
3. ✅ Test on mobile viewport
4. ✅ Verify modals are usable

---

## 🔄 Data Flow Testing

### Create → Read → Update → Delete ✅

**Threat CRUD:**
1. ✅ Create threat → appears in list
2. ✅ Read threat → opens detail modal
3. ✅ Update status → changes reflect immediately
4. ✅ Delete threat → removed from list

**Alert CRUD:**
1. ✅ Create alert → appears in list
2. ✅ Read alert → displays full details
3. ✅ Update (acknowledge) → status changes
4. ✅ Delete alert → removed from list

---

## ⚠️ Error Handling Testing

### Network Errors ✅
1. Stop backend server
2. Try creating a threat
3. ✅ Verify error toast appears
4. ✅ Verify user-friendly message

### Validation Errors ✅
1. Open create modal
2. Leave required fields empty
3. Click submit
4. ✅ Verify validation message appears

### Confirmation Dialogs ✅
1. Click delete button
2. ✅ Verify confirmation dialog appears
3. Click cancel
4. ✅ Verify item is NOT deleted

---

## 🚀 Performance Testing

### Load Time ✅
1. Navigate to threat intelligence page
2. ✅ Verify page loads quickly
3. ✅ Verify statistics fetch
4. ✅ Verify tabs load without delay

### Mutation Speed ✅
1. Create multiple items rapidly
2. ✅ Verify no lag or freezing
3. ✅ Verify all items are created
4. ✅ Verify UI updates smoothly

---

## 📝 Sample Test Data

### Threat 1: Phishing Campaign
```
Title: "Targeted Phishing Campaign"
Description: "Sophisticated phishing emails sent from compromised domain evil-site.com targeting finance department. Emails contain links to fake login page at http://192.168.1.100/login. Sender email: attacker@fake-domain.com"
Type: Social Engineering
Severity: Critical
Source: "Email Security Gateway"
Tags: phishing, credential-theft, finance
```

### Threat 2: Ransomware
```
Title: "Ransomware Activity Detected"
Description: "Suspicious file encryption activity detected on workstation WS-2024. Hash: a1b2c3d4e5f6. Connection attempts to C2 server 203.0.113.50 on port 8080."
Type: Cyber Security
Severity: Critical
Source: "Endpoint Protection"
Tags: ransomware, encryption, malware
```

### Alert 1: Failed Logins
```
Title: "Multiple Failed Login Attempts"
Description: "5 failed login attempts for admin account from IP 198.51.100.10 within 2 minutes"
Type: Intrusion Detection
Severity: High
Source: "Authentication System"
```

---

## ✅ Expected AI Outputs

### For Phishing Threat:
**Extracted Indicators:**
- Domain: evil-site.com
- IP: 192.168.1.100
- Email: attacker@fake-domain.com

**AI Analysis:**
- Severity: Critical/High
- Attack Vector: Social Engineering, Credential Theft
- Recommendations: Block domain, user training, MFA enforcement

**Risk Assessment:**
- Risk Level: High
- Likelihood: Likely
- Impact: Severe
- Mitigation: Email filtering, security awareness training

---

## 🎉 Success Criteria

All tests pass if:
- ✅ No console errors
- ✅ All CRUD operations work
- ✅ AI features execute successfully
- ✅ UI is responsive and user-friendly
- ✅ Error handling works properly
- ✅ Data persists correctly
- ✅ Statistics update in real-time
- ✅ Dark mode works
- ✅ Confirmations prevent accidental deletions

**Status: READY FOR PRODUCTION** 🚀
