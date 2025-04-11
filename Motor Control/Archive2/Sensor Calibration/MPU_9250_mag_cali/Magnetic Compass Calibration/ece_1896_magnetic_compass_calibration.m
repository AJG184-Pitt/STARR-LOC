% Adam Nichols
% ECE 1896
% Team Starr Loc
% 19 March 2025

% create plots to represent calibration data

% reset the workspace
clear, clc

% import data from the text file
filename = "magnetic_compass_data_fwd.txt";
data = importdata(filename);



% Define a format pattern to extract Step, X, Y, Z
pattern = 'Step: %d\tX: %d\tY: %d\tZ: %d';

% create vectors from the imported data
step = zeros(length(data),1);
x = zeros(length(data),1);
y = zeros(length(data),1);
z = zeros(length(data),1);

for i = 1:length(data)
    % Example input string
    line = data{i};
    
    % Extract values
    curr = sscanf(line, pattern, [1, 4]);
    step(i) = curr(1);
    x(i) = curr(2);
    y(i) = curr(3);
    z(i) = curr(4);
end

% % get the magnitude of the spherical radius vectorr
% mag_all = sqrt(x.^2+y.^2+z.^2);
% offset = sum(mag_all)/length(mag_all);
% scale = max(abs(mag_all));

% determine the offsets for the measurements
x_offset = (max(x)+min(x))/2;
y_offset = (max(y)+min(y))/2;
z_offset = (max(z)+min(z))/2;

% scale x and y by their offset to center at zero
x = x - x_offset;
y = y - y_offset;
z = z - z_offset;

% scale x and y to be within 1
x_scale = max(abs(x));
x = x / x_scale;
y_scale = max(abs(y));
y = y / y_scale;

% use the arctangent to get the bearing
az = atan2(-y,x);
az_deg = az*180/pi - 9.25;
az_deg = unwrap(az_deg);


% create plots of x, y, z vs. step
figure(1)
clf
plot(step,x)
title("Plot of X vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(2)
clf
plot(step,y)
title("Plot of Y vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(3)
clf
plot(step,z)
title("Plot of Z vs. Step")
xlabel("Step Number")
ylabel("Sensor Reading")

figure(4)
clf
plot(step,az_deg)
title("Plot of Azimuth Angle vs. Step")
xlabel("Step Number")
ylabel("Azimuth Angle [deg]")

% figure(5)
% clf
% plot(step,mag_all)