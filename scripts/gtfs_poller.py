import threading    
import time 
from  vancouver_transit_analyzer.GTFSPoll import GTFSPoll
import schedule
from schedule import Scheduler
import random

_started = False
_POLL_FREQ = 10 

def run():
    poll()
    # Include the random int to prevent polling at the same time each day
    schedule.every(_POLL_FREQ+random.randint(0,3)).minutes.do(poll)
    threading.Thread(target = run_continuously).start()


def poll():
    """Pull data from GTFS and add to the database
    """
    poll = GTFSPoll()
    poll.build_model()
    print("Polled Data")

def run_continuously(interval=100):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run
