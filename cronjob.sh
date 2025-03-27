# Auto CV Updater - automatize your CV modifications
# Copyright (C) 2025  Mariusz Matusiak <mariusz.m.matusiak@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
# Shell script to automatically update target data in CVs by calling updatecv.py with cron.
#
# Version 1.0, 2025-03-27 - The initial version, contains CLI and LinkedIn support. 
#

echo "==== CV Updater job started ===="

alias python="/opt/homebrew/bin/python3.11"
timestamp=`date "+%Y%m%d_%H%M%S"`
logfile="Logs/updatecv_log_${timestamp}.txt"

cd "${HOME}/Projects/CV_Updater"
echo python updatecv.py -s 2>&1 | tee ${logfile}
python updatecv.py -s 2>&1 | tee -a ${logfile}
# If above failed try for the second time (safari webdriver error)
echo Trying for the second time... | tee -a ${logfile}
python updatecv.py -s 2>&1 | tee -a ${logfile}

echo "==== CV Updater job finished ===="
