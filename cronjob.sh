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
# Shell script to be called automatically by cron to invoke updatecv.py.
#
# Example:
# 0 22 * * * /path/to/the/cloned/auto_cv_repo/cronjob.sh
#
# Version 1.0, 2025-03-27 - The initial version, contains CLI and LinkedIn support. 
#

echo "==== Auto CV Updater job started ===="

# Provide the path to your Python executable here:
alias python="/opt/homebrew/bin/python3.11"
timestamp=`date "+%Y%m%d_%H%M%S"`
auto_cv_updater_dir=$(dirname $0)
# A default path for logs
logfile="${auto_cv_updater_dir}/Logs/updatecv_log_${timestamp}.txt"
# Define extra arguments for updatecv.py, e.g. -s to sync with pages
extra_arguments="-s -env=${auto_cv_updater_dir}/user_cfg.env -sj=${auto_cv_updater_dir}/User/skills_user.json -lc=${auto_cv_updater_dir}/User/linkedin_cookies_user.json"

echo "Executing python ${auto_cv_updater_dir}/updatecv.py ${extra_arguments}..." 2>&1 | tee ${logfile}
python ${auto_cv_updater_dir}/updatecv.py ${extra_arguments} 2>&1 | tee -a ${logfile}
# If above execution fails try for the second time (safari webdriver error: https://github.com/SeleniumHQ/selenium/issues/15160)
echo Trying for the second time... | tee -a ${logfile}
python ${auto_cv_updater_dir}/updatecv.py ${extra_arguments} 2>&1 | tee -a ${logfile}

echo "==== Auto CV Updater job finished ===="
