# elevator_frontend.py

import tkinter as tk
import os
from schindler import lift
from elevator_parser import parse_record

# Load passenger icon
PERSON_IMG = None

# Floor coordinate mapping
FLOOR_Y = {3: 50, 2: 150, 1: 250, 0: 350}

LIFT_WIDTH = 80
LIFT_HEIGHT = 60

PASSENGER_SIZE = 30   # size of the PNG icon


from PIL import Image, ImageTk

def load_images(canvas):
    global PERSON_IMG

    # Load original PNG
    img = Image.open("person.png")

    # Resize it to something reasonable (e.g., 24×48)
    img = img.resize((24, 48), Image.LANCZOS)

    PERSON_IMG = ImageTk.PhotoImage(img)

    # Keep reference so Tkinter doesn't garbage collect it
    canvas.person_img = PERSON_IMG


def draw_static_building(canvas):
    for y in FLOOR_Y.values():
        canvas.create_line(50, y + LIFT_HEIGHT, 250, y + LIFT_HEIGHT, width=3)
    canvas.create_rectangle(100, 20, 200, 420, outline="black", width=3)


def draw_lift(canvas, floor):
    y = FLOOR_Y[floor]
    return canvas.create_rectangle(
        110, y,
        110 + LIFT_WIDTH, y + LIFT_HEIGHT,
        fill="lightgreen"
    )


def draw_waiting_passengers(canvas, events):
    """Creates icons for each floor that will later be picked up."""
    waiting = {0: [], 1: [], 2: [], 3: []}

    for ev in events:
        if ev[0] == "PICKUP":
            _, floor, count = ev

            # Start from however many are already drawn for this floor
            start_index = len(waiting[floor])

            for i in range(count):
                idx = start_index + i
                x = 260 - idx * 35      # queue horizontally toward the shaft
                y = FLOOR_Y[floor] + 15
                icon = canvas.create_image(x, y, image=PERSON_IMG)
                waiting[floor].append(icon)

    return waiting



def lift_passenger_slots(floor_y, num):
    """Return horizontal x positions for N passengers inside lift (max 5)."""
    base_x = 110 + 10
    spacing = (LIFT_WIDTH - 20) // max(1, num)
    xs = [base_x + i * spacing for i in range(num)]
    y = floor_y + LIFT_HEIGHT // 2
    return [(x, y) for x in xs]


def animate_move(canvas, lift_car, start_floor, end_floor, lift_passengers, callback):
    start_y = FLOOR_Y[start_floor]
    end_y = FLOOR_Y[end_floor]

    total_steps = 30
    dy = (end_y - start_y) / total_steps
    step = 0

    def tick():
        nonlocal step
        if step < total_steps:
            # Move the elevator car
            canvas.move(lift_car, 0, dy)

            # Move passengers IN the elevator
            for icon in lift_passengers:
                canvas.move(icon, 0, dy)

            step += 1
            canvas.after(20, tick)
        else:
            # Snap into final position
            canvas.coords(lift_car, 110, end_y, 190, end_y + LIFT_HEIGHT)

            # Snap passengers to correct y positions too
            coords = canvas.coords(lift_car)
            fy = coords[1]  # top y of lift
            y_center = fy + LIFT_HEIGHT // 2

            for icon in lift_passengers:
                x, _ = canvas.coords(icon)
                canvas.coords(icon, x, y_center)

            callback()

    tick()



def animate_icon(canvas, icon, x_target, y_target, callback=None):
    """Generic smooth mover for PNG passengers."""
    x0, y0 = canvas.coords(icon)
    steps = 20
    dx = (x_target - x0) / steps
    dy = (y_target - y0) / steps
    step = 0

    def tick():
        nonlocal step
        if step < steps:
            canvas.move(icon, dx, dy)
            step += 1
            canvas.after(15, tick)
        else:
            canvas.coords(icon, x_target, y_target)
            if callback:
                callback()

    tick()


def run_events(canvas, lift_car, events, waiting_passengers, lift_passengers, idx=0):
    if idx >= len(events):
        return

    ev = events[idx]
    etype = ev[0]

    # ---- MOVE EVENT ----
    if etype == "MOVE":
        target_floor = ev[1]

        # detect current floor by lift Y
        y_current = canvas.coords(lift_car)[1]
        current_floor = min(FLOOR_Y.keys(), key=lambda f: abs(FLOOR_Y[f] - y_current))

        animate_move(
            canvas,
            lift_car,
            current_floor,
            target_floor,
            lift_passengers,
            callback=lambda: run_events(canvas, lift_car, events, waiting_passengers, lift_passengers, idx+1)
        )

        return

    # ---- PICKUP EVENT ----
    if etype == "PICKUP":
        floor, count = ev[1], ev[2]

        def continue_after_pickups():
            run_events(canvas, lift_car, events, waiting_passengers, lift_passengers, idx+1)

        if count == 0:
            continue_after_pickups()
            return

        # Animate each pickup sequentially
        def animate_one_pickup(n_remaining):
            if n_remaining == 0:
                canvas.after(200, continue_after_pickups)
                return

            if waiting_passengers[floor]:
                icon = waiting_passengers[floor].pop(0)

                lift_coords = canvas.coords(lift_car)
                lift_y = lift_coords[1]

                target_positions = lift_passenger_slots(lift_y, len(lift_passengers) + 1)
                x_target, y_target = target_positions[-1]

                def after_move():
                    lift_passengers.append(icon)
                    animate_one_pickup(n_remaining - 1)

                animate_icon(canvas, icon, x_target, y_target, callback=after_move)
            else:
                animate_one_pickup(n_remaining - 1)

        animate_one_pickup(count)
        return


    # ---- DROPOFF EVENT ----
    if etype == "DROPOFF":
        floor, count = ev[1], ev[2]

        for _ in range(count):
            if lift_passengers:
                icon = lift_passengers.pop()

                x_exit = 250
                y_exit = FLOOR_Y[floor] + 15

                animate_icon(canvas, icon, x_exit, y_exit, callback=lambda: canvas.delete(icon))

        canvas.after(300, lambda: run_events(canvas, lift_car, events, waiting_passengers, lift_passengers, idx+1))
        return

    # ---- FINISHED ----
    if etype == "FINISHED":
        print("Simulation finished.")
        canvas.after(500, canvas.winfo_toplevel().destroy)
        return



def main():
    record = lift(
            current_floor=0,
            onboard_passengers=1,
            direction=1,
            passengers_drop_off=1,
            drop_off_floors=[3],          # initial onboard passenger goes to floor 3
            offboard_passengers=3,        # three people waiting
            pick_up_floors=[1, 1, 2],     # two wait at floor 1, one at floor 2
            pick_up_destinations=[3, 0, 1],  # their destinations
            return_record=True
        )


    events = parse_record(record)

    root = tk.Tk()
    root.title("Elevator Simulation")

    canvas = tk.Canvas(root, width=300, height=450, bg="lightgrey")
    canvas.pack()

    load_images(canvas)
    draw_static_building(canvas)

    lift_car = draw_lift(canvas, 0)

    waiting = draw_waiting_passengers(canvas, events)
    passengers = []

    run_events(canvas, lift_car, events, waiting, passengers)

    root.mainloop()


if __name__ == "__main__":
    main()
