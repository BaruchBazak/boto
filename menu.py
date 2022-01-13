from boto3 import exceptions
import boto3
import json_oparations


def describe():
    client = boto3.client('ec2', region)
    response = client.describe_instances()
    for i in response['Reservations']:
        for out in i["Instances"]:
            if out['State']['Name'] == "running":
                print("ID : {0}, State : {1}, IP : {2}".format(out['InstanceId'], out['State']['Name'],
                                                               out['PublicIpAddress']))
                if out['InstanceId'] not in ec2_data["ec2_instance_ids"]:
                    ec2_data["ec2_instance_ids"].append(out['InstanceId'])
                    json_oparations.saveJsonFata("./ec2_data.json", ec2_data)
            else:
                print("ID : {0}, State : {1}".format(out['InstanceId'], out['State']['Name']))
                if out['InstanceId'] not in ec2_data["ec2_instance_ids"]:
                    ec2_data["ec2_instance_ids"].append(out['InstanceId'])
                    json_oparations.saveJsonFata("./ec2_data.json", ec2_data)
    print("\n")


def create_instances():
    instances = ec2_client.run_instances(
        ImageId=ImageId,
        MinCount=MinCount,
        MaxCount=MaxCount,
        InstanceType=InstanceType
    )
    instance_id = instances["Instances"][0]["InstanceId"]
    print(instance_id)
    if "ec2_instance_ids" in ec2_data:
        ec2_data["ec2_instance_ids"].append(instance_id)
        json_oparations.saveJsonFata("./ec2_data.json", ec2_data)
    else:
        ec2_data["ec2_instance_ids"] = [instance_id]
        json_oparations.saveJsonFata("./ec2_data.json", ec2_data)


def start_instances():
    ec2 = boto3.resource("ec2", region)
    try:
        num_instances = int(input("Enter how many instances you want start ? : "))
    except ValueError as e:
        print(e, "\nOnly numbers !")
        num_instances = int(input("Enter how many instances you want start ? : "))
    ids = []
    for i in range(num_instances):
        instance = input("instance id : ")
        ids.append(instance)
    ec2.instances.filter(InstanceIds=ids).stop()
    print("Instances {0} started\n".format(ids))


def stop_instances():
    ec2 = boto3.resource("ec2", region)
    try:
        num_instances = int(input("Enter how many instances you want stop ? : "))
    except ValueError as e:
        print(e, "\nOnly numbers !")
        num_instances = int(input("Enter how many instances you want stop ? : "))
    ids = []
    for i in range(num_instances):
        instance = input("instance id : ")
        ids.append(instance)
    ec2.instances.filter(InstanceIds=ids).stop()
    print("Instances {0} stopped\n".format(ids))


def print_all_id():
    # Print all ids from ec2_data.json file
    num = 1
    for instance_id in ec2_data["ec2_instance_ids"]:
        print("{0}) {1}".format(num, instance_id))
        num += 1
    print("\n")


def terminate_by_id():
    ec2 = boto3.resource("ec2", region)
    instance = input("Enter the id off machine you want to terminate : ")
    ids = [instance]
    ec2.instances.filter(InstanceIds=ids).terminate()
    print("{0} terminated.".format(ids))
    for i in ids:
        if i in ec2_data["ec2_instance_ids"]:
            ec2_data["ec2_instance_ids"].remove(i)


def terminate_all():
    ec2 = boto3.resource('ec2', region)
    for instance_id in ec2_data["ec2_instance_ids"]:
        instance = ec2.Instance(instance_id)
        print(instance)
        try:
            instance.terminate()
            print("terminated {0}\n".format(instance_id))
            ec2_data["ec2_instance_ids"].remove(instance_id)
            json_oparations.saveJsonFata("./ec2_data.json", ec2_data)
        except exceptions as e:
            print(e)
            print("{0} not found\n".format(instance_id))
            ec2_data["ec2_instance_ids"].remove(instance_id)
            json_oparations.saveJsonFata("./ec2_data.json", ec2_data)


def main():
    while True:
        print("Boto3 menu : \n----------------\n1.Deploy instance(s)\n"
              "2.Start instances by ID\n3.Stop instances by ID\n"
              "4.Terminate instance\n5.Describe instances\n6.Terminate all instances\n7.Exit")
        choice = input("Enter number 1-6 : ")
        if choice == "1":
            print("\nDeploy Instances\n-----------------")
            num_instances = int(input("How many instances you want to deploy ? : ")) + 1
            for i in range(1, num_instances):
                print("Deploy instance {0}".format(i))
                create_instances()
                print("Instance {0} pending".format(i))
            print("done\n")
        elif choice == "2":
            print("\nStart instance\n---------------")  # Ids from ec2_data.config
            start_instances()
        elif choice == "3":
            print("\nStop Instances\n-------------------")  # Ids from ec2_data.config
            stop_instances()
        elif choice == "4":
            print("\nTerminate Instance\n------------------")
            terminate_by_id()
        elif choice == "5":
            print("\nDescribe All instances in region - {0}"
                  "\n--------------------".format(region))  # 12/01/22 Describe only : ID, State and PublicIP
            describe()
        elif choice == "6":
            print("\nTerminate all Instances\n------------------")
            terminate_all()
        elif choice == "7":
            break
        else:
            print("Only 1-7")


config_data = json_oparations.loadJsonData("./config.json")
ec2_json_data_path = config_data["ec2_data_path"]
ImageId = config_data["ami"]
MinCount = config_data["MinCount"]
MaxCount = config_data["MaxCount"]
InstanceType = config_data["InstanceType"]
ec2_data = json_oparations.loadJsonData(ec2_json_data_path)
region = config_data["Region"]

ec2_client = boto3.client("ec2", region_name=region)


if __name__ == '__main__':
    main()
