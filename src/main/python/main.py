import PySide2
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, QIODevice, Slot
from PySide2.QtWidgets import QApplication, QFileDialog, QPlainTextEdit, QTreeWidgetItem, QListWidgetItem, QMenu, QAction, QLineEdit
from PySide2.QtGui import QColor, QCursor
from fbs_runtime.application_context.PySide2 import ApplicationContext
from copy import deepcopy
import sys
import os
import struct
import re
from pprint import pprint as pp
import json

class TextEditFocusChecking(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def focusOutEvent(self, e: PySide2.QtGui.QFocusEvent) -> None:
        box = self.objectName()
        if self.text() == '':
            return super().focusOutEvent(e)

        value = int(self.text())
        # print(box)
        if box.startswith('d'):
            dwarf = 'driller'
        elif box.startswith('e'):
            dwarf = 'engineer'
        elif box.startswith('g'):
            dwarf = 'gunner'
        elif box.startswith('s'):
            dwarf = 'scout'
        else:
            print('abandon all hope, ye who see this message')
            return super().focusOutEvent(e)
        # print(dwarf)

        if box.endswith('xp'):
            # print('main xp')
            total = value
        elif box.endswith('text'):
            # print('level xp')
            xp, level, rem = get_dwarf_xp(dwarf)
            if xp_table[value-1] + rem == xp:
                total = xp
            else:
                total = xp_table[value-1]
        elif box.endswith('2'):
            xp, level, rem = get_dwarf_xp(dwarf)
            total = xp_table[level-1] + value
        
        update_xp(dwarf, total)
        
        return super().focusOutEvent(e)


def get_dwarf_xp(dwarf):
    if dwarf == 'driller':
        total = int(widget.driller_xp.text())
        level = int(widget.dr_lvl_text.text())
        rem = int(widget.driller_xp_2.text())
    elif dwarf == 'engineer':
        total = int(widget.engineer_xp.text())
        level = int(widget.en_lvl_text.text())
        rem = int(widget.engineer_xp_2.text())
    elif dwarf == 'gunner':
        total = int(widget.gunner_xp.text())
        level = int(widget.gu_lvl_text.text())
        rem = int(widget.gunner_xp_2.text())
    elif dwarf == 'scout':
        total = int(widget.scout_xp.text())
        level = int(widget.sc_lvl_text.text())
        rem = int(widget.scout_xp_2.text())
    else:
        total = rem = level = -1

    return total, level, rem


def update_xp(dwarf, total_xp=0):
    if total_xp > 315000:
        total_xp = 315000
    level, remainder = xp_total_to_level(total_xp)
    bad_dwarf = False
    if dwarf == 'driller':
        total_box = widget.driller_xp
        level_box = widget.dr_lvl_text
        remainder_box = widget.driller_xp_2
    elif dwarf == 'engineer':
        total_box = widget.engineer_xp
        level_box = widget.en_lvl_text
        remainder_box = widget.engineer_xp_2
    elif dwarf == 'gunner':
        total_box = widget.gunner_xp
        level_box = widget.gu_lvl_text
        remainder_box = widget.gunner_xp_2
    elif dwarf == 'scout':
        total_box = widget.scout_xp
        level_box = widget.sc_lvl_text
        remainder_box = widget.scout_xp_2
    else:
        print('no valid dward specified')
        bad_dwarf = True

    

    if not bad_dwarf:
        total_box.setText(str(total_xp))
        level_box.setText(str(level))
        remainder_box.setText(str(remainder))
    

@Slot()
def open_file():
    global file_name
    file_name = QFileDialog.getOpenFileName(None, 'Open Save File', '.', 'Player Save Files (*.sav)')[0]
    widget.setWindowTitle(f'DRG Save Editor - {file_name}')
    with open(file_name, 'rb') as f:
        save_data = f.read()

    widget.combo_oc_filter.setEnabled(True)
    init_values(save_data)

    global forged_ocs
    global unacquired_ocs
    global unforged_ocs

    forged_ocs, unacquired_ocs, unforged_ocs = get_overclocks(save_data, guid_dict)

    overclock_tree = widget.overclock_tree.invisibleRootItem()
    build_oc_tree(overclock_tree, guid_dict)
    widget.overclock_tree.sortItems(0, PySide2.QtCore.Qt.AscendingOrder)
    # PySide2.QtCore.Qt.
    # populate list of unforged ocs
    unforged_list = widget.unforged_list
    for k,v in unforged_ocs.items():
        oc = QListWidgetItem(None)
        try:
            oc.setText(f'{v["weapon"]}: {v["name"]} ({k})')
        except:
            oc.setText(f'Cosmetic: {k}')
        unforged_list.addItem(oc)


def get_resources(save_bytes):
    marker = b'OwnedResources'
    start_offset = 101
    offset = 20
    resources = [
        'Yeast Cone',
        'Starch Nut',
        'Barley Bulb',
        'Bismor',
        'Enor Pearl',
        'Malt Star',
        'Umanite',
        'Jadiz',
        'Croppa',
        'Magnite',
        'Error Cube',
        'Blank Matrix Core',
    ]
    res_amts = list()
    marker_pos = save_bytes.find(marker)
    pos = marker_pos + start_offset -20
    for i in range(len(resources)):
        pos += offset
        res_amts.append(int(struct.unpack('f', save_bytes[pos:pos+4])[0]))
        
    # print(res_amts)
    # print(resources)
    res_dict = dict(zip(resources, res_amts))
    return res_dict


def get_xp(save_bytes):
    marker = b'XP\x00\x0c\x00\x00\x00IntP'
    start_offset = 0
    offset = 28
    eng_xp_pos = save_bytes.find(marker) + offset
    scout_xp_pos = save_bytes.find(marker, eng_xp_pos+1) + offset
    drill_xp_pos = save_bytes.find(marker, scout_xp_pos+1) + offset
    gun_xp_pos = save_bytes.find(marker, drill_xp_pos+1) + offset

    eng_xp = struct.unpack('i', save_bytes[eng_xp_pos:eng_xp_pos+4])[0]
    scout_xp = struct.unpack('i', save_bytes[scout_xp_pos:scout_xp_pos+4])[0]
    drill_xp = struct.unpack('i', save_bytes[drill_xp_pos:drill_xp_pos+4])[0]
    gun_xp = struct.unpack('i', save_bytes[gun_xp_pos:gun_xp_pos+4])[0]

    xp_dict = {
        'engineer': eng_xp,
        'scout': scout_xp,
        'driller': drill_xp,
        'gunner': gun_xp
    }

    return xp_dict


def xp_total_to_level(xp):
    for i in xp_table:
        if xp < i:
            level = xp_table.index(i)
            remainder = xp - xp_table[level-1]
            return (level, remainder)
    return (25, 0)
    

def get_credits(save_bytes):
    marker = b'Credits'
    offset = 33
    pos = save_bytes.find(marker) + offset
    money = struct.unpack('i', save_bytes[pos:pos+4])[0]

    return money


def get_perk_points(save_bytes):
    marker = b'PerkPoints'
    offset = 36
    pos = save_bytes.find(marker) + offset
    perk_points = struct.unpack('i', save_bytes[pos:pos+4])[0]

    return perk_points


def build_oc_dict(guid_dict):
    overclocks = dict()

    for v in guid_dict.values():
        try:
            overclocks.update({v['class']: dict()})
        except:
            pass

    for v in guid_dict.values():
        try:
            overclocks[v['class']].update({v['weapon']: dict()})
        except:
            pass
    
    for k,v in guid_dict.items():
        try:
            overclocks[v['class']][v['weapon']].update({v['name']: k})
        except:
            pass

    return overclocks
    

def build_oc_tree(tree, source_dict):
    oc_dict = build_oc_dict(source_dict)
    # entry = QTreeWidgetItem(None)
    for char, weapons in oc_dict.items():
        # dwarves[dwarf] = QTreeWidgetItem(tree)
        char_entry = QTreeWidgetItem(None)
        char_entry.setText(0, char)
        for weapon, oc_names in weapons.items():
            weapon_entry = QTreeWidgetItem(None)
            weapon_entry.setText(0, weapon)
            for name, uuid in oc_names.items():
                oc_entry = QTreeWidgetItem(None)
                oc_entry.setText(0, name)
                oc_entry.setText(1, source_dict[uuid]['status'])
                oc_entry.setText(2, uuid)
                weapon_entry.addChild(oc_entry)
            char_entry.addChild(weapon_entry)
        tree.addChild(char_entry)
            

def get_overclocks(save_bytes, guid_source):
    search_term = b'ForgedSchematics'#\x00\x0F\x00\x00\x00Struct'
    search_end = b'bFirstSchematicMessageShown'
    pos = save_bytes.find(search_term)
    end_pos = save_bytes.find(search_end)
    oc_data = save_bytes[pos:end_pos]
    oc_list_offset = 141
    for i in guid_source.values():
        i['status'] = 'Unacquired'

    guids = deepcopy(guid_source)

    # print(f'pos: {pos}, end_pos: {end_pos}')
    # print(f'owned_pos: {owned}, diff: {owned-pos}')
    unforged = True if oc_data.find(b'Owned') else False
    # print(unforged) # bool
    num_forged = struct.unpack('i', save_bytes[pos+63:pos+67])[0]
    forged = dict()
    # print(num_forged)


    for i in range(num_forged):
        uuid = save_bytes[pos+oc_list_offset+(i*16):pos+oc_list_offset+(i*16)+16].hex().upper()
        try:
            a = guids[uuid]
            guid_source[uuid]['status'] = 'Forged'
            a['status'] = 'Forged'
            del guids[uuid]
            forged.update({uuid: a})
            
            # print('success')
        except Exception as e:
            # print(f'Error: {e}')
            pass

    if unforged:
        unforged = dict()
        num_pos = save_bytes.find(b'Owned', pos) + 62
        num_unforged = struct.unpack('i', save_bytes[num_pos:num_pos+4])[0]
        unforged_pos = num_pos + 77
        for i in range(num_unforged):
            uuid = save_bytes[unforged_pos + (i*16):unforged_pos + (i * 16) + 16].hex().upper()
            try:
                unforged.update({uuid: guids[uuid]})
                guid_source[uuid]['status'] = 'Unforged'
                unforged[uuid]['status'] = 'Unforged'
            except KeyError:
                unforged.update({uuid: "Cosmetic"})

    # forged OCs, unacquired OCs, unforged OCs
    return (forged, guids, unforged)


@Slot()
def filter_overclocks():
    item_filter = widget.combo_oc_filter.currentText()
    # forged_ocs, unacquired_ocs, unforged_ocs = get_overclocks(save_data, guid_dict)
    print(item_filter)
    tree = widget.overclock_tree
    tree.clear()
    tree_root = tree.invisibleRootItem()
    if item_filter == 'All':
        build_oc_tree(tree_root, guid_dict)
    elif item_filter == 'Forged':
        build_oc_tree(tree_root, forged_ocs)
    elif item_filter == 'Unforged':
        build_oc_tree(tree_root, unforged_ocs)
    elif item_filter == 'Unacquired':
        build_oc_tree(tree_root, unacquired_ocs)

    tree.sortItems(0, PySide2.QtCore.Qt.AscendingOrder)


@Slot()
def oc_ctx_menu(pos):
    # oc_context_menu = make_oc_context_menu()
    # global oc_context_menu
    ctx_menu = QMenu(widget.overclock_tree)
    add_act = ctx_menu.addAction('Add Core(s) to Inventory')
    global_pos = QCursor().pos()
    action = ctx_menu.exec_(global_pos)
    if action == add_act:
        add_cores()

    # add_act.triggered.connect(add_cores())


@Slot()
def add_cores():
    print('add cores')
    global unforged_ocs
    tree = widget.overclock_tree
    selected = tree.selectedItems()
    items_to_add = list()
    for i in selected:
        items_to_add.append(f'{i.parent().text(0)}: {i.text(0)} ({i.text(2)})')
        unforged_ocs.update({i.text(2): guid_dict[i.text(2)]})
    
    core_list = widget.unforged_list
    for item in items_to_add:
        core_list.addItem(item)

    core_list.sortItems()


@Slot()
def save_changes():
    with open(file_name, 'rb') as f:
        save_data = f.read()
    
    new_values = get_values()
    #write resources
    resource_bytes = list()
    resources = [
        new_values['brewing']['yeast'],
        new_values['brewing']['starch'],
        new_values['brewing']['barley'],
        new_values['minerals']['bismor'],
        new_values['minerals']['enor'],
        new_values['brewing']['malt'],
        new_values['minerals']['umanite'],
        new_values['minerals']['jadiz'],
        new_values['minerals']['croppa'],
        new_values['minerals']['magnite'],
        new_values['misc']['error'],
        new_values['misc']['cores']
    ]
    for i in range(len(resources)):
        resource_bytes.append(struct.pack('f', resources[i]))

    res_marker = b'OwnedResources'
    res_pos = save_data.find(res_marker) + 101
    offset = 20
    for i in resource_bytes:
        save_data = save_data[:res_pos] + i + save_data[res_pos+4:]
        res_pos += offset

    # write credits
    cred_marker = b'Credits'
    cred_pos = save_data.find(cred_marker) + 33
    cred_bytes = struct.pack('i', new_values['misc']['credits'])
    save_data = save_data[:cred_pos] + cred_bytes + save_data[cred_pos+4:]

    # write perk points
    perks_marker = b'PerkPoints'
    perks_pos = save_data.find(perks_marker) + 36
    perks_bytes = struct.pack('i', new_values['misc']['perks'])
    save_data = save_data[:perks_pos] + perks_bytes + save_data[perks_pos+4:]

    # write XP
    xp_marker = b'XP\x00\x0c\x00\x00\x00IntP'
    offset = 28
    eng_xp_pos = save_data.find(xp_marker) + offset
    scout_xp_pos = save_data.find(xp_marker, eng_xp_pos+1) + offset
    drill_xp_pos = save_data.find(xp_marker, scout_xp_pos+1) + offset
    gun_xp_pos = save_data.find(xp_marker, drill_xp_pos+1) + offset

    eng_bytes = struct.pack('i', new_values['xp']['engineer'])
    scout_bytes = struct.pack('i', new_values['xp']['scout'])
    drill_bytes = struct.pack('i', new_values['xp']['driller'])
    gun_bytes = struct.pack('i', new_values['xp']['gunner'])

    save_data = save_data[:eng_xp_pos] + eng_bytes + save_data[eng_xp_pos+4:]
    save_data = save_data[:scout_xp_pos] + scout_bytes + save_data[scout_xp_pos+4:]
    save_data = save_data[:drill_xp_pos] + drill_bytes + save_data[drill_xp_pos+4:]
    save_data = save_data[:gun_xp_pos] + gun_bytes + save_data[gun_xp_pos+4:]
    
    #write overclocks
    search_term = b'ForgedSchematics'#\x00\x0F\x00\x00\x00Struct'
    search_end = b'\x1c\x00\x00\x00bFirstSchematicMessageShown'
    pos = save_data.find(search_term)
    end_pos = save_data.find(search_end)
    num_forged = struct.unpack('i', save_data[pos+63:pos+67])[0]
    if len(unforged_ocs) > 0:
        ocs = b'\x10\x00\x00\x00\x4F\x77\x6E\x65\x64\x53\x63\x68\x65\x6D\x61\x74\x69\x63\x73\x00\x0E\x00\x00\x00\x41\x72\x72\x61\x79\x50\x72\x6F\x70\x65\x72\x74\x79\x00\x6D\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\x53\x74\x72\x75\x63\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00\x00' + struct.pack('i', len(unforged_ocs)) + b'\x10\x00\x00\x00\x4F\x77\x6E\x65\x64\x53\x63\x68\x65\x6D\x61\x74\x69\x63\x73\x00\x0F\x00\x00\x00\x53\x74\x72\x75\x63\x74\x50\x72\x6F\x70\x65\x72\x74\x79\x00\x20\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x47\x75\x69\x64\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        uuids = [bytes.fromhex(i) for i in unforged_ocs.keys()]
        for i in uuids:
            ocs += i
    else:
        ocs = b''
    save_data = save_data[:pos+(num_forged*16)+141] + ocs + save_data[end_pos:]

    with open(f'{file_name}', 'wb') as t:
        t.write(save_data)


@Slot()
def set_all_25():
    update_xp('driller', 315000)
    update_xp('engineer', 315000)
    update_xp('gunner', 315000)
    update_xp('scout', 315000)

@Slot()
def reset_values():
    widget.bismor_text.setText(str(stats['minerals']['bismor']))
    widget.enor_text.setText(str(stats['minerals']['enor']))
    widget.jadiz_text.setText(str(stats['minerals']['jadiz']))
    widget.croppa_text.setText(str(stats['minerals']['croppa']))
    widget.magnite_text.setText(str(stats['minerals']['magnite']))
    widget.umanite_text.setText(str(stats['minerals']['umanite']))

    widget.yeast_text.setText(str(stats['brewing']['yeast']))
    widget.starch_text.setText(str(stats['brewing']['starch']))
    widget.malt_text.setText(str(stats['brewing']['malt']))
    widget.barley_text.setText(str(stats['brewing']['barley']))

    widget.error_text.setText(str(stats['misc']['error']))
    widget.core_text.setText(str(stats['misc']['cores']))
    widget.credits_text.setText(str(stats['misc']['credits']))
    widget.perk_text.setText(str(stats['misc']['perks']))

    widget.driller_xp.setText(str(stats['xp']['driller']))
    d_xp = xp_total_to_level(stats['xp']['driller'])
    widget.dr_lvl_text.setText(str(d_xp[0]))
    widget.driller_xp_2.setText(str(d_xp[1]))

    widget.engineer_xp.setText(str(stats['xp']['engineer']))
    e_xp = xp_total_to_level(stats['xp']['engineer'])
    widget.en_lvl_text.setText(str(e_xp[0]))
    widget.engineer_xp_2.setText(str(e_xp[1]))

    widget.gunner_xp.setText(str(stats['xp']['gunner']))
    g_xp = xp_total_to_level(stats['xp']['gunner'])
    widget.gu_lvl_text.setText(str(g_xp[0]))
    widget.gunner_xp_2.setText(str(g_xp[1]))

    widget.scout_xp.setText(str(stats['xp']['scout']))
    s_xp = xp_total_to_level(stats['xp']['scout'])
    widget.sc_lvl_text.setText(str(s_xp[0]))
    widget.scout_xp_2.setText(str(s_xp[1]))


@Slot()
def add_crafting_mats():
    cost = {
        'bismor': 0,
        'croppa': 0,
        'jadiz': 0,
        'enor': 0,
        'magnite': 0,
        'umanite': 0,
        'credits': 0
    }
    for k,v in unforged_ocs.items():
        print(k, v)
        try:
            for i in v['cost'].keys():
                cost[i] += v['cost'][i]
        except:
            print(f'Cosmetic')
    print(cost)
    add_resources(cost)
        

def add_resources(res_dict):
    # res_dict is {'bismor': 123, 'credits': 10000, ...}
    try:
        widget.bismor_text.setText(str(int(widget.bismor_text.text())+res_dict['bismor']))
    except:
        pass
    try:
        widget.croppa_text.setText(str(int(widget.croppa_text.text())+res_dict['croppa']))
    except:
        pass
    try:
        widget.enor_text.setText(str(int(widget.enor_text.text())+res_dict['enor']))
    except:
        pass
    try:
        widget.jadiz_text.setText(str(int(widget.jadiz_text.text())+res_dict['jadiz']))
    except:
        pass
    try:
        widget.magnite_text.setText(str(int(widget.magnite_text.text())+res_dict['magnite']))
    except:
        pass
    try:
        widget.umanite_text.setText(str(int(widget.umanite_text.text())+res_dict['umanite']))
    except:
        pass
    try:
        widget.barley_text.setText(str(int(widget.barley_text.text())+res_dict['barley']))
    except:
        pass
    try:
        widget.yeast_text.setText(str(int(widget.yeast_text.text())+res_dict['yeast']))
    except:
        pass
    try:
        widget.malt_text.setText(str(int(widget.malt_text.text())+res_dict['malt']))
    except:
        pass
    try:
        widget.starch_text.setText(str(int(widget.starch_text.text())+res_dict['starch']))
    except:
        pass
    try:
        widget.error_text.setText(str(int(widget.error_text.text())+res_dict['error']))
    except:
        pass
    try:
        widget.core_text.setText(str(int(widget.core_text.text())+res_dict['cores']))
    except:
        pass
    try:
        widget.credits_text.setText(str(int(widget.credits_text.text())+res_dict['credits']))
    except:
        pass


def init_values(save_data):
    global stats

    stats['xp'] = get_xp(save_data)
    stats['misc'] = dict()
    stats['misc']['credits'] = get_credits(save_data)
    stats['misc']['perks'] = get_perk_points(save_data)
    resources = get_resources(save_data)
    stats['misc']['cores'] = resources['Blank Matrix Core']
    stats['misc']['error'] = resources['Error Cube']
    stats['minerals'] = dict()
    stats['minerals']['bismor'] = resources['Bismor']
    stats['minerals']['enor'] = resources['Enor Pearl']
    stats['minerals']['jadiz'] = resources['Jadiz']
    stats['minerals']['croppa'] = resources['Croppa']
    stats['minerals']['magnite'] = resources['Magnite']
    stats['minerals']['umanite'] = resources['Umanite']
    stats['brewing'] = dict()
    stats['brewing']['yeast'] = resources['Yeast Cone']
    stats['brewing']['starch'] = resources['Starch Nut']
    stats['brewing']['barley'] = resources['Barley Bulb']
    stats['brewing']['malt'] = resources['Malt Star']


    reset_values()


def get_values():
    ns = dict()
    ns['minerals'] = dict()
    ns['brewing'] = dict()
    ns['misc'] = dict()
    ns['xp'] = dict()

    ns['minerals']['bismor'] = int(widget.bismor_text.text())
    ns['minerals']['croppa'] = int(widget.croppa_text.text())
    ns['minerals']['enor'] = int(widget.enor_text.text())
    ns['minerals']['jadiz'] = int(widget.jadiz_text.text())
    ns['minerals']['magnite'] = int(widget.magnite_text.text())
    ns['minerals']['umanite'] = int(widget.umanite_text.text())

    ns['brewing']['yeast'] = int(widget.yeast_text.text())
    ns['brewing']['starch'] = int(widget.starch_text.text())
    ns['brewing']['malt'] = int(widget.malt_text.text())
    ns['brewing']['barley'] = int(widget.barley_text.text())

    ns['xp']['driller'] = int(widget.driller_xp.text())
    ns['xp']['engineer'] = int(widget.engineer_xp.text())
    ns['xp']['gunner'] = int(widget.gunner_xp.text())
    ns['xp']['scout'] = int(widget.scout_xp.text())

    ns['misc']['error'] = int(widget.error_text.text())
    ns['misc']['cores'] = int(widget.core_text.text())
    ns['misc']['credits'] = int(widget.credits_text.text())
    ns['misc']['perks'] = int(widget.perk_text.text())

    return ns


xp_table = [
    0,
    3000,
    7000,
    12000,
    18000,
    25000,
    33000,
    42000,
    52000,
    63000,
    75000,
    88000,
    102000,
    117000,
    132500,
    148500,
    165000,
    182000,
    199500,
    217500,
    236000,
    255000,
    274500,
    294500,
    315000,
]

dwarf_xp ={
    'driller':{
        'level': 0,
        'rem': 0
    },
    'engineer':{
        'level': 0,
        'rem': 0
    },
    'gunner':{
        'level': 0,
        'rem': 0
    },
    'scout':{
        'level': 0,
        'rem': 0
    },
}
forged_ocs = dict()
unforged_ocs = dict()
unacquired_ocs = dict()
stats = dict()
file_name = ''

if __name__ == '__main__':
    # Some code to obtain the form file name, ui_file_name
    print(os.getcwd())
    # os.chdir(os.path.dirname(__file__))
    ui_file_name = 'editor.ui'
    appctext = ApplicationContext()
    # app = QApplication()
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QIODevice.ReadOnly):
        print("Cannot open {}: {}".format(ui_file_name, ui_file.errorString()))
        sys.exit(-1)

    with open('guids.json', 'r') as g:
        guid_dict = json.loads(g.read())

    loader = QUiLoader()
    loader.registerCustomWidget(TextEditFocusChecking)
    widget = loader.load(ui_file, None)
    ui_file.close()
    if not widget:
        print(loader.errorString())
        sys.exit(-1)

    widget.actionOpen_Save_File.triggered.connect(open_file)
    widget.overclock_tree.setHeaderLabels(['Overclock', 'Status', 'GUID'])
    sort_labels = ['All', 'Unforged', 'Forged', 'Unacquired']
    for i in sort_labels:
        widget.combo_oc_filter.addItem(i)

    widget.actionSave_changes.triggered.connect(save_changes)
    widget.actionSet_All_Classes_to_25.triggered.connect(set_all_25)
    widget.actionAdd_overclock_crafting_materials.triggered.connect(add_crafting_mats)
    widget.actionReset_to_original_values.triggered.connect(reset_values)
    widget.combo_oc_filter.currentTextChanged.connect(filter_overclocks)
    widget.overclock_tree.customContextMenuRequested.connect(oc_ctx_menu)
    widget.add_cores_button.clicked.connect(add_cores)
    
    widget.show()
    exit_code = appctext.app.exec_()
    sys.exit(exit_code)