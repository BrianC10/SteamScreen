# SteamScreen
A Linux tool to copy, convert, organize, and back up Steam screenshots. Works on Steam games and Non-steam games added as shortcuts to Steam.

From this:

`~/.local/share/Steam/userdata/99999999/760/remote/570/screenshots/20260502192826_1.jpg`

To this:

`~/screenshots/Dota 2/20260502192826_1.jpg`


## Features
- Copy your screenshots out of the deep dungeon that is the steamapps userdata folder into clean directories based on game title
- Optionally copy original files, convert to a compressed webp file, or both
- Works for all Steam users on a PC or a defined single user
- Run as a continuous service or as a one-time command line tool

## Dependencies
The following python dependencies are required. They will be installed automatically by one of the install scripts:

- webp: https://pypi.org/project/webp/
- vdf: https://pypi.org/project/vdf/
- python-steam-api: https://pypi.org/project/python-steam-api/

## Installation
1. Clone the repo: `git clone steamscreen`
2. Enter the repo directory: `cd steamscreen`
3. Allow the Install script to be run: `chmod +x install.sh` (or `chmod +x install-cli.sh`) for the non-service version.
4. Install: `./install.sh` (`./install-cli.sh`)

## Configutation
`settings.py` is a config file to change various settings of the program. After installation it will be located at `~/.config/steamscreen.py`

| Setting                | Description                                                                                                          | Default                        |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| `STEAM_FOLDER`         | The location of your Steam installation.                                                                             | `~/.local/share/Steam`         |
| `STEAM_USER_ID`        | By default the script will process screenshots for all users. To specify a single user enter your Steam user ID here | `disabled`                     |
| `COPY_MODE`            | 0, copy original files<br>1, convert to webp<br>2, copy and convert, keep both copies                                | `0`                            |
| `OUTPUT_FOLDER`        | The directory where output files should be saved. Only applies to COPY_MODE 0 and 1                                  | `~/steam-screenshots`          |
| `BOTH_WEBP_FOLDER`     | In COPY_MODE 2, the directory the webp files will be saved to                                                        | `~/steam-screenshots/webp`     |
| `BOTH_ORIGINAL_FOLDER` | In COPY_MODE 2, the directory the original files will be saved to                                                    | `~/steam-screenshots/original` |
| `LOG_LEVEL`            | The level of detail of the logs. INFO, WARNING, VERBOSE                                                              | `INFO`                         |
| `RUN_INTERVAL`         | The frequency (in minutes) the running service will re-check for screenshots                                         | `15`                           |

## Usage
For a continuously running service:
1. Edit the config as necessary: `nano ~/.config/steamscreen/settings.py`
2. Enable the service: `systemctl --user enable steamscreen`
3. Start the service: `systemctl --user start steamscreen`
4. Check the status: `systemctl --user status steamscreen`

##### Editing After First Run
1. Stop the service: `systemctl --user stop steamscreen`
2. Edit the config file as necessary: `nano ~/.config/steamscreen/settings.py`
3. Restart the service: `systemctl --user restart steamscreen`

## Command Line
Instead of running the program as a service or editing the settings file, you can run SteamScreen from the terminal:
- `steamscreen` to run the program with default settings
- `steamscreen -arguments` to run and override both defaults and the settings file. `steamscreen -h` for details. 

| Argument          | Setting                            |
| ----------------- | ---------------------------------- |
| `-r, --recurring` | Enable continuous (recurring) mode |
| `-m, --mode`      | `COPY_MODE`                        |
| `-u, -user`       | `STEAM_USER_ID`                    |
| `-o, --output`    | `OUTPUT_FOLDER`                    |
| `-s, --steam`     | `STEAM_USER_ID`                    |
| `-w, --webp`      | `BOTH_WEBP_FOLDER`                 |
| `-or, --original` | `BOTH_ORIGINAL_FOLDER`             |
| `-i, --interval`  | `RUN_INTERVAL`                     |
| `-l, --loglevel`  | `LOG_LEVEL`                        |