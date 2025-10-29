# 🧪 Access Control Testing Guide

## 📦 Setup Test Data

### Step 1: Create Test Data

```bash
cd backend
python manage.py shell < create_test_data.py
```

This creates:
- ✅ 1 Test Organization
- ✅ 5 Test Users (John, Jane, Mike, Sarah, David)
- ✅ 8 Access Points (Doors, Gates, Turnstiles, etc.)
- ✅ ~100+ Access Logs with realistic patterns
- ✅ 3 AI-detected anomalies
- ✅ Multiple denied access attempts

---

## 🧪 What to Test

### **Test 1: Access Points Management** (`/access-points`)

#### **A. View Access Points**
✅ Navigate to http://localhost:3000/access-points
✅ You should see 8 access points in the table
✅ Check stats cards show correct counts

#### **B. Search & Filter**
1. Type "Server" in search → Should show "Server Room Gate"
2. Type "Door" → Should show all doors
3. Select filter "Active" → Should show only active points
4. Select filter "Maintenance" → Should show empty (no maintenance points)

#### **C. Create New Access Point**
1. Click "Add Access Point" button
2. Fill form:
   ```
   Name: Test Security Door
   Type: Door 🚪
   Location: Building C - Floor 5
   Hardware ID: AP-TEST-001
   IP Address: 192.168.1.200
   Description: Test door for QA
   Status: Active
   ```
3. Click "Create"
4. Should see toast notification: "✅ Access point created successfully!"
5. New point appears in table

#### **D. Edit Access Point**
1. Find "Test Security Door" in table
2. Click Edit button (✏️)
3. Change name to "Test Security Door UPDATED"
4. Click "Update"
5. Should see toast: "✅ Access point updated successfully!"
6. Name updates in table

#### **E. Lockdown Mode**
1. Find "Main Entrance Door"
2. Click Lock icon (🔒)
3. Should see toast: "✅ Lockdown activated!"
4. Red "Lockdown" badge appears
5. Click Unlock icon (🔓)
6. Lockdown badge disappears

#### **F. Delete Access Point**
1. Find "Test Security Door UPDATED"
2. Click Delete button (🗑️)
3. Confirm deletion in popup
4. Should see toast: "✅ Access point deleted successfully!"
5. Point removed from table

---

### **Test 2: Login Events** (`/login-events`)

#### **A. View Events Dashboard**
✅ Navigate to http://localhost:3000/login-events
✅ Check stats cards:
   - Total Events: ~100+
   - Granted: ~95+
   - Denied: ~5+
   - AI Anomalies: 3

#### **B. Top Access Points Card**
✅ Should show ranked list:
   1. Parking Barrier (highest - rush hour traffic)
   2. Main Entrance Door
   3. Server Room Gate
   4. Others...

✅ Progress bars show relative usage
✅ Numbers show exact access count

#### **C. AI Busy Hours Card**
✅ Should show peak times:
   - 08:00-08:59 (High) 🔴
   - 09:00-09:59 (High) 🔴
   - 17:00-17:59 (High) 🔴
   - Others (Medium/Low) 🟡🟢

#### **D. AI Suggestions Card**
✅ Should show recommendations:
   - High traffic suggestions
   - Access denial patterns
   - Optimization tips

#### **E. Event Filtering**
1. Click "All" button → Shows all events
2. Click "✓ Granted" → Shows only successful accesses
3. Click "✗ Denied" → Shows only denied attempts
4. Click "⚡ Anomalies" → Shows only 3 AI-flagged events

#### **F. Time Range Filtering**
1. Select "Last 24 Hours" → Shows recent events
2. Select "Last 7 Days" → Shows all test data
3. Select "Last 30 Days" → Shows all test data

#### **G. Verify Anomaly Display**
Look for purple ⚡ badges:

**Anomaly 1: Late Night Access**
```
⚡ Jane Smith → Server Room Gate
Entry • 2:30 AM • AI ANOMALY
Anomaly Score: 89% (purple progress bar)
```

**Anomaly 2: Weekend Access**
```
⚡ David Brown → Main Entrance Door
Entry • Saturday 8:15 PM • AI ANOMALY
Anomaly Score: 72%
```

**Anomaly 3: Rapid Sequential**
```
⚡ Mike Johnson → Multiple Points
Entry • 4 accesses in 6 minutes • AI ANOMALY
```

#### **H. Event Details**
Each event should show:
- ✅ User icon with color coding
- ✅ User name → Access Point name
- ✅ Timestamp (relative: "2m ago", "1h ago")
- ✅ Event type (Entry/Exit/Denied)
- ✅ Direction indicator (if present)
- ✅ Denial reason (if denied)
- ✅ Anomaly badge and score (if anomalous)

#### **I. Export Functionality**
1. Set desired filters (e.g., "Anomalies only")
2. Click "Export CSV" button
3. Should download CSV file: `access-logs-2025-10-29T01-09-00.csv`
4. Open CSV → Verify data matches filtered view

---

### **Test 3: Access Point ↔ Login Events Relationship**

#### **Scenario: Follow a User's Journey**

1. **In Access Points page:**
   - Note "Main Entrance Door" location: "Building A - Ground Floor"
   - Note status: Active
   - Note hardware ID: AP-001

2. **In Login Events page:**
   - Find events for "Main Entrance Door"
   - See which users accessed it
   - See access times and patterns
   - Example: "John Doe → Main Entrance Door" at 9:00 AM

3. **Relationship Test:**
   - Click between both pages
   - Verify same access point appears in both
   - Verify events show actual activity at that point
   - Verify stats match (Today's Access count)

#### **Scenario: Create Access Point → Generate Event**

1. **Create new access point:**
   ```
   Name: QA Test Door
   Hardware ID: AP-QA-001
   ```

2. **Simulate access log** (via Django admin or API):
   ```python
   # In Django shell
   from access_control.models import AccessLog, AccessPoint
   from core.models import User
   from django.utils import timezone
   
   point = AccessPoint.objects.get(hardware_id='AP-QA-001')
   user = User.objects.get(username='john.doe')
   
   AccessLog.objects.create(
       organization=user.organization,
       access_point=point,
       user=user,
       event_type='entry',
       is_granted=True,
       timestamp=timezone.now(),
       direction='in'
   )
   ```

3. **Verify in Login Events:**
   - Refresh page
   - See new event: "John Doe → QA Test Door"
   - Event appears in real-time feed

---

### **Test 4: AI Features**

#### **A. Anomaly Detection Triggers**

**Test Case 1: Unusual Time**
1. Access logs show John normally works 9-5
2. Create log for John at 2 AM
3. AI should flag: "Unusual time access"
4. Appears in LoginEvents with ⚡ badge

**Test Case 2: Unusual Location**
1. Sarah only accesses Marketing floor (AP-006)
2. Create log for Sarah at Server Room (AP-002)
3. AI should flag: "Unusual location"
4. Severity: High

**Test Case 3: Rapid Sequence**
1. Create 4 access logs for Mike
2. All within 5 minutes
3. Different access points
4. AI should flag: "Rapid sequential access"

#### **B. Busy Hours Accuracy**
1. Check "AI Busy Hours" card
2. Verify 8-9 AM shows high traffic
3. Verify 5-6 PM shows high traffic
4. Verify 2-3 AM shows low/no traffic
5. Percentages should add up correctly

#### **C. Suggestions Quality**
1. Check "AI Suggestions" card
2. Should suggest:
   - Adding capacity where traffic is high
   - Reviewing permissions where denials occur
   - Security measures for anomalies

---

### **Test 5: Real-time Features**

#### **A. Auto-Refresh**
1. Open Login Events page
2. Wait 10 seconds
3. Page should auto-refresh (check network tab)
4. New events appear automatically

#### **B. Live Stats Update**
1. Note current "Total Events" count
2. Create new access log (via API or shell)
3. Wait 10 seconds for auto-refresh
4. Count should increase by 1

---

### **Test 6: Error Handling**

#### **A. Network Errors**
1. Stop backend server
2. Try to load Access Points page
3. Should show loading spinner, then error state
4. Restart server → Page recovers

#### **B. Invalid Data**
1. Try to create access point with duplicate Hardware ID
2. Should show error toast
3. Try to create with empty required fields
4. Should prevent submission

#### **C. Permission Errors**
1. Logout
2. Try to access /access-points
3. Should redirect to /login
4. Login again → Access restored

---

## 📊 Expected Results Summary

### **Access Points Page:**
```
✅ 8-9 access points visible
✅ Search works instantly
✅ Filters apply correctly
✅ Create/Edit/Delete work
✅ Lockdown toggle works
✅ Stats cards show accurate counts
✅ Table updates in real-time
✅ Emoji icons display for each type
```

### **Login Events Page:**
```
✅ 100+ events visible
✅ 3 anomalies with ⚡ badges
✅ Top 5 access points ranked
✅ Busy hours prediction shown
✅ AI suggestions displayed
✅ Filters work (All/Granted/Denied/Anomaly)
✅ Time range selector works
✅ Export CSV functions
✅ Event details complete
✅ Real-time updates every 10s
```

### **AI Features:**
```
✅ Anomalies automatically detected
✅ Confidence scores displayed (0-100%)
✅ Anomaly types identified
✅ Busy hours predicted accurately
✅ Suggestions are actionable
✅ Pattern analysis works
```

---

## 🐛 Common Issues & Solutions

### **Issue 1: No data showing**
**Solution:** Run `python manage.py shell < create_test_data.py`

### **Issue 2: 401 Unauthorized errors**
**Solution:** Check `localStorage.getItem('access_token')` exists, re-login if needed

### **Issue 3: Anomalies not showing**
**Solution:** Anomalies are created manually in test data with `is_anomaly=True`
For real AI detection, access logs need historical pattern (5+ previous accesses)

### **Issue 4: Stats showing 0**
**Solution:** Ensure organization matches between user and test data

### **Issue 5: Export CSV empty**
**Solution:** Apply filters first, ensure filtered results exist

---

## 🎯 Success Criteria

All tests pass if:
- ✅ All CRUD operations work without errors
- ✅ Real-time updates happen automatically
- ✅ AI anomalies display with badges and scores
- ✅ Filters and search work instantly
- ✅ Relationship between Access Points and Events is clear
- ✅ Export produces valid CSV
- ✅ UI is responsive and animations smooth
- ✅ Error messages are helpful
- ✅ No console errors
- ✅ Data persists across page refreshes

---

## 📝 Test Credentials

```
Username: john.doe    | Password: Test123!
Username: jane.smith  | Password: Test123!
Username: mike.johnson| Password: Test123!
Username: sarah.williams| Password: Test123!
Username: david.brown | Password: Test123!
```

**Test as different users to see personalized behavioral profiles!**

---

## 🚀 Quick Test Checklist

```
□ Run create_test_data.py
□ Login with test credentials
□ Navigate to /access-points
□ Verify 8 access points show
□ Create new access point
□ Edit existing access point
□ Toggle lockdown
□ Delete access point
□ Navigate to /login-events
□ Verify events display
□ Check anomalies have ⚡ badges
□ Test all filters
□ Test time range selector
□ Export CSV
□ Verify Top Access Points card
□ Verify AI Busy Hours card
□ Verify AI Suggestions card
□ Test search functionality
□ Wait 10s for auto-refresh
□ Check relationship between pages
```

**If all boxes checked ✅ = System works perfectly!**
