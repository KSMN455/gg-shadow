import json
import os
import random
import time

from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

client_id = "door_controller"
iot_endpoint = "xxxxxxxxxxxxxx-ats.iot.ap-northeast-1.amazonaws.com"
root_ca = "/path/to/root.ca.pem"
cert = "xxxxxxxxxx.cert.pem"
private_key = "xxxxxxxxxx.private.key"
gg_core_addr = "GG Core Device IP"
gg_group_ca = "root-ca.crt"

def customShadowCallback_Update(payload, responseStatus, token):
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")
    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~Shadow Update Accepted~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("status: " + str(payloadDict["state"]["desired"]["status"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

if not os.path.isfile(gg_group_ca):
    discoveryInfoProvider = DiscoveryInfoProvider()
    discoveryInfoProvider.configureEndpoint(iot_endpoint)
    discoveryInfoProvider.configureCredentials(root_ca, cert, private_key)
    discoveryInfoProvider.configureTimeout(10)
    discoveryInfo = discoveryInfoProvider.discover(client_id)
    caList = discoveryInfo.getAllCas()
    coreList = discoveryInfo.getAllCores()
    ca = caList[0][1]
    groupCAFile = open(gg_group_ca, "w")
    groupCAFile.write(ca)
    groupCAFile.close()
    print("Successed to discover greengrasss core!")
else:
    print("Greengrass core has already been discovered.")

myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(client_id)
myAWSIoTMQTTShadowClient.configureEndpoint(gg_core_addr, 8883)
myAWSIoTMQTTShadowClient.configureCredentials(gg_group_ca, private_key, cert)

myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)

myAWSIoTMQTTShadowClient.connect()

deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName("door01", True)

items = cycle(["open", "close"])

while True:
    status = random.choice(items)
    JSONPayload = '{"state":{"desired":{"status":' + '"' + status + '"}}}'
    print(JSONPayload)
    deviceShadowHandler.shadowUpdate(JSONPayload, customShadowCallback_Update, 10)
    time.sleep(30)