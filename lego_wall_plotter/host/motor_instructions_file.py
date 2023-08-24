import logging

from lego_wall_plotter.host.base_types import MotorInstructionsPack

def write_motor_instructions_file( instructions_pack : MotorInstructionsPack, path : str ) -> None:
    logging.info( "=" * 64 )

    with open( path, 'w' ) as instructions_file :

        # first write the number of paths, which makes reading easier
        n_paths = len(instructions_pack)
        instructions_file.write( f'{n_paths}\n' )

        for path in instructions_pack:
            for instruction in path:
                instructions_file.write( f'{instruction.target_degrees_left},{instruction.target_degrees_right}\n' )
            instructions_file.write( '\n' ) # empty line to signal the end of the file

    logging.info( f"Wrote motor instructions to file '{path}'" )