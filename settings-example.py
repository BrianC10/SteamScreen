# The location of your main steam installation
STEAM_FOLDER = '~/.local/share/Steam'

# Your Steam User ID. By default all user screenshots will be processed.
# Uncomment to specify a steam user to process. You can find this in two ways:
# 1. Your online steam user profile. Instructions at https://help.steampowered.com/en/faqs/view/2816-BE67-5B69-0FEC
# 2. In your Steam 'userdata' folder. /home/{user}/.local/share/Steam/userdata/{your_game_id}
# STEAM_USER_ID = '0000000'

# COPY MODE
# 0, copy original files
# 1, convert to webp
# 2, copy and convert, keep both copies
COPY_MODE = 2

# Directory where output files should be saved. This setting only affects COPY_MODE 0 and 1
OUTPUT_FOLDER = '~/steam-screenshots'

#### COPY MODE 2 LOCATIONS ####
# If you choose to keep the original and the webp copy, specify
# a directory name to save the images to.
BOTH_WEBP_FOLDER = '~/steam-screenshots/webp'
BOTH_ORIGINAL_FOLDER = '~/steam-screenshots/original'

# Log Level INFO, WARNING, ERROR, VERBOSE, Dedault INFO
LOG_LEVEL = 'INFO'

# Enable Service mode. Set to 'True' if you want to continuously run
# the script on a loop
RUN_AS_SERVICE = False

# Autorun interval in minutes, default 15. This only applies if the script
# is run in service mode with the '--service' argument
# RUN_INTERVAL = 15