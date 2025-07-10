# Task Template

## Task Information

**Task Number:** [X.X]  
**Task Title:** [Brief, descriptive title]  
**Created:** [Date]  
**Assigned To:** [Name/Team]  
**Priority:** [High/Medium/Low]  
**Estimated Duration:** [Time estimate]  

## Task Description

[Provide a clear, specific description of what needs to be accomplished. Include necessary context and scope.]

## SMART+ST Validation

| Principle | Status | Notes |
|-----------|--------|-------|
| **Specific** | ✅/❌ | [Is the task clearly defined with no ambiguity?] |
| **Measurable** | ✅/❌ | [Are success criteria clearly defined?] |
| **Achievable** | ✅/❌ | [Is the task realistic given constraints?] |
| **Relevant** | ✅/❌ | [Does this align with project goals?] |
| **Small** | ✅/❌ | [Is the scope narrow enough for single execution?] |
| **Testable** | ✅/❌ | [Can completion be verified objectively?] |

## Prerequisites

**Hard Dependencies:**
- [List tasks that must be 100% complete before this task can start]

**Soft Dependencies:**
- [List tasks that should ideally be complete but task can proceed with warnings]

**Conditional Dependencies:**
- [List tasks that depend on specific outcomes of previous tasks]

## Configuration Requirements

**Environment Variables (.env):**
```
[List required environment variables]
EXAMPLE_VAR=value
```

**Configuration Files (.json/.yaml):**
```
[List required configuration files and their purposes]
config/example.json - [Purpose]
config/example.yaml - [Purpose]
```

**External Resources:**
- [List any external dependencies, APIs, or resources needed]

## Sub-Tasks

| Sub-Task | Description | Commands/Steps | Success Criteria |
|----------|-------------|----------------|------------------|
| X.1 | [Description] | [Specific commands or steps] | [How to verify completion] |
| X.2 | [Description] | [Specific commands or steps] | [How to verify completion] |
| X.3 | [Description] | [Specific commands or steps] | [How to verify completion] |

## Success Criteria

**Primary Objectives:**
- [ ] [Specific, measurable outcome 1]
- [ ] [Specific, measurable outcome 2]
- [ ] [Specific, measurable outcome 3]

**Validation Commands:**
```bash
# Commands to verify task completion
[example: nvidia-smi]
[example: curl -X GET http://localhost:8000/health]
```

**Expected Outputs:**
```
[Show expected command outputs or screenshots]
```

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|-------------------|
| [Risk description] | [High/Medium/Low] | [High/Medium/Low] | [How to prevent/handle] |

## Rollback Procedures

**If Task Fails:**
1. [Step-by-step rollback instructions]
2. [Commands to restore previous state]
3. [Cleanup procedures]

**Rollback Validation:**
```bash
# Commands to verify rollback completion
[example commands]
```

## Task Execution Log

| Date | Action | Result | Notes |
|------|--------|--------|-------|
| [Date] | [Started/Completed/Failed] | [Outcome] | [Additional details] |

## Dependencies This Task Enables

**Next Tasks:**
- Task Y.Y: [Description]
- Task Z.Z: [Description]

**Parallel Candidates:**
- Task A.A: [Description] (can run simultaneously)

## Troubleshooting

**Common Issues:**
| Issue | Symptoms | Resolution |
|-------|----------|------------|
| [Problem description] | [How to identify] | [How to fix] |

**Debug Commands:**
```bash
# Commands to diagnose issues
[example: ps aux | grep service_name]
[example: journalctl -u service_name]
```

## Post-Completion Actions

**Documentation Updates:**
- [ ] Update task list status (change `- [ ]` to `- [x]`)
- [ ] Create result summary document: `[Task_Title]_Results.md`
- [ ] Update project documentation if needed

**Result Document Location:**
- Save to: `/project/tasks/results/[Task_Title]_Results.md`

**Notification Requirements:**
- [ ] Notify dependent task owners
- [ ] Update project status dashboard
- [ ] Communicate to stakeholders (if applicable)

## Notes

[Any additional notes, lessons learned, or future considerations]

---

**Template Version:** 1.0  
**Last Updated:** [Date]  
**Template Source:** Based on SMART+ST principles from hx-task-creation.md
