# Escape Velocity: Nova + Override merger

This tool allows you to merge the universes in EV:N and EV:O, so that you can play both games in the same game. It's not 100\% finished.

Theoretically, you can merge any two EV games/mods using this method... but you might run out of resource IDs.
`reserved.txt` contains the IDs that are already reserved by the original plugin. By default, this contains EV: Nova reserved IDs.

## Notes:

### Building
To build the plugin follow these steps:

* Install Quicktime on a Windows virtual machine
e.g. from https://archive.org/details/apple-quicktime-7.7.9-last-version-for-the-windows on a Windows 10 VM.
* Restart the VM.
* Then open `EVNEW.exe` on the virtual machine
* Open `full_plugin.txt` with the open `EVNEW` instance
* Save the plugin as a `.rez` file with `EVNEW`
* Use the plugin how you seem fit

Don't try to convert from `txt` to `rez` on the command line if you have any resources that need to be imported. You need to launch the app visually and use the `File -> Load` method for the QuickTime importer to actually work. Don't ask me why, maybe it's gremlins.

### Running Escape Velocity

Escape Velocity isn't exactly the best-supported game out there anymore. Fortunately, various resources exist and a vibrant community has kept the game series relatively alive.

I recommend playing the game by downloading the `Community Edition` (this should also work under `wine` with `ddraw`, YMMV but I personally had the best results with the `gdi` renderer and reasonably sane settings).

Useful links:
* [https://github.com/andrews05/EV-Nova-CE](https://github.com/andrews05/EV-Nova-CE)
* [https://escape-velocity.games/](https://escape-velocity.games/)
* [https://wiki.ambrosia.garden/doku.php?id=start](https://wiki.ambrosia.garden/doku.php?id=start)

### EVNEW

The source code for EVNEW is included. I don't take any credit for it, but I didn't want it to get lost to bit rot permanently and used it quite a few times for reference when debugging.
