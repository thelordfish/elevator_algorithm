
import sys
import re



def create_lift(current_floor, onboard_passengers, direction, passengers_drop_off, drop_off_floors, offboard_passengers, pick_up_floors, pick_up_destinations):
    lift = {"current_floor":current_floor, 
            "onboard_passengers": onboard_passengers,
            "direction": direction, 
            "drop_off_floors":drop_off_floors, 
            "offboard_passengers": offboard_passengers, 
            "pick_up_floors": pick_up_floors, 
            "pick_up_destinations": pick_up_destinations,
            "output_record" : []                                #For new frontend!
              }
    return lift

def valid_input(lift):
    # check if floor numbers are between 0 and 3
    valid_floors = [0, 1, 2, 3]
    if lift["current_floor"] not in valid_floors:
        print(f"Current floor {lift['current_floor']} out of range. Floors are 0, 1, 2, 3")
        return False

    for floor in lift["drop_off_floors"]:
        if floor not in valid_floors:
            print(f"Drop-off floor {floor} out of range. Floors are 0, 1, 2, 3")
            return False

    for floor in lift["pick_up_floors"]:
        if floor not in valid_floors:
            print(f"Pick-up floor {floor} out of range. Floors are 0 1, 2, 3")
            return False

    # make sure theres no more than 5 in the lift
    if lift["onboard_passengers"] > 5:
        print(f"Onboard passengers {lift['onboard_passengers']} exceeds capacity. Dangerous.")
        return False
    
    if lift['onboard_passengers'] < 0:
        print(f"Ghost detected? Cannot have negative passengers.. you entered [{lift['onboard_passengers']}]")

    # onboard passengers and drop off floors should match
    if lift["onboard_passengers"] != len(lift["drop_off_floors"]):
        print(f"Number of drop off requests and onboard passengers should match. Passengers: {lift['onboard_passengers']} Drop off floor requests {len(lift['drop_off_floors'])}")
        return False

    # make sure there are no negative numbers 
    for key, value in lift.items():
        if isinstance(value, int) and value < 0:  # Only check integers for negative values
            print(f"Negative value detected for {key}: {value}.")
            return False

    # check that the number of pick-up destinations matches the number of pick-up floors and offboard passengers
    if len(lift["pick_up_floors"]) != len(lift["pick_up_destinations"]) or len(lift["pick_up_floors"]) != lift['offboard_passengers']:
        print("Error: The number of pick-up floors, offboard passengers, and pick-up destinations are not consistent.")
        return False

#no need to check passengers_drop_offs as it is a completely redundant parameter
    return True

def find_next_move(lift):

    #for efficiency, store next drop off and pick up in variables
    next_drop_off = find_next_drop_off(lift)
    next_pick_up = find_next_pick_up(lift)

    #if there are no drop offs or pick ups, change direction
    if next_drop_off == None and next_pick_up == None:
            lift["direction"] = 1 - lift["direction"]

            #store variables again
            next_drop_off = find_next_drop_off(lift)
            next_pick_up = find_next_pick_up(lift)

            #if there's still none, then nothing more to do.
            if next_drop_off == None and next_pick_up == None:
                return None
            
    if next_drop_off != None:

        #check if it can pick people up on the way. 
        if next_pick_up != None and pick_up_on_way(lift, next_drop_off, next_pick_up) and lift_has_space(lift):
            return next_pick_up
        #if it can't then go straight to the drop off
        else:
            return next_drop_off
        #if theres no drop off go to a pick up
    elif next_pick_up != None:
        return next_pick_up
        #if theres no pick up then None
    else:
        return None


def lift_has_space(lift):
    return lift["onboard_passengers"] < 5 #check if it has space

def find_next_drop_off(lift):

    #iterate up from next floor to 3, return first dropoff floor found
    if lift["direction"] == 1 and lift["current_floor"] != 3:
        for floor in range(lift["current_floor"] +1, 4):
            if floor in lift["drop_off_floors"]:
                return floor
        return None
    #iterate down from current floor to 0, return first dropoff floor found
    if lift["direction"] == 0 and lift["current_floor"] != 0:
        for floor in range(lift["current_floor"] -1, -1, -1):
            if floor in lift["drop_off_floors"]:
                return floor
        return None
    
def find_next_pick_up(lift):

    #iterate up from next floor to 3, return first pickup floor found
    if lift["direction"] == 1 and lift["current_floor"] != 3:
        for floor in range(lift["current_floor"] +1, 4):
            if floor in lift["pick_up_floors"]:
                return floor
        return None
    
    #iterate down from current floor to 0, return first pickup floor found
    if lift["direction"] == 0 and lift["current_floor"] != 0:
        for floor in range(lift["current_floor"] -1, -1, -1):
            if floor in lift["pick_up_floors"]:
                return floor
        return None

def pick_up_on_way(lift, next_drop_off, next_pick_up):

    #if its going up, pick up <= drop off
    if lift["direction"] == 1:  
        return lift["current_floor"] < next_pick_up <= next_drop_off
    
    #if its going down, pick up >= drop off
    elif lift["direction"] == 0:  
        return next_drop_off <= next_pick_up < lift["current_floor"]
    return False



def process_drop_offs(lift, next_move):
    if next_move in lift["drop_off_floors"]:

        #remove departures from lift, add to onboard
        departures = lift["drop_off_floors"].count(next_move)
        lift["onboard_passengers"] -= departures

        #remove their drop off requests from lift
        lift["drop_off_floors"] = [floor for floor in lift["drop_off_floors"] if floor != next_move]

        #print status
        line = f"Dropping off {departures} passenger(s) on floor {next_move}."
        print(line)
        lift["output_record"].append(line)
    return lift
    
def process_pick_ups(lift, next_move):

    if next_move in lift["pick_up_floors"]:

        #add offboarders to onboarders
        offboarders = lift["pick_up_floors"].count(next_move)
        lift["onboard_passengers"] += offboarders
        lift['offboard_passengers'] -= offboarders

        #remove pick up requests from lift 
        lift["pick_up_floors"] = [floor for floor in lift["pick_up_floors"] if floor != next_move]

        #transfer/pop their offboard destination requests to onboard drop off requests
        for i in range(offboarders):
            lift["drop_off_floors"].append(lift["pick_up_destinations"].pop(0))

        #pass status to be printed and recorded
        line = f"Picking up {offboarders} passenger(s) on floor {next_move}"
        print(line)
        lift["output_record"].append(line)

    return lift

def lift_update(lift, next_move):
    #process drop offs and pick ups
    lift = process_drop_offs(lift, next_move)
    lift = process_pick_ups(lift, next_move)
    #update current floor
    lift["current_floor"] = next_move

    #print lift contents
    line = f"Passengers in the lift: {lift['onboard_passengers']}"
    print(line)
    lift["output_record"].append(line)

    return lift

def track_initial_passengers(lift, initial_passengers):

    #remove any departed initial passengers
    initial_passengers = [i for i in initial_passengers if i in lift['drop_off_floors']]  
    return initial_passengers


    

def update_time(lift, time, next_move, initial_passengers):

    time_taken = abs(lift["current_floor"] - next_move)

    #keep track of how the next move impacts different waiting times
    time["total_time"] += time_taken
    time["onboard_waiting_time"] += (time_taken * lift["onboard_passengers"])
    time["offboard_waiting_time"] += (time_taken * lift["offboard_passengers"])
    time['initial_passenger_time'] += (time_taken * len(initial_passengers))
   
    return time_taken, time

def validate_passenger_counts(lift):
    # Ensure that the number of passengers onboard never goes negative
    if lift["onboard_passengers"] < 0:
        print("Error: Negative passengers in the lift.")
        return False
    
    # Ensure that there are no more passengers to drop off than onboard
    if lift["onboard_passengers"] < len(lift["drop_off_floors"]):
        print("Error: More drop-off requests than onboard passengers.")
        return False
    
    return True

def lift(current_floor, onboard_passengers, direction, passengers_drop_off, drop_off_floors, offboard_passengers, pick_up_floors, pick_up_destinations, return_record=False):

    #initialize dictionary variables to organize info
    lift = create_lift(current_floor, onboard_passengers, direction, passengers_drop_off, drop_off_floors, offboard_passengers, pick_up_floors, pick_up_destinations)
    if not valid_input(lift):
        sys.exit()
    initial_passengers = drop_off_floors[:]
    time = {"total_time":0, "onboard_waiting_time":0, "offboard_waiting_time":0, 'initial_passenger_time': 0}
    flag = True
    #to look nicer:
    print("\n")
    #find next move in given direction
    while flag == True:
        validate_passenger_counts(lift)
        next_move = find_next_move(lift)
        if next_move == None:
            line = f"\n\nFinal state: Lift at floor {lift['current_floor']}. Passengers in lift: {lift['onboard_passengers']}. \n Total wait time for passengers inside the lift: {time['onboard_waiting_time']}. \n Total wait time for passengers waiting to be picked up: {time['offboard_waiting_time']}.\n Total wait time for passengers originally in the lift: {time['initial_passenger_time']}.\n"
            print(line)
            lift["output_record"].append(line)
            flag = False
            if return_record == False:
                sys.exit()
            else:
                return lift["output_record"]
        time_taken, time = update_time(lift, time, next_move, initial_passengers)
        line = f"Moving to floor {next_move} (Time taken {time_taken} second, Total time: {time['total_time']})."
        print(line)
        lift["output_record"].append(line)
        lift = lift_update(lift, next_move)
        initial_passengers = track_initial_passengers(lift, initial_passengers)
    return 0



def get_input():
    # check it has 9 args
    if len(sys.argv) != 9:
        print('Write your input like this, with lists in string format "", e.g. "4, 5, 6" for a list of [4, 5, 6]: python lift_simulation.py <current_floor> <onboard_passengers> <direction> <passengers_drop_off> <drop_off_floors> <offboard_passengers> <pick_up_floors> <pick_up_destinations>')
        sys.exit(1)

    try:
        #turn arguments from terminal into variables for lift
        current_floor = int(sys.argv[1])
        onboard_passengers = int(sys.argv[2])
        direction = int(sys.argv[3])
        passengers_drop_off = int(sys.argv[4])  
        drop_off_floors = list(map(int, re.findall(r'\d+', sys.argv[5])))  # turn string to list
        offboard_passengers = int(sys.argv[6])
        pick_up_floors = list(map(int, re.findall(r'\d+', sys.argv[7])))  
        pick_up_destinations = list(map(int, re.findall(r'\d+', sys.argv[8])))  

        return current_floor, onboard_passengers, direction, passengers_drop_off, drop_off_floors, offboard_passengers, pick_up_floors, pick_up_destinations

    except ValueError:
        # if something went wrong with the values, print an error
        print("Input format may be wrong. Remember to add them as lists")
        sys.exit(1)


if __name__ == "__main__":
    # should stop it executing if it's imported into a test file etc
    current_floor, onboard_passengers, direction, passengers_drop_off, drop_off_floors, offboard_passengers, pick_up_floors, pick_up_destinations = get_input()

    #gives it a place to start
    lift(current_floor, onboard_passengers, direction, passengers_drop_off, drop_off_floors, offboard_passengers, pick_up_floors, pick_up_destinations)


