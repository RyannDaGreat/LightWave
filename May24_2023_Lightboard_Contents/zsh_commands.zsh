cd /Volumes/CIRCUITPY && rm -rf * .* && git clone https://github.com/RyannDaGreat/Teensy4.1_Test . #Download repo into teensy after flashing it
cd /Volumes/CIRCUITPY ; lazygit #Don't run lazygit while running code; it will make it refresh repeatedly
screen  /dev/cu.usbmodem14101 ; killall screen #Run then kill when detach (via ctrl+a then ctrl+d)
#Buy teensy here: https://protosupplies.com/product/teensy-4-1-fully-loaded/