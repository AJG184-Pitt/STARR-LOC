% Adam Nichols
% ECE 1896
% Team Starr Loc
% 19 March 2025

% create plots to represent calibration data

% reset the workspace
clear, clc

% import data from the text file
filename = "ece_1896_starrloc_mpu9250_data_az.txt";
data = importdata(filename);

% create vectors from the imported data
d1 = data(:,1);
d2 = data(:,2);
acc_x = data(:,3);
acc_y = data(:,4);
acc_z = data(:,5);
gyr_x = data(:,6);
gyr_y = data(:,7);
gyr_z = data(:,8);
mag_x = data(:,9);
mag_y = data(:,10);
mag_z = data(:,11);
temp = data(:,12);

% modify the mag sensor values
mag_x_max = -35.73;
mag_x_min = -86.32;
mag_x_offset = (mag_x_max+mag_x_min)/2;
mag_x_scale = (mag_x_max-mag_x_min)/2;
mag_x = (mag_x - mag_x_offset)/mag_x_scale;

% modify the mag sensor values
mag_y_max = -169.28;
mag_y_min = -223.22;
mag_y_offset = (mag_y_max+mag_y_min)/2;
mag_y_scale = (mag_y_max-mag_y_min)/2;
mag_y = (mag_y - mag_y_offset)/mag_y_scale;

% calculate heading
az = -atan2(mag_x,mag_y)*180/pi;

% create step vector
step = (1:500)*10;

% create plots of x, y, z vs. step
figure(1)
clf
plot(step,d1)
title("Plot of D1 vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(2)
clf
plot(step,d2)
title("Plot of D2 vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(3)
clf
plot(step,acc_x)
title("Plot of AccX vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(4)
clf
plot(step,acc_y)
title("Plot of AccY vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(5)
clf
plot(step,acc_z)
title("Plot of AccZ vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(6)
clf
plot(step, gyr_x)
title("Plot of GryX vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(7)
clf
plot(step, gyr_y)
title("Plot of GryY vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(8)
clf
plot(step, gyr_z)
title("Plot of GryZ vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(9)
clf
plot(step, mag_x)
title("Plot of MagX vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(10)
clf
plot(step, mag_y)
title("Plot of MagY vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(11)
clf
plot(step, mag_z)
title("Plot of MagZ vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(12)
clf
plot(step, temp)
title("Temp vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(13)
clf
plot(step, az)
title("Az vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")