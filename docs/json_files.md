# Project Json Files

If you've taken a look in the project's *json* directory you might have noticed
a couple of files and wondered what they were for.

```
json
├── accepted_cfgs.json
├── commands.json
├── ctrl_exemptions.json
├── game_servers.json
└── test_data.json
```

These files are used by the app to do three different things.

1) They're used to generate the buttons on the controls and install pages.
2) They're used to validate user input from the controls / install pages.
3) They're used by the project's tests to verify things are working correctly.

The `accepted_cfgs.json` file is a list of all of the accepted game server cfg
files name I could find for the games supported by the LGSM.

The `commands.json` is a list of the accepted game server commands.

The `ctrl_exemptions.json` is a list of specific exemptions to the commands
list on a game server by game server basis. This is useful because certain game
servers do not support certain controls options, such as `bf1942` not
supporting the `console` option.

The `game_servers.json` file is a list of currently support LGSM game servers.

The `test_data.json` file is a mapping of gs script file names to the full game
server name, used by the project's tests.
