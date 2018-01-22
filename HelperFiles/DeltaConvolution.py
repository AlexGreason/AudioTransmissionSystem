import scipy.signal as signal
import numpy as np


class Convolver:
    """
    Allows iterative extension of the signal being searched and the template being searched for in a matched-filter
    search. This is much faster than computing the full convolution every time if the signal and template are frequently
    being extended by small amounts. Does not produce exactly the same results as a single convolve call due to
    floating-point errors, but the results are close enough for this application.
    """

    def __init__(self, sig, template):
        self.signal = sig
        self.template = template[::-1]
        self.convolved = None

    def fft_convolve(self, dsignal, dtemplate):
        self.signal = np.concatenate((self.signal, dsignal), axis=0)
        self.template = np.concatenate((dtemplate[::-1], self.template), axis=0)
        self.convolved = signal.convolve(self.signal, self.template)
        return self.convolved

    def delta_convolve(self, dsignal, dtemplate):
        newsignal = np.concatenate((self.signal, dsignal), axis=0)
        newtemplate = np.concatenate((dtemplate[::-1], self.template), axis=0)
        newconvolve = np.zeros(self.convolved.shape[0] + 2 * dsignal.shape[0])

        # copy over old values
        newconvolve[dsignal.shape[0]:self.convolved.shape[0] + dsignal.shape[0]] = self.convolved

        # account for new signal values
        newtemp_dsignal = signal.convolve(newtemplate, dsignal)
        newconvolve[newconvolve.shape[0] - newtemp_dsignal.shape[0]: newconvolve.shape[0]] += newtemp_dsignal

        # account for new template values (note exclusion of d/d corner to prevent double-counting)
        signal_dtemplate = signal.convolve(self.signal, dtemplate[::-1])
        newconvolve[0:signal_dtemplate.shape[0]] += signal_dtemplate

        # save values
        self.signal = newsignal
        self.template = newtemplate
        self.convolved = newconvolve
        return newconvolve

    def convolve(self, dsignal, dtemplate):
        if self.convolved is None:
            return self.fft_convolve(dsignal, dtemplate)
        else:
            return self.delta_convolve(dsignal, dtemplate)

    def clear(self):
        self.signal = np.array([])
        self.template = np.array([])
        self.convolved = None

if __name__ == "__main__":
    signal = np.array([1])
    temp = np.array([0])
    C = Convolver(np.array([]), np.array([]))
    print(C.convolved)
    C.convolve(np.array([2]), np.array([1]))
    n = 370
    C.convolve(np.random.random_integers(-1000, 1000, n), np.random.random_integers(-1000, 1000, n))
    C.convolve(np.array([2, 5, 1]), np.array([1, 0, 7]))
