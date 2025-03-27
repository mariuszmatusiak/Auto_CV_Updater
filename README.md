# Auto CV Updater 

A script to update target crucial data in CVs, resumes, cover letters and research statements in a format used in the [CV Templates repo](https://github.com/mariuszmatusiak/CV-Templates).
Supports skills highlighting based on the provided job description (using CLI or a supported job portal).

Tested with Python v3.11.9 on macOS Sonoma and Safari v18.2.

Copyright (c) 2025 Mariusz Matusiak <mariusz.m.matusiak@gmail.com>

I'm a coffee-driven being who combines the power of neurons and caffeine in order to develop new technologies and solutions. If you like my work, you can support its future by sending me an [espresso injection](https://paypal.me/MMatk).

## Prerequisites
- cloned [CV Templates](https://github.com/mariuszmatusiak/CV-Templates) repo
- installed LaTeX distribution
- shell terminal with the GNU MAKE >= v3.8 support
- Python v3.11

## Setup

1. To make the program running correctly, first install the required dependencies listed in the requirements.txt file by calling:

```python
pip install -r requirements.txt
```

2. Next, update your data in the `User` directory, based on the command format in the CV-Templates repository. Update the following files:
- skills details in the json format, the `skills.json` file
- cookies for the authentication purposes on LinkedIn etc., the `*_cookies.json` file.

3. Finally, update your data in the `.env` file.

4. Make sure you have a couple of interesting jobs saved in one of the supported portals and let's get started!

## Example usage:

1. Run
```shell
python -3 updatecv.py [-c="Company Name"] [-j="Engineer"] [-l="Los Angeles, CA"] [-v=1]
```
to update your CV files using the provided data.

2. Run
```shell
python -3 updatecv.py -s
```
to update your CV files using saved jobs. 

## Register frequent job 

To run the script e.g. daily, add the cronjob.sh script to your crontab (Linux/macOS). Type `crontab -e` and add the following line:
```
# Run CV updater daily on 10 pm.
0 22 * * * /path/to/cloned/repo/cronjob.sh
```

## Changelog

### v1.0.0 [2025-03-27]
- The initial version, contains CLI and LinkedIn support. Based on the Safari WebDriver for Selenium.

## License

Auto CV Updater - automatize your CV modifications
Copyright (C) 2025  Mariusz Matusiak <mariusz.m.matusiak@gmail.com>

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