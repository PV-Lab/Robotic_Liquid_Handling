# Spin Coater Major Debug

### Problems:
- Calibration using FRG spincoater code inconsistent like seen on personal laptop
- High friction between motor and encoder preventing smooth rotation while using odrivetool and while using FRG code
	- Likely cause 1: Interface between 3d printed spincoater components and motor
	- Likely cause 2: Uneven screw tightness between motor and base causing irregular rotation. Some smooth regions and some "sticky" regions 
- AMLS-Boxer Laptop may have improper USB drivers installed
- Odrive shuts off during calibration and attempts at velocity control. Could be from stalling?
- May be a grounding issue present within the circuit
- UCSD code calibrates ot2 twice then spins correctly, but calling sc.spin() afterwards does not work. 
	- Could be some specific inputs/configs are necessary that aren't happening when you use `odrivetool`
	- Could be that commands are added to a queue then executed in order?
- Motor used to rotate 90deg then stop and become unresponsive
- Possible firmware mismatach between v3.6 and AMLS-boxer, as my laptop's config works just fine (shouldn't be an issue because both follow `PASCAL/build_instructions`)
- Wire length could be too long to transmit commands from odrive to motor.

## New Info: 
- SC beeps twice during FRG code calibration because it performs the full calibration sequence, then the encoder offset calibration sequence. Once per beep
- **If odrive stops listening once entering closed loop control, it's usually noise on USB**


## Solution Paths:
- Adjust screw tightness on motor-base interface until rotation is smooth for a full revolution
- Remove encoder and attempt calibration/velocity control without it. Something weird may be going on
- Triple check USB driver versions on AMLS laptop (why is it shutting off now and not on your macbook? Likely downstream effect of high friction)
- Plot current and see what's going on
- USB noise could be the reason the v3.6 isn't working
- Attempt switching wire locations in screw terminals from top of terminal to bottom
- M0 channel of v3.6 could be bad  

## Fixes to attempt:

#### Configuration
- [ ] Attempt setting unused axis to idle mode. Also, prior to save configuration set both axes to idle
	- [ ] Set params -> set both axes to idle -> save -> calibrate axis -> set `motor` and `encoder.pre_calibrated` to true-> set both axes to idle -> save
#### Motor Control
- [ ] Play around with increasing `odrv0.axis0.controller.config.vel_gain`
	- Also check `my_odrive.motor1.current_control.Iq_setpoint` 
	- Make sure `vel_integrator_gain` nonzero
- [ ] Raise controller velocity limit `odrv0.axis0.controller.config.vel_limit`, default is 2 turns/sec
	- [ ] Can disable by setting ` odrv0.axis0.controller.config.enable_vel_limit = False` 
	- [ ] If want to prevent error upon exceeding motor speed: `odrv0.axis0.controller.config.enable_overspeed_error = False`
- [ ] Sensorless control guide (SENSORLESS DOES NOT SUPPORT STOPPING OR DIRECTION CHANGES):
	- `odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL`
	- Four new params must be set:
		- `motor.sensorless.pm_flux_linkage = 5.51328895422 / (<pole pairs> * <motor kv>)`
		- `motor.sensorless.spinup_current`: motor current during spinup, in amps
		- - `motor.sensorless.spin_up_acceleration`: acceleration (slope) of the spin-up velocity ramp, in rad/s^2 electrical
		- - `motor.sensorless.spin_up_target_vel`: the speed at the end of the velocity spin-up ramp, where we switch over to sensorless closed loop. In rad/s electrical.
		- alternative guide from odrive docs: 
```
			odrv0.axis0.controller.config.vel_gain = 0.01
			odrv0.axis0.controller.config.vel_integrator_gain = 0.05
			odrv0.axis0.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
			odrv0.axis0.controller.config.vel_limit = <a value greater than axis.config.sensorless_ramp.vel / (2pi * <pole_pairs>)>
			odrv0.axis0.motor.config.current_lim = 2 * odrv0.axis0.config.sensorless_ramp.current
			odrv0.axis0.sensorless_estimator.config.pm_flux_linkage = 5.51328895422 / (<pole pairs> * <motor kv>)
			odrv0.axis0.config.enable_sensorless_mode = True

# to start the motor after these inputs: 
			odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
```

---

(03/31/25) *Increasing velocity limit to 35 turn/sec enabled velocity control to work on the first attempt. This is the first time velocity control has worked in a controlled and understandable way, as opposed to the unpredictable jerking motions or max speed rotations followed by things slowing down. The following chain of commands were issued: `odrv0.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE` -> `dump_errors(odrv0) # note no errors were seen here` -> `odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL` -> `odrv0.axis0.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL` -> `odrv0.axis0.controller.input_vel = 10` -> `odrv0.axis0.controller.input_vel = 0`. The motor turned at a steady 10 turn/sec wihout interruptions or chattering, and following the command to return velocity to 0, the motor ceased rotation.* 

***Note: once velocity went to 0 on the motor, white dust/smoke (unable to determine which) rose from near the OT2's deck towards the top of the fume hood. The motor was cool to the touch and there is a 20ul pipette tip rack in deck slot 6 immediately behind the spincoater in deck slot 3. The current belief is that this is residue from a prior opentrons experiment rather than smoke from frying the motor.***

*Following this successful velocity control run, another set of commands: `odrv0.axis0.controller.input_vel = 15` -> `odrv0.axis0.controller.input_vel = 0` was issued, but the motor remained motionless and cool to the touch with no dust or smoke. calling `dump_errors(odrv0)` returns the following:*

```
system: no error
axis0
  axis: Error(s):
    AxisError.MOTOR_FAILED
    AxisError.CONTROLLER_FAILED
  motor: Error(s):
    MotorError.UNKNOWN_TORQUE
    MotorError.UNKNOWN_VOLTAGE_COMMAND
  DRV fault: none
  sensorless_estimator: no error
  encoder: no error
  controller: Error(s):
    ControllerError.SPINOUT_DETECTED
  axis: no error
  motor: no error
  DRV fault: none
  sensorless_estimator: no error
  encoder: no error
  controller: no error
```
*Using velocity control instead of ramped velocity control means speed has to be reached instantly. Decreasing the motor's speed instantly or switching directions can cause current to spike, and if the current spike is greater than the current limit the motor will fail. Attempting the same set of commands with ramped velocity control yields the same error trace as above. However, it is seen that following smooth rotation for a few seconds, the motor begins to wobble and the speed varies. Finally, the motor comes to a halt and the bottom becomes hot.*

*Removing the encoder and rotating the motor by hand does not present any problems. Motion is smooth through a full rotation without snagging. Placing the encoder and deck mount atop the motor introduces a snagging point, and this is the likely cause of the wobbling at higher RPM. Ramped velocity control will be attempted at 1 turn/sec instead to see whether this behavior continues and how soon it arises.* 

*Immediately following the above test, calibration was performed to attempt the lower speed velocity control. However, upon calibration the following message appeared:*

```
 encoder: Error(s):
    EncoderError.CPR_POLEPAIRS_MISMATCH
```

Repeated ramped velocity control test after adjusting encoder fasteners. New error trace below: 
```
system: no error
axis0
  axis: Error(s):
    AxisError.MOTOR_FAILED
    AxisError.CONTROLLER_FAILED
  motor: Error(s):
    MotorError.CURRENT_LIMIT_VIOLATION
    MotorError.UNKNOWN_TORQUE
  DRV fault: none
  sensorless_estimator: no error
  encoder: no error
  controller: Error(s):
    ControllerError.OVERSPEED
axis1
  axis: no error
  motor: no error
  DRV fault: none
  sensorless_estimator: no error
  encoder: no error
  controller: no error
```
*Following this error, the odrive was rebooted and calibration was performed again. Motor observed making unprompted rotations prior to calibration or switching to closed loop control. To fix this, switch from velocity control to torque control prior to entering closed loop control `odrv0.axis0.controller.config.control_mode = CONTROL_MODE_TORQUE_CONTROL`. Otherwise, a current limit violation will occur.*

*An identical sequence of velocity control commands was issued in subsequent tests. However, given the spinout and current limit errors from earlier runs, the torque on the screws that fasten the encoder to the deck mount was increased alongside the torque on those between the deck mount and the base. Calibration proceeded successfully but the motor stalled during velocity control. Current limit was raised to 46A to match the motor's specification prior to this test and therefore the **motor began smoking profusely**. Need to investigate why the controller seems to be holding commands in a queue now as opposed to the earlier tests today.*

*Next things to test are a new encoder deck mount that eliminates need to use spacers on the screws, swapping the orientation of the screws with their nuts, and reverting the controller's configuration to that from the earlier test.*


---

#### Procedural
- Live plot behavior (see guide in reference info). Isolate the following:
	- [ ] Voltage
	- [ ] Current
	- [ ] Velocity
	- [ ] Encoder Position

 --- 


 
 ---
 

#### Mechanical 
***Overarching Goal: Reduce Friction 
- [ ] Alter fastening method for securing encoder to deck mount. Current spacer and nut combination is janky
- [ ] Alter geometry of encoder-deck mount
- [x ] Adjust torque on encoder deck mount fasteners

  	---
  	(03/12/25)
  	*This got rid of the "sticky" region of rotation for the motor. Originally tightened with hex wrench, however this likely had too much clamping force, which results in too much friction due to direct contact between deck mount and motor. Hand tightening proved to be fine. Deck mount remains affixed to base, and motor can rotate smoothly.*

   *Now attempting calibration and velocity control with only the motor and encoder. Upon removal of fasteners, rotation during calibration stays choppy. Attempting the same process on other USB port to see if this is a signal issue, an issue with FRG's code, or a hardware issue. Upon changing the fastener torque, the velocity control command remained dead until USB port switched from LEFT to RIGHT. See further explanation in electrical section.*

  	---
  
- [ ] Switch from o-ring to sheet of rubber at drone-deck interface
- [ ] Loosen fasteners at motor-deck interface
      ---
      	(03/12/25)
	*Motion during calibration makes encoder deck mount walk if fasteners not included. Motor moving in more than 1 axis indicating it is either not level or the o-ring isnt compressed evenly, causing wobbly rotation due to non flat base. **attempt without o-ring at some point to confirm***
	*Note: Still testing without the bowl or chuck attached to the motor. Very low clearance between bodies so it is crucial to avoid too many clamping forces upon the motor--as fully assembled device has too much friction.*
      ---
- [ ] Shorten 3d printed chuck for encoder (no contact between bowl and chuck = no friction) <- imperative lock nut fully fastened, but right now the motor can't rotate at all if fully fastened
	- Likely the most bang for buck at mechanical side
	- **Note:** instead of a lock nut, FRG uses a hex shaft from mcmaster. They then glue an o-ring to the top of the hex shaft Here: we use the nut that comes stock with the drone motor, and the o-ring is glued to the top of the chuck (MODIFY CHUCK SO ITS OPENING AT THE BASE ISN'T TOO LARGE)

	---
      (04/02/25)
      *Following semi-successful run on 3/31 that ended in a smoked motor, a better encoder-motor mounting procedure will be adopted in order to keep friction to a minimum and make small adjustments to fastener torque less catastrophic. A set of spacers for the encoder were 3d printed at thicknesses of 1.5, 2, and 2.5mm, used to ensure encoder has 3 points of contact with flat surfaces and can't deflect as easily. Lower effort and faster iteration time than a full redesign of the encoder deck mount, especially because the latter is an STL mesh rather than a solid STEP object in CAD.

      Additionally, the smoked motor was replaced as it is of no use if the enamel between windings has eroded. The code that worked will be ran a second time but with a far lower peak velocity and velocity ramp rate. Current spikes should be kept to a minimum. Inertial load on the motor should be low given the low weight of the chuck + glass slide, so friction and acceleration are the next levers to pull.

      Upon inspection of broken motor, degradation of the windings is observed. The sheath around one of the motor's wires is also damaged, as the screw securing the motor to the base was in contact with that sheathing and likely provided a path for stall current to travel.

      The encoder sagging has been determined to be the final source of excessive friction as well as the uneven rotation. Using some combination of the spacer pieces will likely fix the sag issue. Using the 2.5mm spacer at the motor contact area and the 2mm spacer at the back to contact the deck plate will likely fully support the base and prevent any additional moment being placed upon the shaft. Update design and continue iteration on 04/03.
	---

#### Electrical 
- [ ] USB noise is source. Use [ODrive USB Isolator](https://odriverobotics.com/shop/usb-isolator) or different USB port as a fix
	- Recall in 2.009 when macbook USB for Teensy 4.0 signals was functional but power bank was not
	- Also recall BNC connectors being the issue and them working once connectors were stripped due to problems with how the BNC transferred power
   
    ---

(03/12/25) **New Find**
   	*Switching to RIGHT usb port of AMLS laptop brings SC closer to the state seen when using personal laptop. `sc.stop()` actually transmits to the odrive now and resets it, whereas before the code would remain stuck and incapable of a keyboard interrupt. Also, sc.set_rpm() returns to familiar behavior of doing approx 90deg turn then stopping. Now that it is back to a familiar point, will move to diagnosing errors using odrivetool instead of FRG code. Need more explicit visibility into whats going on.*

    *Upon moving to odrivetool and running `odrv0.axis0.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE`, the odrive completed the calibration motion--though shut off and became unrecognizable to the laptop upon plugging it in again.*

(03/31/25) *After adjusting the speed limit for the motor, the left USB port has become functional. Running code from FRG will be avoided for the time being until raw odrivetool commands are bug free.*
    ---
- [ ] May need to shorten wire to prevent ground loop
- [Ferrite rings](https://shop.odriverobotics.com/products/n97xgxel6y0ufvunsxq70kih4p19nx) can also reduce noise 
- [ ] Switching encoder to 3.3V instead of 5V 
- [ ] Velocity dying after rotating for a few seconds until rebooting seems to be an encoder issue per [here](https://discourse.odriverobotics.com/t/in-velocity-control-the-velocity-dies-off-and-doesnt-start-again/8093/12)
- [ ] Check encoder CPR value
    Encoder CPR value could be a few % off, harming functino. In general encoder can be source of dysfunction even without throwing errors
- [ ] Check `odrv0.axis0.motor.config.requested_current_range` and set it higher in case there are spikes higher than the limit
- [ ] Look at [index search via encoder](https://discourse.odriverobotics.com/t/velocity-control-mode-only-works-for-a-couple-seconds/2362/2)
- [ ] Check if contacts good between odrive and encoder. 


## Reference Info: 
- [PASCAL Spin Coater Build Instructions](https://github.com/fenning-research-group/PASCAL/tree/main/build_instructions/spincoater)
- [Live plotting current for v3.6](https://docs.odriverobotics.com/v/0.5.6/odrivetool.html#liveplotter)
- [Control modes not working v3.6](https://discourse.odriverobotics.com/t/control-modes-not-working/8620/3)
- [Motor does not work in velocity control](https://discourse.odriverobotics.com/t/motor-does-not-move-in-velocity-control/2644)
- [Velocity dies and doesn't start again](https://discourse.odriverobotics.com/t/in-velocity-control-the-velocity-dies-off-and-doesnt-start-again/8093)
- [Bizarre errors on ODrive v3.6](https://discourse.odriverobotics.com/t/bizarre-errors-on-odrive-v3-6-position-mode/7374)
- [ODrive Nuggets](https://www.andyvickers.net/2022/11/25/odrive-nuggets/)
- [ODrive Setup Driving Me Insane](https://discourse.odriverobotics.com/t/odrive-setup-driving-me-insane/9781)
- [ODrive shuts off](https://discourse.odriverobotics.com/t/odrive-shuts-off/7088)
- [Every time need calibration of ODrive upon reboot/restart](https://discourse.odriverobotics.com/t/every-time-need-calibration-of-odrive-when-i-reboot-or-restart-the-odrive/6435)
- [Constantly having to reset](https://forum.odrive.com/t/constantly-having-to-reset-odrive/3795)
- [Unresponsive Board](https://discourse.odriverobotics.com/t/unresponsive-board/9225)
- [3 Months and no progress with ODrive v3.6](https://discourse.odriverobotics.com/t/3-months-and-no-progress-with-odrive-v3-6-for-quadruped/10095)
- [Sensorless mode](https://discourse.odriverobotics.com/t/sensorless-mode/164/15)
- [ODrive Workshop](https://www.youtube.com/watch?v=Ym3srZ0MRIA)
- [Problem with closed loop velocity control](https://discourse.odriverobotics.com/t/problem-with-closed-loop-velocity-control/1529/10)
- [Velocity control mode only works for a couple seconds](https://discourse.odriverobotics.com/t/velocity-control-mode-only-works-for-a-couple-seconds/2362/2)
- [Weird ODrive Encoder Issue](https://www.xsimulator.net/community/threads/weird-odrive-issue.16405/)
- [ODrivetool Liveplotter Error Fixes](https://discourse.odriverobotics.com/t/liveplotter-error-qapplication-was-not-created-in-the-main-thread/8954/7)
- [Motor Spinout at Bottom of Page](https://docs.odriverobotics.com/v/latest/manual/control.html)
- [Specific Axis State & Control Mode Representations](https://docs.odriverobotics.com/v/latest/fibre_types/com_odriverobotics_ODrive.html#ODrive.Axis.AxisState)


