% Adam Nichols
% ECE 1896
% Team Starr Loc
% 20 March 2025

% create plots to represent calibration data

% reset the workspace
clear, clc

% import data from the text file
filename = "arduino_output.txt";
data = importdata(filename);



% Define a format pattern to extract Step, X, Y, Z
pattern = 'Az: %d\tEl: %d\tX: %d\tY: %d\tZ: %d';

% create vectors from the imported data
step = zeros(length(data),1);
az_vec = zeros(length(data),1);
el_vec = zeros(length(data),1);
x_vec = zeros(length(data),1);
y_vec = zeros(length(data),1);
z_vec = zeros(length(data),1);

for i = 1:length(data)
    % Example input string
    line = data{i};
    
    % Extract values
    curr = sscanf(line, pattern, [1, 5]);
    az_vec(i) = curr(1);
    el_vec(i) = curr(2);
    x_vec(i) = curr(3);
    y_vec(i) = curr(4);
    z_vec(i) = curr(5);
end

% reshape for plots
az = reshape(az_vec,40,[]);
el = reshape(el_vec,40,[]);
x = reshape(x_vec,40,[]);
y = reshape(y_vec,40,[]);
z = reshape(z_vec,40,[]);

% convert az/el into spherical coordinates
az_pol = az_vec / 4500 * 2*pi;
el_pol = (el_vec-1100) / 4500 * 2*pi;

% get the magnitude of the spherical radius vectorr
%mag_all = sqrt(x.^2+y.^2+z.^2);
% offset = sum(mag_all)/length(mag_all);
% scale = max(abs(mag_all));

% determine the offsets for the measurements
x_offset = (max(max(x))+min(min(x)))/2;
y_offset = (max(max(y))+min(min(y)))/2;
z_offset = (max(max(z))+min(min(z)))/2;

% scale x and y by their offset to center at zero
x = x - x_offset;
x_vec = x_vec-x_offset;
y = y - y_offset;% + 3167;
y_vec = y_vec-y_offset;
z = z - z_offset;% - 4595;
z_vec = z_vec-z_offset;

% scale x and y to be within 1
x_scale = max(max(abs(x)));
x = x / x_scale;
x_vec = x_vec / x_scale;
y_scale = max(max(abs(y)));
y = y / y_scale;
y_vec = y_vec / y_scale;
z_scale = max(max(abs(z)));
z = z / z_scale;
z_vec = z_vec / z_scale;

% get x,y,z coords for spherical plot of x
x_sph_x = x_vec.*cos(el_pol).*cos(az_pol);
x_sph_y = x_vec.*cos(el_pol).*sin(az_pol);
x_sph_z = x_vec.*sin(el_pol);
y_sph_x = y_vec.*cos(el_pol).*cos(az_pol);
y_sph_y = y_vec.*cos(el_pol).*sin(az_pol);
y_sph_z = y_vec.*sin(el_pol);
z_sph_x = z_vec.*cos(el_pol).*cos(az_pol);
z_sph_y = z_vec.*cos(el_pol).*sin(az_pol);
z_sph_z = z_vec.*sin(el_pol);

% use the arctangent to get the bearing
az_exp = atan2(y,x);
az_exp = unwrap(az_exp,[],2);
az_deg = az_exp*180/pi - 9.25;


% use the arctangent to get the elevation
el_exp = -asin(z./(sqrt(x.^2+y.^2+z.^2)));
%el_exp = unwrap(el_exp,[],1);
%el_exp = unwrap(el_exp,[],2);
el_deg = el_exp*180/pi;

% create plots of x, y, z vs. step
figure(1)
clf
mesh(az,el,x)
title("Plot of X vs. Step")
xlabel("Az step number")
ylabel("El step number")
zlabel("Sensor reading")

% create plots of x, y, z vs. step
figure(2)
clf
mesh(az,el,y)
title("Plot of Y vs. Step")
xlabel("Az step number")
ylabel("El step number")
zlabel("Sensor reading")

% create plots of x, y, z vs. step
figure(3)
clf
mesh(az,el,z)
title("Plot of Z vs. Step")
xlabel("Az step number")
ylabel("El step number")
zlabel("Sensor reading")

% create plot of experiment
figure(4)
clf
mesh(az,el,sqrt(x.^2+y.^2+z.^2))
title("Plot of Magnitude of Field Vector")
xlabel("az")
ylabel("el")
zlabel("mag")

% create plot of az angle
figure(5)
clf
mesh(az,el,az_deg)
title("Plot of AZ vs. Step")
xlabel("Az step number")
ylabel("El step number")
zlabel("Sensor reading")

% create plot of el angle
figure(6)
clf
mesh(az,el,el_deg)
title("Plot of EL vs. Step")
xlabel("Az step number")
ylabel("El step number")
zlabel("Sensor reading")

% create plot of experiment
figure(7)
clf
plot3(x_sph_x,x_sph_y,x_sph_z,'bo')
title("Plot of X SPH")
xlabel("x")
ylabel("y")
zlabel("z")

% create plot of experiment
figure(8)
clf
plot3(y_sph_x,y_sph_y,y_sph_z,'bo')
title("Plot of Y SPH")
xlabel("x")
ylabel("y")
zlabel("z")

% create plot of experiment
figure(9)
clf
plot3(z_sph_x,z_sph_y,z_sph_z,'bo')
title("Plot of Z SPH")
xlabel("x")
ylabel("y")
zlabel("z")



% create plot of experiment
figure(10)
clf
plot3(x_vec,y_vec,z_vec,'bo')
title("Plot of rescaled x, y, z values")
xlabel("x")
ylabel("y")
zlabel("z")