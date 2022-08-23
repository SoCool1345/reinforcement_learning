#!/usr/bin/env python
# coding: utf-8

# In[1]:


import math
import pickle
import random
import time
import cv2
import numpy as np
from sc2 import maps
from sc2.ids.unit_typeid import UnitTypeId
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
import nest_asyncio
nest_asyncio.apply()


# In[2]:


# self.minerals: int
# self.vespene: int
# self.supply_army: int # 0 at game start
# self.supply_workers: int # 12 at game start
# self.supply_cap: int # 14 for zerg, 15 for T and P at game start
# self.supply_used: int # 12 at game start
# self.supply_left: int # 2 for zerg, 3 for T and P at game start

class WorkerRushBot(BotAI):
    async def on_step(self, iteration: int):
        while True:
            try:
                with open('transaction.pkl','rb') as f:
                    transaction = pickle.load(f)
                if transaction['action'] is not None:
                    break
                time.sleep(0.1)
            except Exception as e:
                time.sleep(0.1)
        action = transaction['action']
        await self.distribute_workers()
        try:
            if action == 0:
                have_builded = False
                for nexus in self.townhalls:
                    #水晶塔
                    if self.supply_left<4:
                        if self.can_afford(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON)==0:
                            await self.build(UnitTypeId.PYLON,near=nexus)
                            have_builded = True
                            # print('建造水晶塔')

                    #探机
                    if not have_builded:
                        workers_count = len(self.workers.closer_than(10,nexus))
                        if workers_count < 22:
                            if self.can_afford(UnitTypeId.PROBE) and nexus.is_idle :
                                nexus.train(UnitTypeId.PROBE)
                                have_builded = True
                                # print('建造探机')

                        #吸收间
                        for vespene in self.vespene_geyser.closer_than(15,nexus):
                            if self.can_afford(UnitTypeId.ASSIMILATOR) and not self.structures(UnitTypeId.ASSIMILATOR).closer_than(2,vespene).exists:
                                await self.build(UnitTypeId.ASSIMILATOR,near=vespene)
                                have_builded = True
                                # print('建造吸收间')
                    #扩建基地
                    if not have_builded:
                        if self.can_afford(UnitTypeId.NEXUS) and self.already_pending(UnitTypeId.NEXUS)==0:
                            await self.expand_now()

            elif action == 1:
                for nexus in self.townhalls:
                    #传送门
                    if not self.structures(UnitTypeId.GATEWAY) and self.already_pending(UnitTypeId.GATEWAY)==0:
                        if self.can_afford(UnitTypeId.GATEWAY):
                            await self.build(UnitTypeId.GATEWAY,near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
                            # print('建造传送门')
                    #控制核心
                    if not self.structures(UnitTypeId.CYBERNETICSCORE) and self.already_pending(UnitTypeId.CYBERNETICSCORE)==0:
                        if self.can_afford(UnitTypeId.CYBERNETICSCORE):
                            await self.build(UnitTypeId.CYBERNETICSCORE,near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
                            # print('建造控制核心')
                    #星门
                    if self.structures(UnitTypeId.STARGATE).amount < 2:
                        if self.can_afford(UnitTypeId.STARGATE):
                            await self.build(UnitTypeId.STARGATE,near=self.structures(UnitTypeId.PYLON).closest_to(nexus))
                            # print('建造星门')
            elif action == 2:
                #虚空辉光舰
                for sg in self.structures(UnitTypeId.STARGATE).ready.idle:
                    if self.can_afford(UnitTypeId.VOIDRAY):
                        sg.train(UnitTypeId.VOIDRAY)
                        # print('建造虚空辉光舰')
            #侦察
            elif action == 3:
                try:
                    self.last_sent
                except:
                    self.last_sent = 0
                if (iteration - self.last_sent)>200:
                    try:
                        if self.units(UnitTypeId.PROBE).idle.exists:
                            probe = random.choice(self.units(UnitTypeId.PROBE).idle)
                        else:
                            probe = random.choice(self.units(UnitTypeId.PROBE))
                        probe.attact(self.enemy_start_locations[0])
                        self.last_sent = iteration
                        # print('侦察')
                    except:
                        pass
            #进攻
            elif action == 4:

                for voidray in self.units(UnitTypeId.VOIDRAY).idle:

                    if self.enemy_units.closer_than(10,voidray):
                        voidray.attack(random.choice(self.enemy_units.closer_than(10,voidray)))
                    elif self.enemy_structures.closer_than(10,voidray):
                        voidray.attack(random.choice(self.enemy_structures.closer_than(10,voidray)))
                    elif self.enemy_units:
                        voidray.attack(random.choice(self.enemy_units))
                    elif self.enemy_structures:
                        voidray.attack(random.choice(self.enemy_structures))

                    elif self.enemy_start_locations:
                        voidray.attack(self.enemy_start_locations[0])
            #撤退
            elif action == 5:
                try:
                    if self.units(UnitTypeId.VOIDRAY).amount>0:
                        for voidray in self.units(UnitTypeId.VOIDRAY):
                            voidray.attack(self.start_location)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
        #画图
        map = np.zeros((self.game_info.map_size[0],self.game_info.map_size[1],3),dtype=np.uint8)
        for mineral in self.mineral_field:
            pos = mineral.position
            c = [175,255,255]
            fration = mineral.mineral_contents/1000
            y,x = math.ceil(pos.y),math.ceil(pos.x)
            if mineral.is_visible:
                map[y][x] = [int(fration*i) for i in c]
            else:
                map[y][x] = [50,50,50]


        for vespene in self.vespene_geyser:
            pos = vespene.position
            c = [255,175,255]
            fration = vespene.vespene_contents/2250
            y,x = math.ceil(pos.y),math.ceil(pos.x)
            if vespene.is_visible:
                map[y][x] = [int(fration*i) for i in c]
            else:
                map[y][x] = [50,50,50]

        for structure in self.structures:
            pos = structure.position
            if structure.type_id == UnitTypeId.NEXUS:
                c = [255,255,175]
            else:
                c = [0,255,175]
            fration = structure.health_percentage
            y,x = math.ceil(pos.y),math.ceil(pos.x)
            map[y][x] = [int(fration*i) for i in c]


        for unit in self.units:
            pos = unit.position
            if unit.type_id == UnitTypeId.VOIDRAY:
                c = [255,0,0]
            else:
                c = [175,255,0]
            fration = unit.health_percentage
            y,x = math.ceil(pos.y),math.ceil(pos.x)
            map[y][x] = [int(fration*i) for i in c]

        #绘制敌人
        for enemy_location in self.enemy_start_locations:
            pos = enemy_location.position
            c = [0,0,255]
            y,x = math.ceil(pos.y),math.ceil(pos.x)
            map[y][x] = c

        for structure in self.enemy_structures:
            pos = structure.position
            c = [0,100,175]
            fration = structure.health_percentage
            y,x = math.ceil(pos.y),math.ceil(pos.x)
            map[y][x] = [int(fration*i) for i in c]

        for unit in self.enemy_units:
            pos = unit.position
            c = [100,0,255]
            fration = unit.health_percentage
            y,x = math.ceil(pos.y),math.ceil(pos.x)
            map[y][x] = [int(fration*i) for i in c]

        #计算奖励值
        reward = 0
        try:
            for voidray in self.units(UnitTypeId.VOIDRAY):
                if voidray.is_attacking and voidray.target_in_range:
                    if self.enemy_structures.closer_than(8,voidray) or self.enemy_units.closer_than(8,voidray):
                        reward += 0.01
        except Exception as e:
            print(e)
            reward = 0

        if iteration%10==0:
            print(f'action:{action}')
            print(f'iter:{iteration},reward:{reward}')
        map = cv2.copyMakeBorder(map,224-map.shape[0],0,224-map.shape[1],0,cv2.BORDER_CONSTANT, value=(0,0,0))
        cv2.imshow('map',cv2.flip(cv2.resize(map,None,fx=2,fy=2,interpolation=cv2.INTER_NEAREST),0))
        cv2.waitKey(1)

        transaction = {'observation':map,'reward':reward,'action':None,'done':False}

        with open('transaction.pkl','wb') as f:
            pickle.dump(transaction,f)


# In[3]:


result = run_game(maps.get("WorldofSleepersLE"), [
    Bot(Race.Protoss, WorkerRushBot()),
    Computer(Race.Random, Difficulty.VeryHard)
], realtime=False)


# In[4]:


with open('result.txt','a') as f:
    f.write(f'{result}\n')
if str(result) == 'Result.Victory':
    print(str(result))
    rwd = 500
else:
    rwd = -500
observation = np.zeros((224,224,3),dtype=np.uint8)
transaction = {'observation':observation,'reward':0,'action':None,'done':True}
with open('transaction.pkl','wb') as f:
    pickle.dump(transaction,f)

cv2.destroyAllWindows()
cv2.waitKey(1)

