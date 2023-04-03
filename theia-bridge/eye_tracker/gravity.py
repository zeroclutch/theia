import numpy as np

# Set the gravitational constant
G = 6.67430e-11

# Define the masses of the objects
m_node = 1.0  # Mass of the node
m_cursor = 0.001  # Mass of the cursor (assumed to be small)

# Define the initial positions and velocities of the objects
cursor_pos = np.array([0.0, 0.0])  # 2D vector for the cursor position
node_pos = np.array([1.0, 1.0])  # 2D vector for the node position
cursor_vel = np.array([0.0, 0.0])  # 2D vector for the cursor velocity

# Set the time step of the simulation
dt = 1/60

# Initialize the time and frame counters
t = 0.0
frame_count = 0

# Run the simulation until the maximum duration is reached or a stop signal is received
def apply_node_gravity(node_pos, cursor_pos):
    # Calculate the distance and direction between the objects
    r_vector = node_pos - cursor_pos
    r_distance = np.linalg.norm(r_vector)
    r_direction = r_vector / r_distance
    
    # Calculate the gravitational force between the objects
    f_gravity = G * m_node * m_cursor / r_distance**2 * r_direction
    
    # Calculate the acceleration of the cursor
    a_cursor = f_gravity / m_cursor
    
    # Update the velocity and position of the cursor
    cursor_vel += a_cursor * dt
    cursor_pos += cursor_vel * dt

    return cursor_pos

def apply_gravity(nodes, cursor_pos):
    pass
