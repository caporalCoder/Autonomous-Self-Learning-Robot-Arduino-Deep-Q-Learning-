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

MAX_RANGE = 4000.0


# Deep Q-learning Agent
class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # discount rate
        self.epsilon = 0.95  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
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
    print(state[action])
    if state[action] <= 100.0 / MAX_RANGE:
        return -500

    if action != 0 and state[0] == max(state):
        return 10

    if action == 0 and state[0] == max(state):
        return 500

    return 10


if __name__ == "__main__":

    import numpy as np
    import matplotlib.pyplot as plt

    # initialize environment and the agent
    from Car import Car
    from frame import frame

    # Instances
    cadre = frame([0, 0], math.pi / 120, 4, 4)
    obj1 = frame([-1.5, 0.9], math.pi / 3, 0.5, 0.3)
    obj2 = frame([0.25, -1.0], math.pi / 15, 0.5, 0.5)
    obj3 = frame([1.0, 1.1], math.pi / 4, 0.4, 0.4)
    voiture = Car(lag=0.15, ang=50)

    # Demarrer
    voiture.speed = 2.0
    remain_delay = 0.0

    state_size = 3  # (signaux envoyes par 3 capteurs)
    action_size = 3  # (Avancer:0, Gauche:1, Droite:2)

    agent = DQNAgent(state_size, action_size)
    episodes = 10000

    ACTION_NAME = [1, 0, 2]

    [lecture, points] = voiture.read([cadre, obj1, obj2, obj3])

    state = np.array(lecture) * 0.25
    state = state.reshape(1, 3)

    # Iterate the game
    for e in range(episodes):
        total_reward = 0.0

        cpt = 0

        while True:

            # Decide action

            print(state)
            action = agent.act(state)

            # Advance the game to the next frame based on the action.
            voiture.move(action, 0.05)

            # Afficher
            plt.axis([-3, 3, -3, 3])
            plt.clf()
            plt.ion()
            cadre.show()
            obj1.show()
            obj2.show()
            obj3.show()
            voiture.show()
            plt.axes().set_aspect('equal', 'datalim')
            plt.text(0, -2.75, 'Temps: ' + str(round(0, 1)))


            #  Calculate Reward i

            [lecture, points] = voiture.read([cadre, obj1, obj2, obj3])

            input_data = np.array(lecture) * 0.25  # Normaliser

            reward = computeReward(state.reshape(3, 1), action, input_data)
            input_data = input_data.reshape(1, 3)

            state = input_data

            next_state = input_data
            print("action :: {}  --- next state :: {}   ---- reward :: {}".format(action, next_state, reward))

            fail = 0

            if reward > 0:  # Tant qu'on est a plus de 5cm d'un obstacle
                cpt += 1
            else:
                fail = 1

            # Remember the previous state, action, reward, and done
            agent.remember(state, action, reward, next_state, fail)

            state = next_state

            if cpt % 100:
                agent.replay(min(cpt, 100))

            # ex) The agent drops the pole
            if fail:
                # print the score and break out of the loop
                print("episode: {}/{}, score: {}".format(e, episodes, cpt))
                voiture = Car(lag=0.15, ang=50)
                voiture.speed = 5.0
                break

        f = open("reward.txt", "a+")

        if (cpt != 0):
            f.write(str(cpt) + "\n")
