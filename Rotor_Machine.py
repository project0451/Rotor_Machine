# rotor_machine.py
# Classes for a fully-assembled virtual rotor machine and major components of such machines
# Includes classes for:
#   RotorBank - a bank of one or more rotors, not including stepping schedule or pre/post-processing layers
#   RotorMachine - base class for a fully-assembled rotor machine, including stepping control and any special features
#   SimpleRotorMachine - class for a full basic rotor machine with simple odometer type stepping and no special features
#   SIGABAMachine - class for a full assembled SIGABA type machine with secondary rotors to control stepping
#   IndexSIGABAMachine - class for a full historical SIGABA machine with index "rotors"
#   EnigmaMachine - class for a full Enigma type machine with a steckerboard and reflector
#   SteppingGenerator - class for a generic stepping control component for a rotor machine

# Base class representing a single fully-assembled virtual rotor machine.
# This class defines the basic functions and structure of a virtual rotor machine

from types import List
import rotor
class RotorMachine:

    def set_cipher_rotors(self, rotors: List[rotor]):
        self.cipher_rotors = RotorBank(rotors)
    
# Class for a SIGABA type virtual rotor machine
# Stepping of the cipher rotors is driven by a second "control" rotor bank
class SIGABAMachine:

    def __init__(self, cipher_rotors: List[rotor], control_rotors: List[rotor], index_map: List[int],
            control_inputs: List[int] = [5,6,7,8], control_step_position: int = 0, control_step_order: List[int] = [2,3,1]):
        self.set_cipher_rotors(cipher_rotors)
        self.set_control_rotors(control_rotors)
        self.set_index_map(index_map)
        self.set_control_inputs(control_inputs)
        self.set_control_step_position(control_step_position)
        self.set_control_step_order(control_step_order)
    
    def set_cipher_rotors(self, rotors: List[rotor]):
        self.cipher_rotors = rotors
        self.num_cipher_rotors = len(rotors)
        self.cipher_rotor_size = rotors[0].get_size()
        if __debug__:
            for r in rotors: assert r.get_size() == self.cipher_rotor_size

    def set_control_rotors(self, rotors: List[rotor]):
        self.control_rotors = rotors
        self.num_control_rotors = len(rotors)
        self.control_rotor_size = rotors[0].get_size()
        if __debug__:
            for r in rotors: assert r.get_size() == self.control_rotor_size

    def set_index_map(self, index_map: List[int]):
        assert len(index_map) == self.control_rotor_size
        self.index_map = index_map
    
    # Sets the inputs to the control rotor bank
    def set_control_inputs(self, control_inputs: List[int]):
        if __debug__:
            for i in control_inputs: assert input[i] not in control_inputs[0,i]
        self.control_inputs = control_inputs
    
    # Step next-slower control rotor when a faster control rotor steps PAST this position
    def set_control_step_position(self, position: int):
        self.control_step_position = position
    
    # Sets odometer stepping order of control rotors, starting with the fastest
    # The first rotor in the list steps after every character encrypted or decrypted
    # Each subsequent rotor steps once per full rotation of the preceding rotor
    # The list does not need to include every rotor; any rotors not listed will not step at all
    def set_control_step_order(self, order: List[int]):
        self.control_step_order = order

    def reset_rotors(self):
        for r in self.cipher_rotors: r.set_position(0)
        for r in self.control_rotors: r.set_position(0)

    def set_rotor_positions(self, cipher_positions: List[int], control_positions: List[int]):
        self.set_cipher_rotor_positions(cipher_positions)
        self.set_control_rotor_positions(control_positions)

    def set_cipher_rotor_positions(self, cipher_positions: List[int]):
        assert len(cipher_positions) == self.num_cipher_rotors
        for i in range(0, self.num_cipher_rotors): cipher_rotors[i].set_position(cipher_positions[i])
#        for r in self.cipher_rotors, i in cipher_positions:
#            r.set_position(i)
    
    def set_control_rotor_positions(self, control_positions: List[int]):
        assert  len(control_positions) == self.num_control_rotors
        for i in range(0, self.num_control_rotors): control_rotors[i].set_position(control_positions[i])
    
    def set_cipher_rotor_position(self, rotor: int, position: int):
        self.cipher_rotors[rotor].set_position(position)
    
    def set_control_rotor_position(self, rotor: int, position: int):
        self.control_rotors[rotor].set_position(position)

    # Pass an input through the cipher rotors.  Does not step the rotors by itself.
    def encipher(self, x: int) -> int:
        for r in cipher_rotors: x = r.encrypt(x)
        return x
    
    # Pass an input backwards through the cipher rotors.  Does not step the rotors by itself.
    def decipher(self, y: int) -> int:
        for i in range(0, self.num_cipher_rotors):
            y = self.cipher_rotors[self.num_rotors - 1 - i].decrypt(y)
        return y
    
    # Pass an input through the control rotors
    def control(self, x: int) -> int:
        for r in self.control_rotors: x = r.encrypt(x)
        return x
    
    # Pass an input through the control rotors backwards
    def control_back(self, x: int) -> int:
        for i in range(0, self.num_control_rotors):
            x = self.control_rotors[self.num_control_rotors -1 - i].decrypt(x)
        return x
    
    # Calculates control rotor outputs and steps the cipher rotors
    def step_cipher_rotors(self):
        stepping = [False for i in range(0, self.num_control_rotors)]
        for c in self.control_inputs:
            z = self.index_map[self.control(c)]
            if z != -1: stepping[z] = True
        for i in range(0, len(stepping)):
            if stepping[i]: self.cipher_rotors[i].step()

    # Steps the control rotors, using odometer type stepping
    def step_control_rotors(self):
        self.control_rotors[self.control_rotor_stepping[0]].step()
        for i in range(1, len(self.control_stepping_order)):
            if (self.control_rotors[i-1].get_position() - 1) % self.control_alphabet_size == self.control_step_position:
                self.control_rotors[i].step()
            else: break

    # Encrypt a single input value and step the rotors
    def encrypt(self, x: int) -> int:
        y = self.encipher(x)
        self.step_cipher_rotors()
        self.step_control_rotors()
        return y
    
    # Decrypt a single input value and step the rotors
    def decrypt(self, y: int) -> int:
        x = self.decipher(y)
        self.step_cipher_rotors()
        self.step_control_rotors()
        return x


# Class for an Enigma type machine with a reflector and a steckerboard
class EnigmaMachine:
    
    def __init__(self, rotors: List[rotor], stepping_positions: List[int] = None, reflector: rotor = None,
        steckerboard: rotor = None):
        self.set_rotors(rotors)
        self.set_reflector(reflector)
        self.set_steckerboard(steckerboard)
        self.set_stepping_positions(stepping_positions)

    def set_rotors(self, rotors: List[rotor]):
        self.rotors = rotors
        self.num_rotors = len(rotors)
        self.rotor_size = rotors[0].get_size()
    
    def set_reflector(self, reflector: rotor):
        self.reflector = reflector
    
    def set_steckerboard(self, steckerboard: rotor):
        if steckerboard == None:
            self.steckerboard = rotor(range(self.rotor_size))
        else:
            self.steckerboard = steckerboard
    
    def set_stepping_positions(self, stepping_positions: List[int]):
        if stepping_positions == None: stepping_positions = [1 for i in range(0, self.num_rotors)]
        self.stepping_positions = stepping_positions
    
    def step_rotors(self):
        self.rotors[0].step(-1)
        for i in range(1, self.rotor_size):
            if (self.rotors[i-1].get_position() + 1) % self.rotor_size == self.stepping_positions[i-1]:
                self.rotors[i].step(-1)
            else:
                break

    def encrypt(self, x: int) -> int:
        y = self.steckerboard.encrypt(x)
        for r in self.rotors: y = r.encrypt(y)
        if self.reflector != None:
            y = self.reflector.encrypt(y)
            for i in range(self.num_rotors -1, -1, -1):
                y = self.rotors[i].decrypt(y)
            y = self.steckerboard.decrypt(y)
        self.step_rotors()
        return y

    def decrypt(self, y: int) -> int:
        if self.reflector != None:
            return self.encrypt(y)
        else:
            for i in range(self.num_rotors -1, -1, -1):
                y = self.rotors[i].decrypt(y)
            x = steckerboard.decrypt(y)
            self.step_rotors()
            return x





# Class for a rotor bank
# Holds a number of rotors in a sequence
# Provides functions for managing the rotors and passing a value through the rotors
class RotorBank:

    # Create a new RotorBank with the specified set of rotors
    def __init__(self, rotors: List[rotor]): self.set_rotors(rotors)

    def set_rotors(self, rotors: List[rotor]):
        self.rotors = rotors
        self.num_rotors = len(rotors)
        self.rotor_size = self.rotors[0].get_size()
        if __debug__:
            for r in self.rotors: assert r.get_size() == self.rotor_size
    
    def reset_positions(self):
        self.set_positions([0 for i in range(0, self.num_rotors)])

    def set_positions(self, positions: List[int]):
        for i in range(0, len(self.rotors)):
            assert 0 <= i <= self.rotor_size
            self.rotors[i].set_position(positions[i])
    
    def set_rotor_position(self, rotor: int, position: int):
        self.rotors[rotor].set_position(position)
    
    def get_positions(self) -> List[int]:
        positions = []
        for i in range(0, self.num_rotors): positions[i] = self.rotors[i].get_position()
        return positions
    
    def get_rotor_position(self, rotor: int) -> int:
        return self.rotors[rotor].get_position()

    def step_rotor(self, rotor: int, steps: int = 1):
        self.rotors[rotor].step(steps)

    def encrypt(self, x: int) -> int:
        for r in self.rotors: x = r.encrypt(x)
        return x
    
    def decrypt(self, y: int) -> int:
        for i in range(self.num_rotors - 1, -1, -1):
            y = self.rotors[i].decrypt(y)
        return y

    def encrypt_with_intermediates(self, x: int) -> List[int]:
        y = list(range(self.num_rotors + 1))
        y[0] = x
        for i in range(0, self.num_rotors):
            y[i+1] = self.rotors[i].encrypt(y[i])
        return y
    
    def decrypt_with_intermediates(self, y: int) -> List[int]:
        x = list(range(self.num_rotors + 1))
        x[0] = y
        for i in range(0, self.num_rotors):
            x[i+1] = self.rotors[self.num_rotors - i].decrypt(x[i])
        return x