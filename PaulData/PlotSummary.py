def plotRunSummary(hdrText, dataTime, sumSignal, LR_Signal, TB_Signal):
    """
    plot the data from the run:

    """
    import numpy as np
    import matplotlib.pyplot as plt

    for line in hdrText.split('\n'):
        plotTitle = line  # grabs run name from hdrText and exits
        break

    tmax = dataTime.max()

    plt.figure(figsize=(12,14))

    plt.subplot(611)
    plt.axis('off')
    plt.xlim(0,1)
    plt.ylim(0,1)
    plt.title('Run Summary: ' + plotTitle, fontsize=20)
    plt.text(0, 0.9, hdrText, fontsize=10)

    plt.subplot(612)
    plt.plot(dataTime, sumSignal)
    plt.ylabel('sum Signal')
    plt.xlim(0,tmax)

    plt.subplot(613)
    plt.plot(dataTime, LR_Signal)
    plt.ylabel('Left - Right')
    plt.xlim(0,tmax)

    plt.subplot(614)
    plt.plot(dataTime, TB_Signal)
    plt.ylabel('Top-Bottom')
    plt.xlabel('time (s)')
    plt.xlim(0,tmax)

    plt.subplot(615)
    n = len(dataTime)
    dt = dataTime[1:n-1] - dataTime[0:n-2]
    print type(dt)
    print dt.mean()
    plt.hist(dt,bins=100)

    plt.subplot(616)
    plt.plot(dataTime[0:n-2],dt)
    plt.tight_layout()
    plt.savefig(run + 'Summary'+ '.pdf', dpi=300, orientation='landscape', format='pdf', transparent=False, bbox_inches=None, pad_inches=0.1)

    plt.show()

    return None
