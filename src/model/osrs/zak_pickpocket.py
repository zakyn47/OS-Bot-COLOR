import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class Pickpocket(OSRSBot):
    def __init__(self):
        bot_title = "Pickpocket"
        description = "pickpocket master farmer @ hosidius - mark NPC clr.cyan, use cakes as food"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 10

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)


    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def __pickpocket(self, api_m: MorgHTTPSocket):
        """
        Pickpocket cyan tagged NPC
        """
        self.log_msg("Pickpocketing")
        nearest_npc = self.get_nearest_tag(color=clr.CYAN)
        if nearest_npc is None:
            self.log_msg("No cyan tagged NPC found.")
            return
        self.log_msg(f"Found cyan tagged NPC: {nearest_npc}")
        self.mouse.move_to(destination=nearest_npc.random_point())
        self.mouse.click()
        api_m.wait_til_gained_xp(skill="Thieving", timeout=4)

    def __open_pouches(self, api_m: MorgHTTPSocket):
        """
        clicks on pouches in first inventory slot
        """
        self.log_msg("Opening pouches")
        pouch = api_m.get_inv_item_indices(item_id=ids.COIN_POUCH)
        self.drop(slots=pouch)

    def __silk_stall(self, api_m: MorgHTTPSocket):
        """
        clicks on silk stall
        """
        stall = self.get_nearest_tag(color=clr.YELLOW)
        self.mouse.move_to(destination=stall.center())
        self.mouse.click()
        time.sleep(7)
        self.log_msg("Stealing silk")
        silk = api_m.get_inv_item_indices(item_id=ids.SILK)
        if api_m.get_is_inv_full():
            self.drop(slots=silk)

    def __eat(self, api: StatusSocket):
        self.log_msg("HP is low.")
        food_slots = api.get_inv_item_indices(ids.combo_food)
        if len(food_slots) == 0:
            self.log_msg("No food found. Pls tell me what to do...")
            return
        self.log_msg("Eating food...")
        self.mouse.move_to(self.win.inventory_slots[food_slots[0]].random_point())
        self.mouse.click()

    def main_loop(self):
        # Setup APIs
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()

        junk = [
            ids.POTATO_SEED,
            ids.ONION_SEED,
            ids.CABBAGE_SEED,
            ids.TOMATO_SEED,
            ids.SWEETCORN_SEED,
            ids.STRAWBERRY_SEED,
            ids.WOAD_SEED,
            ids.MARIGOLD_SEED,
            ids.ROSEMARY_SEED,
            ids.NASTURTIUM_SEED,
            ids.WILDBLOOD_SEED,
        ]

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --
            # Code within this block will LOOP until the bot is stopped.
            print(f"api status: {api_m.test_endpoints()}")
            self.__pickpocket(api_m=api_m)
            if api_m.get_hitpoints()[0] < 20:
                self.__eat(api_m)
            elif api_m.get_is_inv_full():
                self.drop(slots=api_m.get_inv_item_indices(junk))
            elif api_m.get_inv_item_stack_amount(ids.combo_food) < 1:
                self.logout()

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()
