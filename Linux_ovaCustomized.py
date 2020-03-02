#！/usr/bin/env python

import os
import sys
import subprocess
from xml.dom.minidom import parseString




def get_ovf_properties():
    properties={}
    ovfenv_cmd = "/usr/bin/vmtoolsd --cmd 'info-get guestinfo.ovfEnv'"
    xml_parts=subprocess.Popen(ovfenv_cmd,shell=True,stdout=subprocess.PIPE).stdout.read()
    raw_data=parseString(xml_parts)
    for property in raw_data.getElementsByTagName('Property'):
        key,value=[ property.attributes['oe:key'].value,property.attributes['oe:value'].value]
        properties[key]=value
    return properties

def network_seeting(ipaddr,prefix,gateway,hostname,dns):
    sp=subprocess.Popen(["/usr/bin/hostnamectl","set-hostname",hostname],stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    sp.communicate()

    sp=subprocess.Popen(["/usr/bin/nmcli connection modify ens160 ipv4.addresses "+ipaddr+"/"+prefix+" ipv4.gateway "+gateway+" ipv4.dns "+dns+" ipv4.method manual"],shell=True,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    sp.communicate()


def change_root_passwd(root_password):
    #subprocess.call(["echo "+root_password+ "| /usr/bin/passwd --stdin root"],shell=true)
    sp=subprocess.Popen(["/usr/sbin/chpasswd"],stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    sp.communicate(input='root:%s' % root_password)
    sp.wait()
    if sp.returncode != 0:
        print("Failed to set new for root")

def replace_line(filepath):
    fin=open(filepath,"rt")
    data=fin.read()
    data.replace('/etc/rc.d/getOVF.py','')
    fin.close()

    fin=open(filepath,"wt")
    fin.write(data)
    fin.close()




properties = get_ovf_properties()

if len(properties['hostname'])>0 and len(properties['ipaddr'])>0 and len(properties['prefix'])>0 and len(properties['gateway'])>0 and len(properties['dns_server'])>0:
    network_seeting(properties['ipaddr'], properties['prefix'], properties['gateway'], properties['hostname'], properties['dns_server'])

if len(properties['root_password'])>0:
    change_root_passwd(properties['root_password'])

replace_line("/etc/rc.d/rc.local")
#subprocess.call("/usr/bin/sed '$ d' /etc/rc.d/rc.local",shell=True)
subprocess.call("/usr/bin/chmod u-x /etc/rc.d/rc.local",shell=True)




dir = os.getcwd()
os.remove(dir+'/%s' % sys.argv[0])

