import numpy as np
import json
import subprocess
from operator import itemgetter

class IntCondition:
        def __init__(self, condition, range):
                self.condition = condition
                self.range = range

        def generate(self):
                return np.random.choice(["", ",if=" + np.random.choice(["", "!"]) + self.condition + np.random.choice(["<", ">", "=", ">=", "<="]) + str(np.random.choice(self.range))])

class Conditions:
        def __init__(self):
                self.conditions = []

        def generate(self):
                return np.random.choice(self.conditions).generate()

        def add(self, condition):
                self.conditions.append(condition)

actions = np.array(["use_items", "potion", "call_dreadstalkers", "summon_demonic_tyrant", "hand_of_guldan", "demonbolt", "shadow_bolt", "grimoire_felguard", "summon_vilefiend", "bilescourge_bombers"], dtype=np.object)

conditions = Conditions()
conditions.add(IntCondition("soul_shard", range(0,5)))
conditions.add(IntCondition("buff.demonic_core.stack", range(0, 4)))

chromosomes = []

for i in range(2):

        print("Iteration: " + str(i))

        for i in range(1000-len(chromosomes)):
                genes = []
                for j in range(np.random.randint(len(actions), 30)):
                        genes.append(np.random.choice(actions) + conditions.generate())
                chromosomes.append({"Genes" : genes})

        file = open(r"tmp\apl_gen_run.simc", "w")
        file.write("apl_gen_base.simc\n")

        for i in range(1000):
                file.write("profileset.\"" + str(i) + "\"=\"actions=/" + chromosomes[i]["Genes"][0] + "\n")
                for j in range(1, len(chromosomes[i]["Genes"])):
                        file.write("profileset.\"" + str(i) + "\"+=\"actions+=/" + chromosomes[i]["Genes"][j] + "\n")

        file.close()

        subprocess.run([r"C:\Simulationcraft(x64)\810-01\simc.exe", r"tmp\apl_gen_run.simc"])

        dps = {}

        json_data = open(r"tmp\report.json")
        data = json.load(json_data)

        results = data["sim"]["profilesets"]["results"]

        for result in results:
                if(result["name"] == "Nuraki"):
                        continue
                chromosomes[int(result["name"])]["DPS"] = result["mean"]

        json_data.close()

        chromosomes = sorted(chromosomes, key=itemgetter("DPS"), reverse=True)
        chromosomes = chromosomes[:(len(chromosomes)//10)]

print(chromosomes[0])