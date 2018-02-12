from unittest import TestCase
import random

import pearldiver
from iota import Hash, TryteString, crypto

ALPHABETS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ9'
HASH_LENGTH = 243


class PearlDiverTest(TestCase):
    TRYTE_LENGTH = 2673
    MIN_WEIGHT_MAGNITUDE = 10
    NUM_CORES = -1

    def setUp(self):
        self.pearldiver = pearldiver.PearlDiver()
        self.hash_trits = [0] * HASH_LENGTH

    def test_random_tryte_hash(self):
        trytes = self.get_random_trytes()
        print("Trytes: {}".format(trytes))
        hash = self.get_hash_for(trytes)
        print("Hash: {}".format(hash))
        self.assertTrue(
            self.is_all_nines(
                hash[HASH_LENGTH // 3 - self.MIN_WEIGHT_MAGNITUDE // 3:]))

    def get_hash_for(self, trytes):
        curl = crypto.pycurl.Curl()
        # curl = crypto.Curl()
        trits = trytes.as_trits()
        self.pearldiver.search(trits,
                               self.MIN_WEIGHT_MAGNITUDE, self.NUM_CORES)

        curl.absorb(trits)
        curl.squeeze(self.hash_trits)
        curl.reset()

        return Hash.from_trits(self.hash_trits)

    def get_random_trytes(self):
        return TryteString(''.join(
            [random.choice(ALPHABETS) for _ in range(self.TRYTE_LENGTH)]))

    @staticmethod
    def is_all_nines(hash):
        return set(hash) == {b'9'}
