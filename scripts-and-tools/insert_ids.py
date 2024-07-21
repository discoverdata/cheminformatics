# grep -A1 '<DRUGBANK_ID>' structures.sdf | grep 'DB' > ids.txt
# grep -n 'Mrv' structures.sdf | cut -f1 -d: >line_numbers.txt

id_file = open("ids.txt","r")
ln_file = open("line_numbers.txt","r")
ids = id_file.read()
ln = ln_file.read()
#print(ids)

id_list = ids.split("\n") 
ln_list = ln.split("\n") 
# printing the data 
id_list = id_list[:-1]
ln_list = ln_list[:-1]

print(len(id_list))
print(len(ln_list))
id_file.close() 
ln_file.close()

ln_list = [int(i) -1 for i in ln_list]
#print(ln_list[0:10])

file = open("solid_stock.sdf","r", encoding = "ISO-8859-1")
nfile = open("new_file.sdf","w")

for count,line in enumerate(file,start = 1):
    if count in ln_list:
        id = id_list.pop(0)
        nfile.write(f"{id}\n")
    else:
        nfile.write(line)

file.close()
nfile.close()
