import json
import os
import struct
import sys
from copy import deepcopy
from re import Match
from sys import platform
from typing import Any

from components import Stats, Dwarf, Resource

from definitions import (
    GUID_RE,
    LATEST_SEASON,
    MAX_BADGES,
    PROMO_RANKS,
    RANK_TITLES,
    RESOURCE_GUIDS,
    SEASON_GUIDS,
    XP_PER_SEASON_LEVEL,
    XP_PER_WEAPON_LEVEL,
    XP_TABLE,
)
from PySide6.QtCore import QCoreApplication, QFile, QIODevice, Qt, Slot
from PySide6.QtGui import QAction, QFocusEvent
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
)

if platform == "win32":
    import winreg


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
        # print(dwarf)

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
                # print('main xp')
                total = value
            elif box.endswith("text"):  # dwarf level box changed
                # print('level xp')
                xp, level, rem = get_dwarf_xp(dwarf)
                if XP_TABLE[value - 1] + rem == xp:
                    total = xp
                else:
                    total = XP_TABLE[value - 1]
            elif box.endswith("2"):  # xp for current level changed
                xp, level, rem = get_dwarf_xp(dwarf)
                total = XP_TABLE[level - 1] + value

            update_xp(dwarf, total)  # update relevant xp fields

        return super().focusOutEvent(e)  # call any other stuff that might happen (?)


def get_dwarf_xp(dwarf) -> tuple[int, int, int]:
    # gets the total xp, level, and progress to the next level (rem)
    if dwarf == "driller":
        total = int(widget.driller_xp.text())
        level = int(widget.driller_lvl_text.text())
        rem = int(widget.driller_xp_2.text())
    elif dwarf == "engineer":
        total = int(widget.engineer_xp.text())
        level = int(widget.engineer_lvl_text.text())
        rem = int(widget.engineer_xp_2.text())
    elif dwarf == "gunner":
        total = int(widget.gunner_xp.text())
        level = int(widget.gunner_lvl_text.text())
        rem = int(widget.gunner_xp_2.text())
    elif dwarf == "scout":
        total = int(widget.scout_xp.text())
        level = int(widget.scout_lvl_text.text())
        rem = int(widget.scout_xp_2.text())
    else:
        total = rem = level = -1

    return total, level, rem


def update_xp(dwarf, total_xp=0) -> None:
    # updates the xp fields for the specified dwarf with the new xp total
    if total_xp > 315000:  # max xp check
        total_xp = 315000
    level, remainder = xp_total_to_level(total_xp)  # transform XP total
    bad_dwarf = False  # check for possible weirdness
    if dwarf == "driller":
        total_box = widget.driller_xp
        level_box = widget.driller_lvl_text
        remainder_box = widget.driller_xp_2
    elif dwarf == "engineer":
        total_box = widget.engineer_xp
        level_box = widget.engineer_lvl_text
        remainder_box = widget.engineer_xp_2
    elif dwarf == "gunner":
        total_box = widget.gunner_xp
        level_box = widget.gunner_lvl_text
        remainder_box = widget.gunner_xp_2
    elif dwarf == "scout":
        total_box = widget.scout_xp
        level_box = widget.scout_lvl_text
        remainder_box = widget.scout_xp_2
    else:
        print("no valid dward specified")
        bad_dwarf = True

    if not bad_dwarf:  # update xp totals
        total_box.setText(str(total_xp))
        level_box.setText(str(level))
        remainder_box.setText(str(remainder))

    update_rank()


def update_rank() -> None:
    s_promo: int = (
        Stats.dwarf_promo[Dwarf.SCOUT]
        if widget.scout_promo_box.currentIndex() == MAX_BADGES
        else widget.scout_promo_box.currentIndex()
    )
    e_promo: int = (
        Stats.dwarf_promo[Dwarf.ENGINEER]
        if widget.engineer_promo_box.currentIndex() == MAX_BADGES
        else widget.engineer_promo_box.currentIndex()
    )
    g_promo: int = (
        Stats.dwarf_promo[Dwarf.GUNNER]
        if widget.gunner_promo_box.currentIndex() == MAX_BADGES
        else widget.gunner_promo_box.currentIndex()
    )
    d_promo: int = (
        Stats.dwarf_promo[Dwarf.DRILLER]
        if widget.driller_promo_box.currentIndex() == MAX_BADGES
        else widget.driller_promo_box.currentIndex()
    )

    try:
        s_level = int(widget.scout_lvl_text.text())
        e_level = int(widget.engineer_lvl_text.text())
        g_level = int(widget.gunner_lvl_text.text())
        d_level = int(widget.driller_lvl_text.text())
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
    except:
        rank = 1
        rem = 0

    try:
        title: str = RANK_TITLES[rank]
    except:
        title = "Lord of the Deep"

    widget.classes_group.setTitle(f"Classes - Rank {rank + 1} {rem}/3, {title}")


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

        # connect file opening function to menu item
        self.actionOpen_Save_File.triggered.connect(open_file)
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

        # for k,v in season_guids.items():
        #     widget.season_picker.addItem(f'Season {v}')

        # populate the filter drop down for overclocks
        sort_labels: list[str] = ["All", "Unforged", "Forged", "Unacquired"]
        for i in sort_labels:
            self.combo_oc_filter.addItem(i)

        # connect functions to buttons and menu items
        self.actionSave_changes.triggered.connect(save_changes)
        self.actionSet_All_Classes_to_25.triggered.connect(set_all_25)
        self.actionAdd_overclock_crafting_materials.triggered.connect(add_crafting_mats)
        self.actionReset_to_original_values.triggered.connect(reset_values)
        self.actionMax_all_available_weapons.triggered.connect(
            max_all_available_weapon_maintenance
        )
        self.combo_oc_filter.currentTextChanged.connect(filter_overclocks)
        self.season_box.currentTextChanged.connect(update_season_data)
        # widget.overclock_tree.customContextMenuRequested.connect(oc_ctx_menu)
        self.add_cores_button.clicked.connect(add_cores)
        self.remove_all_ocs.clicked.connect(remove_all_ocs)
        self.remove_selected_ocs.clicked.connect(remove_selected_ocs)
        self.driller_promo_box.currentIndexChanged.connect(update_rank)
        self.engineer_promo_box.currentIndexChanged.connect(update_rank)
        self.gunner_promo_box.currentIndexChanged.connect(update_rank)
        self.scout_promo_box.currentIndexChanged.connect(update_rank)

    def show(self):
        self.inner.show()

    def setWindowTitle(self, title: str) -> None:
        self.inner.setWindowTitle(title)


@Slot()  # type: ignore
def open_file() -> None:
    global file_name
    global save_data
    # open file dialog box, start in steam install path if present
    file_name = QFileDialog.getOpenFileName(
        None,
        "Open Save File...",
        steam_path,
        "Player Save Files (*.sav);;All Files (*.*)",
    )[0]
    # print('about to open file')

    if not file_name:
        return

    widget.setWindowTitle(f"DRG Save Editor - {file_name}")  # window-dressing
    with open(file_name, "rb") as f:
        save_data = f.read()

    # make a backup of the save file in case of weirdness or bugs
    with open(f"{file_name}.old", "wb") as backup:
        backup.write(save_data)

    # print(f'opened: {file_name}')

    # enable widgets that don't work without a save file present
    widget.actionSave_changes.setEnabled(True)
    widget.actionReset_to_original_values.setEnabled(True)
    widget.combo_oc_filter.setEnabled(True)

    # initialize and populate the text fields
    init_values(save_data)
    reset_values()
    update_rank()

    global forged_ocs
    global unacquired_ocs
    global unforged_ocs

    # print('before ocs')
    # parse save file and categorize weapon overclocks
    forged_ocs, unacquired_ocs, unforged_ocs = get_overclocks(save_data, guid_dict)
    # print('after ocs')

    # clear and initialize overclock tree view
    widget.overclock_tree.clear()
    overclock_tree = widget.overclock_tree.invisibleRootItem()
    build_oc_tree(overclock_tree, guid_dict)
    widget.overclock_tree.sortItems(0, Qt.SortOrder.AscendingOrder)

    # populate list of unforged ocs
    unforged_list = widget.unforged_list
    populate_unforged_list(unforged_list, unforged_ocs)


def populate_unforged_list(list_widget: QListWidget, unforged: dict) -> None:
    # populates the list on acquired but unforged overclocks (includes cosmetics)
    list_widget.clear()
    for k, v in unforged.items():
        oc = QListWidgetItem(None)
        try:  # cosmetic overclocks don't have these values
            oc.setText(f'{v["weapon"]}: {v["name"]} ({k})')
        except:
            oc.setText(f"Cosmetic: {k}")
        list_widget.addItem(oc)


def store_season_changes(season_num):
    new_xp = widget.season_xp.text()
    new_scrip = widget.scrip_text.text()
    if new_xp and new_scrip:
        Stats.season_data[season_num] = {
            "xp": int(new_xp)
            + XP_PER_SEASON_LEVEL * int(widget.season_lvl_text.text()),
            "scrip": int(new_scrip),
        }


def update_season_data() -> None:
    global season_selected

    # store textbox values before changing which season's data is being viewed
    # currently displayed values can be saved before saving the new file data
    store_season_changes(season_selected)
    if widget.season_box.currentText():
        season_selected = int(widget.season_box.currentText())

    # refresh display
    reset_season_data()


def get_season_data(save_bytes: bytes, season_guid: str) -> dict[str, int]:
    # scrip_marker = bytes.fromhex("546F6B656E73")
    season_marker: bytes = bytes.fromhex(season_guid)
    season_marker_pos: int = save_bytes.find(season_marker)
    # season data does not exist
    if season_marker_pos == -1:
        raise ValueError("Season missing")

    season_xp_offset = 169
    scrip_offset = 209

    season_xp_pos = save_bytes.find(season_marker) + season_xp_offset
    scrip_pos = save_bytes.find(season_marker) + scrip_offset

    season_xp = struct.unpack("i", save_bytes[season_xp_pos : season_xp_pos + 4])[0]
    scrip = struct.unpack("i", save_bytes[scrip_pos : scrip_pos + 4])[0]

    return {"xp": season_xp, "scrip": scrip}


def xp_total_to_level(xp: int) -> tuple[int, int]:
    for i in XP_TABLE:
        if xp < i:
            level: int = XP_TABLE.index(i)
            remainder: int = xp - XP_TABLE[level - 1]
            return (level, remainder)
    return (25, 0)


def get_credits(save_bytes: bytes):
    marker = b"Credits"
    offset = 33
    pos = save_bytes.find(marker) + offset
    money = struct.unpack("i", save_bytes[pos : pos + 4])[0]

    return money


def get_perk_points(save_bytes: bytes):
    marker = b"PerkPoints"
    offset = 36
    if save_bytes.find(marker) == -1:
        perk_points = 0
    else:
        pos = save_bytes.find(marker) + offset
        perk_points = struct.unpack("i", save_bytes[pos : pos + 4])[0]

    return perk_points


def build_oc_dict(guid_dict: dict[str, Any]) -> dict[str, Any]:
    overclocks: dict[str, Any] = dict()

    for v in guid_dict.values():
        try:
            overclocks.update({v["class"]: dict()})
        except:
            pass

    for v in guid_dict.values():
        try:
            overclocks[v["class"]].update({v["weapon"]: dict()})
        except:
            pass

    for k, v in guid_dict.items():
        try:
            overclocks[v["class"]][v["weapon"]].update({v["name"]: k})
        except:
            pass

    return overclocks


def build_oc_tree(tree: QTreeWidgetItem, source_dict: dict[str, Any]) -> None:
    oc_dict = build_oc_dict(source_dict)
    # entry = QTreeWidgetItem(None)
    for char, weapons in oc_dict.items():
        # dwarves[dwarf] = QTreeWidgetItem(tree)
        char_entry = QTreeWidgetItem(tree)
        char_entry.setText(0, char)
        for weapon, oc_names in weapons.items():
            weapon_entry = QTreeWidgetItem(char_entry)
            weapon_entry.setText(0, weapon)
            for name, uuid in oc_names.items():
                oc_entry = QTreeWidgetItem(weapon_entry)
                oc_entry.setText(0, name)
                oc_entry.setText(1, source_dict[uuid]["status"])
                oc_entry.setText(2, uuid)


def get_overclocks(
    save_bytes: bytes, guid_source: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    search_term = b"ForgedSchematics"
    search_end = b"SkinFixupCounter"
    pos = save_bytes.find(search_term)
    end_pos = save_bytes.find(search_end)
    if end_pos == -1:
        search_end = b"bFirstSchematicMessageShown"
        end_pos = save_bytes.find(search_end)

    for i in guid_source.values():
        i["status"] = "Unacquired"

    guids = deepcopy(guid_source)
    if pos > 0:
        oc_data = save_bytes[pos:end_pos]
        oc_list_offset = 141

        # print(f'pos: {pos}, end_pos: {end_pos}')
        # print(f'owned_pos: {owned}, diff: {owned-pos}')
        # has_unforged = True if oc_data.find(b'Owned') else False
        has_unforged = oc_data.find(b"Owned") > 0
        # print(has_unforged) # bool
        num_forged = struct.unpack("i", save_bytes[pos + 63 : pos + 67])[0]
        forged = dict()
        # print(num_forged)

        for i in range(num_forged):
            uuid = (
                save_bytes[
                    pos
                    + oc_list_offset
                    + (i * 16) : pos
                    + oc_list_offset
                    + (i * 16)
                    + 16
                ]
                .hex()
                .upper()
            )
            try:
                a = guids[uuid]
                guid_source[uuid]["status"] = "Forged"
                a["status"] = "Forged"
                del guids[uuid]
                forged.update({uuid: a})

                # print('success')
            except:
                # print(f'Error: {e}')
                pass

        # print('after forged extraction')
        if has_unforged:
            unforged = dict()
            # print('in unforged loop')
            num_pos = save_bytes.find(b"Owned", pos) + 62
            num_unforged = struct.unpack("i", save_bytes[num_pos : num_pos + 4])[0]
            unforged_pos = num_pos + 77
            for i in range(num_unforged):
                uuid = (
                    save_bytes[unforged_pos + (i * 16) : unforged_pos + (i * 16) + 16]
                    .hex()
                    .upper()
                )
                try:
                    unforged.update({uuid: guids[uuid]})
                    guid_source[uuid]["status"] = "Unforged"
                    unforged[uuid]["status"] = "Unforged"
                except KeyError:
                    unforged.update({uuid: "Cosmetic"})
        else:
            unforged = dict()
    else:
        forged = dict()
        unforged = dict()

    # print('after unforged extraction')
    # print(f'unforged: {unforged}')
    # forged OCs, unacquired OCs, unforged OCs
    return (forged, guids, unforged)


@Slot()  # type: ignore
def filter_overclocks() -> None:
    item_filter = widget.combo_oc_filter.currentText()
    # forged_ocs, unacquired_ocs, unforged_ocs = get_overclocks(save_data, guid_dict)
    # print(item_filter)
    tree = widget.overclock_tree
    tree_root = tree.invisibleRootItem()

    for i in range(tree_root.childCount()):
        # print(tree_root.child(i).text(0))
        dwarf = tree_root.child(i)
        for j in range(dwarf.childCount()):
            weapon = dwarf.child(j)
            # print(f'\t{weapon.text(0)}')
            for k in range(weapon.childCount()):
                oc = weapon.child(k)
                # print(f'\t\t{oc.text(0)}')
                if oc.text(1) == item_filter or item_filter == "All":
                    oc.setHidden(False)
                else:
                    oc.setHidden(True)


# @Slot()  # type: ignore
# def oc_ctx_menu(pos) -> None:
#     # oc_context_menu = make_oc_context_menu()
#     # global oc_context_menu
#     ctx_menu = QMenu(widget.overclock_tree)
#     add_act = ctx_menu.addAction("Add Core(s) to Inventory")
#     global_pos = QCursor().pos()
#     action: QAction = ctx_menu.exec_(global_pos)
#     if action == add_act:
#         add_cores()
#     # add_act.triggered.connect(add_cores())


@Slot()  # type: ignore
def add_cores() -> None:
    # print("add cores")
    global unforged_ocs
    global unacquired_ocs
    tree = widget.overclock_tree
    selected = tree.selectedItems()
    items_to_add = list()
    for i in selected:
        if i.text(1) == "Unacquired" and i.text(2) in unacquired_ocs:
            items_to_add.append(f"{i.parent().text(0)}: {i.text(0)} ({i.text(2)})")
            guid_dict[i.text(2)]["status"] = "Unforged"
            unforged_ocs.update({i.text(2): guid_dict[i.text(2)]})
            del unacquired_ocs[i.text(2)]
            guid_dict[i.text(2)]["status"] = "Unforged"

    core_list = widget.unforged_list
    for item in items_to_add:
        core_list.addItem(item)

    core_list.sortItems()
    filter_overclocks()


@Slot()  # type: ignore
def save_changes() -> None:
    changes: dict[str, Any] = get_values()
    changes["unforged"] = unforged_ocs
    # pp(changes)
    save_file: bytes = make_save_file(file_name, changes)
    with open(file_name, "wb") as f:
        f.write(save_file)


def make_save_file(file_path, new_values) -> bytes:
    with open(file_path, "rb") as f:
        save_data: bytes = f.read()

    # write resources
    # resource_bytes = list()
    # res_guids = deepcopy(resource_guids)
    resources: dict[Resource, int] = {
        Resource.YEAST: new_values["brewing"]["yeast"],
        Resource.STARCH: new_values["brewing"]["starch"],
        Resource.BARLEY: new_values["brewing"]["barley"],
        Resource.BISMOR: new_values["minerals"]["bismor"],
        Resource.ENOR: new_values["minerals"]["enor"],
        Resource.MALT: new_values["brewing"]["malt"],
        Resource.UMANITE: new_values["minerals"]["umanite"],
        Resource.JADIZ: new_values["minerals"]["jadiz"],
        Resource.CROPPA: new_values["minerals"]["croppa"],
        Resource.MAGNITE: new_values["minerals"]["magnite"],
        Resource.ERROR: new_values["misc"]["error"],
        Resource.CORES: new_values["misc"]["cores"],
        Resource.DATA: new_values["misc"]["data"],
        Resource.PHAZ: new_values["misc"]["phazyonite"],
    }

    res_marker = b"OwnedResources"
    res_pos: int = save_data.find(res_marker) + 85
    res_length = struct.unpack("i", save_data[res_pos - 4 : res_pos])[0] * 20
    res_bytes: bytes = save_data[res_pos : res_pos + res_length]

    for k, v in resources.items():
        if res_bytes.find(bytes.fromhex(RESOURCE_GUIDS[k])) > -1:
            pos: int = res_bytes.find(bytes.fromhex(RESOURCE_GUIDS[k]))
            res_bytes = (
                res_bytes[: pos + 16] + struct.pack("f", v) + res_bytes[pos + 20 :]
            )
            # print(
            #     f'res: {k}, pos: {pos}, guid: {res_guids[k]}, val: {v}, v bytes: {struct.pack("f", v)}'
            # )

    # print(res_bytes.hex().upper())

    save_data = save_data[:res_pos] + res_bytes + save_data[res_pos + res_length :]

    # write credits
    cred_marker = b"Credits"
    cred_pos: int = save_data.find(cred_marker) + 33
    cred_bytes: bytes = struct.pack("i", new_values["misc"]["credits"])
    save_data = save_data[:cred_pos] + cred_bytes + save_data[cred_pos + 4 :]

    # write perk points
    if new_values["misc"]["perks"] > 0:
        perks_marker = b"PerkPoints"
        perks_bytes: bytes = struct.pack("i", new_values["misc"]["perks"])
        if save_data.find(perks_marker) != -1:
            perks_pos: int = save_data.find(perks_marker) + 36
            save_data = save_data[:perks_pos] + perks_bytes + save_data[perks_pos + 4 :]
        else:
            perks_entry: bytes = (
                b"\x0B\x00\x00\x00\x50\x65\x72\x6B\x50\x6F\x69\x6E\x74\x73\x00\x0C\x00\x00\x00\x49\x6E\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00"
                + perks_bytes
            )
            perks_pos = save_data.find(
                b"\x11\x00\x00\x00\x55\x6E\x4C\x6F\x63\x6B\x65\x64\x4D\x69\x73\x73\x69\x6F\x6E\x73\x00\x0E"
            )
            save_data = (
                save_data[:perks_pos] + perks_entry + save_data[perks_pos:]
            )  # inserting data, not overwriting
    # print(f'2. {len(save_data)}')
    # write XP
    en_marker = b"\x85\xEF\x62\x6C\x65\xF1\x02\x4A\x8D\xFE\xB5\xD0\xF3\x90\x9D\x2E\x03\x00\x00\x00\x58\x50"
    sc_marker = b"\x30\xD8\xEA\x17\xD8\xFB\xBA\x4C\x95\x30\x6D\xE9\x65\x5C\x2F\x8C\x03\x00\x00\x00\x58\x50"
    dr_marker = b"\x9E\xDD\x56\xF1\xEE\xBC\xC5\x48\x8D\x5B\x5E\x5B\x80\xB6\x2D\xB4\x03\x00\x00\x00\x58\x50"
    gu_marker = b"\xAE\x56\xE1\x80\xFE\xC0\xC4\x4D\x96\xFA\x29\xC2\x83\x66\xB9\x7B\x03\x00\x00\x00\x58\x50"
    offset = 48
    eng_xp_pos: int = save_data.find(en_marker) + offset
    scout_xp_pos: int = save_data.find(sc_marker) + offset
    drill_xp_pos: int = save_data.find(dr_marker) + offset
    gun_xp_pos: int = save_data.find(gu_marker) + offset

    eng_xp_bytes: bytes = struct.pack("i", new_values["xp"]["engineer"]["xp"])
    scout_xp_bytes: bytes = struct.pack("i", new_values["xp"]["scout"]["xp"])
    drill_xp_bytes: bytes = struct.pack("i", new_values["xp"]["driller"]["xp"])
    gun_xp_bytes: bytes = struct.pack("i", new_values["xp"]["gunner"]["xp"])

    promo_offset = 108
    levels_per_promo = 25
    promo_levels_offset = 56
    eng_promo_pos: int = eng_xp_pos + promo_offset
    scout_promo_pos: int = scout_xp_pos + promo_offset
    drill_promo_pos: int = drill_xp_pos + promo_offset
    gun_promo_pos: int = gun_xp_pos + promo_offset

    eng_promo_bytes: bytes = struct.pack("i", new_values["xp"]["engineer"]["promo"])
    eng_promo_level_bytes: bytes = struct.pack(
        "i", new_values["xp"]["engineer"]["promo"] * levels_per_promo
    )
    scout_promo_bytes: bytes = struct.pack("i", new_values["xp"]["scout"]["promo"])
    scout_promo_level_bytes: bytes = struct.pack(
        "i", new_values["xp"]["scout"]["promo"] * levels_per_promo
    )
    drill_promo_bytes: bytes = struct.pack("i", new_values["xp"]["driller"]["promo"])
    drill_promo_level_bytes: bytes = struct.pack(
        "i", new_values["xp"]["driller"]["promo"] * levels_per_promo
    )
    gun_promo_bytes: bytes = struct.pack("i", new_values["xp"]["gunner"]["promo"])
    gun_promo_level_bytes: bytes = struct.pack(
        "i", new_values["xp"]["gunner"]["promo"] * levels_per_promo
    )

    save_data = save_data[:eng_xp_pos] + eng_xp_bytes + save_data[eng_xp_pos + 4 :]
    save_data = (
        save_data[:eng_promo_pos] + eng_promo_bytes + save_data[eng_promo_pos + 4 :]
    )
    save_data = (
        save_data[: eng_promo_pos + promo_levels_offset]
        + eng_promo_level_bytes
        + save_data[eng_promo_pos + promo_levels_offset + 4 :]
    )

    save_data = (
        save_data[:scout_xp_pos] + scout_xp_bytes + save_data[scout_xp_pos + 4 :]
    )
    save_data = (
        save_data[:scout_promo_pos]
        + scout_promo_bytes
        + save_data[scout_promo_pos + 4 :]
    )
    save_data = (
        save_data[: scout_promo_pos + promo_levels_offset]
        + scout_promo_level_bytes
        + save_data[scout_promo_pos + promo_levels_offset + 4 :]
    )

    save_data = (
        save_data[:drill_xp_pos] + drill_xp_bytes + save_data[drill_xp_pos + 4 :]
    )
    save_data = (
        save_data[:drill_promo_pos]
        + drill_promo_bytes
        + save_data[drill_promo_pos + 4 :]
    )
    save_data = (
        save_data[: drill_promo_pos + promo_levels_offset]
        + drill_promo_level_bytes
        + save_data[drill_promo_pos + promo_levels_offset + 4 :]
    )

    save_data = save_data[:gun_xp_pos] + gun_xp_bytes + save_data[gun_xp_pos + 4 :]
    save_data = (
        save_data[:gun_promo_pos] + gun_promo_bytes + save_data[gun_promo_pos + 4 :]
    )
    save_data = (
        save_data[: gun_promo_pos + promo_levels_offset]
        + gun_promo_level_bytes
        + save_data[gun_promo_pos + promo_levels_offset + 4 :]
    )
    # print(f'3. {len(save_data)}')
    # write overclocks
    search_term = b"ForgedSchematics"  # \x00\x0F\x00\x00\x00Struct'
    search_end = b"SkinFixupCounter"
    pos = save_data.find(search_term)
    end_pos: int = (
        save_data.find(search_end) - 4
    )  # means I don't have to hardcode the boundary bytes
    # print(f'pos: {pos}, end_pos: {end_pos}')

    # this is currently broken, don't care enough to put more effort into fixing it.
    # the problem seems to be related to the \x5D in the middle of the first hex string,
    # this changes to \x6D when going from 1->2 overclocks. Similarly, the \x10 in the
    # middle of the second hex string (\x74\x79\x00\x10 <- this one) changes to \x20
    # when going from 1->2 overclocks. My testing involved one weapon OC and one cosmetic OC.
    # If someone can provide a save file with more than 2 overclocks waiting to be forged,
    # that might help figure it out, but I'm currently stumped.
    if pos > 0:
        num_forged = struct.unpack("i", save_data[pos + 63 : pos + 67])[0]
        unforged_ocs = new_values["unforged"]

        schematic_save_marker = b"SchematicSave"
        schematic_save_offset = 33
        schematic_save_pos = (
            save_data.find(schematic_save_marker) + schematic_save_offset
        )
        schematic_save_end_pos = schematic_save_pos + 8
        schematic_save_size = b""

        if len(unforged_ocs) > 0:
            ocs: bytes = (
                b"\x10\x00\x00\x00\x4F\x77\x6E\x65\x64\x53\x63\x68\x65\x6D\x61\x74\x69\x63\x73\x00\x0E\x00\x00\x00\x41\x72\x72\x61\x79\x50\x72\x6F\x70\x65\x72\x74\x79\x00"
                # number of bytes between position of first "OwnedSchematic" and end_pos, -62, as a 64bit unsigned integer
                + struct.pack("Q", 139 + len(unforged_ocs) * 16 - 62)
                + b"\x0F\x00\x00\x00\x53\x74\x72\x75\x63\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00\x00"
                # number of unforged ocs, stored as a 32bit unsigned integer
                + struct.pack("I", len(unforged_ocs))
                + b"\x10\x00\x00\x00\x4F\x77\x6E\x65\x64\x53\x63\x68\x65\x6D\x61\x74\x69\x63\x73\x00\x0F\x00\x00\x00\x53\x74\x72\x75\x63\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00"
                # number of bytes taken up by the GUID's of the unforged oc's, stored as a 64bit unsigned integer
                + struct.pack("Q", len(unforged_ocs) * 16)
                + b"\x05\x00\x00\x00\x47\x75\x69\x64\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            )
            # print(ocs)
            uuids: list[bytes] = [bytes.fromhex(i) for i in unforged_ocs.keys()]
            for i in uuids:
                ocs += i

            # the number of bytes between position of first "SchematicSave" and end_pos, -17, as a 64bit unsigned integer
            schematic_save_size = struct.pack(
                "Q",
                139 + (141 + num_forged * 16) + 4 + (139 + len(unforged_ocs) * 16) - 17,
            )

        else:
            ocs = b""
            # the number of bytes between position of first "SchematicSave" and end_pos, -17, as a 64bit unsigned integer
            schematic_save_size = struct.pack("Q", 139 + (141 + num_forged * 16) - 17)

        save_data = (
            save_data[: pos + (num_forged * 16) + 141] + ocs + save_data[end_pos:]
        )
        save_data = (
            save_data[:schematic_save_pos]
            + schematic_save_size
            + save_data[schematic_save_end_pos:]
        )

    # write season data
    for season_num, season_guid in SEASON_GUIDS.items():
        season_marker: bytes = bytes.fromhex(season_guid)
        season_marker_pos: int = save_data.find(season_marker)
        # season data does not exist
        if season_marker_pos == -1:
            print(f"Season {season_num} missing")
            continue

        season_xp_offset = 169
        season_xp_pos: int = season_marker_pos + season_xp_offset
        # scrip_marker = b"Tokens"
        scrip_offset = 209
        scrip_pos: int = season_marker_pos + scrip_offset

        save_data = (
            save_data[:season_xp_pos]
            + struct.pack("i", new_values["season"][season_num]["xp"])
            + save_data[season_xp_pos + 4 :]
        )
        save_data = (
            save_data[:scrip_pos]
            + struct.pack("i", new_values["season"][season_num]["scrip"])
            + save_data[scrip_pos + 4 :]
        )

    # write weapon maintenance data
    global weapon_stats
    OFFSET_WEAPON_XP = 0x6E
    OFFSET_WEAPON_LEVEL_UP = 0xCA
    if weapon_stats:
        for weapon_pos, _ in weapon_stats.items():
            xp = struct.pack("i", weapon_stats[weapon_pos][0])
            level_up = struct.pack("b", weapon_stats[weapon_pos][2])
            save_data = (
                save_data[: weapon_pos + OFFSET_WEAPON_XP]
                + xp
                + save_data[weapon_pos + OFFSET_WEAPON_XP + 4 :]
            )
            save_data = (
                save_data[: weapon_pos + OFFSET_WEAPON_LEVEL_UP]
                + level_up
                + save_data[weapon_pos + OFFSET_WEAPON_LEVEL_UP + 1 :]
            )

    return save_data
    # with open(f"{file_name}", "wb") as t:
    #     t.write(save_data)


@Slot()  # type: ignore
def set_all_25() -> None:
    update_xp("driller", 315000)
    update_xp("engineer", 315000)
    update_xp("gunner", 315000)
    update_xp("scout", 315000)


@Slot()  # type: ignore
def max_all_available_weapon_maintenance() -> None:
    global weapon_stats
    weapon_stats = dict()
    for weapon, [_, level, _] in stats["weapons"].items():
        xp_needed = 0
        for xp_level, xp_for_levelup in XP_PER_WEAPON_LEVEL.items():
            if level < xp_level:
                xp_needed += xp_for_levelup
        if xp_needed:
            weapon_stats[weapon] = [xp_needed, level, True]


@Slot()  # type: ignore
def reset_values() -> None:
    global save_data
    global unforged_ocs
    global unacquired_ocs
    global forged_ocs
    Stats.get_initial_stats(save_data)

    # Sets all minerals to the values in Stats
    widget.bismor_text.setText(str(Stats.resources[Resource.BISMOR]))
    widget.enor_text.setText(str(Stats.resources[Resource.ENOR]))
    widget.jadiz_text.setText(str(Stats.resources[Resource.JADIZ]))
    widget.croppa_text.setText(str(Stats.resources[Resource.CROPPA]))
    widget.magnite_text.setText(str(Stats.resources[Resource.MAGNITE]))
    widget.umanite_text.setText(str(Stats.resources[Resource.UMANITE]))

    # Sets all brewing materials to the values in Stats
    widget.yeast_text.setText(str(Stats.resources[Resource.YEAST]))
    widget.starch_text.setText(str(Stats.resources[Resource.STARCH]))
    widget.malt_text.setText(str(Stats.resources[Resource.MALT]))
    widget.barley_text.setText(str(Stats.resources[Resource.BARLEY]))

    # Sets all misc resources to the values in Stats
    widget.error_text.setText(str(Stats.resources[Resource.ERROR]))
    widget.core_text.setText(str(Stats.resources[Resource.CORES]))
    widget.credits_text.setText(str(Stats.credits))
    widget.perk_text.setText(str(Stats.perk_points))
    widget.data_text.setText(str(Stats.resources[Resource.DATA]))
    widget.phazy_text.setText(str(Stats.resources[Resource.PHAZ]))

    # Sets all dwarf XP to the values in Stats
    widget.driller_xp.setText(str(Stats.dwarf_xp[Dwarf.DRILLER]))
    d_xp = xp_total_to_level(Stats.dwarf_xp[Dwarf.DRILLER])
    d_promo = Stats.dwarf_promo[Dwarf.DRILLER]
    widget.driller_lvl_text.setText(str(d_xp[0]))
    widget.driller_xp_2.setText(str(d_xp[1]))
    widget.driller_promo_box.setCurrentIndex(
        d_promo if d_promo < MAX_BADGES else MAX_BADGES
    )

    widget.engineer_xp.setText(str(Stats.dwarf_xp[Dwarf.ENGINEER]))
    e_xp = xp_total_to_level(Stats.dwarf_xp[Dwarf.ENGINEER])
    e_promo = Stats.dwarf_promo[Dwarf.ENGINEER]
    widget.engineer_lvl_text.setText(str(e_xp[0]))
    widget.engineer_xp_2.setText(str(e_xp[1]))
    widget.engineer_promo_box.setCurrentIndex(
        e_promo if e_promo < MAX_BADGES else MAX_BADGES
    )

    widget.gunner_xp.setText(str(Stats.dwarf_xp[Dwarf.GUNNER]))
    g_xp = xp_total_to_level(Stats.dwarf_xp[Dwarf.GUNNER])
    g_promo = Stats.dwarf_promo[Dwarf.GUNNER]
    widget.gunner_lvl_text.setText(str(g_xp[0]))
    widget.gunner_xp_2.setText(str(g_xp[1]))
    widget.gunner_promo_box.setCurrentIndex(
        g_promo if g_promo < MAX_BADGES else MAX_BADGES
    )

    widget.scout_xp.setText(str(Stats.dwarf_xp[Dwarf.SCOUT]))
    s_xp = xp_total_to_level(Stats.dwarf_xp[Dwarf.SCOUT])
    s_promo = Stats.dwarf_promo[Dwarf.SCOUT]
    widget.scout_lvl_text.setText(str(s_xp[0]))
    widget.scout_xp_2.setText(str(s_xp[1]))
    widget.scout_promo_box.setCurrentIndex(
        s_promo if s_promo < MAX_BADGES else MAX_BADGES
    )

    forged_ocs, unacquired_ocs, unforged_ocs = get_overclocks(save_data, guid_dict)
    unforged_list = widget.unforged_list
    populate_unforged_list(unforged_list, unforged_ocs)

    filter_overclocks()
    update_rank()
    reset_season_data()


def reset_season_data():
    season_total_xp = Stats.season_data[season_selected]["xp"]
    widget.season_xp.setText(str(season_total_xp % XP_PER_SEASON_LEVEL))
    widget.season_lvl_text.setText(str(season_total_xp // XP_PER_SEASON_LEVEL))
    widget.scrip_text.setText(str(Stats.season_data[season_selected]["scrip"]))


@Slot()  # type: ignore
def add_crafting_mats() -> None:
    cost: dict[str, int] = {
        "bismor": 0,
        "croppa": 0,
        "jadiz": 0,
        "enor": 0,
        "magnite": 0,
        "umanite": 0,
        "credits": 0,
    }
    for k, v in unforged_ocs.items():
        print(k, v)
        try:
            for i in v["cost"].keys():
                cost[i] += v["cost"][i]
        except:
            print("Cosmetic")
    print(cost)
    add_resources(cost)


def add_resources(res_dict) -> None:
    # res_dict is {'bismor': 123, 'credits': 10000, ...}
    try:
        widget.bismor_text.setText(
            str(int(widget.bismor_text.text()) + res_dict["bismor"])
        )
    except:
        pass
    try:
        widget.croppa_text.setText(
            str(int(widget.croppa_text.text()) + res_dict["croppa"])
        )
    except:
        pass
    try:
        widget.enor_text.setText(str(int(widget.enor_text.text()) + res_dict["enor"]))
    except:
        pass
    try:
        widget.jadiz_text.setText(
            str(int(widget.jadiz_text.text()) + res_dict["jadiz"])
        )
    except:
        pass
    try:
        widget.magnite_text.setText(
            str(int(widget.magnite_text.text()) + res_dict["magnite"])
        )
    except:
        pass
    try:
        widget.umanite_text.setText(
            str(int(widget.umanite_text.text()) + res_dict["umanite"])
        )
    except:
        pass
    try:
        widget.barley_text.setText(
            str(int(widget.barley_text.text()) + res_dict["barley"])
        )
    except:
        pass
    try:
        widget.yeast_text.setText(
            str(int(widget.yeast_text.text()) + res_dict["yeast"])
        )
    except:
        pass
    try:
        widget.malt_text.setText(str(int(widget.malt_text.text()) + res_dict["malt"]))
    except:
        pass
    try:
        widget.starch_text.setText(
            str(int(widget.starch_text.text()) + res_dict["starch"])
        )
    except:
        pass
    try:
        widget.error_text.setText(
            str(int(widget.error_text.text()) + res_dict["error"])
        )
    except:
        pass
    try:
        widget.core_text.setText(str(int(widget.core_text.text()) + res_dict["cores"]))
    except:
        pass
    try:
        widget.credits_text.setText(
            str(int(widget.credits_text.text()) + res_dict["credits"])
        )
    except:
        pass


def init_values(save_data):
    Stats.get_initial_stats(save_data)

    # addItem triggers currentTextChanged which triggers saving of data currently in textbox.
    # if two saves are loaded consecutively, it will cause values in the textbox (from file1)
    # to be saved into storage now (representing file2)
    # remove any text already inside to prevent this
    widget.season_xp.setText("")
    widget.season_lvl_text.setText("")
    widget.scrip_text.setText("")

    # populate the dropdown for season numbers
    for season_num in Stats.season_data.keys():
        widget.season_box.addItem(str(season_num))
    widget.season_box.setCurrentIndex(len(Stats.season_data) - 1)

    if len(Stats.season_data) == 0:
        widget.season_group.setEnabled(False)


def get_values() -> dict[str, Any]:
    ns: dict[str, Any] = dict()
    ns["minerals"] = dict()
    ns["brewing"] = dict()
    ns["misc"] = dict()
    ns["xp"] = {
        "driller": dict(),
        "gunner": dict(),
        "scout": dict(),
        "engineer": dict(),
    }

    ns["minerals"]["bismor"] = int(widget.bismor_text.text())
    ns["minerals"]["croppa"] = int(widget.croppa_text.text())
    ns["minerals"]["enor"] = int(widget.enor_text.text())
    ns["minerals"]["jadiz"] = int(widget.jadiz_text.text())
    ns["minerals"]["magnite"] = int(widget.magnite_text.text())
    ns["minerals"]["umanite"] = int(widget.umanite_text.text())

    ns["brewing"]["yeast"] = int(widget.yeast_text.text())
    ns["brewing"]["starch"] = int(widget.starch_text.text())
    ns["brewing"]["malt"] = int(widget.malt_text.text())
    ns["brewing"]["barley"] = int(widget.barley_text.text())

    ns["xp"]["driller"]["xp"] = int(widget.driller_xp.text())
    ns["xp"]["engineer"]["xp"] = int(widget.engineer_xp.text())
    ns["xp"]["gunner"]["xp"] = int(widget.gunner_xp.text())
    ns["xp"]["scout"]["xp"] = int(widget.scout_xp.text())

    driller_promo = int(widget.driller_promo_box.currentIndex())
    gunner_promo = int(widget.gunner_promo_box.currentIndex())
    scout_promo = int(widget.scout_promo_box.currentIndex())
    engineer_promo = int(widget.engineer_promo_box.currentIndex())

    ns["xp"]["driller"]["promo"] = (
        driller_promo if driller_promo < MAX_BADGES else stats["xp"]["driller"]["promo"]
    )
    ns["xp"]["engineer"]["promo"] = (
        engineer_promo
        if engineer_promo < MAX_BADGES
        else stats["xp"]["engineer"]["promo"]
    )
    ns["xp"]["gunner"]["promo"] = (
        gunner_promo if gunner_promo < MAX_BADGES else stats["xp"]["gunner"]["promo"]
    )
    ns["xp"]["scout"]["promo"] = (
        scout_promo if scout_promo < MAX_BADGES else stats["xp"]["scout"]["promo"]
    )

    ns["misc"]["error"] = int(widget.error_text.text())
    ns["misc"]["cores"] = int(widget.core_text.text())
    ns["misc"]["credits"] = int(widget.credits_text.text())
    ns["misc"]["perks"] = int(widget.perk_text.text())
    ns["misc"]["data"] = int(widget.data_text.text())
    ns["misc"]["phazyonite"] = int(widget.phazy_text.text())

    store_season_changes(season_selected)
    ns["season"] = stats["season-changes"]

    return ns


@Slot()  # type: ignore
def remove_selected_ocs() -> None:
    global unforged_ocs
    global unacquired_ocs
    global file_name
    list_items = widget.unforged_list.selectedItems()
    items_to_remove = list()
    for i in list_items:
        maybe_item_to_remove: Match[str] | None = GUID_RE.search(i.text())
        if maybe_item_to_remove is None:
            continue
        item_to_remove: Match[str] = maybe_item_to_remove

        items_to_remove.append(item_to_remove.group(1))
        item = widget.unforged_list.row(i)
        widget.unforged_list.takeItem(item)

    remove_ocs(items_to_remove)


def remove_ocs(oc_list: list[str]) -> None:
    global unforged_ocs
    global unacquired_ocs
    global guid_dict

    for i in oc_list:
        oc: dict[str, Any] = unforged_ocs[i]
        oc["status"] = "Unacquired"
        guid_dict[i]["status"] = "Unacquired"
        unacquired_ocs.update({i: oc})
        del unforged_ocs[i]

    filter_overclocks()


@Slot()  # type: ignore
def remove_all_ocs() -> None:
    global unforged_ocs
    # unforged_ocs = dict()
    items_to_remove = list()
    unforged_list = widget.unforged_list
    for i in range(unforged_list.count()):
        item = unforged_list.item(i)
        maybe_item_to_remove: Match[str] | None = GUID_RE.search(item.text())
        if maybe_item_to_remove is None:
            continue
        item_to_remove: Match[str] = maybe_item_to_remove

        items_to_remove.append(item_to_remove.group(1))

    remove_ocs(items_to_remove)
    unforged_list.clear()


# global variable definitions
forged_ocs: dict[str, Any] = dict()
unforged_ocs: dict[str, Any] = dict()
unacquired_ocs: dict[str, Any] = dict()
stats: dict[str, Any] = dict()
weapon_stats: dict[int, list[int, int, bool]] | None = None  # type: ignore
file_name: str = ""
save_data: bytes = b""
season_selected: int = LATEST_SEASON

if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
    # print(os.getcwd())
    # print(os.path.dirname(__file__))
    app = QApplication()

    guids_file = "guids.json"

    # check if the guid file exists in the current working directory, if not, use the one in the same directory as the script (for pyinstaller)
    if not os.path.exists(guids_file):
        guids_file = os.path.join(os.path.dirname(__file__), guids_file)

    # load reference data
    with open(guids_file, "r", encoding="utf-8") as g:
        guid_dict: dict[str, Any] = json.loads(g.read())

    try:
        # find the install path for the steam version
        if platform == "win32":
            steam_reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")  # type: ignore
            steam_path = winreg.QueryValueEx(steam_reg, "SteamPath")[0]  # type: ignore
            steam_path += "/steamapps/common/Deep Rock Galactic/FSD/Saved/SaveGames"
        else:
            steam_path = "."
    except:
        steam_path = "."

    # load the UI
    widget: EditorUI = EditorUI()

    # actually display the thing
    widget.show()
    exit_code = app.exec()
    sys.exit(exit_code)
