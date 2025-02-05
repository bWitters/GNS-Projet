import json

#chemin_projet = str(input("Chemin d'acces vers le projet GNS"))
chemin_default = "default.cfg"
chemin_default_after_boot = "default_after_boot.cfg"

address_used = {}


with open('Test_j.json', 'r') as file_json:
    data_json = json.load(file_json)
    address_pool = {"Loopback" : {}, "Address" : {}, "IP Range" : {}, "eBGP_IP" : {}}
    connections = {}
    for as_num in data_json["AS"].keys():
        connections[as_num] = {}
    for as_n,as_val in data_json["AS"].items():
        address_pool["Loopback"][as_n] = {}
        address_pool["Address"][as_n] = {}
        address_pool["IP Range"][as_n] = []
        address_pool["eBGP_IP"][as_n] = []
        connection_done = []
        for router in as_val["Router"].items():
            connections[as_n][router[0]] = {}
            for inter in as_val["Router"][router[0]].keys():
                if "Loopback" not in inter:
                    for key in list(as_val["Router"][router[0]][inter]["connect"].keys()):
                        as_found = None
                        for as_number in data_json["AS"].keys():
                            for router_in_as in data_json["AS"][as_number]["Router"].keys():
                                if router_in_as == key:
                                    as_found = as_number
                        # anti doublon... ;( marche plus avec les items puisque j'ai changé la construction.
                        connection_now_1 = (router[0],key)
                        connection_now_2 = (key,router[0])
                        if connection_now_1 not in connection_done and connection_now_2 not in connection_done:
                            if as_found != as_n:
                                connections[as_n][router[0]][(key, "eBGP")] = ""
                            else:
                                connections[as_n][router[0]][key] = ""
                            connection_done.append(connection_now_1)
                            
        
        i = 1
        j = 1
        for connect in connections[as_n].keys():
            for k in range(len(connections[as_n][connect].keys())):
                address_pool["IP Range"][as_n].append(as_val["Router IP range"].split("/")[0][0:-1]+str(i)+"::")
                i += 1
        

        ip_range_used = []
        i = 1
        for router in as_val["Router"].keys():
            address_pool["Loopback"][as_n][router] = as_val["Loopback IP range"].split("/")[0]+str(i)
            i += 1
        j=0
        for connection in connections[as_n].keys():
            for inter_connection in connections[as_n][connection].keys():
                if type(inter_connection) != type(tuple()):
                    if j< len(address_pool["IP Range"][as_n]):
                        range_to_use = address_pool["IP Range"][as_n][j]
                        j+=1
                        connections[as_n][connection][inter_connection] = range_to_use
                    else: 
                        print("error too much connection for nb of ip range created")
        
    for as_n,as_val in data_json["AS"].items():
        address_used[as_n] = {"Loopback" : [], "Address" : [], "OSPF_ID" : [], "BGP_ID" : []}
        j = 1
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
            bgp_id = " bgp router-id "+bgp_id_to_use+"\n"+" bgp log-neighbor-changes\n no bgp default ipv4-unicast\n no synchronization\n"
            data[69] += bgp_id
            neighbors_data = ""
            loopback_name = ""
            ## Determination de l'adresse de loopback
            i = 1
            address_to_use = address_pool["Loopback"][as_n][router[0]]
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
                for key in data_json["eBGP"][router[0]]["Ext_router"].keys():
                    neighbors_data += " neighbor " + str(data_json["eBGP"][router[0]]["Ext_router"][key]["IP"]).split("/")[0] + " remote-as " + str(data_json["eBGP"][router[0]]["Ext_router"][key]["AS"]) + "\n"

            data[69] += neighbors_data
            data[69] += " !\n address-family ipv4\n exit-address-family\n !\n"


            data[69] += " address-family ipv6\n"
            add_fam_data = ""
            for router_to_compare in address_pool["Loopback"][as_n]:
                if address_pool["Loopback"][as_n][router_to_compare] != address_to_use:
                    add_fam_data += "  neighbor " + address_pool["Loopback"][as_n][router_to_compare] + " activate "
                    # if router[0] in list(data_json["eBGP"].keys()):
                    #     add_fam_data += " next-hop-self "
                    # else :
                    #     add_fam_data += " activate "
                    add_fam_data += "\n"
            if router[0] in list(data_json["eBGP"].keys()):
                for key in data_json["eBGP"][router[0]]["Ext_router"].keys():
                    add_fam_data += "  neighbor " + str(data_json["eBGP"][router[0]]["Ext_router"][key]["IP"]).split("/")[0] + " activate " + "\n"
            if router[0] in data_json["eBGP"].keys():
                for ip in address_pool["IP Range"][as_n]:
                    add_fam_data += "  network " + ip + "/" + as_val["Router IP range"].split("/")[1] + "\n"
                add_fam_data += "  network " + data_json["eBGP"][router[0]]["IP"].split("::")[0] + "::/" + data_json["eBGP"][router[0]]["IP"].split("/")[1] + "\n"
            add_fam_data += " exit-address-family\n" + "!\n"
            data[69] += add_fam_data

            
            for inter in interfaces:

                if "Loopback" in inter:                  
                    address = "ipv6 address "+address_pool["Loopback"][as_n][router[0]]+"/"+"128"+"\n"
                else:                    
                    # Utiliser la plage de la connection
                    
                    if list(as_val["Router"][router[0]][inter]["connect"].keys())[0] in connections[as_n][router[0]].keys():
                        address_to_use = connections[as_n][router[0]][list(as_val["Router"][router[0]][inter]["connect"].keys())[0]]
                    elif "eBGP" in as_val["Router"][router[0]][inter].keys():
                        address_to_use = ""
                    else:
                        address_to_use = connections[as_n][list(as_val["Router"][router[0]][inter]["connect"].keys())[0]][router[0]]
                    address = "ipv6 address "+address_to_use+str(j)+ "/" + as_val["Router IP range"].split("/")[1]+"\n"
                    j += 1

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
                elif as_val["Protocol"] == "RIP":
                    prot = "ipv6 rip ng enable\n"
                    if first_time:
                        for inter_for_rip in interfaces:
                            if "Loopback" in inter_for_rip:
                                inter_name = inter_for_rip
                        data[77] = "ipv6 router rip ng\n" + " redistribute connected\n"
                        first_time = False
                else:
                    prot = "!"
                
                if "Loopback" in inter:
                    to_add =  "!\ninterface " + inter +"\n"+ " no ip address\n " + address + " ipv6 enable\n" + prot +"\n!\n"
                    data[49 + inter_num] = to_add
                    inter_num += 4
                else: # Pour le moment les numéros d'interfaces doivent être assigné dans l'ordre croissant 
                    if "eBGP" in router[1][inter].keys():
                        to_add =  "interface " + inter +"\n"+ " no ip address\n negotiation auto\n " + "ipv6 address " + data_json["eBGP"][router[0]]["IP"] + "\n" + " ipv6 enable\n" + prot + "\n"
                    else:
                        to_add =  "interface " + inter +"\n"+ " no ip address\n negotiation auto\n " + address + " ipv6 enable\n" + prot + "\n"
                    data[49 + inter_num +1:49 + inter_num +4] = ""
                    

                    data[49 + inter_num] = to_add
                
                
                inter_num += 2
            

            # and write everything back
            with open("router_file_"+router[0]+".cfg", 'w') as file:
                file.writelines(data)