{
    "title": "Terminal",
    "tagline": "Graphics Terminal frontend",
    "description": "Are you up for a challenge? The terminal lets you take complete control of your computer and dig deep into its internals.",
    "slug": "terminal",

    "icon": "terminal-app",
    "colour": "#4A5152",

    "categories": ["code"],

    "packages": [],
    "dependencies": ["lxterminal", "kano-profile"],
    "launch_command": "kano-tracker-ctl session run 'lxterminal' 'lxterminal'",
    "overrides": ["lxterminal.desktop", "lxde-x-terminal-emulator.desktop"],
    "priority": 0
}
