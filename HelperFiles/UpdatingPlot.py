import matplotlib
import numpy as np
matplotlib.use("tkagg")
import matplotlib.pyplot as plt


class UpdatingPlot:
    """
    A matplotlib-based live-updating plot
    """

    def __init__(self, title):
        plt.ion()
        self.title = title
        self.fig = plt.figure()
        self.fig.canvas.set_window_title(title)
        self.fig.show()
        self.ax = self.fig.add_subplot(111)

    def updateplotscatter(self, values, datalen, color=True):
        self.ax.cla()
        if color:
            self.ax.scatter(values[0], values[1], c=[i // datalen for i in range(datalen * 2)], s=10)
        else:
            self.ax.scatter(values[0], values[1], s=10)
        # self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()

    def updateplotbar(self, values, bins=100):
        hist0, bins0 = np.histogram(values, bins=bins)
        width0 = 0.7 * (bins0[1] - bins0[0])
        center0 = (bins0[:-1] + bins0[1:]) / 2
        self.ax.cla()
        self.ax.bar(center0, hist0, width=width0)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()

    def updateplot(self, xs, ys, multiplot=False):
        colors = ["r-", "b-", "g-", "k-", "y-"]
        params = []
        if not multiplot:
            params = [xs, ys]
        else:
            for i in range(len(xs)):
                params.append(xs[i])
                params.append(ys[i])
                params.append(colors[i])

        self.ax.cla()
        self.ax.plot(*params)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()

    def close(self):
        plt.close("all")
