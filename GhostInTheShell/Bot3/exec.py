from GhostInTheShell.Bot3.field import *
from GhostInTheShell.Bot3.turn import *

field = Field(int(input()))
for _ in range(int(input())):
    field.connect(*[int(j) for j in input().split()])
field.end_init()

# game loop
while True:
    entity_count = int(input())  # the number of entities (e.g. factories and troops)
    field.start_turn()

    for _ in range(entity_count):
        entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5 = input().split()
        entity_id = int(entity_id)
        arg_1 = int(arg_1)
        arg_2 = int(arg_2)
        arg_3 = int(arg_3)
        arg_4 = int(arg_4)
        arg_5 = int(arg_5)
        if entity_type == FACTORY_ENTITY:
            field.update_factory(entity_id, arg_1, arg_2, arg_3, arg_4)
        elif entity_type == TROOP_ENTITY:
            field.update_troop(arg_1, arg_3, arg_4, arg_5)
        elif entity_type == BOMB_ENTITY:
            field.update_bomb(arg_1, arg_3, arg_4)

    field.end_input()
    # print(field.choose_move())
    print(Wait())
