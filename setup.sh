#!/bin/bash

#
# For quick setup of virtualenv
#

[ -d env ] && echo "deleting old virtualenv" && rm -rf env 

if [ -z "$(which python3)" ]; then
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    brew install python3 
fi

if [ -z "$(which virtualenv)" ]; then
    pip3 install virtualenv
fi


cat << EOF
         _   _   _                             _     _             _
 ___ ___| |_| |_(_)_ _  __ _   _  _ _ __  __ _(_)_ _| |_ _  _ __ _| |___ _ ___ __
(_-</ -_)  _|  _| | ' \/ _\` | | || | '_ \ \ V / | '_|  _| || / _\` | / -_) ' \ V /
/__/\___|\__|\__|_|_||_\__, |  \_,_| .__/  \_/|_|_|  \__|\_,_\__,_|_\___|_||_\_/
                       |___/       |_|
EOF

DIV="$(python -c "print '\n'+'-'*60+'\n'")"

pip install virtualenv
virtualenv -p $(which python3) env
source ./env/bin/activate

cat <<EOF
 _         _        _ _ _                _                       _             _
(_)_ _  __| |_ __ _| | (_)_ _  __ _   __| |___ _ __  ___ _ _  __| |___ _ _  __(_)___ ___
| | ' \(_-<  _/ _\` | | | | ' \/ _\` | / _\` / -_) '_ \/ -_) ' \/ _\` / -_) ' \/ _| / -_|_-<
|_|_||_/__/\__\__,_|_|_|_|_||_\__, | \__,_\___| .__/\___|_||_\__,_\___|_||_\__|_\___/__/
                              |___/           |_|
EOF

pip install pyfiglet colorama opencv-python pyobjc-framework-Quartz

cat <<EOF
 ___   ___  _  _ ___
|   \ / _ \| \| | __|
| |) | (_) | .\` | _|
|___/ \___/|_|\_|___|

EOF

echo $DIV
echo "now run \"source activate\" to activate virtualenv"
