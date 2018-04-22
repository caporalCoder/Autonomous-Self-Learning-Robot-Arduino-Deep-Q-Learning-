import random
from collections import deque
from pathlib import Path
import math

import keras
import serial
import time

from keras import Sequential
from keras.layers import Dense
import numpy as np
from keras.models import model_from_json
from keras.optimizers import Adam

print("Start")
port = "/dev/tty.HC-05-DevB"  # This will be different for various devices and on windows it will probably be a COM port.
bluetooth = serial.Serial(port, 9600)  # Start communications with the bluetooth unit
print("Connected")

MAX_RANGE = 4000.0


# Deep Q-learning Agent
class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # discount rate
        self.epsilon = 0.2939294464899635  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.99995
        self.learning_rate = 0.001
        if Path("model.json").is_file():
            self.model = self.load()
        else:
            self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(4, input_dim=self.state_size, activation='relu'))
        model.add(Dense(8, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        print("Epsilon = {}".format(self.epsilon))
        if np.random.rand() <= self.epsilon:
            return np.random.randint(0, 3)

        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * \
                         np.amax(self.model.predict(next_state)[0])

            # print("Replay ", state)
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
            self.save()
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save(self):
        # serialize model to JSON
        model_json = self.model.to_json()
        with open("model.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights("model.h5")

    def load(self):
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights("model.h5")
        loaded_model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        return loaded_model


def computeReward(state, action, input_data):
    if state[action] <= 25.0 / MAX_RANGE:
        return -500

    if math.sqrt(math.pow(state[0] - input_data[0], 2) + math.pow(state[1] - input_data[1], 2) + math.pow(
            state[2] - input_data[2], 2)) <= 20.0 / MAX_RANGE:
        return -200

    if action != 1 and state[1] == max(state):
        return -200

    if action == 1 and state[1] == max(state):
        return 500

    if state[action] == min(state):
        return -50

    return 10


if __name__ == "__main__":
    # initialize gym environment and the agent

    bluetooth.flushInput()  # This gives the bluetooth a little kick

    state_size = 3  # (signaux envoyes par 3 capteurs)
    action_size = 3
    agent = DQNAgent(state_size, action_size)
    episodes = 10000

    ACTION_NAME = ["L", "F", "R"]

    state = bluetooth.readline()

    # print(state)
    # Parse la state
    state = str(state.decode()).replace("\r\n", "")

    state = state.split(",")

    state = [int(a) / MAX_RANGE for a in state]

    st = state
    # Iterate the game
    for e in range(episodes):
        total_reward = 0.0

        cpt = 0

        while True:

            # Decide action

            state = np.array(state).reshape(1, 3)
            action = agent.act(state)

            # print(ACTION_NAME[action])

            # Advance the game to the next frame based on the action.
            bluetooth.write(
                b"" + str.encode(str(ACTION_NAME[action])))  # These need to be bytes not unicode, plus a number

            time.sleep(0.5)  # A pause between bursts

            # Reward i
            input_data = bluetooth.readline().decode().replace("\r", "").replace("\n", "").split(",")
            input_data = [int(a) / MAX_RANGE for a in input_data]

            reward = computeReward(st, action, input_data)

            st = input_data

            next_state = np.array(input_data).reshape(1, 3)
            print("action :: {}  --- next state :: {}   ---- reward :: {}".format(action, next_state, reward))

            fail = 0

            state = next_state

            if reward > 0:  # Tant qu'on est a plus de 5cm d'un obstacle
                cpt += 1

            else:
                fail = 1

            # Remember the previous state, action, reward, and done
            agent.remember(state, action, reward, next_state, fail)

            # ex) The agent drops the pole
            if fail:
                # print the score and break out of the loop
                print("episode: {}/{}, score: {}".format(e, episodes, cpt))
                break

        # train the agent with the experience of the episode
        agent.replay(cpt)

        # bluetooth.write(b"" + str.encode(str("A")))

        f = open("reward.txt", "a+")

        if (cpt != 0):
            f.write(str(cpt) + "\n")
