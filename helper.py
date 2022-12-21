import matplotlib.pyplot as plt
from IPython import display

plt.ion()


def plot(times, mean_times):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title("Training...")
    plt.xlabel("Number o games")
    plt.ylabel("Time")
    plt.plot(times)
    plt.plot(mean_times)
    plt.ylim(ymin=0)
    plt.text(len(times) - 1, times[-1], str(times[-1]))
    plt.text(len(mean_times) - 1, mean_times[-1], str(mean_times[-1]))
