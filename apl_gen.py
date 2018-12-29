import numpy as np
import json
import subprocess
from operator import itemgetter

actions = np.array(["use_items", "potion", "call_dreadstalkers", "summon_demonic_tyrant", "hand_of_guldan", "demonbolt", "shadow_bolt", "grimoire_felguard", "summon_vilefiend", "bilescourge_bombers"], dtype=np.object)

conditions = np.array(["", "soul_shard>=3"], dtype=np.object)

chromosomes = []

for i in range(1):

        print("Iteration: " + str(i))

        for i in range(100-len(chromosomes)):
                chromosomes.append({"Genes" : np.random.choice(actions + ',if=' + np.random.choice(conditions, len(actions)), len(actions), False)})
        file = open(r"tmp\apl_gen_run.simc", "w")
        file.write("apl_gen_base.simc\n")

        for i in range(100):
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
        chromosomes = chromosomes[:10]

        for chromosome in chromosomes:
                print(chromosome)