# Kano Apps

**Apps** is a small app installer and launcher for the **Kano OS**. It
downloads apps from [Kano World](http://world.kano.me/apps) and installs them
on your system. Being focused on ease of use, it colour codes each application
and may provide custom icons for some.

The applications are divided into several categories in the directory:

* Code,
* Games,
* Media,
* Others,
* Tools,
* and Experimental.

The program is written entirely in Python using **GTK 3.12** via the
[gi](https://wiki.gnome.org/action/show/Projects/GObjectIntrospection) bindings.

It also reads the desktop entries from `/usr/share/applications/` and displays
them on the **Others** pane.

![Kano World Window](http://i.imgur.com/5z3JgI9.png)

## Installation

To install **Apps** on your system, get the **kano-apps** from our package
repository:

```bash
sudo apt-get install kano-apps
```

If not on **Kano OS**, you might need to add our repo to your sources list:

```bash
deb http://repo.kano.me/archive/ release main
```

## Testing

This project doesn't require any compiling to run, just clone the repo and run
the main script:

```bash
git clone git@github.com:KanoComputing/kano-apps.git
cd kano-apps/bin
./kano-apps
```

## Contributing

We welcome anyone who would like contribute to this project. Check out the [bug
tracker](https://github.com/KanoComputing/kano-apps/issues) and
[wiki](https://github.com/KanoComputing/kano-apps/wiki). You might also find
some useful information in the [generic contributor's
guidelines](http://developers.kano.me/get-involved/) that apply to all of our
projects.

## License

This program is licensed under the terms of the GNU GPLv2. See the `LICENSE`
file for the full text.
