from schindler import lift


def parse_record(record):
    events = []

    for line in record:
        line = line.strip()

        # Movement --------------------------------------
        if line.startswith("Moving to floor"):
            parts = line.split()
            floor = int(parts[3])
            events.append(("MOVE", floor))

        # Pickup -----------------------------------------
        elif line.startswith("Picking up"):
            # Example: "Picking up 1 passenger(s) on floor 1"
            parts = line.split()
            count = int(parts[2])  # "1"
            floor = int(parts[-1])  # "1"
            events.append(("PICKUP", floor, count))

        # Dropoff ----------------------------------------
        elif line.startswith("Dropping off"):
            # Example: "Dropping off 1 passenger(s) on floor 2."
            parts = line.split()
            count = int(parts[2])
            # last part is "2." → strip the dot
            floor = int(parts[-1].rstrip("."))
            events.append(("DROPOFF", floor, count))

        # Final state -------------------------------------
        elif line.startswith("Final state"):
            events.append(("FINISHED", None))

    return events


def main():
    record = lift(
        current_floor=0,
        onboard_passengers=1,
        direction=1,
        passengers_drop_off=1,
        drop_off_floors=[2],
        offboard_passengers=1,
        pick_up_floors=[1],
        pick_up_destinations=[3],
        return_record=True
    )

    print("=== FRONTEND RECEIVED RECORD ===")
    for line in record:
        print(line)
    
    parsed = parse_record(record)
    print("=== PARSED EVENTS ===")
    for e in parsed:
        print(e)

if __name__ == "__main__":
    main()

