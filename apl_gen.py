import numpy as np
import json
import subprocess
from operator import itemgetter

actions = np.array(["use_items", "potion", "call_dreadstalkers", "summon_demonic_tyrant", "hand_of_guldan", "demonbolt", "shadow_bolt", "grimoire_felguard", "summon_vilefiend", "bilescourge_bombers"], dtype=np.object)

conditions = np.array(["", "soul_shard>=3"], dtype=np.object)

# Generate APL
chromosomes = []

for i in range(2):

        for i in range(1000-len(chromosomes)):
                chromosomes.append({"Genes" : np.random.choice(actions + ',if=' + np.random.choice(conditions, len(actions)), len(actions), False)})
        file = open("apl_gen_run.simc", "w")
        file.write("apl_gen_base.simc\n")

        for i in range(1000):
                file.write("copy=\"" + str(i) + "\"\n")
                file.write("actions=/" + chromosomes[i]["Genes"][0] + "\n")
                for j in range(1, len(chromosomes[i]["Genes"])):
                        file.write("actions+=/" + chromosomes[i]["Genes"][j] + "\n")

        file.close()

        subprocess.run(["C:\Simulationcraft(x64)\810-01\simc.exe", 'apl_gen_run.simc'])

        dps = {}

        json_data = open("report.json")
        data = json.load(json_data)

        players = data["sim"]["players"]

        for player in players:
                if(player["name"] == "Nuraki"):
                        continue
                chromosomes[int(player["name"])]["DPS"] = player["collected_data"]["dps"]["mean"]

        json_data.close()

        chromosomes = sorted(chromosomes, key=itemgetter("DPS"))
        chromosomes = chromosomes[900:]
        print(chromosomes)