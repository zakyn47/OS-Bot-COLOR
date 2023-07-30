import time

import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
import pyautogui
from utilities.imagesearch import search_img_in_rect

class Fletcher(OSRSBot):
    def __init__(self):
        bot_title = "Zak Fletcher"
        description = """
        fletches logs
        1st inventory slot must be knife
        bank all must be enabled

        tag bank booth with clr.YELLOW
        """
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 100

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

    def __bank(self):
        logs = search_img_in_rect(r"C:\Users\sakul\Desktop\OS-Bot-COLOR\src\images\bot\scraper\Maple_logs_bank.png", self.win.game_view)
        bank_location = self.get_all_tagged_in_rect(self.win.game_view, clr.YELLOW)
        second_inv_slot_location = self.win.inventory_slots[1]
        self.mouse.move_to(bank_location[0].center())
        self.mouse.click()
        time.sleep(1)
        self.mouse.move_to(second_inv_slot_location.get_center())
        self.mouse.click()
        time.sleep(1)
        self.mouse.move_to(logs.center())
        self.mouse.click()
        time.sleep(1)
        pyautogui.press("esc")
        time.sleep(1)

    def __fletch(self):
        knife_location = self.win.inventory_slots[0]
        second_inv_slot_location = self.win.inventory_slots[1]
        self.mouse.move_to(knife_location.get_center())
        self.mouse.click()
        self.mouse.move_to(second_inv_slot_location.get_center())
        self.mouse.click()
        time.sleep(1)
        pyautogui.press("space")
        time.sleep(rd.fancy_normal_sample(40, 60))


    def main_loop(self):
        """
        When implementing this function, you have the following responsibilities:
        1. If you need to halt the bot from within this function, call `self.stop()`. You'll want to do this
           when the bot has made a mistake, gets stuck, or a condition is met that requires the bot to stop.
        2. Frequently call self.update_progress() and self.log_msg() to send information to the UI.
        3. At the end of the main loop, make sure to call `self.stop()`.

        Additional notes:
        - Make use of Bot/RuneLiteBot member functions. There are many functions to simplify various actions.
          Visit the Wiki for more.
        - Using the available APIs is highly recommended. Some of all of the API tools may be unavailable for
          select private servers. For usage, uncomment the `api_m` and/or `api_s` lines below, and use the `.`
          operator to access their functions.
        """
        # Setup APIs
        api_m = MorgHTTPSocket()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            self.__bank()
            self.__fletch()

            self.update_progress((time.time() - start_time) / end_time)
            self.log_msg(f"Running for {round((time.time() - start_time) / 60, 2)} minutes.")
        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()