from typing import Optional
import disnake as discord
from disnake.ui import View, TextInput
from disnake import Embed, ButtonStyle, Button, TextInputStyle
from disnake.ext import commands
import os
import json
from .economy_basics import EconomyBasics
import asyncio
from typing import List
import re

class Items(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("item cog loaded")
    
    class NewItem(View):
        def __init__(self, *, timeout: float = 180, client: commands.Bot) -> None:
            super().__init__(timeout=timeout)
            self.client = client

        @discord.ui.button(label="Start", style=ButtonStyle.blurple)
        async def receive(self, button: Button, inter: discord.MessageInteraction):
            await inter.response.send_modal(
                title="Create Item",
                custom_id="create_item",
                components=[
                    TextInput(
                        label="Name",
                        placeholder="Only use alphanumeric characters and spaces",
                        custom_id="name",
                        style=TextInputStyle.short,
                        min_length=1,
                        max_length=50,
                    ),
                    TextInput(
                        label="Price",
                        placeholder="69.42",
                        custom_id="price",
                        style=TextInputStyle.short,
                        min_length=1,
                        max_length=25
                    ),
                    TextInput(
                        label="Description",
                        placeholder="This is one of the items of all time.",
                        custom_id="description",
                        style=TextInputStyle.short,
                        min_length=1,
                        max_length=100
                    ),
                    TextInput(
                        label="Stock",
                        placeholder="Leave empty if there's unlimited stock",
                        custom_id="stock",
                        style=TextInputStyle.short,
                        min_length=1,
                        max_length=25,
                        required=False
                    ),
                    TextInput(
                        label="Wallet",
                        placeholder="Use if you have a wallet for your company",
                        custom_id="wallet",
                        style=TextInputStyle.short,
                        min_length=1,
                        max_length=100,
                        required=False
                    )
                ],
            )

            try:
                modal_inter: discord.ModalInteraction = await self.client.wait_for(
                    "modal_submit",
                    check=lambda i: i.custom_id == "create_item" and i.author.id == inter.author.id,
                    timeout=1000,
                )
            except asyncio.TimeoutError:
                return

            name = modal_inter.text_values["name"]
            price_ = modal_inter.text_values["price"]
            description = modal_inter.text_values["description"]
            stock_ = modal_inter.text_values["stock"]
            wallet = modal_inter.text_values["wallet"]

            # make sure the item doesn't already exist
            name = re.sub("[^a-zA-Z0-9 ]", "", name) # only alphanumeric characters and spaces allowed
            with open(f"data/shop.json", "r") as f:
                pain: dict = json.load(f)
            
            if name in pain.keys():
                embed = Embed(title="Error",
                              description=f"Item `{name}` already exists.",
                              color=discord.Color(0xff4865))
                await modal_inter.response.send_message(embed=embed)
                return

            # make sure things the price and stock are valid
            price = 0
            stock = 0
            try:
                price = float(price_)
                if price < 0.01:
                    raise "bruh"
                if (stock_ == ""):
                    stock = -1
                else:
                    stock = int(stock_)
            except:
                embed = Embed(title="Error",
                              description="Invalid price or stock. Are you sure these are valid numbers?",
                              color=discord.Color(0xff4865))
                await modal_inter.response.send_message(embed=embed)
                return

            # make sure the wallet exists and stuff
            if wallet != "":
                bruh = {}
                with open(f"data/money/{modal_inter.author.id}.json", "r") as f:
                    bruh = json.load(f)
                
                if not wallet in bruh["wallets"]:
                    embed = Embed(title="Error",
                                description=f"Wallet `{wallet}` not found. (remember to leave it empty for the cash wallet)",
                                color=discord.Color(0xff4865))
                    await modal_inter.response.send_message(embed=embed)
                    return
            else:
                wallet = ""

            stock_but_the_user_sees_it = ""
            if stock == -1:
                stock_but_the_user_sees_it = "unlimited"
            else:
                stock_but_the_user_sees_it = f"{stock:,}"
            
            wallet_but_the_user_sees_it = ""
            if wallet == "":
                wallet_but_the_user_sees_it = "Cash"
            else:
                wallet_but_the_user_sees_it = wallet

            # now we actually add the item :)
            with open(f"data/shop.json", "r+") as f:
                pain = json.load(f)
                pain.update({
                    name: {
                        "author": modal_inter.author.id,
                        "price": price,
                        "description": description,
                        "stock": stock,
                        "wallet": wallet,
                        "purchases": 0
                    }
                })
                f.seek(0)
                f.write(json.dumps(pain))
                f.truncate()

            embed = Embed(description=f"Successfully created item `{name}`", color=discord.Color(0x3eba49))
            embed.set_author(name=modal_inter.author.display_name, icon_url=modal_inter.author.display_avatar.url)
            embed.add_field(name="Price", value=f"£{price:,.2f}", inline=True)
            embed.add_field(name="Description", value=description, inline=True)
            embed.add_field(name="Stock", value=stock_but_the_user_sees_it, inline=True)
            embed.add_field(name="Wallet", value=wallet_but_the_user_sees_it, inline=True)
            await modal_inter.response.send_message(embed=embed)

    @commands.command(aliases=["create-item", "add-item", "add_item", "new-item", "new_item"])
    async def create_item(self, ctx: commands.Context):
        EconomyBasics.setup_user(ctx.author.id)
        embed = Embed(color=0x008cff, description="You will answer a form to create the store item. Press the button below to continue.")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed, view=self.NewItem(client=self.client))
    


    class EditItem(View):
        def __init__(self, *, timeout: float = 180, client: commands.Bot, name: str) -> None:
            super().__init__(timeout=timeout)
            self.client = client
            self.name = name

        @discord.ui.button(label="Start", style=ButtonStyle.blurple)
        async def receive(self, button: Button, inter: discord.MessageInteraction):
            await inter.response.send_modal(
                title="Edit Item",
                custom_id="edit_item",
                components=[
                    TextInput(
                        label="Price",
                        placeholder="69.42",
                        custom_id="price",
                        style=TextInputStyle.short,
                        min_length=1,
                        max_length=25,
                        required=False
                    ),
                    TextInput(
                        label="Description",
                        placeholder="This is one of the items of all time.",
                        custom_id="description",
                        style=TextInputStyle.short,
                        min_length=1,
                        max_length=100,
                        required=False
                    ),
                    TextInput(
                        label="Stock",
                        placeholder="Leave empty if there's unlimited stock",
                        custom_id="stock",
                        style=TextInputStyle.short,
                        min_length=1,
                        max_length=25,
                        required=False
                    ),
                    TextInput(
                        label="Wallet",
                        placeholder="Use if you have a wallet for your company",
                        custom_id="wallet",
                        style=TextInputStyle.short,
                        min_length=1,
                        max_length=100,
                        required=False
                    )
                ],
            )

            try:
                modal_inter: discord.ModalInteraction = await self.client.wait_for(
                    "modal_submit",
                    check=lambda i: i.custom_id == "edit_item" and i.author.id == inter.author.id,
                    timeout=1000,
                )
            except asyncio.TimeoutError:
                return

            price_ = modal_inter.text_values["price"]
            description = modal_inter.text_values["description"]
            stock_ = modal_inter.text_values["stock"]
            wallet = modal_inter.text_values["wallet"]

            # make sure things the price and stock are valid
            price = 0
            stock = 0
            try:
                if price_ == "":
                    price = -1
                else:
                    price = float(price_)
                    if price < 0.01:
                        raise "bruh"

                if stock_ == "":
                    stock = -1
                else:
                    stock = int(stock_)
            except:
                embed = Embed(title="Error",
                              description="Invalid price or stock. Are you sure these are valid numbers?",
                              color=discord.Color(0xff4865))
                await modal_inter.response.send_message(embed=embed)
                return

            # make sure the wallet exists and stuff
            if wallet != "":
                bruh = {}
                with open(f"data/money/{modal_inter.author.id}.json", "r") as f:
                    bruh = json.load(f)
                
                if not wallet in bruh["wallets"]:
                    embed = Embed(title="Error",
                                description=f"Wallet `{wallet}` not found. (remember to leave it empty for the cash wallet)",
                                color=discord.Color(0xff4865))
                    await modal_inter.response.send_message(embed=embed)
                    return
            else:
                wallet = ""
            
            pain = {}
            with open(f"data/shop.json", "r") as f:
                pain = json.load(f)

            if pain[self.name]["author"] != modal_inter.author.id:
                embed = Embed(title="Error",
                            description=f"You're not the author lol",
                            color=discord.Color(0xff4865))
                await modal_inter.response.send_message(embed=embed)
                return

            # now we actually edit the item :)
            with open(f"data/shop.json", "w") as f:
                if description != "":
                    pain[self.name]["description"] = description
                if price != -1:
                    pain[self.name]["price"] = price
                if stock != -1:
                    pain[self.name]["stock"] = stock
                if wallet != "":
                    pain[self.name]["wallet"] = wallet
                json.dump(pain, f)

            embed = Embed(description=f"Successfully edited item `{self.name}`", color=discord.Color(0x3eba49))
            embed.set_author(name=modal_inter.author.display_name, icon_url=modal_inter.author.display_avatar.url)
            await modal_inter.response.send_message(embed=embed)

    @commands.command(aliases=["edit-item"])
    async def edit_item(self, ctx: commands.Context, *, name: str):
        EconomyBasics.setup_user(ctx.author.id)

        pain = {}
        with open("data/shop.json", "r") as f:
            pain = json.load(f)
        
        if not name in pain:
            embed = Embed(title="Error",
                          description=f"Item `{name}` not found.",
                          color=discord.Color(0xff4865))
            await ctx.send(embed=embed)
        else:
            embed = Embed(color=0x008cff,
                          description="You will answer a form to edit the item. Leave empty anything you don't want to change. Press the button below to continue.\n\nNOTE: The name can't be changed due to technical limitations.")
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed, view=self.EditItem(client=self.client, name=name))
    


    @commands.command(aliases=["remove-item", "delete-item", "remove_item"])
    async def delete_item(self, ctx, *, item):
        EconomyBasics.setup_user(ctx.author.id)

        pain = {}
        with open(f"data/shop.json", "r") as f:
            pain = json.load(f)
        
        # find item
        if not item in pain:
            embed = Embed(title="Error", description=f"Item `{item}` not found.", 
                            color=discord.Color(0xff4865))
            await ctx.send(embed=embed)
        else:
            if ctx.author.id == pain[item]["author"]:
                # we need to ask the user to confirm cuz yes
                embed = Embed(description=f"Are you sure you want to delete {item}? Keep in mind that some users might still own this item.\n\nSend \"y\" to confirm.",
                            color=discord.Color(0xff4865))
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
                yes = await ctx.send(embed=embed)

                def check(message):
                    return message.author == ctx.author and str(message.content) == "y"

                try:
                    reply = await self.client.wait_for('message', timeout=10.0, check=check)
                except asyncio.TimeoutError:
                    await yes.edit(content="Operation cancelled.", embed=None)
                else:
                    del pain[item]
                    with open(f"data/shop.json", "w") as f:
                        json.dump(pain, f)

                    await ctx.send(f"{item} is now gone.")
            else:
                embed = Embed(title="Error", description=f"<@{pain[item]['author']}> created this item, and this person is not you!", 
                              color=discord.Color(0xff4865))
                await ctx.send(embed=embed)
    


    @commands.command(aliases=["item-info"])
    async def item_info(self, ctx: commands.Context, *, item: str):
        pain = {}
        with open(f"data/shop.json", "r") as f:
            pain = json.load(f)
        
        # find item
        if not item in pain:
            embed = Embed(title="Error", description=f"Item `{item}` not found.", 
                            color=discord.Color(0xff4865))
            await ctx.send(embed=embed)
        else:
            stock_but_the_user_sees_it = ""
            if pain[item]["stock"] == -1:
                stock_but_the_user_sees_it = "unlimited"
            else:
                stock_but_the_user_sees_it = f"{pain[item]['stock']:,.2f}"
            
            wallet_but_the_user_sees_it = ""
            if pain[item]["wallet"] == "":
                wallet_but_the_user_sees_it = "Cash"
            else:
                wallet_but_the_user_sees_it = pain[item]["wallet"]

            embed = Embed(title=item, color=discord.Color(0x008cff))
            embed.add_field(name="Author", value=f"<@{pain[item]['author']}>", inline=True)
            embed.add_field(name="Price", value=f"£{pain[item]['price']:,.2f}", inline=True)
            embed.add_field(name="Description", value=pain[item]['description'], inline=True)
            embed.add_field(name="Stock", value=stock_but_the_user_sees_it, inline=True)
            embed.add_field(name="Wallet", value=wallet_but_the_user_sees_it, inline=True)
            embed.add_field(name="Purchases", value=pain[item]["purchases"], inline=True)
            await ctx.send(embed=embed)
    


    @commands.command(aliases=["purchase", "get", "buy-item"])
    async def buy(self, ctx: commands.Context, item: str, amount: int = 1):
        EconomyBasics.setup_user(ctx.author.id)

        if amount < 0:
            embed = Embed(title="Error", description=f"That's very wrong.", 
                            color=discord.Color(0xff4865))
            await ctx.send(embed=embed)
            return

        # does the item exist?
        pain = {}
        with open(f"data/shop.json", "r") as f:
            pain = json.load(f)
        
        if not item in pain:
            embed = Embed(title="Error", description=f"Item `{item}` not found.\n (If the name has spaces then put it in quotes, example: `l.buy \"cool item\"`)", 
                            color=discord.Color(0xff4865))
            await ctx.send(embed=embed)
            return

        # make sure there's enough stock
        if not pain[item]["stock"] == -1:
            if amount > pain[item]["stock"]:
                embed = Embed(title="Error", description=f"The stock available for this item is only {pain[item]['stock']:,}", 
                              color=discord.Color(0xff4865))
                await ctx.send(embed=embed)
                return

        # make sure the payment info is valid and stuff
        seller = {}
        
        try:
            with open(f"data/money/{pain[item]['author']}.json", "r") as f:
                seller = json.load(f)
            if pain[item]["wallet"] != "":
                if pain[item]["wallet"] not in seller["wallets"]:
                    raise "bruh"
        except:
            embed = Embed(title="Error", description="Payment info from the seller seems incorrect.",
                          color=discord.Color(0xff4865))
            await ctx.send(embed=embed)
            return

        # make sure the user can actually afford this item
        price = pain[item]["price"] * amount
        buyer = {}
        with open(f"data/money/{ctx.author.id}.json", "r") as f:
            buyer = json.load(f)
        
        if price > buyer["money"]:
            embed = Embed(title="Error", description="Not enough money in cash!",
                          color=discord.Color(0xff4865))
            await ctx.send(embed=embed)
            return
        
        # ok everything is right, we can actually buy the product now
        # first update the moneys
        if pain[item]["wallet"] != "":
            seller["wallets"][pain[item]["wallet"]] += price
        else:
            seller["money"] += price

        seller["total"] += price
        buyer["money"] -= price
        buyer["total"] -= price

        with open(f"data/money/{pain[item]['author']}.json", "w") as f:
            json.dump(seller, f)
        with open(f"data/money/{ctx.author.id}.json", "w") as f:
            json.dump(buyer, f)
        
        EconomyBasics.update_leaderboard(pain[item]["author"])
        EconomyBasics.update_leaderboard(ctx.author.id)

        # now add the item to the user's inventory
        with open(f"data/items/{ctx.author.id}.json", "r+") as f:
            bruh = json.load(f)
            if item not in bruh:
                bruh.update({item: amount})
            else:
                bruh[item] += amount
            f.seek(0)
            f.write(json.dumps(bruh))
            f.truncate()
        
        # update the stock and number of purchases (required for calculating inflation)
        # -1 means unlimited stock
        with open(f"data/shop.json", "r+") as f:
            bruh = json.load(f)
            if pain[item]["stock"] != -1:
                bruh[item]["stock"] -= amount
            bruh[item]["purchases"] += amount
            f.seek(0)
            f.write(json.dumps(bruh))
            f.truncate()
        
        embed = Embed(description=f"Successfully bought {amount:,} {item}s", color=discord.Color(0x3eba49))
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)



    class InventoryView(View):
        def __init__(self, embeds: List[Embed]):
            super().__init__(timeout=None)
            self.embeds = embeds
            self.index = 0

            for i, embed in enumerate(self.embeds):
                embed.set_footer(text=f"Page {i + 1} of {len(self.embeds)}")

            self._update_state()

        def _update_state(self) -> None:
            self.first_page.disabled = self.prev_page.disabled = self.index == 0
            self.last_page.disabled = self.next_page.disabled = self.index == len(self.embeds) - 1
        
        @discord.ui.button(emoji="◀", style=ButtonStyle.blurple)
        async def prev_page(self, button: Button, inter: discord.MessageInteraction):
            self.index -= 1
            self._update_state()

            await inter.response.edit_message(embed=self.embeds[self.index], view=self)

        @discord.ui.button(emoji="▶", style=ButtonStyle.blurple)
        async def next_page(self, button: Button, inter: discord.MessageInteraction):
            self.index += 1
            self._update_state()

            await inter.response.edit_message(embed=self.embeds[self.index], view=self)

        @discord.ui.button(emoji="⏪", style=ButtonStyle.secondary)
        async def first_page(self, button: Button, inter: discord.MessageInteraction):
            self.index = 0
            self._update_state()

            await inter.response.edit_message(embed=self.embeds[self.index], view=self)

        @discord.ui.button(emoji="⏩", style=ButtonStyle.secondary)
        async def last_page(self, button: Button, inter: discord.MessageInteraction):
            self.index = len(self.embeds) - 1
            self._update_state()

            await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @commands.command(aliases=["inv"])
    async def inventory(self, ctx: commands.Context, user: discord.User = None):
        if user == None:
            user = ctx.author

        EconomyBasics.setup_user(user.id)

        inv = {}
        with open(f"data/items/{user.id}.json", "r") as f:
            inv = json.load(f)
        
        # split the leaderboard so pages work :)
        chunks = []
        new_dict = {}
        for k, v in inv.items():
            if v > 0:
                if len(new_dict) < 10:
                    new_dict[k] = v
                else:
                    chunks.append(new_dict)
                    new_dict = {k: v}
        chunks.append(new_dict)

        # make cool embeds for the pages
        embeds = []
        bruh = 0
        for chunk in chunks:
            embed = Embed(color=0x008cff, description="")
            embed.set_author(name=user.display_name, icon_url=user.display_avatar.url)
            for item, amount in chunk.items():
                bruh += 1
                embed.description += f"**{bruh}.** `{item}`: {amount:,}\n"
            embeds.append(embed)

        # Sends first embed with the buttons, it also passes the embeds list into the View class.
        await ctx.send(embed=embeds[0], view=self.InventoryView(embeds))
    


    @commands.command(aliases=["give-item"])
    async def give_item(self, ctx: commands.Context, item: str, user: discord.User, amount: int = 1):
        EconomyBasics.setup_user(ctx.author.id)
        EconomyBasics.setup_user(user.id)

        # does the author own that?
        pain = {}
        with open(f"data/items/{ctx.author.id}.json", "r") as f:
            pain = json.load(f)
        
        if not item in pain:
            embed = Embed(title="Error", description=f"Item `{item}` not found in your inventory.\n (If the name has spaces then put it in quotes, example: `l.give-item \"cool item\" @cooluser`)", 
                            color=discord.Color(0xff4865))
            await ctx.send(embed=embed)
            return

        # make sure there's enough stock
        if amount > pain[item]:
            embed = Embed(title="Error", description=f"You only own {pain[item]['stock']:,} {item}s!", 
                            color=discord.Color(0xff4865))
            await ctx.send(embed=embed)
            return

        # ok everything is right, we can actually give the item now
        with open(f"data/items/{ctx.author.id}.json", "w") as f:
            pain[item] -= amount
            json.dump(pain, f)

        with open(f"data/items/{user.id}.json", "r+") as f:
            bruh = json.load(f)
            if item not in bruh:
                bruh.update({item: amount})
            else:
                bruh[item] += amount
            f.seek(0)
            f.write(json.dumps(bruh))
            f.truncate()
        
        embed = Embed(description=f"Successfully gave {amount:,} {item}s to {user.mention}", color=discord.Color(0x3eba49))
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

def setup(client: commands.Bot):
    client.add_cog(Items(client))