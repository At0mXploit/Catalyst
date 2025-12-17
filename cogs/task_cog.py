from discord.ext import commands, tasks
from utils.data_handler import load_data, save_data
from utils.helpers import parse_tasks, today_str, is_after_11_am, validate_task_format

TASK_CHANNELS = {
    "daily-goals": "daily",
    "weekly-goals": "weekly",
    "monthly-goals": "monthly"
}


def extract_active_tasks(content: str):
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    active = []

    for line in lines:
        if line.startswith("- ") or line.startswith("* "):
            if not (line.startswith("- ~~") or line.startswith("* ~~")):
                active.append(line)

    return active


class TasksCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_task_updates.start()

    def cog_unload(self):
        self.check_task_updates.cancel()

    @tasks.loop(seconds=30)
    async def check_task_updates(self):
        data = load_data()

        for user_id, info in data.items():
            for task_type in ["daily", "weekly", "monthly"]:
                task_data = info.get(task_type, {})
                message_id = task_data.get("message_id")

                if not message_id or task_data.get("date") != today_str():
                    continue

                channel_name = f"{task_type}-goals"
                channel = None

                for ch in self.bot.get_all_channels():
                    if ch.name == channel_name:
                        channel = ch
                        break

                if not channel:
                    continue

                try:
                    message = await channel.fetch_message(int(message_id))
                    total, completed = parse_tasks(message.content)
                    failed = total - completed

                    if completed != task_data.get("completed"):
                        task_data["completed"] = completed
                        task_data["failed"] = failed
                        data[user_id][task_type] = task_data
                        save_data(data)

                        try:
                            await message.add_reaction("✅")
                        except:
                            pass
                except:
                    pass

    @check_task_updates.before_loop
    async def before_check_task_updates(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        await self.process_task_message(message, is_edit=False)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return

        channel_name = after.channel.name
        if channel_name not in TASK_CHANNELS:
            return

        before_tasks = extract_active_tasks(before.content)
        after_tasks = extract_active_tasks(after.content)

        if len(after_tasks) <= len(before_tasks):
            return

        await self.process_task_message(after, is_edit=True)

    async def process_task_message(self, message, is_edit=False):
        if message.author.bot:
            return

        channel_name = message.channel.name
        if channel_name not in TASK_CHANNELS:
            return

        content = message.content.strip()
        if content.startswith("!"):
            return

        is_valid, error_msg = validate_task_format(content)
        if not is_valid:
            await message.channel.send(
                f"{message.author.mention} {error_msg}\n\n"
                "- Task name\n"
                "- ~~Completed task~~"
            )
            return

        task_type = TASK_CHANNELS[channel_name]
        user_id = str(message.author.id)
        data = load_data()

        if user_id not in data:
            data[user_id] = {
                "daily": {},
                "weekly": {},
                "monthly": {},
                "fine": 0,
                "leaves": []
            }

        if today_str() in data[user_id].get("leaves", []):
            return

        if task_type == "daily" and is_after_11_am():
            data[user_id]["fine"] += 120
            save_data(data)
            await message.channel.send(
                f"{message.author.mention} Daily tasks after 11 AM are not accepted. "
                f"Fine Rs.120 added. Total Fine: Rs.{data[user_id]['fine']}"
            )
            return

        total, completed = parse_tasks(message.content)
        failed = total - completed

        if task_type == "daily" and total < 2:
            await message.channel.send(
                f"{message.author.mention} Minimum 2 daily tasks required. "
                f"You set {total} task(s). Fine Rs.120 may apply."
            )

        if data[user_id][task_type].get("date") != today_str() and not is_edit:
            await message.channel.send(
                f"{message.author.mention} Tasks recorded: {completed}/{total} completed."
            )

        data[user_id][task_type] = {
            "total": total,
            "completed": completed,
            "failed": failed,
            "date": today_str(),
            "message_id": str(message.id)
        }

        save_data(data)

        if is_edit:
            try:
                await message.add_reaction("✅")
            except:
                pass


async def setup(bot):
    await bot.add_cog(TasksCog(bot))
