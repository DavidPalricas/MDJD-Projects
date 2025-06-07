# Reinforcement Learning Agent to play the Snake Game 
The goal of this project was to develop an agent capable of learning to play a modified version of the Snake game using reinforcement learning. This customized Snake game was designed by Professor Diogo Gomes as part of a project for the Artificial Intelligence and Intelligent Systems I modules at University of Aveiro, where students were tasked with creating agents employing AI search algorithms to play this game effectively.

## Prerequisites
* Python 3.11 (Versions below or above may not work - tested with 3.10 and 3.11)
* Linux system

## How to Run
Follow the steps below to set up and run the project.

### 1. Create a virtual environment in python 3.11 and activate it
```sh
python3.11 -m venv .env && source ./.env/bin/activate
```

### 2. Install dependencies
```sh
pip install -r requirements.txt
```

### 3. Train the agent
#### 3.1 Without a policy
```sh
 # In one terminaL
 python3 server.py

 # In another terminal, where it the says train number_of_epsiodes put a number examples : 20, 100 ,1000, etc.
 python3 student.py train number_of_episodes

 ```
#### 3.2 With a Policy
```sh
 # In one terminaL
 python3 server.py

 # In another terminal, where it the says train number_of_epsiodes put a number examples : 20, 100 ,1000, etc.
 # Note : The policy are stored in the policy directory which is generated after completing a training cycle example of a policy name : dqn_agent_episode_6000
 python3 student.py train number_of_episodes policy_name
 ```

 ### 4. Run the trained agent model
 ```sh
  # In one terminaL
 python3 server.py

# In another terminal
# Note : The policy are stored in the policy directory which is generated after completing a training cycle example of a policy name : dqn_agent_episode_6000
python student.py policy_name
 ``` 

## How to play
If you want to play this game instead of running the agent

```sh
# In one terminal
python3 server.py

# In another terminal
python3 viewer.py

# And in another terminal
python3 client.py
````