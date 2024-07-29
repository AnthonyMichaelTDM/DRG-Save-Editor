from re import Match
from sys import platform
from typing import List

from core.file_writer import make_save_file
from core.state_manager import Stats
from core.view import EditorUI
from definitions import (
    GUID_RE,
    LATEST_SEASON,
    MAX_BADGES,
    RANK_TITLES,
    XP_PER_SEASON_LEVEL,
    XP_PER_WEAPON_LEVEL,
    XP_TABLE,
    MAX_DWARF_XP,
)
from helpers import utils
from helpers.datatypes import Cost
from helpers.enums import Dwarf, Resource
from helpers.overclock import Overclock

from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import QFileDialog, QListWidget, QListWidgetItem, QTreeWidgetItem

if platform == "win32":
    import winreg


class Controller:
    def __init__(self, widget: EditorUI, state_manager: Stats) -> None:
        self.widget = widget
        self.state_manager = state_manager

        self.file_name: str = ""
        self.season_selected = LATEST_SEASON

        self.setup_connections()

    def setup_connections(self):
        self.widget.actionOpen_Save_File.triggered.connect(self.open_file)
        self.widget.actionSave_changes.triggered.connect(self.save_changes)
        self.widget.actionSet_All_Classes_to_25.triggered.connect(self.set_all_25)
        self.widget.actionAdd_overclock_crafting_materials.triggered.connect(
            self.add_crafting_mats
        )
        self.widget.actionReset_to_original_values.triggered.connect(self.reset_values)
        self.widget.actionMax_all_available_weapons.triggered.connect(
            self.max_all_available_weapon_maintenance
        )
        self.widget.combo_oc_filter.currentTextChanged.connect(self.filter_overclocks)
        self.widget.season_box.currentTextChanged.connect(self.update_season_data)
        self.widget.add_cores_button.clicked.connect(self.add_cores)
        self.widget.remove_all_ocs.clicked.connect(self.remove_all_ocs)
        self.widget.remove_selected_ocs.clicked.connect(self.remove_selected_ocs)
        self.widget.driller_promo_box.currentIndexChanged.connect(self.update_rank)
        self.widget.engineer_promo_box.currentIndexChanged.connect(self.update_rank)
        self.widget.gunner_promo_box.currentIndexChanged.connect(self.update_rank)
        self.widget.scout_promo_box.currentIndexChanged.connect(self.update_rank)

        for widget in [
            self.widget.driller_xp,
            self.widget.driller_lvl_text,
            self.widget.driller_xp_2,
            self.widget.engineer_xp,
            self.widget.engineer_lvl_text,
            self.widget.engineer_xp_2,
            self.widget.gunner_xp,
            self.widget.gunner_lvl_text,
            self.widget.gunner_xp_2,
            self.widget.scout_xp,
            self.widget.scout_lvl_text,
            self.widget.scout_xp_2,
            self.widget.season_xp,
            self.widget.season_lvl_text,
        ]:
            widget.focus_out_signal.connect(self.handle_focus_out)

    @Slot(str, int)
    def handle_focus_out(self, box_name: str, value: int):
        season = False

        if box_name.startswith("driller"):
            dwarf = "driller"
        elif box_name.startswith("engineer"):
            dwarf = "engineer"
        elif box_name.startswith("gunner"):
            dwarf = "gunner"
        elif box_name.startswith("scout"):
            dwarf = "scout"
        elif box_name.startswith("season"):
            season = True
        else:
            print("abandon all hope, ye who see this message")
            return

        if season:
            if box_name.endswith("xp"):
                if value >= 5000:
                    self.widget.season_xp.setText("4999")
                elif value < 0:
                    self.widget.season_xp.setText("0")
            elif box_name.endswith("lvl_text"):
                if value < 0:
                    self.widget.season_lvl_text.setText("0")
                elif value > 100:
                    self.widget.season_lvl_text.setText("100")
                    self.widget.season_xp.setText("0")
        else:
            if box_name.endswith("xp"):  # total xp box changed
                total = value
            elif box_name.endswith("text"):  # dwarf level box changed
                xp, level, rem = self.get_dwarf_xp(dwarf)
                if XP_TABLE[value - 1] + rem == xp:
                    total = xp
                else:
                    total = XP_TABLE[value - 1]
            elif box_name.endswith("2"):  # xp for current level changed
                xp, level, rem = self.get_dwarf_xp(dwarf)
                total = XP_TABLE[level - 1] + value

            self.update_xp(dwarf, total)  # update relevant xp fields

    @Slot()  # type: ignore
    def open_file(self) -> None:
        # open file dialog box, start in steam install path if present
        steam_path = get_steam_path()
        self.file_name = QFileDialog.getOpenFileName(
            None,
            "Open Save File...",
            steam_path,
            "Player Save Files (*.sav);;All Files (*.*)",
        )[0]

        if not self.file_name:
            return

        self.widget.setWindowTitle(
            f"DRG Save Editor - {self.file_name}"
        )  # window-dressing
        with open(self.file_name, "rb") as f:
            save_data = f.read()

        # make a backup of the save file in case of weirdness or bugs
        with open(f"{self.file_name}.old", "wb") as backup:
            backup.write(save_data)

        # enable widgets that don't work without a save file present
        self.widget.actionSave_changes.setEnabled(True)
        self.widget.actionReset_to_original_values.setEnabled(True)
        self.widget.combo_oc_filter.setEnabled(True)

        # initialize and populate the text fields
        self.init_values(save_data)
        self.reset_values()
        self.update_rank()

        # clear and initialize overclock tree view
        self.init_overclock_tree()

    def get_values(self):
        self.state_manager.resources[Resource.BISMOR] = int(
            self.widget.bismor_text.text()
        )
        self.state_manager.resources[Resource.CROPPA] = int(
            self.widget.croppa_text.text()
        )
        self.state_manager.resources[Resource.ENOR] = int(self.widget.enor_text.text())
        self.state_manager.resources[Resource.JADIZ] = int(
            self.widget.jadiz_text.text()
        )
        self.state_manager.resources[Resource.MAGNITE] = int(
            self.widget.magnite_text.text()
        )
        self.state_manager.resources[Resource.UMANITE] = int(
            self.widget.umanite_text.text()
        )

        self.state_manager.resources[Resource.YEAST] = int(
            self.widget.yeast_text.text()
        )
        self.state_manager.resources[Resource.STARCH] = int(
            self.widget.starch_text.text()
        )
        self.state_manager.resources[Resource.MALT] = int(self.widget.malt_text.text())
        self.state_manager.resources[Resource.BARLEY] = int(
            self.widget.barley_text.text()
        )

        self.state_manager.dwarf_xp[Dwarf.DRILLER] = int(self.widget.driller_xp.text())
        self.state_manager.dwarf_xp[Dwarf.ENGINEER] = int(
            self.widget.engineer_xp.text()
        )
        self.state_manager.dwarf_xp[Dwarf.GUNNER] = int(self.widget.gunner_xp.text())
        self.state_manager.dwarf_xp[Dwarf.SCOUT] = int(self.widget.scout_xp.text())

        driller_promo = int(self.widget.driller_promo_box.currentIndex())
        gunner_promo = int(self.widget.gunner_promo_box.currentIndex())
        scout_promo = int(self.widget.scout_promo_box.currentIndex())
        engineer_promo = int(self.widget.engineer_promo_box.currentIndex())

        self.state_manager.dwarf_promo[Dwarf.DRILLER] = (
            driller_promo
            if driller_promo < MAX_BADGES
            else self.state_manager.dwarf_promo[Dwarf.DRILLER]
        )
        self.state_manager.dwarf_promo[Dwarf.ENGINEER] = (
            engineer_promo
            if engineer_promo < MAX_BADGES
            else self.state_manager.dwarf_promo[Dwarf.ENGINEER]
        )
        self.state_manager.dwarf_promo[Dwarf.GUNNER] = (
            gunner_promo
            if gunner_promo < MAX_BADGES
            else self.state_manager.dwarf_promo[Dwarf.GUNNER]
        )
        self.state_manager.dwarf_promo[Dwarf.SCOUT] = (
            scout_promo
            if scout_promo < MAX_BADGES
            else self.state_manager.dwarf_promo[Dwarf.SCOUT]
        )

        self.state_manager.resources[Resource.ERROR] = int(
            self.widget.error_text.text()
        )
        self.state_manager.resources[Resource.CORES] = int(self.widget.core_text.text())
        self.state_manager.credits = int(self.widget.credits_text.text())
        self.state_manager.perk_points = int(self.widget.perk_text.text())
        self.state_manager.resources[Resource.DATA] = int(self.widget.data_text.text())
        self.state_manager.resources[Resource.PHAZ] = int(self.widget.phazy_text.text())

        self.store_season_changes(self.season_selected)

    def store_season_changes(self, season_num):
        new_xp = self.widget.season_xp.text()
        new_scrip = self.widget.scrip_text.text()
        if new_xp and new_scrip:
            self.state_manager.season_data[season_num] = {
                "xp": int(new_xp)
                + XP_PER_SEASON_LEVEL * int(self.widget.season_lvl_text.text()),
                "scrip": int(new_scrip),
            }

    def init_values(self, save_data):
        self.state_manager.parse_data(save_data)

        # addItem triggers currentTextChanged which triggers saving of data currently in textbox.
        # if two saves are loaded consecutively, it will cause values in the textbox (from file1)
        # to be saved into storage now (representing file2)
        # remove any text already inside to prevent this
        self.widget.season_xp.setText("")
        self.widget.season_lvl_text.setText("")
        self.widget.scrip_text.setText("")

        # populate the dropdown for season numbers
        self.widget.season_box.clear()
        for season_num in self.state_manager.season_data.keys():
            self.widget.season_box.addItem(str(season_num))
        self.widget.season_box.setCurrentIndex(len(self.state_manager.season_data) - 1)

        if len(self.state_manager.season_data) == 0:
            self.widget.season_group.setEnabled(False)

    @Slot()  # type: ignore
    def set_all_25(self) -> None:
        self.update_xp("driller", MAX_DWARF_XP)
        self.update_xp("engineer", MAX_DWARF_XP)
        self.update_xp("gunner", MAX_DWARF_XP)
        self.update_xp("scout", MAX_DWARF_XP)

    @Slot()  # type: ignore
    def add_crafting_mats(self) -> None:
        cost: Cost = Cost()
        unforged_ocs: List[Overclock] = self.state_manager.get_unforged_overclocks()
        for oc in unforged_ocs:
            cost += oc.cost
        print(cost)
        self.add_resources(cost)

    def add_resources(self, res_dict) -> None:
        self.widget.bismor_text.setText(
            str(int(self.widget.bismor_text.text()) + res_dict.bismor)
        )
        self.widget.croppa_text.setText(
            str(int(self.widget.croppa_text.text()) + res_dict.croppa)
        )
        self.widget.enor_text.setText(
            str(int(self.widget.enor_text.text()) + res_dict.enor)
        )
        self.widget.jadiz_text.setText(
            str(int(self.widget.jadiz_text.text()) + res_dict.jadiz)
        )
        self.widget.magnite_text.setText(
            str(int(self.widget.magnite_text.text()) + res_dict.magnite)
        )
        self.widget.umanite_text.setText(
            str(int(self.widget.umanite_text.text()) + res_dict.umanite)
        )
        self.widget.credits_text.setText(
            str(int(self.widget.credits_text.text()) + res_dict.credits)
        )

    @Slot()  # type: ignore
    def reset_values(self) -> None:
        self.widget.bismor_text.setText(
            str(self.state_manager.resources[Resource.BISMOR])
        )
        self.widget.enor_text.setText(str(self.state_manager.resources[Resource.ENOR]))
        self.widget.jadiz_text.setText(
            str(self.state_manager.resources[Resource.JADIZ])
        )
        self.widget.croppa_text.setText(
            str(self.state_manager.resources[Resource.CROPPA])
        )
        self.widget.magnite_text.setText(
            str(self.state_manager.resources[Resource.MAGNITE])
        )
        self.widget.umanite_text.setText(
            str(self.state_manager.resources[Resource.UMANITE])
        )

        self.widget.yeast_text.setText(
            str(self.state_manager.resources[Resource.YEAST])
        )
        self.widget.starch_text.setText(
            str(self.state_manager.resources[Resource.STARCH])
        )
        self.widget.malt_text.setText(str(self.state_manager.resources[Resource.MALT]))
        self.widget.barley_text.setText(
            str(self.state_manager.resources[Resource.BARLEY])
        )

        self.widget.error_text.setText(
            str(self.state_manager.resources[Resource.ERROR])
        )
        self.widget.core_text.setText(str(self.state_manager.resources[Resource.CORES]))
        self.widget.credits_text.setText(str(self.state_manager.credits))
        self.widget.perk_text.setText(str(self.state_manager.perk_points))
        self.widget.data_text.setText(str(self.state_manager.resources[Resource.DATA]))
        self.widget.phazy_text.setText(str(self.state_manager.resources[Resource.PHAZ]))

        self.widget.driller_xp.setText(str(self.state_manager.dwarf_xp[Dwarf.DRILLER]))
        d_xp = utils.xp_total_to_level(self.state_manager.dwarf_xp[Dwarf.DRILLER])
        d_promo = self.state_manager.dwarf_promo[Dwarf.DRILLER]
        self.widget.driller_lvl_text.setText(str(d_xp[0]))
        self.widget.driller_xp_2.setText(str(d_xp[1]))
        self.widget.driller_promo_box.setCurrentIndex(
            d_promo if d_promo < MAX_BADGES else MAX_BADGES
        )

        self.widget.engineer_xp.setText(
            str(self.state_manager.dwarf_xp[Dwarf.ENGINEER])
        )
        e_xp = utils.xp_total_to_level(self.state_manager.dwarf_xp[Dwarf.ENGINEER])
        e_promo = self.state_manager.dwarf_promo[Dwarf.ENGINEER]
        self.widget.engineer_lvl_text.setText(str(e_xp[0]))
        self.widget.engineer_xp_2.setText(str(e_xp[1]))
        self.widget.engineer_promo_box.setCurrentIndex(
            e_promo if e_promo < MAX_BADGES else MAX_BADGES
        )

        self.widget.gunner_xp.setText(str(self.state_manager.dwarf_xp[Dwarf.GUNNER]))
        g_xp = utils.xp_total_to_level(self.state_manager.dwarf_xp[Dwarf.GUNNER])
        g_promo = self.state_manager.dwarf_promo[Dwarf.GUNNER]
        self.widget.gunner_lvl_text.setText(str(g_xp[0]))
        self.widget.gunner_xp_2.setText(str(g_xp[1]))
        self.widget.gunner_promo_box.setCurrentIndex(
            g_promo if g_promo < MAX_BADGES else MAX_BADGES
        )

        self.widget.scout_xp.setText(str(self.state_manager.dwarf_xp[Dwarf.SCOUT]))
        s_xp = utils.xp_total_to_level(self.state_manager.dwarf_xp[Dwarf.SCOUT])
        s_promo = self.state_manager.dwarf_promo[Dwarf.SCOUT]
        self.widget.scout_lvl_text.setText(str(s_xp[0]))
        self.widget.scout_xp_2.setText(str(s_xp[1]))
        self.widget.scout_promo_box.setCurrentIndex(
            s_promo if s_promo < MAX_BADGES else MAX_BADGES
        )

        unforged_list = self.widget.unforged_list
        unforged_ocs = self.state_manager.get_unforged_overclocks()
        populate_unforged_list(unforged_list, unforged_ocs)

        self.filter_overclocks()
        self.update_rank()
        self.reset_season_data()

    def reset_season_data(self):
        season_total_xp = self.state_manager.season_data[self.season_selected]["xp"]
        self.widget.season_xp.setText(str(season_total_xp % XP_PER_SEASON_LEVEL))
        self.widget.season_lvl_text.setText(str(season_total_xp // XP_PER_SEASON_LEVEL))
        self.widget.scrip_text.setText(
            str(self.state_manager.season_data[self.season_selected]["scrip"])
        )

    @Slot()  # type: ignore
    def save_changes(self) -> None:
        self.get_values()

        with open(self.file_name, "rb") as f:
            save_data: bytes = f.read()

        save_file: bytes = make_save_file(save_data, self.state_manager)

        with open(self.file_name, "wb") as f:
            f.write(save_file)

    @Slot()  # type: ignore
    def max_all_available_weapon_maintenance(self) -> None:
        for weapon, [_, level, _] in self.state_manager.weapons.items():
            xp_needed = 0
            for xp_level, xp_for_levelup in XP_PER_WEAPON_LEVEL.items():
                if level < xp_level:
                    xp_needed += xp_for_levelup
            if xp_needed:
                self.state_manager.weapons[weapon] = [xp_needed, level, True]

    @Slot()  # type: ignore
    def remove_selected_ocs(self) -> None:
        list_items = self.widget.unforged_list.selectedItems()
        items_to_remove = list()
        for i in list_items:
            maybe_item_to_remove: Match[str] | None = GUID_RE.search(i.text())
            if maybe_item_to_remove is None:
                continue
            item_to_remove: Match[str] = maybe_item_to_remove

            items_to_remove.append(item_to_remove.group(1))
            item = self.widget.unforged_list.row(i)
            self.widget.unforged_list.takeItem(item)

        self.remove_ocs(items_to_remove)

    @Slot()  # type: ignore
    def remove_all_ocs(self) -> None:
        items_to_remove = list()
        unforged_list = self.widget.unforged_list
        for i in range(unforged_list.count()):
            item = unforged_list.item(i)
            maybe_item_to_remove: Match[str] | None = GUID_RE.search(item.text())
            if maybe_item_to_remove is None:
                continue
            item_to_remove: Match[str] = maybe_item_to_remove

            items_to_remove.append(item_to_remove.group(1))

        self.remove_ocs(items_to_remove)
        unforged_list.clear()

    def remove_ocs(self, oc_list: list[str]) -> None:
        self.state_manager.set_overclocks_to_unacquired(oc_list)
        self.filter_overclocks()

    def update_season_data(self) -> None:

        # store textbox values before changing which season's data is being viewed
        # currently displayed values can be saved before saving the new file data
        self.store_season_changes(self.season_selected)
        if self.widget.season_box.currentText():
            self.season_selected = int(self.widget.season_box.currentText())

        # refresh display
        self.reset_season_data()

    @Slot()  # type: ignore
    def filter_overclocks(self) -> None:
        item_filter = self.widget.combo_oc_filter.currentText()
        tree = self.widget.overclock_tree
        tree_root = tree.invisibleRootItem()

        for i in range(tree_root.childCount()):
            dwarf = tree_root.child(i)
            for j in range(dwarf.childCount()):
                weapon = dwarf.child(j)
                for k in range(weapon.childCount()):
                    oc = weapon.child(k)
                    if oc.text(1) == item_filter or item_filter == "All":
                        oc.setHidden(False)
                    else:
                        oc.setHidden(True)

    @Slot()  # type: ignore
    def add_cores(self) -> None:
        tree = self.widget.overclock_tree
        selected = tree.selectedItems()
        unacquired_ocs = self.state_manager.get_unacquired_overclocks()
        items_to_add = list()
        newly_acquired_ocs = []
        for i in selected:
            if i.text(1) == "Unacquired" and i.text(2) in unacquired_ocs:
                items_to_add.append(f"{i.parent().text(0)}: {i.text(0)} ({i.text(2)})")
                self.state_manager.guid_dict[i.text(2)].status = "Unforged"
                newly_acquired_ocs.append(i.text(2))

        self.state_manager.set_overclocks_to_unforged(newly_acquired_ocs)

        core_list = self.widget.unforged_list
        for item in items_to_add:
            core_list.addItem(item)

        core_list.sortItems()
        self.filter_overclocks()

    def get_dwarf_xp(self, dwarf) -> tuple[int, int, int]:
        # gets the total xp, level, and progress to the next level (rem)
        if dwarf == "driller":
            total = int(self.widget.driller_xp.text())
            level = int(self.widget.driller_lvl_text.text())
            rem = int(self.widget.driller_xp_2.text())
        elif dwarf == "engineer":
            total = int(self.widget.engineer_xp.text())
            level = int(self.widget.engineer_lvl_text.text())
            rem = int(self.widget.engineer_xp_2.text())
        elif dwarf == "gunner":
            total = int(self.widget.gunner_xp.text())
            level = int(self.widget.gunner_lvl_text.text())
            rem = int(self.widget.gunner_xp_2.text())
        elif dwarf == "scout":
            total = int(self.widget.scout_xp.text())
            level = int(self.widget.scout_lvl_text.text())
            rem = int(self.widget.scout_xp_2.text())
        else:
            total = rem = level = -1

        return total, level, rem

    def update_xp(self, dwarf, total_xp=0) -> None:
        # updates the xp fields for the specified dwarf with the new xp total
        if total_xp > MAX_DWARF_XP:  # max xp check
            total_xp = MAX_DWARF_XP
        level, remainder = utils.xp_total_to_level(total_xp)  # transform XP total
        bad_dwarf = False  # check for possible weirdness
        if dwarf == "driller":
            total_box = self.widget.driller_xp
            level_box = self.widget.driller_lvl_text
            remainder_box = self.widget.driller_xp_2
        elif dwarf == "engineer":
            total_box = self.widget.engineer_xp
            level_box = self.widget.engineer_lvl_text
            remainder_box = self.widget.engineer_xp_2
        elif dwarf == "gunner":
            total_box = self.widget.gunner_xp
            level_box = self.widget.gunner_lvl_text
            remainder_box = self.widget.gunner_xp_2
        elif dwarf == "scout":
            total_box = self.widget.scout_xp
            level_box = self.widget.scout_lvl_text
            remainder_box = self.widget.scout_xp_2
        else:
            print("no valid dwarf specified")
            bad_dwarf = True

        if not bad_dwarf:  # update xp totals
            total_box.setText(str(total_xp))
            level_box.setText(str(level))
            remainder_box.setText(str(remainder))

        self.update_rank()

    def update_rank(self) -> None:
        s_promo: int = (
            self.state_manager.dwarf_promo[Dwarf.SCOUT]
            if self.widget.scout_promo_box.currentIndex() == MAX_BADGES
            else self.widget.scout_promo_box.currentIndex()
        )
        e_promo: int = (
            self.state_manager.dwarf_promo[Dwarf.ENGINEER]
            if self.widget.engineer_promo_box.currentIndex() == MAX_BADGES
            else self.widget.engineer_promo_box.currentIndex()
        )
        g_promo: int = (
            self.state_manager.dwarf_promo[Dwarf.GUNNER]
            if self.widget.gunner_promo_box.currentIndex() == MAX_BADGES
            else self.widget.gunner_promo_box.currentIndex()
        )
        d_promo: int = (
            self.state_manager.dwarf_promo[Dwarf.DRILLER]
            if self.widget.driller_promo_box.currentIndex() == MAX_BADGES
            else self.widget.driller_promo_box.currentIndex()
        )

        try:
            s_level = int(self.widget.scout_lvl_text.text())
            e_level = int(self.widget.engineer_lvl_text.text())
            g_level = int(self.widget.gunner_lvl_text.text())
            d_level = int(self.widget.driller_lvl_text.text())
            total_levels: int = (
                ((s_promo + e_promo + g_promo + d_promo) * 25)
                + s_level
                + e_level
                + g_level
                + d_level
                - 4
            )
            rank: int = total_levels // 3  # integer division
            rem: int = total_levels % 3
        except ValueError:
            rank = 1
            rem = 0

        try:
            title: str = RANK_TITLES[rank]
        except IndexError:
            title = "Lord of the Deep"

        self.widget.classes_group.setTitle(
            f"Classes - Rank {rank + 1} {rem}/3, {title}"
        )

    def build_oc_tree(self, tree: QTreeWidgetItem) -> None:
        oc_dict = self.state_manager.build_oc_dict()
        for char, weapons in oc_dict.items():
            char_entry = QTreeWidgetItem(tree)
            char_entry.setText(0, char)
            for weapon, oc_names in weapons.items():
                weapon_entry = QTreeWidgetItem(char_entry)
                weapon_entry.setText(0, weapon)
                for name, uuid in oc_names.items():
                    oc_entry = QTreeWidgetItem(weapon_entry)
                    oc_entry.setText(0, name)
                    oc_entry.setText(1, self.state_manager.guid_dict[uuid].status)
                    oc_entry.setText(2, uuid)

    def init_overclock_tree(self):
        self.widget.overclock_tree.clear()
        overclock_tree = self.widget.overclock_tree.invisibleRootItem()
        self.build_oc_tree(overclock_tree)
        self.widget.overclock_tree.sortItems(0, Qt.SortOrder.AscendingOrder)


def get_steam_path():
    try:
        # find the install path for the steam version
        if platform == "win32":
            steam_reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")  # type: ignore
            steam_path = winreg.QueryValueEx(steam_reg, "SteamPath")[0]  # type: ignore
            steam_path += "/steamapps/common/Deep Rock Galactic/FSD/Saved/SaveGames"
        else:
            steam_path = "."
    except FileNotFoundError:
        steam_path = "."

    return steam_path


def populate_unforged_list(list_widget: QListWidget, unforged: List[Overclock]) -> None:
    # populates the list on acquired but unforged overclocks (includes cosmetics)
    list_widget.clear()
    for oc_item in unforged:
        oc = QListWidgetItem(None)
        try:
            oc.setText(f"{oc_item.weapon}: {oc_item.name} ({oc_item.guid})")
        except Exception:
            oc.setText(f"Cosmetic: {oc_item.guid}")
        list_widget.addItem(oc)
