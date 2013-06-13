#labelList=lambda x: 

def writePropertiesFiles(propertiesFile,completeList):
    for x in completeList:
        element=x[1]
        #stringToWrite=element
        #propertiesFile.write("yada\n")
        #stringToWrite=""
        #stringToWrite = "%s%s%s%s%s\n"%(str(element),"\t",str(x[0][1]),"\t",str(x[0][0])) if element=="jobtracker" else str(element)+"\t"+str(x[0][1])+"\n"
        stringToWrite = '{0}{1}{2}:54311{3}{4}\n'.format(\
                        str(element)," "*(4),\
                        str(x[0][1])," "*(4),\
                        str(x[0][0]))\
                        if element=="jobtracker" else\
                        '{0}{1}{2}\n'.format(\
                        str(element),\
                        " "*(4),\
                        str(x[0][1]))
        propertiesFile.write(stringToWrite)




def preparePropertyFile(conn,currentReservationId):
    propertiesFile=open("properties","w")
    allIPs=[ i.ip_address for r in conn.get_all_instances() if r.id in\
            currentReservationId for i in r.instances]
    allPrivateIPs=[ i.private_ip_address for r in conn.get_all_instances()\
                    if r.id in currentReservationId for i in r.instances]
    ipList=map(lambda x,y :(x,y) ,allIPs,allPrivateIPs) 
    labelList=map( lambda x : "tasktracker" if (x[0]==x[1])\
                   else "jobtracker"  ,   ipList)
    completeList=map(lambda x,y:(x,y) ,ipList,labelList)
    writePropertiesFiles(propertiesFile,completeList)
    #propertiesFile.write(str(allIPs))
    #propertiesFile.write(str(allPrivateIPs))
    #propertiesFile.write(str(ipList))
    #propertiesFile.write(str(labelList))
    #propertiesFile.write(str(completeList))
    propertiesFile.flush()
    print "hello"
