import os
import sys

from definitions import PROMO_RANKS
from helpers.overclock import Overclock

from PySide6.QtCore import QFile, QIODevice, Signal, Qt
from PySide6.QtGui import QAction, QFocusEvent
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (QComboBox, QGroupBox, QLabel, QLineEdit,
                               QListWidget, QPushButton, QTreeWidget, QTreeWidgetItem,
                               QListWidgetItem, QFileDialog)


class TextEditFocusChecking(QLineEdit):
    focus_out_signal = Signal(str, int)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def focusOutEvent(self, e: QFocusEvent) -> None:
        # check for blank text
        box: str = self.objectName()
        if self.text() == "":
            return super().focusOutEvent(e)

        value = int(self.text())
        self.focus_out_signal.emit(box, value)
        return super().focusOutEvent(e)


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

    def show_empty_oc_tree(self):
        overclock_tree = self.overclock_tree.invisibleRootItem()
        error_text = QTreeWidgetItem(overclock_tree)
        error_text.setText(0, "No dwarf promoted yet")
        self.add_cores_button.setEnabled(False)

    def build_oc_tree(self, oc_dict: dict, guid_dict: dict) -> None:
        overclock_tree = self.overclock_tree.invisibleRootItem()

        self.make_weapon_oc_tree(overclock_tree, oc_dict, guid_dict)
        self.make_non_weapon_oc_trees(overclock_tree, oc_dict, guid_dict)

        self.overclock_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
        self.add_cores_button.setEnabled(True)

    def make_non_weapon_oc_trees(
        self,
        tree: QTreeWidgetItem,
        oc_dict: dict[str, dict[str, dict]],
        guid_dict: dict
    ):
        for category in oc_dict.keys():
            if category == "Weapon":
                continue
            non_weapon_category = QTreeWidgetItem(tree)
            non_weapon_category.setText(0, category)
            for oc_name, dwarves in oc_dict[category].items():
                char_entry = QTreeWidgetItem(non_weapon_category)
                char_entry.setText(0, oc_name)
                for dwarf, uuid in dwarves.items():
                    oc_entry = QTreeWidgetItem(char_entry)
                    oc_entry.setText(0, dwarf)
                    oc_entry.setText(1, guid_dict[uuid].status)
                    oc_entry.setText(2, uuid)

    def make_weapon_oc_tree(
        self,
        tree: QTreeWidgetItem,
        oc_dict: dict[str, dict[str, dict]],
        guid_dict: dict
    ):
        weapon_category_entry = QTreeWidgetItem(tree)
        weapon_category_entry.setText(0, "Weapon")
        for char, weapons in oc_dict["Weapon"].items():
            char_entry = QTreeWidgetItem(weapon_category_entry)
            char_entry.setText(0, char)
            for weapon, oc_names in weapons.items():
                weapon_entry = QTreeWidgetItem(char_entry)
                weapon_entry.setText(0, weapon)
                for name, uuid in oc_names.items():
                    oc_entry = QTreeWidgetItem(weapon_entry)
                    oc_entry.setText(0, name)
                    oc_entry.setText(1, guid_dict[uuid].status)
                    oc_entry.setText(2, uuid)

    def populate_unforged_list(self, unforged: list[Overclock]) -> None:
        # populates the list on acquired but unforged overclocks (includes cosmetics)
        self.unforged_list.clear()
        for oc_item in unforged:
            oc = QListWidgetItem(None)
            if oc_item.category == 'Weapon':
                oc.setText(f"{oc_item.weapon}: {oc_item.name} ({oc_item.guid})")
            elif oc_item.category == 'Cosmetic':
                oc.setText(f"Cosmetic: {oc_item.name} - {oc_item.dwarf} ({oc_item.guid})")
            else:
                oc.setText(f"Unknown: ({oc_item.guid})")
            self.unforged_list.addItem(oc)

    def get_file_name(self, steam_path: str):
        return QFileDialog.getOpenFileName(
            None,
            "Open Save File...",
            steam_path,
            "Player Save Files (*.sav);;All Files (*.*)",
        )[0]
