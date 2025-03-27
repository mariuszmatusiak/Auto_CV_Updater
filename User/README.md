# Description

This directory contains all the files that need to be customized by a user:
- linkedin_cookies.json
- skills.json

# Setup

You can edit the existing files or create your own versions of these files ignoring automatic Git versioning by using the following syntax:
- linkedin_cookies_**<your_suffix>**.json, e.g.: linkedin_cookies_winnie.json,
- skills_**<your_suffix>**.json, e.g.: skills_winnie.json

## linkedin_cookies.json

To update linkedin_cookies.json sign in to your LinkedIn account, open developer settings of your browser, copy the values of the following cookies:

- **bscookie** - cookie to remember that a logged-in user has been verified by the two-factor authentication
- **li_at** - cookie to authenticate a user
- **li_rm** - cookie set when a user has selected the "Remember me" option

and paste them into the corresponding fields of linkedin_cookies.json, replacing the **\<Add value of the ... cookie HERE\>** strings. A full description of the LinkedIn cookies can be found in https://www.linkedin.com/legal/l/cookie-table.

## skills.json

The skill.json file contains a database of a user's skills which are used by the script to update the \<CV-Templates\>/data/04_skills.tex according to either the explicitly determined skill area (`-sa` argument) or a given job description. Skills shall be given in the following format:
```json
{
    "skillsSectionNameAInLatex": [
        {"skill": "Skill A.1 name", "latex": "Skill~A.1~name~in~LaTeX~syntax", "area": ["skill_area_1", "skill_area_2", ...], "alias": ["Alternative A.1 name", ...], "is_case_sensitive": false},
        {"skill": "Skill A.2 name", "latex": "Skill~A.2~name~in~LaTeX~syntax", "area": ["skill_area_2", "skill_area_3", "generic"], "alias": ["Alternative A.2 name"], "is_case_sensitive": true},
        ...
    ],
    ...
    ...
    ...
    "skillsSectionNameZInLatex": [
        {"skill": "Skill Z.1 name", "latex": "Skill~Z.1~name~in~LaTeX~syntax", "area": ["skill_area_1", "skill_area_3", "generic"], "alias": [], "is_case_sensitive": false}
    ]
}
```
where:
- `skillsSectionNameAInLatex` is the skill section name defined in \<CV-Templates\>/data/04_skills.tex as  `\newcommand\skillsSectionNameAInLatex{...}`
- `skill` is a dictionary key for the skill text used in parsing a job description
- `latex` is a dictionary key for the LaTeX-compatible skill text used in resume files, e.g. containing '~', superscripts, or a math environment 
- `area` is a dictionary key for the list of common tags, which can be used to include all area-related skills. Useful with the `-sa` parameter. The "generic" tag shall be used to force mentioning the specific skill in a resume, even if it does not appear in the job description
- `alias` is a dictionary key for the list of alternative skill names
- `is_case_sensitive` is a dictionary key for a boolean value, used to specify if the skill shall be searched in the job description matching case

Copyright (c) 2025 Mariusz Matusiak