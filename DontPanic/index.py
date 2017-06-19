# https://www.codingame.com/ide/puzzle/don't-panic

# nb_rounds: maximum number of rounds
# exit_floor: floor on which the exit is found
# exit_pos: position of the exit on its floor
# nb_total_clones: number of generated clones
# nb_additional_elevators: ignore (always zero)
# nb_elevators: number of elevators

nb_floors, width, nb_rounds, exit_floor, exit_pos, nb_total_clones, nb_additional_elevators, nb_elevators = [int(i) for i in input().split()]
elevators = {exit_floor: exit_pos}
for i in range(nb_elevators):
    # elevator_floor: floor on which this elevator is found
    # elevator_pos: position of the elevator on its floor
    elevator_floor, elevator_pos = [int(j) for j in input().split()]
    elevators[elevator_floor] = elevator_pos

# print(elevators, exit_floor, exit_pos, file=sys.stderr)

# game loop
while True:
    # clone_floor: floor of the leading clone
    # clone_pos: position of the leading clone on its floor
    # direction: direction of the leading clone: LEFT or RIGHT
    clone_floor, clone_pos, direction = input().split()
    clone_floor = int(clone_floor)
    clone_pos = int(clone_pos)

    target = elevators.get(clone_floor)
    if target is None:
        print("WAIT")
    elif target == clone_pos:
        print("WAIT")
    elif (target < clone_pos and direction == 'RIGHT') or (target > clone_pos and direction == 'LEFT'):
        print("BLOCK")
    else:
        print("WAIT")