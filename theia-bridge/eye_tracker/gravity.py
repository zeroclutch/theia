import numpy as np

class Gravity:
    # Set the gravitational constant
    G = 6.67430e-11

    # Define the masses of the objects
    m_node = 1.0  # Mass of the node
    m_cursor = 0.001  # Mass of the cursor (assumed to be small)

    # Set the time step of the simulation
    dt = 1/60

    # Initialize the time and frame counters
    t = 0.0
    frame_count = 0

    r_distance_cutoff = 0.05

    nodes = []

    def __init__(self):
        pass

    # Returns a numpy array with the adjusted node position.
    def apply_node_gravity(self, node_pos_array, cursor_pos_array):
        # Define the initial positions and velocities of the objects
        cursor_pos = np.array(cursor_pos_array)  # 2D vector for the cursor position
        node_pos = np.array(node_pos_array)  # 2D vector for the node position
        cursor_vel = np.array([0.0, 0.0])  # 2D vector for the cursor velocity

        # Calculate the distance and direction between the objects
        r_vector = node_pos - cursor_pos
        r_distance = np.linalg.norm(r_vector)
        r_direction = r_vector / r_distance

        if(r_distance > self.r_distance_cutoff):
            return cursor_pos_array
        
        # Calculate the gravitational force between the objects
        f_gravity = self.G * self.m_node * self.m_cursor / r_distance**2 * r_direction
        
        # Calculate the acceleration of the cursor
        a_cursor = f_gravity / self.m_cursor
            
        # Update the velocity and position of the cursor
        cursor_vel += a_cursor * self.dt
        cursor_pos += cursor_vel * self.dt

        return cursor_pos

    def apply_gravity(self, nodes, cursor_pos):
        for node in nodes:
            print(node)

    def set_nodes(self, nodes):
        self.nodes = nodes
