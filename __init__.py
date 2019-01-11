# import lazyLoad
# # lazyLoad.load("wx", includeKey = False)
# lazyLoad.load(
# 	"ast", 
# 	"copy", 
# 	"string", 

# 	"atexit", 
# 	"bisect", 
# 	"anytree", 

# 	"wx",
# 	"forks.objectlistview.ObjectListView", 
	
# 	# "win32print", 
# 	# "pubsub.pub", 
# 	"forks.pypubsub.src.pubsub.pub", 

# 	"PIL", 
# 	# "LICENSE_forSections", 
# )

from . import version
__version__ = version.VERSION_STRING

#Import the controller module as this namespace
from .controller import *
del controller