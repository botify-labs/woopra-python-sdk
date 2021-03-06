Track customers directly in Python using Woopra's Python SDK

The purpose of this SDK is to allow our customers who have servers running Python to track their users by writing only Python code. Tracking directly in Python will allow you to track your users through the back-end without having to handle http requests manually.


Installation
============

::

   pip install woopra

Usage
=====
The first step is to setup the tracker SDK. To do so, configure the tracker instance as follows (replace mybusiness.com with your website as registered on Woopra and access_key with your Woopra API access key, encoded in base64):

::

   #import the SDK
   from woopra import WoopraTracker

   woopra_tracker = WoopraTracker("mybusiness.com", "access_key")


You can also configure the timeout (in milliseconds, defaults to 30000 - equivalent to 30 seconds) after which the event will expire and the visit will be marked as offline:

::

   # set the timeout to 15seconds:
   woopra_tracker.set_timeout(15000)

To identify a user, you should use the identify() function. You can choose to identify the visitor with his EMAIL, or with a UNIQUE_ID of your choice (in this case, make sure to re-use the same ID for a given visitor accross different visits).

::

   user_properties = woopra_tracker.identify(WoopraTracker.EMAIL,
      "johndoe@mybusiness.com", {
          'name' : 'Test Name2',
          'admin' : False
      }, IP_ADDRESS, # the IP address of the user
      USER_AGENT # the user agent
    )


And you're ready to start tracking events:

::

    woopra_tracker.track_event(user_properties, "play",
                               {"artist": "Dave Brubeck",
                                "song": "Take Five",
                                "genre": "Jazz"
                                })


Or just push the user information (without event tracking) by doing:
::

   woopra_tracker.track_identify(user_properties)


The search profile API is also supported:
::

   woopra_tracker.search_profile(user_properties)
