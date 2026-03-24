# Task Steward Rules

This file is created by the setup interview (see AGENT.md -- First Run). It is never
overwritten by openclaw-config updates. Edit it directly to change your preferences.

---

## Task System

- system: asana
- workspace_gid: <your Asana workspace GID>
- project_gid: <your Asana project GID>
- ai_assignee_gid: <GID of this bot's Asana account>
- human_assignee_gid: <GID of the human's Asana account>

## Sections

- working: <section GID for in-progress tasks>
- waiting: <section GID for blocked tasks>
- review: <section GID for tasks awaiting review>
- done: <section GID for completed tasks>

## Tags

- ai_working: <tag GID>
- blocked: <tag GID>
- quality_verified: <tag GID>

## Preferences

- alert_channel: telegram
- max_new_tasks_per_run: 2
- stale_threshold_days: 5
- calendar_check_before_delivery: true
- handoff_target: human

## Completion Detection

- completion_detection: true
- completion_channels: [imessage, email]
- completion_lookback_hours: 48

## Quiet Hours

- quiet_start: "21:00"
- quiet_end: "08:00"
- timezone: America/Chicago

## Never Touch

# Add task name patterns or assignee IDs to always skip

# - pattern: "MEETING NOTES"

# - assignee_gid: <skip this person's tasks>
