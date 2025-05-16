import random
import pickle
import os
from collections import defaultdict

# Define the Q-table file path
Q_TABLE_FILE = "q_table.pkl"

# Define states and actions
CPU_STATES = ['low', 'medium', 'high']
MEMORY_STATES = ['low', 'medium', 'high']
ACTIONS = ['schedule_task', 'skip_task']

# Learning parameters
ALPHA = 0.1       # learning rate
GAMMA = 0.9       # discount factor
EPSILON = 0.1     # exploration rate

# Helper to get default Q-values
def default_action_values():
    return {action: 0.0 for action in ACTIONS}

# Load or initialize Q-table safely
Q_TABLE = defaultdict(default_action_values)

if os.path.exists(Q_TABLE_FILE):
    try:
        with open(Q_TABLE_FILE, "rb") as f:
            loaded_q = pickle.load(f)
            Q_TABLE.update(loaded_q)
            print("[Info] Q-table loaded successfully.")
            print(f"Loaded Q-table: {dict(Q_TABLE)}")  # Log the Q-table contents
    except (EOFError, pickle.UnpicklingError):
        print("[Warning] Q-table file was empty or corrupted. Starting fresh...")


# Simulate current system state (replace with actual logic if needed)
# Add disk usage state
DISK_STATES = ['low', 'medium', 'high']

# Modify get_current_state to include disk usage
def get_current_state():
    cpu_usage = random.randint(0, 100)
    memory_usage = random.randint(0, 100)
    disk_usage = random.randint(0, 100)  # Simulate disk usage

    cpu_state = 'low' if cpu_usage < 40 else 'medium' if cpu_usage < 75 else 'high'
    mem_state = 'low' if memory_usage < 40 else 'medium' if memory_usage < 75 else 'high'
    disk_state = 'low' if disk_usage < 40 else 'medium' if disk_usage < 75 else 'high'

    return (cpu_state, mem_state, disk_state)


# Simulate reward logic
# Add new action: prioritize_task
ACTIONS = ['schedule_task', 'skip_task', 'prioritize_task']

# Update reward logic to handle prioritization
def get_reward(state, action):
    cpu, mem, disk = state  # Include disk state in the reward function
    # Penalty/Reward for scheduling tasks based on system state
    if action == 'schedule_task':
        if cpu == 'low' and mem == 'low' and disk == 'low':
            return 5  # Ideal condition for scheduling
        elif cpu == 'medium' or mem == 'medium' or disk == 'medium':
            return 2  # Marginal condition
        else:
            return -5  # High load penalty
    elif action == 'skip_task':
        if cpu == 'high' or mem == 'high' or disk == 'high':
            return 4  # Reward for skipping when under high load
        else:
            return -2  # Slight penalty for skipping during normal load
    elif action == 'prioritize_task':
        if cpu == 'low' and mem == 'low' and disk == 'low':
            return 6  # High reward for prioritizing under low load
        elif cpu == 'medium' or mem == 'medium' or disk == 'medium':
            return 3  # Medium reward for prioritizing in marginal conditions
        else:
            return -1  # Small penalty for prioritizing under high load

    return 0


# Choose action using epsilon-greedy strategy
def choose_action(state):
    if random.random() < EPSILON:
        return random.choice(ACTIONS)
    else:
        state_actions = Q_TABLE[state]
        return max(state_actions, key=state_actions.get)

# Perform one step of training and return result
def rl_scheduler_step():
    state = get_current_state()
    action = choose_action(state)
    reward = get_reward(state, action)

    next_state = get_current_state()
    next_max = max(Q_TABLE[next_state].values())

    # Q-learning update
    old_value = Q_TABLE[state][action]
    Q_TABLE[state][action] = old_value + ALPHA * (reward + GAMMA * next_max - old_value)

    # Save Q-table
    with open(Q_TABLE_FILE, "wb") as f:
        pickle.dump(dict(Q_TABLE), f)

    return {
        'state': state,
        'action': action,
        'reward': reward,
        'updated_q_value': Q_TABLE[state][action]
    }

# Run RL loop (for testing)
if __name__ == "__main__":
    for _ in range(10):  # Run 10 iterations
        result = rl_scheduler_step()
        print(f"State: {result['state']}, Action: {result['action']}, "
              f"Reward: {result['reward']}, Q: {result['updated_q_value']:.2f}")
