# Deep Rock Galactic Save Editor
This is a standalone DRG save editor written in python (3.6.12), using PyQt5 (5.9.2) and PySide2 (5.15.2) and packaged using the [fman build system](https://build-system.fman.io). 

## Requirements
- Windows 7 and up
- ???

## Installation
Download the "DRG Save Editor.zip" file and extract the zip file and start the editor using the "start editor.cmd" batch file. 

## Usage

### ALWAYS BACKUP YOUR SAVE FILE!
The editor will make a backup of the save file you open in the same folder as the save file with the extension of `.old`. The editor makes this backup at the moment you open the save file.

The editor should be pretty self-explanatory, see the screenshot below.

![main_screen](sshot.png)
## Changelog
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

## Would be nice, but ehh...
- Promotion support
- Assignment support
- Character loadout support
- Perk support
- Weapon modification support
- Milestone support
- Bells
- Whistles