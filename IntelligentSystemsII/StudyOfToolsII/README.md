# Tensor Flow Agents - Research and Demo
TensorFlow Agents (TF-Agents) is an open-source library built on top of TensorFlow, designed to simplify the process of creating, training, and deploying RL agents. It offers a comprehensive set of modular components, including pre-built algorithms, environments, and utilities that facilitate the implementation of both standard and custom reinforcement learning models.

As part of this project, we explored the core concepts of TF-Agents, its architecture, and its application in building reinforcement learning agents. The repository includes a presentation of our findings and a demonstration showcasing the "Cart Pole" environment. In this classic reinforcement learning task, an agent is trained to balance a pole on a moving cart by applying forces to the cart. The demo illustrates the step-by-step implementation of the agent, from setting up the environment to training and evaluating its performance.

## Prerequisites
* Python 3.11 (Versions below or above may not work - tested with 3.10 and 3.11)

## How to Run
### 1. Create a virtual environment in python 3.11 and activate it
```bash
python3.11 -m venv .env && source ./.env/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt 
```

### 3. Execute the Program
First train the agent with the following command.
```bash
python3 demo.py train
```

After training, you can see the results of the training with the following command.
```bash
python3 demo.py
```

To see the training metrics:
```bash
tensorboard --logdir=./logs
```
