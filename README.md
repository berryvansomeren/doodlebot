# Doodlebot: A Lego Wall Plotter

By chance, I came across [this lego wall plotter by Marco Schulte](https://voot.de/projects/lego-wallplotter/).
It reminded me of the Lego Mindstorms project which was my first encounter with programming, 
and I really wanted to recreate this awesome project. 

I did not want to copy the original code, and also thought I could perhaps taylor it a bit more to my own desired workflow.
So, I quickly made a much simpler version of the code using only Lego Mindstorms standard functions. 
It worked by deciding for every piece of linear path, which motor had to run at max speed, how the speed of the other motor had to be scaled relatively, and for how long both motors had to run. 
However, I found out that when going up against gravity, the robot would undershoot targets, and when going down with gravity, the robot would overshoot targets. 
Then, I finally understood why Marco Schulte's code had this feedback loop that keeps checking the progress towards a target, and adjusts accordingly. 
I also found out that some of the functions that were used in the original code were undocumented. 
I was able to find more information about those functions [thanks to Anton's Mindstorms](https://www.antonsmindstorms.com/2021/01/14/advanced-undocumented-python-in-spike-prime-and-mindstorms-hubs/).

I then rewrote the entire thing in a way that minimized the amount of code on the device, and maximized precomputation of plotter instructions and creation of previews. 
This created in a workflow that allowed me to quickly catch any errors in normal modern python, before I even had to mess with micropython and lego mindstorms. 
I did not really change anything in the design of the lego construction of the robot. 
I only added a few pieces to make the frame just a tad more robust. Really, Marco Schulte's design for the plotter is absolutely perfect! 

## Gallery

<div align="center">
    <div >
        <a href="https://github.com/berryvansomeren/toucan/assets/6871825/d40b691e-e336-4a30-a128-b2d619c4e5a7">
            <img src="./doc/doodlebot_elephant.jpg" width="75%">
        </a>
    </div>
    <div>
        <a href="https://github.com/berryvansomeren/toucan/assets/6871825/08b851b3-d0eb-4a4a-a4c0-a49f6dffece8">
            <img src="./doc/doodlebot_nature.jpg" width="50%">
        </a>
    </div>
    <div>
        <a href="https://github.com/berryvansomeren/toucan/assets/6871825/17162b60-0fcf-4686-b48d-2760f5141289">
            <img src="./doc/doodlebot_tree.jpg" width="75%">
        </a>
    </div>
</div>
