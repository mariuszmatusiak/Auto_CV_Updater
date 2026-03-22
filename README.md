# Auto CV Updater

A script to update user's data in CVs, resumes, cover letters and research statements in a format used in the [CV Templates repo](https://github.com/mariuszmatusiak/CV-Templates).
Supports skills highlighting based on the provided job description (using CLI or a supported job portal).

Tested with:
- Python v3.11.9 on macOS Sonoma with Safari v18.2,
- Python v3.14.0 on Windows 11 with Firefox v148.0.2

Copyright (C) 2026 Mariusz Matusiak <coffeedrivenengineer@gmail.com>

I'm a coffee-driven being who combines the power of neurons and caffeine in order to develop new technologies and solutions. If you like my work, you can support its future by sending me an [espresso injection](https://paypal.me/MMatk).

## Prerequisites
- cloned [CV Templates](https://github.com/mariuszmatusiak/CV-Templates) repo
- installed LaTeX distribution with latexmk
- shell terminal with the GNU MAKE >= v3.8 support, Git Bash recommended
- Python >=v3.11

## Setup

1. To make the program running correctly, first install the required dependencies listed in the requirements.txt file by calling:

```shell
pip install -r requirements.txt
```

2. Next, update your data in the `User/` directory, based on the command format in the CV-Templates repository. Update the following files:
- skills details in the json format, the `example_skills.json` file

3. Finally, the below information needs to be provided as well. For convenience it can be delivered as a cmd line argument, environment variable, or in the `.env` file:
- a path to the CV Templates dir, `--cv_dir` or `$CV_DIR`
- for LinkedIn:
    - a base64-encoded token with the LinkedIn credentials in the following form `<account_e-mail>::<account_password>`, `$LIN_KEY`

4. Make sure you have a bunch of interesting jobs saved in one of the supported portals and let's get started!

## Example usage:

1. To update your CV files using all the registered job fetchers.
```shell
python -3 updatecv.py -s -b=Firefox -sj=./User/example_skills.json -cv=D:\CV_Templates
```

2. To update your CV files for a specific job webpage (TBD).
```shell
python -3 updatecv.py --url=<job page>  -b=Firefox -sj=./User/example_skills.json -cv=D:\CV_Templates
```

3. To update your CV files using the provided data.
```shell
python -3 updatecv.py [-c="Company Name"] [-j="Engineer"] [-l="Los Angeles, CA"] [-v=1]
```

## Register a scheduled job

To run the script e.g. daily, add the cronjob.sh script to your crontab (Linux/macOS). Type `crontab -e` and add the following line:
```
# Run CV updater daily on 10 pm.
0 22 * * * /path/to/cloned/repo/cronjob.sh
```
On Windows, create a new task in Task Scheduler.

## Changelog

### v1.1.0 [2026-03-22]
- Solid refactoring, updated LinkedIn support after introduction of their Job Tracker page.

### v1.0.0 [2025-03-27]
- The initial version, contains CLI and LinkedIn support. Based on the Safari WebDriver for Selenium.

## License

Auto CV Updater - automatize your CV modifications
Copyright (C) 2026 Mariusz Matusiak <coffeedrivenengineer@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.