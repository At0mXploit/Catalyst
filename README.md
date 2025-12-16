# Catalyst
Catalyst Bot is a Discord bot for task management, leave tracking, and fine calculation.  
It helps teams track **daily, weekly, and monthly goals**, automatically calculates fines for missed tasks, and provides reports.

<img width="422" height="558" alt="2025-12-16_20-01" src="https://github.com/user-attachments/assets/829562e4-d4a9-4af6-a3ff-b5490a47c911" />
## Stack Used
**GCD** (GPT, Claude, Deepseek) whichever premium ended jumped to next one.
## Features
- **Daily, Weekly, and Monthly Task Tracking**
  - Users submit tasks in dedicated channels.
  - Mark tasks completed using `~~Task~~`.
- **Leave Management**
  - Users can request leaves with `!leave`.
  - Leaves are limited to 7 per 90 days.
  - Late leave requests incur fines.
- **Fine System**
  - Missed tasks incur fines:
    - Daily task: Rs.30 each
    - Weekly task: Rs.45 each
    - Monthly task: Rs.60 each
    - No tasks: Rs.120
    - Less than 2 daily tasks: Rs.120
    - Late submission after 11 AM: Rs.120
  - Fines are accumulated per user.
- **Automated Reports**
  - Daily, weekly, and monthly reports in designated channels.
  - Fines are reset automatically at the end of the week/month.
- **Status Commands**
  - `!mystatus` - view personal task and fine status.
  - `!allstatus` - view everyone's status.
  - `!leaderboard` - view fine leaderboard.
  - `!reporttime` - check next report schedule.
  - `!help` - display command guide. 
## Setup Instructions
```bash
pip install -r requirements.txt
export DISCORD_TOKEN="your-bot-token"
python3 bot.py
```

Data are logged in `data.json`.

Make sure your server has the following channels:

`daily-goals` -	Daily task submission

`weekly-goals` - Weekly task submission

`monthly-goals`	- Monthly task submission

Rename in `cogs/task_cog.py` and `cogs/reports_cog.py` if needed. 
## Deployment

Deploy using Railway and add env variables there.

> This shit might have too many loopholes or bugs if you find any just fucking add some PR for me.
---

