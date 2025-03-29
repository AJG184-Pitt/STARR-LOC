% Adam Nichols
% Prof. Li, Yun, Jacobs
% ECE 1896
% 10 February 2025

% recognize voice from a noisy signal using autocorrelation slices

% reset the workspace
clear, clc

%% listen to audio messages
% original signal
% sound(5*samples_raw,sample_rate_raw)
% most noise cut out
% sound(5*voice_containing_signal,sample_rate)

%% get example message samples

% get samples from file
filename = 'DemodulatedVoiceTestMessage.wav';                                               % define the filename
[samples_raw, sample_rate_raw] = audioread(filename);                       % extract data from wav file

% downsample the message to required samples
upsamp = 1;
downsamp = 10;
samples = resample(samples_raw, upsamp, downsamp);
sample_rate = sample_rate_raw * upsamp / downsamp;

% define signal parameters from file data
N = length(samples);                                                        % determine the number of samples
time_span_sec = N / sample_rate;                                            % determine the length of time of the audio file
sample_period = 1/sample_rate;                                              % determine the time between samples
t = linspace(0, time_span_sec - sample_period, N);                          % generate linear time vector

% get the first autocorrelation coefficient from windows of message
samples_per_window = 4800;                                                  % define the number of samples per window
num_windows = floor(N / samples_per_window);                                    % get the number of windows from the file (round down)

% slice the set of windows from the file
samples_trunc = samples(1:num_windows*samples_per_window);                      % truncate the remaining samples to fit evenly into windows
windows = reshape(samples_trunc, samples_per_window, []);                   % use reshape function to slice windows from message

% perform autocorrelation on each of the windows
window_autocorr_0 = zeros(num_windows,1);   % store the autocorr 0
window_autocorr_1 = zeros(num_windows,1);   % store the autocorr 1
window_voice_pres = zeros(num_windows,1);   % store if voice is detected
thresh = 0.3;
voice_containing_signal = [];   % initialize vector that program thinks contains voice
for i = 1:num_windows
    % get the current window
    curr_window = windows( ((i-1)*samples_per_window+1 : i*samples_per_window) );
    % get total power in the window
    k = 0;  
    window_autocorr_0(i) = sum(curr_window(1:samples_per_window-k) .* curr_window(k+1:samples_per_window));
    % get 1st autocorrelation coefficient
    k = 1;  
    window_autocorr_1(i) = sum(curr_window(1:samples_per_window-k) .* curr_window(k+1:samples_per_window));
    % determine voice presence by comparing 1st autocorrelation coefficient
    % against the total power multiplied by some threshold
    window_voice_pres(i) = window_autocorr_1(i) > window_autocorr_0(i)*thresh;
    % slice the message by what the model thinks contains voice
    if window_voice_pres(i) == 1
        voice_containing_signal = [voice_containing_signal, curr_window];
    end
end

