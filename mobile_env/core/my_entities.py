from typing import Tuple
from shapely.geometry import Point
from mobile_env.core.entities import UserEquipment
import random
import scipy.special as sp
import numpy as np

# my class
class Buffer:
    def __init__(
        self,
        service_type = str, # URRLC, CV, MIOT        
    ):
        self.service_type = service_type
        self.pending_data = 0; # e.g. 4.3 Mbit
        # UE's max. data rate achievable when BS schedules all resources to it
        self.theoretical_maximum_capacity = 0.0 # in Mbps, Based on: bs.bw * log2(1 + snr), Shannon-Hartley Theorem, 
        self.dt = 1.0 # e.g. 1 sec duration between 2 time steps

        self.maximum_bit_rate = 2.0 # e.g 3.5 Mbps
        self.priority = 0.5 # from 0 to 1
        self.service_rate = 0.0;

        self.snr = 0.0
        self.bit_error = 0.0
        self.latency_per_mb = 0.5 # is in msec
        self.latency_history = [];
        self.qoe_history = [];
        #slot duration

        
    def reset(self):
        self.pending_data = 0;
        self.latency_history = [];
        self.qoe_history = [];
        self.theoretical_maximum_capacity = 2.0
        self.maximum_bit_rate = 2.0
        
    def set_theoretical_maximum_capacity(self, capacity):
        self.theoretical_maximum_capacity = capacity
    
    # It is called per time step for each service type
    def generate_traffic(self): 
        if self.service_type == "CV":
            # generate traffic between [3, 4] Mb per each step
            self.pending_data  += random.uniform(3, 5) 
        elif self.service_type == "URLLC":
            # generate traffic between [2, 3] Mb per each step
            self.pending_data += random.uniform(2, 6) 
        elif self.service_type == "MIOT":
            # generate traffic that would be 1 Mb 9/10 times and 20 Mb 1/10 times
            self.pending_data += (1 if random.random() < 0.9 else 20)

    # It is called per time step for each service type
    def send_traffic(self): 

        # Calculate service rate (in Mbits)
        self.service_rate = min(self.dt*self.maximum_bit_rate, self.dt*self.theoretical_maximum_capacity)
        self.pending_data -= self.service_rate

    def calculate_ber(self):
        # Calculate BER
        if self.maximum_bit_rate > self.theoretical_maximum_capacity:
            # Excess rate factor - how much the data rate exceeds the link capacity
            excess_rate_factor = (self.maximum_bit_rate - self.theoretical_maximum_capacity) / self.theoretical_maximum_capacity

            # BER model - as excess rate factor increases, BER increases exponentially
            # Adjust the exponent base (e.g., 10) and exponent factor (e.g., 2) based on specific requirements
            ber = 1 - np.exp(-10 * excess_rate_factor ** 2)

            # Ensure BER is between 0 and 1
            return max(0, min(ber, 1))
        else: # Calculate BER for the case when data rate is within or below the link capacity

            def Q(x):
                return 0.5 * sp.erfc(x / np.sqrt(2))

            modulation = "16-QAM"
            if modulation == "BPSK":
                return Q(np.sqrt(2 * self.snr))
            elif modulation == "QPSK":
                return 0.5 * Q(np.sqrt(2 * self.snr))
            elif modulation == "16-QAM":
                return (3 / 4) * Q(np.sqrt((4 / 5) * self.snr))
            elif modulation == "64-QAM":
                return (7 / 12) * Q(np.sqrt((4 / 21) * self.snr))
            else:
                raise ValueError("Unknown modulation scheme")

        
    def get_latency(self):
        return self.pending_data * self.dt
    
    def get_statistics(self):
        self.latency_history.append(self.get_latency())
        self.qoe_history.append(self.get_qoe())

            
    def apply_action(self, action):
        if(action == 1):
            self.maximum_bit_rate += 0.5
        else:
            self.maximum_bit_rate -= 0.5
       
        if (self.maximum_bit_rate < 0):
            self.maximum_bit_rate = 0
    
    def get_qoe(self):
        # Get the latest latency
        latest_latency = self.get_latency()

        # Define the upper limit for latency to get a minimum QoE (e.g., 100 ms)
        max_latency = 100.0

        # Calculate the QoE based on latency
        # The formula is designed so that QoE is 5 when latency is 0 and linearly decreases to 0 as latency reaches 100
        qoe = 5 * (1 - latest_latency / max_latency)

        # Ensure QoE is within the valid range [0, 5]
        qoe = max(0, min(qoe, 5))

        return qoe



class myUserEquipment(UserEquipment):
    def __init__(self, ue_id: int, service_type: str, velocity: float, snr_tr: float, noise: float, height: float):
        # Initialize properties from the superclass
        super().__init__(ue_id, velocity, snr_tr, noise, height)

        self.service_type = service_type
        self.buffer = Buffer(self.service_type)




