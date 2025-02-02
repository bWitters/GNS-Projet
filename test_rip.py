import json
# from Exscript.protocols import telnet

# conn = 
# conn.connect('localhost')

#chemin_projet = str(input("Chemin d'acces vers le projet GNS"))

chemin_default = "default.cfg"
chemin_default_after_boot = "default_after_boot.cfg"

address_used = {}
with open('Test_j.json', 'r') as file_json:
    data_json = json.load(file_json)
    address_pool = {"Loopback" : {}, "Address" : {}}
    for as_n,as_val in data_json["AS"].items():
        i = 1
        address_pool["Loopback"][as_n] = {} 
        for router in as_val["Router"].items():
            address_pool["Loopback"][as_n][router[0]] = as_val["Loopback IP range"].split("/")[0]+str(i)
            i += 1

    for as_n,as_val in data_json["AS"].items():
        
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
            data[69] = "!\nrouter bgp " + as_n + "\n"
            i = 1
            bgp_id_to_use = "1.1.1.1"
            while bgp_id_to_use in address_used[as_n]["BGP_ID"]:
                i+=1 
                bgp_id_to_use = str(i)+"."+str(i)+"."+str(i)+"."+str(i)
            address_used[as_n]["BGP_ID"].append(bgp_id_to_use)
            bgp_id = " bgp router-id "+bgp_id_to_use+"\n"+" bgp log-neighbor-changes\n no bgp default ipv4-unicast\n"
            data[69] += bgp_id
            neighbors_data = ""
            loopback_name = ""
            ## Determination de l'adresse de loopback
            i = 1
            address_to_use = address_pool["Loopback"][as_n][router[0]]
            
            # as_val["Loopback IP range"].split("/")[0]+str(i)
            # while address_to_use in address_used[as_n]["Loopback"]:
            #     i+=1 
            #     address_to_use = as_val["Loopback IP range"].split("/")[0]+str(i)
            #     print("coucou loopback")
            address_used[as_n]["Loopback"].append(address_to_use)
            ##
            for inter in interfaces:
                if "Loopback" in inter:
                    loopback_name = inter
            for router_to_compare in address_pool["Loopback"][as_n]:
                if address_pool["Loopback"][as_n][router_to_compare] != address_to_use:
                    neighbors_data += " neighbor " + address_pool["Loopback"][as_n][router_to_compare] + " remote-as " + as_n + "\n"
                    neighbors_data += " neighbor " + address_pool["Loopback"][as_n][router_to_compare] + " update-source " + loopback_name + "\n"
            if router[0] in list(data_json["eBGP"].keys()):
                neighbors_data += " neighbor " + address_pool["Loopback"][list(data_json["eBGP"][router[0]].values())[0]][list(data_json["eBGP"][router[0]].keys())[0]] + " remote-as " + list(data_json["eBGP"][router[0]].values())[0] + "\n"
                neighbors_data += " neighbor " + address_pool["Loopback"][list(data_json["eBGP"][router[0]].values())[0]][list(data_json["eBGP"][router[0]].keys())[0]] + " update-source " + loopback_name + "\n"
            data[69] += neighbors_data
            data[69] += " !\n address-family ipv4\n exit-address-family\n!\n"


            for inter in interfaces:

                if "Loopback" in inter:
                    i = 1
                    address_to_use = as_val["Loopback IP range"].split("/")[0]+str(i)
                    while address_to_use in address_used[as_n]["Loopback"]:
                        i+=1 
                        address_to_use = as_val["Loopback IP range"].split("/")[0]+str(i)
                    address_used[as_n]["Loopback"].append(address_to_use)
                    address = "ipv6 address "+address_to_use+"/128"+"\n"
                else:
                    i = 1
                    address_to_use = as_val["Router IP range"].split("/")[0]+str(i)
                    while address_to_use in address_used[as_n]["Address"]:
                        i+=1 
                        address_to_use = as_val["Router IP range"].split("/")[0]+str(i)
                    address_used[as_n]["Address"].append(address_to_use)
                    address = "ipv6 address "+address_to_use+"/64"+"\n"

                # if as_val["Protocol"] == "OSPF":
                #     prot = "ipv6 ospf 3 area "+str(router[1][inter]["area"])
                #     if first_time:
                #         ospf_id = "1.1.1.1"
                #         i=1
                #         while ospf_id in address_used[as_n]["OSPF_ID"]:
                #             i+=1
                #             ospf_id = str(i)+"."+str(i)+"."+str(i)+"."+str(i)
                #         address_used[as_n]["OSPF_ID"].append(ospf_id)
                #         data[77] = "ipv6 router ospf 3\nrouter-id " + ospf_id + "\n"
                #         first_time = False
                
                # if "Loopback" in inter:
                #     to_add =  "!\ninterface " + inter +"\n"+ " no ip address\n " + address + " ipv6 enable\n " + prot +"\n!\n"
                #     data[49 + inter_num] = to_add
                #     inter_num += 4
                # else: # Pour le moment les numéros d'interfaces doivent être assigné dans l'ordre croissant 
                #     to_add =  "interface " + inter +"\n"+ " no ip address\n negotiation auto\n " + address + " ipv6 enable\n " + prot + "\n"
                #     print(data[49 + inter_num +1:49 + inter_num +4])
                #     data[49 + inter_num +1:49 + inter_num +4] = ""
                #     data[49 + inter_num] = to_add
                # inter_num += 2

                prot = ""
                if as_val["Protocol"] == "RIP":
                    prot = "ipv6 rip ng enable\n"
                    if first_time:
                        data[77] = "ipv6 router rip ng\n redistribute connected\n"
                        first_time = False

                if "Loopback" in inter:
                    to_add = "!\ninterface " + inter + "\n" + " no ip address\n " + address + " ipv6 enable" + "\n!\n"
                    data[49 + inter_num] = to_add
                    inter_num += 4
                else:
                    to_add = "interface " + inter + "\n" + " no ip address\n negotiation auto\n " + address + " ipv6 enable\n " + prot
                    # print(data[49 + inter_num + 1:49 + inter_num + 4])
                    data[49 + inter_num + 1:49 + inter_num + 4] = ""
                    data[49 + inter_num] = to_add

                inter_num += 2

            # and write everything back
            with open("router_file_"+router[0]+".cfg", 'w') as file:
                file.writelines(data)