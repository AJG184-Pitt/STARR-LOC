function [f,spectrum] = GetSpectrum(time, samples, sample_rate)
% GETSPECTRUM get the spectrum of the input signal

    % determine the spectrum of the baseband signal
    spectrum = 1/sample_rate*fftshift(fft(samples));
    
    % define the frequency range
    f_index_min = floor(-1/2*length(time));
    f_index_max = floor(1/2*length(time)-1);
    f = sample_rate * (f_index_min:f_index_max);
    f = f/length(f); % normalize f

end

