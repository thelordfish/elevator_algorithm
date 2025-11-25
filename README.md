# Elevator Scheduling Algorithm

This project implements and explains a simple elevator-scheduling algorithm for a 4-floor lift system (0–3). The goal is to reduce:

1. passenger travel time  
2. passenger wait time  
3. unnecessary lift movement  

[tkinter frontend animation added after submission:]
<!-- RIGHT-FLOATING IMAGE -->
<div style="float:right; margin-left:20px; margin-bottom:10px;">
  <img src="https://github.com/user-attachments/assets/cdf5cc70-a37d-412a-91dd-d1040ebb7217" width="260">
</div>

The solution uses a **direction-based greedy algorithm**: the lift continues moving in its current direction until no requests remain, only reversing when necessary. It prioritises:

- nearest drop-offs  
- pick-ups that lie “on the way” to a drop-off, if capacity allows  
- minimal backtracking and minimal direction changes  

This mirrors how real lifts behave and avoids inefficient detours.

The full pseudocode is available in `Pseudocode.docx`.  
The implementation is in `schindler.py`.

An optional `frontend.py` is added with it's `elevator_parser.py` post-submission, to visualize the output of the algorithm and make the whole thing slightly less boring:

---

## Files in This Repository

### `schindler.py`

Python implementation of the scheduling logic, including:
- input validation  
- selecting the next floor to move to (drop-off or pick-up)  
- picking up passengers en-route when possible  
- processing drop-offs and pick-ups  
- tracking movement time and waiting times  
- terminating the loop when all requests are handled

  
### 'Pseudocode.docx'

Pseudocode of the above.

### `elevator_parser.py`
Parses the textual log produced by `schindler.py` into structured events.  
Extracts:
- movement events (`MOVE`)  
- pickups (`PICKUP`)  
- drop-offs (`DROPOFF`)  
- simulation termination (`FINISHED`)  

Used as the clean interface between backend logic and the animation frontend.

### `elevator_frontend.py`
Tkinter visual simulation of the lift.  
Responsible for:
- drawing the building and lift shaft  
- rendering waiting passengers and arranging them in queues  
- animating elevator movement smoothly between floors  
- animating pickups into the lift and drop-offs out of it  
- stepping through parsed events to replay the entire scenario

### `person.png`
Used for the people in the lift.
- ---


## Tasks from Coursework

### `Task 1 - Pseudocode`

Found in Pseudocode.docx

---

### `Task 2 - greedy algorithm'`

Task2: Explain how your algorithm optimizes passenger travel time, wait time, and energy efficiency. [15 marks]

My algorithm optimizes wait time, travel time, and energy efficiency with a direction-based greedy scheduling approach. While it beelines for the next drop-off in its direction, its inefficient to not pick up passengers en-route if space allows. Function pick_up_on_way reduces wait times for passengers between lift and its drop-off. By focusing on closest viable floors, many inefficient detours are avoided. The direction-based approach prevents unnecessary direction changes, ensuring the lift only reverses when no requests remain in the current direction, reducing energy-wasting backtracking and mirroring real-life lift behaviour.  
88 words

---

### `Task 3 - Time Complexity, big-O notation`

• Task3: Discuss the time complexity in the worst-case scenario.3 [25 marks]

Using algorithms from the RAM model of computation, such as:  
 T(n)=cop×C(n)  
(where cop is the cost of executing a basic function, equal to 1 in the hypothetical Random-Access Machine and C(n) is the number of operations relative to n the input size) the time-complexity of my direction-based greedy algorithm can be quantified for the worst-case scenario.

The two dominant algorithms, that contribute most to the scaling of the overhead as n approaches the worst-case, are:

- the main loop – which is roughly proportional to the size of n i.e. the size of the input lift requests and drop offs. Let it be n.  
- the major operations within the main loop: find_next_move(lift) and lift_update(lift, next_move). Let these be m.

In big-O notation constants are ignored, so rather than combining these operations to make 2m, as they become negligible as we scale up to the worst case scenario, we can leave the equation at O(n*m).

This is linear, as m is limited by the number of floors to iterate through, and so should handle large inputs better than exhaustive search algorithms that might, for instance, simulate all possible routes traversing the nodes of a tree-like structure, and then select the one with the best results.

While such algorithms may return better answers for some edge cases than mine as they can look ahead, their overhead may increase exponentially in the worst case scenario, for instance O(bd), where b is the branching factor (possible lift moves at any point), and d is the depth (number of decision-making levels of the tree to explore).

---

## How to Run the Simulation

Run frontend by simply running frontend.py, it has an example set of inputs already, which can be edited in the script.

OR

Run backend (schindler.py) via command line:

```bash
python schindler.py <current_floor> <onboard_passengers> <direction> "<drop_off_floors>" <offboard_passengers> "<pick_up_floors>" "<pick_up_destinations>"



