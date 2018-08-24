{
    "title": "Song Maker",
    "tagline": "An easy-to-use music synthesizer",
    "description": "Use this app from Google to draw music on your screen and hear the beats from your speakers!",
    "slug": "songmaker",

    "icon": "songmaker",
    "colour": "#95c630",

    "categories": ["tools"],

    "packages": [],
    "dependencies": [
        "chromium-browser",
        "kano-profile"
    ],
    "launch_command": "kano-tracker-ctl session run 'songmaker' 'chromium-browser --app=http://os-redirect.kano.me/songmaker --start-maximized'",
    "overrides": [],
    "priority": 700
}
