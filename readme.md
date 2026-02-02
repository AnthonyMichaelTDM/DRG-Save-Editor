# Deep Rock Galactic Save Editor

There are likely to be bugs, see the Known Issues and Troubleshooting section

This repo is aimed at providing continued support and updates for [robertnunn/DRG-Save-Editor](https://github.com/robertnunn/DRG-Save-Editor) as the original creator has "Largely moved on from this project"

That said, I'm in college right now and likely won't have time to implement many of the To-Do items at the end of this file, not without help anyway

## Installation

### Releases (recommended)

- download the latest release from the [releases page](https://github.com/AnthonyMichaelTDM/DRG-Save-Editor/releases)
  - for windows download the `DRG-Save-Editor-windows.zip` file
  - for linux download the `DRG-Save-Editor-linux.tar.gz` file
- extract the contents of the archive to a folder of your choice and run the executable:
  - for windows run the `DRG-Save-Editor.exe` file
  - for linux run the `DRG-Save-Editor` file

### From Source

#### Requirements

- python 3.12 or later
- (optional) git to clone the repo

#### Steps

1. clone the repo: `git clone https://github.com/AnthonyMichaelTDM/DRG-Save-Editor.git` (or download the source code from github)
2. open your terminal in the base directory of the project
   - (optional) run `python --version` to ensure the version is correct
   - (optional) run `python -m venv venv` to create a virtual environment
     - activate the virtual environment with the following command:
       - for windows: `.\venv\Scripts\activate`
       - for linux: `source ./venv/bin/activate`
3. install the required packages with pip using the following command: `pip install -r ./requirements.txt`
4. start the program with the `python ./src/main/python/main.py` command

if these instructions are unclear a member of the community, [NerdyJosh1](https://github.com/NerdyJosh1), has made a [video tutorial for windows users](https://www.youtube.com/watch?v=2h2-nZ2ptRo&ab_channel=NerdyJosh)

- Note: this tutorial was made for version 1.7.0/1.8.0 of the editor, some things have changed since then

## Known Issues

- The editor works by looking for specific values in the raw data of the save, it doesn't decode the data into a nice, neat python object. As a result if certain things aren't present in the save (e.g., >0 forged overclocks, certain resources) the editor will malfunction and give nonsensical results. The solution is to acquire at least one of the resources in game _then_ use the editor.

## Troubleshooting

If the editor opens but doesn't edit your save properly (i.e., values not being read properly, changes not being reflected in-game, etc) please open an issue, describe the problem as thoroughly as you can, and attach a copy of your save file from BEFORE any edits were attempted.

## Usage

Note: **ALWAYS BACKUP YOUR SAVE FILE**

The editor will make a backup of the save file you open in the same folder as the save file with the extension of `.old`. The editor makes this backup at the moment you open the save file.

The editor should be pretty self-explanatory, see the screenshot below.

Some notes:

- There is a context menu in the overclock tree listing to add overclocks to the inventory
- You can CTRL+Click on overclocks to select more than one
- Changing XP values will update the other relevant fields when the focus changes (i.e., click on a different part of the program or another program entirely)
- If you have promotions beyond Legendary 3 those promotions will be preserved as long as the drop-down is set to "Legendary 3+". If you don't have enough promotions for a specific dwarf and set them to "Legendary 3+" it will keep whatever the original value was.

![main_screen](sshot.png)

## Changelog

- v1.10.0
  - assorted bug fixes and maintenance (#112, #113)
  - Updated for season 6
    - updated season guid (special thanks to [wahlp](https://github.com/wahlp) for contributing the update)
- v1.9.2
  - assorted bug fixes, refactoring, and maintenance (#90, #98, #100, #101)
  - add cosmetic overclocks #102
  - special thanks to [wahlp](https://github.com/wahlp) and [simon-wg](https://github.com/simon-wg) for their work on this release
- v1.9.1
  - assorted bug fixes (#83, #84)
  - build release in console mode and as a single standalone binary (#88)
- v1.9.0
  - build process updated to use pyinstaller (special thanks to [wahlp](https://github.com/wahlp) for contributing the initial workflow)
  - Updated for season 5
    - updated season guid (special thanks to [wahlp](https://github.com/wahlp) for contributing the update)
    - add season selection combobox (special thanks to [wahlp](https://github.com/wahlp) for contributing the update)
    - add new OCs (special thanks to [LordFoogThe4rd](https://github.com/LordFoogThe4rd) and [kagrith](https://github.com/kagrith) for contributing the new OC data)
    - add action to max out your weapon maintenance rank (special thanks to [simon-wg](https://github.com/simon-wg) for contributing the update)
- v1.8.0
  - Updated for season 4
    - updated season guid
      - special thanks to [simon-wg](https://github.com/simon-wg) for contributing the update
- v1.7.0
  - Updated for season 3
    - updated season guid
  - Anthony's fork detached from original repo to better enable continued development
- v1.6.0
  - issue with adding OC's fixed by [Anthony](https://github.com/AnthonyMichaelTDM) in [PR #45](https://github.com/robertnunn/DRG-Save-Editor/pull/45)
- v1.5.0
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
- v1.4.0
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
- v1.3.0
  - Added promotion support
  - Added "Remove Selected" and "Remove All" buttons for the overclock inventory
  - Updated "DRG Save Editing.txt" to correctly specify XP locations
  - Refactored code to integrate with pytest (6.2.1)
  - Fixed a critical bug that caused the editor to crash on opening a save file
- v1.2.0
  - Added auto-backup of save file upon opening the file
  - Fixed bug with fetching xp values where the dwarves would have their xp values swapped
- v1.1.0
  - Fixed a bug with the overclock tree and overclock inventory wouldn't update properly when opening another save file after opening the first
- v1.0.0
  - Initial release

## To-Do

- Refactor project to follow SOLID design principles
- Cosmetic overclock support
- GUI polish
- Better readme
- "Restore from backup" option in toolbar menu

## Would be nice, but ehh

- Assignment support
- Character loadout support
- Perk support
- Weapon modification support
- Milestone support
- Bells & Whistles
