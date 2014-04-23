XBMC MyAnimeList Updater
========================

* Author:	Spencer Julian (<helloThere@spencerjulian.com>)
* Date:		May, 2012
* Last Update:	January 23, 2014
* Version:	0.4.6
* Github:	<https://github.com/kuruoujou/XBMal>
* Webpage:	<http://ramblingahoge.net/xbmal>

This is free software released under version 3 of the GPL License.

Good day!

This is XBMAL, The XBMC MyAnimeList Updater Plugin. It's still in the early stages and can't
quite do everything I want it to yet, but it does work with an XBMC TV Library to update
non-specials on MAL.

If you would like to help out (please do!), I could use bug reports and feature requests.
If you can code in python and want to help with the coding side of things, go ahead
and fork the project. That's what github's for, right?

Usage
-----
You'll first want to backup your MAL account. I'm serious, I can't be sure this won't
break things, although it works fine for my list.

If you're installing from the repository, skip the next paragraph.

Once you've backed up (you have backed up, right?), copy the `xbmc.script` directory into
your addons directory. In linux, this is `/home/<username>/.xbmc/addons`, in windows this
is `C:\Users\<username>\AppData\Roaming\XBMC\addons`, I think. I'm not sure for MAC OS X.

Ok, so you've installed the add on. Start XBMC if it's not already running, and
navigate to Addons -> Enabled Add-ons -> Services -> XBMAL. When you select XBMAL, you
should see the addon information page. Select 'Configure'.

Now you just need to configure your settings. Set your MAL username and password in the
appropriate boxes.

Settings configured? Ok. Go to the addons screen (whereever all of your installed addons
are listed, this varies from skin to skin), and select XBMAL. It's the one with the big,
blue, "MyAnimeList" icon. Once you select it, it will go through your entire XBMC TV show
library and try to guess the appropriate MAL mapping. This will take a while, particularly
with a large library, so now is a good time to go grab a sandwich.

Have you eaten your sandwich? Ok. You should now see a list of items that looks similar to
the following:

	XBMC show S1 -> MAL Show
	XBMC show S2 -> MAL Show
	XBMC show S1 -> Could not find mapping on MAL.
	Save above selections

Except it will have your shows instead of the generic strings I used above. Now you have
to go through each show listed and be sure that the mapping it guessed is correct. About
half of the time, it probably will be, but there are a few that will almost certainly be wrong.
Most notably, almost everything with multiple seasons (denoted by S) will not have the
correct mapping.

To fix a mapping, select the show you want to fix. A new menu should show up with all of
the search results from MAL for the particular show. If you see the correct one, simply
select it and the mapping will update. If you do not, you can select `None of the above`,
which will mark it to be skipped and not updated during MAL udpates, or you can select
`Manual Search`, where you enter your own MAL search for the show.

Once you have everything mapped, simply select the last item in the full list, labeled
`Save above selections`. This will write your mappings to it's configuration file.

Ok, so the configuration file is written. Now you just need to watch a video. Whenever
a video stops playing (it reaches the end or the user hits stop), the script will run and
update your watching, completed, and plan to watch lists appropriately.

If you add a show to XBMC, you will need to re-run the setup script. However, the setup
script will read your previous mappings, so you should only need to update the newest items,
which are typically at the bottom of the list. It will also run much faster, as it won't
look up all of your shows again. It will only look up the ones it has no clue about.

Questions, Comments, Concerns, Issues
-------------------------------------

If you have any of these, you can [submit an issue](https://github.com/kuruoujou/XBMal/issues) or
you can stop by the [xbmc thread for xbmal](http://forum.xbmc.org/showthread.php?tid=125866), or you can
even check out the [myanimelist thread for xbmal](http://myanimelist.net/forum/?topicid=414901). I look
forward to hearing from you!

TODO
----
* Make the list look nicer, like [this](http://www.howtogeek.com/wp-content/uploads/2011/10/2011-10-04_152227.jpg).
* Support mapping multiple seasons into a single show, i.e. Naruto or Eureka Seven
* When item is removed from XBMC library, remove from XML file (perhaps try to check with library cleaned?)
* Invert the list so that newest items are on top
* Make the setup script smarter when guessing mappings
  * Ignore anything with 'special', 'extras', etc. in the name
  * Guess seasons appropriately, i.e., season 2 looks for '2', 'II', etc., season 3 looks for '3', 'III', etc.
  * If above fails, search for additional punctuation. Silly japan and punctuation. (See Ika Musume for an example)
  * If all of the above fails, then default to first season title.
* Support videos along with tv shows
* Maybe, if we're really really lucky, and work on this really hard, get in the official repository?
