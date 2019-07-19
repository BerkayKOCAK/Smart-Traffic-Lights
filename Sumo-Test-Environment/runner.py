#!/usr/bin/env python
# Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.org/sumo
# Copyright (C) 2009-2018 German Aerospace Center (DLR) and others.
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v2.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v20.html
# SPDX-License-Identifier: EPL-2.0

# @file    runner.py
# @author  Lena Kalleske
# @author  Daniel Krajzewicz
# @author  Michael Behrisch
# @author  Jakob Erdmann
# @date    2009-03-26
# @version $Id$

from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import time

VEHICLE_AMOUNT = 50

TEST_TYPE = "Primary_vs_Street"

VERTICAL_VEHICLE_AMOUNT = 100
LIGHT_VERTICAL_RED = int(1.7 * 60) #2.5 * 60
LIGHT_VERTICAL_GREEN = int(0.8 * 60) #2 * 60

HORIZONTAL_VEHICLE_AMOUNT = 100
LIGHT_HORIZONTAL_RED = int(0.8 * 60)#1.5 * 60
LIGHT_HORIZONTAL_GREEN = int(1.7 * 60) #2 * 60

HORIZONTAL_SPEED = 10
VERTICAL_SPEED = 10

IS_PROPOSED_SYSTEM = False
HAS_PEDESTRIANS = False

VEHICLE_EVENTS_FILE_NAME = "vehicle_events.xml"
TRAFFIC_LIGHTS_EVENTS_FILE_NAME = "traffic_lights_events.txt"





VERTICAL_NEXT_TIME = 0
HORIZONTAL_NEXT_TIME = 0



# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import traci  # noqa


def generate_routefile(newSeed):
    #random.seed(time.time())  # make tests reproducible
    N = 3600  # number of time steps
    # demand per second from different directions
    pWE = 1. / 10	#goes from west to east
    pEW = 1. / 10	# goes from east to west
    pNS = 1. / 10	# goes from north to south
    pSN = 1. / 10   # goes from south to north
    CURRENT_SEED = newSeed
    random.seed(CURRENT_SEED)
    vehicles_that_goes_sideways_chance = random.randint(20,80) #SOURCE: http://www.mikeontraffic.com/study-results-right-turn-red-percentages/

    print("Vehicles have %s percent chance to go right in red" %(str(vehicles_that_goes_sideways_chance)))

    avg_bus_amount = 9.2    #SOURCE : https://ec.europa.eu/eurostat/statistics-explained/pdfscache/14273.pdf
    avg_motor_amount = 7.7  #SOURCE : https://ec.europa.eu/eurostat/statistics-explained/pdfscache/14273.pdf


    abc = 0

    with open("data/cross.rou.xml", "w") as routes:

        print("""<routes>
        <vType id="carWE" accel="30" decel="60" sigma="0.5" length="4.5" minGap="2.5" maxSpeed="60" \
guiShape="passenger"/>
        <vType id="carNS" accel="30" decel="60" sigma="0.5" length="4.5" minGap="2.5" maxSpeed="60"/>

        <vType id="motorWE" accel="60" decel="90" sigma="0.5" length="2.5" minGap="2.5" maxSpeed="90" \
guiShape="passenger"/>
        <vType id="motorNS" accel="60" decel="90" sigma="0.5" length="2.5" minGap="2.5" maxSpeed="90"/>

        <vType id="busWE" accel="15" decel="30" sigma="0.5" length="14" minGap="2.5" maxSpeed="30" \
guiShape="passenger"/>
        <vType id="busNS" accel="15" decel="30" sigma="0.5" length="2.5" minGap="2.5" maxSpeed="30"/>



        <route id="right" edges="51o 1i 2o 52i" />
        <route id="rightDown" edges="51o 1i 3o 53i" />

        <route id="left" edges="52o 2i 1o 51i" />
        <route id="leftUp" edges="52o 2i 4o 54i" />

        <route id="up" edges="53o 3i 4o 54i" />
        <route id="upRight" edges="53o 3i 2o 52i" />

        <route id="down" edges="54o 4i 3o 53i" />
        <route id="downLeft" edges="54o 4i 1o 51i" />

        """, file=routes)

        #print(open(VEHICLE_EVENTS_FILE_NAME,"r").read(),file=routes)

        # Old version of vehicle events

        HvehNr = 0
        VvehNr = 0
        vehID = 0
        departTime = 1
        #for i in range(N):
        
        SIDEWAYS_MAX_CHANCE = 20
        while HvehNr + VvehNr < HORIZONTAL_VEHICLE_AMOUNT + VERTICAL_VEHICLE_AMOUNT:
            #print("The spawned car amount for horizontal roads: " + str(HvehNr) + " The spawned car amount for vertical roads: " + str(VvehNr))
            
            abc += 1

            curCarTypeChance = random.randint(0,100)
            curCarType = "car"

            if curCarTypeChance < avg_bus_amount:
                curCarType = "bus"
            elif curCarTypeChance >= avg_bus_amount and curCarTypeChance < avg_motor_amount + avg_bus_amount:
                curCarType = "motor"

            
            if HvehNr != HORIZONTAL_VEHICLE_AMOUNT:
                
                curGoSidewaysChance = random.randint(0,100)
                CURRENT_SEED += 1
                #print(str(curGoSidewaysChance))

                if curGoSidewaysChance > vehicles_that_goes_sideways_chance:
                    print('    <vehicle id="right_%i" type="%sWE" route="right" depart="%i" />' % (
                            vehID,curCarType, departTime), file=routes)
                    vehID += 1
                    print('    <vehicle id="left_%i" type="%sWE" route="left" depart="%i" />' % (
                            vehID, curCarType,departTime), file=routes)
                else:
                   # print("CREATING VEHICLE THAT GOES SIDEWAYS")
                    print('    <vehicle id="right_%i" type="%sWE" route="rightDown" depart="%i" />' % (
                            vehID, curCarType,departTime), file=routes)
                    vehID += 1
                    print('    <vehicle id="left_%i" type="%sWE" route="leftUp" depart="%i" />' % (
                            vehID, curCarType,departTime), file=routes)
                


                vehID += 1
                HvehNr += 1

            if HAS_PEDESTRIANS == False and VvehNr != VERTICAL_VEHICLE_AMOUNT:
                
                curGoSidewaysChance = random.randint(0,100)
                CURRENT_SEED += 1
                if curGoSidewaysChance > vehicles_that_goes_sideways_chance:
                    print('    <vehicle id="down_%i" type="%sNS" route="down" depart="%i" color="1,0,0"/>' % (
                            vehID,curCarType, departTime), file=routes)
                    vehID += 1

                    print('    <vehicle id="up_%i" type="%sNS" route="up" depart="%i" color="1,0,0"/>' % (
                            vehID,curCarType, departTime), file=routes)
                else:
                    print('    <vehicle id="down_%i" type="%sNS" route="downLeft" depart="%i" color="1,0,0"/>' % (
                            vehID, curCarType,departTime), file=routes)
                    vehID += 1

                    print('    <vehicle id="up_%i" type="%sNS" route="upRight" depart="%i" color="1,0,0"/>' % (
                            vehID, curCarType,departTime), file=routes)                    
                vehID  += 1
                VvehNr += 1


            # print("vehNr: " + str(vehNr))
            # if random.uniform(0, 1) < pWE and vehNr < VEHICLE_AMOUNT:
            #     print('    <vehicle id="right_%i" type="typeWE" route="right" depart="%i" />' % (
            #         vehNr, vehNr), file=routes)
            #     vehNr += 1
            # if random.uniform(0, 1) < pEW and vehNr < VEHICLE_AMOUNT:
            #     print('    <vehicle id="left_%i" type="typeWE" route="left" depart="%i" />' % (
            #         vehNr, vehNr), file=routes)
            #     vehNr += 1
            # if random.uniform(0, 1) < pNS and vehNr < VEHICLE_AMOUNT:
            #     print('    <vehicle id="down_%i" type="typeNS" route="down" depart="%i" color="1,0,0"/>' % (
            #         vehNr, vehNr), file=routes)
            #     vehNr += 1
            # if random.uniform(0, 1) < pSN and vehNr < VEHICLE_AMOUNT:
            #     print('    <vehicle id="up_%i" type="typeNS" route="up" depart="%i" color="1,0,0"/>' % (
            #         vehNr, vehNr), file=routes)

            departTime += 3
        print("</routes>", file=routes)

# The program looks like this
#    <tlLogic id="0" type="static" programID="0" offset="0">
# the locations of the tls are      NESW
#     0   <phase duration="31" state="GrGr"/>
#     1   <phase duration="6"  state="yryr"/>
#     2   <phase duration="31" state="rGrG"/>
#     3   <phase duration="6"  state="ryry"/>
#     4   <phase duration="31" state="rrrr"/>    -> System has failed
#     5   <phase duration="31" state="GGGG"/>    -> System has failed
#    </tlLogic>

FINAL_STEPS = 0

def run():
    print("started")
    """execute the TraCI control loop"""
    HORIZONTAL_IS_GREEN = False
    VERTICAL_IS_GREEN = True
    VERTICAL_NEXT_TIME = LIGHT_VERTICAL_GREEN
    HORIZONTAL_NEXT_TIME = LIGHT_HORIZONTAL_RED
    step = 0
    
    sleepTime = 0.1
    totalTime = step * sleepTime
    curState = 2
    # we start with phase 2 where EW has green
    traci.trafficlight.setPhase("0", 2)

    # readVals = open(TRAFFIC_LIGHTS_EVENTS_FILE_NAME,"r")
    # realVals = []
    #nextChangeStep = int(LIGHT_1_RED)
    stepIndex = 0
    # if IS_PROPOSED_SYSTEM:
    #     for x in readVals:
    #         #print(x[:-1])
    #         realVals.append(x[:-1])
    #     nextChangeStep = int(realVals[0])
    #     print("nextChangeStep is: "+ str(nextChangeStep))
    gaveWarning = False
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        #if traci.trafficlight.getPhase("0") == 2:
            # we are not already switching

            #print("Changed lights to 3")
        traci.trafficlight.setPhase("0",curState)


            #else:
                # otherwise try to keep green for EW
                #traci.trafficlight.setPhase("0", 2)
		#if totalTime > 5:
		#	traci.trafficlight.setPhase("0",3)


        #time.sleep(sleepTime)
        step += 1
        totalTime += step * sleepTime
        #print("vert: " + str(VERTICAL_NEXT_TIME)  + str(VERTICAL_IS_GREEN) + " horz: " + str(HORIZONTAL_NEXT_TIME))
        if step == VERTICAL_NEXT_TIME:

            if VERTICAL_IS_GREEN:
                VERTICAL_NEXT_TIME += LIGHT_VERTICAL_RED
            else:
                VERTICAL_NEXT_TIME += LIGHT_VERTICAL_GREEN
                curState = 2

            VERTICAL_IS_GREEN = not VERTICAL_IS_GREEN
            # if VERTICAL_IS_GREEN:
            #    # print("TRAFFIC LIGHTS AT VERTICAL ROADS BECAME GREEN AT t=" + str(step))
            #     #print("GREEN")
            # else:
            #    # print("TRAFFIC LIGHTS AT VERTICAL ROADS BECAME RED AT t=" + str(step))

        if step == HORIZONTAL_NEXT_TIME:
           # print("HORIZONTAL CHANGED AT" + str(step))
            if HORIZONTAL_IS_GREEN:
                HORIZONTAL_NEXT_TIME += LIGHT_HORIZONTAL_RED
            else:
                HORIZONTAL_NEXT_TIME += LIGHT_HORIZONTAL_GREEN
                curState = 0

            HORIZONTAL_IS_GREEN = not HORIZONTAL_IS_GREEN

            # if HORIZONTAL_IS_GREEN:
            #    # print("TRAFFIC LIGHTS AT HORIZONTAL ROADS BECAME GREEN AT t=" + str(step))
            # else:
            #    # print("TRAFFIC LIGHTS AT HORIZONTAL ROADS BECAME RED AT t=" + str(step))


        if HORIZONTAL_IS_GREEN and VERTICAL_IS_GREEN:
            curState = 5
            #print("ERROR : ALL OF THE LIGHTS ARE GREEN. SYSTEM IS PRONE TO CRASHES!!")

        if not HORIZONTAL_IS_GREEN and not VERTICAL_IS_GREEN:
            curState = 4
            #print("WARNING : ALL OF THE LIGHTS ARE RED. SYSTEM MIGHT BE IMPROVED!!")


        # if step % 120 == 0 and not IS_PROPOSED_SYSTEM: #Change lights at every 2mins (standard, not the proposed system)
        #     print("Changed lights at step: " + str(step))
        #     curState = not curState
        # if IS_PROPOSED_SYSTEM and step == nextChangeStep:
        #     if curState == True:
        #         nextChangeStep += LIGHT_1_GREEN
        #     else:
        #         nextChangeStep += LIGHT_1_RED

        #    # print("BeforecurState" + str(curState))

        #     curState = not curState
        #     #print("curState" + str(curState))
        #     stepIndex += 1
        #     #nextChangeStep = int(realVals[stepIndex])
        #     print("Changed lights at step: " + str(step) + " next step:" + str(nextChangeStep))
    FINAL_STEPS = step
    print("step amount: " + str(FINAL_STEPS))
    filename = "C:/Users/Lenovo/Documents/pdfler/okul/BAHAR - 2019/Vehicular Networks/proje/sumo-tests/traci_tls/sonuclar/"
#    filename += str(HORIZONTAL_VEHICLE_AMOUNT) + "vs" +  str(VERTICAL_VEHICLE_AMOUNT) + "DEFAULT.txt"
    filename += str(TEST_TYPE) + "PROPOSED.txt"

    print(filename)
    f=open(filename,"+a")
    f.write(str(step) + "\n")
    f.close()
    traci.close()
    sys.stdout.flush()


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=True, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options

def executeSim():
    curSeed = 1
    testAmount = 20
    while(curSeed < testAmount +1):
        generate_routefile(curSeed)
        traci.start([sumoBinary, "-c", "data/cross.sumocfg",
                                "--tripinfo-output", "tripinfo.xml"])

        run()
        curSeed +=1
        print("[ " + str(curSeed-1) + " / " + str(testAmount) + " ] tests are done...")
    

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will starom offset to the  sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # first, generate the route file for this simulation
    
    executeSim()
    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    # traci.start([sumoBinary, "-c", "data/cross.sumocfg",
    #                          "--tripinfo-output", "tripinfo.xml"])
    # run()
    # print("step amount: " + str(FINAL_STEPS))


    # traci.start([sumoBinary, "-c", "data/cross.sumocfg",
    #                          "--tripinfo-output", "tripinfo.xml"])

    # run()
    # print("step amount: " + str(FINAL_STEPS))
