import csv
import matplotlib.pyplot as plt
import numpy as np

#linear speed in mm
speed = 800
graph_title = "{0}mm/s".format(speed)
path_high_res = "C:/Users/sevek/Desktop/BabyfootSpring2023/LinearTest/Cam5_{0}".format(speed)
path_low_res = "C:/Users/sevek/Desktop/BabyfootSpring2023/LinearTest/Cam0_{0}".format(speed)

#reads a file and puts the data in a dictionnary
def read_file(path,discard_zeros=True):
    file = open(path, "r", encoding="utf8")
    tsv_reader = csv.reader(file, delimiter="\t")
    data = {"ts":[],
            "x":[],
            "y":[],
            "vx":[],
            "vy":[],
            "ypred_frwd":[],
            "ypred_mid":[],
            "ypred_def":[],
            "ypred_goal":[]}
    counter = 0
    for row in tsv_reader:
        if round(float(row[0])) == 0 and counter > 10:
            return data,counter
        data["ts"].append(float(row[0]))
        data["x"].append(float(row[1]))
        data["y"].append(float(row[2]))
        data["vx"].append(float(row[7]))
        data["vy"].append(float(row[8]))
        data["ypred_frwd"].append(float(row[3]))
        data["ypred_mid"].append(float(row[4]))
        data["ypred_def"].append(float(row[5]))
        data["ypred_goal"].append(float(row[6]))
        counter += 1

#recreate the commands sent to the actuators (same formula as in the VI)
def make_data(ts,speed):
    data = []
    for t in ts:
        temp = (t*speed*0.1+15)%60
        if temp <= 30:
            data.append((temp - 15)*10 - 120)
        else:
            data.append((45 - temp)*10 - 120)
    return data

#crop and shift the data to have all 3 "channels" (command, Cam0 and Cam5) synchronized
def sinc_data(data,speed,length):
    for i in range(len(data["ts"])):
        if round((data["ts"][i]*speed*0.1+15)%60) == 0:
            data["ts"] = data["ts"][i:i+length]
            data["y"] = data["y"][i:i+length]
            return data

if __name__ == "__main__":
    data_high, counter = read_file(path_high_res)
    data_low, counter = read_file(path_low_res)

    data_size = int(300000/speed)#int(min(len(data_high["ts"]),len(data_low["ts"]))-400000/speed)
    print("Data size: " + str(data_size))

    data_high = sinc_data(data_high,speed,data_size)
    data_low = sinc_data(data_low,speed,data_size)
    y_control = make_data(data_low["ts"][:],speed)

    error_low = abs(np.array(y_control)-np.array(data_low["y"]))
    print("\n===== LOW RES ===== \nerror mean: {0}".format(np.mean(error_low)))
    print("error median: {0}".format(np.median(error_low)))
    print("error std: {0}\n".format(np.std(error_low)))

    error_high = abs(np.array(y_control)-np.array(data_high["y"]))
    print("\n===== HIGH RES ===== \nerror mean: {0}".format(np.mean(error_high)))
    print("error median: {0}".format(np.median(error_high)))
    print("error std: {0}\n".format(np.std(error_high)))

    fig, ax = plt.subplots()
    time_axis = [i-data_low["ts"][0] for i in data_low["ts"]]
    ax.plot(time_axis, data_low["y"], label="cam0")
    ax.plot(time_axis, data_high["y"], label="cam5")
    ax.plot(time_axis, y_control, label="command")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("position [mm]")
    ax.set_title(graph_title)
    ax.legend()
    plt.show()