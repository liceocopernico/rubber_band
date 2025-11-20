#a very naive circular buffer to store wave time series

import numpy as np


class timeCirBuffer:
    def __init__(self, object: object, maxlen: int):
        
        self.max_length: int = maxlen
        self.queue_tail: int = maxlen - 1
        o_len = len(object)
        if (o_len == maxlen):
            self.rec_queue = np.array(object, dtype=np.float64)
        elif (o_len > maxlen):
            self.rec_queue = np.array(object[o_len-maxlen:], dtype=np.float64)
        else:
            self.rec_queue = np.append(np.array(object, dtype=np.float64), np.zeros(maxlen-o_len, dtype=np.float64))
            self.queue_tail = o_len - 1

    def to_array(self) -> np.array:
        head = (self.queue_tail + 1) % self.max_length
        return np.roll(self.rec_queue, -head) 
    def enqueue(self, new_data: np.float64) -> None:
        
        self.queue_tail = (self.queue_tail + 1) % self.max_length        
        self.rec_queue[self.queue_tail] = new_data

    def peek(self) -> np.float64:
        queue_head = (self.queue_tail + 1) % self.max_length
        return self.rec_queue[queue_head]

    def replace_item_at(self, index: int, new_value: np.float64):
        loc = (self.queue_tail + 1 + index) % self.max_length
        self.rec_queue[loc] = new_value

    def item_at(self, index: int) -> np.float64:
        
        loc = (self.queue_tail + 1 + index) % self.max_length
        return self.rec_queue[loc]

    def __repr__(self):
        return "tail: " + str(self.queue_tail) + "\narray: " + str(self.rec_queue)

    def __str__(self):
        return "tail: " + str(self.queue_tail) + "\narray: " + str(self.rec_queue)
        