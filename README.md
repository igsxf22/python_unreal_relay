# Control Actors and Pawns in UE5 with Python in Realtime 

 >>>> Undergoing updates
  
`Components require UnrealEngine vers >= 5.6.1`
  
This project provides a minimalist method to exchange real-time data between a python script and an Unreal Engine 5 runtime.

This can be used to control UE5 actors, characters, and environments with simple data from Python:

- Use ArduPilot SITL to control the location and orientation of an actor in UE5

- Visualize a reinforcement learning agent interacting with the environment

...and to receive feedback from interactions with the UE5 environment:

- Add context to the SITL world by simulating a lidar height sensor 
<br>


## Components
`tcp_relay.py`
- Basic python TCP client with some error handling and a function to assemble floats in a list for the tcpRelay actor to parse in Unreal

`bp_tcpRelay.uasset`<br>
- Blueprint that uses the SpartanCode TCP Socket Plugin parent class to convert bytes from Python to an array of floats

`bpi_relay.uasset`<br>
- Basic blueprint interface to exchange data between the tcp_relay and other UE actors

`bp_pythonPawn.uasset`<br>
- Simple pawn that moves and rotates based on the values sent by the Python script

### Optional:
`bp_pythonPawn_Camera.uasset`
- Alternate pythonPawn that includes a camera

`pythonPawn_GameMode.uasset`
- Game Mode that uses `bp_pythonPawn` as the default player pawn (game view will be camera of  `bp_pythonPawn_Camera`)

 ## Quick How-To
 1. Start a new UE project and enable the SpartanCode TCP Socket Plugin
 2. Add the `bp_tcpRelay`, `bpi_relay`, and `bp_pythoPawn` to your project
 > Steps 3 and 4 are set by default, but its a good idea to check out these fields; you'll need them to redirect the TCP data if you want to use custom actors
 3. In your `bp_tcpRelay` actor, use the `Get Actor of Class` to identify the `pythonPawn` as the `send_to` actor
 4. Conversely, in your `bp_pythonPawn`, use the `Get Actor of Class` node to indetify the `bp_tcpRelay` actor
 5. Place your `tcpRelay` actor in the level
 6. Place the `pythonPawn` actor in the level
    - **OR** If you want to use the `pythonPawn_Camera` as a first-person character, don't place a pawn, just change GameMode to pythonPawn_GameMode
 7. Launch `tcp_relay.py` as a main python script and it will start listening for the tcp_Relay actor connect
 8. Launch UE level using Play in Editor, tcp_Relay actor will connect and both UE and Python should start printing the relay data
 9. The `pythonPawn` should begin moving and rotating based on the python script
 10. The python script will recieve bytes containing the three floats generated in realtime from the `pythonPawn` (you can decode to string, parse with .split() and convert to floats) 


## Setup from new Unreal Engine 5 - Blank Game with Blueprints

### Download SpartanCode TCP Socket Plugin
 - Fab Page: https://www.fab.com/listings/48db4522-8a05-4b91-bcf8-4217a698339b
 - Github: https://github.com/CodeSpartan/UE4TcpSocketPlugin

<br>

 If you download from Fab, it will be in your Epic Games Launcher, Unreal Engine Libray:

![Install Plugin to Libary](media/tcp_socket_plugin_uelibrary.jpg)

Then install to engine.

### Create a new UE5 Game with Blank Template
Enable blueprints.

### Launch Editor and Activate Plugin
1. Click Settings drop-down in the top-right of your editor window
2. Click Plugins
3. Search for 'tcp' and it should appear at the top of the list

![Project screenshot](media/tcp_socket_plugin_enable.jpg)

Enable plugin the and a window will pop-up up prompting you to restart UE Editor, click **Restart Now**

### Download Unreal Assets
```
bp_tcpRelay.uassest
bp_pythonPawn.uasset
bp_pythonPawn_Camera.uasset
bpi_relay.uasset
pythonPawn_GameMode.uasset
```
Create a `custom` folder in the `content` folder in the Content Drawer. In Explorer,place these blueprints in you Unreal Project/content folder

> For example on windows in the default Unreal Engine save path it looks like: <br>
 C:\Users\<username>\Documents\Unreal Projects\myTcpRelayProject\Content\custom

Back in Unreal Editor, they should appear in your content drawer:

![Project screenshot](media/downloaded_assets_in_content_drawer.jpg)

### Drag bp_tcpRelay actor and bp_pythonPawn pawn into the level

> If you're not seeing data, make sure you remembered to place the tcpRelay actor in your level

> If you want to use the bp_pythonPawn as the default player pawn instead, you'll probably have create a new blankGame mode

![Project screenshot](media/assets_in_level.jpg)

## Look for data exchange between Python and UE5
Run `tcp_relay.py` as main python script to create the relay sever.

> The code has notional variables for x, y, z, pitch, roll, yaw, which will increase by 1 every second and stream to the TCP Relay actor

With your TCP relay actor placed in the UE level, start the Play in Editor to launch the game runtime

- The UE Editor will print the data its receiving in yellow and sending in green<br>
- Floats_out from UE is default `'0.0 0.0 0.0'` but you can change the floats_out items if you want see it change in Python

![Project screenshot](media/data_exchanged.jpg)

- The Python code will print the msg_out and msg_in (23 fields out, 3 in by default)<br> 

![Project screenshot](media/python_data_exchanged.jpg)

> Make sure you're sending at least one value back to Python<br>
> Note that out and in are relative to the sender

### Controlling a basic UE5 Actor or Pawn
The example pawn has the following variables:
```
Premade:
    data_live: bool
    location: vector
    rotation: rotator
    floats_out = float_array (default 3 items)

Promoted from nodes to avoid conflicts:
    relay_actor: bp_tcpRelay actor (inherits class)
    floats_in: float_array (inherits size)
```
The example pawn recieves the x, y, z, roll, pitch, yaw in the first six items we send from python to UE.

```
floats_in[:3] --> location vector
floats_in[3:6] --> rotation rotator
```

Then we use an `Actor Set Location and Rotation` node using the location vector and rotation rotator

Start play-in-editor runtime. The pawn should begin moving and rotating based on the python values
![Project screenshot](media/success_pawn_control.jpg)

#### Change the basic TCP relay script
You can import the TCP_Relay class and create_fields_string function into your own python scripts, or copy the `tcp_relay.py` file, edit, and run as main.

All you have to do is add your own code to update the location x, y, z and the rotation roll, pitch, yaw
* Convert your values for location and rotation to `centimeters` and `degrees` before sending them to Unreal
```
while True:
  x, y, z = <code to update location> # centimeters
  roll, pitch, yaw = <code to update rotation>  # degrees
  fields[:6] = [x, y, z, roll, pitch, yaw]
  relay.msg = fields
```
> NOTE: Unreal uses a left-handed coordinate system: [Unreal Coordinate System](https://dev.epicgames.com/documentation/en-us/unreal-engine/coordinate-system-and-spaces-in-unreal-engine)<br>
>- If the `pythonPawn` in Unreal isn't moving or rotating as expected, you may need to invert the direction of some of your axes or rotations

Here's an overview of the entire process:
```
Python:
    with a TCP_Relay object
    creates msg_out string: "{x} {y} {z} {pitch} {roll} {yaw} ... "
    TCP Relay server sends bytes(msg_out) to client

UE5/tcpRelay:
    receives bytes(msg_in), parses to string and splits into list
    converts list of strings to floats and creates `floats_in` array
    relays floats_in array to pythonPawn through bpi_relay interface

UE5/pythonPawn:
    recieves floats_in array from tcp_relay via bpi_relay interface
    parses floats_in arrays by index to assign values to vectors, rotators, or bools with == nodes
    gets data from environment, such as 1.0 for a collision event or a distance using a line trace, to create floats_out array
    sends floats_out array to tcpRelay via bpi_relay

UE5/tcpRelay: 
    recieves floats_out from pythonPawn, encodes to bytes, returns to Python

Python
    recieves floats from tcp_relay as msg_in
    parses msg_in to floats and uses data in main loop

repeats
```
## Common Issues and Fixes

- **TCP Errors, 'socket in use'**
   - If python crashed or didn't close naturally, the socket might still be in use - Restart the python kernel

- **Downloaded unreal assets placed in the project folder, but don't appear in Content Drawer in Unreal Editor**
  - Make sure you're on Unreal Engine 5.5.3 or later

- **Can't change my Player pawn, option for `Default pawn - Select Pawn class` is grayed out**
  - Create a new blank blame game mode

- **pythonPawn isn't moving**
  - check that bp_tcpRelay is placed in the level
  - check that bp_tcpRelay `Get Actor of Class` node selects the exact pythonPawn you're trying to use
    - also check that you only have one pythonPawn of the class you selected, its only going to target the first one, or add your own rules
  - check that the `Get Actor of Class` node in the pythonPawn selects the proper bp_tcpRelay class, in case you made a modified one

- **tcp_relay.py isn't showing any data after saying "Connected"**
  - Make sure you didn't disconnect any nodes that the bp_tcpRelay actor uses to send data back to Python, even if its just 0.0's

- **pythonPawn is moving the wrong direction or rotating the opposite way**
  - Confirm that your python code is using Unreal's coordinate system, or add code to reconcile the differences before sending the values to Unreal
  - Check that your `fields[3:6]` are in the proper order for rotations: `[roll, pitch, yaw]`. If you want to use quaternions, you can change the fields and use another item, just make sure you make the proper adjustments in your pawn or actor blueprint 
