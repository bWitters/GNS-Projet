import json
# from Exscript.protocols import telnet

# conn = 
# conn.connect('localhost')

#chemin_projet = str(input("Chemin d'acces vers le projet GNS"))
chemin_default = "default.cfg"
chemin_default_after_boot = "default_after_boot.cfg"

address_used = {}
with open('Test_j.json', 'r') as file_json:
    data = json.load(file_json)

    for as_n,as_val in data["AS"].items():
        address_used[as_n] = {"Loopback" : [], "Address" : [], "OSPF_ID" : [], "BGP_ID" : []}
        for router in as_val["Router"].items():
            with open("router_file_"+router[0]+".cfg", 'w') as router_file:
                with open(chemin_default_after_boot, 'r') as src:
                    router_file.write(src.read())
            
            with open("router_file_"+router[0]+".cfg", 'r') as router_file:
                data = router_file.readlines()

            data[7] = "hostname " +router[0] +"\n"

            data[24] = "ipv6 unicast-routing\nipv6 cef\n"

            inter_to_add = []
            interfaces = as_val["Router"][router[0]].keys()
            inter_num = 0
            first_time = True
            data[69] = "!\nrouter bgp" + as_n + "\n!\n"
            i = 1
            bgp_id_to_use = "1.1.1.1"
            while bgp_id_to_use in address_used[as_n]["BGP_ID"]:
                i+=1 
                bgp_id = str(i)+"."+str(i)+"."+str(i)+"."+str(i)
            address_used[as_n]["BGP_ID"].append(bgp_id_to_use)
            bgp_id = "bgp router-id "+bgp_id_to_use+"\n"+"bgp log-neighbor-changes\n no bgp default ipv4-unicast"
            
            "neighbor"
            "!\naddress-family ipv4\n exit-address-family\n!\n"

            "address-family ipv6"
            "neighbor"
            "exit-address-family"


            for inter in interfaces:

                if "Loopback" in inter:
                    i = 1
                    address_to_use = as_val["Loopback IP range"].split("/")[0]+str(i)
                    while address_to_use in address_used[as_n]["Loopback"]:
                        i+=1 
                        address_to_use = as_val["Loopback IP range"].split("/")[0]+str(i)
                    address_used[as_n]["Loopback"].append(address_to_use)
                    address = "ipv6 address "+address_to_use+"\n"
                else:
                    i = 1
                    address_to_use = as_val["Router IP range"].split("/")[0]+str(i)
                    while address_to_use in address_used[as_n]["Address"]:
                        i+=1 
                        address_to_use = as_val["Router IP range"].split("/")[0]+str(i)
                    address_used[as_n]["Address"].append(address_to_use)
                    address = "ipv6 address "+address_to_use+"\n"

                if as_val["Protocol"] == "OSPF" and "eBGP" not in router[1][inter].keys():
                    prot = " ipv6 ospf 3 area "+str(router[1][inter]["area"])
                    if first_time:
                        ospf_id = "1.1.1.1"
                        i=1
                        while ospf_id in address_used[as_n]["OSPF_ID"]:
                            i+=1
                            ospf_id = str(i)+"."+str(i)+"."+str(i)+"."+str(i)
                        address_used[as_n]["OSPF_ID"].append(ospf_id)
                        data[77] = "ipv6 router ospf 3\nrouter-id " + ospf_id + "\n"
                        first_time = False
                else:
                    prot = "!"
                
                if "Loopback" in inter:
                    to_add =  "!\ninterface " + inter +"\n"+ " no ip address\n " + address + " ipv6 enable\n " + prot +"\n!\n"
                    data[49 + inter_num] = to_add
                    inter_num += 4
                else: # Pour le moment les numéros d'interfaces doivent être assigné dans l'ordre croissant 
                    to_add =  "interface " + inter +"\n"+ " no ip address\n negotiation auto\n " + address + " ipv6 enable\n" + prot + "\n"
                    data[49 + inter_num +1:49 + inter_num +4] = ""
                    

                    data[49 + inter_num] = to_add
                
                inter_num += 2
            

            # and write everything back
            with open("router_file_"+router[0]+".cfg", 'w') as file:
                file.writelines(data)