# 🐞 Defect Tracker Template

This document tracks all known defects encountered during [project/system] installation, testing, and operational processes. Each defect must be traceable to the task or test where it was discovered, and if remediated, linked to a follow-up resolution task.

**System/Component:** [Name/IP/Details]  
**Specialization:** [Primary function]  
**Document ID:** [DT-XXX-XXX]  
**Version:** [X.X]

---

## 📘 Reference Documents
- [Related Document 1]
- [Related Document 2]
- [Related Document 3]

---

## 🏷️ Defect Categories

Classify defects by type to improve tracking and resolution patterns:

| Category | Description | Examples |
|----------|-------------|----------|
| **ENV** | Environment and system setup issues | [Example 1, Example 2] |
| **INSTALL** | Installation and dependency issues | [Example 1, Example 2] |
| **CONFIG** | Configuration and setup issues | [Example 1, Example 2] |
| **PERF** | Performance and resource issues | [Example 1, Example 2] |
| **API** | API server and endpoint issues | [Example 1, Example 2] |
| **TEST** | Testing and validation issues | [Example 1, Example 2] |
| **DOC** | Documentation and process issues | [Example 1, Example 2] |
| **SEC** | Security and compliance issues | [Example 1, Example 2] |
| **[CUSTOM]** | [Custom category description] | [Example 1, Example 2] |

---

## 🧾 Defect Log

| Defect ID | Category | Related Task/Test ID | Description | Severity | Status | Resolution Task | Date Reported | Owner | Business Impact |
|-----------|----------|----------------------|-------------|----------|--------|-----------------|----------------|-------|-----------------|
| [DEF-XXX] | [Category] | [Task/Test ID] | [Description] | [Severity] | [Status] | [Resolution] | [Date] | [Owner] | [Impact] |
|           |            |                      |             |          |        |                 |                |       |                 |

Legend:
- **Category**: [List of applicable categories]
- **Severity**: [Low | Medium | High | Critical | Business-Critical]
- **Status**: [Open | Investigating | Escalated | Deferred | Closed]
- **Business Impact**: [None | Low | Medium | High | Critical]

---

## 📋 Defect Guidelines

### Defect Reporting Requirements
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

### Defect Classification Rules
- **Business-Critical**: [Definition and criteria]
- **Critical**: [Definition and criteria]
- **High**: [Definition and criteria]
- **Medium**: [Definition and criteria]
- **Low**: [Definition and criteria]

### Escalation Procedures
1. **Business-Critical/Critical**: [Escalation procedure]
2. **High**: [Escalation procedure]
3. **Medium**: [Escalation procedure]
4. **Low**: [Escalation procedure]

### Documentation Requirements
- [Documentation requirement 1]
- [Documentation requirement 2]
- [Documentation requirement 3]

### Component-Specific Considerations
- **[Component 1]**: [Special considerations]
- **[Component 2]**: [Special considerations]

### Compliance Requirements
- [Compliance requirement 1]
- [Compliance requirement 2]

---

## 📊 Defect Metrics

### Key Performance Indicators
- **Mean Time to Resolution (MTTR)**: [Target times by severity]
- **[Metric 2]**: [Description and target]
- **[Metric 3]**: [Description and target]

### Reporting Schedule
- **Real-time**: [When and what to report]
- **Daily**: [When and what to report]
- **Weekly**: [When and what to report]
- **Monthly**: [When and what to report]

---

## 📝 Defect Entry Template

### Defect Information
**Defect ID:** [DEF-XXX-XXX]  
**Title:** [Brief, descriptive title]  
**Category:** [Select from categories above]  
**Severity:** [Business-Critical/Critical/High/Medium/Low]  
**Status:** [Open/Investigating/Escalated/Deferred/Closed]  
**Date Reported:** [YYYY-MM-DD]  
**Reported By:** [Name]  
**Assigned To:** [Name]  

### Related Information
**Related Task/Test ID:** [ID and description]  
**Environment:** [Environment where defect occurred]  
**Build/Version:** [Build number or version]  
**Component:** [Affected component]  

### Description
**Summary:** [Brief description of the defect]

**Detailed Description:** [Comprehensive description of the issue]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result:** [What should happen]

**Actual Result:** [What actually happened]

### Impact Assessment
**Business Impact:** [None/Low/Medium/High/Critical]  
**Impact Description:** [Detailed impact assessment]  
**Affected Users/Systems:** [Who/what is affected]  
**Workaround Available:** [Yes/No - describe if yes]  

### Technical Details
**Error Messages:** 
```
[Paste error messages here]
```

**Log Entries:**
```
[Relevant log entries]
```

**Screenshots/Evidence:** [Attach or describe]

### Resolution
**Root Cause:** [Analysis of root cause]  
**Resolution Steps:** [Steps taken to resolve]  
**Resolution Task ID:** [If applicable]  
**Date Resolved:** [YYYY-MM-DD]  
**Resolved By:** [Name]  
**Verification:** [How resolution was verified]  

### Prevention
**Prevention Measures:** [Steps to prevent recurrence]  
**Process Improvements:** [Suggested improvements]  
**Documentation Updates:** [Required documentation changes]  

---

## 🔍 Defect Analysis

### Common Defect Patterns
- [Pattern 1]: [Description and frequency]
- [Pattern 2]: [Description and frequency]

### Root Cause Analysis Summary
- [Root cause 1]: [Frequency and impact]
- [Root cause 2]: [Frequency and impact]

### Improvement Recommendations
- [Recommendation 1]
- [Recommendation 2]

---

## 📈 Defect Statistics

### Current Status Summary
- **Open**: [Count]
- **Investigating**: [Count]
- **Escalated**: [Count]
- **Deferred**: [Count]
- **Closed**: [Count]

### Severity Distribution
- **Business-Critical**: [Count]
- **Critical**: [Count]
- **High**: [Count]
- **Medium**: [Count]
- **Low**: [Count]

### Category Distribution
- **[Category 1]**: [Count]
- **[Category 2]**: [Count]

### Resolution Metrics
- **Average MTTR**: [Time]
- **Fastest Resolution**: [Time]
- **Longest Resolution**: [Time]

---

## 🔄 Version History

| Version | Date | Author | Changes | Review Status |
|---------|------|--------|---------|---------------|
| [X.X] | [YYYY-MM-DD] | [Author] | [Description] | [Status] |

---

## 📋 Template Usage Instructions

**How to use this template:**

1. **Customize the categories** to match your project/system needs
2. **Update severity definitions** based on your business requirements
3. **Configure escalation procedures** according to your organization
4. **Add defects** using the structured format provided
5. **Maintain regular updates** to status and metrics sections
6. **Review and analyze** patterns for continuous improvement

**Best Practices:**
- Log defects immediately when discovered
- Provide detailed reproduction steps
- Include relevant technical details and evidence
- Update status regularly throughout resolution process
- Conduct root cause analysis for critical defects
- Track metrics to identify improvement opportunities

**Status Management:**
- **Open**: Defect reported and awaiting assignment
- **Investigating**: Actively working on root cause analysis
- **Escalated**: Requires higher-level intervention
- **Deferred**: Not being worked on currently
- **Closed**: Resolution completed and verified

---

*This defect tracker template provides a comprehensive framework for tracking, analyzing, and resolving defects throughout the project lifecycle.*

_Last updated: [Date]_  
_Next review: [Date]_  
_Status: [Status]_
