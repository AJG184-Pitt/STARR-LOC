% Adam Nichols
% ECE 1896
% Team Starr Loc
% 27 March 2025

% create plots to represent calibration data

% reset the workspace
clear, clc

% import data from the text file
filename = "MPU_9250_mag_cali_data_3_28_2025.txt";
data = importdata(filename);

% create vectors from the imported data
step = data(:,1);
mag_x = data(:,2);
mag_y = data(:,3);
mag_z = data(:,4);


% modify the mag sensor values
mag_x_max = max(mag_x);
mag_x_min = min(mag_x);
mag_x_offset = (mag_x_max+mag_x_min)/2;
mag_x_scale = (mag_x_max-mag_x_min)/2;
mag_x = (mag_x - mag_x_offset)/mag_x_scale;

% modify the mag sensor values
mag_y_max = max(mag_y);
mag_y_min = min(mag_y);
mag_y_offset = (mag_y_max+mag_y_min)/2;
mag_y_scale = (mag_y_max-mag_y_min)/2;
mag_y = (mag_y - mag_y_offset)/mag_y_scale;

% calculate heading
az = atan2(mag_x,mag_y)*180/pi;

figure(1)
clf
plot(step, mag_x)
title("Plot of MagX vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(2)
clf
plot(step, mag_y)
title("Plot of MagY vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(3)
clf
plot(step, mag_z)
title("Plot of MagZ vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(4)
clf
plot(step, az)
title("Az vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")