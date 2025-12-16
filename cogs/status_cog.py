from discord.ext import commands
from utils.data_handler import load_data
from utils.helpers import today_str, clean_old_leaves
import discord

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help_command(self, ctx):
        help_msg = """**Catalyst Bot Commands**

**Task Submission:**
Post tasks in respective channels (#daily-tasks, #weekly-tasks, #monthly-tasks)
Format: 
- Task 1
- Task 2
Mark completed: - ~~Task 1~~

**Commands:**
`!leave` - Request leave (must be before 11 AM)
`!mystatus` - View your personal status
`!allstatus` - View everyone's status
`!leaderboard` - View fine leaderboard
`!reporttime` - Check when next report runs
`!help` - Show this help message

**Rules:**
- Daily tasks must be set before 11 AM
- Minimum 2 daily tasks required
- Maximum 7 leaves in 90 days
- Leave must be taken before 11 AM

**Fines:**
- Failed daily task: Rs.30 each
- Failed weekly task: Rs.45 each
- Failed monthly task: Rs.60 each
- No tasks set: Rs.120
- Less than 2 daily tasks: Rs.120
- Late leave/tasks after 11 AM: Rs.120
"""
        await ctx.send(help_msg)

    @commands.command()
    async def mystatus(self, ctx):
        user_id = str(ctx.author.id)
        data = load_data()
        
        if user_id not in data:
            await ctx.send(f"{ctx.author.mention} No data found. You haven't submitted any tasks yet.")
            return
        
        info = data[user_id]
        leaves = clean_old_leaves(info.get("leaves", []))
        
        daily = info.get("daily", {})
        weekly = info.get("weekly", {})
        monthly = info.get("monthly", {})
        
        status_msg = f"**Status for {ctx.author.mention}**\n\n"
        status_msg += f"**Total Fine:** Rs.{info.get('fine', 0)}\n"
        status_msg += f"**Leaves Used:** {len(leaves)}/7 (in last 90 days)\n\n"
        
        if daily and daily.get("date") == today_str():
            status_msg += f"**Today's Tasks:** {daily['completed']}/{daily['total']} completed\n"
        else:
            status_msg += f"**Today's Tasks:** Not set\n"
        
        if weekly and weekly.get("date"):
            status_msg += f"**Weekly Tasks:** {weekly['completed']}/{weekly['total']} completed (Date: {weekly['date']})\n"
        else:
            status_msg += f"**Weekly Tasks:** Not set\n"
        
        if monthly and monthly.get("date"):
            status_msg += f"**Monthly Tasks:** {monthly['completed']}/{monthly['total']} completed (Date: {monthly['date']})\n"
        else:
            status_msg += f"**Monthly Tasks:** Not set\n"
        
        await ctx.send(status_msg)

    @commands.command()
    async def leaderboard(self, ctx):
        data = load_data()
        
        if not data:
            await ctx.send("No data available yet. Nobody has submitted tasks.")
            return
        
        sorted_users = sorted(data.items(), key=lambda x: x[1].get('fine', 0))
        
        leaderboard_msg = f"**Fine Leaderboard - {today_str()}**\n\n"
        
        for idx, (user_id, info) in enumerate(sorted_users, 1):
            try:
                user = await self.bot.fetch_user(int(user_id))
                username = user.name
            except:
                username = f"User {user_id}"
            
            fine = info.get('fine', 0)
            leaderboard_msg += f"{idx}. {username}: Rs.{fine}\n"
        
        await ctx.send(leaderboard_msg)

    @commands.command()
    async def allstatus(self, ctx):
        data = load_data()
        
        if not data:
            await ctx.send("No data available yet. Nobody has submitted tasks.")
            return
        
        status_msg = f"**All Users Status - {today_str()}**\n\n"
        
        for user_id, info in data.items():
            try:
                user = await self.bot.fetch_user(int(user_id))
                username = user.name
            except:
                username = f"User {user_id}"
            
            leaves = clean_old_leaves(info.get("leaves", []))
            daily = info.get("daily", {})
            
            status_msg += f"**{username}**\n"
            status_msg += f"Fine: Rs.{info.get('fine', 0)} | Leaves: {len(leaves)}/7\n"
            
            if today_str() in leaves:
                status_msg += f"Today: On Leave\n"
            elif daily and daily.get("date") == today_str():
                status_msg += f"Today: {daily['completed']}/{daily['total']} tasks completed\n"
            else:
                status_msg += f"Today: No tasks set\n"
            
            status_msg += "\n"
        
        await ctx.send(status_msg)

    @commands.command()
    async def reporttime(self, ctx):
        from utils.helpers import now_np, NEPAL_TZ
        from datetime import time, datetime
        
        current_time = now_np()
        report_time = datetime.now(NEPAL_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
        
        if current_time.hour >= 0:
            from datetime import timedelta
            report_time += timedelta(days=1)
        
        time_until = report_time - current_time
        hours = int(time_until.total_seconds() // 3600)
        minutes = int((time_until.total_seconds() % 3600) // 60)
        
        msg = f"**Report Schedule**\n\n"
        msg += f"Current Nepal Time: {current_time.strftime('%I:%M %p')}\n"
        msg += f"Next Daily Report: 12:00 AM (in {hours}h {minutes}m)\n"
        msg += f"Weekly Report: Every Sunday 12:00 AM\n"
        msg += f"Monthly Report: 1st of every month 12:00 AM\n"
        
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(StatusCog(bot))

