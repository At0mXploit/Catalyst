from discord.ext import commands, tasks
from datetime import time
from utils.data_handler import load_data, save_data
from utils.helpers import today_str, clean_old_leaves, NEPAL_TZ

FINE = {
    "daily": 30,
    "weekly": 45,
    "monthly": 60,
    "no_tasks": 120,
    "min_daily": 120
}

class ReportsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_report.start()
        self.weekly_report.start()
        self.monthly_report.start()

    def cog_unload(self):
        self.daily_report.cancel()
        self.weekly_report.cancel()
        self.monthly_report.cancel()

    def get_channel(self, name):
        for ch in self.bot.get_all_channels():
            if ch.name == name:
                return ch
        return None

    @tasks.loop(time=time(hour=0, minute=0, tzinfo=NEPAL_TZ))
    async def daily_report(self):
        data = load_data()
        channel = self.get_channel("daily-goals")
        if not channel:
            return

        report = f"**Daily Report - {today_str()}**\n\n"

        for user_id, info in data.items():
            leaves = clean_old_leaves(info.get("leaves", []))
            info["leaves"] = leaves
            daily = info.get("daily", {})

            if today_str() in leaves:
                report += f"<@{user_id}> was on leave.\n"
                info["daily"] = {}
                continue

            if not daily or daily.get("date") != today_str():
                info["fine"] += FINE["no_tasks"]
                report += f"<@{user_id}> did not set tasks. Fine: Rs.{FINE['no_tasks']}. Total Fine: Rs.{info['fine']}\n"
            else:
                total_fine = 0
                
                if daily["total"] < 2:
                    info["fine"] += FINE["min_daily"]
                    total_fine += FINE["min_daily"]
                    report += f"<@{user_id}> set less than 2 tasks. Fine: Rs.{FINE['min_daily']}. "

                failed = daily["failed"]
                if failed > 0:
                    task_fine = failed * FINE["daily"]
                    info["fine"] += task_fine
                    total_fine += task_fine
                    report += f"Failed {failed} task(s). Fine: Rs.{task_fine}. "
                
                if total_fine > 0:
                    report += f"Total Fine: Rs.{info['fine']}\n"
                else:
                    report += f"<@{user_id}> completed all tasks.\n"

            info["daily"] = {}

        save_data(data)
        await channel.send(report)

    @tasks.loop(time=time(hour=0, minute=0, tzinfo=NEPAL_TZ))
    async def weekly_report(self):
        data = load_data()
        channel = self.get_channel("weekly-goals")
        if not channel:
            return

        report = f"**Weekly Report - {today_str()}**\n\n"
        has_data = False

        for user_id, info in data.items():
            weekly = info.get("weekly", {})
            if weekly and weekly.get("date"):
                has_data = True
                failed = weekly["failed"]
                if failed > 0:
                    fine = failed * FINE["weekly"]
                    info["fine"] += fine
                    report += f"<@{user_id}> failed {failed} weekly task(s). Fine: Rs.{fine}. Total Fine: Rs.{info['fine']}\n"
                else:
                    report += f"<@{user_id}> completed all weekly tasks.\n"
                info["weekly"] = {}

        if not has_data:
            report += "No weekly tasks were set this week.\n"

        save_data(data)
        await channel.send(report)

    @tasks.loop(time=time(hour=0, minute=0, tzinfo=NEPAL_TZ))
    async def monthly_report(self):
        data = load_data()
        channel = self.get_channel("monthly-goals")
        if not channel:
            return

        report = f"**Monthly Report - {today_str()}**\n\n"
        has_data = False

        for user_id, info in data.items():
            monthly = info.get("monthly", {})
            if monthly and monthly.get("date"):
                has_data = True
                failed = monthly["failed"]
                if failed > 0:
                    fine = failed * FINE["monthly"]
                    info["fine"] += fine
                    report += f"<@{user_id}> failed {failed} monthly task(s). Fine: Rs.{fine}. Total Fine: Rs.{info['fine']}\n"
                else:
                    report += f"<@{user_id}> completed all monthly tasks.\n"
                info["monthly"] = {}

        if not has_data:
            report += "No monthly tasks were set this month.\n"

        save_data(data)
        await channel.send(report)

    @daily_report.before_loop
    async def before_daily_report(self):
        await self.bot.wait_until_ready()

    @weekly_report.before_loop
    async def before_weekly_report(self):
        await self.bot.wait_until_ready()

    @monthly_report.before_loop
    async def before_monthly_report(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(ReportsCog(bot))

