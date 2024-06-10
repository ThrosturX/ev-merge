# Escape Velocity: Nova + Override merger

This tool allows you to merge the universes in EV:N and EV:O, so that you can play both games in the same game. It's not 100\% finished.

Theoretically, you can merge any two EV games/mods using this method... but you might run out of resource IDs.
`reserved.txt` contains the IDs that are already reserved by the original plugin. By default, this contains EV: Nova reserved IDs.

## Notes:
To build the plugin follow these steps:

* Install Quicktime on a Windows virtual machine
e.g. from https://archive.org/details/apple-quicktime-7.7.9-last-version-for-the-windows on a Windows 10 VM.
* Restart the VM.
* Then open EVNEW.exe on the virtual machine
* Open full\_plugin.txt with the open EVNEW.exe instance
* Save the plugin as a `.rez` file with EVNEW.exe
* Use the plugin how you seem fit

Don't try to convert from `txt` to `rez` on the command line if you have any resources that need to be imported. You need to launch the app visually and use the `File -> Load` method for the QuickTime importer to actually work. Don't ask me why, maybe it's gremlins.
