% Adam Nichols
% Prof. Li, Yun, Jacobs
% ECE 1896
% 16 February 2025

% recognize voice

% reset the workspace
clear, clc

%% parameters
filename = 'This is a test messa.mp3';      % filename where voice samples stored
SNR = -10;                                  % [dB] SNR of the noisy voice message
num_points_voice = 20000;                   % number of points to plot on voice
num_points_noise = 20000;                   % number of points to plot on noise
num_points_noisy_voice = 20000;             % number of points to plot on noisy voice

%% listen to the different signals

% sound(voice_samples,sample_rate)
% sound(noise_samples,sample_rate)
% sound(noisy_voice_samples,sample_rate)

%% get example message samples
[voice_samples, sample_rate] = audioread(filename); % extract data from wav file
N = length(voice_samples);                          % determine the number of samples
time_span_sec = N / sample_rate;                    % determine the length of time of the audio file
sample_period = 1/sample_rate;                      % determine the time between samples
t = linspace(0, time_span_sec - sample_period, N);  % generate linear time vector

% generate noise at the appropriate scale
noise_samples = randn(N,1);  % generate a vector of white noise (not scaled)
noise_power_init = sum(noise_samples.^2)/N;
voice_power = sum(voice_samples.^2)/N;
SNR_init = 10*log10(voice_power/noise_power_init);
noise_adj = SNR_init - SNR;
noise_samples = 10^(noise_adj/20)*noise_samples;

% add the noise to the voice signal
noisy_voice_samples = voice_samples + noise_samples;

% efficiently calculate the autocorrelation using the wiener khintchine thm
% and the power spectral density obtained using the fft
% compute the spectra of the signals for comparison
[f, voice_spec] = GetSpectrum(t,voice_samples,sample_rate);
voice_mag_spec = abs(voice_spec);
voice_mag_spec_dB = 20*log10(voice_mag_spec);
[~, noise_spec] = GetSpectrum(t,noise_samples,sample_rate);
noise_mag_spec = abs(noise_spec);
noise_mag_spec_dB = 20*log10(noise_mag_spec);
[~, noisy_voice_spec] = GetSpectrum(t,noisy_voice_samples,sample_rate);
noisy_voice_mag_spec = abs(noisy_voice_spec);
noisy_voice_mag_spec_dB = 20*log10(noisy_voice_mag_spec);

% % get the power spectral density (energy spectral density)
% voice_psd = voice_mag_spec.^2;
% noise_psd = noise_mag_spec.^2;
% noisy_voice_psd = noisy_voice_mag_spec.^2;
% 
% % get the autocorrelation function for each signal
% voice_autocorr = fftshift(fft(voice_psd));

% compute the 0th autocorrelation coefficient (not normalized)
k = 0;
voice_autocorr_0 = sum(voice_samples(1:N-k) .* voice_samples(k+1:N));
noise_autocorr_0 = sum(noise_samples(1:N-k) .* noise_samples(k+1:N));
voice_noisy_autocorr_0 = sum(noisy_voice_samples(1:N-k) .* noisy_voice_samples(k+1:N));
% compute the 1st autocorrelation coefficient (not normalized)
k = 1;
voice_autocorr_1 = sum(voice_samples(1:N-k) .* voice_samples(k+1:N));
noise_autocorr_1 = sum(noise_samples(1:N-k) .* noise_samples(k+1:N));
voice_noisy_autocorr_1 = sum(noisy_voice_samples(1:N-k) .* noisy_voice_samples(k+1:N));



% initialize figure number
fig_num = 1;

% plot the voice time domain message and its autocorrelation
figure(fig_num)
clf
fig_num = fig_num + 1;
tiledlayout
nexttile
plot(t(1:num_points_voice), voice_samples(1:num_points_voice), 'b-')
title("Voice Signal")
xlabel("time [sec]")
ylabel("Amplitude")
nexttile
plot(f, voice_mag_spec_dB, 'b-')
title("Voice Magnitude Spectrum")
xlabel("frequency [Hz]")
ylabel("Amplitude [dB]")

figure(fig_num)
clf
fig_num = fig_num + 1;
[voice_autocorr, voice_lags] = xcorr(voice_samples, voice_samples);
plot(voice_lags, voice_autocorr, 'b-')
title("Voice Autocorrelation")
xlabel("n")
ylabel("Amplitude")

% plot the noise time domain message and its autocorrelation
figure(fig_num)
clf
fig_num = fig_num + 1;
tiledlayout
nexttile
plot(t(1:num_points_noise), noise_samples(1:num_points_noise), 'r-')
title("Noise Signal")
xlabel("time [sec]")
ylabel("Amplitude")
nexttile
plot(f, noise_mag_spec_dB, 'r-')
title("Noise Magnitude Spectrum")
xlabel("frequency [Hz]")
ylabel("Amplitude [dB]")

figure(fig_num)
clf
fig_num = fig_num + 1;
[noise_autocorr, noise_lags] = xcorr(noise_samples, noise_samples);
plot(noise_lags, noise_autocorr, 'r-')
title("Noise Autocorrelation")
xlabel("n")
ylabel("Amplitude")

% plot the noisy voice time domain message and its autocorrelation
figure(fig_num)
clf
fig_num = fig_num + 1;
tiledlayout
nexttile
plot(t(1:num_points_noisy_voice), noisy_voice_samples(1:num_points_noisy_voice), 'm-')
title("Noisy Voice Signal")
xlabel("time [sec]")
ylabel("Amplitude")
nexttile
plot(f, noisy_voice_mag_spec_dB, 'm-')
title("Noisy Voice Magnitude Spectrum")
xlabel("frequency [Hz]")
ylabel("Amplitude [dB]")

figure(fig_num)
clf
fig_num = fig_num + 1;
[noisy_voice_autocorr, noisy_voice_lags] = xcorr(noisy_voice_samples, noisy_voice_samples);
plot(noisy_voice_lags, noisy_voice_autocorr, 'm-')
title("Noisy Voice Autocorrelation")
xlabel("n")
ylabel("Amplitude")


% set threshold of 1st autocorrelation coefficient
thresh = 0.01;
min_for_detection = voice_noisy_autocorr_0 * thresh;
if voice_noisy_autocorr_1 > min_for_detection
    fprintf("Voice is detected.\n")
else
    fprintf("Voice is not detected.\n")
end


% display results for the noise autocorrelation
fprintf('\nThe noise autocorrelation values are:\n0: ')
fprintf(num2str(noise_autocorr_0))
fprintf('\n1: ')
fprintf(num2str(noise_autocorr_1))
fprintf('\nRatio: ')
fprintf(num2str(noise_autocorr_1/noise_autocorr_0))
fprintf('\n\n')

% display results for the ideal voice autocorrelation
fprintf('The ideal voice autocorrelation values are:\n0: ')
fprintf(num2str(voice_autocorr_0))
fprintf('\n1: ')
fprintf(num2str(voice_autocorr_1))
fprintf('\nRatio: ')
fprintf(num2str(voice_autocorr_1/voice_autocorr_0))
fprintf('\n\n')

% display results for the noisy voice autocorrelation
fprintf('The noisy voice autocorrelation values are:\n0: ')
fprintf(num2str(voice_noisy_autocorr_0))
fprintf('\n1: ')
fprintf(num2str(voice_noisy_autocorr_1))
fprintf('\nRatio: ')
fprintf(num2str(voice_noisy_autocorr_1/voice_noisy_autocorr_0))
fprintf('\nThe threshold for detection was: ')
fprintf(num2str(thresh))
fprintf(' and minimum for detection: ')
fprintf(num2str(min_for_detection))
fprintf('\nThe SNR was: ')
fprintf(num2str(SNR))
fprintf(' [dB]\n\n')