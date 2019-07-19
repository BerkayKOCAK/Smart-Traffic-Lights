
FileRoot = "C:/Users/Lenovo/Documents/pdfler/okul/BAHAR - 2019/Vehicular Networks/proje/sumo-tests/traci_tls/sonuclar/"

ProposedFileRaw = "Primary_vs_StreetPROPOSED"
DefaultFileRaw = "Primary_vs_StreetDEFAULT"

ProposedFile = FileRoot + ProposedFileRaw + ".txt"
DefaultFile = FileRoot + DefaultFileRaw + ".txt"


fBetter = open(ProposedFile,"r")
fWorse = open(DefaultFile, "r")

ProposedSet = []
DefaultSet = []

f1 = fBetter.readlines()

for x in f1:
    ProposedSet.append(int(x))

f2 = fWorse.readlines()

for x in f2:
    DefaultSet.append(int(x))

FinalSet = []
OutputFile = FileRoot + ProposedFileRaw +"_vs_" + DefaultFileRaw + ".txt"
fOutput =  open( OutputFile,"w")

for x in range(0,len(ProposedSet)):
    if ProposedSet[x] < DefaultSet[x]:
        fOutput.write(str(ProposedSet[x]) + "\t" + str(DefaultSet[x]) + "\n")






