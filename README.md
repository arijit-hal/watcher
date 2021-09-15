# Watcher

A simple python based daemon to react to file change events
using user-defined actions. The actions are to be provided in a JSON file.

- Works on Linux only (for now).


## Prerequisites

Requires python3 and the [pyinotify](https://github.com/seb-m/pyinotify) module which can be installed using
```code:bash
pip3 install pyinotify
```


## Example

Running the script is as simple as typing
```code:bash
$ ./watcher.py
```
at the shell prompt. After the launch, a line like 
```bash
watcher daemon is running. Delete pid file .watcher_2302527 to stop.
```
will be displayed in the terminal. At this point `watcher` has created a process id (pid) file in the directory, which you can use to kill the daemon simply by removing the file 
```code:bash
$ rm .watcher_2302527
```
The contents of the pid file points to the `.json` file containing the commands/ actions as rules to be executed while responding to file change events. By default, `watcher` looks for a file named `watcher_rules.json` in the working directory. If it does not find the rules file, `watcher` will create it for you, which you can then populate using appropriate JSON syntax.

E.g., if you want to watch a file named `hello.py` for changes and then run it in the terminal when it gets modified, the JSON rules file will look like
```code:JSON
{
	"hello.py" : { "cmds" : "python hello.py", "pause" : false}
}
```
The `"pause"` JSON-key is a boolean and, if needed, can be used to temporarily deactivate the execution of the commands listed under the field `"cmds"`. 

You can include additional commands under the `"cmds"` field as follows:
```code:JSON
{
	"hello.py" : { "cmds" : ["python hello.py", "cat hello.py"], "pause" : false}
}
```
Watcher will execute the commands for you, one after another, when `hello.py` has been modified. Individual commands can be paused by adding the comment symbol `#` (if you are using bash) at the start of that specific command.

Also, you can add other files to be watched in the rules file as follows:
```code:JSON
{
	"hello.py" : { "cmds" : ["python hello.py", "cat hello.py"], "pause" : false},
	"greetings.sh" : { "cmds" : "bash greetings.sh", "pause" : false}
}
```
In this case, the shell-script `greetings.sh` will be executed whenever it gets modified. 
## Logs 
Watcher stores all relevant information, such as info, debug messages and warnings, in a log file created in the directory where `watcher.py` was launched. The default name for the log file is `watcher.log` and can be changed using the `-log` option (see next section). If the log file already exists `watcher` will append the new messages to the end of the file, preserving the previous log entries.

## Extra options

The script `watcher.py` can take some additional command-line options to change its default behaviour:
* `-rules rules_file`	change the default JSON file containing the watch rules .
* `-log log_file`		change the default logfile
*  `-h`					show the help message and exits without launching the daemon.
# watcher
