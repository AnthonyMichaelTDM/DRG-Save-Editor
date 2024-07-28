import os
import sys

from core.state_manager import Stats
from definitions import (MAX_BADGES, PROMO_RANKS,
                         RANK_TITLES,
                         XP_TABLE)
from helpers.enums import Dwarf
from helpers import utils

from PySide6.QtCore import QFile, QIODevice, Qt
from PySide6.QtGui import QAction, QFocusEvent
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QComboBox, QGroupBox, QLabel,
                               QLineEdit, QListWidget,
                               QPushButton, QTreeWidget, QTreeWidgetItem)


class TextEditFocusChecking(QLineEdit):
    """
    Custom single-line text box to allow for event-driven updating of XP totals
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def focusOutEvent(self, e: QFocusEvent) -> None:
        # check for blank text
        box: str = self.objectName()
        if self.text() == "":
            return super().focusOutEvent(e)
        season = False
        value = int(self.text())

        if box.startswith("driller"):
            dwarf = "driller"
        elif box.startswith("engineer"):
            dwarf = "engineer"
        elif box.startswith("gunner"):
            dwarf = "gunner"
        elif box.startswith("scout"):
            dwarf = "scout"
        elif box.startswith("season"):
            season = True
        else:
            print("abandon all hope, ye who see this message")
            return super().focusOutEvent(e)

        if season:
            if box.endswith("xp"):
                if value >= 5000:
                    widget.season_xp.setText("4999")
                elif value < 0:
                    widget.season_xp.setText("0")
            elif box.endswith("lvl_text"):
                if value < 0:
                    widget.season_lvl_text.setText("0")
                elif value > 100:
                    widget.season_lvl_text.setText("100")
                    widget.season_xp.setText("0")
        else:
            # decide/calculate how to update based on which box was changed
            if box.endswith("xp"):  # total xp box changed
                total = value
            elif box.endswith("text"):  # dwarf level box changed
                xp, level, rem = EditorUI.get_dwarf_xp(dwarf)
                if XP_TABLE[value - 1] + rem == xp:
                    total = xp
                else:
                    total = XP_TABLE[value - 1]
            elif box.endswith("2"):  # xp for current level changed
                xp, level, rem = EditorUI.get_dwarf_xp(dwarf)
                total = XP_TABLE[level - 1] + value

            update_xp(dwarf, total)  # update relevant xp fields

        return super().focusOutEvent(e)  # call any other stuff that might happen (?)


# we use dependency injection to pass the widget to the EditorUI class
class EditorUI:
    def __init__(self):
        # specify and open the UI
        ui_file_name = "editor.ui"

        # check if the UI file exists in the current working directory, if not, check the directory of the script (for PyInstaller)
        if not os.path.exists(ui_file_name):
            ui_file_name = os.path.join(os.path.dirname(__file__), ui_file_name)

        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):  # type: ignore
            print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
            sys.exit(-1)
        ui_file.close()

        # load the UI and do a basic check
        loader = QUiLoader()
        loader.registerCustomWidget(TextEditFocusChecking)
        widget = loader.load(ui_file, None)
        if not widget:
            print(loader.errorString())
            sys.exit(-1)

        # set the inner widget to the loaded UI
        self.inner = widget

        # define the widget's custom attributes for type hinting

        self.actionOpen_Save_File: QAction = self.inner.actionOpen_Save_File  # type: ignore[attr-defined]
        self.actionReset_to_original_values: QAction = self.inner.actionReset_to_original_values  # type: ignore[attr-defined]
        self.actionSave_changes: QAction = self.inner.actionSave_changes  # type: ignore[attr-defined]
        self.actionAdd_overclock_crafting_materials: QAction = self.inner.actionAdd_overclock_crafting_materials  # type: ignore[attr-defined]
        self.actionSet_All_Classes_to_25: QAction = self.inner.actionSet_All_Classes_to_25  # type: ignore[attr-defined]
        self.actionMax_all_available_weapons: QAction = self.inner.actionMax_all_available_weapons  # type: ignore[attr-defined]

        self.bismor_text: QLabel = self.inner.__getattribute__("bismor_text")
        self.enor_text: QLabel = self.inner.__getattribute__("enor_text")
        self.jadiz_text: QLabel = self.inner.__getattribute__("jadiz_text")
        self.croppa_text: QLabel = self.inner.__getattribute__("croppa_text")
        self.magnite_text: QLabel = self.inner.__getattribute__("magnite_text")
        self.umanite_text: QLabel = self.inner.__getattribute__("umanite_text")

        self.barley_text: QLineEdit = self.inner.__getattribute__("barley_text")
        self.malt_text: QLineEdit = self.inner.__getattribute__("malt_text")
        self.starch_text: QLineEdit = self.inner.__getattribute__("starch_text")
        self.yeast_text: QLineEdit = self.inner.__getattribute__("yeast_text")

        self.error_text: QLineEdit = self.inner.__getattribute__("error_text")
        self.core_text: QLineEdit = self.inner.__getattribute__("core_text")
        self.credits_text: QLineEdit = self.inner.__getattribute__("credits_text")
        self.perk_text: QLineEdit = self.inner.__getattribute__("perk_text")
        self.data_text: QLineEdit = self.inner.__getattribute__("data_text")
        self.phazy_text: QLineEdit = self.inner.__getattribute__("phazy_text")

        self.classes_group: QGroupBox = self.inner.__getattribute__("classes_group")
        self.driller_xp: TextEditFocusChecking = self.inner.driller_xp  # type: ignore[attr-defined]
        self.driller_lvl_text: TextEditFocusChecking = self.inner.driller_lvl_text  # type: ignore[attr-defined]
        self.driller_xp_2: TextEditFocusChecking = self.inner.driller_xp_2  # type: ignore[attr-defined]
        self.driller_promo_box: QComboBox = self.inner.driller_promo_box  # type: ignore[attr-defined]
        self.engineer_xp: TextEditFocusChecking = self.inner.engineer_xp  # type: ignore[attr-defined]
        self.engineer_lvl_text: TextEditFocusChecking = self.inner.engineer_lvl_text  # type: ignore[attr-defined]
        self.engineer_xp_2: TextEditFocusChecking = self.inner.engineer_xp_2  # type: ignore[attr-defined]
        self.engineer_promo_box: QComboBox = self.inner.engineer_promo_box  # type: ignore[attr-defined]
        self.gunner_xp: TextEditFocusChecking = self.inner.__getattribute__("gunner_xp")
        self.gunner_lvl_text: TextEditFocusChecking = self.inner.gunner_lvl_text  # type: ignore[attr-defined]
        self.gunner_xp_2: TextEditFocusChecking = self.inner.gunner_xp_2  # type: ignore[attr-defined]
        self.gunner_promo_box: QComboBox = self.inner.gunner_promo_box  # type: ignore[attr-defined]
        self.scout_xp: TextEditFocusChecking = self.inner.__getattribute__("scout_xp")
        self.scout_lvl_text: TextEditFocusChecking = self.inner.scout_lvl_text  # type: ignore[attr-defined]
        self.scout_xp_2: TextEditFocusChecking = self.inner.scout_xp_2  # type: ignore[attr-defined]
        self.scout_promo_box: QComboBox = self.inner.__getattribute__("scout_promo_box")

        self.season_group: QGroupBox = self.inner.__getattribute__("season_group")
        self.season_xp: TextEditFocusChecking = self.inner.__getattribute__("season_xp")
        self.season_lvl_text: TextEditFocusChecking = self.inner.season_lvl_text  # type: ignore[attr-defined]
        self.scrip_text: QLineEdit = self.inner.__getattribute__("scrip_text")
        self.season_box: QComboBox = self.inner.__getattribute__("season_box")

        self.overclock_tree: QTreeWidget = self.inner.__getattribute__("overclock_tree")
        self.combo_oc_filter: QComboBox = self.inner.__getattribute__("combo_oc_filter")
        self.add_cores_button: QPushButton = self.inner.add_cores_button  # type: ignore[attr-defined]
        self.unforged_list: QListWidget = self.inner.__getattribute__("unforged_list")
        self.remove_selected_ocs: QPushButton = self.inner.remove_selected_ocs  # type: ignore[attr-defined]
        self.remove_all_ocs: QPushButton = self.inner.__getattribute__("remove_all_ocs")

        # set column names for overclock treeview
        self.overclock_tree.setHeaderLabels(["Overclock", "Status", "GUID"])

        # populate the promotion drop downs
        promo_boxes = [
            self.driller_promo_box,
            self.gunner_promo_box,
            self.engineer_promo_box,
            self.scout_promo_box,
        ]
        for i in promo_boxes:
            for j in PROMO_RANKS:
                i.addItem(j)

        # populate the filter drop down for overclocks
        sort_labels: list[str] = ["All", "Unforged", "Forged", "Unacquired"]
        for i in sort_labels:
            self.combo_oc_filter.addItem(i)

    def show(self):
        self.inner.show()

    def setWindowTitle(self, title: str) -> None:
        self.inner.setWindowTitle(title)

    # new stuff
    def init_overclock_tree(self):
        self.overclock_tree.clear()
        overclock_tree = self.overclock_tree.invisibleRootItem()
        build_oc_tree(overclock_tree)
        self.overclock_tree.sortItems(0, Qt.SortOrder.AscendingOrder)

    def get_dwarf_xp(self, dwarf) -> tuple[int, int, int]:
        # gets the total xp, level, and progress to the next level (rem)
        if dwarf == "driller":
            total = int(self.driller_xp.text())
            level = int(self.driller_lvl_text.text())
            rem = int(self.driller_xp_2.text())
        elif dwarf == "engineer":
            total = int(self.engineer_xp.text())
            level = int(self.engineer_lvl_text.text())
            rem = int(self.engineer_xp_2.text())
        elif dwarf == "gunner":
            total = int(self.gunner_xp.text())
            level = int(self.gunner_lvl_text.text())
            rem = int(self.gunner_xp_2.text())
        elif dwarf == "scout":
            total = int(self.scout_xp.text())
            level = int(self.scout_lvl_text.text())
            rem = int(self.scout_xp_2.text())
        else:
            total = rem = level = -1

        return total, level, rem

    def update_xp(self, dwarf, total_xp=0) -> None:
        # updates the xp fields for the specified dwarf with the new xp total
        if total_xp > 315000:  # max xp check
            total_xp = 315000
        level, remainder = utils.xp_total_to_level(total_xp)  # transform XP total
        bad_dwarf = False  # check for possible weirdness
        if dwarf == "driller":
            total_box = self.driller_xp
            level_box = self.driller_lvl_text
            remainder_box = self.driller_xp_2
        elif dwarf == "engineer":
            total_box = self.engineer_xp
            level_box = self.engineer_lvl_text
            remainder_box = self.engineer_xp_2
        elif dwarf == "gunner":
            total_box = self.gunner_xp
            level_box = self.gunner_lvl_text
            remainder_box = self.gunner_xp_2
        elif dwarf == "scout":
            total_box = self.scout_xp
            level_box = self.scout_lvl_text
            remainder_box = self.scout_xp_2
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
            Stats.dwarf_promo[Dwarf.SCOUT]
            if self.scout_promo_box.currentIndex() == MAX_BADGES
            else self.scout_promo_box.currentIndex()
        )
        e_promo: int = (
            Stats.dwarf_promo[Dwarf.ENGINEER]
            if self.engineer_promo_box.currentIndex() == MAX_BADGES
            else self.engineer_promo_box.currentIndex()
        )
        g_promo: int = (
            Stats.dwarf_promo[Dwarf.GUNNER]
            if self.gunner_promo_box.currentIndex() == MAX_BADGES
            else self.gunner_promo_box.currentIndex()
        )
        d_promo: int = (
            Stats.dwarf_promo[Dwarf.DRILLER]
            if self.driller_promo_box.currentIndex() == MAX_BADGES
            else self.driller_promo_box.currentIndex()
        )

        try:
            s_level = int(self.scout_lvl_text.text())
            e_level = int(self.engineer_lvl_text.text())
            g_level = int(self.gunner_lvl_text.text())
            d_level = int(self.driller_lvl_text.text())
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

        self.classes_group.setTitle(f"Classes - Rank {rank + 1} {rem}/3, {title}")


def build_oc_tree(tree: QTreeWidgetItem) -> None:
    oc_dict = Stats.build_oc_dict()
    for char, weapons in oc_dict.items():
        char_entry = QTreeWidgetItem(tree)
        char_entry.setText(0, char)
        for weapon, oc_names in weapons.items():
            weapon_entry = QTreeWidgetItem(char_entry)
            weapon_entry.setText(0, weapon)
            for name, uuid in oc_names.items():
                oc_entry = QTreeWidgetItem(weapon_entry)
                oc_entry.setText(0, name)
                oc_entry.setText(1, Stats.guid_dict[uuid]["status"])
                oc_entry.setText(2, uuid)
