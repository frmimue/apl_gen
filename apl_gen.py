import numpy as np
import json
import subprocess
from operator import itemgetter
import copy
import sys

class Condition:

        conditions = {'soul_shard' : (0, 5), 'buff.demonic_core.stack' : (0, 4), 'cooldown.summon_demonic_tyrant.remains': (0, 90)}

        operators = ['>', '<', '>=', '<=', '=']

        def random():
                condition = np.random.choice(list(Condition.conditions.keys()))
                value = np.random.randint(Condition.conditions[condition][0], Condition.conditions[condition][1])
                operator = np.random.choice(Condition.operators)
                return Condition(condition, operator, value)

        def __init__(self, condition, operator, value):
                self.condition = condition
                self.operator = operator
                self.value = value

        def __str__(self):
                return ',if=' + str(self.condition) + str(self.operator) + str(self.value)

        def mutate(self):
                option = np.random.randint(0, 3)
                if(option == 0):
                        self = Condition.random()
                        return
                if(option == 1):
                        self.operator = np.random.choice(Condition.operators)
                        return
                if(option == 2):
                        self.value = np.random.randint(Condition.conditions[self.condition][0], Condition.conditions[self.condition][1])
                        
                        

class Action:

        actions = ['use_items', 'potion', 'call_dreadstalkers', 'summon_demonic_tyrant', 'hand_of_guldan', 'demonbolt', 'shadow_bolt', 'grimoire_felguard', 'summon_vilefiend', 'bilescourge_bombers']

        def random():
                choice = np.random.randint(0, 2)
                if(choice == 0):
                        return Action(np.random.choice(Action.actions), None)
                if(choice == 1):
                        return Action(np.random.choice(Action.actions), Condition.random())

        def __init__(self, action, condition):
                self.action = action
                self.condition = condition

        def __str__(self):
                if(self.condition != None):
                        return str(self.action) + str(self.condition)
                return str(self.action)

        def mutate(self):
                option = np.random.randint(0, 2)
                if(option == 0):
                        self.action = np.random.choice(Action.actions)
                        return
                if(option == 1):
                        if(self.condition == None):
                                self.condition = Condition.random()
                                return
                        option = np.random.randint(0, 2)
                        if(option == 0):
                                self.condition = None
                                return
                        if(option == 1):
                                self.condition.mutate()
                                return

class APL:

        def random(max_length):
                actions = []
                for i in range(np.random.randint(1, max_length)):
                        actions.append(Action.random())
                return APL(actions)

        def __init__(self, actions):
                self.actions = actions
                self.dps = 0

        def __lt__(self, other):
                if(abs(other.dps - self.dps) < 100):
                        return len(self.actions) < len(other.actions)
                return self.dps < other.dps

        def __str__(self):
                retval = ''
                for action in self.actions:
                        retval += str(action) + '\n'
                retval += '\n'
                return retval

        def asProfileSet(self, n):
                retval = ''
                retval += "profileset.\"" + str(n) + "\"=\"actions=/" + str(self.actions[0]) + "\n"
                for i in range(1, len(self.actions)):
                        retval += "profileset.\"" + str(n) + "\"+=\"actions+=/" + str(self.actions[i]) + "\n"
                retval += '\n'
                return retval

        def asCopy(self, n):
                retval = r'copy=' + str(n) + '\n'
                retval += "actions=/" + str(self.actions[0]) + "\n"
                for i in range(1, len(self.actions)):
                        retval += "actions+=/" + str(self.actions[i]) + "\n"
                retval += '\n'
                return retval
                

        def crossover(self, other):
                crossover_point = np.random.randint(0, min(len(self.actions), len(other.actions)))
                return [APL(copy.deepcopy(self.actions[:crossover_point]) + copy.deepcopy(other.actions[crossover_point:])), APL(copy.deepcopy(other.actions[:crossover_point]) + copy.deepcopy(self.actions[crossover_point:]))]

        def mutate(self, chance):
                for i in range(len(self.actions)):
                        if (np.random.random() > chance):
                                return
                        option = np.random.randint(0, 3)
                        if(option == 0):
                                self.actions[i].mutate()
                                return
                        if(option == 1):
                                if(len(self.actions) == 1):
                                        return
                                del self.actions[i]
                                i = i - 1
                                return
                        if(option == 2):
                                self.actions.insert(i+1, Action.random())
                                i = i + 1
                                return


NUM_APLS = int(sys.argv[1])
ITERATIONS = int(sys.argv[2])

apls = []

evolutions = []

## Init

for i in range(NUM_APLS):
        apls.append(APL.random(30))

for i in range(ITERATIONS):

        print("Iteration: " + str(i))

        ## Generate simc file
        file = open(r"tmp\apl_gen_run.simc", "w")
        file.write("apl_gen_base.simc\n")
        for j in range(len(apls)):
                file.write(apls[j].asProfileSet(j))
        file.close()

        ## Run SimC and collect data
        subprocess.run([r"C:\Simulationcraft(x64)\810-01\simc.exe", r"tmp\apl_gen_run.simc", r"html=tmp\report-" + str(i) + r".html"])

        json_data = open(r"tmp\report.json")
        data = json.load(json_data)

        results = data["sim"]["profilesets"]["results"]

        for result in results:
                apls[int(result["name"])].dps = int(result["median"])

        json_data.close()

        apls = sorted(apls, reverse=True)

        evolutions.append( {"max": apls[0].dps, "median": (apls[len(apls)//2].dps + apls[(len(apls)//2)-1].dps)/2.0})

        pie_size = len(apls)//5

        apls = apls[:pie_size]

        ## Do some special stuff in the last iteration to get a more detailed report
        if(i == (ITERATIONS -1)):
                file = open(r"tmp\apl_gen_run.simc", "w")
                file.write("apl_gen_base.simc\n")
                for j in range(len(apls)):
                        file.write(apls[j].asCopy(j))
                file.close()
                subprocess.run([r"C:\Simulationcraft(x64)\810-01\simc.exe", r"tmp\apl_gen_run.simc", r"html=tmp\report-last.html"])
                break


        apl_pairs = np.random.choice(apls, (len(apls)//2, 2), False)


        for apl_pair in apl_pairs:
                cross_apls = apl_pair[0].crossover(apl_pair[1])
                for j in range(4):
                        for cross_apl in cross_apls:
                                apls.append(cross_apl)


        for j in range(2 * pie_size, 3 * pie_size):
                apls[j].mutate(0.25)

        for j in range(3 * pie_size, 4 * pie_size):
                apls[j].mutate(0.5)

        for j in range(4 * pie_size, 5 * pie_size):
                apls[j].mutate(1.0)

print('########################################')
for evolution in evolutions:
        print(evolution)