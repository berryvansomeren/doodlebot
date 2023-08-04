from dataclasses import dataclass


"""
These are the datastructures we like working with as a fundamental basis of our workflow.
"""


# ----------------------------------------------------------------
PlotPoint = tuple[ float, float ]
PlotPath = list[ PlotPoint ]
PlotPack = list[ PlotPath ]


# ----------------------------------------------------------------
# These types will be used in host code, where we can freely use modern Python

@dataclass
class MotorInstruction:
    left_speed : int
    right_speed : int
    duration : float

MotorInstructionsPath = list[ MotorInstruction ]
MotorInstructionsPack = list[ MotorInstructionsPath ]


# ----------------------------------------------------------------
# These types will be used for the data that needs to be stored on the Device
# However, note that we do not actually use type annotation in device code!

MotorInstructionTuple = tuple[ int, int, float ]
MotorInstructionTuplePath = list[ MotorInstructionTuple ]
MotorInstructionsTuplePack = list[ MotorInstructionTuplePath ]


# ----------------------------------------------------------------
# This conversion needs to be used when transforming data so that it can be copied to device code

def convert_motor_instructions_pack_to_tuple_based( pack : MotorInstructionsPack ) -> MotorInstructionsTuplePack:
    tuple_pack = []
    for path in pack:
        tuple_path = []
        for instruction in path:
            tuple_instruction = (
                instruction.left_speed,
                instruction.right_speed,
                instruction.duration
            )
            tuple_path.append( tuple_instruction )
        tuple_pack.append( tuple_path )
    return tuple_pack
