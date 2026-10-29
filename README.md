ArangoExec
=========

A Plugin for running Aql Queries commands in Sublime Text.

# Usage:
--------

```
{ "keys": ["ctrl+e", "ctrl+enter"], "command": "arango_exec" },
{ "keys": ["ctrl+y", "ctrl+enter"], "command": "arango_explain" },
{ "keys": ["ctrl+alt+y"], "command": "arango_list_connection" }
```

## How to Install

### Package Control *(Recommended)*

1. Package Control: **Install Package** `ArangoExec`
2. **Restart** Sublime Text

### Git

1. **Clone** to your packages folder `git clone git@github.com:jjchiw/ArangoExec.git`
2. **Restart** Sublime Text

# Configuration
---------------

Settings
--------

'Preferences' -> 'Package Settings' -> 'ArangoExec'

```json
{
    "connections": {
    	"someConnection" : {
    		"host"    : "127.0.0.1",
			"port"    : 8529,
			"username": "user",
			"password": "password",
			"database": "super_graphs"
    	},
    	"TestStress" : {
    		"host"    : "127.0.0.1",
			"port"    : 8529,
			"username": "user",
			"password": "password",
			"database": "test_stress"
    	}
    }
}
```

`username` and `password` are sent with HTTP basic auth. If your server has authentication disabled, leave `username` empty (`""`) and no credentials are sent. Connections use plain HTTP; HTTPS is not supported.

The first connection in alphabetical order is used until you pick another one with `arango_list_connection` (`ctrl+alt+y`).

Optionally add a top-level `"timeout"` (in seconds, default `500`) to the settings to change how long a request may take.

# TODO
--------

* ~~Use credentials~~
* ~~Function Intellisense (autocompletion)~~
* ~~Collections, Edges intellisense~~
* I know there are more things, but I'm not really sure right now what else :)

Inspired and Based on [SQLExec](https://sublime.wbond.net/packages/SQLExec) & [SublimeHttpRequester](https://github.com/braindamageinc/SublimeHttpRequester)
