#!/usr/bin/env python3

import vdf, os, re, shutil, webp, logging, argparse, sys
from settings import *
from pathlib import Path
from PIL import Image
from steam_web_api import Steam
from time import sleep

# GLOBAL DEFINITIONS
# Determine which variables are set in the config file
if not 'LOG_LEVEL' in globals():
    LOG_LEVEL = 'INFO'
if not 'COPY_MODE' in globals():
    COPY_MODE = 0

if not 'RUN_INTERVAL' in globals():
    RUN_INTERVAL = 15

# Logging
if LOG_LEVEL == 'VERBOSE':
    LOG_LEVEL = 'DEBUG'

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)


# Commandline flags and arguments
parser = argparse.ArgumentParser(prog='SteamScreen', description='A screenshot manager for Steam.')

parser.add_argument('-r', '--recurring', action='store_true', 
                    help='Run the program in continuous service mode')
parser.add_argument('-m', '--mode', 
                    help='Copy mode, 0 = copy original files, 1 = convert to webp, 2 copy and ' \
'convert while keeping both copies', type=int)
parser.add_argument('-u', '--user', 
                    help='The Steam ID number of the user to process.')
parser.add_argument('-o', '--output', 
                    help='Output directory to copy images to')
parser.add_argument('-s', '--steam', 
                    help='The location of you main steam directory i.e. /home/user/.local/share/Steam')


RUN_AS_SERVICE = False

args = vars(parser.parse_args())
if not args['recurring'] == None:
    RUN_AS_SERVICE = args['recurring']

if not args['mode'] == None:
    COPY_MODE = args['mode']
    logging.info('Running script with flag: mode = ' + str(args['mode']))
if not args['id'] == None:
    STEAM_USER_ID = args['id']
    logging.info('Running script with flag: id = ' + args['id'])
if not args['output'] == None:
    OUTPUT_FOLDER = args['output']
    logging.info('Running script with flag: output = ' + args['output'])
if not args['steam'] == None:
    STEAM_FOLDER = args['steam']
    logging.info('Running script with flag: steam = ' + args['steam'])

for k, v in args:
    if v != None:
        break
    RUN_AS_SERVICE = True


# Standardize Home folder
STEAM_FOLDER = os.path.expanduser(STEAM_FOLDER)
OUTPUT_FOLDER = os.path.expanduser(OUTPUT_FOLDER)


# Check "libraryfolders.vdf" for all steam install locations
def get_libraries():
    logging.info('Checking for all steam library locations...')
    all_libraries = []
    library_vdf_path = STEAM_FOLDER + '/steamapps/libraryfolders.vdf'
    
    with open(library_vdf_path, 'r', encoding='UTF-8') as f:
        data = vdf.load(f)

    libraries = data.get("libraryfolders", {})
    
    for entry in libraries.values():
        path = entry.get('path')
        logging.info('Found a steam library at: ' + path)
        all_libraries.append(path)
    
    return all_libraries



# Load Screenshots.vdf
def get_screenshots_vdf():
    logging.info('Loading "Screenshots.vdf" files...')
    users = get_user_directories()
    logging.info('Retrieving game IDs....')

    for user in users:
        try:
            screenshots_vdf_path = STEAM_FOLDER + '/userdata/' + user + '/760/screenshots.vdf'


            with open((screenshots_vdf_path), 'r', encoding='UTF-8') as f:
                data = vdf.load(f)

                # get screenshot list
                screenshots = data.get('screenshots', {})
                # get non-steam games list
                shortcuts = screenshots.get('shortcutnames', {})
                
                # Get each game id
                game_ids = list(screenshots.keys())

            game_ids.remove('shortcutnames')
        except:
            logging.warning('Could not load screenshots.vdf file for user: ' + user)
            continue

    return game_ids, shortcuts



# Use appmanifest_#####.acf files to match app id to game title
def match_titles(all_libraries, game_ids):

    manifest_files = []
    games = {}

    # get all appmanifest files that match the Game IDs
    for i in all_libraries:
        p = Path(i + '/steamapps')

        for g in game_ids:
            if Path(p / ('appmanifest_' + g + '.acf')).exists():
                find_appmanifest = Path(p / ('appmanifest_' + g + '.acf'))
                manifest_files.append(find_appmanifest)
                games[g] = ''

    # Open each Manifest file to get game name
    for file in manifest_files:
        with open(file, 'r', encoding='UTF-8') as f:
            data = vdf.load(f)
            game_data = data.get('AppState', {})
            game_id = game_data.get('appid')
            game_title = game_data.get("name")

            games[game_id] = game_title

    return games



# Clean directory names of illegal characters
def sanitize_names(name):
    clean_name = re.sub(r'[\\\/:*?"<>|]', '', name).strip()
    return clean_name


# Merge games found with ACF and ones without
def merge_sources():
    # Add non-steam shortcut games to the list
    games.update(shortcuts)

    # If the game is not installed (no ACF file), fallback to gettig the game title from Steam API
    users = get_user_directories()
    for user in users:

        screenshots_dir = STEAM_FOLDER + '/userdata/' + user + '/760/remote'
        steam = Steam()
        try:
            with os.scandir(screenshots_dir) as folder:
                for f in folder:
                    if f.is_dir():
                        game_id = f.name
                        if not f.name in games.keys():
                            # Match the ID to the game name if it's not already in 'games' and there is a screenshot folder 
                            steam_app = steam.apps.get_app_details(game_id)
                            game_data = steam_app.get(game_id, {}).get('data', {})
                            game_title = game_data.get('name')
                            games.update({game_id : game_title})

            logging.info('Found screenshots for user ' + user)
        except:
            logging.warning('No screenshots for user ' + user + ', skipping...')


# Get all steam user locations
def get_user_directories():
    userdata_dir = STEAM_FOLDER + '/userdata'
    user_dirs = []
    with os.scandir(userdata_dir) as entry:
        for e in entry:
            if e.is_dir():
                user_dirs.append(e.name)

    return user_dirs



# For each game create a new directory (if non-existent) and loop through copying each entry to the new directory
def copy_files():
    merge_sources()
    SCREENSHOT_COUNT = 0

    # merge steam games with non-steam games
    games.update(shortcuts)

    # Create game directories
    logging.info('Creating directories...')
    if 'STEAM_USER_ID' in globals():
        logging.info('User ID ' + STEAM_USER_ID + ' specified. Scanning that user\'s directory only.')

    # Get the path of the output folders
    p = Path(OUTPUT_FOLDER)
    w = Path(os.path.expanduser(BOTH_WEBP_FOLDER))
    o = Path(os.path.expanduser(BOTH_ORIGINAL_FOLDER))

    # Loop through all detected games
    for id, game in games.items():       
        user_dirs = get_user_directories()

        # Loop through each user
        for user in user_dirs:
            if 'STEAM_USER_ID' in globals():
                source_dir = STEAM_FOLDER + '/userdata/' + STEAM_USER_ID + '/760/remote/' + id + '/screenshots'

            else:
                source_dir = STEAM_FOLDER + '/userdata/' + user + '/760/remote/' + id + '/screenshots'

            # Define the path of each output game folder
            output_dir = Path(p / sanitize_names(game))

            if COPY_MODE == 2:
                webp_dir = Path(w / sanitize_names(game))
                original_dir = Path(o / sanitize_names(game))

            # Check if game has a screenshots source folder
            if Path(source_dir).exists():
                logging.info('Copying files for ' + game + '...')               

                # Create folders for WEBP and original copies
                if COPY_MODE == 2:
                    if not webp_dir.exists():
                        logging.debug('Directory for ' + game + ' doesn\'t exist. Creating one...')
                        os.makedirs(webp_dir)
                    else:
                        logging.debug('Directory for ' + game + ' exists. Skipping....')

                    if not original_dir.exists():
                        logging.debug('Directory for ' + game + ' doesn\'t exist. Creating one...')
                        os.makedirs(original_dir)
                    else:
                        logging.debug('Directory for ' + game + ' exists. Skipping....')

                # Create game folders
                else:
                    if not output_dir.exists():
                        logging.debug('Directory for ' + game + ' doesn\'t exist. Creating one...')
                        os.makedirs(output_dir)
                    else:
                        logging.debug('Directory for ' + game + ' exists. Skipping....')


                # loop through each screenshot
                with os.scandir(source_dir) as file:
                    for f in file:
                        if f.is_file():

                            # Copy files to output folder
                            if COPY_MODE == 0 or COPY_MODE == 2:
                                file_title = os.path.basename(f)
                                file_title = os.path.splitext(file_title)[0]

                                # For copy only mode, copy the files
                                if COPY_MODE == 0:
                                    if not os.path.exists(output_dir / os.path.basename(f)):
                                        logging.debug('Copying file ' + str(f.name) + ' to ' + game)
                                        shutil.copy(f, output_dir)
                                        SCREENSHOT_COUNT += 1
                                    else:
                                        logging.debug(game + ': ' + f.name + ' already exists, skipping....')

                                # For copy and convert mode, copy the files to the specified folder
                                else:
                                    original_directory = Path(os.path.expanduser(BOTH_ORIGINAL_FOLDER))
                                    
                                    if not os.path.exists(original_directory):
                                        os.makedirs(original_directory)
                                    
                                    if not os.path.exists(original_dir / os.path.basename(f)):
                                        logging.debug('Copying file ' + str(f.name) + ' to ' + game)
                                        shutil.copy(f, original_dir)
                                        SCREENSHOT_COUNT += 1
                                    else:
                                        logging.debug(game + ': ' + f.name + ' already exists, skipping....')
                        
                            # Convert all screenshots to WEBP and move them into the new directories
                            if COPY_MODE == 1 or COPY_MODE == 2:
                                file_title = os.path.basename(f)
                                file_title = os.path.splitext(file_title)[0]

                                # For convert only, convert and place files
                                if COPY_MODE == 1:
                                    new_file_path = Path(output_dir / (file_title + '.webp'))

                                    if not os.path.exists(new_file_path):
                                        logging.debug('Converting ' + game + ': ' + file_title + ' to WEBP')
                                        img = Image.open(f)
                                        logging.debug(f"WEBP DESTINATION: {new_file_path.resolve()}")
                                        webp.save_image(img, new_file_path, quality=60)
                                        SCREENSHOT_COUNT += 1
                                    else:
                                        logging.debug(game + ': ' + file_title + '.webp already exists, skipping...')

                                # For convert and copy, convert and place files in output directory
                                else:
                                    webp_directory = Path(os.path.expanduser(BOTH_WEBP_FOLDER))
                                    new_file_path = Path(webp_dir / (file_title + '.webp'))

                                    if not os.path.exists(webp_directory):
                                        os.makedirs(webp_directory)

                                    if not os.path.exists(new_file_path):
                                        logging.debug('Converting ' + game + ': ' + file_title + ' to WEBP')
                                        img = Image.open(f)
                                        webp.save_image(img, new_file_path, quality=60)
                                        SCREENSHOT_COUNT += 1
                                    else:
                                        logging.debug(game + ': ' + file_title + '.webp already exists, skipping...')

                        # Ignore non-files during the scan
                        else:
                            logging.debug(f.name + ' is a directory, skipping...')

            # Ignore games that have no screenshots
            else:
                logging.debug(game + ' (Non-Steam game) has no screenshots, skipping...')

            # Don't loop through all users if a user was specified
            if 'STEAM_USER_ID' in globals():
                break

    # Completion messsages and reset the screenshot counter
    logging.info(str(SCREENSHOT_COUNT) + ' screenshot(s) successfully added to output directory.')
    logging.info('Done!')
    SCREENSHOT_COUNT = 0
    
# Run the functions as a looping service
if RUN_AS_SERVICE == True:
    while True:
        game_ids, shortcuts = get_screenshots_vdf()
        all_libraries = get_libraries()
        games = match_titles(all_libraries, game_ids)
        copy_files()
        logging.info('Waiting ' + str(RUN_INTERVAL) + ' minutes for next run...')
        sleep(RUN_INTERVAL * 60)

# Run the functions once
else:
    game_ids, shortcuts = get_screenshots_vdf()
    all_libraries = get_libraries()
    games = match_titles(all_libraries, game_ids)
    copy_files()