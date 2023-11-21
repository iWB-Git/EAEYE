
# Lighthouse Sports Back End API

API connecting the front end for Lighthouse's scouting platform with the MongoDB database, as well as performing server side computations. The goal is to do as much work on the back end as possible to reduce the load on a user's device and network connection.

## Installation and Usage

Clone this repository using the IDE/development environment of your choice, and install all of the packages held in requirements.txt; be sure to set your database username, passcode, and URI in the environment variables of your run/debug configuration.

**NOTE: Do not hardcode these values, *only* set them as environment variables. Failure to do so is a security risk if someone was to gain access to your code.**

The three variables that need to be set are:

    1. DB_URI
    2. DB_USERNAME
    3. DB_PASSWORD

If you are unsure of any of these, or need to request access, please reach out to me (Bryce) either through WhatsApp (+16037819501) or at my email bryce@carlislecapital.com.

## Issues

Try to keep all tasks documented with the opening of issues, whether that be through the project board or just opening an issue on this repository. Give it a succinct but detailed title involving the method/endpoint if applicable, what the issue is, and assign yourself/whoever is relevant to the issue. This will help with our task management as well as lends itself to proper branching, as discussed below.

## Branching

Branches will be used to ensure tracking of changes to the codebase. The main branch is at the top and will hold the code for the live deployment, followed by test, then development branches. This gives multiple levels of safety to freely work on development and testing without risking the deployed API. Moving up the chain will require pull requests that must be reviewed by another developer before any merge. Branches can be merged from from any level to main, as long as the new code has been properly tested to ensure no issues will arise with main once deployed.

A new branch can be formed from any existing branch, however if possible using main to create a new branch is best; this will reduce miscellaneous code that will need to be reviewed during pull requests, however if code from another existing branch is needed it's acceptable to use that.

**NOTE: Please do not make any changes to the branch 'backup'. This branch will be updated periodically by an admin to ensure a stable copy of the API is at the ready in case anything ever goes wrong.**

#### Branch Naming

The standard branch naming conventions are to begin any new branch with author name, a category, an ID number if the branch is created to work on a specific issue, and a <u>short</u> description of the task/branch. Each category needs to be delimited: use slashes (/) for the categorization words and dashes (-) for words inside of a category.

So for example if I was working on an issue with the number 40 to add player profile pages, the branch name would be:

`bryce/feature/40/player-profiles`

The general categories will be:

    ● hotfix  | for critical issues that need to be solved ASAP, solutions
                may be temporary
    ● bugfix  | for fixing reported bugs
    ● feature | adding, removing, or editing existing features
    ● test    | to test your code before submitting a pull request to main
    ● dev     | development branches, more experimental branches to code
                freely as needed

Feel free to use other categories if these don't accurately describe the intended branch's purpose, just be sure to keep the category short and descriptive and keep naming conventions consistent.

More info on branch naming can be found [here](https://tilburgsciencehub.com/building-blocks/collaborate-and-share-your-work/use-github/naming-git-branches/).

## Documentation

Documentation is in the process of being generated to provide to the front end developers. More information will be provided when this is established.

## License

Copyright © Lighthouse Sports Limited - All Rights Reserved

Unauthorized copying or distribution via any medium is strictly prohibited

Proprietary and confidential

Written by Bryce Sczekan, \<bryce@carlislecapital.com\> October 2023
