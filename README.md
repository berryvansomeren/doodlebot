# Get Started

First install "LEGO® MINDSTORMS® Robot Inventor" from [here](https://www.lego.com/nl-nl/service/device-guide/mindstorms-robot-inventor).
This program (that I will call LMS) will be used to edit all code that is supposed to run on the hub.
I do not think you can really use PyCharm for that, as the python libraries inside LMS do not seem to be available outside LMS. 
You can find similar or related libraries, but not the same. 

So you need LMS for:
- the code that runs on the hub
- update hub and motor drivers
- transfer code to the hub

The rest we will do in PyCharm.


To create the files as expected in the hub program, use:

````commandline
python voot/svgtools/convert.py voot/svgtools/svg/heart.svg voot/svgtools/out
````




# Code for Lego Wallplotter

For details/how to use visit https://voot.de/projects/lego-wallplotter