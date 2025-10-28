from enum import Enum
class program_State(Enum):
	IDLE = 0
	GET_BLOCK_COORDS = 1
	PREP_GLUE_1 = 2
	PREP_GLUE_2 = 3
	GET_MIRROR_COORDS = 4
	ERROR = 5

