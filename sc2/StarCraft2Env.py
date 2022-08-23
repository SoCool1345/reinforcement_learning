#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import pickle
import time

import gym
import numpy
import subprocess
from stable_baselines3.common.env_checker import check_env


# In[2]:


import numpy as np


class StarCraft2Env(gym.Env):


    def __init__(self):
        super(StarCraft2Env,self).__init__()
        self.observation_space = gym.spaces.Box(low=0,high=255,shape=(224,224,3),dtype=np.uint8)
        self.action_space = gym.spaces.Discrete(6)

    def render(self, mode="human"):
        pass

    def step(self,action):
        while True:
            try:
                with open('transaction.pkl','rb') as f:
                    transaction = pickle.load(f)
                if transaction['action'] is None:
                    transaction['action'] = action
                    with open('transaction.pkl','wb') as f:
                        pickle.dump(transaction,f)
                    break
                    time.sleep(0.1)
            except Exception as e:
                time.sleep(0.1)
        #取回环境返回的transaction
        while True:
            try:
                with open('transaction.pkl','rb') as f:
                    transaction = pickle.load(f)
                if transaction['action'] is None:
                    transaction['action'] = action
                    observation = transaction['observation']
                    reward = transaction['reward']
                    done = transaction['done']
                    break
            except Exception as e:
                time.sleep(0.1)
        info = {}
        return observation,reward,done,info


    def reset(self):
        print('Reset Env')
        observation = np.zeros((224,224,3),dtype=np.uint8)
        transaction = {'observation':observation,'reward':0,'action':None,'done':False}
        with open('transaction.pkl','wb') as f:
            pickle.dump(transaction,f)
        subprocess.Popen(["cmd", "/c",'python','WorkRLRobot.py'])
        return observation


# In[3]:


# sc2 = StarCraft2Env()
# check_env(sc2)


# In[ ]:


# for _ in range(300):
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




