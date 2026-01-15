import json
import discord
import aiohttp
from discord import app_commands, ui

def departure_arrival_board_commands(bot):
    @bot.tree.command(name="departureboardnew", description="Show departures at an airport")
    @app_commands.describe(icao_code = "4-letter ICAO code")
    async def departureboard(interaction: discord.Interaction, icao_code: str):
        icao_code = icao_code.upper()
        vatsimdata = await fetch_vatsim_api()
        airportname_database = await fetch_airportname_database()

        found_pilots_list = []
        for pilot in vatsimdata["pilots"]:
            pilot_flight_plan = pilot.get("flight_plan", None)
            if pilot_flight_plan:
                if pilot_flight_plan["departure"] == icao_code:
                    found_pilots_list.append(pilot)
                else:
                    pass
            else:
                pass
        if found_pilots_list:
            view = View(found_pilots_list, airportname_database, icao_code, True)
            await interaction.response.send_message(view=view)
        else:
            failure_embed = discord.Embed(title=f"No departures at {icao_code}")
            await interaction.response.send_message(embed=failure_embed)

    @bot.tree.command(name="arrivalboardnew", description="Show arrivals at an airport")
    @app_commands.describe(icao_code = "4-letter ICAO code")
    async def departureboard(interaction: discord.Interaction, icao_code: str):
        icao_code = icao_code.upper()
        vatsimdata = await fetch_vatsim_api()
        airportname_database = await fetch_airportname_database()

        found_pilots_list = []
        for pilot in vatsimdata["pilots"]:
            pilot_flight_plan = pilot.get("flight_plan", None)
            if pilot_flight_plan:
                if pilot_flight_plan["arrival"] == icao_code:
                    found_pilots_list.append(pilot)
                else:
                    pass
            else:
                pass
        if found_pilots_list:
            view = View(found_pilots_list, airportname_database, icao_code, False)
            await interaction.response.send_message(view=view)
        else:
            failure_embed = discord.Embed(title=f"No Arrivals at {icao_code}")
            await interaction.response.send_message(embed=failure_embed)

    async def fetch_vatsim_api():
        async with aiohttp.ClientSession() as session:
            async with session.get("https://data.vatsim.net/v3/vatsim-data.json") as response:
                vatsim_data = await response.json()
        return vatsim_data
    
    async def fetch_airportname_database():
        async with aiohttp.ClientSession() as session:
            async with session.get("https://raw.githubusercontent.com/mwgg/Airports/refs/heads/master/airports.json") as response:
                airportname_database = await response.json(content_type=None)
        return airportname_database
    
    class View(ui.LayoutView):
        def __init__(self, found_pilots, airportname_database, icaocode, is_for_departureBoard):
            super().__init__()

            self.page_count = 0 # this is for previous and next buttons

            self.pilot_list = found_pilots
            self.is_for_departureBoard = is_for_departureBoard
            self.icao_code = icaocode.upper()
            self.airportname_database = airportname_database

            pilot_counter = 0

            self.container1 = ui.Container()
            if self.is_for_departureBoard == True:
                header = ui.TextDisplay(f"# {self.airportname_database[self.icao_code]["name"]} ({self.icao_code}) Departures")
            else:
                header = ui.TextDisplay(f"# {self.airportname_database[self.icao_code]["name"]} ({self.icao_code}) Arrivals")
            self.container1.add_item(header)

            self.container2 = ui.Container()
            if self.is_for_departureBoard == True:
                header = ui.TextDisplay(f"# {self.airportname_database[self.icao_code]["name"]} ({self.icao_code}) Departures - Page 2")
            else:
                header = ui.TextDisplay(f"# {self.airportname_database[self.icao_code]["name"]} ({self.icao_code}) Arrivals - Page 2")
            self.container2.add_item(header)

            self.container3 = ui.Container()
            if self.is_for_departureBoard == True:
                header = ui.TextDisplay(f"# {self.airportname_database[self.icao_code]["name"]} ({self.icao_code}) Departures - Page 3")
            else:
                header = ui.TextDisplay(f"# {self.airportname_database[self.icao_code]["name"]} ({self.icao_code}) Arrivals - Page 3")
            self.container3.add_item(header)

            self.container4 = ui.Container()
            if self.is_for_departureBoard == True:
                header = ui.TextDisplay(f"# {self.airportname_database[self.icao_code]["name"]} ({self.icao_code}) Departures - Page 4")
            else:
                header = ui.TextDisplay(f"# {self.airportname_database[self.icao_code]["name"]} ({self.icao_code}) Arrivals - Page 4")
            self.container4.add_item(header)

            self.containers = [
                self.container1,
                self.container2,
                self.container3,
                self.container4
            ]

            for pilot in self.pilot_list:
                if self.is_for_departureBoard == True:
                    # convert icaocode to departure mode (versatility)
                    pilot_arrivalICAO = pilot["flight_plan"]["arrival"]
                    self.icao_code = pilot_arrivalICAO
                if self.is_for_departureBoard == False:
                    # convert icaocode to arrival mode
                    pilot_arrivalICAO = pilot["flight_plan"]["departure"]
                    self.icao_code = pilot_arrivalICAO

                button_label = f"{pilot.get("callsign")}"
                if pilot_counter <= 8:
                    if self.is_for_departureBoard == True:
                        self.container1.add_item(
                            ui.Section(
                                ui.TextDisplay(
                                    f"### {pilot.get("callsign")} - {str(pilot.get("cid"))} \n-# Departing to {self.airportname_database.get(self.icao_code, {}).get("name")}"
                                ),
                                accessory = ui.Button(label=button_label, url=f"https://vatsim-radar.com/?pilot={pilot.get("cid")}")
                            )
                        )
                        pilot_counter += 1
                    elif self.is_for_departureBoard == False:
                        self.container1.add_item(
                            ui.Section(
                                ui.TextDisplay(
                                    f"### {pilot.get("callsign")} - {str(pilot.get("cid"))} \n-# From {self.airportname_database.get(self.icao_code, {}).get("name")}"
                                ),
                                accessory = ui.Button(label=button_label, url=f"https://vatsim-radar.com/?pilot={pilot.get("cid")}")
                            )
                        )
                        pilot_counter += 1
                elif pilot_counter <= 16:
                    if self.is_for_departureBoard == True:
                        self.container2.add_item(
                            ui.Section(
                                ui.TextDisplay(
                                    f"### {pilot.get("callsign")} - {str(pilot.get("cid"))} \n-# Departing to {self.airportname_database.get(self.icao_code, {}).get("name")}"
                                ),
                                accessory = ui.Button(label=button_label, url=f"https://vatsim-radar.com/?pilot={pilot.get("cid")}")
                            )
                        )
                        pilot_counter += 1
                    elif self.is_for_departureBoard == False:
                        self.container2.add_item(
                            ui.Section(
                                ui.TextDisplay(
                                    f"### {pilot.get("callsign")} - {str(pilot.get("cid"))} \n-# From {self.airportname_database.get(self.icao_code, {}).get("name")}"
                                ),
                                accessory = ui.Button(label=button_label, url=f"https://vatsim-radar.com/?pilot={pilot.get("cid")}")
                            )
                        )
                        pilot_counter += 1
                elif pilot_counter <= 24:
                    if self.is_for_departureBoard == True:
                        self.container3.add_item(
                            ui.Section(
                                ui.TextDisplay(
                                    f"### {pilot.get("callsign")} - {str(pilot.get("cid"))} \n-# Departing to {self.airportname_database.get(self.icao_code, {}).get("name")}"
                                ),
                                accessory = ui.Button(label=button_label, url=f"https://vatsim-radar.com/?pilot={pilot.get("cid")}")
                            )
                        )
                        pilot_counter += 1
                    elif self.is_for_departureBoard == False:
                        self.container3.add_item(
                            ui.Section(
                                ui.TextDisplay(
                                    f"### {pilot.get("callsign")} - {str(pilot.get("cid"))} \n-# From {self.airportname_database.get(self.icao_code, {}).get("name")}"
                                ),
                                accessory = ui.Button(label=button_label, url=f"https://vatsim-radar.com/?pilot={pilot.get("cid")}")
                            )
                        )
                        pilot_counter += 1   
                elif pilot_counter <= 32:
                    if self.is_for_departureBoard == True:
                        self.container4.add_item(
                            ui.Section(
                                ui.TextDisplay(
                                    f"### {pilot.get("callsign")} - {str(pilot.get("cid"))} \n-# Departing to {self.airportname_database.get(self.icao_code, {}).get("name")}"
                                ),
                                accessory = ui.Button(label=button_label, url=f"https://vatsim-radar.com/?pilot={pilot.get("cid")}")
                            )
                        )
                        pilot_counter += 1
                    elif self.is_for_departureBoard == False:
                        self.container4.add_item(
                            ui.Section(
                                ui.TextDisplay(
                                    f"### {pilot.get("callsign")} - {str(pilot.get("cid"))} \n-# From {self.airportname_database.get(self.icao_code, {}).get("name")}"
                                ),
                                accessory = ui.Button(label=button_label, url=f"https://vatsim-radar.com/?pilot={pilot.get("cid")}")
                            )
                        )
                        pilot_counter += 1
                elif pilot_counter > 32:
                    pilot_counter += 1
            remaining_pilots = pilot_counter - 32
            self.container4.add_item(
                    ui.TextDisplay(
                        f"-# {remaining_pilots} pilots are not shown here"
                    )
                # i have no idea whats going on :)
            )            

            self.add_item(self.container1)    

        row = ui.ActionRow()

        @row.button(label="Previous")
        async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.page_count != 0:
                self.page_count -= 1
            self.clear_items()
            self.add_item(self.containers[self.page_count])

            self.add_item(self.row)
            await interaction.response.edit_message(view=self)

        @row.button(label="Next")
        async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if self.page_count != 3:
                self.page_count += 1
            print(self.containers[self.page_count])
            self.clear_items()
            self.add_item(self.containers[self.page_count])

            self.add_item(self.row)
            await interaction.response.edit_message(view=self)