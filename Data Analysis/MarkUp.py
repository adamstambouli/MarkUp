import csv
import numpy as np
import matplotlib.pyplot as plt


##################################################################
## Defining Functions ############################################
##################################################################

def parse_data(filename):

    time = []
    time_s = []
    Ax = []
    Ay = []
    Az = []
    Gx = []
    Gy = []
    Gz = []


    with open(filename) as f:

        reader = csv.reader(f, delimiter=',')
        header = next(reader, None)

        for row in reader:
            time.append(row[0])
            hours = float(row[0][0:2])
            minutes = float(row[0][3:5])
            seconds = float(row[0][6:8])
            milli_s = float(row[0][9:])
            time_s.append(hours*3600 + minutes*60 + seconds + milli_s*1e-3)
            Ax.append(float(row[1]))
            Ay.append(float(row[2]))
            Az.append(float(row[3]))
            Gx.append(float(row[4]))
            Gy.append(float(row[5]))
            Gz.append(float(row[6]))

    return (time, time_s, Ax, Ay, Az, Gx, Gy, Gz)

def filter_outliers(x, threshold_min, threshold_max):

    x_new = x

    for index in range(0, len(x)):
        if abs(x[index]) < threshold_min or abs(x[index]) > threshold_max:
            if index == 1:
                x_new[index] = 0
            else:
                x_new[index] = x[index-1]

    return x_new

def filter_LPF(samplefreq_des, time, x, a):

    time_des = np.arange(time[0],time[-1], 1/samplefreq_des)
    y = np.interp(time_des, time[100:-100], x[100:-100])

    y_LPF[0] = y[0]

    for index in range(1, len(y)-1):
        y_LPF[index] =  a*y[index-1] + (1-a)*y_LPF[index-1]

    return y_LPF

def filter_movingavg(x, N):
    x_new = x[N:-N]
    # Need to filter points before jumping to the middle point
    # for index in range(0,N-1):
    #     x_new[index] = np.sum(x[index:index+5*N])/(5*N+1)
    for index in range(N, len(x)-1-N):
        x_new[index] = np.sum(x[index-N:index+N])/(2*N+1)
    # for index in range(len(x)-N, len(x)-1):
    #     x_new[index] = np.sum(x[index-5*N:index])/(5*N+1)
    return x_new

def plot_sensor_noise(x, binSize, title, xlabel):
    avg_x = np.mean(x)
    print(avg_x)
    std_x = np.std(x)
    print(std_x)
    bins = np.linspace(avg_x - 4*std_x, avg_x + 4*std_x, binSize)
    plt.hist(x, bins)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.show()

##################################################################
## Main ##########################################################
##################################################################
print('hello Atom!')

time = []
time_s = []
Ax = []
Ay = []
Az = []
Gx = []
Gy = []
Gz = []

fileid = 'dynamic_test.csv'


time, time_s, Ax, Ay, Az, Gx, Gy, Gz = parse_data(fileid)

t = np.array(range(1, len(Ax)+1))

plt.plot(t, Ax)
plt.plot(t, Ay)
plt.plot(t, Az)
plt.legend(['$A_x$', '$A_y$', '$A_z$'], loc='lower left')
plt.title('Accelerometer Data - Raw')
plt.ylabel('A/g [m/s$^2$]')
plt.xlabel('Index')
plt.savefig('accel_data.png', dpi=700)
plt.show()

plt.plot(t, Gx)
plt.plot(t, Gy)
plt.plot(t, Gz)
plt.legend(['$G_x$', '$G_y$', '$G_z$'], loc='lower left')
plt.title('Gyroscope Data - Raw')
plt.ylabel('$\omega$ [$^\circ$/s]')
plt.xlabel('Index')
plt.savefig('gyro_data.png', dpi=700)
plt.show()

# Filter data from LARGE outliers then filter data using a moving average
accel_minthres = 1e-4
accel_maxthres = 2
gyro_minthres = 1e-7
gyro_maxthres = 360

Ax = filter_outliers(Ax, accel_minthres, accel_maxthres)
Ay = filter_outliers(Ay, accel_minthres, accel_maxthres)
Az = filter_outliers(Az, accel_minthres, accel_maxthres)
Gx = filter_outliers(Gx, gyro_minthres, gyro_maxthres)
Gy = filter_outliers(Gy, gyro_minthres, gyro_maxthres)
Gz = filter_outliers(Gz, gyro_minthres, gyro_maxthres)

plt.plot(t, Ax)
plt.plot(t, Ay)
plt.plot(t, Az)
plt.legend(['$A_x$', '$A_y$', '$A_z$'], loc='lower left')
plt.title('Accelerometer Data - Outlier Filter')
plt.ylabel('A/g [m/s$^2$]')
plt.xlabel('Index')
plt.savefig('accel_data.png', dpi=700)
plt.show()

plt.plot(t, Gx)
plt.plot(t, Gy)
plt.plot(t, Gz)
plt.legend(['$G_x$', '$G_y$', '$G_z$'], loc='lower left')
plt.title('Gyroscope Data - Outlier Filter')
plt.ylabel('$\omega$ [$^\circ$/s]')
plt.xlabel('Index')
plt.savefig('gyro_data.png', dpi=700)
plt.show()




# Checking noise characteristics (static test)


# plot_sensor_noise(Ax, 100, '$A_x$ distribution', '$A_x$ [m/s$^2$]' )
# plot_sensor_noise(Ay, 100, '$A_y$ distribution', '$A_y$ [m/s$^2$]' )
# plot_sensor_noise(Az, 100, '$A_z$ distribution', '$A_z$ [m/s$^2$]' )
# plot_sensor_noise(Gx, 100, '$G_x$ distribution', '$G_x$ [m/s$^2$]' )
# plot_sensor_noise(Gy, 100, '$G_y$ distribution', '$G_y$ [m/s$^2$]' )
# plot_sensor_noise(Gz, 100, '$G_z$ distribution', '$G_z$ [m/s$^2$]' )


# Smooth Data


Ax = filter_LPF(15, time_s, Ax, 0.99)
Ay = filter_LPF(15, time_s, Ay, 0.99)
Az = filter_LPF(15, time_s, Az, 0.99)
Gx = filter_LPF(15, time_s, Gx, 0.99)
Gy = filter_LPF(15, time_s, Gy, 0.99)
Gz = filter_LPF(15, time_s, Gz, 0.99)

# N = 3;
# Ax = filter_movingavg(Ax, N)
# Ay = filter_movingavg(Ay, N)
# Az = filter_movingavg(Az, N)
# Gx = filter_movingavg(Gx, N)
# Gy = filter_movingavg(Gy, N)
# Gz = filter_movingavg(Gz, N)

t = np.array(range(1, len(Ax)+1))

plt.plot(t, Ax)
plt.plot(t, Ay)
plt.plot(t, Az)
plt.legend(['$A_x$', '$A_y$', '$A_z$'], loc='lower left')
plt.title('Accelerometer Data - Outlier + LP Filter')
plt.ylabel('A/g [m/s$^2$]')
plt.xlabel('Index')
plt.savefig('accel_data.png', dpi=700)
plt.show()

plt.plot(t, Gx)
plt.plot(t, Gy)
plt.plot(t, Gz)
plt.legend(['$G_x$', '$G_y$', '$G_z$'], loc='lower left')
plt.title('Gyroscope Data - Outlier + LP Filter')
plt.ylabel('$\omega$ [$^\circ$/s]')
plt.xlabel('Index')
plt.savefig('gyro_data.png', dpi=700)
plt.show()
#
# time_des
#
# time_s
#
# a = 0.009
# time_des = np.arange(time_s[0],time_s[-1], 1/20)
# y = np.interp(time_des, time_s[100:-100], Ax[100:-100])
#
# print(len(y))
# print(len(Ax))
# y_LPF[0] = y[0]
#
# for index in range(1, len(y)-1):
#     y_LPF[index] =  a*y[index-1] + (1-a)*y_LPF[index-1]
#
# plt.plot(t, Ax)
# plt.title('No LPF')
# plt.show()
# t_new = np.array(range(1, len(y)+1))
#
# plt.plot(time_des, y)
# plt.title('No LPF - Interp')
# plt.show()
#
#
# plt.plot(time_des, y_LPF)
# plt.title('LPF')
# plt.show()
#
# # Position Estimation
# g = 9.81 # m/s^2
#
# # index = k
# # Finding k+1 state
#
# # delta_t = time_s[k+1] - time_s[k]
#
# # Need to check if stationary.
# #     If stationary: ax = vx = 0
