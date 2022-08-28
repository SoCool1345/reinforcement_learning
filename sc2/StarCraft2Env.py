#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pickle
import time

import cv2
import gym
import numpy
import subprocess
from stable_baselines3.common.env_checker import check_env


# In[2]:


import numpy as np


class StarCraft2Env(gym.Env):


    def __init__(self,rank):
        super(StarCraft2Env,self).__init__()
        self.observation_space = gym.spaces.Box(low=0,high=255,shape=(224,224,3),dtype=np.uint8)

        self.action_space = gym.spaces.Discrete(7)
        self.rank = rank
        self.transaction_file = f'transaction{self.rank}.pkl'

    def render(self, mode="human"):
        cv2.imshow('map', cv2.flip(cv2.resize(self.map, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST), 0))
        cv2.waitKey(1)

    def step(self,action):
        if self.done:
            observation = np.zeros((224, 224, 3), dtype=np.uint8)
            return observation,0,None,True
        while True:
            try:
                with open(self.transaction_file,'rb') as f:
                    transaction = pickle.load(f)
                if transaction['done']:
                    break
                if transaction['action'] is None:
                    transaction['action'] = action
                    with open(self.transaction_file,'wb') as f:
                        pickle.dump(transaction,f)
                    break
                time.sleep(0.1)
            except Exception as e:
                time.sleep(0.1)
        #取回环境返回的transaction
        while True:
            try:
                with open(self.transaction_file,'rb') as f:
                    transaction = pickle.load(f)
                if transaction['action'] is None:
                    transaction['action'] = action
                    observation = transaction['observation']
                    reward = transaction['reward']
                    done = transaction['done']
                    break
            except Exception as e:
                time.sleep(0.1)
        self.map = observation
        self.done = done
        info = {}
        return observation,reward,done,info


    def reset(self):
        self.map = np.zeros((224, 224, 3), dtype=np.uint8)
        self.done = False
        print('Reset Env')
        observation = np.zeros((224,224,3),dtype=np.uint8)
        transaction = {'observation':observation,'reward':0,'action':None,'done':False}
        with open(self.transaction_file,'wb') as f:
            pickle.dump(transaction,f)
        subprocess.Popen(["cmd", "/c",'python','WorkRLRobot.py','-rank', str(self.rank)])
        return observation


# In[3]:

#
# sc2 = StarCraft2Env(0)
# check_env(sc2)


# In[ ]:


# for _ in range(600):
#     sc2.step(0)
#     sc2.step(1)
#     sc2.step(2)
#     sc2.step(3)
#     sc2.step(4)
# sc2.step(5)


# In[5]:


# with open('transaction.pkl','rb') as f:
#             tr2 = pickle.load(f)
# print(tr2)


# In[5]:




