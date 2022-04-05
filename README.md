# Spotify Releases Tracker
A Spotify Script that search for new releases for your chosen artists

## Prerequisites:

#### Spotify API Keys - https://developer.spotify.com/dashboard/

* After building a application in the spotify dashboard you will need the following keys:
  - App Client ID
  - App Client Secret
  - Your User ID

Obtained keys must be as environment variables

#### Spotify Authorization

* You will need to set a callback uri witch will be used to retrieve the token for spotify actions.

## Running the Script

1. Start ```main.py``` in a console
2. Choose between saving/removing artist, show last saved releases or search for new releases.

## Purpose

This script was built with the purpose of using it's functions to provide data for any given app that wants to access any given artists new releases. For a imediate use, i created a structure to use them from command line. Feel free to change and adapt for your own project.


## License

This program is a free software: you can redistribute it and/or modify
it under the terms of the [GNU General Public License](LICENSE.txt) as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
