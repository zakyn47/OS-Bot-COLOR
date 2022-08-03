'''
Thieving bot for OSNR. Thieves from NPCs.
'''
from model.bot import BotStatus, Point
from model.osnr.osnr_bot import OSNRBot
import time
import pyautogui as pag


class OSNRThievingNPC(OSNRBot):
    def __init__(self):
        title = "Thieving NPC Bot"
        description = ("This bot thieves from NPCs in OSNR. Position your character near the NPC you wish to thieve from. " +
                       "If you have food, tag all in inventory as NPC-blue. This bot cannot yet bank. Start bot with full HP, " +
                       "coins in first slot, and empty last inventory slot. Turn on Entity Hider > Hide NPCs 2D.")
        super().__init__(title=title, description=description)
        self.should_eat = False
        self.should_drop_inv = False
        self.skip_rows = 0
        self.coin_pouch_path = "./src/images/bot/near_reality/coin_pouch.png"

    def create_options(self):
        self.options_builder.add_slider_option("iterations", "How long to run (minutes)?", 1, 200)
        self.options_builder.add_dropdown_option("should_drop_inv", "Drop inventory?", ["Yes", "No"])
        self.options_builder.add_slider_option("skip_rows", "If dropping, skip rows?", 0, 6)

    def save_options(self, options: dict):
        for option, res in options.items():
            if option == "iterations":
                self.iterations = options[option]
                self.log_msg(f"Running time: {self.iterations} minutes.")
            elif option == "should_drop_inv":
                if res == "Yes":
                    self.should_drop_inv = True
                    self.log_msg("Dropping inventory enabled.")
                else:
                    self.should_drop_inv = False
                    self.log_msg("Dropping inventory disabled.")
            elif option == "skip_rows":
                self.skip_rows = options[option]
                self.log_msg(f"Skipping {self.skip_rows} rows when dropping inventory.")
            else:
                self.log_msg(f"Unknown option: {option}")
        self.options_set = True
        self.log_msg("Options set successfully.")

    def main_loop(self):  # sourcery skip: low-code-quality, use-named-expression
        # Setup
        self.setup_osnr()

        # Anchors/counters
        hp_threshold_pos = Point(541, 394)  # TODO: implement checking health threshold
        hp_threshold_rgb = pag.pixel(hp_threshold_pos.x, hp_threshold_pos.y)
        last_inventory_pos = self.inventory_slots[6][3]  # TODO: or [-1][-1]?
        last_inventory_rgb = pag.pixel(last_inventory_pos.x, last_inventory_pos.y)
        npc_search_fail_count = 0
        theft_count = 0
        no_pouch_count = 0

        # Main loop
        start_time = time.time()
        while time.time() - start_time < self.iterations * 60:
            # Check if we should eat
            while pag.pixel(hp_threshold_pos.x, hp_threshold_pos.y) != hp_threshold_rgb:
                if not self.status_check_passed():
                    return
                foods = self.get_all_tagged_in_rect(rect=self.rect_inventory, color=self.NPC_BLUE)
                if len(foods) > 0:
                    self.log_msg("Eating...")
                    self.mouse.move_to(foods[0])
                    time.sleep(0.3)
                    pag.click()
                    if len(foods) > 1:  # eat another if available
                        time.sleep(1)
                        self.mouse.move_to(foods[1])
                        time.sleep(0.3)
                        pag.click()
                else:
                    self.log_msg("Out of food.")
                    self.teleport_home()
                    self.set_status(BotStatus.STOPPED)
                    return

            if not self.status_check_passed():
                return

            # Check if we should drop inventory
            if self.should_drop_inv and pag.pixel(last_inventory_pos.x, last_inventory_pos.y) != last_inventory_rgb:
                self.drop_inventory(skip_rows=self.skip_rows)

            if not self.status_check_passed():
                return

            # Thieve from NPC
            npc_pos = self.get_nearest_tagged_NPC(game_view=self.rect_game_view)
            if npc_pos is not None:
                self.mouse.move_to(npc_pos, duration=0.4)
                pag.rightClick()
                time.sleep(0.3)
                self.mouse.move_rel(x=0, y=41, duration=0.2)
                pag.click()
                npc_search_fail_count = 0
                theft_count += 1
                if theft_count % 10 == 0:
                    self.log_msg("Clicking coin pouch...")
                    pouch = self.search_img_in_rect(img_path=self.coin_pouch_path, rect=self.rect_inventory, conf=0.9)
                    if pouch:
                        self.mouse.move_to(pouch)
                        time.sleep(0.5)
                        pag.click()
                        no_pouch_count = 0
                    else:
                        self.log_msg("Could not find coin pouch.")
                        no_pouch_count += 1
                        if no_pouch_count > 5:
                            self.log_msg("Could not find coin pouch 5 times. Aborting...")
                            self.teleport_home()
                            self.set_status(BotStatus.STOPPED)
                            return
            else:
                self.log_msg("No NPC found.")
                npc_search_fail_count += 1
                if npc_search_fail_count > 10:
                    self.log_msg("No NPC found 10 times in a row.")
                    self.teleport_home()
                    self.set_status(BotStatus.STOPPED)
                    return

            if not self.status_check_passed():
                return

        self.set_status(BotStatus.STOPPED)