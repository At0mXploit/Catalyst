from discord.ext import commands
from utils.data_handler import load_data, save_data
from utils.helpers import today_str, clean_old_leaves, is_after_11_am

class LeaveCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def leave(self, ctx):
        user_id = str(ctx.author.id)
        today = today_str()
        data = load_data()

        if user_id not in data:
            data[user_id] = {
                "daily": {},
                "weekly": {},
                "monthly": {},
                "fine": 0,
                "leaves": []
            }

        if is_after_11_am():
            data[user_id]["fine"] += 120
            save_data(data)
            await ctx.send(f"{ctx.author.mention} Leave request rejected. Leave must be taken before 11 AM. Fine Rs.120 added. Total Fine: Rs.{data[user_id]['fine']}")
            return

        leaves = clean_old_leaves(data[user_id].get("leaves", []))

        if today in leaves:
            await ctx.send(f"{ctx.author.mention} Leave already recorded for today.")
            return

        if len(leaves) >= 7:
            await ctx.send(f"{ctx.author.mention} Leave denied. You have already used 7 leaves in the last 90 days.")
            return

        leaves.append(today)
        data[user_id]["leaves"] = leaves
        save_data(data)

        await ctx.send(f"{ctx.author.mention} Leave recorded for {today}. You have used {len(leaves)}/7 leaves in the last 90 days.")

async def setup(bot):
    await bot.add_cog(LeaveCog(bot))

