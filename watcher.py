#!/usr/bin/env python3
"""
watcher.py : A simple python based daemon to react to file change events
using user-defined actions.
"""
import os, sys, time, argparse, json, logging
import pyinotify

class watcher(pyinotify.ProcessEvent):
	def __init__(self, rules_file = None):
		self.pid_file	= '.watcher_'
		self.rules_file	= rules_file if rules_file else 'watcher_rules.json'
		self.rules_json	= {}

		self.fullpaths = {}
		self.wdds	= {}
		self.watch_manager = pyinotify.WatchManager()
		self.event_notifier = pyinotify.ThreadedNotifier(self.watch_manager, self)
		pass

	def process_IN_CLOSE_WRITE(self, event):
		logging.info("Path name: {} "
			   "Event Name: {}".format(event.pathname, event.maskname))
		fullpath_rules_file = os.path.abspath(self.rules_file)
		fullpath_pid_file = os.path.abspath(self.pid_file)
		if event.pathname == fullpath_rules_file:
			logging.info("Rules file %s modified." % self.rules_file)
			if self.__load_rules():
				self.__add_rules_to_watch()
		elif event.pathname == fullpath_pid_file:
			logging.info("pid file %s modified." % self.pid_file)
		else:
			key		= self.fullpaths[event.pathname]
			cmds	= self.rules_json[key]['cmds']
			# print (cmds)
			logging.info('Executing cmds for file %s.'
						' If control is not returned back use kill to stop the spawned process.'
						 % key)
			if type(cmds) == type('') :
				os.system(cmds)
			elif type(cmds) == type([]):
				for cmd in cmds:
					os.system(cmd)
			else:
				#If it is some other type leave it alone
				logging.warning('Unrecognized format for specifying cmds.')
			logging.info('Control handed back to the watcher daemon.')

		pass
	def process_IN_DELETE(self, event):
		logging.info("Path name: {} "
			   "Event Name: {}".format(event.pathname, event.maskname))
		fullpath_pid_file = os.path.abspath(self.pid_file)
		if event.pathname == fullpath_pid_file:
			self.pid_file_prsnt	= False
			sys.exit(0)
		pass

	def __load_rules(self):
		rules_file_prsnt = os.path.isfile(self.rules_file)
		if not rules_file_prsnt:
			try:
				#Create the rules JSON file if it doesnot exist.
				with open(self.rules_file,'w') as f:
					f.write('{}\n')
				return True
			except:
				return False
		with open(self.rules_file,'r') as f:
			try:
				read_json	= json.load(f)
			except:
				logging.error('Incorrect json format in %s.' % self.rules_file)
				return False
			else:
				self.rules_json	= read_json
				logging.info('Sucessfully read JSON rules from %s' % self.rules_file)
		return True

	def __add_rules_to_watch(self):
		# print (self.rules_json)
		for key in self.rules_json:
			cmds	= self.rules_json[key]['cmds']
			logging.debug("watch key: %s" % key)
			logging.debug(cmds)
			watch_this = os.path.abspath(key)
			pause_watch = self.rules_json[key]['pause'] if 'pause' in self.rules_json[key] else False
			try:
				wdd=self.watch_manager.add_watch(watch_this, pyinotify.ALL_EVENTS, quiet=False)
			except pyinotify.WatchManagerError as err:
				# print (err, err.wmd)
				logging.warning(err)
			else:
				self.wdds[key]		= wdd[os.path.abspath(key)]
				self.fullpaths[os.path.abspath(key)]	= key
			if (key in self.wdds) and pause_watch:
				self.watch_manager.rm_watch(self.wdds[key])

		pass

	def run(self):
		try:
			pid = os.fork()
			if pid > 0:
				# exit first parent
				sys.exit(0)
			else:
				daemon_pid	=	os.getpid()
				self.pid_file	= self.pid_file+'%d'%(daemon_pid,)
				try:
					open(self.pid_file,'w').close()
				except:
					# sys.stderr.write('Could not create pid file.\n')
					logging.error('Could not create pid file.\n')
					sys.exit(1)
				self.pid_file_prsnt = os.path.isfile(self.pid_file)
				self.watch_manager.add_watch(os.path.abspath(self.pid_file), pyinotify.ALL_EVENTS)

				if self.__load_rules():
					#Setup notofications to detect changes to the rules file
					self.watch_manager.add_watch(os.path.abspath(self.rules_file), pyinotify.ALL_EVENTS)
					#add the rules in rules_file to be watched by watch_manager
					self.__add_rules_to_watch()
					#Everything is successful so add the rules_file to the pid_file to keep track of things.
					try:
						with open(self.pid_file,'w') as f:
							f.write(os.path.abspath(self.rules_file)+'\n')
					except:
						logging.error('Could not access pid file. Exiting.\n')
						sys.exit(1)
				else:
					logging.error('Failed to load JSON rules file.')
					sys.exit(1)


				self.event_notifier.start()
				sys.stdout.write("watcher daemon is running. Delete pid file %s to stop.\n" % self.pid_file)
				logging.info("watcher daemon is running.")
				self.event_notifier.join()
				self.event_notifier.stop()
				logging.info("watcher daemeon exiting.\n")
				sys.exit(0)
		except OSError as err:
			logging.error('Fork #1 failed: {0}\n'.format(err))
			sys.exit(1)
		pass

if __name__=='__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-rules", help="change the default JSON file containing the watch rules.")
	parser.add_argument("-log", help="change the default logfile")
	args = parser.parse_args()
	logfile = args.log if args.log else 'watcher.log'
	# print (args.rules)
	# quit()
	logging.basicConfig(format='%(levelname)s %(asctime)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
						filename=logfile, level=logging.DEBUG)

	w   = watcher(rules_file=args.rules)
	w.run()
