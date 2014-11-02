#!/usr/bin/python

import sys, os, xbmcaddon

__addon__ = xbmcaddon.Addon( id = 'plugin.video.kg-ontv' )
sys.path.append( os.path.join( __addon__.getAddonInfo( 'path' ), 'resources', 'lib') )

if (__name__ == '__main__' ):
	import kgontv
	kgontv._main()