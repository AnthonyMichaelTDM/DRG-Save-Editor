# Deep Rock Galactic Save Editor

This is a DRG save editor written in python (3.6.12), using PyQt5 (5.9.2) and PySide2 (5.15.2).

## There are likely to be bugs, see the Known Issues and Troubleshooting section!
## Repo is aimed at providing continued support and updates for [robertnunn/DRG-Save-Editor](https://github.com/robertnunn/DRG-Save-Editor) as the original creator has "Largely moved on from this project"
That said, I'm in college right now and likely won't have time to implement many of the To-Do items at the end of this file, not without help anyway ;)

## Requirements
any computer with __git__ (and/or a browser) to download the code, __pip__ to download the required python packages, __Python3__ to run the code, and a display should be able to make use of this project

## Installation
- clone the repo: `git clone https://github.com/AnthonyMichaelTDM/DRG-Save-Editor.git` (or download the source code from github)
- open your terminal in the base directory of the project
- install the required packages with pip using the following command: `pip install -r ./requirements.txt`
- start the program with the `python3 ./src/main/python/main.py` command

if these instructions are unclear a member of the community, [NerdyJosh1](https://github.com/NerdyJosh1), has made a [video tutorial for windows users](https://www.youtube.com/watch?v=2h2-nZ2ptRo&ab_channel=NerdyJosh)

## Known Issues
- The editor works by looking for specific values in the raw data of the save, it doesn't decode the data into a nice, neat python object. As a result if certain things aren't present in the save (e.g., >0 forged overclocks, certain resources) the editor will malfunction and give nonsensical results. The solution is to acquire at least one of the resources in game _then_ use the editor.

## Troubleshooting
If the editor opens but doesn't edit your save properly (i.e., values not being read properly, changes not being reflected in-game, etc) please open an issue, describe the problem as thoroughly as you can, and attach a copy of your save file from BEFORE any edits were attempted.

## Usage
### ALWAYS BACKUP YOUR SAVE FILE!
The editor will make a backup of the save file you open in the same folder as the save file with the extension of `.old`. The editor makes this backup at the moment you open the save file.

The editor should be pretty self-explanatory, see the screenshot below.

Some notes:
- There is a context menu in the overclock tree listing to add overclocks to the inventory
- You can CTRL+Click on overclocks to select more than one
- Changing XP values will update the other relevant fields when the focus changes (i.e., click on a different part of the program or another program entirely)
- If you have promotions beyond Legendary 3 those promotions will be preserved as long as the drop-down is set to "Legendary 3+". If you don't have enough promotions for a specific dwarf and set them to "Legendary 3+" it will keep whatever the original value was.
- the `DRG Save Editor.zip` file is out of date, the only reason it's still in the repository is because there's really no point in removing it 

![main_screen](sshot.png)
## Changelog
- v1.7
    - Updated for season 3
        - updated season guid
- v1.6
    - issue with adding OC's fixed by [Anthony](https://github.com/AnthonyMichaelTDM) in [PR #45](https://github.com/robertnunn/DRG-Save-Editor/pull/45)
- v1.5
    - Updated editor for Season 2
    - Can adjust season xp and scrip
    - Can edit amount of phazyonite
    - Disabled adding OCs as it's currently broken and it's more effort than I'm willing to put in to figure it out. See the comments in main.py (line 767) if you're interested.
    - Missing data for the new overclocks (for the new secondary weapons)
- v1.4.4
    - Added option to select all files when opening save files
- v1.4.3
    - Fixed a bug that prevented editing of XP levels for dwarves
- v1.4.2
    - Fixed a bug that would cause the editor to hang when opening old saves
- v1.4.1
    - Fixed lack of new OCs showing up
- v1.4
    - Updated for update 35
        - Added new weapon overclocks (special thanks to [Eleison](https://github.com/Eleison) for all the new OC data)
        - Added support for data cell resource
        - Added support for season xp/level and scrip
- v1.3.7
    - Fixed a bug where the editor would crash with the microsoft store version of the game
- v1.3.6
    - Fixed a bug where an unexpected number of resources in the save file would throw off reading/writing of new values. The editor now reads how many entries there are and adjusts accordingly
- v1.3.5
    - Fixed a bug where promotions beyond Legendary 3 would be lost when saving. As long as the promotion is set to "Legendary 3+" before saving, the original number of promotions (and thus player rank) is preserved
- v1.3.4
    - Fixed a bug related to editing perk points when using a new save or a save that doesn't have any available perk points
    - Added player rank calculation and rank title to the classes area
- v1.3.3
    - Fixed a bug related to opening saves that have not forged any overclocks
    - Fixed a bug where resource counts would get mixed up
- v1.3.2
    - Fixed a bug in saving the game file that would truncate the save to a few hundred bytes
- v1.3.1
    - Forgot what I fixed here, lol
- v1.3
    - Added promotion support
    - Added "Remove Selected" and "Remove All" buttons for the overclock inventory
    - Updated "DRG Save Editing.txt" to correctly specify XP locations
    - Refactored code to integrate with pytest (6.2.1)
    - Fixed a critical bug that caused the editor to crash on opening a save file
- v1.2
    - Added auto-backup of save file upon opening the file
    - Fixed bug with fetching xp values where the dwarves would have their xp values swapped
- v1.1
    - Fixed a bug with the overclock tree and overclock inventory wouldn't update properly when opening another save file after opening the first
- v1.0
    - Initial release

## To-Do
- Cosmetic overclock support
- GUI polish
- Better readme
- "Restore from backup" option in toolbar menu

## Would be nice, but ehh...
- Assignment support
- Character loadout support
- Perk support
- Weapon modification support
- Milestone support
- Bells & Whistles
