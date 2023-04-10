import numpy as np

class Gravity:
    # Set the gravitational constant
    G = 3e-3

    # Define the masses of the objects
    m_node = 1.0  # Mass of the node
    m_cursor = 1.0  # Mass of the cursor (assumed to be small)

    # Set the time step of the simulation
    dt = 1/60

    # Initialize the time and frame counters
    t = 0.0
    frame_count = 0

    r_distance_cutoff = 0.25 # Distance cutoff for gravitational model 
    r_min_distance = 0.01 # The distance at which we can assume the points are the same

    nodes = []

    def __init__(self):
        pass

    def get_node_distance(self, node_pos_array, cursor_pos_array):
        # Define the initial positions and velocities of the objects
        cursor_pos = np.array(cursor_pos_array)  # 2D vector for the cursor position
        node_pos = np.array(node_pos_array)  # 2D vector for the node position

        # Calculate the distance and direction between the objects
        r_vector = node_pos - cursor_pos
        r_distance = np.linalg.norm(r_vector)
        r_direction = r_vector / r_distance

        return (float(r_distance), r_direction)

    # Returns a numpy array with the adjusted node position.
    def apply_node_gravity(self, cursor_pos, r_distance, r_direction):

        cursor_vel = np.array([0.0, 0.0])  # 2D vector for the cursor velocity

        # Calculate the gravitational force between the objects
        f_gravity = self.G * self.m_node * self.m_cursor / r_distance**2 * r_direction
        
        # Check if we're "close enough"
        if(r_distance <= self.r_min_distance):
            f_gravity = 0
        
        # Calculate the acceleration of the cursor
        a_cursor = f_gravity / self.m_cursor
            
        # Update the velocity and position of the cursor
        cursor_vel += a_cursor * self.dt
        cursor_pos += cursor_vel * self.dt

        return list(cursor_pos)

    def apply_gravity(self, cursor_pos):
        closest_node = None
        closest_distance = 100000.0
        closest_direction = None

        for node in self.nodes:
            (r_distance, r_direction) = self.get_node_distance([node['x'], node['y']], cursor_pos)
            if (r_distance < self.r_distance_cutoff) and (r_distance < closest_distance):
                # print(f"Distance {r_distance}. Closest node distance: {r_direction}")
                closest_node = node
                closest_distance  = r_distance
                closest_direction = r_direction
        
        if closest_node is not None:
            # print(f"Readjusting cursor from {cursor_pos[0]},{cursor_pos[1]} to {closest_node['x']},{closest_node['y']} ")
            return self.apply_node_gravity(cursor_pos, closest_distance, closest_direction)
        else:
            return cursor_pos

    def set_nodes(self, nodes):
        self.nodes = nodes
