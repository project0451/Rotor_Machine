# Class for rotor machine rotor
# Implements an N-symbol monoalphabetic substitution with a shifting modulo N offset before and after
# Uses the SIGABA stepping convention: A,B,C,...,Z + 1 step --> Z,A,B,...,Y
# This is the opposite of the Enigma convention; for Enigma-style stepping, use step(-1)
#
# Wiring pattern for each rotor should be given as a list or tuple containing a permutation of
# the sequence (0,1,2,...,n-1), mapping input i to output w[i]
#
# Methods do not validate rotor input or wiring if compiled with debug flag off, and raise assertion errors otherwise.
# Main program is expected to validate all wiring patters before use, ensure rotor sizes match, and ensure that initial
# inputs to the rotor bank are in the valid range.
# Most rotors receive their encoding/decoding inputs from an adjacent rotor, so all downstream inputs should always be
# valid so long as the initial setup and input to the first rotor are valid.

from typing import List

class rotor:

    # Create a new rotor with specified wiring configuration
    def __init__(self, wiring: List[int]):
        self.set_wiring(wiring)

    def get_size(self) -> int: return self.size
    def get_wiring(self) -> List[int]: return self.wiring
    def get_reverse_wiring(self) -> List[int]: return self.reverse_wiring
    def get_position(self) -> int: return self.position
    
    # Reversed orientation - used only in historical modes, redundant if using full keyspace
    def get_is_reversed(self) -> bool: return self.reversed
#    def set_is_reversed(self, reversed: bool): self.reversed = reversed
    # Flip the rotor over to face backward; if already facing backward, flip it to face forward again.
    def reverse_rotor(self):
        for j in range(self.size):
            wiring[self.size - j] = (self.size -1) - reverse_wiring[j]
        for i in range(self.size):
            reverse_wiring[wiring[i]] = i
        reversed = not(reversed)

    # Treats an out-of-bounds position as a rollover
    def set_position(self, position: int): self.position = position % self.size

    # Set the wiring for the rotor
    # Takes a sequence containing some permutation of 0,1,...,n-1
    # Resets position to 0, since this is a safe value regardless of rotor size, and resets reversed flag
    # Automatically sets size to n and calculates the reverse wiring
    def set_wiring(self, wiring: List[int]):
        self.position = 0
        self.reversed = False
        self.size = len(wiring)
        assert self.size > 0, "Wiring sequence is empty"
        self.wiring = wiring
        self.reverse_wiring = [i for i in range(self.size)]
        for i in range(self.size):
            j = self.wiring[i]
            assert 0 <= j < self.size, "Wiring value outside valid range"
            assert j not in wiring[0,i], "Duplicate wiring value"
            self.reverse_wiring[j] = i

    # Steps the rotor, using the SIGABA sign convention; number of steps may be large or negative
    # Large values roll over modulo n; negative values step the rotor in the other direction (use -1 for Enigma)
    # This is the recommended method to step a rotor during encoding, decoding, or US Navy historical SIGABA setup
    # Otherwise, set_position is typically used for setting inital rotor positions
    def step(self, steps: int = 1): self.position = (self.position + steps) % self.size

    # Passes a value through the rotor
    def encode(self, x: int) -> int:
        assert 0 <= x < self.size, "Rotor input outside valid range"
#        if reversed:
#            y = self.reverse_wiring[self.size - 1 - ((x + self.position) % self.size)]
#            return ((self.size - 1 - y) - self.position) % self.size
        y = self.wiring[(x - self.position) % self.size]
        return (y + self.position) % self.size

    # Passes a value through the rotor from behind; used for decryption in most machines
    def decode(self, y: int) -> int:
        assert 0 <= y < self.size, "Rotor input outside valid range"
#        if reversed:
#            x = self.wiring(self.size - 1 - ((y + self.position) % self.size))
#            return ((self.size - 1 - x) - self.position) % self.size
        x = self.reverse_wiring[(y - self.position) % self.size]
        return (x + self.position) % self.size
